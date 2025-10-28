import datetime

def apply_adaptive_changes(timetable, holidays, absentees):
    """Apply changes to timetable for holidays and absent teachers"""
    updated = []
    
    for slot in timetable:
        # Skip slots on holidays
        if slot["Day"] in holidays:
            continue
            
        # Reassign slots with absent teachers
        if slot["Teacher"] in absentees:
            # For now, just mark as "Reassigned"
            slot = slot.copy()
            slot["Teacher"] = "Reassigned"
        
        updated.append(slot)
        
    return updated
