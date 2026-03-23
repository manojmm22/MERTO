# Metro Arrival Predictor

A small **Flask** web app that estimates metro segment and full-line **arrival times** using a trained **linear Perceptron** model, with **SQLite** persistence and an interactive **Leaflet** route map.

## Features

- **Single-station ETA** from departure time, distance, speed, and dwell time  
- **Full-journey timeline** along seeded corridor stations  
- **Perceptron** trained on synthetic data aligned with kinematic travel time  
- **REST API** for predictions, stations, history, and statistics  
- **Operations-style UI** with map, stats, and recent prediction history  

## Tech stack

| Layer | Choice |
|--------|--------|
| Web | Flask 3 |
| ML | Single-layer Perceptron (pure Python) |
| Data | SQLite (`metro.db` auto-created on first run) |
| Map | Leaflet + OpenStreetMap / Esri imagery |

## Project layout

```
Metro/
├── app.py              # Flask routes and API
├── perceptron_model.py # Model training & inference
├── database.py         # SQLite schema, stations, predictions
├── requirements.txt
├── SPEC.md             # Original design notes
├── templates/
│   └── index.html      # Single-page UI
└── README.md
```

## Prerequisites

- **Python 3.10+** recommended  
- `pip`  

## Setup

```bash
cd Metro
python -m venv .venv
```

**Windows (PowerShell):**

```powershell
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

**macOS / Linux:**

```bash
source .venv/bin/activate
pip install -r requirements.txt
```

## Run locally

```bash
python app.py
```

Open **http://127.0.0.1:5000** in your browser.

The first run creates `metro.db` and seeds default stations with coordinates for the map.

## API (summary)

| Method | Path | Purpose |
|--------|------|---------|
| `GET` | `/` | Web UI |
| `POST` | `/api/predict` | Single-segment prediction (JSON) |
| `POST` | `/api/journey` | Full line prediction |
| `GET` | `/api/stations` | Stations for map and journey |
| `GET` | `/api/history?limit=20` | Recent predictions |
| `GET` | `/api/statistics` | Counts (stations, predictions, routes) |
| `POST` | `/api/train` | Retrain / reload model |

Example `POST /api/predict` body:

```json
{
  "departure_time": "08:00",
  "distance": 2.5,
  "speed": 40,
  "dwell_time": 0.5
}
```

`dwell_time` is in **minutes** (converted to seconds server-side).

## Production notes

- Replace the default Flask **`SECRET_KEY`** in `app.py` with a secure value (e.g. environment variable).  
- Use a production WSGI server (e.g. **gunicorn**, **waitress**, or **Hypercorn**) instead of `app.run(debug=True)`.  

## License

Use and modify freely for learning and demos; add a license file if you redistribute.

---

## Push this project to GitHub ([manojmm22](https://github.com/manojmm22))

1. On GitHub, create a **new empty repository** (e.g. `metro-arrival-predictor`):  
   [https://github.com/new](https://github.com/new)  
   Do **not** add a README, `.gitignore`, or license on GitHub if you already have them locally.

2. **In this project folder** (`Metro`), run:

```bash
git init
git add .
git commit -m "Initial commit: Metro Arrival Predictor"
git branch -M main
git remote add origin https://github.com/manojmm22/metro-arrival-predictor.git
git push -u origin main
```

Change the repo name in the URL if you used something other than `metro-arrival-predictor`.

**GitHub CLI** (optional):

```bash
gh auth login
gh repo create metro-arrival-predictor --public --source=. --remote=origin --push
```

After pushing, the repo will appear on your profile: [github.com/manojmm22](https://github.com/manojmm22).
