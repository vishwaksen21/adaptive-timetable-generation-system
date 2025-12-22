"""
VTU Semester-wise Subject Configuration
Based on VTU 5th Semester AI&DS/CSDS Curriculum
"""

from config.vtu_config import Subject

# 5th Semester Subjects (AI&DS / CSDS)
SEMESTER_5_SUBJECTS = {
    # Theory Subjects
    "21CS51": Subject(
        code="21CS51",
        name="Computer Networks",
        short_name="CN",
        subject_type="theory",
        hours_per_week=4,
        credits=4,
        semester=5,
        priority=1
    ),
    "21CS52": Subject(
        code="21CS52",
        name="Theory of Computation",
        short_name="TOC",
        subject_type="theory",
        hours_per_week=4,
        credits=4,
        semester=5,
        priority=1
    ),
    "21CS53": Subject(
        code="21CS53",
        name="Software Engineering & Project Management",
        short_name="SEPM",
        subject_type="theory",
        hours_per_week=3,
        credits=3,
        semester=5,
        priority=1
    ),
    "21CS54": Subject(
        code="21CS54",
        name="Full Stack Development",
        short_name="FSD",
        subject_type="theory",
        hours_per_week=3,
        credits=3,
        semester=5,
        priority=1
    ),
    "21RMI56": Subject(
        code="21RMI56",
        name="Research Methodology & IPR",
        short_name="RM",
        subject_type="theory",
        hours_per_week=2,
        credits=2,
        semester=5,
        priority=2
    ),
    "21CIP57": Subject(
        code="21CIP57",
        name="Environmental Studies",
        short_name="ES",
        subject_type="audit",
        hours_per_week=1,
        credits=0,
        semester=5,
        priority=3
    ),
    
    # Professional Electives
    "21CS551": Subject(
        code="21CS551",
        name="Data Visualization",
        short_name="DV",
        subject_type="theory",
        hours_per_week=3,
        credits=3,
        semester=5,
        is_elective=True,
        priority=2
    ),
    "21CS552": Subject(
        code="21CS552",
        name="Cloud Computing",
        short_name="CC",
        subject_type="theory",
        hours_per_week=3,
        credits=3,
        semester=5,
        is_elective=True,
        priority=2
    ),
    "21CS553": Subject(
        code="21CS553",
        name="Artificial Intelligence",
        short_name="AI",
        subject_type="theory",
        hours_per_week=3,
        credits=3,
        semester=5,
        is_elective=True,
        priority=2
    ),
    
    # Laboratory Subjects
    "21CSL55": Subject(
        code="21CSL55",
        name="Computer Networks Laboratory",
        short_name="CNL",
        subject_type="lab",
        hours_per_week=3,
        credits=1,
        semester=5,
        lab_duration=3,
        requires_room_type="computer_lab",
        batches_required=True,
        priority=1
    ),
    "21CSL581": Subject(
        code="21CSL581",
        name="Data Visualization Laboratory",
        short_name="DVL",
        subject_type="lab",
        hours_per_week=2,
        credits=1,
        semester=5,
        lab_duration=2,
        requires_room_type="computer_lab",
        batches_required=True,
        priority=2
    ),
    "21CSL582": Subject(
        code="21CSL582",
        name="Full Stack Development Laboratory",
        short_name="FSDL",
        subject_type="lab",
        hours_per_week=2,
        credits=1,
        semester=5,
        lab_duration=2,
        requires_room_type="computer_lab",
        batches_required=True,
        priority=2
    ),
    
    # Mini Project
    "21CMP58": Subject(
        code="21CMP58",
        name="Mini Project",
        short_name="MP",
        subject_type="mini_project",
        hours_per_week=2,
        credits=2,
        semester=5,
        lab_duration=2,
        requires_room_type="computer_lab",
        priority=2
    ),
    
    # Special Activities
    "TYL": Subject(
        code="TYL",
        name="Technical/Aptitude/Logical/Soft Skills",
        short_name="TYL",
        subject_type="tyl",
        hours_per_week=2,
        credits=0,
        semester=5,
        priority=3
    ),
    "9LPA": Subject(
        code="9LPA",
        name="Placement Training (9 LPA)",
        short_name="9LPA",
        subject_type="9lpa",
        hours_per_week=2,
        credits=0,
        semester=5,
        priority=3
    ),
    "YOGA": Subject(
        code="YOGA",
        name="Yoga",
        short_name="YOGA",
        subject_type="yoga",
        hours_per_week=1,
        credits=0,
        semester=5,
        priority=4
    ),
    "CLUB": Subject(
        code="CLUB",
        name="Club Activity",
        short_name="CLUB",
        subject_type="club",
        hours_per_week=1,
        credits=0,
        semester=5,
        priority=4
    ),
}

