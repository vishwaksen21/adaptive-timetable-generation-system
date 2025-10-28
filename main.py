from typing import List, Dict
import csv
from modules.ga_core import run_genetic_algorithm
from modules.subjects import SUBJECTS
import os

def read_csv_column(filepath: str, column_name: str) -> List[str]:
    """Read a single column from a CSV file"""
    with open(filepath, 'r') as f:
        reader = csv.DictReader(f)
        return [row[column_name] for row in reader]

def load_data():
    """Load input data including labs and activities"""
    # Load base data
    teachers = read_csv_column('data/teachers.csv', 'Teacher')
    subjects = read_csv_column('data/subjects.csv', 'Subject')
    rooms = read_csv_column('data/rooms.csv', 'Room')
    sections = read_csv_column('data/sections.csv', 'Section')
    
    # Add labs for subjects that have them
    lab_subjects = []
    for subject in subjects:
        if subject in SUBJECTS and SUBJECTS[subject].get("labs_per_week", 0) > 0:
            lab_subjects.append(f"{subject} Lab")
    subjects.extend(lab_subjects)
    
    # Add activities
    activities = ["Club", "Sports", "NSS", "Yoga"]
    subjects.extend(activities)
    
    return teachers, subjects, rooms, sections

def save_timetable(timetable: List[Dict], filepath: str):
    """Save timetable to CSV"""
    if not timetable:
        return
        
    fieldnames = list(timetable[0].keys())
    with open(filepath, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(timetable)

def create_grid_timetable(timetable: List[Dict]):
    """Create grid-based timetable for each section"""
    os.makedirs('data/section_timetables', exist_ok=True)
    
    # Group by section
    sections_data = {}
    for entry in timetable:
        section = entry["Section"]
        if section not in sections_data:
            sections_data[section] = []
        sections_data[section].append(entry)
    
    # Days and periods
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    day_short = ["Mon", "Tue", "Wed", "Thu", "Fri"]
    periods = [1, 2, 3, 4, 5, 6]
    period_times = [
        "09:00–09:50",
        "10:00–10:50",
        "11:00–11:50",
        "12:00–12:50",
        "02:00–02:50",
        "03:00–03:50"
    ]
    
    # Create timetable for each section
    for section, entries in sections_data.items():
        filename = f'data/section_timetables/{section}_timetable.txt'
        
        with open(filename, 'w') as f:
            # Title
            f.write(f"TIMETABLE – {section}\n\n")
            
            # Header row with times
            f.write("Day/Period")
            for time in period_times:
                f.write(f" | {time}")
            f.write("\n")
            
            # Separator line
            f.write("-" * 120 + "\n")
            
            # Each day row
            for day_idx, day in enumerate(days):
                day_cells = [day]  # Start with day name
                
                # For each period, get the cell content
                for period in periods:
                    entries_found = [e for e in entries 
                                   if e["Day"] == day_short[day_idx] and e["Slot"] == period]
                    
                    if entries_found:
                        e = entries_found[0]
                        # Format: Subject\n(Teacher/Room)
                        cell_content = f"{e['Subject']}\n({e['Teacher']}/{e['Room']})"
                        day_cells.append(cell_content)
                    else:
                        day_cells.append("")
                
                # Write day row
                f.write(day_cells[0])  # Day name
                for cell in day_cells[1:]:
                    if cell:
                        f.write(f" | {cell}")
                    else:
                        f.write(" | ")
                
                f.write("\n\n")
        
        print(f"✅ Created formatted timetable for {section}")

if __name__ == "__main__":
    print("=== Adaptive Timetable Generation System ===")
    
    # Load data
    teachers, subjects, rooms, sections = load_data()
    
    # Generate timetable
    timetable = run_genetic_algorithm(teachers, subjects, rooms, sections)
    
    # Calculate and display final fitness
    final_fitness = len(timetable) * 100
    print(f"\n=== Final Timetable ===")
    print(f"Total Classes Scheduled: {len(timetable)}")
    print(f"Final Fitness Score: {final_fitness:.2f}\n")
    
    # Save to CSV
    save_timetable(timetable, 'data/final_timetable.csv')
    
    # Create grid-based section timetables
    create_grid_timetable(timetable)
    
    print("\n✅ Timetable saved to data/final_timetable.csv")
    print("✅ Grid timetables created in data/section_timetables/")
