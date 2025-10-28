"""Verification script for adaptive timetable generation system"""

import csv
from modules.subjects import SUBJECTS

def verify_system():
    """Verify all system components"""
    print("=" * 60)
    print("ADAPTIVE TIMETABLE GENERATION SYSTEM - VERIFICATION")
    print("=" * 60)
    
    # 1. Check subjects configuration
    print("\n1. SUBJECTS CONFIGURATION:")
    print("-" * 60)
    total_credits = 0
    for subject, config in SUBJECTS.items():
        credits = config.get("credits", 0)
        labs = "Yes" if config.get("labs_per_week", 0) > 0 else "No"
        total_credits += credits
        print(f"   {subject:15} | Credits: {credits} | Labs: {labs}")
    print(f"   Total Credits per Section: {total_credits}")
    
    # 2. Check data files
    print("\n2. DATA FILES VERIFICATION:")
    print("-" * 60)
    files = {
        'data/teachers.csv': 'Teacher',
        'data/rooms.csv': 'Room',
        'data/sections.csv': 'Section',
        'data/subjects.csv': 'Subject'
    }
    
    for filepath, column in files.items():
        try:
            with open(filepath, 'r') as f:
                reader = csv.DictReader(f)
                data = [row[column] for row in reader]
                print(f"   ✅ {filepath}: {len(data)} entries")
        except Exception as e:
            print(f"   ❌ {filepath}: Error - {e}")
    
    # 3. Check output requirements
    print("\n3. TIMETABLE REQUIREMENTS:")
    print("-" * 60)
    print(f"   • Days per week: 5 (Mon-Fri)")
    print(f"   • Periods per day: 6")
    print(f"   • Total slots per week: 30")
    print(f"   • Activities per section: 4 (Club, Sports, NSS, Yoga)")
    print(f"   • Labs per subject: Physics, Chemistry, Programming, DBMS")
    
    # 4. Check credit hours
    print("\n4. CREDIT HOUR DISTRIBUTION:")
    print("-" * 60)
    theory_hours = sum(SUBJECTS[s]["credits"] for s in SUBJECTS)
    lab_hours = sum(2 for s in SUBJECTS if SUBJECTS[s].get("labs_per_week", 0) > 0)  # 2 hrs per lab
    activity_hours = 2 + 2 + 1 + 1  # Club(2) + Sports(2) + NSS(1) + Yoga(1)
    
    print(f"   Theory Classes per Section: {theory_hours} hours/week")
    print(f"   Lab Classes (total): {lab_hours} hours/week")
    print(f"   Activities (total): {activity_hours} hours/week")
    print(f"   Total: {theory_hours + lab_hours + activity_hours} hours/week")
    
    # 5. Check output files
    print("\n5. OUTPUT FILES:")
    print("-" * 60)
    import os
    output_files = [
        'data/final_timetable.csv',
        'data/section_timetables'
    ]
    
    for filepath in output_files:
        if os.path.exists(filepath):
            if os.path.isdir(filepath):
                sections_count = len([f for f in os.listdir(filepath) if f.endswith('.txt')])
                print(f"   ✅ {filepath}: {sections_count} section timetables")
            else:
                size = os.path.getsize(filepath)
                print(f"   ✅ {filepath}: {size} bytes")
        else:
            print(f"   ⚠️  {filepath}: Not yet created")
    
    print("\n" + "=" * 60)
    print("VERIFICATION COMPLETE!")
    print("=" * 60)