# 6th Semester Subjects (AI&DS / CSDS)
SEMESTER_6_SUBJECTS = {
    "21CS61": Subject(
        code="21CS61",
        name="System Software & Compiler Design",
        short_name="SSCD",
        subject_type="theory",
        hours_per_week=4,
        credits=4,
        semester=6,
        priority=1
    ),
    "21CS62": Subject(
        code="21CS62",
        name="Computer Graphics & Visualization",
        short_name="CGV",
        subject_type="theory",
        hours_per_week=4,
        credits=4,
        semester=6,
        priority=1
    ),
    "21CS63": Subject(
        code="21CS63",
        name="Machine Learning",
        short_name="ML",
        subject_type="theory",
        hours_per_week=3,
        credits=3,
        semester=6,
        priority=1
    ),
    "21CS64": Subject(
        code="21CS64",
        name="Cryptography & Network Security",
        short_name="CNS",
        subject_type="theory",
        hours_per_week=3,
        credits=3,
        semester=6,
        priority=1
    ),
    "21CS651": Subject(
        code="21CS651",
        name="Big Data Analytics",
        short_name="BDA",
        subject_type="theory",
        hours_per_week=3,
        credits=3,
        semester=6,
        is_elective=True,
        priority=2
    ),
    "21CS652": Subject(
        code="21CS652",
        name="Internet of Things",
        short_name="IoT",
        subject_type="theory",
        hours_per_week=3,
        credits=3,
        semester=6,
        is_elective=True,
        priority=2
    ),
    "21CSL66": Subject(
        code="21CSL66",
        name="Machine Learning Laboratory",
        short_name="MLL",
        subject_type="lab",
        hours_per_week=3,
        credits=1,
        semester=6,
        lab_duration=3,
        requires_room_type="computer_lab",
        batches_required=True,
        priority=1
    ),
    "21CSL67": Subject(
        code="21CSL67",
        name="Computer Graphics Laboratory",
        short_name="CGL",
        subject_type="lab",
        hours_per_week=2,
        credits=1,
        semester=6,
        lab_duration=2,
        requires_room_type="computer_lab",
        batches_required=True,
        priority=2
    ),
    "21CS68": Subject(
        code="21CS68",
        name="Project Phase 1",
        short_name="PP1",
        subject_type="mini_project",
        hours_per_week=2,
        credits=2,
        semester=6,
        lab_duration=2,
        requires_room_type="computer_lab",
        priority=2
    ),
    "TYL6": Subject(
        code="TYL6",
        name="Technical/Aptitude/Logical/Soft Skills",
        short_name="TYL",
        subject_type="tyl",
        hours_per_week=2,
        credits=0,
        semester=6,
        priority=3
    ),
    "9LPA6": Subject(
        code="9LPA6",
        name="Placement Training (9 LPA)",
        short_name="9LPA",
        subject_type="9lpa",
        hours_per_week=2,
        credits=0,
        semester=6,
        priority=3
    ),
    "YOGA6": Subject(
        code="YOGA6",
        name="Yoga",
        short_name="YOGA",
        subject_type="yoga",
        hours_per_week=1,
        credits=0,
        semester=6,
        priority=4
    ),
    "CLUB6": Subject(
        code="CLUB6",
        name="Club Activity",
        short_name="CLUB",
        subject_type="club",
        hours_per_week=1,
        credits=0,
        semester=6,
        priority=4
    ),
}

