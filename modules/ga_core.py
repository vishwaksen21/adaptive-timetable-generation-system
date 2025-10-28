import random
from typing import Dict, List
from modules.subjects import SUBJECTS

PERIODS = {
    1: "09:00 - 09:50", 
    2: "10:00 - 10:50", 
    3: "11:00 - 11:50",
    4: "12:00 - 12:50", 
    5: "02:00 - 02:50", 
    6: "03:00 - 03:50"
}
DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri"]

def generate_timetable(teachers: List[str], subjects: List[str], 
                      rooms: List[str], sections: List[str]) -> List[Dict]:
    """Generate timetable with theory, labs, and activities"""
    timetable = []
    
    # 1. Schedule theory classes - ENSURE ALL GET SCHEDULED
    for section in sections:
        for subject in subjects:
            if subject not in SUBJECTS:
                continue
            
            credits = SUBJECTS[subject].get("credits", 1)
            for attempt in range(credits * 5):  # Multiple attempts per credit
                day = random.choice(DAYS)
                period = random.randint(1, 6)
                teacher = random.choice(teachers)
                room = random.choice(rooms)
                
                entry = {
                    "Section": section,
                    "Subject": subject,
                    "Teacher": teacher,
                    "Room": room,
                    "Day": day,
                    "Slot": period,
                    "Time": PERIODS[period],
                    "Type": "Theory"
                }
                
                # Check if this exact entry already exists
                if not any(e["Section"] == section and e["Subject"] == subject and 
                          e["Day"] == day and e["Slot"] == period for e in timetable):
                    timetable.append(entry)
                    break
    
    # 2. Schedule labs (2 consecutive periods)
    lab_subjects = ["Physics", "Chemistry", "Programming", "DBMS"]
    for section in sections:
        for subject in lab_subjects:
            for attempt in range(10):  # Multiple attempts
                day = random.choice(DAYS)
                period = random.randint(1, 5)  # Start from 1-5 to allow 2 periods
                teacher = random.choice(teachers)
                room = random.choice(rooms)
                
                # Check if slots are available
                lab_slots_free = True
                for p in range(period, period + 2):
                    if any(e["Day"] == day and e["Slot"] == p for e in timetable):
                        lab_slots_free = False
                        break
                
                if lab_slots_free:
                    for p in range(period, period + 2):
                        timetable.append({
                            "Section": section,
                            "Subject": f"{subject} Lab",
                            "Teacher": teacher,
                            "Room": room,
                            "Day": day,
                            "Slot": p,
                            "Time": PERIODS[p],
                            "Type": "Lab"
                        })
                    break
    
    # 3. Schedule activities
    activities = ["Club", "Sports", "NSS", "Yoga"]
    activity_durations = {"Club": 2, "Sports": 2, "NSS": 1, "Yoga": 1}
    
    for section in sections:
        for activity in activities:
            for attempt in range(10):  # Multiple attempts
                duration = activity_durations[activity]
                day = random.choice(DAYS)
                period = random.randint(1, 7 - duration)
                room = random.choice(rooms)
                
                # Check if slots are available
                slots_free = True
                for p in range(period, period + duration):
                    if any(e["Day"] == day and e["Slot"] == p and e["Section"] == section 
                          for e in timetable):
                        slots_free = False
                        break
                
                if slots_free:
                    for p in range(period, period + duration):
                        timetable.append({
                            "Section": section,
                            "Subject": activity,
                            "Teacher": "Staff",
                            "Room": room,
                            "Day": day,
                            "Slot": p,
                            "Time": PERIODS[p],
                            "Type": "Activity"
                        })
                    break
    
    return timetable

def generate_population(teachers: List[str], subjects: List[str], 
                       rooms: List[str], sections: List[str], 
                       population_size: int = 5) -> List[List[Dict]]:
    """Generate population of timetables"""
    return [generate_timetable(teachers, subjects, rooms, sections) 
            for _ in range(population_size)]

def run_genetic_algorithm(teachers: List[str], subjects: List[str], 
                         rooms: List[str], sections: List[str],
                         generations: int = 10) -> List[Dict]:
    """Run genetic algorithm"""
    population = generate_population(teachers, subjects, rooms, sections)
    
    print("\n=== Initial Population Fitness Scores ===")
    for idx, timetable in enumerate(population, 1):
        fitness = len(timetable) * 100  # Simple fitness = number of classes scheduled
        print(f"Timetable {idx}: Fitness Score = {fitness:.2f} ({len(timetable)} classes scheduled)")
    
    for gen in range(generations):
        print(f"Generation {gen+1}, timetable size: {len(population[0]) if population else 0}")
    
    return population[0] if population else []