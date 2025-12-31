"""Verification script for CMRIT Timetable Generation System"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config.vtu_config import DAYS, PERIODS_PER_DAY
from config.semester_subjects import get_subjects_for_semester, ALL_SEMESTER_SUBJECTS
from config.faculty_rooms import FACULTY_LIST, ROOM_LIST
from algorithms.dsa_scheduler import create_scheduler
from algorithms.constraint_validator import ConstraintValidator

def verify_system():
    """Verify all system components"""
    print("=" * 80)
    print("CMRIT TIMETABLE GENERATION SYSTEM - VERIFICATION")
    print("=" * 80)
    
    # 1. Check VTU configuration
    print("\n1. VTU CONFIGURATION:")
    print("-" * 80)
    print(f"   Days per week: {len(DAYS)} ({', '.join(DAYS)})")
    print(f"   Periods per day: {PERIODS_PER_DAY}")
    print(f"   Total slots per week: {len(DAYS) * PERIODS_PER_DAY}")
    
    # 2. Check subjects configuration
    print("\n2. SUBJECTS CONFIGURATION (Semester 5):")
    print("-" * 80)
    semester = 5
    subjects = get_subjects_for_semester(semester)
    total_credits = 0
    total_hours = 0
    for code, subject in sorted(subjects.items()):
        credits = getattr(subject, 'credits', 0)
        hours = getattr(subject, 'hours_per_week', 0)
        total_credits += credits
        total_hours += hours
        print(f"   {subject.short_name:8} | {code:10} | {subject.subject_type:12} | Credits: {credits} | Hours: {hours}")
    print(f"\n   Total Credits: {total_credits}")
    print(f"   Total Hours Required: {total_hours}")
    
    # 3. Check faculty
    print("\n3. FACULTY VERIFICATION:")
    print("-" * 80)
    print(f"   Total Faculty: {len(FACULTY_LIST)}")
    for fac_id, faculty in list(FACULTY_LIST.items())[:5]:
        subjects_str = ', '.join(faculty.subjects[:3])
        if len(faculty.subjects) > 3:
            subjects_str += f" ... ({len(faculty.subjects)} total)"
        print(f"   {faculty.short_name:6} | {faculty.name:25} | Subjects: {subjects_str}")
    if len(FACULTY_LIST) > 5:
        print(f"   ... and {len(FACULTY_LIST) - 5} more faculty members")
    
    # 4. Check rooms
    print("\n4. ROOM VERIFICATION:")
    print("-" * 80)
    room_types = {}
    for room_id, room in ROOM_LIST.items():
        room_type = getattr(room, 'room_type', 'unknown')
        room_types[room_type] = room_types.get(room_type, 0) + 1
    print(f"   Total Rooms: {len(ROOM_LIST)}")
    for room_type, count in sorted(room_types.items()):
        print(f"   {room_type:20}: {count} rooms")
    
    # 5. Test scheduling
    print("\n5. SCHEDULING TEST:")
    print("-" * 80)
    sections = ['AIDS-A', 'AIDS-B']
    section_batches = {
        'AIDS-A': ['A1', 'A2', 'A3'],
        'AIDS-B': ['B1', 'B2', 'B3']
    }
    
    config = {
        'algorithm_type': 'constraint_satisfaction',
        'debug_mode': False,
        'timeout_seconds': 30,
        'days': DAYS,
        'periods_per_day': PERIODS_PER_DAY,
        'max_consecutive_theory': 3,
        'prefer_morning_labs': True,
        'limit_first_period': 3
    }
    
    scheduler = create_scheduler(config)
    subject_list = list(subjects.values())
    faculty_list = list(FACULTY_LIST.values())
    room_list = list(ROOM_LIST.values())
    
    print("   Generating timetable...")
    success, timetable = scheduler.schedule_greedy(
        sections=sections,
        subjects=subject_list,
        faculty_list=faculty_list,
        room_list=room_list,
        section_batches=section_batches
    )
    
    if success:
        print(f"   ✅ Timetable generated successfully!")
        
        # Validate constraints
        validator = ConstraintValidator(config)
        result = validator.validate(timetable, {s.code: s for s in subject_list}, sections)
        
        print(f"\n   Validation Results:")
        print(f"   - Valid: {result.is_valid}")
        print(f"   - Hard Violations: {len(result.hard_violations)}")
        print(f"   - Soft Violations: {len(result.soft_violations)}")
        print(f"   - Score: {result.score:.2f}")
        
        if result.hard_violations:
            print(f"\n   Hard Violations:")
            for v in result.hard_violations[:5]:
                print(f"   - {v['type']}: {v['description']}")
            if len(result.hard_violations) > 5:
                print(f"   ... and {len(result.hard_violations) - 5} more violations")
        
        # Check slot utilization
        for section in sections:
            filled_slots = len(timetable.get(section, {}))
            print(f"\n   {section}: {filled_slots}/{len(DAYS) * PERIODS_PER_DAY} slots filled")
    else:
        print(f"   ❌ Timetable generation failed!")
        return False
    
    # 6. Summary
    print("\n" + "=" * 80)
    print("VERIFICATION COMPLETE")
    print("=" * 80)
    if success and result.is_valid and len(result.hard_violations) == 0:
        print("✅ All checks passed! System is working correctly.")
        return True
    else:
        print("⚠️  Some issues detected. Please review the output above.")
        return False

if __name__ == "__main__":
    success = verify_system()
    sys.exit(0 if success else 1)
    
    # 4. Check credit hours
    print("\n4. CREDIT HOUR DISTRIBUTION:")
    print("-" * 60)
    theory_hours = sum(SUBJECTS[s]["credits"] for s in SUBJECTS)
    lab_hours = sum(2 for s in SUBJECTS if SUBJECTS[s].get("labs_per_week", 0) > 0)  # 2 hrs per lab
    activity_hours = 2 + 2 + 1 + 1  # Club(2) + Sports(2) + NSS(1) + Yoga(1)
    
    print(f"   Theory Classes per Section: {theory_hours} hours/week")
    print(f"   Lab Classes (total): {lab_hours} hours/week")
    print(f"   Activities (total): {activity_hours} hours/week")
    print(f"   Total: {theory_hours + lab_hours + activity_hours} hours/week")
    
    # 5. Check output files
    print("\n5. OUTPUT FILES:")
    print("-" * 60)
    import os
    output_files = [
        'data/final_timetable.csv',
        'data/section_timetables'
    ]
    
    for filepath in output_files:
        if os.path.exists(filepath):
            if os.path.isdir(filepath):
                sections_count = len([f for f in os.listdir(filepath) if f.endswith('.txt')])
                print(f"   ✅ {filepath}: {sections_count} section timetables")
            else:
                size = os.path.getsize(filepath)
                print(f"   ✅ {filepath}: {size} bytes")
        else:
            print(f"   ⚠️  {filepath}: Not yet created")
    
    print("\n" + "=" * 60)
    print("VERIFICATION COMPLETE!")
    print("=" * 60)