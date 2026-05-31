from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any

from seed_data import (
    DEFAULT_FOCUS,
    DEFAULT_GAME_STATS,
    DEFAULT_NOTES,
    DEFAULT_PLANNER,
    DEFAULT_SETTINGS,
    DEFAULT_SUBJECTS,
)

BASE_DIR = Path(__file__).resolve().parent
DATABASE_PATH = BASE_DIR / "syllabase.sqlite3"
SCHEMA_PATH = BASE_DIR / "schema.sql"


def get_connection() -> sqlite3.Connection:
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def as_bool(value: Any) -> bool:
    return bool(value)


def bool_int(value: Any) -> int:
    return 1 if bool(value) else 0


def init_db(seed: bool = True) -> None:
    with get_connection() as connection:
        connection.executescript(SCHEMA_PATH.read_text())
        if seed and is_empty(connection):
            seed_db(connection)


def is_empty(connection: sqlite3.Connection) -> bool:
    row = connection.execute("SELECT COUNT(*) AS count FROM subjects").fetchone()
    return row["count"] == 0


def seed_db(connection: sqlite3.Connection) -> None:
    for subject in DEFAULT_SUBJECTS:
        upsert_subject(connection, subject)

    for position, entry in enumerate(DEFAULT_PLANNER):
        upsert_planner_entry(connection, {**entry, "position": position})

    for note in DEFAULT_NOTES:
        upsert_note(connection, note)

    set_focus(connection, DEFAULT_FOCUS)
    set_game_stats(connection, DEFAULT_GAME_STATS)
    set_settings(connection, DEFAULT_SETTINGS)


def get_subjects(connection: sqlite3.Connection) -> list[dict[str, Any]]:
    rows = connection.execute(
        "SELECT id, name, icon, color, hours, mastered FROM subjects ORDER BY created_at, name"
    ).fetchall()
    return [dict(row) for row in rows]


def upsert_subject(connection: sqlite3.Connection, subject: dict[str, Any]) -> dict[str, Any]:
    connection.execute(
        """
        INSERT INTO subjects (id, name, icon, color, hours, mastered, updated_at)
        VALUES (:id, :name, :icon, :color, :hours, :mastered, CURRENT_TIMESTAMP)
        ON CONFLICT(id) DO UPDATE SET
          name = excluded.name,
          icon = excluded.icon,
          color = excluded.color,
          hours = excluded.hours,
          mastered = excluded.mastered,
          updated_at = CURRENT_TIMESTAMP
        """,
        {
            "id": subject["id"],
            "name": subject["name"],
            "icon": subject.get("icon", "SUB"),
            "color": subject.get("color", "#2563eb"),
            "hours": int(subject.get("hours", 0)),
            "mastered": int(subject.get("mastered", 0)),
        },
    )
    return subject


def delete_subject(connection: sqlite3.Connection, subject_id: str) -> None:
    connection.execute("DELETE FROM subjects WHERE id = ?", (subject_id,))


def get_planner(connection: sqlite3.Connection) -> list[dict[str, Any]]:
    rows = connection.execute(
        """
        SELECT id, title, subject_id, type, due_date, priority, estimate, completed, position
        FROM planner_entries
        ORDER BY position, due_date, created_at
        """
    ).fetchall()
    return [
        {
            "id": row["id"],
            "title": row["title"],
            "subjectId": row["subject_id"],
            "type": row["type"],
            "dueDate": row["due_date"],
            "priority": row["priority"],
            "estimate": row["estimate"],
            "completed": as_bool(row["completed"]),
            "position": row["position"],
        }
        for row in rows
    ]


def upsert_planner_entry(connection: sqlite3.Connection, entry: dict[str, Any]) -> dict[str, Any]:
    connection.execute(
        """
        INSERT INTO planner_entries
          (id, title, subject_id, type, due_date, priority, estimate, completed, position, updated_at)
        VALUES
          (:id, :title, :subject_id, :type, :due_date, :priority, :estimate, :completed, :position, CURRENT_TIMESTAMP)
        ON CONFLICT(id) DO UPDATE SET
          title = excluded.title,
          subject_id = excluded.subject_id,
          type = excluded.type,
          due_date = excluded.due_date,
          priority = excluded.priority,
          estimate = excluded.estimate,
          completed = excluded.completed,
          position = excluded.position,
          updated_at = CURRENT_TIMESTAMP
        """,
        {
            "id": entry["id"],
            "title": entry["title"],
            "subject_id": entry["subjectId"],
            "type": entry.get("type", "Homework"),
            "due_date": entry["dueDate"],
            "priority": entry.get("priority", "Medium"),
            "estimate": int(entry.get("estimate", 30)),
            "completed": bool_int(entry.get("completed", False)),
            "position": int(entry.get("position", 0)),
        },
    )
    return entry


