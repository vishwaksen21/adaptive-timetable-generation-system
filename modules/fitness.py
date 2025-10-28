from modules.subjects import SUBJECTS, ACTIVITIES

def calculate_fitness(timetable):
    """Calculate fitness score with lab and activity requirements"""
    if not timetable:
        return float('-inf')
    
    score = 0
    section_data = {}
    
    # Track all assignments
    for entry in timetable:
        section = entry["Section"]
        subject = entry["Subject"]
        day = entry["Day"]
        slot = entry["Slot"]
        
        if section not in section_data:
            section_data[section] = {
                "theory": {},
                "labs": set(),
                "activities": set(),
                "slots": set()
            }
            
        slot_key = (day, slot)
        section_data[section]["slots"].add(slot_key)
        
        # Score theory classes
        if subject in SUBJECTS:
            if subject not in section_data[section]["theory"]:
                section_data[section]["theory"][subject] = 0
            current_count = section_data[section]["theory"][subject]
            if current_count < SUBJECTS[subject]["credits"]:
                score += 100
            section_data[section]["theory"][subject] += 1
            
        # Score labs (2-hour blocks)
        elif subject.endswith("Lab"):
            base_subject = subject.replace(" Lab", "")
            if base_subject in SUBJECTS and "lab" in SUBJECTS[base_subject]:
                if subject not in section_data[section]["labs"]:
                    score += 150
                section_data[section]["labs"].add(subject)
                
        # Score activities
        elif subject in ACTIVITIES:
            if subject not in section_data[section]["activities"]:
                score += 50
            section_data[section]["activities"].add(subject)
            
    # Penalties
    for section, data in section_data.items():
        # Missing required classes
        for subject, config in SUBJECTS.items():
            required = config["credits"]
            actual = data["theory"].get(subject, 0)
            if actual < required:
                score -= 200 * (required - actual)
        
        # Missing labs
        for subject in SUBJECTS:
            if "lab" in SUBJECTS[subject]:
                lab_name = f"{subject} Lab"
                if lab_name not in data["labs"]:
                    score -= 300
                    
        # Missing activities
        for activity in ACTIVITIES:
            if activity not in data["activities"]:
                score -= 100
    
    return score