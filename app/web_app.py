"""
CMRIT Timetable Generation System - Flask Web Application
"""

import os
import json
import time
import logging
from datetime import datetime
from collections import deque
from flask import Flask, render_template, request, jsonify, send_file, Response
from flask_cors import CORS
import csv
import io

# Set up logging
logger = logging.getLogger(__name__)

# Add parent directory to path for imports
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.vtu_config import (
    TIME_SLOTS, DAYS, DAYS_SHORT, PERIODS_PER_DAY,
    Branch, BRANCH_SECTIONS, SEMESTERS, get_period_time
)
from config.semester_subjects import (
    get_subjects_for_semester, get_lab_subjects,
    get_theory_subjects, get_special_activities,
    ALL_SEMESTER_SUBJECTS
)
from config.faculty_rooms import FACULTY_LIST, ROOM_LIST, get_faculty_for_subject

from algorithms.dsa_scheduler import (
    create_scheduler, ConstraintSatisfactionScheduler,
    TimeSlotEntry
)
from algorithms.constraint_validator import ConstraintValidator

app = Flask(__name__, 
            template_folder='templates',
            static_folder='static')
CORS(app)

# Store generated timetables in memory (in production, use database)
generated_timetables = {}

# ============================================================
# SUBJECT GROUPING FOR VTU-STYLE DISPLAY
# ============================================================
# Groups subjects that should appear together in one cell
SUBJECT_GROUPS = {
    "CC / CV / NoSQL": {"CC", "CV", "NOSQL"},
    "TYL": {"TYL", "TYL-L", "TYL-T", "TYL-A"},
    "9LPA": {"9LPA"},
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


def rotated_periods_for_day(day: str) -> list:
    """
    Get rotated period order for a specific day.
    This ensures different subjects appear in first period on different days,
    preventing visual bias (e.g., CN always appearing first).
    
    NOTE: This only affects DISPLAY order, not actual scheduling.
    """
    base = deque(range(1, PERIODS_PER_DAY + 1))
    shift = DAYS.index(day) % PERIODS_PER_DAY
    base.rotate(-shift)
    return list(base)


def group_entries(entries: list) -> list:
    """
    Group multiple entries into display-friendly format.
    
    - Merges CC/CV/NoSQL into single cell
    - Merges lab batches (C1/C2/C3) into single cell
    - Returns formatted entry list for template
    """
    if not entries:
        return []
    
    subjects = {e.subject_short.upper() for e in entries}
    
    # Check if this is a lab with multiple batches
    if any(e.subject_type == "lab" for e in entries):
        batches = sorted({e.batch for e in entries if e.batch})
        faculties = sorted({e.faculty_name for e in entries})
        rooms = sorted({e.room_number for e in entries})
        
        return [{
            'subject': entries[0].subject_short,
            'faculty': ' / '.join(faculties) if len(faculties) <= 2 else faculties[0] + ' +',
            'room': ' / '.join(rooms) if len(rooms) <= 2 else rooms[0] + ' +',
            'batch': ' / '.join(batches) if batches else None,
            'type': 'lab'
        }]
    
    # Check if entries match a subject group (CC/CV/NoSQL etc.)
    for label, members in SUBJECT_GROUPS.items():
        if subjects.issubset(members) or subjects == members:
            faculties = sorted({e.faculty_name for e in entries})
            rooms = sorted({e.room_number for e in entries})
            return [{
                'subject': label,
                'faculty': ', '.join(faculties),
                'room': ', '.join(rooms),
                'batch': None,
                'type': entries[0].subject_type
            }]
    
    # Default: return individual entries
    return [{
        'subject': e.subject_short,
        'faculty': e.faculty_name,
        'room': e.room_number,
        'batch': e.batch,
        'type': e.subject_type
    } for e in entries]


def convert_timetable_to_matrix(timetable: dict, section: str) -> list:
    """Convert timetable dictionary to matrix format for display"""
    matrix = []
    
    for day in DAYS:
        row = {'day': day, 'periods': []}
        
        for period in range(1, PERIODS_PER_DAY + 1):
            slot_key = (day, period)
            
            if section in timetable and slot_key in timetable[section]:
                entries = timetable[section][slot_key]
                
                # Use grouped entries for VTU-style display
                cell_content = group_entries(entries)
                
                row['periods'].append({
                    'period': period,
                    'time': get_time_display(period),
                    'entries': cell_content,
                    'is_empty': False
                })
            else:
                row['periods'].append({
                    'period': period,
                    'time': get_time_display(period),
                    'entries': [],
                    'is_empty': True
                })
        
        matrix.append(row)
    
    return matrix

def convert_timetable_to_json(timetable: dict, section: str) -> dict:
    """Convert timetable to JSON format for API response"""
    result = {
        'section': section,
        'days': [],
        'metadata': {
            'generated_at': datetime.now().isoformat(),
            'periods_per_day': PERIODS_PER_DAY,
            'time_slots': {str(k): get_time_display(k) for k in range(1, PERIODS_PER_DAY + 1)}
        }
    }
    
    for day in DAYS:
        day_data = {
            'name': day,
            'short': DAYS_SHORT[DAYS.index(day)],
            'slots': []
        }
        
        for period in range(1, PERIODS_PER_DAY + 1):
            slot_key = (day, period)
            
            slot_data = {
                'period': period,
                'time': get_time_display(period),
                'classes': []
            }
            
            if section in timetable and slot_key in timetable[section]:
                entries = timetable[section][slot_key]
                # Use grouped display for VTU-style format
                grouped = group_entries(entries)
                for g in grouped:
                    slot_data['classes'].append({
                        'subject_code': entries[0].subject_code if entries else '',
                        'subject_name': entries[0].subject_name if entries else '',
                        'subject_short': g['subject'],
                        'subject_type': g['type'],
                        'faculty_id': entries[0].faculty_id if entries else '',
                        'faculty_name': g['faculty'],
                        'room': g['room'],
                        'batch': g['batch'],
                        'is_continuation': any(e.is_lab_continuation for e in entries)
                    })
            
            day_data['slots'].append(slot_data)
        
        result['days'].append(day_data)
    
    return result

def get_faculty_timetable(timetable: dict, faculty_id: str) -> dict:
    """Get timetable for a specific faculty member"""
    faculty_schedule = {
        'faculty_id': faculty_id,
        'faculty_name': FACULTY_LIST[faculty_id].name if faculty_id in FACULTY_LIST else faculty_id,
        'days': []
    }
    
    for day in DAYS:
        day_data = {'name': day, 'slots': []}
        
        for period in range(1, PERIODS_PER_DAY + 1):
            slot_data = {
                'period': period,
                'time': get_time_display(period),
                'classes': []
            }
            
            # Find all classes for this faculty at this time
            for section, slots in timetable.items():
                slot_key = (day, period)
                if slot_key in slots:
                    for entry in slots[slot_key]:
                        if entry.faculty_id == faculty_id:
                            slot_data['classes'].append({
                                'section': section,
                                'subject': entry.subject_short,
                                'room': entry.room_number,
                                'batch': entry.batch
                            })
            
            day_data['slots'].append(slot_data)
        
        faculty_schedule['days'].append(day_data)
    
    return faculty_schedule


# ============ Routes ============

@app.route('/')
def index():
    """Main page with semester/section selection"""
    return render_template('index.html',
                          semesters=SEMESTERS,
                          branches=[b.value for b in Branch],
                          branch_sections=BRANCH_SECTIONS)

@app.route('/api/branches')
def get_branches():
    """Get available branches"""
    return jsonify({
        'branches': [
            {'id': 'AIDS', 'name': 'AI & Data Science', 'sections': ['AIDS-A', 'AIDS-B']},
            {'id': 'CSDS', 'name': 'Computer Science & Data Science', 'sections': ['CSDS-C']}
        ]
    })

@app.route('/api/semesters')
def get_semesters():
    """Get available semesters"""
    return jsonify({
        'semesters': [
            {'id': 3, 'name': '3rd Semester'},
            {'id': 4, 'name': '4th Semester'},
            {'id': 5, 'name': '5th Semester'},
            {'id': 6, 'name': '6th Semester'}
        ]
    })

@app.route('/api/subjects/<int:semester>')
def get_subjects(semester):
    """Get subjects for a semester"""
    subjects = get_subjects_for_semester(semester)
    
    result = []
    for code, subject in subjects.items():
        result.append({
            'code': code,
            'name': subject.name,
            'short_name': subject.short_name,
            'type': subject.subject_type,
            'hours_per_week': subject.hours_per_week,
            'credits': subject.credits,
            'is_lab': subject.subject_type == 'lab',
            'lab_duration': subject.lab_duration
        })
    
    return jsonify({'semester': semester, 'subjects': result})

@app.route('/api/faculty')
def get_faculty():
    """Get all faculty members"""
    result = []
    for fid, faculty in FACULTY_LIST.items():
        result.append({
            'id': fid,
            'name': faculty.name,
            'short_name': faculty.short_name,
            'subjects': faculty.subjects,
            'max_hours_per_day': faculty.max_hours_per_day,
            'max_hours_per_week': faculty.max_hours_per_week
        })
    
    return jsonify({'faculty': result})

@app.route('/api/rooms')
def get_rooms():
    """Get all rooms"""
    result = []
    for rid, room in ROOM_LIST.items():
        result.append({
            'number': room.number,
            'name': room.name,
            'type': room.room_type,
            'capacity': room.capacity,
            'building': room.building
        })
    
    return jsonify({'rooms': result})

@app.route('/api/generate', methods=['POST'])
def generate_timetable():
    """Generate timetable for selected configuration"""
    try:
        data = request.json
        
        semester = data.get('semester', 5)
        branch = data.get('branch', 'AIDS')
        sections = data.get('sections', ['AIDS-A', 'AIDS-B'])
        algorithm = data.get('algorithm', 'constraint_satisfaction')
        debug_mode = data.get('debug_mode', False)
        
        # Get subjects for semester
        subjects = get_subjects_for_semester(semester)
        subject_list = list(subjects.values())
        
        # Get faculty and rooms
        faculty_list = list(FACULTY_LIST.values())
        room_list = list(ROOM_LIST.values())
        
        # Get section batches
        section_batches = {}
        for section in sections:
            if branch == 'AIDS':
                section_batches[section] = BRANCH_SECTIONS[Branch.AIDS]['batches_per_section'].get(section, [])
            else:
                section_batches[section] = BRANCH_SECTIONS[Branch.CSDS]['batches_per_section'].get(section, [])
        
        # Create scheduler configuration
        config = {
            'algorithm_type': algorithm,
            'debug_mode': debug_mode,
            'timeout_seconds': 30,
            'days': DAYS,
            'periods_per_day': PERIODS_PER_DAY,
            'max_consecutive_theory': 3,
            'prefer_morning_labs': True,
            'limit_first_period': 3,
            'population_size': 50,
            'generations': 100,
            'mutation_rate': 0.15,
            'crossover_rate': 0.8
        }
        
        # Create and run scheduler
        start_time = time.time()
        scheduler = create_scheduler(config)
        
        if algorithm == 'genetic' or algorithm == 'hybrid':
            success, timetable, violations = scheduler.schedule(
                sections, subject_list, faculty_list, room_list, section_batches
            )
        else:
            # constraint_satisfaction - use fast greedy scheduler
            success, timetable = scheduler.schedule_greedy(
                sections, subject_list, faculty_list, room_list, section_batches
            )
            violations = []
        
        generation_time = time.time() - start_time
        
        # Store generated timetable
        timetable_id = f"{semester}_{branch}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        generated_timetables[timetable_id] = {
            'timetable': timetable,
            'semester': semester,
            'branch': branch,
            'sections': sections,
            'generated_at': datetime.now().isoformat()
        }
        
        # Validate
        validator = ConstraintValidator(config)
        validation = validator.validate(timetable, subjects, sections)
        
        # Prepare response
        response = {
            'success': success,
            'timetable_id': timetable_id,
            'generation_time': round(generation_time, 2),
            'algorithm': algorithm,
            'statistics': {
                'backtrack_count': scheduler.backtrack_count if hasattr(scheduler, 'backtrack_count') else 0,
                'total_attempts': scheduler.total_attempts if hasattr(scheduler, 'total_attempts') else 0
            },
            'validation': {
                'is_valid': validation.is_valid,
                'score': validation.score,
                'hard_violations': len(validation.hard_violations),
                'soft_violations': len(validation.soft_violations)
            },
            'sections_data': {}
        }
        
        # Add timetable data for each section
        for section in sections:
            response['sections_data'][section] = convert_timetable_to_json(timetable, section)
        
        return jsonify(response)
    
    except Exception as e:
        import traceback
        error_traceback = traceback.format_exc()
        logger.error(f"Error generating timetable: {str(e)}\n{error_traceback}")
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': error_traceback
        }), 500