# 4th Semester Subjects
SEMESTER_4_SUBJECTS = {
    "21CS41": Subject(
        code="21CS41",
        name="Analysis & Design of Algorithms",
        short_name="ADA",
        subject_type="theory",
        hours_per_week=4,
        credits=4,
        semester=4,
        priority=1
    ),
    "21CS42": Subject(
        code="21CS42",
        name="Microcontrollers & Embedded Systems",
        short_name="MES",
        subject_type="theory",
        hours_per_week=4,
        credits=4,
        semester=4,
        priority=1
    ),
    "21CS43": Subject(
        code="21CS43",
        name="Operating Systems",
        short_name="OS",
        subject_type="theory",
        hours_per_week=3,
        credits=3,
        semester=4,
        priority=1
    ),
    "21CS44": Subject(
        code="21CS44",
        name="Database Management System",
        short_name="DBMS",
        subject_type="theory",
        hours_per_week=3,
        credits=3,
        semester=4,
        priority=1
    ),
    "21CS45": Subject(
        code="21CS45",
        name="Object Oriented Concepts",
        short_name="OOC",
        subject_type="theory",
        hours_per_week=3,
        credits=3,
        semester=4,
        priority=1
    ),
    "21MAT41": Subject(
        code="21MAT41",
        name="Complex Analysis, Probability & Statistical Methods",
        short_name="MATHS",
        subject_type="theory",
        hours_per_week=3,
        credits=3,
        semester=4,
        priority=2
    ),
    "21CSL46": Subject(
        code="21CSL46",
        name="ADA Laboratory",
        short_name="ADAL",
        subject_type="lab",
        hours_per_week=3,
        credits=1,
        semester=4,
        lab_duration=3,
        requires_room_type="computer_lab",
        batches_required=True,
        priority=1
    ),
    "21CSL47": Subject(
        code="21CSL47",
        name="DBMS Laboratory",
        short_name="DBMSL",
        subject_type="lab",
        hours_per_week=2,
        credits=1,
        semester=4,
        lab_duration=2,
        requires_room_type="computer_lab",
        batches_required=True,
        priority=2
    ),
    "21CSL48": Subject(
        code="21CSL48",
        name="Microcontrollers Laboratory",
        short_name="MESL",
        subject_type="lab",
        hours_per_week=2,
        credits=1,
        semester=4,
        lab_duration=2,
        requires_room_type="electronics_lab",
        batches_required=True,
        priority=2
    ),
    "21KSK47": Subject(
        code="21KSK47",
        name="Samskrutika Kannada / Constitution of India",
        short_name="KAN/COI",
        subject_type="audit",
        hours_per_week=1,
        credits=0,
        semester=4,
        priority=3
    ),
    "TYL4": Subject(
        code="TYL4",
        name="Technical/Aptitude/Logical/Soft Skills",
        short_name="TYL",
        subject_type="tyl",
        hours_per_week=2,
        credits=0,
        semester=4,
        priority=3
    ),
    "YOGA4": Subject(
        code="YOGA4",
        name="Yoga",
        short_name="YOGA",
        subject_type="yoga",
        hours_per_week=1,
        credits=0,
        semester=4,
        priority=4
    ),
    "CLUB4": Subject(
        code="CLUB4",
        name="Club Activity",
        short_name="CLUB",
        subject_type="club",
        hours_per_week=1,
        credits=0,
        semester=4,
        priority=4
    ),
}

