"""
Faculty and Room Configuration for CMRIT Timetable System
"""

from config.vtu_config import Faculty, Room

# Faculty Configuration for AI&DS / CSDS (VTU 2022 Scheme - BCS Codes)
FACULTY_LIST = {
    # Computer Science Faculty - Semester 5
    "F001": Faculty(
        id="F001",
        name="Dr. Ramesh Kumar",
        short_name="RK",
        subjects=["BCS501", "BCS502", "BCSL506"],
        max_hours_per_day=6,
        max_hours_per_week=24
    ),
    "F002": Faculty(
        id="F002",
        name="Prof. Suresh Babu",
        short_name="SB",
        subjects=["BCS502", "BCS503", "BCSL507"],
        max_hours_per_day=6,
        max_hours_per_week=24
    ),
    "F003": Faculty(
        id="F003",
        name="Dr. Mahesh Reddy",
        short_name="MR",
        subjects=["BCS501", "BCS505A", "BCSL506"],
        max_hours_per_day=6,
        max_hours_per_week=24
    ),
    "F004": Faculty(
        id="F004",
        name="Prof. Rajesh Gowda",
        short_name="RG",
        subjects=["BCS503", "BRMK557", "BCS505B"],
        max_hours_per_day=6,
        max_hours_per_week=24
    ),
    "F005": Faculty(
        id="F005",
        name="Dr. Dinesh Rao",
        short_name="DR",
        subjects=["BCS505C", "BCSL507", "BCMP508"],
        max_hours_per_day=6,
        max_hours_per_week=24
    ),

    # Additional Mini Project mentor to support parallel fixed slots across sections
    "F021": Faculty(
        id="F021",
        name="Mini Project Mentor 2",
        short_name="MP2",
        subjects=["BCMP508"],
        max_hours_per_day=6,
        max_hours_per_week=24
    ),
    "F006": Faculty(
        id="F006",
        name="Prof. Lakshmi Devi",
        short_name="LD",
        subjects=["BCS505A", "BCS505B", "BCSL506"],
        max_hours_per_day=6,
        max_hours_per_week=24
    ),
    "F007": Faculty(
        id="F007",
        name="Dr. Priya Sharma",
        short_name="PS",
        subjects=["BRMK557", "BCS508", "BCS501"],
        max_hours_per_day=6,
        max_hours_per_week=24
    ),
    "F008": Faculty(
        id="F008",
        name="Prof. Anand Kumar",
        short_name="AK",
        subjects=["21CS61", "21CS62", "21CSL66"],
        max_hours_per_day=6,
        max_hours_per_week=24
    ),
    "F009": Faculty(
        id="F009",
        name="Dr. Kavitha Nair",
        short_name="KN",
        subjects=["21CS63", "21CS64", "21CSL66"],
        max_hours_per_day=6,
        max_hours_per_week=24
    ),
    "F010": Faculty(
        id="F010",
        name="Prof. Venkatesh Murthy",
        short_name="VM",
        subjects=["21CS651", "21CS652", "21CSL67"],
        max_hours_per_day=6,
        max_hours_per_week=24
    ),
    
    # 4th Semester Faculty
    "F011": Faculty(
        id="F011",
        name="Dr. Srinivas Iyengar",
        short_name="SI",
        subjects=["21CS41", "21CS42", "21CSL46"],
        max_hours_per_day=6,
        max_hours_per_week=24
    ),
    "F012": Faculty(
        id="F012",
        name="Prof. Meena Kumari",
        short_name="MK",
        subjects=["21CS43", "21CS44", "21CSL47"],
        max_hours_per_day=6,
        max_hours_per_week=24
    ),
    "F013": Faculty(
        id="F013",
        name="Dr. Rajan Pillai",
        short_name="RP",
        subjects=["21CS45", "21MAT41", "21CSL48"],
        max_hours_per_day=6,
        max_hours_per_week=24
    ),
    
    # 3rd Semester Faculty
    "F014": Faculty(
        id="F014",
        name="Prof. Harish Chandra",
        short_name="HC",
        subjects=["21CS31", "21CS32", "21CSL36"],
        max_hours_per_day=6,
        max_hours_per_week=24
    ),
    "F015": Faculty(
        id="F015",
        name="Dr. Savitha Rao",
        short_name="SR",
        subjects=["21CS33", "21CS34", "21CSL37"],
        max_hours_per_day=6,
        max_hours_per_week=24
    ),
    "F016": Faculty(
        id="F016",
        name="Prof. Ganesh Hegde",
        short_name="GH",
        subjects=["21MAT31", "21CS35", "21CSL38"],
        max_hours_per_day=6,
        max_hours_per_week=24
    ),
    
    # Special Activity Coordinators (updated for VTU 2022 codes)
    "F017": Faculty(
        id="F017",
        name="TYL Coordinator",
        short_name="TYL-C",
        subjects=["TYL5", "TYL3", "TYL4", "TYL6"],
        max_hours_per_day=8,
        max_hours_per_week=30
    ),
    "F018": Faculty(
        id="F018",
        name="9LPA Training Coordinator",
        short_name="9LPA-C",
        subjects=["9LPA5", "9LPA6"],
        max_hours_per_day=8,
        max_hours_per_week=30
    ),
    "F019": Faculty(
        id="F019",
        name="Yoga Instructor",
        short_name="YOGA-I",
        subjects=["YOGA5", "YOGA3", "YOGA4", "YOGA6"],
        max_hours_per_day=6,
        max_hours_per_week=20
    ),
    # Additional Yoga instructor for multi-section fixed slot (Wed P6)
    "F022": Faculty(
        id="F022",
        name="Yoga Instructor 2",
        short_name="YOGA-2",
        subjects=["YOGA5", "YOGA3", "YOGA4", "YOGA6"],
        max_hours_per_day=6,
        max_hours_per_week=20
    ),
    "F020": Faculty(
        id="F020",
        name="Club Activity Coordinator",
        short_name="CLUB-C",
        subjects=["CLUB5", "CLUB3", "CLUB4", "CLUB6"],
        max_hours_per_day=6,
        max_hours_per_week=20
    ),
    # Additional Club coordinator for multi-section fixed slot (Wed P7)
    "F023": Faculty(
        id="F023",
        name="Club Activity Coordinator 2",
        short_name="CLUB-2",
        subjects=["CLUB5", "CLUB3", "CLUB4", "CLUB6"],
        max_hours_per_day=6,
        max_hours_per_week=20
    ),
}

