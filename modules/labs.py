"""Lab and activity scheduling configuration"""

LAB_CONFIG = {
    "Physics Lab": {
        "duration": 2,  # consecutive periods
        "room_type": "lab",
        "max_students": 30,
        "requires_subject": "Physics"
    },
    "Chemistry Lab": {
        "duration": 2,
        "room_type": "lab",
        "max_students": 30,
        "requires_subject": "Chemistry"
    },
    "Programming Lab": {
        "duration": 2,
        "room_type": "computer_lab",
        "max_students": 30,
        "requires_subject": "Programming"
    },
    "DBMS Lab": {
        "duration": 2,
        "room_type": "computer_lab",
        "max_students": 30,
        "requires_subject": "DBMS"
    }
}

ACTIVITIES = {
    "Club": {
        "duration": 2,
        "consecutive": True,
        "frequency": "weekly",
        "priority": 1
    },
    "Sports": {
        "duration": 2,
        "consecutive": True,
        "frequency": "weekly",
        "priority": 2
    },
    "NSS": {
        "duration": 1,
        "consecutive": False,
        "frequency": "weekly",
        "priority": 3
    },
    "Yoga": {
        "duration": 1,
        "consecutive": False,
        "frequency": "weekly",
        "priority": 4
    }
}