# 3rd Semester Subjects
SEMESTER_3_SUBJECTS = {
    "21CS31": Subject(
        code="21CS31",
        name="Data Structures & Applications",
        short_name="DSA",
        subject_type="theory",
        hours_per_week=4,
        credits=4,
        semester=3,
        priority=1
    ),
    "21CS32": Subject(
        code="21CS32",
        name="Digital Design & Computer Organization",
        short_name="DDCO",
        subject_type="theory",
        hours_per_week=4,
        credits=4,
        semester=3,
        priority=1
    ),
    "21CS33": Subject(
        code="21CS33",
        name="Computer Networks Fundamentals",
        short_name="CNF",
        subject_type="theory",
        hours_per_week=3,
        credits=3,
        semester=3,
        priority=1
    ),
    "21CS34": Subject(
        code="21CS34",
        name="Discrete Mathematical Structures",
        short_name="DMS",
        subject_type="theory",
        hours_per_week=3,
        credits=3,
        semester=3,
        priority=1
    ),
    "21MAT31": Subject(
        code="21MAT31",
        name="Transform Calculus, Fourier Series & Numerical Techniques",
        short_name="MATHS",
        subject_type="theory",
        hours_per_week=3,
        credits=3,
        semester=3,
        priority=2
    ),
    "21CS35": Subject(
        code="21CS35",
        name="Social Connect & Responsibility",
        short_name="SCR",
        subject_type="audit",
        hours_per_week=1,
        credits=0,
        semester=3,
        priority=3
    ),
    "21CSL36": Subject(
        code="21CSL36",
        name="Data Structures Laboratory",
        short_name="DSAL",
        subject_type="lab",
        hours_per_week=3,
        credits=1,
        semester=3,
        lab_duration=3,
        requires_room_type="computer_lab",
        batches_required=True,
        priority=1
    ),
    "21CSL37": Subject(
        code="21CSL37",
        name="Digital Design Laboratory",
        short_name="DDL",
        subject_type="lab",
        hours_per_week=2,
        credits=1,
        semester=3,
        lab_duration=2,
        requires_room_type="electronics_lab",
        batches_required=True,
        priority=2
    ),
    "21CSL38": Subject(
        code="21CSL38",
        name="Computer Networks Laboratory",
        short_name="CNL",
        subject_type="lab",
        hours_per_week=2,
        credits=1,
        semester=3,
        lab_duration=2,
        requires_room_type="computer_lab",
        batches_required=True,
        priority=2
    ),
    "TYL3": Subject(
        code="TYL3",
        name="Technical/Aptitude/Logical/Soft Skills",
        short_name="TYL",
        subject_type="tyl",
        hours_per_week=2,
        credits=0,
        semester=3,
        priority=3
    ),
    "YOGA3": Subject(
        code="YOGA3",
        name="Yoga",
        short_name="YOGA",
        subject_type="yoga",
        hours_per_week=1,
        credits=0,
        semester=3,
        priority=4
    ),
    "CLUB3": Subject(
        code="CLUB3",
        name="Club Activity",
        short_name="CLUB",
        subject_type="club",
        hours_per_week=1,
        credits=0,
        semester=3,
        priority=4
    ),
}

# Consolidate all semester subjects
ALL_SEMESTER_SUBJECTS = {
    3: SEMESTER_3_SUBJECTS,
    4: SEMESTER_4_SUBJECTS,
    5: SEMESTER_5_SUBJECTS,
    6: SEMESTER_6_SUBJECTS,
}

def get_subjects_for_semester(semester: int) -> dict:
    """Get all subjects for a given semester"""
    return ALL_SEMESTER_SUBJECTS.get(semester, {})

def get_lab_subjects(semester: int) -> list:
    """Get all lab subjects for a semester"""
    subjects = get_subjects_for_semester(semester)
    return [s for s in subjects.values() if s.subject_type == "lab"]

def get_theory_subjects(semester: int) -> list:
    """Get all theory subjects for a semester"""
    subjects = get_subjects_for_semester(semester)
    return [s for s in subjects.values() if s.subject_type == "theory"]

def get_special_activities(semester: int) -> list:
    """Get special activities (TYL, 9LPA, Yoga, Club) for a semester"""
    subjects = get_subjects_for_semester(semester)
    special_types = ["tyl", "9lpa", "yoga", "club", "mini_project"]
    return [s for s in subjects.values() if s.subject_type in special_types]