# Room Configuration
ROOM_LIST = {
    # Regular Classrooms
    "501": Room(number="501", name="Classroom 501", room_type="classroom", capacity=60, building="CSE Block"),
    "502": Room(number="502", name="Classroom 502", room_type="classroom", capacity=60, building="CSE Block"),
    "503": Room(number="503", name="Classroom 503", room_type="classroom", capacity=60, building="CSE Block"),
    "504": Room(number="504", name="Classroom 504", room_type="classroom", capacity=60, building="CSE Block"),
    "505": Room(number="505", name="Classroom 505", room_type="classroom", capacity=60, building="CSE Block"),
    "506": Room(number="506", name="Classroom 506", room_type="classroom", capacity=60, building="CSE Block"),
    
    # Computer Labs
    "CL1": Room(number="CL1", name="Computer Lab 1", room_type="computer_lab", capacity=30, building="CSE Block"),
    "CL2": Room(number="CL2", name="Computer Lab 2", room_type="computer_lab", capacity=30, building="CSE Block"),
    "CL3": Room(number="CL3", name="Computer Lab 3", room_type="computer_lab", capacity=30, building="CSE Block"),
    "CL4": Room(number="CL4", name="Computer Lab 4", room_type="computer_lab", capacity=30, building="CSE Block"),
    
    # Electronics Labs
    "EL1": Room(number="EL1", name="Electronics Lab 1", room_type="electronics_lab", capacity=30, building="ECE Block"),
    "EL2": Room(number="EL2", name="Electronics Lab 2", room_type="electronics_lab", capacity=30, building="ECE Block"),
    
    # Seminar Halls
    "SH1": Room(number="SH1", name="Seminar Hall 1", room_type="seminar_hall", capacity=100, building="Main Block"),
    "SH2": Room(number="SH2", name="Seminar Hall 2", room_type="seminar_hall", capacity=80, building="Main Block"),
    
    # Activity Rooms
    "AR1": Room(number="AR1", name="Yoga Hall", room_type="activity_room", capacity=50, building="Sports Block"),
    "AR2": Room(number="AR2", name="Club Room", room_type="activity_room", capacity=40, building="Student Center"),
}

def get_faculty_for_subject(subject_code: str) -> list:
    """Get all faculty who can teach a subject"""
    return [f for f in FACULTY_LIST.values() if subject_code in f.subjects]

def get_rooms_by_type(room_type: str) -> list:
    """Get all rooms of a specific type"""
    return [r for r in ROOM_LIST.values() if r.room_type == room_type]

def get_available_rooms_for_subject(subject_code: str, subject_type: str) -> list:
    """Get available rooms based on subject type"""
    if subject_type == "lab":
        return get_rooms_by_type("computer_lab") + get_rooms_by_type("electronics_lab")
    elif subject_type in ["yoga"]:
        return get_rooms_by_type("activity_room")
    elif subject_type in ["tyl", "9lpa"]:
        return get_rooms_by_type("seminar_hall") + get_rooms_by_type("classroom")
    else:
        return get_rooms_by_type("classroom")
