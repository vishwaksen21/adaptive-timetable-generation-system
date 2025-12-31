from typing import Dict, List, Tuple
from collections import defaultdict
from dataclasses import dataclass

@dataclass
class ValidationResult:
    is_valid: bool
    hard_violations: List[dict]
    soft_violations: List[dict]
    score: float
    details: dict


class ConstraintValidator:
    def __init__(self, config: dict):
        self.config = config
        self.max_consecutive_theory = config.get('max_consecutive_theory', 3)
        self.limit_first_period = config.get('limit_first_period', 3)
        self.days = config.get(
            'days',
            ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
        )
        self.periods_per_day = config.get('periods_per_day', 7)

    def validate(self, timetable: Dict, subjects_config: Dict,
                 sections: List[str]) -> ValidationResult:

        hard_violations = []
        soft_violations = []

        teacher_schedule = defaultdict(lambda: defaultdict(list))
        room_schedule = defaultdict(lambda: defaultdict(list))
        section_schedule = defaultdict(lambda: defaultdict(list))

        subject_slots = defaultdict(lambda: defaultdict(set))

        # ---------- MAIN SCAN ----------
        for section, slots in timetable.items():
            for (day, period), entries in slots.items():
                slot_key = (day, period)

                existing_section = section_schedule[section][slot_key]

                for entry in entries:
                    # 1. Section clash
                    if existing_section:
                        if not any(e.batch for e in existing_section) and not entry.batch:
                            hard_violations.append({
                                'type': 'section_clash',
                                'description': f'{section} has multiple classes at {day} P{period}',
                                'affected': [entry]
                            })
                        elif entry.batch and any(e.batch == entry.batch for e in existing_section):
                            hard_violations.append({
                                'type': 'section_clash',
                                'description': f'{section} batch {entry.batch} duplicated at {day} P{period}',
                                'affected': [entry]
                            })
                        elif not entry.batch and any(e.batch for e in existing_section):
                            hard_violations.append({
                                'type': 'section_clash',
                                'description': f'{section} theory overlaps lab at {day} P{period}',
                                'affected': [entry]
                            })

                    section_schedule[section][slot_key].append(entry)

                    # 2. Teacher clash (batch-parallel same subject only)
                    t_existing = teacher_schedule[entry.faculty_id][slot_key]
                    if t_existing:
                        allowed = (
                            entry.batch is not None and
                            all(
                                e.batch is not None and
                                e.section == section and
                                e.subject_code == entry.subject_code
                                for e in t_existing
                            )
                        )
                        if not allowed:
                            hard_violations.append({
                                'type': 'teacher_clash',
                                'description': f'Teacher {entry.faculty_name} clash at {day} P{period}',
                                'affected': [entry]
                            })

                    teacher_schedule[entry.faculty_id][slot_key].append(entry)

                    # 3. Room clash
                    if room_schedule[entry.room_number][slot_key]:
                        hard_violations.append({
                            'type': 'room_clash',
                            'description': f'Room {entry.room_number} double-booked at {day} P{period}',
                            'affected': [entry]
                        })

                    room_schedule[entry.room_number][slot_key].append(entry)

                # Subject hours (dedupe parallel batches)
                for code in {e.subject_code for e in entries}:
                    subject_slots[section][code].add(slot_key)

        # ---------- CREDIT CHECK ----------
        for section in sections:
            for code, subject in subjects_config.items():
                actual = len(subject_slots[section].get(code, set()))
                required = subject.hours_per_week
                if actual != required:
                    hard_violations.append({
                        'type': 'credit_mismatch',
                        'description': f'{section}: {subject.short_name} {actual}/{required} hours',
                        'affected': []
                    })

        # ---------- GAP CHECK ----------
        for section in sections:
            slots = timetable.get(section, {})
            by_day = defaultdict(list)
            for (day, period) in slots:
                by_day[day].append(period)

            for day, periods in by_day.items():
                if len(periods) <= 1:
                    continue
                lo, hi = min(periods), max(periods)
                for p in range(lo, hi + 1):
                    if (day, p) not in slots:
                        hard_violations.append({
                            'type': 'gap',
                            'description': f'{section}: gap at {day} P{p}',
                            'affected': []
                        })

        # ---------- LAB BLOCK CHECK ----------
        for section in sections:
            labs = defaultdict(lambda: defaultdict(list))
            for (day, period), entries in timetable.get(section, {}).items():
                for e in entries:
                    if e.subject_type == 'lab':
                        labs[e.subject_code][day].append((period, e))

            for code, by_day in labs.items():
                for day, items in by_day.items():
                    # Distinct periods for this lab (batch labs will have multiple entries per period)
                    distinct_periods = sorted({p for p, _ in items})
                    if len(distinct_periods) != 2 or distinct_periods[1] != distinct_periods[0] + 1:
                        hard_violations.append({
                            'type': 'lab_block',
                            'description': f'{section}: {code} lab must be 2 consecutive periods on {day}',
                            'affected': []
                        })
                        continue

                    # Valid 2-hour starts: (1,2), (3,4), (5,6)
                    if distinct_periods[0] not in (1, 3, 5):
                        hard_violations.append({
                            'type': 'lab_block',
                            'description': f'{section}: {code} lab starts at invalid period on {day}',
                            'affected': []
                        })

                    # Batch consistency: if batches are used, the set of batches must match in both periods
                    p1, p2 = distinct_periods[0], distinct_periods[1]
                    batches_p1 = {e.batch for p, e in items if p == p1 and e.batch is not None}
                    batches_p2 = {e.batch for p, e in items if p == p2 and e.batch is not None}
                    if batches_p1 or batches_p2:
                        if not batches_p1 or not batches_p2 or batches_p1 != batches_p2:
                            hard_violations.append({
                                'type': 'lab_block',
                                'description': f'{section}: {code} inconsistent batches across the 2 lab periods on {day}',
                                'affected': []
                            })

        # ---------- SOFT CONSTRAINTS ----------
        for section, slots in timetable.items():
            for day in self.days:
                consecutive = 0
                for p in range(1, self.periods_per_day + 1):
                    if (day, p) in slots and any(e.subject_type == 'theory' for e in slots[(day, p)]):
                        consecutive += 1
                        if consecutive > self.max_consecutive_theory:
                            soft_violations.append({
                                'type': 'consecutive_theory',
                                'description': f'{section}: {consecutive} theory periods on {day}',
                                'penalty': (consecutive - self.max_consecutive_theory) * 5
                            })
                    else:
                        consecutive = 0

            first_p = sum(1 for d in self.days if (d, 1) in slots)
            if first_p > self.limit_first_period:
                soft_violations.append({
                    'type': 'early_slots',
                    'description': f'{section}: first period used {first_p} times',
                    'penalty': (first_p - self.limit_first_period) * 2
                })

        score = 1000 - len(hard_violations) * 100 - sum(v.get('penalty', 1) for v in soft_violations)

        return ValidationResult(
            is_valid=(not hard_violations),
            hard_violations=hard_violations,
            soft_violations=soft_violations,
            score=score,
            details={
                'sections': sections,
                'subject_hours': {
                    sec: {c: len(s) for c, s in subj.items()}
                    for sec, subj in subject_slots.items()
                }
            }
        )


