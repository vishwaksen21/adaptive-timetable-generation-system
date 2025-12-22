#!/usr/bin/env python3
"""
VTU Timetable Generation System - Main Entry Point
DSA-Based Adaptive Scheduling Algorithm

Usage:
    python run.py              - Start web server
    python run.py --cli        - Command-line generation
    python run.py --test       - Run tests
"""

import os
import sys
import argparse
import json
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config.vtu_config import (
    DAYS, PERIODS_PER_DAY, Branch, BRANCH_SECTIONS, SEMESTERS
)
from config.semester_subjects import get_subjects_for_semester, ALL_SEMESTER_SUBJECTS
from config.faculty_rooms import FACULTY_LIST, ROOM_LIST

from algorithms.dsa_scheduler import (
    create_scheduler, ConstraintSatisfactionScheduler, TimeSlotEntry
)
from algorithms.constraint_validator import ConstraintValidator


def get_time_display(period: int) -> str:
    """Get display time for a period"""
    time_map = {
        1: "08:00-09:00",
        2: "09:00-10:00",
        3: "10:20-11:20",
        4: "11:20-12:20",
        5: "13:00-14:00",
        6: "14:00-15:00",
        7: "15:00-16:00"
    }
    return time_map.get(period, "")


def print_timetable_text(timetable: dict, section: str):
    """Print timetable in text format"""
    print(f"\n{'='*100}")
    print(f"TIMETABLE - {section}")
    print(f"{'='*100}")
    
    # Header
    header = f"{'Day':<12}"
    for period in range(1, PERIODS_PER_DAY + 1):
        header += f"| {get_time_display(period):^13}"
    print(header)
    print("-" * 100)
    
    # Rows
    for day in DAYS:
        row = f"{day:<12}"
        for period in range(1, PERIODS_PER_DAY + 1):
            slot_key = (day, period)
            
            if section in timetable and slot_key in timetable[section]:
                entries = timetable[section][slot_key]
                if entries:
                    entry = entries[0]
                    cell = f"{entry.subject_short}/{entry.faculty_name}"
                    if entry.batch:
                        cell = f"{entry.subject_short}({entry.batch})"
                else:
                    cell = "-"
            else:
                cell = "-"
            
            row += f"| {cell:^13}"
        print(row)
    
    print("=" * 100)


