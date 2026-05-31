from __future__ import annotations

from uuid import uuid4

from flask import Flask, jsonify, request
from flask_cors import CORS

from db import (
    delete_note,
    delete_planner_entry,
    delete_subject,
    get_connection,
    get_focus,
    get_game_stats,
    get_notes,
    get_planner,
    get_settings,
    get_state,
    get_subjects,
    init_db,
    replace_state,
    set_focus,
    set_game_stats,
    set_settings,
    upsert_note,
    upsert_planner_entry,
    upsert_subject,
)

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})


@app.before_request
def ensure_database() -> None:
    init_db(seed=True)


def json_body() -> dict:
    return request.get_json(silent=True) or {}


def api_response(payload, status: int = 200):
    return jsonify(payload), status


def level_from_xp(xp: int) -> int:
    return max(1, xp // 200 + 1)


@app.get("/api/health")
def health():
    return api_response({"status": "ok", "service": "syllabase-api"})


@app.get("/api/state")
def read_state():
    with get_connection() as connection:
        return api_response(get_state(connection))


@app.put("/api/state")
def write_state():
    with get_connection() as connection:
        state = replace_state(connection, json_body())
        return api_response(state)


@app.get("/api/subjects")
def list_subjects():
    with get_connection() as connection:
        return api_response(get_subjects(connection))


@app.post("/api/subjects")
def create_subject():
    subject = json_body()
    subject.setdefault("id", f"subject-{uuid4().hex[:8]}")
    subject.setdefault("icon", subject.get("name", "SUB")[:3].upper())
    subject.setdefault("color", "#2563eb")
    subject.setdefault("hours", 0)
    subject.setdefault("mastered", 0)
    with get_connection() as connection:
        upsert_subject(connection, subject)
        return api_response(subject, 201)


@app.put("/api/subjects/<subject_id>")
def update_subject(subject_id):
    subject = {**json_body(), "id": subject_id}
    with get_connection() as connection:
        upsert_subject(connection, subject)
        return api_response(subject)


@app.delete("/api/subjects/<subject_id>")
def remove_subject(subject_id):
    with get_connection() as connection:
        delete_subject(connection, subject_id)
        return api_response({"deleted": subject_id})


@app.get("/api/planner")
def list_planner():
    with get_connection() as connection:
        return api_response(get_planner(connection))


@app.post("/api/planner")
def create_planner_entry():
    entry = json_body()
    entry.setdefault("id", f"entry-{uuid4().hex[:8]}")
    entry.setdefault("type", "Homework")
    entry.setdefault("priority", "Medium")
    entry.setdefault("estimate", 30)
    entry.setdefault("completed", False)
    with get_connection() as connection:
        upsert_planner_entry(connection, entry)
        return api_response(entry, 201)


@app.put("/api/planner/<entry_id>")
def update_planner_entry(entry_id):
    entry = {**json_body(), "id": entry_id}
    with get_connection() as connection:
        upsert_planner_entry(connection, entry)
        return api_response(entry)


@app.delete("/api/planner/<entry_id>")
def remove_planner_entry(entry_id):
    with get_connection() as connection:
        delete_planner_entry(connection, entry_id)
        return api_response({"deleted": entry_id})


@app.get("/api/notes")
def list_notes():
    with get_connection() as connection:
        return api_response(get_notes(connection))


@app.post("/api/notes")
def create_note():
    note = json_body()
    note.setdefault("id", f"note-{uuid4().hex[:8]}")
    note.setdefault("folder", "Inbox")
    note.setdefault("pinned", False)
    note.setdefault("content", "")
    with get_connection() as connection:
        upsert_note(connection, note)
        return api_response(note, 201)


@app.put("/api/notes/<note_id>")
def update_note(note_id):
    note = {**json_body(), "id": note_id}
    with get_connection() as connection:
        upsert_note(connection, note)
        return api_response(note)


@app.delete("/api/notes/<note_id>")
def remove_note(note_id):
    with get_connection() as connection:
        delete_note(connection, note_id)
        return api_response({"deleted": note_id})


@app.get("/api/focus")
def read_focus():
    with get_connection() as connection:
        return api_response(get_focus(connection))


@app.put("/api/focus")
def write_focus():
    with get_connection() as connection:
        set_focus(connection, json_body())
        return api_response(get_focus(connection))


@app.get("/api/game-stats")
def read_game_stats():
    with get_connection() as connection:
        return api_response(get_game_stats(connection))


@app.put("/api/game-stats")
def write_game_stats():
    with get_connection() as connection:
        set_game_stats(connection, json_body())
        return api_response(get_game_stats(connection))


@app.post("/api/games/answer")
def record_game_answer():
    payload = json_body()
    game_id = payload.get("gameId", "quiz")
    correct = bool(payload.get("correct", False))
    with get_connection() as connection:
        stats = get_game_stats(connection)
        earned = 35 if correct else 5
        stats["xp"] += earned
        stats["level"] = level_from_xp(stats["xp"])
        stats["streak"] = stats["streak"] + 1 if correct else 0
        if game_id in stats:
            stats[game_id] += earned
        set_game_stats(connection, stats)
        return api_response({"earned": earned, "gameStats": get_game_stats(connection)})


@app.get("/api/settings")
def read_settings():
    with get_connection() as connection:
        return api_response(get_settings(connection))


@app.put("/api/settings")
def write_settings():
    with get_connection() as connection:
        set_settings(connection, json_body())
        return api_response(get_settings(connection))


if __name__ == "__main__":
    init_db(seed=True)
    app.run(host="127.0.0.1", port=5000, debug=True)