@app.route('/api/timetable/<timetable_id>')
def get_timetable(timetable_id):
    """Get a generated timetable by ID"""
    if timetable_id not in generated_timetables:
        return jsonify({'error': 'Timetable not found'}), 404
    
    data = generated_timetables[timetable_id]
    timetable = data['timetable']
    sections = data['sections']
    
    result = {
        'timetable_id': timetable_id,
        'semester': data['semester'],
        'branch': data['branch'],
        'generated_at': data['generated_at'],
        'sections': {}
    }
    
    for section in sections:
        result['sections'][section] = convert_timetable_to_json(timetable, section)
    
    return jsonify(result)

@app.route('/api/timetable/<timetable_id>/section/<section>')
def get_section_timetable(timetable_id, section):
    """Get timetable for a specific section"""
    if timetable_id not in generated_timetables:
        return jsonify({'error': 'Timetable not found'}), 404
    
    data = generated_timetables[timetable_id]
    timetable = data['timetable']
    
    return jsonify(convert_timetable_to_json(timetable, section))

@app.route('/api/timetable/<timetable_id>/faculty/<faculty_id>')
def get_faculty_schedule(timetable_id, faculty_id):
    """Get faculty-wise timetable"""
    if timetable_id not in generated_timetables:
        return jsonify({'error': 'Timetable not found'}), 404
    
    data = generated_timetables[timetable_id]
    timetable = data['timetable']
    
    return jsonify(get_faculty_timetable(timetable, faculty_id))

