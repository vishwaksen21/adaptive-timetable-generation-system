"""
Constraint Validation System for VTU Timetable
"""

from typing import Dict, List, Tuple, Set
from collections import defaultdict
from dataclasses import dataclass

@dataclass
class ValidationResult:
    """Result of constraint validation"""
    is_valid: bool
    hard_violations: List[dict]
    soft_violations: List[dict]
    score: float
    details: dict

class ConstraintValidator:
    """
    Validates timetable against all hard and soft constraints
    """
    
    def __init__(self, config: dict):
        self.config = config
        self.max_consecutive_theory = config.get('max_consecutive_theory', 3)
        self.limit_first_period = config.get('limit_first_period', 3)
        self.days = config.get('days', ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"])
        self.periods_per_day = config.get('periods_per_day', 7)
    
    def validate(self, timetable: Dict, subjects_config: Dict, 
                 sections: List[str]) -> ValidationResult:
        """
        Validate complete timetable against all constraints
        """
        hard_violations = []
        soft_violations = []
        
        # Track schedules
        teacher_schedule = defaultdict(set)
        room_schedule = defaultdict(set)
        section_schedule = defaultdict(set)
        subject_hours = defaultdict(lambda: defaultdict(int))
        
        # Process all entries
        for section, slots in timetable.items():
            for (day, period), entries in slots.items():
                for entry in entries:
                    slot_key = (day, period)
                    
                    # 1. Check section clash
                    if slot_key in section_schedule[section] and not entry.batch:
                        hard_violations.append({
                            'type': 'section_clash',
                            'description': f'Section {section} has multiple classes at {day} period {period}',
                            'affected': [entry]
                        })
                    section_schedule[section].add(slot_key)
                    
                    # 2. Check teacher clash
                    if slot_key in teacher_schedule[entry.faculty_id]:
                        hard_violations.append({
                            'type': 'teacher_clash',
                            'description': f'Teacher {entry.faculty_name} has clash at {day} period {period}',
                            'affected': [entry]
                        })
                    teacher_schedule[entry.faculty_id].add(slot_key)
                    
                    # 3. Check room clash
                    if slot_key in room_schedule[entry.room_number]:
                        hard_violations.append({
                            'type': 'room_clash',
                            'description': f'Room {entry.room_number} double-booked at {day} period {period}',
                            'affected': [entry]
                        })
                    room_schedule[entry.room_number].add(slot_key)
                    
                    # Track subject hours
                    if not entry.is_lab_continuation:
                        subject_hours[section][entry.subject_code] += 1
        
        # 4. Check required hours
        for section in sections:
            for code, subject in subjects_config.items():
                required = subject.hours_per_week
                actual = subject_hours[section].get(code, 0)
                
                if actual < required:
                    hard_violations.append({
                        'type': 'missing_hours',
                        'description': f'{section}: {subject.name} has {actual}/{required} hours',
                        'affected': []
                    })
        
        # 5. Check soft constraints
        for section, slots in timetable.items():
            # Check consecutive theory periods
            for day in self.days:
                consecutive = 0
                for period in range(1, self.periods_per_day + 1):
                    if (day, period) in slots:
                        entries = slots[(day, period)]
                        if any(e.subject_type == 'theory' for e in entries):
                            consecutive += 1
                        else:
                            consecutive = 0
                    else:
                        consecutive = 0
                    
                    if consecutive > self.max_consecutive_theory:
                        soft_violations.append({
                            'type': 'consecutive_theory',
                            'description': f'{section}: {consecutive} consecutive theory on {day}',
                            'penalty': (consecutive - self.max_consecutive_theory) * 5
                        })
            
            # Check first period usage
            first_period_count = sum(
                1 for day in self.days
                if (day, 1) in slots
            )
            if first_period_count > self.limit_first_period:
                soft_violations.append({
                    'type': 'early_slots',
                    'description': f'{section}: 8 AM slot used {first_period_count} times',
                    'penalty': (first_period_count - self.limit_first_period) * 2
                })
        
        # Calculate score
        base_score = 1000
        hard_penalty = len(hard_violations) * 100
        soft_penalty = sum(v.get('penalty', 1) for v in soft_violations)
        score = base_score - hard_penalty - soft_penalty
        
        return ValidationResult(
            is_valid=(len(hard_violations) == 0),
            hard_violations=hard_violations,
            soft_violations=soft_violations,
            score=score,
            details={
                'total_entries': sum(
                    len(entries) for slots in timetable.values() 
                    for entries in slots.values()
                ),
                'sections': list(timetable.keys()),
                'subject_hours': dict(subject_hours)
            }
        )
    
    def validate_single_entry(self, entry, timetable: Dict,
                              teacher_schedule: Dict,
                              room_schedule: Dict) -> Tuple[bool, List[str]]:
        """
        Validate a single entry against current state
        """
        violations = []
        day = entry.day
        period = entry.period
        section = entry.section
        slot_key = (day, period)
        
        # Check section clash
        if section in timetable:
            if slot_key in timetable[section]:
                existing = timetable[section][slot_key]
                if existing and not any(e.batch for e in existing):
                    violations.append(f"Section {section} already has class at {day} P{period}")
        
        # Check teacher clash
        if entry.faculty_id in teacher_schedule:
            if slot_key in teacher_schedule[entry.faculty_id]:
                violations.append(f"Teacher {entry.faculty_name} busy at {day} P{period}")
        
        # Check room clash
        if entry.room_number in room_schedule:
            if slot_key in room_schedule[entry.room_number]:
                violations.append(f"Room {entry.room_number} occupied at {day} P{period}")
        
        return len(violations) == 0, violations


class LabContinuityValidator:
    """
    Validates lab sessions are in continuous blocks
    """
    
    def validate_lab_continuity(self, timetable: Dict) -> List[dict]:
        """Check all labs are in continuous blocks"""
        violations = []
        
        for section, slots in timetable.items():
            # Group entries by subject
            subject_slots = defaultdict(list)
            
            for (day, period), entries in slots.items():
                for entry in entries:
                    if entry.subject_type == 'lab':
                        subject_slots[entry.subject_code].append((day, period, entry))
            
            # Check continuity for each lab
            for subject, slot_list in subject_slots.items():
                # Group by day
                by_day = defaultdict(list)
                for day, period, entry in slot_list:
                    by_day[day].append((period, entry))
                
                for day, periods in by_day.items():
                    periods.sort(key=lambda x: x[0])
                    
                    # Check if periods are consecutive
                    for i in range(1, len(periods)):
                        if periods[i][0] != periods[i-1][0] + 1:
                            violations.append({
                                'type': 'lab_not_continuous',
                                'description': f'{section}: {subject} not continuous on {day}',
                                'affected': [periods[i][1], periods[i-1][1]]
                            })
        
        return violations


class BatchLabValidator:
    """
    Validates batch-wise lab scheduling
    """
    
    def validate_batch_labs(self, timetable: Dict, 
                           section_batches: Dict[str, List[str]]) -> List[dict]:
        """Validate batch labs are properly scheduled"""
        violations = []
        
        for section, slots in timetable.items():
            batches = section_batches.get(section, [])
            if not batches:
                continue
            
            # Group lab entries by subject
            lab_by_subject = defaultdict(list)
            
            for (day, period), entries in slots.items():
                for entry in entries:
                    if entry.subject_type == 'lab' and entry.batch:
                        lab_by_subject[entry.subject_code].append(entry)
            
            # Check each lab has all batches scheduled
            for subject, entries in lab_by_subject.items():
                scheduled_batches = set(e.batch for e in entries if e.batch)
                missing = set(batches) - scheduled_batches
                
                if missing:
                    violations.append({
                        'type': 'missing_batch',
                        'description': f'{section}: {subject} missing batches {missing}',
                        'affected': []
                    })
        
        return violations
