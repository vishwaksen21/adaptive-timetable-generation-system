# CMRIT Timetable Generation System

## DSA-Based Adaptive Scheduling for CMR Institute of Technology

A comprehensive timetable generation system designed specifically for CMR Institute of Technology (CMRIT), Bangalore, with support for AI&DS and CSDS departments.

**✅ Latest Update (Dec 31, 2025)**: Complete system overhaul with improved scheduling, VTU credits compliance, and clean output format. See [IMPROVEMENTS.md](IMPROVEMENTS.md) and [CREDITS_EXPLANATION.md](CREDITS_EXPLANATION.md) for details.

## Features

### Core Features
- **DSA-Based Scheduling Algorithms**
  - Constraint Satisfaction Problem (CSP) with deterministic greedy scheduling
  - Credit-based round-robin subject selection
  - Smart day block allocation (fills morning first, free periods after 1pm)
  - Soft constraint relaxation with fallback mechanisms
  - Genetic Algorithm (GA) optimization (planned)

- **VTU-Compliant Structure**
  - VTU 2022 Scheme for 5th Semester
  - Indian Standard Time (IST) slots
  - Monday to Saturday schedule (6 days)
  - 7 periods per day with breaks
  - Support for semesters 3, 4, 5, and 6
  - **22 credits = 31 hours/week** (proper credit mapping)

- **Branch & Section Support**
  - AI&DS: 2 sections (AIDS-A, AIDS-B)
  - CSDS: 1 section (CSDS-C)
  - Lab batches (A1/A2/A3, B1/B2/B3, C1/C2/C3)
  - Parallel batch lab sessions

### Time Slots (IST)
| Period | Time |
|--------|------|
| I | 08:00 - 09:00 |
| II | 09:00 - 10:00 |
| Short Break | 10:00 - 10:20 |
| III | 10:20 - 11:20 |
| IV | 11:20 - 12:20 |
| Lunch | 12:20 - 13:00 |
| V | 13:00 - 14:00 |
| VI | 14:00 - 15:00 |
| VII | 15:00 - 16:00 |

### VTU Credits System
- **Theory subjects**: 1 credit = 1 hour/week
  - SEPM, CN, TOC: 4 credits = 4 classes/week
  - CV, RM: 3 credits = 3 classes/week
- **Lab subjects**: 1 credit = 2 hours/week
  - CNL, SEPL: 1 credit = 2 hours/week (continuous blocks)
- **Total**: 22 credits = 31 contact hours + 11 free periods

### Subject Types Supported
- Theory subjects (CN, TOC, SEPM, etc.)
- Laboratory sessions with batch splitting (2-hour continuous blocks)
- Professional Electives (CV, BDA, CC, NoSQL, etc.)
- TYL (Technical/Aptitude/Logical/Soft Skills)
- 9LPA Placement Training
- Yoga sessions (Fixed: Wednesday P6)
- Club activities (Fixed: Wednesday P7)
- Mini Projects (Fixed: Thursday P6-P7)
- Audit courses (Environmental Studies)

### Hard Constraints (Guaranteed)
- ✅ No teacher clashes
- ✅ No room double-booking
- ✅ No section overlaps
- ✅ Required weekly hours per subject (VTU credits compliance)
- ✅ Lab sessions in continuous 2-hour blocks
- ✅ Fixed slot activities respected
- ✅ No same theory subject twice in a day

### Soft Constraints (Optimized)
- Max 3 consecutive theory periods (relaxed when necessary)
- Subject distribution across week
- Fill morning periods first (P1-P4)
- Free periods after 1pm (P5-P7)
- Minimize 8am (P1) classes
- Morning lab preferences

## System Status

**✅ Fully Operational - Production Ready**

Latest test results (Dec 31, 2025):
- Timetable generation: **SUCCESS**
- Hard constraint violations: **0**
- Soft constraint violations: **5** (acceptable)
- Slot utilization: **31/42** (matches required hours exactly)
- Validation score: **970.00/1000**
- Free period distribution: **5 before 1pm, 6 after 1pm**

### Output Features
- ✅ No teacher names displayed (student-friendly format)
- ✅ No room assignments shown (clean output)
- ✅ Empty slots marked as "FREE"
- ✅ Lab batches clearly indicated (C1/C2/C3)
- ✅ JSON, CSV, and HTML export formats
- ✅ Print-friendly timetable view

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Verify system
python verify.py

# Run the web server
python run.py

# Open http://localhost:5000 in your browser
```

## Usage

### Verification
```bash
# Check system health and run validation
python verify.py
```

### Web Interface
```bash
python run.py
# Open http://localhost:5000 in your browser
```

### Command Line
```bash
# Generate timetable for 5th semester AIDS
python run.py --cli --semester 5 --branch AIDS --sections AIDS-A AIDS-B

# Use genetic algorithm (experimental)
python run.py --cli --semester 5 --branch AIDS --algorithm genetic

# Enable debug mode
python run.py --cli --semester 5 --branch AIDS --debug

