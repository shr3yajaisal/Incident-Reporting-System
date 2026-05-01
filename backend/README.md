# Real-Time Incident Response System - Backend

A complete backend system for real-time incident reporting and management.

## Features

- Real-time incident report submission
- Trust Score calculation (5-factor system)
- Automatic report verification and flagging
- Similarity-based incident grouping
- Confidence and Priority scoring
- WebSocket real-time updates
- Public and Admin REST APIs

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
python app.py
```

The server will start on `http://localhost:5000`

## API Endpoints

### Public Endpoints

- `POST /api/report` - Submit a new incident report
- `GET /api/report/status/<id>` - Get report status
- `GET /api/incidents/public` - Get public incidents (with verified reports)

### Admin Endpoints

- `POST /api/admin/login` - Admin login (username: admin, password: admin123)
- `GET /api/admin/incidents` - Get all incidents
- `GET /api/admin/reports/flagged` - Get flagged reports
- `GET /api/admin/reports/similarity` - Get similarity review queue
- `POST /api/admin/report/<id>/approve` - Approve a flagged report
- `POST /api/admin/report/<id>/reject` - Reject a flagged report
- `POST /api/admin/incident/<id>/resolve` - Resolve/unresolve an incident

## WebSocket Events

The server emits the following events:

- `INCIDENT_CREATED` - New incident created
- `INCIDENT_UPDATED` - Incident updated
- `INCIDENT_RESOLVED` - Incident resolution status changed
- `REPORT_VERIFICATION_UPDATED` - Report verification state changed

## Database

SQLite database (`db.sqlite`) is created automatically on first run.

## Trust Score Calculation

Trust Score is calculated using:
- Evidence consistency (30%)
- Geolocation consistency (25%)
- Category bias (15%)
- Temporal validity (15%)
- Report completeness (15%)

Reports with TS >= 0.4 are automatically verified.

## Similarity Matching

Verified reports are matched to incidents using:
- Spatial proximity (35%)
- Temporal proximity (25%)
- Category match (20%)
- Description similarity (15%)
- Evidence overlap (5%)

- S >= 70%: Auto-merge
- 40% <= S < 70%: Admin review
- S < 40%: New incident

