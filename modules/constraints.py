from modules.subjects import SUBJECTS, ACTIVITIES

def is_valid_timetable(timetable):
    """Validate timetable including labs and activities"""
    if not timetable:
        return False

    # Track assignments per section
    section_data = {}
    for entry in timetable:
        section = entry["Section"]
        subject = entry["Subject"]
        day = entry["Day"]
        slot = entry["Slot"]
        
        if section not in section_data:
            section_data[section] = {
                "theory": {},       # subject -> count
                "labs": set(),      # set of completed labs
                "activities": set() # set of completed activities
            }
            
        # Check if it's a lab
        if subject.endswith("Lab"):
            section_data[section]["labs"].add(subject)
        # Check if it's an activity
        elif subject in ["Club", "Sports", "NSS", "Yoga"]:
            section_data[section]["activities"].add(subject)
        # Regular subject
        else:
            if subject not in section_data[section]["theory"]:
                section_data[section]["theory"][subject] = 0
            section_data[section]["theory"][subject] += 1

    slot_map = {}  # (day, period) -> set of (teacher, room, section)
    
    for entry in timetable:
        key = (entry["Day"], entry["Slot"])
        if key not in slot_map:
            slot_map[key] = {"teachers": set(), "rooms": set(), "sections": set()}
            
        # Check basic conflicts
        if entry["Teacher"] in slot_map[key]["teachers"]:
            return False
        if entry["Room"] in slot_map[key]["rooms"]:
            return False
        if entry["Section"] in slot_map[key]["sections"]:
            return False
            
        # Track assignments
        slot_map[key]["teachers"].add(entry["Teacher"])
        slot_map[key]["rooms"].add(entry["Room"])
        slot_map[key]["sections"].add(entry["Section"])
    
    return True