@app.route('/api/export/<timetable_id>/<format_type>')
def export_timetable(timetable_id, format_type):
    """Export timetable in different formats"""
    if timetable_id not in generated_timetables:
        return jsonify({'error': 'Timetable not found'}), 404
    
    data = generated_timetables[timetable_id]
    timetable = data['timetable']
    sections = data['sections']
    
    if format_type == 'json':
        result = {
            'timetable_id': timetable_id,
            'sections': {}
        }
        for section in sections:
            result['sections'][section] = convert_timetable_to_json(timetable, section)
        
        return Response(
            json.dumps(result, indent=2),
            mimetype='application/json',
            headers={'Content-Disposition': f'attachment;filename=timetable_{timetable_id}.json'}
        )
    
    elif format_type == 'csv':
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Header
        writer.writerow(['Section', 'Day', 'Period', 'Time', 'Subject', 'Faculty', 'Room', 'Batch', 'Type'])
        
        for section in sections:
            for day in DAYS:
                for period in range(1, PERIODS_PER_DAY + 1):
                    slot_key = (day, period)
                    if section in timetable and slot_key in timetable[section]:
                        for entry in timetable[section][slot_key]:
                            writer.writerow([
                                section,
                                day,
                                period,
                                get_time_display(period),
                                entry.subject_short,
                                entry.faculty_name,
                                entry.room_number,
                                entry.batch or '',
                                entry.subject_type
                            ])
                    else:
                        writer.writerow([section, day, period, get_time_display(period), '', '', '', '', ''])
        
        output.seek(0)
        return Response(
            output.getvalue(),
            mimetype='text/csv',
            headers={'Content-Disposition': f'attachment;filename=timetable_{timetable_id}.csv'}
        )
    
    return jsonify({'error': 'Invalid format'}), 400

