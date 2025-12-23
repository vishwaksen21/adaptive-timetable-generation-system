"""
CMRIT Semester-wise Subject Configuration
Based on VTU 2022 Scheme - 5th Semester CSE/CSDS/AI&DS Curriculum
"""

from config.vtu_config import Subject

# ============================================================
# 5th Semester Subjects (VTU 2022 Scheme - BCS Codes)
# ============================================================
SEMESTER_5_SUBJECTS = {

    # ---------------- THEORY CORE ----------------
    "BCS501": Subject(
        code="BCS501",
        name="Software Engineering & Project Management",
        short_name="SEPM",
        subject_type="theory",
        hours_per_week=4,   # 4 credits ⇒ 4 classes
        credits=4,
        semester=5,
        priority=1
    ),

    "BCS502": Subject(
        code="BCS502",
        name="Computer Networks",
        short_name="CN",
        subject_type="theory",
        hours_per_week=4,   # 4 credits ⇒ 4 classes
        credits=4,
        semester=5,
        priority=1
    ),

    "BCS503": Subject(
        code="BCS503",
        name="Theory of Computation",
        short_name="TOC",
        subject_type="theory",
        hours_per_week=4,   # 4 credits ⇒ 4 classes
        credits=4,
        semester=5,
        priority=1
    ),

    # ---------------- CORE / OTHER THEORY ----------------
    "BRMK557": Subject(
        code="BRMK557",
        name="Research Methodology & IPR",
        short_name="RM",
        subject_type="theory",
        hours_per_week=3,   # 3 credits ⇒ 3 classes
        credits=3,
        semester=5,
        priority=2
    ),

    "BCS508": Subject(
        code="BCS508",
        name="Environmental Studies and E-Waste Management",
        short_name="ES",
        subject_type="audit",
        hours_per_week=1,   # 1 hour (non-credit)
        credits=0,
        semester=5,
        priority=3
    ),

    # ---------------- PROFESSIONAL ELECTIVES (Choose ONE) ----------------
    # VTU Rule: Only ONE elective is scheduled per section
    "BCS505A": Subject(
        code="BCS505A",
        name="Computer Vision",
        short_name="CV",
        subject_type="theory",
        hours_per_week=3,   # 3 credits ⇒ 3 classes
        credits=3,
        semester=5,
        is_elective=True,
        priority=2
    ),
    "BCS505B": Subject(
        code="BCS505B",
        name="Big Data Analytics",
        short_name="BDA",
        subject_type="theory",
        hours_per_week=3,
        credits=3,
        semester=5,
        is_elective=True,
        priority=2
    ),
    "BCS505C": Subject(
        code="BCS505C",
        name="Cloud Computing",
        short_name="CC",
        subject_type="theory",
        hours_per_week=3,
        credits=3,
        semester=5,
        is_elective=True,
        priority=2
    ),

    # ---------------- LABS (Continuous 2-hour blocks) ----------------
    "BCSL506": Subject(
        code="BCSL506",
        name="Computer Networks Laboratory",
        short_name="CNL",
        subject_type="lab",
        hours_per_week=2,   # 2 hours total
        credits=1,
        semester=5,
        lab_duration=2,     # Continuous 2-hour slot
        requires_room_type="computer_lab",
        batches_required=True,
        priority=1
    ),

    "BCSL507": Subject(
        code="BCSL507",
        name="Software Engineering Lab / Web Technology Lab",
        short_name="SEPL",
        subject_type="lab",
        hours_per_week=2,   # 2 hours total
        credits=1,
        semester=5,
        lab_duration=2,
        requires_room_type="computer_lab",
        batches_required=True,
        priority=2
    ),

    # ---------------- MINI PROJECT ----------------
    "BCMP508": Subject(
        code="BCMP508",
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

    # ---------------- SPECIAL ACTIVITIES ----------------
    "TYL5": Subject(
        code="TYL5",
        name="Technical/Aptitude/Logical/Soft Skills",
        short_name="TYL",
        subject_type="tyl",
        hours_per_week=2,
        credits=0,
        semester=5,
        priority=3
    ),

    "9LPA5": Subject(
        code="9LPA5",
        name="Placement Training (9-LPA)",
        short_name="9LPA",
        subject_type="9lpa",
        hours_per_week=2,
        credits=0,
        semester=5,
        priority=3
    ),

    "YOGA5": Subject(
        code="YOGA5",
        name="Yoga",
        short_name="YOGA",
        subject_type="yoga",
        hours_per_week=1,
        credits=0,
        semester=5,
        priority=4
    ),

    "CLUB5": Subject(
        code="CLUB5",
        name="Club Activity",
        short_name="CLUB",
        subject_type="club",
        hours_per_week=1,
        credits=0,
        semester=5,
        priority=4
    ),
}

# ============================================================
# 6th Semester Subjects (AI&DS / CSDS)
# ============================================================
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

# Default elective selection per semester
# Only ONE elective should be scheduled per section (VTU rule)
DEFAULT_ELECTIVE = {
    5: "BCS505A",  # Computer Vision (can change to BCS505B or BCS505C)
    6: "21CS651",  # Big Data Analytics
}

def get_subjects_for_semester(semester: int, selected_elective: str = None) -> dict:
    """
    Get all subjects for a given semester.
    
    VTU Rule: Only ONE professional elective is scheduled per section.
    By default, uses the configured elective. Can be overridden.
    
    Args:
        semester: Semester number (3, 4, 5, 6)
        selected_elective: Optional specific elective code to include
        
    Returns:
        Dictionary of subject_code -> Subject
    """
    all_subjects = ALL_SEMESTER_SUBJECTS.get(semester, {})
    
    # Filter: include only the selected elective, exclude other electives
    result = {}
    elective_code = selected_elective or DEFAULT_ELECTIVE.get(semester)
    
    for code, subject in all_subjects.items():
        if hasattr(subject, 'is_elective') and subject.is_elective:
            # Only include the selected elective
            if code == elective_code:
                result[code] = subject
        else:
            result[code] = subject
    
    # VTU 2022: Verify only ONE elective is included
    electives = [s for s in result.values() if getattr(s, 'is_elective', False)]
    assert len(electives) <= 1, f"VTU rule violated: {len(electives)} electives found (max 1 allowed)"
    
    return result

def get_all_subjects_for_semester(semester: int) -> dict:
    """Get ALL subjects including all electives (for display purposes)"""
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

def get_available_electives(semester: int) -> list:
    """Get list of available elective subjects for a semester"""
    all_subjects = ALL_SEMESTER_SUBJECTS.get(semester, {})
    return [s for s in all_subjects.values() 
            if hasattr(s, 'is_elective') and s.is_elective]