# Run tests
python test_scheduler.py
```

## Project Structure

```
├── app/
│   ├── web_app.py              # Flask web application
│   └── templates/
│       ├── index.html          # Main UI
│       ├── view_timetable.html # Timetable view
│       └── print_timetable.html # Print-friendly view
├── algorithms/
│   ├── dsa_scheduler.py        # Core scheduling algorithms
│   └── constraint_validator.py # Constraint validation
├── config/
│   ├── vtu_config.py           # VTU configuration
│   ├── semester_subjects.py    # Subject definitions
│   └── faculty_rooms.py        # Faculty & room data
├── data/
│   ├── vtu_subjects.csv        # Subject data
│   ├── vtu_teachers.csv        # Faculty data
│   ├── vtu_rooms.csv           # Room data
│   └── vtu_sections.csv        # Section configuration
├── run.py                      # Main entry point
└── requirements.txt            # Dependencies
```

## API Endpoints

### Configuration
- `GET /api/semesters` - List available semesters
- `GET /api/branches` - List available branches
- `GET /api/subjects/<semester>` - Get subjects for semester
- `GET /api/faculty` - List faculty members
- `GET /api/rooms` - List available rooms

### Generation
- `POST /api/generate` - Generate new timetable
  ```json
  {
    "semester": 5,
    "branch": "AIDS",
    "sections": ["AIDS-A", "AIDS-B"],
    "algorithm": "constraint_satisfaction",
    "debug_mode": false
  }
  ```

### View & Export
- `GET /api/timetable/<id>` - Get generated timetable
- `GET /api/timetable/<id>/section/<section>` - Section timetable
- `GET /api/timetable/<id>/faculty/<faculty_id>` - Faculty schedule
- `GET /api/export/<id>/json` - Export as JSON
- `GET /api/export/<id>/csv` - Export as CSV

## Algorithm Details

### Constraint Satisfaction Problem (CSP) with Greedy Scheduling
Current production algorithm with deterministic behavior:

**Phase 1: Fixed Slot Placement**
- Places fixed activities first (YOGA, CLUB, MP)
- Ensures no conflicts with mandatory slots

**Phase 2: Credit-Based Round-Robin Scheduling**
1. Calculate required periods per day (31 hours ÷ 6 days)
2. Build day blocks that fill morning first (P2-P4), then afternoon
3. Use weighted round-robin to select subjects fairly
4. Place 2-hour lab blocks in valid continuous slots
5. Handle parallel batch labs (3 batches simultaneously)
6. Relax soft constraints when necessary to complete schedule

**Constraint Checking**
- Hard constraints: Must be satisfied (no teacher/room/section clashes)
- Soft constraints: Preferred but can be relaxed (consecutive theory limit)
- Smart backtracking: Continue to next slot instead of failing immediately

**Time Complexity**: O(n×m) where n = subjects, m = slots
**Success Rate**: 100% for configured test cases

### Genetic Algorithm (Experimental)
Evolutionary optimization for complex scenarios:
1. Generate initial population of random timetables
2. Calculate fitness based on constraint satisfaction
3. Tournament selection for breeding
4. Crossover and mutation operations
5. Elitism to preserve best solutions
6. Converge to optimal solution over generations

## Configuration

### Time Slots & Days
Edit [config/vtu_config.py](config/vtu_config.py):
- Modify time slot definitions
- Change working days
- Adjust periods per day
- Configure break timings

### Subjects & Credits
Edit [config/semester_subjects.py](config/semester_subjects.py):
- Add/modify subject definitions
- Set credit hours (4 credits = 4 hours/week for theory)
- Configure lab durations (2-hour continuous blocks)
- Define elective groups
- Set fixed slot activities

### Faculty & Rooms
Edit [config/faculty_rooms.py](config/faculty_rooms.py):
- Add faculty members
- Assign subject expertise
- Define unavailable slots
- Configure room types (classroom, computer_lab, etc.)
- Set room capacities

### Algorithm Parameters
Adjust in [algorithms/dsa_scheduler.py](algorithms/dsa_scheduler.py):
```python
config = {
    'algorithm_type': 'constraint_satisfaction',
    'debug_mode': False,
    'timeout_seconds': 120,
    'max_consecutive_theory': 3,
    'prefer_morning_labs': True,
    'limit_first_period': 3
}
```

## Output Formats

### JSON Export
Complete timetable with metadata, suitable for applications:
```json
{
  "metadata": {
    "semester": 5,
    "branch": "CSDS",
    "generated_at": "2025-12-31T16:05:21",
    "validation": {
      "is_valid": true,
      "hard_violations": 0
    }
  },
  "timetables": {
    "CSDS-C": {
      "days": [...]
    }
  }
}
```

### CSV Export
Tabular format for spreadsheet import (no faculty/room info):
```csv
Section,Day,Period,Time,Subject,Batch,Type
CSDS-C,Monday,1,08:00-09:00,SEPM,,theory
CSDS-C,Monday,5,13:00-14:00,CNL,C1,lab
```

### HTML Export
Print-friendly college notice board format with proper styling.

## Sample Timetable Output

```
Monday:    SEPM | CN | TOC | CV | CNL(C1/C2/C3) | CNL | FREE
Tuesday:   FREE | RM | 9LPA | TYL | SEPL(C1/C2/C3) | SEPL | FREE
Wednesday: FREE | SEPM | CN | TOC | RM | YOGA | CLUB
Thursday:  FREE | CV | ES | SEPM | CN | MP | MP
Friday:    FREE | TOC | 9LPA | TYL | RM | SEPM | FREE
Saturday:  FREE | CN | TOC | CV | FREE | FREE | FREE
```

**Key Features:**
- Morning periods filled first (P1-P4)
- Free periods mostly after 1pm (P5-P7)
- Saturday has afternoon free for weekend
- Labs in 2-hour continuous blocks
- Fixed activities on designated days

### CSV
Tabular format for spreadsheet import.

### Print View
College-style printable format with:
- VTU header
- Subject legend
- Signature blocks

## Requirements
- Python 3.7+
- Flask
- NumPy
- Pandas

## License

MIT License

---

**Note:** This is a computer-generated scheduling system. Final timetables should be reviewed by the Time Table Committee.
- pandas
- numpy