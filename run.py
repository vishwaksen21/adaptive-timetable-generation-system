#!/usr/bin/env python3
"""
CMRIT Timetable Generation System - Main Entry Point
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


# ============================================================
# CMRIT-STYLE TIMETABLE FORMATTING (College/Notice Board Format)
# ============================================================

# Time slots including breaks (for CMRIT-style table)
VTU_TIME_SLOTS = [
    "08:00-09:00",
    "09:00-10:00",
    "10:00-10:20",  # SHORT BREAK
    "10:20-11:20",
    "11:20-12:20",
    "12:20-13:00",  # LUNCH BREAK
    "13:00-14:00",
    "14:00-15:00",
    "15:00-16:00"
]

# Map periods to table columns (0-indexed)
PERIOD_TO_COLUMN = {
    1: 0,   # 08:00-09:00
    2: 1,   # 09:00-10:00
    # 2 = SHORT BREAK
    3: 3,   # 10:20-11:20
    4: 4,   # 11:20-12:20
    # 5 = LUNCH BREAK
    5: 6,   # 13:00-14:00
    6: 7,   # 14:00-15:00
    7: 8    # 15:00-16:00
}

# Subject groups for merged display (like college timetables)
SUBJECT_GROUPS = {
    "CC/CV/NOSQL": ["CC", "CV", "NOSQL"],
    "TYL": ["TYL-L", "TYL-T", "TYL-A", "TYL"],
    "9LPA": ["9LPA"],
}


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


def display_subject(entries) -> str:
    """Format subject display with grouping for similar subjects"""
    if not entries:
        return ""
    
    codes = sorted(set(e.subject_short for e in entries))
    
    # Check if entries match a subject group
    for group_name, members in SUBJECT_GROUPS.items():
        if all(m in codes for m in members):
            return group_name
    
    # For labs, show with batches
    if any(e.subject_type == "lab" for e in entries):
        return display_lab(entries)
    
    # Single subject
    if len(codes) == 1:
        entry = entries[0]
        return f"{entry.subject_short}"
    
    # Multiple subjects in same slot (parallel)
    return " / ".join(codes)


def display_lab(entries) -> str:
    """Format lab display with batch information"""
    if not entries:
        return "FREE"
    
    subject = entries[0].subject_short
    batches = sorted(set(e.batch for e in entries if e.batch))
    
    if batches:
        return f"{subject}\n{' / '.join(batches)}"
    return f"{subject}"


def convert_to_vtu_table(timetable: dict, section: str, days: list) -> dict:
    """
    Convert internal timetable to CMRIT-style table matrix (Day × Time)
    Returns: {day: [col0, col1, ..., col8]} with breaks included
    """
    table = {day: [""] * 9 for day in days}
    
    if section not in timetable:
        return table
    
    # Track merged cells for labs (spanning multiple periods)
    merged_cells = {}  # (day, start_col): span_count
    
    for (day, period), entries in timetable[section].items():
        col = PERIOD_TO_COLUMN.get(period)
        if col is None:
            continue
        
        # Skip if this is a continuation (already merged)
        if any(e.is_lab_continuation for e in entries):
            continue
        
        # Format cell content
        text = display_subject(entries)
        table[day][col] = text
        
        # Check for lab spanning multiple periods
        entry = entries[0] if entries else None
        if entry and entry.subject_type == "lab":
            # Look for continuation in next period
            next_period = period + 1
            if (day, next_period) in timetable[section]:
                next_entries = timetable[section][(day, next_period)]
                if any(e.is_lab_continuation for e in next_entries):
                    merged_cells[(day, col)] = 2
    
    # Insert breaks and mark truly empty slots as FREE
    for day in table:
        table[day][2] = "SHORT\nBREAK"
        table[day][5] = "LUNCH\nBREAK"
        # Mark empty slots as FREE (but keep breaks as-is)
        for col_idx in [0, 1, 3, 4, 6, 7, 8]:  # Non-break columns
            if table[day][col_idx] == "":
                table[day][col_idx] = "FREE"
    
    return table, merged_cells


def timetable_to_html(table: dict, section: str, merged_cells: dict = None) -> str:
    """
    Generate CMRIT-style HTML table (suitable for PDF/printing)
    """
    if merged_cells is None:
        merged_cells = {}
    
    html = """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>CMRIT Timetable - {section}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        h1 {{ text-align: center; color: #333; }}
        h2 {{ text-align: center; color: #666; margin-bottom: 20px; }}
        table {{ border-collapse: collapse; width: 100%; margin: 20px auto; }}
        th, td {{ 
            border: 2px solid #333; 
            padding: 8px 4px; 
            text-align: center; 
            vertical-align: middle;
            font-size: 11px;
            min-width: 80px;
        }}
        th {{ 
            background-color: #4472C4; 
            color: white; 
            font-weight: bold;
        }}
        .day-header {{ 
            background-color: #5B9BD5; 
            color: white;
            font-weight: bold;
            width: 80px;
        }}
        .break {{ 
            background-color: #FFC000; 
            color: #333;
            font-weight: bold;
        }}
        .lunch {{ 
            background-color: #92D050; 
            color: #333;
            font-weight: bold;
        }}
        .lab {{ 
            background-color: #E2EFDA; 
        }}
        .theory {{ 
            background-color: #DEEBF7; 
        }}
        .empty {{ 
            background-color: #F2F2F2; 
        }}
        .subject-name {{ font-weight: bold; }}
        .faculty-name {{ font-size: 10px; color: #666; }}
        .batch-info {{ font-size: 9px; color: #888; }}
        @media print {{
            body {{ margin: 0; }}
            table {{ page-break-inside: avoid; }}
        }}
    </style>
</head>
<body>
    <h1>CLASS TIMETABLE</h1>
    <h2>Section: {section}</h2>
    <table>
        <tr>
            <th>Day / Time</th>
""".format(section=section)
    
    # Header row with time slots
    for i, time_slot in enumerate(VTU_TIME_SLOTS):
        css_class = ""
        if i == 2:
            css_class = " class='break'"
        elif i == 5:
            css_class = " class='lunch'"
        html += f"            <th{css_class}>{time_slot}</th>\n"
    html += "        </tr>\n"
    
    # Data rows
    for day, slots in table.items():
        html += f"        <tr>\n"
        html += f"            <th class='day-header'>{day}</th>\n"
        
        skip_cols = set()
        for i, cell in enumerate(slots):
            if i in skip_cols:
                continue
            
            # Determine cell class
            css_class = ""
            colspan = ""
            
            if i == 2:
                css_class = "break"
            elif i == 5:
                css_class = "lunch"
            elif not cell:
                css_class = "empty"
            elif "LAB" in cell.upper() or (day, i) in merged_cells:
                css_class = "lab"
                # Handle merged cells for labs
                if (day, i) in merged_cells:
                    span = merged_cells[(day, i)]
                    colspan = f" colspan='{span}'"
                    for j in range(1, span):
                        skip_cols.add(i + j)
            else:
                css_class = "theory"
            
            # Format cell content with line breaks as HTML
            cell_html = cell.replace('\n', '<br>') if cell else '-'
            
            html += f"            <td class='{css_class}'{colspan}>{cell_html}</td>\n"
        
        html += "        </tr>\n"
    
    html += """    </table>
    <p style="text-align: center; font-size: 10px; color: #666;">
        Generated by CMRIT Timetable Generation System | DSA-Based Adaptive Scheduling
    </p>
</body>
</html>"""
    
    return html


def print_vtu_timetable(timetable: dict, section: str, days: list):
    """Print timetable in CMRIT-style tabular format (console)"""
    table, _ = convert_to_vtu_table(timetable, section, days)
    
    print(f"\n{'='*120}")
    print(f"CMRIT TIMETABLE - {section}")
    print(f"{'='*120}")
    
    # Header
    header = f"{'Day':<10}"
    for time_slot in VTU_TIME_SLOTS:
        header += f"| {time_slot:^12}"
    print(header)
    print("-" * 120)
    
    # Rows
    for day, slots in table.items():
        # First line of row
        row1 = f"{day:<10}"
        for cell in slots:
            lines = cell.split('\n') if cell else ['-']
            row1 += f"| {lines[0]:^12}"
        print(row1)
        
        # Second line if exists (faculty/batch info)
        has_second_line = any('\n' in cell for cell in slots if cell)
        if has_second_line:
            row2 = f"{'':<10}"
            for cell in slots:
                lines = cell.split('\n') if cell else ['']
                row2 += f"| {lines[1] if len(lines) > 1 else '':^12}"
            print(row2)
        
        print("-" * 120)
    
    print("=" * 120)


def save_vtu_html_timetable(timetable: dict, section: str, days: list, output_path: str):
    """Save timetable as CMRIT-style HTML file"""
    table, merged_cells = convert_to_vtu_table(timetable, section, days)
    html = timetable_to_html(table, section, merged_cells)
    
    with open(output_path, 'w') as f:
        f.write(html)
    
    return output_path


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
                    # Show only subject code, no faculty
                    cell = f"{entry.subject_short}"
                    if entry.batch:
                        # For labs with batches, show subject with batch info
                        all_batches = sorted(set(e.batch for e in entries if e.batch))
                        if len(all_batches) > 1:
                            cell = f"{entry.subject_short}({'/'.join(all_batches)})"
                        else:
                            cell = f"{entry.subject_short}({entry.batch})"
                else:
                    cell = "FREE"
            else:
                cell = "FREE"
            
            row += f"| {cell:^13}"
        print(row)
    
    print("=" * 100)


def generate_timetable_cli(semester: int, branch: str, sections: list, 
                          algorithm: str = 'constraint_satisfaction',
                          debug_mode: bool = False):
    """Generate timetable from command line"""
    print(f"\n{'='*60}")
    print("CMRIT TIMETABLE GENERATION SYSTEM")
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
    
    # Print timetables (both formats)
    for section in sections:
        print_timetable_text(timetable, section)
        print_vtu_timetable(timetable, section, DAYS)
    
    # Save to file
    output_dir = 'data/generated_timetables'
    os.makedirs(output_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Save CMRIT-style HTML timetables for each section
    html_dir = f"{output_dir}/html"
    os.makedirs(html_dir, exist_ok=True)
    
    print(f"\n{'='*60}")
    print("SAVING CMRIT-STYLE HTML TIMETABLES")
    print(f"{'='*60}")
    
    for section in sections:
        html_path = f"{html_dir}/{section}_timetable_{timestamp}.html"
        save_vtu_html_timetable(timetable, section, DAYS, html_path)
        print(f"  ✓ {section}: {html_path}")
    
    print(f"\nOpen HTML files in browser → Print → Save as PDF for college format")
    
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
                            'batch': entry.batch
                        })
                else:
                    # Mark empty slots as FREE
                    slot_data['classes'].append({
                        'subject_code': '',
                        'subject_short': 'FREE',
                        'subject_type': 'free',
                        'batch': None
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
    print("CMRIT TIMETABLE GENERATION SYSTEM - WEB SERVER")
    print("="*60)
    print("\nStarting web server...")
    print("Open http://localhost:5000 in your browser")
    print("\nPress Ctrl+C to stop the server\n")
    
    from app.web_app import app
    app.run(debug=True, host='0.0.0.0', port=5000)


def run_tests():
    """Run system tests"""
    print("\n" + "="*60)
    print("CMRIT TIMETABLE GENERATION SYSTEM - TESTS")
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
        description='CMRIT Timetable Generation System - DSA-Based Scheduling'
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
