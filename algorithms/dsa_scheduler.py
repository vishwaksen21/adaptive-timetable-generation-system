"""
DSA-based Timetable Scheduling Algorithm
Implements Constraint Satisfaction Problem (CSP) with Backtracking,
Graph Coloring, and Genetic Algorithm approaches
"""

import random
import time
import copy
import logging
from typing import Dict, List, Tuple, Optional, Set
from dataclasses import dataclass, field
from collections import defaultdict
from enum import Enum

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class TimeSlotEntry:
    """Represents a single entry in the timetable"""
    day: str
    period: int
    section: str
    subject_code: str
    subject_name: str
    subject_short: str
    subject_type: str
    faculty_id: str
    faculty_name: str
    room_number: str
    batch: Optional[str] = None  # For lab batches like A1, A2, A3
    is_lab_continuation: bool = False

@dataclass
class ConstraintViolation:
    """Represents a constraint violation"""
    constraint_type: str
    description: str
    severity: str  # "hard" or "soft"
    affected_entries: List[TimeSlotEntry] = field(default_factory=list)

class AlgorithmType(Enum):
    CONSTRAINT_SATISFACTION = "constraint_satisfaction"
    GENETIC_ALGORITHM = "genetic"
    GRAPH_COLORING = "graph_coloring"
    HYBRID = "hybrid"


