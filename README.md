# AVISE

AI-powered criminal network analysis system — SIH 2026, Problem Statement 26189.

A case-centric investigation workspace that turns fragmented evidence into an
explainable network, and asks the investigator to resolve what it cannot resolve
on its own.

**All data in this project is synthetic.** No real FIRs, no real personal data,
no scraped content, no real faces.

## Documents

| Document | Role |
|---|---|
| `docs/PHASE-0-DECISIONS.md` | Binding rulings. Highest precedence. |
| `docs/AVISE-report.md` | The specification. |
| `docs/PHASES.md` | The eight-phase roadmap. |
| `CLAUDE.md` | Standing instructions and invariants. |

Precedence: PHASE-0-DECISIONS → AVISE-report → PHASES → CLAUDE.

## Prerequisites

- **Python 3.11** — use `py -3.11` on Windows. A bare `python` may resolve to an
  older interpreter.
- **Node 20+** — for the frontend, from Phase 0 step 12.
- **Docker** — PostgreSQL 16 only. The application runs on the host.

## One-time setup

```powershell
docker compose up -d db
py -3.11 -m venv .venv
.venv\Scripts\python.exe -m pip install -e ".[dev]"
Copy-Item .env.example .env
```

## Running

```powershell
.\scripts\dev.ps1      # API, plus the frontend once it exists
.\scripts\test.ps1     # pytest, plus npm run typecheck once web/ exists
.\scripts\seed.ps1     # migrate, then load synthetic data and demo accounts
.\scripts\reset.ps1    # destroy the database volume and rebuild from scratch
.\scripts\lint.ps1     # ruff, mypy, tsc
```

`make` is not required. A `Makefile` mirrors these tasks for Unix.

### A note on the session cookie

The session cookie is issued with `Secure`, and browsers treat `http://localhost`
and `http://127.0.0.1` as trustworthy origins, so it works in local development
over plain HTTP.

**It will not work over a LAN IP.** If you open the app from another machine as
`http://192.168.x.x:5173`, the browser will refuse to store the cookie and every
request will read as signed out. Either use HTTPS with a local certificate, or
set `AVISE_SESSION_COOKIE_SECURE=false` for that session only — never in a
shared or demonstration environment.

## Status

Phase 0 in progress. See `docs/PHASES.md`.