def delete_planner_entry(connection: sqlite3.Connection, entry_id: str) -> None:
    connection.execute("DELETE FROM planner_entries WHERE id = ?", (entry_id,))


def get_notes(connection: sqlite3.Connection) -> list[dict[str, Any]]:
    rows = connection.execute(
        """
        SELECT id, title, subject_id, folder, pinned, content, updated_at
        FROM notes
        ORDER BY pinned DESC, updated_at DESC
        """
    ).fetchall()
    return [
        {
            "id": row["id"],
            "title": row["title"],
            "subjectId": row["subject_id"],
            "folder": row["folder"],
            "pinned": as_bool(row["pinned"]),
            "content": row["content"],
            "updatedAt": row["updated_at"][:10],
        }
        for row in rows
    ]


def upsert_note(connection: sqlite3.Connection, note: dict[str, Any]) -> dict[str, Any]:
    connection.execute(
        """
        INSERT INTO notes (id, title, subject_id, folder, pinned, content, updated_at)
        VALUES (:id, :title, :subject_id, :folder, :pinned, :content, CURRENT_TIMESTAMP)
        ON CONFLICT(id) DO UPDATE SET
          title = excluded.title,
          subject_id = excluded.subject_id,
          folder = excluded.folder,
          pinned = excluded.pinned,
          content = excluded.content,
          updated_at = CURRENT_TIMESTAMP
        """,
        {
            "id": note["id"],
            "title": note["title"],
            "subject_id": note["subjectId"],
            "folder": note.get("folder", "Inbox"),
            "pinned": bool_int(note.get("pinned", False)),
            "content": note.get("content", ""),
        },
    )
    return note


def delete_note(connection: sqlite3.Connection, note_id: str) -> None:
    connection.execute("DELETE FROM notes WHERE id = ?", (note_id,))


def get_focus(connection: sqlite3.Connection) -> dict[str, Any]:
    row = connection.execute("SELECT * FROM focus_stats WHERE id = 1").fetchone()
    if row is None:
        set_focus(connection, DEFAULT_FOCUS)
        row = connection.execute("SELECT * FROM focus_stats WHERE id = 1").fetchone()
    return {
        "workMinutes": row["work_minutes"],
        "breakMinutes": row["break_minutes"],
        "sessions": row["sessions"],
        "todayMinutes": row["today_minutes"],
        "sound": as_bool(row["sound"]),
    }


def set_focus(connection: sqlite3.Connection, focus: dict[str, Any]) -> dict[str, Any]:
    connection.execute(
        """
        INSERT INTO focus_stats (id, work_minutes, break_minutes, sessions, today_minutes, sound, updated_at)
        VALUES (1, :work_minutes, :break_minutes, :sessions, :today_minutes, :sound, CURRENT_TIMESTAMP)
        ON CONFLICT(id) DO UPDATE SET
          work_minutes = excluded.work_minutes,
          break_minutes = excluded.break_minutes,
          sessions = excluded.sessions,
          today_minutes = excluded.today_minutes,
          sound = excluded.sound,
          updated_at = CURRENT_TIMESTAMP
        """,
        {
            "work_minutes": int(focus.get("workMinutes", 25)),
            "break_minutes": int(focus.get("breakMinutes", 5)),
            "sessions": int(focus.get("sessions", 0)),
            "today_minutes": int(focus.get("todayMinutes", 0)),
            "sound": bool_int(focus.get("sound", True)),
        },
    )
    return focus


def get_game_stats(connection: sqlite3.Connection) -> dict[str, Any]:
    row = connection.execute("SELECT * FROM game_stats WHERE id = 1").fetchone()
    if row is None:
        set_game_stats(connection, DEFAULT_GAME_STATS)
        row = connection.execute("SELECT * FROM game_stats WHERE id = 1").fetchone()
    return {
        "xp": row["xp"],
        "level": row["level"],
        "streak": row["streak"],
        "flashcard": row["flashcard"],
        "memory": row["memory"],
        "quiz": row["quiz"],
        "runner": row["runner"],
        "pokestudy": row["pokestudy"],
    }


