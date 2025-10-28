"""Subject and credit hour configuration"""

SUBJECTS = {
    "Mathematics": {
        "credits": 4,
        "type": "theory",
        "priority": 1,
        "labs_per_week": 0
    },
    "Physics": {
        "credits": 3,
        "type": "theory",
        "priority": 2,
        "labs_per_week": 1,
        "lab_duration": 2
    },
    "Chemistry": {
        "credits": 3,
        "type": "theory",
        "priority": 2,
        "labs_per_week": 1,
        "lab_duration": 2
    },
    "Programming": {
        "credits": 2,
        "type": "theory",
        "priority": 3,
        "labs_per_week": 1,
        "lab_duration": 2
    },
    "DBMS": {
        "credits": 3,
        "type": "theory",
        "priority": 2,
        "labs_per_week": 1,
        "lab_duration": 2
    },
    "English": {
        "credits": 1,
        "type": "theory",
        "priority": 4,
        "labs_per_week": 0
    }
}

ACTIVITIES = {
    "Club": {
        "hours": 2,
        "consecutive": True,
        "per_week": 1,
        "priority": 5
    },
    "Sports": {
        "hours": 2,
        "consecutive": True,
        "per_week": 1,
        "priority": 6
    },
    "NSS": {
        "hours": 1,
        "consecutive": False,
        "per_week": 1,
        "priority": 7
    },
    "Yoga": {
        "hours": 1,
        "consecutive": False,
        "per_week": 1,
        "priority": 7
    }
}