# 🎓 CMRIT Timetable Generator

> **Smart DSA-based scheduling system for VTU 2022 Scheme** - Automated timetable generation for CMR Institute of Technology with zero constraint violations.

[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/flask-2.3.0-green.svg)](https://flask.palletsprojects.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Status](https://img.shields.io/badge/status-production%20ready-success.svg)]()


## ✨ Key Features

- 🚀 **DSA-Based CSP Algorithm** - Constraint Satisfaction with greedy scheduling
- 📚 **VTU 2022 Compliant** - 22 credits = 31 hours/week (Sem 3-6)
- 🎯 **Zero Hard Violations** - 970/1000 validation score
- 🏫 **Multi-Branch Support** - AI&DS (2 sections) & CSDS (1 section)
- 🔄 **Smart Scheduling** - Morning priority, free periods after 1pm
- 📊 **Multiple Exports** - JSON, CSV, HTML formats
- 🖨️ **Print-Friendly** - Clean output without faculty/room details

## 🚀 Quick Start

```bash
# Install and verify
pip install -r requirements.txt
python verify.py

# Run web interface
python run.py
# Open http://localhost:5000
```

## 📊 System Performance

| Metric | Result |
|--------|--------|
| Hard Violations | ✅ 0 |
| Validation Score | 970/1000 |
| Slot Utilization | 31/42 (VTU compliant) |
| Free Periods | 5 AM / 6 PM |
| Success Rate | 100% |

## ⏰ Time Slots (IST)

```
I    08:00-09:00    |    Short Break 10:00-10:20
II   09:00-10:00    |    Lunch Break 12:20-13:00
III  10:20-11:20    |
IV   11:20-12:20    |    V-VII: 13:00-16:00
```

## 🎯 Constraints

**Hard (Guaranteed)**
- ✅ No teacher/room/section clashes
- ✅ VTU credit compliance
- ✅ 2-hour continuous lab blocks
- ✅ Fixed slot activities (Yoga, Club, MP)

**Soft (Optimized)**
- Morning priority scheduling
- Max 3 consecutive theory classes
- Balanced subject distribution

## 📖 Usage

### Web Interface
```bash
python run.py
```

### Command Line
```bash
# Generate for 5th semester AIDS
python run.py --cli --semester 5 --branch AIDS

# With debug mode
python run.py --cli --semester 5 --branch AIDS --debug
```

### API Example
```bash
curl -X POST http://localhost:5000/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "semester": 5,
    "branch": "CSDS",
    "sections": ["CSDS-C"],
    "algorithm": "constraint_satisfaction"
  }'
```


## 📁 Project Structure

```
├── algorithms/         # Core scheduling logic (CSP + GA)
├── app/               # Flask web app + templates
├── config/            # VTU config, subjects, faculty
├── data/              # Generated timetables & exports
└── run.py             # Main entry point
```

## ⚙️ Configuration

**Subjects & Credits** → [config/semester_subjects.py](config/semester_subjects.py)  
**Faculty & Rooms** → [config/faculty_rooms.py](config/faculty_rooms.py)  
**Time Slots** → [config/vtu_config.py](config/vtu_config.py)

## 📄 Sample Output

```
Monday:    SEPM | CN | TOC | CV | CNL(C1/C2/C3) | CNL | FREE
Tuesday:   FREE | RM | 9LPA | TYL | SEPL(C1/C2/C3) | SEPL | FREE
Wednesday: FREE | SEPM | CN | TOC | RM | YOGA | CLUB
Thursday:  FREE | CV | ES | SEPM | CN | MP | MP
Friday:    FREE | TOC | 9LPA | TYL | RM | SEPM | FREE
Saturday:  FREE | CN | TOC | CV | FREE | FREE | FREE
```

**✨ Features:** Morning-first scheduling • Labs in 2-hour blocks • Fixed activities • Clean format

## 🔧 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/generate` | POST | Generate timetable |
| `/api/timetable/<id>` | GET | View timetable |
| `/api/export/<id>/json` | GET | Export JSON |
| `/api/export/<id>/csv` | GET | Export CSV |

## 🧪 Algorithm

**Constraint Satisfaction Problem (CSP)**
1. Place fixed slots (Yoga, Club, MP)
2. Credit-based round-robin selection
3. Morning-first allocation (P2-P4)
4. 2-hour lab block placement
5. Soft constraint relaxation

**Complexity:** O(n×m) | **Success:** 100%

## 📦 Requirements

```
Python 3.7+
Flask 2.3.0
Pandas
NumPy
```

## 📝 License

MIT License

---

**⚠️ Note:** Computer-generated schedules should be reviewed by the Time Table Committee before finalization.