def set_game_stats(connection: sqlite3.Connection, stats: dict[str, Any]) -> dict[str, Any]:
    connection.execute(
        """
        INSERT INTO game_stats (id, xp, level, streak, flashcard, memory, quiz, runner, pokestudy, updated_at)
        VALUES (1, :xp, :level, :streak, :flashcard, :memory, :quiz, :runner, :pokestudy, CURRENT_TIMESTAMP)
        ON CONFLICT(id) DO UPDATE SET
          xp = excluded.xp,
          level = excluded.level,
          streak = excluded.streak,
          flashcard = excluded.flashcard,
          memory = excluded.memory,
          quiz = excluded.quiz,
          runner = excluded.runner,
          pokestudy = excluded.pokestudy,
          updated_at = CURRENT_TIMESTAMP
        """,
        {key: int(stats.get(key, DEFAULT_GAME_STATS[key])) for key in DEFAULT_GAME_STATS},
    )
    return stats


def get_settings(connection: sqlite3.Connection) -> dict[str, Any]:
    row = connection.execute("SELECT * FROM app_settings WHERE id = 1").fetchone()
    if row is None:
        set_settings(connection, DEFAULT_SETTINGS)
        row = connection.execute("SELECT * FROM app_settings WHERE id = 1").fetchone()
    return {
        "setupComplete": as_bool(row["setup_complete"]),
        "theme": row["theme"],
        "activeView": row["active_view"],
        "animations": as_bool(row["animations"]),
        "sounds": as_bool(row["sounds"]),
    }


def set_settings(connection: sqlite3.Connection, settings: dict[str, Any]) -> dict[str, Any]:
    connection.execute(
        """
        INSERT INTO app_settings (id, setup_complete, theme, active_view, animations, sounds, updated_at)
        VALUES (1, :setup_complete, :theme, :active_view, :animations, :sounds, CURRENT_TIMESTAMP)
        ON CONFLICT(id) DO UPDATE SET
          setup_complete = excluded.setup_complete,
          theme = excluded.theme,
          active_view = excluded.active_view,
          animations = excluded.animations,
          sounds = excluded.sounds,
          updated_at = CURRENT_TIMESTAMP
        """,
        {
            "setup_complete": bool_int(settings.get("setupComplete", False)),
            "theme": settings.get("theme", "midnight"),
            "active_view": settings.get("activeView", "dashboard"),
            "animations": bool_int(settings.get("animations", True)),
            "sounds": bool_int(settings.get("sounds", True)),
        },
    )
    return settings


def get_state(connection: sqlite3.Connection) -> dict[str, Any]:
    settings = get_settings(connection)
    return {
        "setupComplete": settings["setupComplete"],
        "theme": settings["theme"],
        "activeView": settings["activeView"],
        "subjects": get_subjects(connection),
        "planner": get_planner(connection),
        "notes": get_notes(connection),
        "focus": get_focus(connection),
        "settings": {
            "animations": settings["animations"],
            "sounds": settings["sounds"],
        },
        "gameStats": get_game_stats(connection),
    }


def replace_state(connection: sqlite3.Connection, state: dict[str, Any]) -> dict[str, Any]:
    connection.execute("DELETE FROM planner_entries")
    connection.execute("DELETE FROM notes")
    connection.execute("DELETE FROM subjects")

    for subject in state.get("subjects", []):
        upsert_subject(connection, subject)

    for position, entry in enumerate(state.get("planner", [])):
        upsert_planner_entry(connection, {**entry, "position": entry.get("position", position)})

    for note in state.get("notes", []):
        upsert_note(connection, note)

    set_focus(connection, state.get("focus", DEFAULT_FOCUS))
    set_game_stats(connection, state.get("gameStats", DEFAULT_GAME_STATS))
    set_settings(
        connection,
        {
            **state.get("settings", {}),
            "setupComplete": state.get("setupComplete", False),
            "theme": state.get("theme", "midnight"),
            "activeView": state.get("activeView", "dashboard"),
        },
    )
    return get_state(connection)
