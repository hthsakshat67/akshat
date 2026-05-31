DEFAULT_SUBJECTS = [
    {"id": "calculus", "name": "Calculus", "icon": "CAL", "color": "#2563eb", "hours": 18, "mastered": 72},
    {"id": "physics", "name": "Physics", "icon": "PHY", "color": "#7c3aed", "hours": 14, "mastered": 58},
    {"id": "chemistry", "name": "Chemistry", "icon": "CHE", "color": "#059669", "hours": 21, "mastered": 81},
    {"id": "literature", "name": "Literature", "icon": "LIT", "color": "#d97706", "hours": 10, "mastered": 64},
]

DEFAULT_PLANNER = [
    {
        "id": "task-1",
        "title": "Limits mixed review",
        "subjectId": "calculus",
        "type": "Exam",
        "dueDate": "2026-05-24",
        "priority": "High",
        "estimate": 90,
        "completed": False,
    },
    {
        "id": "task-2",
        "title": "Circuit analysis worksheet",
        "subjectId": "physics",
        "type": "Homework",
        "dueDate": "2026-05-22",
        "priority": "High",
        "estimate": 60,
        "completed": False,
    },
    {
        "id": "task-3",
        "title": "Equilibrium flashcards",
        "subjectId": "chemistry",
        "type": "Quiz",
        "dueDate": "2026-05-21",
        "priority": "Medium",
        "estimate": 35,
        "completed": True,
    },
    {
        "id": "task-4",
        "title": "Essay outline polish",
        "subjectId": "literature",
        "type": "Project",
        "dueDate": "2026-05-27",
        "priority": "Medium",
        "estimate": 50,
        "completed": False,
    },
]

DEFAULT_NOTES = [
    {
        "id": "note-1",
        "title": "Calculus exam map",
        "subjectId": "calculus",
        "folder": "Revision",
        "pinned": True,
        "content": "# Integration checklist\n- Substitution patterns\n- Parts table\n- Trig identities\n\nFocus on recognizing the first step quickly.",
    },
    {
        "id": "note-2",
        "title": "Physics formula bank",
        "subjectId": "physics",
        "folder": "Formulas",
        "pinned": False,
        "content": "Ohm law: V = IR\nPower: P = IV\nSeries circuits share current.",
    },
]

DEFAULT_FOCUS = {
    "workMinutes": 25,
    "breakMinutes": 5,
    "sessions": 4,
    "todayMinutes": 85,
    "sound": True,
}

DEFAULT_GAME_STATS = {
    "xp": 1280,
    "level": 7,
    "streak": 9,
    "flashcard": 420,
    "memory": 310,
    "quiz": 550,
    "runner": 280,
    "pokestudy": 190,
}

DEFAULT_SETTINGS = {
    "setupComplete": False,
    "theme": "midnight",
    "activeView": "dashboard",
    "animations": True,
    "sounds": True,
}
