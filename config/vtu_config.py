"""
CMRIT Engineering College Timetable Configuration
Based on Indian Standard Time (IST) and CMRIT academic structure
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple
from enum import Enum

# Time Configuration - VTU Standard Timings
class TimeSlot:
    """Represents a time slot in the timetable"""
    def __init__(self, period: int, start: str, end: str, is_break: bool = False, break_type: str = None):
        self.period = period
        self.start = start
        self.end = end
        self.is_break = is_break
        self.break_type = break_type
    
    def __repr__(self):
        return f"{self.start}-{self.end}"

# VTU Standard Time Slots (IST)
TIME_SLOTS = {
    1: TimeSlot(1, "08:00", "09:00"),
    2: TimeSlot(2, "09:00", "10:00"),
    # Short Break: 10:00-10:20
    3: TimeSlot(3, "10:20", "11:20"),
    4: TimeSlot(4, "11:20", "12:20"),
    # Lunch Break: 12:20-13:00
    5: TimeSlot(5, "13:00", "14:00"),
    6: TimeSlot(6, "14:00", "15:00"),
    7: TimeSlot(7, "15:00", "16:00"),
}

BREAK_SLOTS = {
    "short_break": TimeSlot(0, "10:00", "10:20", is_break=True, break_type="short"),
    "lunch_break": TimeSlot(0, "12:20", "13:00", is_break=True, break_type="lunch"),
}

# Working Days (Monday to Saturday as per VTU)
DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
DAYS_SHORT = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]

# Number of periods per day
PERIODS_PER_DAY = 7

# Branch and Section Configuration
class Branch(Enum):
    AIDS = "AI&DS"
    CSDS = "CSDS"

@dataclass
class Section:
    """Represents a section/class"""
    name: str
    branch: Branch
    semester: int
    batches: List[str] = field(default_factory=list)  # For lab batches like A1, A2, A3

# VTU Branch-Section Configuration
BRANCH_SECTIONS = {
    Branch.AIDS: {
        "sections": ["AIDS-A", "AIDS-B"],
        "batches_per_section": {
            "AIDS-A": ["A1", "A2", "A3"],
            "AIDS-B": ["B1", "B2", "B3"],
        }
    },
    Branch.CSDS: {
        "sections": ["CSDS-C"],
        "batches_per_section": {
            "CSDS-C": ["C1", "C2", "C3"],
        }
    }
}

# Semester Configuration
SEMESTERS = [3, 4, 5, 6]

@dataclass
class SubjectType(Enum):
    THEORY = "theory"
    LAB = "lab"
    TYL = "tyl"  # Technical/Aptitude/Logical/Soft Skills
    NINE_LPA = "9lpa"  # Placement Training
    YOGA = "yoga"
    CLUB = "club"
    MINI_PROJECT = "mini_project"
    ELECTIVE = "elective"
    AUDIT = "audit"

@dataclass
class Subject:
    """Represents a subject in the curriculum"""
    code: str
    name: str
    short_name: str
    subject_type: str  # theory, lab, tyl, 9lpa, yoga, club, mini_project
    hours_per_week: int
    credits: int
    semester: int
    is_elective: bool = False
    lab_duration: int = 0  # Consecutive periods for labs
    requires_room_type: str = "classroom"  # classroom, lab, computer_lab
    batches_required: bool = False  # If lab needs batch-wise splitting
    priority: int = 1  # Lower is higher priority

@dataclass  
class Faculty:
    """Represents a faculty member"""
    id: str
    name: str
    short_name: str
    subjects: List[str]  # List of subject codes they can teach
    max_hours_per_day: int = 6
    max_hours_per_week: int = 25
    unavailable_slots: List[Tuple[str, int]] = field(default_factory=list)  # [(day, period), ...]

@dataclass
class Room:
    """Represents a room/lab"""
    number: str
    name: str
    room_type: str  # classroom, computer_lab, electronics_lab, etc.
    capacity: int
    building: str = "Main"

# Algorithm Configuration
@dataclass
class AlgorithmConfig:
    """Configuration for the scheduling algorithm"""
    algorithm_type: str = "constraint_satisfaction"  # constraint_satisfaction, genetic, graph_coloring
    population_size: int = 100
    generations: int = 500
    mutation_rate: float = 0.1
    crossover_rate: float = 0.8
    timeout_seconds: int = 300
    debug_mode: bool = False
    max_consecutive_theory: int = 3
    prefer_morning_labs: bool = True
    limit_first_period: int = 3  # Max times 8:00 AM slot can be used per week per section

# Hard Constraints
HARD_CONSTRAINTS = [
    "no_teacher_clash",        # No teacher can be in two places at once
    "no_room_clash",           # No room can be double-booked
    "no_section_clash",        # No section can have two classes at once
    "required_hours",          # Each subject must get required hours
    "lab_continuity",          # Labs must be in continuous blocks
    "batch_split_labs",        # Lab batches in parallel
    "fixed_slots_respected",   # Special activities in configured slots
]

# Soft Constraints (with weights for optimization)
SOFT_CONSTRAINTS = {
    "max_consecutive_theory": 10,    # Weight penalty for exceeding max consecutive theory
    "spread_heavy_subjects": 8,       # Weight for spreading CN, TOC, etc.
    "prefer_lab_blocks": 5,           # Weight for labs in morning/afternoon blocks
    "limit_early_slots": 3,           # Weight for limiting 8 AM slots
    "teacher_preferences": 2,         # Weight for teacher time preferences
}

# Room Type Mapping
ROOM_TYPES = {
    "classroom": "Regular Classroom",
    "computer_lab": "Computer Laboratory",
    "electronics_lab": "Electronics Laboratory",
    "seminar_hall": "Seminar Hall",
    "activity_room": "Activity/Multipurpose Room",
}

# Export format configuration
EXPORT_FORMATS = ["json", "csv", "excel", "pdf"]

def get_period_time(period: int) -> str:
    """Get time string for a period"""
    if period in TIME_SLOTS:
        slot = TIME_SLOTS[period]
        return f"{slot.start}-{slot.end}"
    return ""

def get_all_time_headers() -> List[str]:
    """Get all time headers including breaks for display"""
    headers = []
    headers.append("08:00-09:00")
    headers.append("09:00-10:00")
    headers.append("SHORT BREAK (10:00-10:20)")
    headers.append("10:20-11:20")
    headers.append("11:20-12:20")
    headers.append("LUNCH (12:20-13:00)")
    headers.append("13:00-14:00")
    headers.append("14:00-15:00")
    headers.append("15:00-16:00")
    return headers
