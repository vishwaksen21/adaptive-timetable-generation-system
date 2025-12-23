#!/usr/bin/env python3
"""Test the scheduler to debug empty slots"""

import logging
logging.basicConfig(level=logging.INFO)

from config.vtu_config import DAYS, PERIODS_PER_DAY
from config.semester_subjects import get_subjects_for_semester
from config.faculty_rooms import FACULTY_LIST, ROOM_LIST
from algorithms.dsa_scheduler import create_scheduler

# Setup
semester = 5
sections = ['AIDS-A', 'AIDS-B']
section_batches = {
    'AIDS-A': ['A1', 'A2', 'A3'],
    'AIDS-B': ['B1', 'B2', 'B3']
}

subjects = get_subjects_for_semester(semester)
subject_list = list(subjects.values())
faculty_list = list(FACULTY_LIST.values())
room_list = list(ROOM_LIST.values())

# Print total required hours
print("=== Subject Hours Breakdown ===")
total_theory_hours = 0
total_lab_hours = 0
for s in subject_list:
    if s.subject_type == "lab":
        print(f"  {s.short_name}: {s.hours_per_week}h (lab, {s.lab_duration}h sessions)")
        total_lab_hours += s.hours_per_week
    else:
        print(f"  {s.short_name}: {s.hours_per_week}h ({s.subject_type})")
        total_theory_hours += s.hours_per_week
        
print(f"\nTotal theory/activity hours: {total_theory_hours}")
print(f"Total lab hours: {total_lab_hours}")
print(f"Available slots per section: {len(DAYS)} days * {PERIODS_PER_DAY} periods = {len(DAYS) * PERIODS_PER_DAY}")
print()

config = {
    'algorithm_type': 'constraint_satisfaction',
    'debug_mode': True,
    'timeout_seconds': 30,
    'days': DAYS,
    'periods_per_day': PERIODS_PER_DAY,
    'max_consecutive_theory': 3,
    'prefer_morning_labs': True,
    'limit_first_period': 3
}

scheduler = create_scheduler(config)
success, timetable = scheduler.schedule_greedy(
    sections, subject_list, faculty_list, room_list, section_batches
)

print(f'\n=== Results ===')
print(f'Success: {success}')
print(f'Sections in timetable: {list(timetable.keys())}')

# Count slots for each section
for section in sections:
    if section in timetable:
        total_slots = len(DAYS) * PERIODS_PER_DAY
        filled_slots = len(timetable[section])
        print(f'\n{section}: {filled_slots}/{total_slots} slots filled')
        
        # Show what's scheduled
        subject_counts = {}
        for slot, entries in timetable[section].items():
            for entry in entries:
                key = f"{entry.subject_short}" + (f"({entry.batch})" if entry.batch else "")
                subject_counts[key] = subject_counts.get(key, 0) + 1
        
        print(f"Subject counts: {subject_counts}")
        
        # Show empty slots
        empty_slots = []
        for day in DAYS:
            for period in range(1, PERIODS_PER_DAY + 1):
                if (day, period) not in timetable[section]:
                    empty_slots.append(f'{day[:3]} P{period}')
        print(f'Empty slots ({len(empty_slots)}): {empty_slots}')
        
        # Show sample schedule for Monday
        print(f"\nMonday schedule for {section}:")
        for p in range(1, PERIODS_PER_DAY + 1):
            if ('Monday', p) in timetable[section]:
                entries = timetable[section][('Monday', p)]
                names = [f"{e.subject_short}" + (f"({e.batch})" if e.batch else "") for e in entries]
                print(f"  P{p}: {', '.join(names)}")
            else:
                print(f"  P{p}: (empty)")
    else:
        print(f'No timetable for {section}')