# ---------------------------------------------------------------------------
# Legacy validators (kept for backward compatibility)
# ---------------------------------------------------------------------------

class LabContinuityValidator:
    """Legacy helper: validates only lab continuity rules.

    This project now uses ConstraintValidator as the single source of truth,
    but algorithms/__init__.py historically exported LabContinuityValidator.
    """

    def __init__(self, config: dict):
        self._validator = ConstraintValidator(config)

    def validate(self, timetable: Dict, subjects_config: Dict, sections: List[str]) -> List[dict]:
        result = self._validator.validate(timetable, subjects_config, sections)
        return [v for v in result.hard_violations if v.get('type') == 'lab_block']


class BatchLabValidator:
    """Legacy helper: validates batch-parallel lab rules.

    Batch-parallel semantics are enforced as part of ConstraintValidator.
    This class is retained to satisfy older imports.
    """

    def __init__(self, config: dict):
        self._validator = ConstraintValidator(config)

    def validate(self, timetable: Dict, subjects_config: Dict, sections: List[str]) -> List[dict]:
        result = self._validator.validate(timetable, subjects_config, sections)
        # Batch issues are reported under lab_block and teacher_clash/section_clash.
        return [
            v for v in result.hard_violations
            if v.get('type') in ('lab_block', 'teacher_clash', 'section_clash')
        ]
