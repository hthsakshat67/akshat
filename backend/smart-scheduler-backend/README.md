# Syllabase Flask Backend

Python Flask API for the Syllabase study planner. It stores the app state in SQLite and exposes endpoints for subjects, planner cards, notes, focus stats, game stats, settings, and full state sync.

## Run locally

```bash
cd backend/smart-scheduler-backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py
```

The API runs at:

```text
http://127.0.0.1:5000/api
```

## Frontend connection

The React app defaults to the local Flask API. To point it somewhere else, set:

```bash
REACT_APP_API_URL=http://127.0.0.1:5000/api
```

If the backend is offline, the frontend keeps working with browser local storage and shows a local-mode status pill.

## Useful endpoints

- `GET /api/health`
- `GET /api/state`
- `PUT /api/state`
- `GET|POST /api/subjects`
- `GET|POST /api/planner`
- `GET|POST /api/notes`
- `GET|PUT /api/focus`
- `GET|PUT /api/game-stats`
- `GET|PUT /api/settings`
- `POST /api/games/answer`