def generate_timetable_cli(semester: int, branch: str, sections: list, 
                          algorithm: str = 'constraint_satisfaction',
                          debug_mode: bool = False):
    """Generate timetable from command line"""
    print(f"\n{'='*60}")
    print("VTU TIMETABLE GENERATION SYSTEM")
    print("DSA-Based Adaptive Scheduling Algorithm")
    print(f"{'='*60}")
    print(f"Semester: {semester}")
    print(f"Branch: {branch}")
    print(f"Sections: {', '.join(sections)}")
    print(f"Algorithm: {algorithm}")
    print(f"Debug Mode: {debug_mode}")
    print(f"{'='*60}\n")
    
    # Get subjects for semester
    subjects = get_subjects_for_semester(semester)
    subject_list = list(subjects.values())
    
    # Get faculty and rooms
    faculty_list = list(FACULTY_LIST.values())
    room_list = list(ROOM_LIST.values())
    
    # Get section batches
    section_batches = {}
    branch_enum = Branch.AIDS if branch == 'AIDS' else Branch.CSDS
    for section in sections:
        section_batches[section] = BRANCH_SECTIONS[branch_enum]['batches_per_section'].get(section, [])
    
    # Create scheduler configuration
    config = {
        'algorithm_type': algorithm,
        'debug_mode': debug_mode,
        'timeout_seconds': 120,
        'days': DAYS,
        'periods_per_day': PERIODS_PER_DAY,
        'max_consecutive_theory': 3,
        'prefer_morning_labs': True,
        'limit_first_period': 3,
        'population_size': 100,
        'generations': 300,
        'mutation_rate': 0.15,
        'crossover_rate': 0.8
    }
    
    print("Generating timetable...")
    print(f"Total subjects: {len(subject_list)}")
    print(f"Total faculty: {len(faculty_list)}")
    print(f"Total rooms: {len(room_list)}")
    print()
    
    # Create and run scheduler
    import time
    start_time = time.time()
    scheduler = create_scheduler(config)
    
    if algorithm == 'genetic':
        success, timetable, violations = scheduler.schedule(
            sections, subject_list, faculty_list, room_list, section_batches
        )
    else:
        success, timetable = scheduler.schedule_with_backtracking(
            sections, subject_list, faculty_list, room_list, section_batches
        )
        violations = []
    
    generation_time = time.time() - start_time
    
    print(f"\n{'='*60}")
    print("GENERATION RESULTS")
    print(f"{'='*60}")
    print(f"Success: {success}")
    print(f"Generation Time: {generation_time:.2f} seconds")
    print(f"Backtrack Count: {scheduler.backtrack_count if hasattr(scheduler, 'backtrack_count') else 'N/A'}")
    print(f"Total Attempts: {scheduler.total_attempts if hasattr(scheduler, 'total_attempts') else 'N/A'}")
    
    # Validate
    validator = ConstraintValidator(config)
    validation = validator.validate(timetable, subjects, sections)
    
    print(f"\nValidation:")
    print(f"  Is Valid: {validation.is_valid}")
    print(f"  Quality Score: {validation.score}")
    print(f"  Hard Violations: {len(validation.hard_violations)}")
    print(f"  Soft Violations: {len(validation.soft_violations)}")
    
    if validation.hard_violations:
        print("\nHard Constraint Violations:")
        for v in validation.hard_violations[:5]:
            print(f"  - {v['type']}: {v['description']}")
    
    # Print timetables
    for section in sections:
        print_timetable_text(timetable, section)
    
    # Save to file
    output_dir = 'data/generated_timetables'
    os.makedirs(output_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"{output_dir}/timetable_sem{semester}_{branch}_{timestamp}.json"
    
    # Convert to JSON-serializable format
    json_data = {
        'metadata': {
            'semester': semester,
            'branch': branch,
            'sections': sections,
            'generated_at': datetime.now().isoformat(),
            'algorithm': algorithm,
            'generation_time': generation_time,
            'success': success,
            'validation': {
                'is_valid': validation.is_valid,
                'score': validation.score,
                'hard_violations': len(validation.hard_violations),
                'soft_violations': len(validation.soft_violations)
            }
        },
        'timetables': {}
    }
    
    for section in sections:
        json_data['timetables'][section] = {
            'days': []
        }
        
        for day in DAYS:
            day_data = {'name': day, 'slots': []}
            
            for period in range(1, PERIODS_PER_DAY + 1):
                slot_key = (day, period)
                slot_data = {
                    'period': period,
                    'time': get_time_display(period),
                    'classes': []
                }
                
                if section in timetable and slot_key in timetable[section]:
                    for entry in timetable[section][slot_key]:
                        slot_data['classes'].append({
                            'subject_code': entry.subject_code,
                            'subject_short': entry.subject_short,
                            'subject_type': entry.subject_type,
                            'faculty': entry.faculty_name,
                            'room': entry.room_number,
                            'batch': entry.batch
                        })
                
                day_data['slots'].append(slot_data)
            
            json_data['timetables'][section]['days'].append(day_data)
    
    with open(filename, 'w') as f:
        json.dump(json_data, f, indent=2)
    
    print(f"\nTimetable saved to: {filename}")
    
    return success, timetable


def run_web_server():
    """Run the Flask web server"""
    print("\n" + "="*60)
    print("VTU TIMETABLE GENERATION SYSTEM - WEB SERVER")
    print("="*60)
    print("\nStarting web server...")
    print("Open http://localhost:5000 in your browser")
    print("\nPress Ctrl+C to stop the server\n")
    
    from app.web_app import app
    app.run(debug=True, host='0.0.0.0', port=5000)


def run_tests():
    """Run system tests"""
    print("\n" + "="*60)
    print("VTU TIMETABLE GENERATION SYSTEM - TESTS")
    print("="*60 + "\n")
    
    # Test 1: Configuration Loading
    print("Test 1: Configuration Loading...")
    try:
        from config.vtu_config import DAYS, TIME_SLOTS, PERIODS_PER_DAY
        from config.semester_subjects import ALL_SEMESTER_SUBJECTS
        from config.faculty_rooms import FACULTY_LIST, ROOM_LIST
        
        assert len(DAYS) == 6, "Should have 6 days (Mon-Sat)"
        assert PERIODS_PER_DAY == 7, "Should have 7 periods"
        assert len(ALL_SEMESTER_SUBJECTS) == 4, "Should have 4 semesters"
        assert len(FACULTY_LIST) > 0, "Should have faculty"
        assert len(ROOM_LIST) > 0, "Should have rooms"
        
        print("  ✓ Configuration loaded successfully")
    except Exception as e:
        print(f"  ✗ Failed: {e}")
        return False
    
    # Test 2: Scheduler Creation
    print("\nTest 2: Scheduler Creation...")
    try:
        from algorithms.dsa_scheduler import create_scheduler
        
        config = {
            'algorithm_type': 'constraint_satisfaction',
            'debug_mode': False,
            'timeout_seconds': 60,
            'days': DAYS,
            'periods_per_day': 7
        }
        
        scheduler = create_scheduler(config)
        assert scheduler is not None
        print("  ✓ Scheduler created successfully")
    except Exception as e:
        print(f"  ✗ Failed: {e}")
        return False
    
    # Test 3: Subject Loading
    print("\nTest 3: Subject Loading...")
    try:
        from config.semester_subjects import get_subjects_for_semester
        
        for sem in [3, 4, 5, 6]:
            subjects = get_subjects_for_semester(sem)
            assert len(subjects) > 0, f"Semester {sem} should have subjects"
            print(f"  ✓ Semester {sem}: {len(subjects)} subjects")
    except Exception as e:
        print(f"  ✗ Failed: {e}")
        return False
    
    # Test 4: Mini Timetable Generation
    print("\nTest 4: Mini Timetable Generation (5th Semester, AIDS-A)...")
    try:
        success, timetable = generate_timetable_cli(
            semester=5,
            branch='AIDS',
            sections=['AIDS-A'],
            algorithm='constraint_satisfaction',
            debug_mode=False
        )
        
        if success:
            print("  ✓ Timetable generated successfully")
        else:
            print("  ⚠ Timetable generated with some issues")
    except Exception as e:
        print(f"  ✗ Failed: {e}")
        return False
    
    print("\n" + "="*60)
    print("ALL TESTS COMPLETED")
    print("="*60 + "\n")
    return True


def main():
    parser = argparse.ArgumentParser(
        description='VTU Timetable Generation System - DSA-Based Scheduling'
    )
    parser.add_argument('--cli', action='store_true', 
                        help='Run in CLI mode')
    parser.add_argument('--test', action='store_true',
                        help='Run tests')
    parser.add_argument('--semester', type=int, choices=[3, 4, 5, 6], default=5,
                        help='Semester (3-6)')
    parser.add_argument('--branch', choices=['AIDS', 'CSDS'], default='AIDS',
                        help='Branch')
    parser.add_argument('--sections', nargs='+', 
                        default=['AIDS-A', 'AIDS-B'],
                        help='Sections to generate')
    parser.add_argument('--algorithm', 
                        choices=['constraint_satisfaction', 'genetic', 'hybrid'],
                        default='constraint_satisfaction',
                        help='Scheduling algorithm')
    parser.add_argument('--debug', action='store_true',
                        help='Enable debug mode')
    
    args = parser.parse_args()
    
    if args.test:
        run_tests()
    elif args.cli:
        generate_timetable_cli(
            semester=args.semester,
            branch=args.branch,
            sections=args.sections,
            algorithm=args.algorithm,
            debug_mode=args.debug
        )
    else:
        run_web_server()


if __name__ == '__main__':
    main()