@app.route('/view/<timetable_id>')
def view_timetable(timetable_id):
    """View timetable in browser"""
    if timetable_id not in generated_timetables:
        return "Timetable not found", 404
    
    data = generated_timetables[timetable_id]
    timetable = data['timetable']
    sections = data['sections']
    
    section_matrices = {}
    for section in sections:
        section_matrices[section] = convert_timetable_to_matrix(timetable, section)
    
    return render_template('view_timetable.html',
                          timetable_id=timetable_id,
                          data=data,
                          section_matrices=section_matrices,
                          days=DAYS,
                          periods=range(1, PERIODS_PER_DAY + 1),
                          get_time_display=get_time_display)

@app.route('/print/<timetable_id>/<section>')
def print_timetable(timetable_id, section):
    """Print-friendly view for a section"""
    if timetable_id not in generated_timetables:
        return "Timetable not found", 404
    
    data = generated_timetables[timetable_id]
    timetable = data['timetable']
    
    matrix = convert_timetable_to_matrix(timetable, section)
    
    return render_template('print_timetable.html',
                          timetable_id=timetable_id,
                          section=section,
                          semester=data['semester'],
                          matrix=matrix,
                          days=DAYS,
                          periods=range(1, PERIODS_PER_DAY + 1),
                          get_time_display=get_time_display)


if __name__ == '__main__':
    # Create templates and static directories
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static/css', exist_ok=True)
    os.makedirs('static/js', exist_ok=True)
    
    app.run(debug=True, host='0.0.0.0', port=5000)