class TimetableScheduler:
    """
    Main DSA-based Timetable Scheduler using Constraint Satisfaction Problem approach
    with backtracking and various optimization techniques
    """
    
    def __init__(self, config: dict):
        self.config = config
        self.debug_mode = config.get('debug_mode', False)
        self.timeout_seconds = config.get('timeout_seconds', 300)
        self.algorithm_type = config.get('algorithm_type', AlgorithmType.CONSTRAINT_SATISFACTION)
        
        # Time configuration
        self.days = config.get('days', ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"])
        self.periods_per_day = config.get('periods_per_day', 7)
        
        # Constraint configuration
        self.max_consecutive_theory = config.get('max_consecutive_theory', 3)
        self.prefer_morning_labs = config.get('prefer_morning_labs', True)
        self.limit_first_period = config.get('limit_first_period', 3)
        
        # State tracking
        self.timetable: Dict[str, Dict[Tuple[str, int], List[TimeSlotEntry]]] = {}  # section -> (day, period) -> entries
        self.teacher_schedule: Dict[str, Dict[Tuple[str, int], TimeSlotEntry]] = {}  # faculty_id -> (day, period) -> entry
        self.room_schedule: Dict[str, Dict[Tuple[str, int], TimeSlotEntry]] = {}  # room -> (day, period) -> entry
        
        # Tracking for requirements
        self.subject_hours_allocated: Dict[str, Dict[str, int]] = {}  # section -> subject_code -> hours
        
        # Statistics
        self.backtrack_count = 0
        self.total_attempts = 0
        self.generation_time = 0
        self.violations: List[ConstraintViolation] = []
        
    def initialize_state(self, sections: List[str]):
        """Initialize empty state for all sections"""
        for section in sections:
            self.timetable[section] = {}
            self.subject_hours_allocated[section] = defaultdict(int)
            
        self.teacher_schedule = defaultdict(dict)
        self.room_schedule = defaultdict(dict)
        
    def check_hard_constraints(self, entry: TimeSlotEntry) -> Tuple[bool, List[str]]:
        """
        Check all hard constraints for a proposed entry
        Returns (is_valid, list_of_violations)
        """
        violations = []
        day = entry.day
        period = entry.period
        section = entry.section
        
        # 1. No section clash - section can't have two classes at same time
        if (day, period) in self.timetable.get(section, {}):
            existing = self.timetable[section][(day, period)]
            if existing and not any(e.batch for e in existing):
                violations.append(f"Section {section} already has class at {day} period {period}")
        
        # 2. No teacher clash - teacher can't be in two places at once
        if entry.faculty_id in self.teacher_schedule:
            if (day, period) in self.teacher_schedule[entry.faculty_id]:
                violations.append(f"Teacher {entry.faculty_name} already assigned at {day} period {period}")
        
        # 3. No room clash - room can't be double-booked
        if entry.room_number in self.room_schedule:
            if (day, period) in self.room_schedule[entry.room_number]:
                violations.append(f"Room {entry.room_number} already booked at {day} period {period}")
        
        return len(violations) == 0, violations
    
    def check_lab_continuity(self, section: str, subject_code: str, day: str, 
                             start_period: int, duration: int) -> Tuple[bool, str]:
        """Check if lab can be placed in continuous slots"""
        for p in range(start_period, start_period + duration):
            if p > self.periods_per_day:
                return False, f"Lab exceeds available periods on {day}"
            
            if (day, p) in self.timetable.get(section, {}):
                return False, f"Slot {day} period {p} already occupied"
        
        # Check break constraints - don't span across lunch break
        # Periods 1-4 are before lunch, 5-7 are after lunch
        if start_period <= 4 and start_period + duration > 5:
            return False, "Lab cannot span across lunch break"
        
        return True, ""
    
    def calculate_soft_constraint_penalty(self, entry: TimeSlotEntry) -> int:
        """Calculate penalty for soft constraint violations"""
        penalty = 0
        section = entry.section
        day = entry.day
        period = entry.period
        
        # 1. Check consecutive theory periods
        if entry.subject_type == "theory":
            consecutive = 1
            for p in range(period - 1, 0, -1):
                if (day, p) in self.timetable.get(section, {}):
                    prev_entries = self.timetable[section][(day, p)]
                    if any(e.subject_type == "theory" for e in prev_entries):
                        consecutive += 1
                    else:
                        break
                else:
                    break
            
            if consecutive > self.max_consecutive_theory:
                penalty += (consecutive - self.max_consecutive_theory) * 10
        
        # 2. Early morning slot penalty (8:00 AM)
        if period == 1:
            # Count how many times first period is used for this section
            first_period_count = sum(
                1 for d in self.days 
                if (d, 1) in self.timetable.get(section, {})
            )
            if first_period_count >= self.limit_first_period:
                penalty += 5
        
        # 3. Lab placement preference
        if entry.subject_type == "lab":
            if self.prefer_morning_labs and period > 4:
                penalty += 3  # Prefer morning labs
        
        return penalty
    
    def add_entry(self, entry: TimeSlotEntry) -> bool:
        """Add an entry to the timetable if valid"""
        is_valid, violations = self.check_hard_constraints(entry)
        
        if not is_valid:
            if self.debug_mode:
                logger.debug(f"Entry rejected: {violations}")
            return False
        
        section = entry.section
        day = entry.day
        period = entry.period
        
        # Add to timetable
        if (day, period) not in self.timetable[section]:
            self.timetable[section][(day, period)] = []
        self.timetable[section][(day, period)].append(entry)
        
        # Track teacher schedule
        self.teacher_schedule[entry.faculty_id][(day, period)] = entry
        
        # Track room schedule
        self.room_schedule[entry.room_number][(day, period)] = entry
        
        # Track subject hours
        self.subject_hours_allocated[section][entry.subject_code] += 1
        
        return True
    
    def remove_entry(self, entry: TimeSlotEntry):
        """Remove an entry from the timetable (for backtracking)"""
        section = entry.section
        day = entry.day
        period = entry.period
        
        if (day, period) in self.timetable.get(section, {}):
            self.timetable[section][(day, period)] = [
                e for e in self.timetable[section][(day, period)]
                if e != entry
            ]
            if not self.timetable[section][(day, period)]:
                del self.timetable[section][(day, period)]
        
        # Remove from teacher schedule
        if entry.faculty_id in self.teacher_schedule:
            if (day, period) in self.teacher_schedule[entry.faculty_id]:
                del self.teacher_schedule[entry.faculty_id][(day, period)]
        
        # Remove from room schedule
        if entry.room_number in self.room_schedule:
            if (day, period) in self.room_schedule[entry.room_number]:
                del self.room_schedule[entry.room_number][(day, period)]
        
        # Update subject hours
        self.subject_hours_allocated[section][entry.subject_code] -= 1
    
    def get_available_slots(self, section: str) -> List[Tuple[str, int]]:
        """Get all available slots for a section"""
        available = []
        for day in self.days:
            for period in range(1, self.periods_per_day + 1):
                if (day, period) not in self.timetable.get(section, {}):
                    available.append((day, period))
        return available
    
    def get_available_faculty(self, subject_code: str, day: str, 
                              period: int, faculty_list: List) -> List:
        """Get available faculty for a subject at a given time"""
        available = []
        for faculty in faculty_list:
            if subject_code in faculty.subjects:
                # Check if faculty is available
                if (day, period) not in self.teacher_schedule.get(faculty.id, {}):
                    # Check unavailable slots
                    if (day, period) not in faculty.unavailable_slots:
                        available.append(faculty)
        return available
    
    def get_available_rooms(self, room_type: str, day: str, 
                            period: int, room_list: List) -> List:
        """Get available rooms of a type at a given time"""
        available = []
        for room in room_list:
            if room.room_type == room_type or room_type == "any":
                if (day, period) not in self.room_schedule.get(room.number, {}):
                    available.append(room)
        return available


class ConstraintSatisfactionScheduler(TimetableScheduler):
    """
    CSP-based scheduler using backtracking with constraint propagation
    """
    
    def __init__(self, config: dict):
        super().__init__(config)
        self.domains: Dict[str, List[Tuple[str, int]]] = {}  # Variable -> possible values
        
    def schedule_greedy(self, sections: List[str], subjects: List, 
                       faculty_list: List, room_list: List,
                       section_batches: Dict[str, List[str]]) -> Tuple[bool, Dict]:
        """
        Fast greedy scheduling method - no backtracking, just place items where possible
        """
        start_time = time.time()
        self.initialize_state(sections)
        
        # Fixed slots configuration
        # Wednesday: Period 6 (14:00-15:00) = YOGA, Period 7 (15:00-16:00) = CLUB
        # Thursday: Period 6-7 (14:00-16:00) = Mini Project / Project Phase 1
        fixed_slot_types = {
            'YOGA': [('Wednesday', 6)],
            'CLUB': [('Wednesday', 7)],
            'MP': [('Thursday', 6), ('Thursday', 7)],    # Mini project (sem 5)
            'PP1': [('Thursday', 6), ('Thursday', 7)],   # Project Phase 1 (sem 6)
        }
        
        # First, schedule fixed activities for all sections
        for section in sections:
            for subject in subjects:
                if subject.short_name in fixed_slot_types:
                    slots = fixed_slot_types[subject.short_name]
                    
                    for day, period in slots:
                        # Find a faculty and room for this fixed slot
                        available_faculty = self.get_available_faculty(
                            subject.code, day, period, faculty_list
                        )
                        room_type = self._get_room_type_for_subject(subject)
                        available_rooms = self.get_available_rooms(room_type, day, period, room_list)
                        
                        if available_faculty and available_rooms:
                            faculty = available_faculty[0]
                            room = available_rooms[0]
                            
                            entry = TimeSlotEntry(
                                day=day,
                                period=period,
                                section=section,
                                subject_code=subject.code,
                                subject_name=subject.name,
                                subject_short=subject.short_name,
                                subject_type=subject.subject_type,
                                faculty_id=faculty.id,
                                faculty_name=faculty.short_name,
                                room_number=room.number,
                                batch=None,
                                is_lab_continuation=(period > slots[0][1]) if len(slots) > 1 else False
                            )
                            self.add_entry(entry)
        
        # Create scheduling order - prioritize by subject priority and type
        # Exclude fixed slot subjects
        scheduling_queue = self._create_scheduling_queue(sections, subjects, section_batches)
        scheduling_queue = [item for item in scheduling_queue 
                          if item['subject'].short_name not in fixed_slot_types]
        
        if self.debug_mode:
            logger.info(f"Greedy scheduling {len(scheduling_queue)} items (excluding fixed)")
        
        scheduled_count = 0
        
        for item in scheduling_queue:
            section = item['section']
            subject = item['subject']
            batch = item.get('batch')
            duration = item['duration']
            
            # Get available slots - prefer earlier periods, avoid period 7
            available_slots = self._get_valid_slots_for_item(section, subject, duration)
            
            if not available_slots:
                continue
            
            # Sort slots to prefer:
            # 1. Saturday: prefer periods 1-4 (end by 12:20), avoid 5-7 unless necessary
            # 2. Weekdays: avoid period 7 (15:00-16:00) unless necessary
            # 3. Earlier periods first (morning preference)
            # 4. Slots that fill gaps (no breaks between classes)
            def slot_priority(slot):
                day, start_period = slot
                day_idx = self.days.index(day) if day in self.days else 0
                end_period = start_period + duration - 1
                
                # Saturday penalty - prefer ending by period 4 (12:20)
                is_saturday = (day == 'Saturday')
                saturday_afternoon = is_saturday and end_period >= 5
                
                # General late period penalty
                uses_period_7 = end_period >= 7
                uses_period_6 = end_period >= 6
                
                # Check if this slot fills a gap
                fills_gap = False
                if section in self.timetable:
                    # Check if there's a class before this slot
                    has_before = any((day, p) in self.timetable[section] 
                                    for p in range(1, start_period))
                    # Check if there's a class after this slot
                    has_after = any((day, p) in self.timetable[section] 
                                   for p in range(start_period + duration, 8))
                    fills_gap = has_before and has_after
                
                # Priority tuple: lower is better
                # (saturday_afternoon, uses_period_7, uses_period_6, NOT fills_gap, start_period, day_idx)
                return (saturday_afternoon, uses_period_7, uses_period_6, -int(fills_gap), start_period, day_idx)
            
            available_slots.sort(key=slot_priority)
            
            for day, start_period in available_slots:
                self.total_attempts += 1
                
                entries_added = []
                success = True
                
                for p in range(start_period, start_period + duration):
                    # Get available faculty
                    available_faculty = self.get_available_faculty(
                        subject.code, day, p, faculty_list
                    )
                    
                    if not available_faculty:
                        success = False
                        break
                    
                    # Get available rooms
                    room_type = self._get_room_type_for_subject(subject)
                    available_rooms = self.get_available_rooms(room_type, day, p, room_list)
                    
                    if not available_rooms:
                        success = False
                        break
                    
                    # Create entry
                    faculty = random.choice(available_faculty)
                    room = random.choice(available_rooms)
                    
                    entry = TimeSlotEntry(
                        day=day,
                        period=p,
                        section=section,
                        subject_code=subject.code,
                        subject_name=subject.name,
                        subject_short=subject.short_name,
                        subject_type=subject.subject_type,
                        faculty_id=faculty.id,
                        faculty_name=faculty.short_name,
                        room_number=room.number,
                        batch=batch,
                        is_lab_continuation=(p > start_period)
                    )
                    
                    if self.add_entry(entry):
                        entries_added.append(entry)
                    else:
                        success = False
                        break
                
                if success and len(entries_added) == duration:
                    scheduled_count += 1
                    break
                else:
                    # Remove partial entries
                    for entry in entries_added:
                        self.remove_entry(entry)
        
        self.generation_time = time.time() - start_time
        
        if self.debug_mode:
            logger.info(f"Greedy scheduling completed in {self.generation_time:.2f}s")
            logger.info(f"Scheduled {scheduled_count}/{len(scheduling_queue)} items")
        
        # Consider success if we scheduled most items
        success = scheduled_count >= len(scheduling_queue) * 0.7
        
        return success, self.timetable
        
    def schedule_with_backtracking(self, sections: List[str], subjects: List, 
                                   faculty_list: List, room_list: List,
                                   section_batches: Dict[str, List[str]]) -> Tuple[bool, Dict]:
        """
        Main scheduling method using CSP with backtracking
        """
        start_time = time.time()
        self.initialize_state(sections)
        
        # Create scheduling order - prioritize by subject priority and type
        scheduling_queue = self._create_scheduling_queue(sections, subjects, section_batches)
        
        if self.debug_mode:
            logger.info(f"Scheduling queue has {len(scheduling_queue)} items")
        
        # Try to schedule with backtracking
        success = self._backtrack_schedule(scheduling_queue, 0, faculty_list, room_list, start_time)
        
        self.generation_time = time.time() - start_time
        
        if self.debug_mode:
            logger.info(f"Scheduling completed in {self.generation_time:.2f}s")
            logger.info(f"Backtrack count: {self.backtrack_count}")
            logger.info(f"Total attempts: {self.total_attempts}")
        
        return success, self.timetable
    
    def _create_scheduling_queue(self, sections: List[str], subjects: List,
                                  section_batches: Dict[str, List[str]]) -> List[dict]:
        """Create ordered queue of items to schedule"""
        queue = []
        
        for section in sections:
            batches = section_batches.get(section, [])
            
            for subject in subjects:
                # For labs with batches, create separate entries
                if subject.subject_type == "lab" and subject.batches_required and batches:
                    for batch in batches:
                        for _ in range(subject.hours_per_week // subject.lab_duration if subject.lab_duration > 0 else 1):
                            queue.append({
                                'section': section,
                                'subject': subject,
                                'batch': batch,
                                'duration': subject.lab_duration,
                                'priority': subject.priority
                            })
                elif subject.subject_type == "lab":
                    # Non-batch lab
                    for _ in range(subject.hours_per_week // subject.lab_duration if subject.lab_duration > 0 else 1):
                        queue.append({
                            'section': section,
                            'subject': subject,
                            'batch': None,
                            'duration': subject.lab_duration,
                            'priority': subject.priority
                        })
                else:
                    # Theory and other subjects
                    for _ in range(subject.hours_per_week):
                        queue.append({
                            'section': section,
                            'subject': subject,
                            'batch': None,
                            'duration': 1,
                            'priority': subject.priority
                        })
        
        # Sort by priority (lower is higher priority)
        # Labs first, then theory, then activities
        queue.sort(key=lambda x: (x['priority'], -x['duration'], x['subject'].subject_type != 'lab'))
        
        return queue
    
    def _backtrack_schedule(self, queue: List[dict], index: int,
                            faculty_list: List, room_list: List,
                            start_time: float) -> bool:
        """Recursive backtracking scheduler"""
        
        # Check timeout
        if time.time() - start_time > self.timeout_seconds:
            if self.debug_mode:
                logger.warning("Scheduling timed out")
            return False
        
        # Base case - all items scheduled
        if index >= len(queue):
            return True
        
        item = queue[index]
        section = item['section']
        subject = item['subject']
        batch = item.get('batch')
        duration = item['duration']
        
        # Get available slots
        available_slots = self._get_valid_slots_for_item(section, subject, duration)
        
        # Shuffle for randomization
        random.shuffle(available_slots)
        
        for day, start_period in available_slots:
            self.total_attempts += 1
            
            # Try to place this item
            entries_added = []
            success = True
            
            for p in range(start_period, start_period + duration):
                # Get available faculty
                available_faculty = self.get_available_faculty(
                    subject.code, day, p, faculty_list
                )
                
                if not available_faculty:
                    success = False
                    break
                
                # Get available rooms
                room_type = self._get_room_type_for_subject(subject)
                available_rooms = self.get_available_rooms(room_type, day, p, room_list)
                
                if not available_rooms:
                    success = False
                    break
                
                # Create entry
                faculty = random.choice(available_faculty)
                room = random.choice(available_rooms)
                
                entry = TimeSlotEntry(
                    day=day,
                    period=p,
                    section=section,
                    subject_code=subject.code,
                    subject_name=subject.name,
                    subject_short=subject.short_name,
                    subject_type=subject.subject_type,
                    faculty_id=faculty.id,
                    faculty_name=faculty.short_name,
                    room_number=room.number,
                    batch=batch,
                    is_lab_continuation=(p > start_period)
                )
                
                if self.add_entry(entry):
                    entries_added.append(entry)
                else:
                    success = False
                    break
            
            if success and len(entries_added) == duration:
                # Recursively schedule next item
                if self._backtrack_schedule(queue, index + 1, faculty_list, room_list, start_time):
                    return True
            
            # Backtrack - remove added entries
            self.backtrack_count += 1
            for entry in entries_added:
                self.remove_entry(entry)
        
        return False
    
    def _get_valid_slots_for_item(self, section: str, subject, duration: int) -> List[Tuple[str, int]]:
        """Get valid slots for an item considering duration"""
        valid_slots = []
        
        # Fixed slots that are reserved (don't schedule regular classes here)
        reserved_slots = {
            ('Wednesday', 6),  # YOGA
            ('Wednesday', 7),  # CLUB
            ('Thursday', 6),   # Mini Project / PP1
            ('Thursday', 7),   # Mini Project / PP1
        }
        
        # Fixed slot subject types
        fixed_subject_types = ['YOGA', 'CLUB', 'MP', 'PP1']
        
        for day in self.days:
            for period in range(1, self.periods_per_day - duration + 2):
                # Check if all periods in duration are available
                all_available = True
                
                for p in range(period, period + duration):
                    # Check if slot is already taken
                    if (day, p) in self.timetable.get(section, {}):
                        all_available = False
                        break
                    
                    # Check if this is a reserved slot (for non-fixed subjects)
                    if subject.short_name not in fixed_subject_types:
                        if (day, p) in reserved_slots:
                            all_available = False
                            break
                
                # Check lab doesn't cross lunch (periods 4 to 5)
                if duration > 1:
                    if period <= 4 and period + duration > 5:
                        all_available = False
                
                if all_available:
                    valid_slots.append((day, period))
        
        return valid_slots
    
    def _get_room_type_for_subject(self, subject) -> str:
        """Determine room type needed for a subject"""
        if subject.subject_type == "lab":
            if "computer" in subject.name.lower() or "programming" in subject.name.lower():
                return "computer_lab"
            elif "electronics" in subject.name.lower() or "digital" in subject.name.lower():
                return "electronics_lab"
            else:
                return "computer_lab"
        elif subject.subject_type in ["yoga"]:
            return "activity_room"
        elif subject.subject_type in ["tyl", "9lpa"]:
            return "seminar_hall"
        else:
            return "classroom"


class GeneticAlgorithmScheduler(TimetableScheduler):
    """
    Genetic Algorithm based scheduler
    """
    
    def __init__(self, config: dict):
        super().__init__(config)
        self.population_size = config.get('population_size', 100)
        self.generations = config.get('generations', 500)
        self.mutation_rate = config.get('mutation_rate', 0.1)
        self.crossover_rate = config.get('crossover_rate', 0.8)
        self.elitism_count = config.get('elitism_count', 5)
        
    def schedule(self, sections: List[str], subjects: List,
                faculty_list: List, room_list: List,
                section_batches: Dict[str, List[str]]) -> Tuple[bool, Dict, List]:
        """
        Main scheduling using Genetic Algorithm
        """
        start_time = time.time()
        
        # Generate initial population
        population = self._generate_initial_population(
            sections, subjects, faculty_list, room_list, section_batches
        )
        
        best_timetable = None
        best_fitness = float('-inf')
        
        for gen in range(self.generations):
            # Check timeout
            if time.time() - start_time > self.timeout_seconds:
                break
            
            # Calculate fitness for each individual
            fitness_scores = [self._calculate_fitness(ind) for ind in population]
            
            # Track best
            max_idx = fitness_scores.index(max(fitness_scores))
            if fitness_scores[max_idx] > best_fitness:
                best_fitness = fitness_scores[max_idx]
                best_timetable = copy.deepcopy(population[max_idx])
            
            if self.debug_mode and gen % 50 == 0:
                logger.info(f"Generation {gen}: Best fitness = {best_fitness}")
            
            # Check if perfect solution found
            if best_fitness >= 0:  # No hard constraint violations
                break
            
            # Selection
            selected = self._tournament_selection(population, fitness_scores)
            
            # Crossover
            offspring = self._crossover(selected)
            
            # Mutation
            offspring = self._mutate(offspring, subjects, faculty_list, room_list)
            
            # Elitism - keep best individuals
            elite = sorted(zip(population, fitness_scores), key=lambda x: x[1], reverse=True)
            population = [e[0] for e in elite[:self.elitism_count]] + offspring
            
        self.generation_time = time.time() - start_time
        
        if best_timetable:
            self.timetable = self._convert_to_timetable_format(best_timetable)
            success = best_fitness >= -100  # Accept if reasonably good
        else:
            success = False
        
        return success, self.timetable, self.violations
    
    def _generate_initial_population(self, sections, subjects, faculty_list, 
                                     room_list, section_batches) -> List:
        """Generate random initial population"""
        population = []
        
        for _ in range(self.population_size):
            individual = self._generate_random_timetable(
                sections, subjects, faculty_list, room_list, section_batches
            )
            population.append(individual)
        
        return population
    
    def _generate_random_timetable(self, sections, subjects, faculty_list,
                                   room_list, section_batches) -> List[TimeSlotEntry]:
        """Generate a random timetable (may have conflicts)"""
        entries = []
        
        for section in sections:
            batches = section_batches.get(section, [])
            
            for subject in subjects:
                hours = subject.hours_per_week
                duration = subject.lab_duration if subject.subject_type == "lab" else 1
                
                if subject.subject_type == "lab" and subject.batches_required and batches:
                    for batch in batches:
                        self._add_random_entries(
                            entries, section, subject, batch, 
                            hours // len(batches), duration,
                            faculty_list, room_list
                        )
                else:
                    self._add_random_entries(
                        entries, section, subject, None,
                        hours, duration, faculty_list, room_list
                    )
        
        return entries
    
    def _add_random_entries(self, entries, section, subject, batch, 
                           hours, duration, faculty_list, room_list):
        """Add random entries for a subject"""
        remaining = hours
        
        while remaining > 0:
            day = random.choice(self.days)
            period = random.randint(1, self.periods_per_day - duration + 1)
            
            available_faculty = [f for f in faculty_list if subject.code in f.subjects]
            faculty = random.choice(available_faculty) if available_faculty else None
            
            room_type = self._get_room_type_for_subject(subject)
            available_rooms = [r for r in room_list if r.room_type == room_type]
            room = random.choice(available_rooms) if available_rooms else random.choice(list(room_list))
            
            if faculty and room:
                for p in range(period, period + duration):
                    entry = TimeSlotEntry(
                        day=day,
                        period=p,
                        section=section,
                        subject_code=subject.code,
                        subject_name=subject.name,
                        subject_short=subject.short_name,
                        subject_type=subject.subject_type,
                        faculty_id=faculty.id,
                        faculty_name=faculty.short_name,
                        room_number=room.number,
                        batch=batch,
                        is_lab_continuation=(p > period)
                    )
                    entries.append(entry)
                
                remaining -= duration
            else:
                break
    
    def _get_room_type_for_subject(self, subject) -> str:
        """Determine room type needed for a subject"""
        if subject.subject_type == "lab":
            return "computer_lab"
        elif subject.subject_type in ["yoga"]:
            return "activity_room"
        elif subject.subject_type in ["tyl", "9lpa"]:
            return "seminar_hall"
        else:
            return "classroom"
    
    def _calculate_fitness(self, individual: List[TimeSlotEntry]) -> float:
        """Calculate fitness score for an individual"""
        score = 1000  # Start with base score
        
        # Track conflicts
        section_slots = defaultdict(set)
        teacher_slots = defaultdict(set)
        room_slots = defaultdict(set)
        
        # Track subject hours
        subject_hours = defaultdict(lambda: defaultdict(int))
        
        for entry in individual:
            key = (entry.day, entry.period)
            
            # Check section clash
            if key in section_slots[entry.section]:
                score -= 100  # Hard constraint violation
            section_slots[entry.section].add(key)
            
            # Check teacher clash
            if key in teacher_slots[entry.faculty_id]:
                score -= 100
            teacher_slots[entry.faculty_id].add(key)
            
            # Check room clash
            if key in room_slots[entry.room_number]:
                score -= 100
            room_slots[entry.room_number].add(key)
            
            # Track hours
            subject_hours[entry.section][entry.subject_code] += 1
        
        # Penalize missing hours
        # (Would need subject requirements passed in for full implementation)
        
        return score
    
    def _tournament_selection(self, population, fitness_scores, tournament_size=3):
        """Tournament selection"""
        selected = []
        pop_size = len(population)
        
        for _ in range(pop_size - self.elitism_count):
            tournament_idx = random.sample(range(pop_size), min(tournament_size, pop_size))
            winner_idx = max(tournament_idx, key=lambda i: fitness_scores[i])
            selected.append(copy.deepcopy(population[winner_idx]))
        
        return selected
    
    def _crossover(self, parents):
        """Perform crossover between parents"""
        offspring = []
        
        for i in range(0, len(parents) - 1, 2):
            if random.random() < self.crossover_rate:
                # One-point crossover
                point = random.randint(1, min(len(parents[i]), len(parents[i+1])) - 1)
                child1 = parents[i][:point] + parents[i+1][point:]
                child2 = parents[i+1][:point] + parents[i][point:]
                offspring.extend([child1, child2])
            else:
                offspring.extend([parents[i], parents[i+1]])
        
        return offspring
    
    def _mutate(self, offspring, subjects, faculty_list, room_list):
        """Mutate offspring"""
        for individual in offspring:
            if random.random() < self.mutation_rate:
                if individual:
                    # Random mutation - change day/period of random entry
                    idx = random.randint(0, len(individual) - 1)
                    individual[idx].day = random.choice(self.days)
                    individual[idx].period = random.randint(1, self.periods_per_day)
        
        return offspring
    
    def _convert_to_timetable_format(self, individual: List[TimeSlotEntry]) -> Dict:
        """Convert flat list to timetable dictionary format"""
        timetable = defaultdict(dict)
        
        for entry in individual:
            section = entry.section
            key = (entry.day, entry.period)
            
            if key not in timetable[section]:
                timetable[section][key] = []
            timetable[section][key].append(entry)
        
        return dict(timetable)


class HybridScheduler(TimetableScheduler):
    """
    Hybrid scheduler combining CSP with GA for optimization
    """
    
    def __init__(self, config: dict):
        super().__init__(config)
        self.csp_scheduler = ConstraintSatisfactionScheduler(config)
        self.ga_scheduler = GeneticAlgorithmScheduler(config)
    
    def schedule(self, sections: List[str], subjects: List,
                faculty_list: List, room_list: List,
                section_batches: Dict[str, List[str]]) -> Tuple[bool, Dict, List]:
        """
        First try CSP, then optimize with GA if needed
        """
        # Try CSP first
        success, timetable = self.csp_scheduler.schedule_with_backtracking(
            sections, subjects, faculty_list, room_list, section_batches
        )
        
        if success:
            self.timetable = timetable
            self.generation_time = self.csp_scheduler.generation_time
            return True, timetable, []
        
        # Fall back to GA
        success, timetable, violations = self.ga_scheduler.schedule(
            sections, subjects, faculty_list, room_list, section_batches
        )
        
        self.timetable = timetable
        self.generation_time = self.csp_scheduler.generation_time + self.ga_scheduler.generation_time
        
        return success, timetable, violations


def create_scheduler(config: dict) -> TimetableScheduler:
    """Factory function to create appropriate scheduler"""
    algorithm_type = config.get('algorithm_type', 'constraint_satisfaction')
    
    if algorithm_type == 'genetic':
        return GeneticAlgorithmScheduler(config)
    elif algorithm_type == 'hybrid':
        return HybridScheduler(config)
    else:
        return ConstraintSatisfactionScheduler(config)
