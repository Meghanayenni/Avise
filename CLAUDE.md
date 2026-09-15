# CLAUDE.md — AVISE

Standing instructions. Read this at the start of every session, before touching code.

---

## Project

**AVISE** — AI-powered criminal network analysis system. SIH 2026, Problem Statement 26189.

A case-centric investigation workspace that turns fragmented evidence into an explainable network, and asks the investigator to resolve what it cannot resolve on its own.

**AVISE is unrelated to any other project.** Do not import patterns, terminology, schemas or UI from elsewhere.

## Source of truth

`docs/AVISE-report.md` is the agreed specification. `docs/PHASES.md` is the eight-phase implementation roadmap.

The access spine — user, session, case, membership, case-scoping dependency and audit foundation — is built in **Phase 0**, before any feature endpoint exists. Security *screens* come in Phase 5. Never add a route that is not case-scoped and audited.

If the code and the report disagree, the report wins. If you believe the report is wrong, **stop and say so** — do not silently change the architecture.

---

## Non-negotiable invariants

These are enforced in code, not documentation. A change that breaks any of them is wrong even if tests pass.

1. **No silent identity merges.** No code path merges two person entities without an `identity_decisions` row naming a human. Merges are overlay records; underlying entities are never mutated or deleted.

2. **Every edge carries provenance.** An edge without a `edge_provenance` row fails validation. Character offsets (`char_start`, `char_end`) are required on every mention.

3. **`edge_origin` is non-nullable** and one of `system_observed`, `system_inferred`, `investigator_asserted`. Serialisers may not omit it.

4. **Every case-scoped query takes a `case_id`.** No repository function may query case content without one. Case isolation is structural, not filtered in the UI.

5. **Non-members get 404, never 403.** The existence of a case is itself sensitive.

6. **Membership is never cached in the credential.** The session identifies the user only. Membership is re-resolved from the database on every request.

7. **Every sensitive read and every decision writes an audit row.** Append-only, hash-chained.

8. **No conclusory language.** All system-generated user-facing text comes from `avise/core/vocabulary.py`. The banned-phrase test must pass.

9. **Investigator assertions require a stated basis.** An assertion without one is rejected at the API boundary.

10. **Uncertainty is preserved.** Hypotheses stay `PROPOSED` indefinitely. No timeout resolves them.

---

## Architecture rules

### Module structure

```
avise/
  api/        routes, request/response schemas
  core/       config, security, session, audit, vocabulary
  domain/     ontology models — the contract
  ingest/     source adapters, normalisation
  extract/    regex, gazetteers, spaCy
  identity/   candidate generation, scoring, hypothesis lifecycle
  graph/      projection, analytics, scenarios
  patterns/   rule engine, anomaly scoring
  query/      NL translation, structured query execution
  report/     templated brief generation
  db/         models, migrations, repositories
  worker/     job loop
web/          React + TypeScript frontend
```

**Import direction:** `api` may import anything. Domain modules may import `domain` and `db`, never each other. Nothing imports `api`.

### Data

- PostgreSQL is the single source of truth.
- The graph is a projection, rebuildable from Postgres. Never store graph state as truth.
- `GraphProjection.build(case_id, scenario)` — the scenario parameter is present from the first version.
- Files live on the local filesystem; the database stores path + SHA-256.

### Frontend

- One `EvidenceDrawer` component with one contract, mounted at workspace level, dispatched to from every section. **Never build a second detail panel.**
- Heavy sections (graph, map, timeline) lazy-mount via IntersectionObserver.
- Focus modes are routes, not modal state.
- TanStack Query for server state, Zustand for UI state.

---

## Stack — locked

Python 3.11 · FastAPI · Pydantic v2 · SQLAlchemy 2 · Alembic · PostgreSQL 16 · NetworkX · spaCy `en_core_web_md` · rapidfuzz · jellyfish · scikit-learn · pandas · argon2-cffi · pytest

React 18 · Vite · TypeScript · Tailwind · TanStack Query · Zustand · Cytoscape.js · Leaflet · Recharts

**Do not add a dependency without asking.** Specifically banned: any graph database, any vector database, Elasticsearch, Celery, Redis, Kafka, S3/MinIO, sentence-transformers, torch, any GNN library.

---

## Visual language

| Element | Treatment |
|---|---|
| Observed relationship | Steel `#7C8B9A`, solid |
| Inferred relationship | Red `#C8443C`, dashed |
| Identity question | Red, double-dashed, `?` marker |
| Investigator assertion | Warm `#B5A97E`, solid |

Red appears nowhere else — no error states, no alerts, no priority flags. Amber `#D9A441` means "awaiting a decision" and nothing else. Warm paper tones mean "a human wrote this" and nothing else.

Surface `#14161A` · raised `#1C1F24` · card `#22262C` · text `#E8EAED` / `#9AA0A8`.

Mono type only for record identifiers (`CDR-0231`, `FIR/2026/CBE/0412`, phone numbers, timestamps).

No wood, cork, tape, torn edges, rotated cards, handwriting fonts, or scroll animations.

---

## Workflow per phase

```
PLAN → IMPLEMENT → INTEGRATE → TEST → DEBUG → REVIEW → VERIFY → COMMIT
```

1. Re-read the phase in `docs/PHASES.md` and the relevant report sections.
2. State the file list before writing code.
3. Implement completely. No stubs that will need rewriting.
4. Write the tests listed in the phase.
5. Run the full suite, not just the new tests.
6. Work the verification checklist below.
7. Check the implementation against the report section by section.
8. Confirm nothing from earlier phases regressed.
9. Commit and tag.

**A phase is not complete because the code runs.** It is complete when its tests pass, its verification checklist is clear, and it matches the report.

## Verification checklist — every phase

- [ ] Full test suite passes
- [ ] Banned-phrase test passes
- [ ] `alembic upgrade head` works from an empty database
- [ ] Seed script runs clean
- [ ] No TypeScript errors (`npm run typecheck`)
- [ ] No browser console errors or warnings
- [ ] No unhandled backend exceptions in logs
- [ ] Loading and empty states render where relevant
- [ ] Invalid input returns a structured error, never a 500
- [ ] Every new endpoint is case-scoped and audited
- [ ] Every new edge writes provenance
- [ ] Earlier phase features still work
- [ ] Workspace remains responsive on a laptop

## Commit protocol

```
git status                  # check for strays before staging
pytest                      # must pass
npm run typecheck           # must pass
git add -A
git commit -m "Phase N: <name>

<what was built>
<what was tested>
<known limitations, if any>"
git tag phase-N
git push && git push --tags
```

Before committing, confirm: no `.env`, no `__pycache__`, no `node_modules`, no `*.db`, no generated synthetic data, no credentials in code or fixtures, no large binaries.

**Never commit knowingly broken work as a completed phase.** If a phase cannot be finished, say what is blocking it and stop.

---

## Stop and ask when

- The report and a technical constraint genuinely conflict
- A phase needs a dependency not on the locked list
- A change would break an invariant above
- A schema change would require rewriting an earlier phase
- You are about to build a second evidence panel, a second detail view, or a second source of access truth
- Something in the report looks wrong

## Never

- Fabricate data, sources, metrics, or evaluation results
- Use real personal data, real FIRs, scraped content, or real faces
- Write UI copy asserting guilt, risk, danger, or prediction
- Auto-merge person entities
- Cache permissions in a token
- Build cross-case entity linkage
- Add an LLM to the extraction path
