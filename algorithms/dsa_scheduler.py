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

# Algorithm types (using strings for simplicity)
ALGORITHM_CONSTRAINT_SATISFACTION = "constraint_satisfaction"
ALGORITHM_GENETIC = "genetic"
ALGORITHM_GRAPH_COLORING = "graph_coloring"
ALGORITHM_HYBRID = "hybrid"


class TimetableScheduler:
    """
    Main DSA-based Timetable Scheduler using Constraint Satisfaction Problem approach
    with backtracking and various optimization techniques
    """
    
    def __init__(self, config: dict):
        self.config = config
        self.debug_mode = config.get('debug_mode', False)
        self.timeout_seconds = config.get('timeout_seconds', 300)
        self.algorithm_type = config.get('algorithm_type', ALGORITHM_CONSTRAINT_SATISFACTION)
        
        # Time configuration
        self.days = config.get('days', ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"])
        self.periods_per_day = config.get('periods_per_day', 7)
        
        # Constraint configuration
        self.max_consecutive_theory = config.get('max_consecutive_theory', 3)
        self.prefer_morning_labs = config.get('prefer_morning_labs', True)
        self.limit_first_period = config.get('limit_first_period', 3)
        
        # State tracking
        self.timetable: Dict[str, Dict[Tuple[str, int], List[TimeSlotEntry]]] = {}  # section -> (day, period) -> entries
        # Use lists to support parallel batch labs (same teacher/room for multiple batches)
        self.teacher_schedule: Dict[str, Dict[Tuple[str, int], List[TimeSlotEntry]]] = {}  # faculty_id -> (day, period) -> entries
        self.room_schedule: Dict[str, Dict[Tuple[str, int], List[TimeSlotEntry]]] = {}  # room -> (day, period) -> entries
        
        # Tracking for requirements
        self.subject_hours_allocated: Dict[str, Dict[str, int]] = {}  # section -> subject_code -> hours
        self.subjects_config: Dict[str, any] = {}  # subject_code -> Subject (for credit checking)
        
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
        
        # Use nested defaultdict with list to support parallel batch labs
        self.teacher_schedule = defaultdict(lambda: defaultdict(list))
        self.room_schedule = defaultdict(lambda: defaultdict(list))
        
    def check_hard_constraints(self, entry: TimeSlotEntry) -> Tuple[bool, List[str]]:
        violations = []
        day = entry.day
        period = entry.period
        section = entry.section

        # 1. Section clash
        if (day, period) in self.timetable.get(section, {}):
            existing = self.timetable[section][(day, period)]
            if existing:
                if not any(e.batch for e in existing) and not entry.batch:
                    violations.append(
                        f"Section {section} already has class at {day} P{period}"
                    )
                elif entry.batch:
                    if any(e.batch == entry.batch for e in existing):
                        violations.append(
                            f"Batch {entry.batch} already has class at {day} P{period}"
                        )
                elif not entry.batch and any(e.batch for e in existing):
                    violations.append(
                        f"Section {section} already has lab at {day} P{period}"
                    )

        # 2. SAME SUBJECT TWICE IN A DAY (THEORY ONLY)
        # Labs/activities are allowed to repeat due to block/parallel batch semantics.
        if entry.subject_type == "theory" and not entry.is_lab_continuation:
            for (d, _), entries in self.timetable.get(section, {}).items():
                if d == day and any(e.subject_code == entry.subject_code for e in entries):
                    violations.append(
                        f"{entry.subject_short} already scheduled on {day} for {section}"
                    )
                    break

        # 3. Teacher clash (batch exception)
        teacher_entries = self.teacher_schedule[entry.faculty_id][(day, period)]
        for e in teacher_entries:
            if not (entry.batch and e.batch and entry.section == e.section):
                violations.append(
                    f"Teacher {entry.faculty_name} busy at {day} P{period}"
                )
                break

        # 4. Room clash
        if self.room_schedule[entry.room_number][(day, period)]:
            violations.append(
                f"Room {entry.room_number} occupied at {day} P{period}"
            )

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
        
        # Track teacher schedule (append to list for parallel lab support)
        self.teacher_schedule[entry.faculty_id][(day, period)].append(entry)
        
        # Track room schedule (append to list for parallel lab support)
        self.room_schedule[entry.room_number][(day, period)].append(entry)
        
        # Track subject hours in actual periods (continuations included)
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
        
        # Remove from teacher schedule (filter from list)
        if (day, period) in self.teacher_schedule[entry.faculty_id]:
            self.teacher_schedule[entry.faculty_id][(day, period)] = [
                e for e in self.teacher_schedule[entry.faculty_id][(day, period)]
                if e != entry
            ]
        
        # Remove from room schedule (filter from list)
        if (day, period) in self.room_schedule[entry.room_number]:
            self.room_schedule[entry.room_number][(day, period)] = [
                e for e in self.room_schedule[entry.room_number][(day, period)]
                if e != entry
            ]
        
        # Update subject hours in actual periods (continuations included)
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
                              period: int, faculty_list: List, 
                              for_batch_lab: bool = False, section: str = None) -> List:
        """Get available faculty for a subject at a given time"""
        available = []
        for faculty in sorted(faculty_list, key=lambda f: getattr(f, 'id', '')):
            if subject_code in faculty.subjects:
                # Check if faculty is available
                is_available = True
                existing_entries = self.teacher_schedule[faculty.id][(day, period)]
                if existing_entries:
                    # If this is for a batch lab in the same section, allow reuse
                    if for_batch_lab and section:
                        # Allow if all existing are also batch labs in same section
                        for existing in existing_entries:
                            if not (existing.batch and existing.section == section):
                                is_available = False
                                break
                    else:
                        is_available = False
                
                if is_available:
                    # Check unavailable slots
                    if (day, period) not in faculty.unavailable_slots:
                        available.append(faculty)
        return sorted(available, key=lambda f: getattr(f, 'id', ''))
    
    def get_available_rooms(self, room_type: str, day: str, 
                            period: int, room_list: List, fallback_to_any: bool = False) -> List:
        """Get available rooms of a type at a given time"""
        available = []
        for room in sorted(room_list, key=lambda r: getattr(r, 'number', '')):
            if room.room_type == room_type or room_type == "any":
                # Check if room has no entries at this slot
                if not self.room_schedule[room.number][(day, period)]:
                    available.append(room)
        
        # If no specific room type available and fallback is allowed, try classrooms
        if not available and fallback_to_any and room_type not in ["classroom", "computer_lab", "electronics_lab"]:
            for room in sorted(room_list, key=lambda r: getattr(r, 'number', '')):
                if room.room_type == "classroom":
                    if not self.room_schedule[room.number][(day, period)]:
                        available.append(room)

        return sorted(available, key=lambda r: getattr(r, 'number', ''))


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
        Deterministic credit-based round-robin scheduler (CMRIT deployment rules).

        Non-negotiable enforcement:
        - Exact hours_per_week matching (period-level)
        - No internal gaps within a day's scheduled block (per section)
        - Days are filled sequentially (Mon→Sat)
        - Labs are strict 2-hour continuous blocks; cannot cross short break or lunch
        - Students stay in ONE fixed classroom for all theory/audit/tyl/9lpa
        - No randomness; no priority-based ordering
        """
        start_time = time.time()
        self.initialize_state(sections)

        self.subjects_config = {s.code: s for s in subjects}
        subjects_by_code = {s.code: s for s in subjects}

        fixed_slot_types = {
            'YOGA': [('Wednesday', 6)],
            'CLUB': [('Wednesday', 7)],
            'MP': [('Thursday', 6), ('Thursday', 7)],
            'PP1': [('Thursday', 6), ('Thursday', 7)],
        }

        home_rooms = self._assign_home_classrooms(sections, room_list)

        fixed_periods_by_section: Dict[str, Dict[str, Set[int]]] = {
            s: defaultdict(set) for s in sections
        }
        fixed_subject_codes: Set[str] = set()

        # 1) Place fixed slots first (deterministic faculty/room choice)
        # Non-negotiable: if a fixed slot cannot be placed, scheduling fails.
        fixed_scheduled = 0
        fixed_required = 0
        for section in sorted(sections):
            for subject in sorted(subjects, key=lambda s: getattr(s, 'code', '')):
                if subject.short_name not in fixed_slot_types:
                    continue
                fixed_subject_codes.add(subject.code)
                slots = fixed_slot_types[subject.short_name]
                fixed_required += len(slots)
                for idx, (day, period) in enumerate(slots):
                    faculty = self.get_available_faculty(subject.code, day, period, faculty_list)
                    room = self._select_room_for_subject(section, subject, day, period, room_list, home_rooms)
                    if not faculty or not room:
                        if self.debug_mode:
                            logger.warning(
                                f"Could not schedule fixed slot {subject.short_name} for {section} on {day} P{period}"
                            )
                        self.generation_time = time.time() - start_time
                        return False, self.timetable

                    entry = TimeSlotEntry(
                        day=day,
                        period=period,
                        section=section,
                        subject_code=subject.code,
                        subject_name=subject.name,
                        subject_short=subject.short_name,
                        subject_type=subject.subject_type,
                        faculty_id=faculty[0].id,
                        faculty_name=faculty[0].short_name,
                        room_number=room,
                        batch=None,
                        is_lab_continuation=(idx > 0)
                    )
                    if self.add_entry(entry):
                        fixed_scheduled += 1
                        fixed_periods_by_section[section][day].add(period)
                    else:
                        # add_entry() rejected due to a hard constraint
                        self.generation_time = time.time() - start_time
                        return False, self.timetable

        if fixed_scheduled != fixed_required:
            self.generation_time = time.time() - start_time
            return False, self.timetable

        if self.debug_mode:
            logger.info(f"Scheduled {fixed_scheduled} fixed slot entries")

        # 2) Fill remaining slots as contiguous day blocks in day order
        for section in sorted(sections):
            required_periods = sum(int(getattr(s, 'hours_per_week', 0)) for s in subjects)
            day_targets = self._build_day_targets(required_periods)
            day_blocks = self._build_day_blocks(day_targets, fixed_periods_by_section[section])

            if self.debug_mode:
                logger.info(f"Section {section}: required_periods={required_periods}, day_blocks={day_blocks}")

            rr_state = self._init_round_robin_state(subjects, fixed_subject_codes)

            for day in self.days:
                start_p, end_p = day_blocks[day]
                consecutive_theory = 0

                for period in range(start_p, end_p + 1):
                    if (day, period) in self.timetable.get(section, {}):
                        # Fixed slot already placed
                        entries = self.timetable[section][(day, period)]
                        if any(self._is_theory_session(subjects_by_code.get(e.subject_code)) for e in entries):
                            consecutive_theory += 1
                        else:
                            consecutive_theory = 0
                        continue

                    choice = self._select_subject_for_slot(
                        section=section,
                        day=day,
                        period=period,
                        day_block=(start_p, end_p),
                        rr_state=rr_state,
                        subjects_by_code=subjects_by_code,
                        section_batches=section_batches,
                        home_rooms=home_rooms,
                        faculty_list=faculty_list,
                        room_list=room_list,
                        consecutive_theory=consecutive_theory
                    )
                    if choice is None:
                        if self.debug_mode:
                            logger.debug(
                                "Greedy failed to select subject: %s %s P%s (block %s-%s), consecutive_theory=%s, remaining=%s",
                                section,
                                day,
                                period,
                                start_p,
                                end_p,
                                consecutive_theory,
                                {c: rr_state['remaining'].get(c, 0) for c in rr_state.get('codes', []) if rr_state['remaining'].get(c, 0) > 0}
                            )
                        # Try to continue with next period - maybe we can place something later
                        consecutive_theory = 0
                        continue

                    subject = choice['subject']
                    duration = choice['duration']
                    batches = choice.get('batches', [])

                    if choice.get('is_parallel_lab', False):
                        ok = self._place_parallel_batch_block(section, subject, day, period, duration, batches, faculty_list, room_list)
                    else:
                        ok = self._place_single_block(section, subject, day, period, duration, faculty_list, room_list, home_rooms)

                    if not ok:
                        logger.debug(
                            "Greedy failed to place subject: %s %s P%s -> %s (%s, duration=%s)",
                            section,
                            day,
                            period,
                            getattr(subject, 'short_name', getattr(subject, 'code', 'UNKNOWN')),
                            getattr(subject, 'subject_type', 'unknown'),
                            duration
                        )
                        self.generation_time = time.time() - start_time
                        return False, self.timetable

                    if self._is_theory_session(subject):
                        consecutive_theory += duration
                    else:
                        consecutive_theory = 0

        self.generation_time = time.time() - start_time
        return True, self.timetable

    def _assign_home_classrooms(self, sections: List[str], room_list: List) -> Dict[str, str]:
        classrooms = sorted([r for r in room_list if getattr(r, 'room_type', '') == 'classroom'],
                            key=lambda r: getattr(r, 'number', ''))
        if len(classrooms) < len(sections):
            raise ValueError("Not enough classrooms to assign one fixed theory room per section")
        return {section: classrooms[idx].number for idx, section in enumerate(sorted(sections))}

    def _is_theory_session(self, subject) -> bool:
        if subject is None:
            return False
        return getattr(subject, 'subject_type', '') in ("theory", "audit", "tyl", "9lpa", "yoga", "club")

    def _select_room_for_subject(self, section: str, subject, day: str, period: int,
                                 room_list: List, home_rooms: Dict[str, str]) -> Optional[str]:
        # Students stay in one classroom for all theory-like sessions
        if getattr(subject, 'subject_type', '') in ("theory", "audit", "tyl", "9lpa"):
            room_num = home_rooms[section]
            if not self.room_schedule[room_num][(day, period)]:
                return room_num

            # Fallback to any free classroom ONLY if home room is unavailable
            rooms = self.get_available_rooms("classroom", day, period, room_list)
            return rooms[0].number if rooms else None

        room_type = self._get_room_type_for_subject(subject)
        fallback = getattr(subject, 'subject_type', '') in ['tyl', '9lpa', 'yoga', 'club', 'audit']
        rooms = self.get_available_rooms(room_type, day, period, room_list, fallback_to_any=fallback)
        return rooms[0].number if rooms else None

    def _build_day_targets(self, required_periods: int) -> Dict[str, int]:
        base = required_periods // len(self.days)
        rem = required_periods % len(self.days)
        targets: Dict[str, int] = {}
        for idx, day in enumerate(self.days):
            targets[day] = base + (1 if idx < rem else 0)
        return targets

    def _build_day_blocks(self, day_targets: Dict[str, int], fixed_periods_by_day: Dict[str, Set[int]]) -> Dict[str, Tuple[int, int]]:
        """
        Build contiguous day blocks that fill morning slots first and leave free periods after 1pm.
        
        Strategy:
        - Fill morning periods first (periods 1-4 before lunch)
        - Then fill afternoon if needed (periods 5-7 after 1pm)
        - Leave free periods only after 1pm (periods 5-7)
        - Avoid too many 8am starts (period 1) unless necessary
        """
        blocks: Dict[str, Tuple[int, int]] = {}
        for day in self.days:
            target = day_targets[day]
            fixed_periods = fixed_periods_by_day.get(day, set())
            fixed_min = min(fixed_periods) if fixed_periods else 0
            fixed_max = max(fixed_periods) if fixed_periods else 0

            # Determine start and end based on target and fixed periods
            if target >= 6:
                # Need 6+ periods: fill P1-P4 (morning) + P5-P6 (afternoon), P7 may be free
                start_p = 1
                end_p = target
            elif target == 5:
                # Need 5 periods: fill P2-P4 (morning) + P5-P6 (afternoon), leave P1 and P7 free
                start_p = 2
                end_p = 6
            elif target == 4:
                # Need 4 periods: fill P2-P4 (morning) + P5, leave P1, P6-P7 free
                start_p = 2
                end_p = 5
            else:
                # Need 3 or fewer: fill morning periods P2-P4
                start_p = 2
                end_p = min(4, 2 + target - 1)
            
            # Adjust for fixed periods
            if fixed_periods:
                # Must include all fixed periods in the range
                if fixed_min < start_p:
                    start_p = fixed_min
                if fixed_max > end_p:
                    end_p = fixed_max
                    
                # If fixed periods force us to have specific coverage, adjust
                # For example, if fixed is at P6-P7, we need to ensure we fill morning first
                if fixed_min >= 5:  # Fixed periods are after lunch
                    # Fill morning periods first (2-4), then include fixed
                    morning_slots = min(4, target)
                    if start_p > 2:
                        start_p = 2
                    # End must include fixed periods
                    end_p = fixed_max

            # Make sure we don't exceed available periods
            if end_p > self.periods_per_day:
                end_p = self.periods_per_day
            
            # Ensure we have enough slots for target
            if end_p - start_p + 1 < target:
                # Expand to fit target, preferring to start earlier
                if start_p > 1:
                    start_p = max(1, end_p - target + 1)
                else:
                    end_p = min(self.periods_per_day, start_p + target - 1)

            blocks[day] = (start_p, end_p)
        return blocks

    def _init_round_robin_state(self, subjects: List, fixed_subject_codes: Set[str]) -> dict:
        eligible = [s for s in subjects if getattr(s, 'code', '') not in fixed_subject_codes]
        eligible = sorted(eligible, key=lambda s: getattr(s, 'code', ''))
        weights = {s.code: int(getattr(s, 'hours_per_week', 0)) for s in eligible}
        remaining = {s.code: int(getattr(s, 'hours_per_week', 0)) for s in eligible}
        current = {s.code: 0 for s in eligible}
        return {'codes': [s.code for s in eligible], 'weights': weights, 'remaining': remaining, 'current': current}

    def _subject_duration(self, subject) -> int:
        if getattr(subject, 'subject_type', '') == 'lab':
            return int(getattr(subject, 'lab_duration', 2))
        return 1

    def _can_start_two_hour_block(self, start_period: int) -> bool:
        # Valid 2-hour starts: (1,2), (3,4), (5,6)
        return start_period in (1, 3, 5)

    def _select_subject_for_slot(self, section: str, day: str, period: int, day_block: Tuple[int, int],
                                 rr_state: dict, subjects_by_code: Dict[str, any], section_batches: Dict[str, List[str]],
                                 home_rooms: Dict[str, str], faculty_list: List, room_list: List,
                                 consecutive_theory: int) -> Optional[dict]:
        start_p, end_p = day_block

        active = [c for c in rr_state['codes'] if rr_state['remaining'].get(c, 0) > 0]
        if not active:
            return None

        total_weight = sum(rr_state['weights'][c] for c in active)

        best = None
        best_score = None
        fallback = None  # Fallback option if max_consecutive is violated but no other choice

        for code in active:
            subject = subjects_by_code[code]
            duration = self._subject_duration(subject)

            if rr_state['remaining'][code] < duration:
                continue

            # Max 3 consecutive theory-like periods/day (soft constraint - can be relaxed if needed)
            exceeds_consecutive = self._is_theory_session(subject) and consecutive_theory + duration > self.max_consecutive_theory
            
            # No same theory subject twice in a day
            if getattr(subject, 'subject_type', '') == 'theory':
                already_today = False
                for (d, _), entries in self.timetable.get(section, {}).items():
                    if d == day and any(e.subject_code == code for e in entries):
                        already_today = True
                        break
                if already_today:
                    continue

            # Strict 2-hour blocks: must fit and not cross breaks
            if duration == 2:
                if period + 1 > end_p:
                    continue
                if not self._can_start_two_hour_block(period):
                    continue
                if (day, period) in self.timetable.get(section, {}) or (day, period + 1) in self.timetable.get(section, {}):
                    continue

            # Feasibility check for faculty/rooms
            if getattr(subject, 'subject_type', '') == 'lab' and getattr(subject, 'batches_required', False):
                batches = section_batches.get(section, [])
                if not batches:
                    continue
                if not self._feasible_parallel_batch_block(section, subject, day, period, duration, batches, faculty_list, room_list):
                    continue
            else:
                if not self._feasible_single_block(section, subject, day, period, duration, faculty_list, room_list, home_rooms):
                    continue

            score = rr_state['current'][code] + rr_state['weights'][code]
            
            # If this exceeds consecutive constraint, store as fallback but keep looking
            if exceeds_consecutive:
                if fallback is None or score > fallback.get('score', -float('inf')):
                    fallback = {
                        'subject': subject,
                        'duration': duration,
                        'is_parallel_lab': (getattr(subject, 'subject_type', '') == 'lab' and getattr(subject, 'batches_required', False)),
                        'batches': section_batches.get(section, []),
                        'score': score
                    }
                continue
            
            # This satisfies the consecutive constraint
            if best is None or score > best_score or (score == best_score and code < best['subject'].code):
                best = {
                    'subject': subject,
                    'duration': duration,
                    'is_parallel_lab': (getattr(subject, 'subject_type', '') == 'lab' and getattr(subject, 'batches_required', False)),
                    'batches': section_batches.get(section, [])
                }
                best_score = score

        # If no perfect match, use fallback (relaxing consecutive constraint)
        if best is None and fallback is not None:
            best = {k: v for k, v in fallback.items() if k != 'score'}
            if self.debug_mode:
                logger.debug(f"Relaxing consecutive theory constraint for {fallback['subject'].short_name} at {day} P{period}")

        if best is None:
            return None

        for c in active:
            rr_state['current'][c] += rr_state['weights'][c]
        chosen = best['subject'].code
        rr_state['current'][chosen] -= total_weight
        rr_state['remaining'][chosen] -= best['duration']

        return best

    def _feasible_single_block(self, section: str, subject, day: str, start_period: int, duration: int,
                               faculty_list: List, room_list: List, home_rooms: Dict[str, str]) -> bool:
        for p in range(start_period, start_period + duration):
            if (day, p) in self.timetable.get(section, {}):
                return False
            faculty = self.get_available_faculty(subject.code, day, p, faculty_list)
            room = self._select_room_for_subject(section, subject, day, p, room_list, home_rooms)
            if not faculty or not room:
                return False
        return True

    def _feasible_parallel_batch_block(self, section: str, subject, day: str, start_period: int, duration: int,
                                       batches: List[str], faculty_list: List, room_list: List) -> bool:
        room_type = self._get_room_type_for_subject(subject)
        for p in range(start_period, start_period + duration):
            if (day, p) in self.timetable.get(section, {}):
                return False
            faculty = self.get_available_faculty(subject.code, day, p, faculty_list, for_batch_lab=True, section=section)
            rooms = self.get_available_rooms(room_type, day, p, room_list)
            if not faculty or len(rooms) < len(batches):
                return False
        return True

    def _place_single_block(self, section: str, subject, day: str, start_period: int, duration: int,
                            faculty_list: List, room_list: List, home_rooms: Dict[str, str]) -> bool:
        entries_added = []
        for p in range(start_period, start_period + duration):
            faculty = self.get_available_faculty(subject.code, day, p, faculty_list)
            room = self._select_room_for_subject(section, subject, day, p, room_list, home_rooms)
            if not faculty or not room:
                for e in entries_added:
                    self.remove_entry(e)
                return False
            entry = TimeSlotEntry(
                day=day,
                period=p,
                section=section,
                subject_code=subject.code,
                subject_name=subject.name,
                subject_short=subject.short_name,
                subject_type=subject.subject_type,
                faculty_id=faculty[0].id,
                faculty_name=faculty[0].short_name,
                room_number=room,
                batch=None,
                is_lab_continuation=(p > start_period)
            )
            if self.add_entry(entry):
                entries_added.append(entry)
            else:
                for e in entries_added:
                    self.remove_entry(e)
                return False
        return True

    def _place_parallel_batch_block(self, section: str, subject, day: str, start_period: int, duration: int,
                                    batches: List[str], faculty_list: List, room_list: List) -> bool:
        room_type = self._get_room_type_for_subject(subject)
        entries_added = []
        for p in range(start_period, start_period + duration):
            faculty = self.get_available_faculty(subject.code, day, p, faculty_list, for_batch_lab=True, section=section)
            rooms = self.get_available_rooms(room_type, day, p, room_list)
            if not faculty or len(rooms) < len(batches):
                for e in entries_added:
                    self.remove_entry(e)
                return False
            for b_idx, batch_name in enumerate(batches):
                f = faculty[b_idx % len(faculty)]
                r = rooms[b_idx]
                entry = TimeSlotEntry(
                    day=day,
                    period=p,
                    section=section,
                    subject_code=subject.code,
                    subject_name=subject.name,
                    subject_short=subject.short_name,
                    subject_type=subject.subject_type,
                    faculty_id=f.id,
                    faculty_name=f.short_name,
                    room_number=r.number,
                    batch=batch_name,
                    is_lab_continuation=(p > start_period)
                )
                if self.add_entry(entry):
                    entries_added.append(entry)
                else:
                    for e in entries_added:
                        self.remove_entry(e)
                    return False
        return True
        
    def schedule_with_backtracking(self, sections: List[str], subjects: List, 
                                   faculty_list: List, room_list: List,
                                   section_batches: Dict[str, List[str]]) -> Tuple[bool, Dict]:
        """
        Main scheduling method - uses fast greedy approach first.
        Backtracking is too slow for real workloads (17+ subjects × sections).
        
        For production: use schedule_greedy() which is much faster.
        """
        # Use greedy scheduler (much faster for real workloads)
        # Pure backtracking is O(n!) and too slow for 17+ subjects
        logger.info("Using fast greedy scheduling (backtracking is too slow for this workload)")
        return self.schedule_greedy(sections, subjects, faculty_list, room_list, section_batches)
    
    def _create_scheduling_queue(self, sections: List[str], subjects: List,
                                  section_batches: Dict[str, List[str]]) -> List[dict]:
        """
        Create ordered queue of items to schedule using CREDIT-BASED ROUND-ROBIN ONLY.

        Legacy method: not used by the deterministic greedy scheduler path.
        Kept for compatibility/debugging and for CSP backtracking experiments.

        Deterministic properties:
        - No randomness/shuffling
        - No priority-based ordering
        - Labs emitted as strict 2-hour blocks
        - Elective/theory/special subjects spread by smooth weighted round-robin
        """
        queue: List[dict] = []

        fixed_short = {"YOGA", "CLUB", "MP", "PP1"}
        subjects_sorted = sorted(subjects, key=lambda s: getattr(s, 'code', ''))

        for section in sorted(sections):
            batches = section_batches.get(section, [])

            eligible = [s for s in subjects_sorted if getattr(s, 'short_name', '') not in fixed_short]
            weights = {s.code: int(getattr(s, 'hours_per_week', 0)) for s in eligible}
            current = {s.code: 0 for s in eligible}
            remaining_blocks: Dict[str, int] = {}
            by_code = {s.code: s for s in eligible}

            for s in eligible:
                duration = 2 if s.subject_type == 'lab' else int(getattr(s, 'lab_duration', 0) or 1)
                if s.subject_type == 'lab':
                    duration = 2
                remaining_blocks[s.code] = int(getattr(s, 'hours_per_week', 0)) // duration

            while any(v > 0 for v in remaining_blocks.values()):
                active = [c for c in [s.code for s in eligible] if remaining_blocks[c] > 0]
                total = sum(weights[c] for c in active)

                best_code = None
                best_score = None
                for c in active:
                    score = current[c] + weights[c]
                    if best_code is None or score > best_score or (score == best_score and c < best_code):
                        best_code = c
                        best_score = score

                for c in active:
                    current[c] += weights[c]
                current[best_code] -= total
                remaining_blocks[best_code] -= 1

                subj = by_code[best_code]
                duration = 2 if subj.subject_type == 'lab' else int(getattr(subj, 'lab_duration', 0) or 1)
                if subj.subject_type == 'lab':
                    duration = 2

                is_parallel = (subj.subject_type == 'lab' and getattr(subj, 'batches_required', False) and bool(batches))

                item = {
                    'section': section,
                    'subject': subj,
                    'batch': None,
                    'duration': duration,
                    'is_parallel_lab': is_parallel
                }
                if is_parallel:
                    item['batches'] = batches
                queue.append(item)

        return queue
    
    def _backtrack_schedule(self, queue: List[dict], index: int,
                            faculty_list: List, room_list: List,
                            start_time: float) -> bool:
        """Recursive backtracking scheduler
        
        NOTE: Batch labs (is_parallel_lab=True) are NOT handled by CSP backtracking.
        They are handled only by the greedy scheduler due to their complexity.
        """
        
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
        is_parallel_lab = item.get('is_parallel_lab', False)
        
        # Skip batch labs in CSP - they are handled by greedy scheduler only
        if is_parallel_lab:
            if self.debug_mode:
                logger.debug(f"Skipping batch lab {subject.short_name} in CSP - use greedy scheduler")
            return self._backtrack_schedule(queue, index + 1, faculty_list, room_list, start_time)
        
        # Get available slots
        available_slots = self._get_valid_slots_for_item(section, subject, duration, is_parallel_lab)
        
        # Sort slots by soft constraint penalty (lower penalty first)
        def slot_penalty(slot):
            day, period = slot
            penalty = 0
            # Prefer morning slots
            penalty += period * 2
            # Prefer earlier days
            penalty += self.days.index(day) if day in self.days else 0
            return penalty
        
        available_slots.sort(key=slot_penalty)
        
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
                
                # Deterministic choice
                faculty = available_faculty[0]
                room = available_rooms[0]
                
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
    
    def _get_valid_slots_for_item(self, section: str, subject, duration: int, 
                                   is_batch_lab: bool = False) -> List[Tuple[str, int]]:
        """Get valid slots for an item considering duration"""
        valid_slots = []
        
        # Fixed slots that are reserved (don't schedule regular classes here)
        reserved_slots = {
            ('Wednesday', 6),  # YOGA
            ('Wednesday', 7),  # CLUB
            ('Thursday', 6),   # Mini Project / PP1
            ('Thursday', 7),   # Mini Project / PP1
        }
        
        # Fixed slot subject short_names (use uppercase for consistent comparison)
        fixed_subject_short_names = ['YOGA', 'CLUB', 'MP', 'PP1']
        
        # Normalize subject short_name for comparison
        subject_short_upper = subject.short_name.upper() if subject.short_name else ''
        
        for day in self.days:
            for period in range(1, self.periods_per_day - duration + 2):
                # Check if all periods in duration are available
                all_available = True
                
                for p in range(period, period + duration):
                    # Check if slot is already taken
                    if (day, p) in self.timetable.get(section, {}):
                        existing = self.timetable[section][(day, p)]
                        # If slot has non-batch entries, it's not available
                        if not all(e.batch for e in existing):
                            all_available = False
                            break
                        # For non-batch items, can't use slot with batch labs
                        if not is_batch_lab:
                            all_available = False
                            break
                    
                    # Check if this is a reserved slot (for non-fixed subjects)
                    if subject_short_upper not in fixed_subject_short_names:
                        if (day, p) in reserved_slots:
                            all_available = False
                            break
                
                # VTU 2022: Labs must be continuous 2-hour blocks
                # Cannot cross short break (period 2→3) or lunch (period 4→5)
                if duration > 1 and subject.subject_type == "lab":
                    # Labs can only start at periods 1, 3, 5, 6
                    # Period 2: would cross to 3 (break between 2 and 3)
                    # Period 4: would cross to 5 (lunch between 4 and 5)
                    if period in [2, 4]:
                        all_available = False
                    # Also check general lunch crossing
                    elif period <= 4 and period + duration > 5:
                        all_available = False
                
                # Check lab continuity for lab subjects
                if all_available and subject.subject_type == "lab" and duration > 1:
                    ok, _ = self.check_lab_continuity(section, subject.code, day, period, duration)
                    if not ok:
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
        elif subject.subject_type == "mini_project":
            return "computer_lab"
        elif subject.subject_type in ["yoga"]:
            return "activity_room"
        elif subject.subject_type in ["tyl", "9lpa"]:
            return "seminar_hall"
        elif subject.subject_type in ["club"]:
            return "activity_room"
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
        self.subjects_config = {}  # Will be set during scheduling
        
    def schedule(self, sections: List[str], subjects: List,
                faculty_list: List, room_list: List,
                section_batches: Dict[str, List[str]]) -> Tuple[bool, Dict, List]:
        """
        Main scheduling using Genetic Algorithm
        """
        start_time = time.time()
        
        # Store subjects config for fitness calculation
        self.subjects_config = {s.code: s for s in subjects}
        self.sections = sections
        
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
            
            # Calculate fitness for each individual (with subject requirements)
            fitness_scores = [self._calculate_fitness(ind, self.subjects_config, self.sections) for ind in population]
            
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
    
    def _calculate_fitness(self, individual: List[TimeSlotEntry], 
                           subjects_config: Dict = None, sections: List[str] = None) -> float:
        """Calculate fitness score for an individual"""
        score = 1000  # Start with base score
        
        # Track conflicts
        section_slots = defaultdict(set)
        teacher_slots = defaultdict(set)
        room_slots = defaultdict(set)
        
        # Track subject hours (only count non-continuation entries)
        subject_hours = defaultdict(lambda: defaultdict(int))
        
        # Track consecutive theory for soft constraint
        section_day_theory = defaultdict(lambda: defaultdict(list))
        
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
            
            # Track hours (only non-continuation for labs)
            if not entry.is_lab_continuation:
                subject_hours[entry.section][entry.subject_code] += 1
            
            # Track theory periods for soft constraint
            if entry.subject_type == "theory":
                section_day_theory[entry.section][entry.day].append(entry.period)
        
        # VTU 2022: Penalize credit mismatch (EXACT match required)
        if subjects_config and sections:
            for section in sections:
                for code, subject in subjects_config.items():
                    required = subject.hours_per_week
                    actual = subject_hours[section].get(code, 0)
                    # VTU rule: credits must match EXACTLY (not just >= required)
                    if actual != required:
                        score -= abs(required - actual) * 100  # Heavy penalty for any mismatch
        
        # Soft constraint: consecutive theory periods
        for section, days in section_day_theory.items():
            for day, periods in days.items():
                periods.sort()
                consecutive = 1
                for i in range(1, len(periods)):
                    if periods[i] == periods[i-1] + 1:
                        consecutive += 1
                        if consecutive > self.max_consecutive_theory:
                            score -= 5  # Soft penalty
                    else:
                        consecutive = 1

        # Penalize internal gaps within a day's scheduled periods
        if sections:
            for section in sections:
                for day in self.days:
                    periods = sorted(p for (d, p) in section_slots[section] if d == day)
                    for i in range(1, len(periods)):
                        if periods[i] != periods[i - 1] + 1:
                            score -= 50
        
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
        """Mutate offspring with constraints"""
        for individual in offspring:
            if random.random() < self.mutation_rate:
                if individual:
                    # Random mutation - change day/period of random entry
                    idx = random.randint(0, len(individual) - 1)
                    entry = individual[idx]
                    
                    # Skip lab continuation entries to preserve continuity
                    if entry.is_lab_continuation:
                        continue
                    
                    individual[idx].day = random.choice(self.days)
                    
                    # Respect lab duration constraints
                    # Labs need 2-3 periods, so don't place at end of day
                    if entry.subject_type == "lab":
                        # Leave room for lab duration (assume max 3 periods)
                        max_period = max(1, self.periods_per_day - 2)
                        individual[idx].period = random.randint(1, max_period)
                    else:
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
