# AVISE — Implementation Roadmap

Eight phases. Work them in order. Read `CLAUDE.md` before every session.

Reference the specification by section: `docs/AVISE-report.md`.

Precedence: `docs/PHASE-0-DECISIONS.md` → `docs/AVISE-report.md` → `docs/PHASES.md` → `CLAUDE.md`.

---

## Phase map

| # | Phase | Type | Depends on |
|---|---|---|---|
| 0 | Contracts, access spine, synthetic data | Foundational | — |
| 1 | Vertical slice — upload to evidence drawer | **First demoable build** | 0 |
| 2 | NLP extraction, entity resolution, identity questions | Feature | 1 |
| 3 | Graph analytics and resolution scenarios | Feature | 2 |
| 4 | Timeline, map, deterministic pattern detection | Feature | 3 |
| 5 | Annotations, assertions, auth UI, access UI, audit view | Feature | 0, 4 |
| 6 | Constrained query layer and investigation reports | Feature | 4 |
| 7 | Hardening and SIH demonstration readiness | Integration | all |

Phases 0 and 1 are strictly sequential. Nothing else starts until the ontology is frozen and the vertical slice runs.

---

# PHASE 0 — Contracts, access spine, synthetic data

**Objective.** Every contract in the project exists and is agreed, and the security spine is in place, before a single feature endpoint is written. Nothing user-visible ships.

**Report sections.** 3, 5, 7, 9, 12, 20–25, 26, 27, 29, 30, 35, 38, 40, 41, 42, 47.

> **Why the access spine is here.** Every endpoint built in Phases 1–4 must be case-scoped and must write an audit row. Building routes first means retrofitting both into every one of them, and missing some. The spine is foundational plumbing; the user-facing security screens stay in Phase 5.

## 0A — Repository and tooling

- Module structure and layered import boundaries exactly as in `CLAUDE.md`
- `.gitignore`, `README.md` (records the `py -3.11` interpreter)
- `docker-compose.yml` for PostgreSQL 16 only
- `pyproject.toml` or `requirements.txt`, virtual environment on Python 3.11
- FastAPI skeleton with `/api/health`, structured error envelope, CORS locked to the dev origin
- Vite + React + TypeScript + Tailwind skeleton, routing shell, design tokens from report §18
- `web/src/theme/TokenSheet.tsx` — one static, unrouted component rendering the four thread types, three card variants and palette swatches
- Alembic wired to an initial revision
- `pytest.ini`, `conftest.py`, test-database fixture
- Scripts: `scripts/dev.ps1`, `test.ps1`, `seed.ps1`, `reset.ps1`, `lint.ps1`, plus a `Makefile` for parity on Unix. `make` is not required.
- Dependencies limited to the approved Phase 0 list in `PHASE-0-DECISIONS.md` §D

## 0B — Ontology and contracts

- `avise/domain/` — Pydantic models for the full ontology (report §7)
  - Node types: Person, Phone, Account, Vehicle, Location, Organisation, Event, Document, Handset, Photo
  - Edge classes: RELATIONSHIP, IDENTITY
  - `edge_origin ∈ {system_observed, system_inferred, investigator_asserted}` — non-nullable
  - On the edge: `edge_origin`, `confidence`, `confidence_basis`, `first_seen_ts`, `last_seen_ts`, `alternative_explanations[]`, `inference_rule_id`, `base_rate_context`
  - On `edge_provenance`: `edge_id`, `document_id`, `record_id`, `mention_id`, locator, `role ∈ {supporting, contradicting}`, `extraction_method`, `created_at`
  - Supporting and contradicting record ids are derived views over `edge_provenance`, never columns
  - `SourceLocator` discriminated union — `text_span`, `record_field`, `record_row` — on both `mentions` and `edge_provenance`, with a per-kind CHECK constraint (report §7)
  - `entities.restricted boolean not null default false` — column only, no gating
- Identity state machine: `PROPOSED`, `CONFIRMED`, `REJECTED`, `NEEDS_EVIDENCE`, `DEFERRED`
- `identity_decisions` schema with `evidence_snapshot`, `rationale_text`, `superseded_by`
- Annotation schema, and `investigator_assertions` schema with the **mandatory basis field** enforced in both Pydantic and a database CHECK (report §8)
- Content origin taxonomy (report §9)
- `case_data_coverage` schema (report §10)
- Source-type enum: `fir`, `cdr`, `transaction`, `surveillance_note`, `prior_record`, `vehicle_registry`, `tower`
- Evidence drawer response contract (report §17)
- `avise/domain/vocabulary.py` — the twenty claim templates (report §12)
- `web/src/types/` — TypeScript mirrors of every domain model
- `web/src/mocks/` — JSON fixtures for all eight workspace sections

## 0C — Access spine *(no user-facing screens)*

**Models and migrations**

```
users                  id · service_id · full_name · designation · email
                       password_hash
                       status(pending_verification|active|suspended|deactivated)
                       failed_login_count · locked_until
                       created_by · created_at · last_login_at

account_capabilities   user_id · capability · granted_by · granted_at · revoked_at
                       capabilities: case:create · audit:read_global · user:provision

sessions               id · user_id · created_at · expires_at · revoked_at
                       ip · user_agent

cases                  id · case_number · title · status(open|closed|archived)
                       created_by · opened_at · closed_at

case_members           id · case_id · user_id · standing(lead|investigator)
                       granted_by · granted_at
                       expires_at · revoked_at · revoke_reason

case_invitations       (table created now, lifecycle logic in Phase 5)

audit_log              id · actor_user_id · action · case_id
                       target_type · target_id · before_state · after_state
                       at · ip · prev_hash · row_hash

jobs                   id · case_id · kind · status · progress · error · timestamps
```

**Authentication foundation**

- Argon2id password hashing (`argon2-cffi`)
- Registration endpoint → `status = pending_verification`
- Activation endpoint, gated on `user:provision`
- Login / logout endpoints, server-side session rows; session tokens stored as SHA-256 only
- Cookie: httpOnly, Secure, SameSite=Lax, 8h sliding renewal
- Identical responses for wrong password and unknown account
- Account lockout: 5 failures within 15 minutes locks for 15 minutes, stored on `users`
- IP rate limit: 10 login attempts per minute, in-process sliding window (`core/ratelimit.py`)

**Permitted routes** — the only routes Phase 0 builds

```
GET    /api/health
POST   /api/auth/register
POST   /api/auth/activate/{user_id}      requires user:provision
POST   /api/auth/login
POST   /api/auth/logout
GET    /api/auth/me                      id, service_id, full_name, designation, status
POST   /api/cases                        requires case:create; writes lead membership
GET    /api/cases                        active memberships only
GET    /api/cases/{case_id}              via get_case_context; audits case.opened
POST   /api/cases/{case_id}/close        lead-only; exists to route-test the 403 rung
```

Membership grant and revoke are **service-level functions** in Phase 0, used by the seed script and tests. Their routes and UI are Phase 5.

**Authorization primitives**

- `standing ∈ {lead, investigator}` — no other roles
- Lead-only actions: invite, remove, transfer lead, close/reopen, reverse another member's decision
- Account capabilities checked separately from case standing

**Case-scoping mechanism**

- One FastAPI dependency, `get_case_context(case_id)`, implementing the ladder:
  ```
  1. Valid session?                     no → 401
  2. Account active?                    no → 401
  3. Active membership on this case?    no → 404   (never 403)
  4. Lead-only action, and not lead?    no → 403
  ```
- Repository base class that refuses any case-content query without a `case_id`
- Case creation writes the lead membership in the same transaction

**Audit foundation**

- Middleware wrapping every sensitive read and every write
- Sensitive read in Phase 0 means entering a case: one `case.opened` row, not one per entity fetched
- Append-only table, one global chain with a `case_id` column; `row_hash = H(prev_hash ‖ row payload)`
- The **complete** event enum from `PHASE-0-DECISIONS.md` A6 is defined now; later phases add emission sites, not migrations
- Phase 0 emits: `auth.register`, `auth.activate`, `auth.login`, `auth.login_failed`, `auth.lockout`, `auth.logout`, `account.capability_granted`, `account.capability_revoked`, `case.created`, `case.opened`, `case.closed`, `membership.granted`, `membership.revoked`
- Chain-verification utility exposed to tests

**Explicitly NOT in Phase 0:** login and registration screens, invitation flow and UI, revocation UI, team management screen, audit viewer. Those are Phase 5.

## 0D — Synthetic data and ground truth

- `tools/generate_data.py`, fixed seed
- Demo volumes per report §41: 40 FIRs, ~8,000 CDR rows, ~1,200 transactions, 25 surveillance notes, 60 prior records, ~40 vehicle registry rows, ~25 towers
- Two districts (Chennai, Coimbatore), three stations
- ~120 background numbers outside every planted structure, traffic weighted toward commercial and transit towers; co-presence base rate derivable from the CDR itself
- Indian realism: 10-digit numbers starting 6–9, `TN 09 BX 1234` registrations, IFSC format, FIR numbering, transliteration variance in names
- All nine planted structures from report §42, **including the three negative cases**: the decoy, the benign coincidence, and the name collision that must not be merged
- `ground_truth.json` — every planted structure, every true identity mapping, every intended negative case
- `demo/` and `holdout/` as independent generations: holdout at ~40% of demo volume, its own nine structures, sharing no entities. Never examined during development.
- Composite-sketch style portraits as procedurally varied **SVG**, clearly synthetic
- `tools/seed.py`, invoked `python -m tools.seed` — demo accounts, one open case, one non-member account

## Tests

- Banned-phrase test over `avise/domain/vocabulary.py`, report templates and `web/src` string tables — no allow-list
- Import boundaries: `tests/structural/test_import_boundaries.py` walks each module's AST
- Domain model round-trip: serialise → deserialise → equal
- `SourceLocator` rejects fields belonging to another kind, in Pydantic and in the database CHECK
- An assertion with a missing or too-short basis is rejected by Pydantic and by the database independently
- Every mock fixture validates against its Pydantic schema
- `alembic upgrade head` from an empty database
- Register → pending account cannot reach any case
- Wrong password and unknown account produce byte-identical responses
- Non-member receives 404, not 403
- Lead-only action as investigator receives 403
- Revoked membership → next request 404, with no wait for expiry
- Audit chain verifies; a tampered row breaks it
- A case cannot exist without a lead
- Data regenerates deterministically from the seed
- Each of the nine planted structures is assert-detectable in the raw output
- No real names, addresses or numbers anywhere in generated data

## Verification

Standard checklist in `CLAUDE.md`. Additionally: grep the codebase and confirm no route reads case content without `get_case_context`, and no permission value appears in the session payload.

## Definition of done

The dev, test, seed and reset scripts run: dev starts API and frontend, test passes. The ontology is frozen. The access ladder is enforced by one dependency. The audit chain verifies. The dataset regenerates deterministically and `ground_truth.json` enumerates all nine structures.

**Commit.** `Phase 0: Contracts, access spine, synthetic data` · tag `phase-0`

---

# PHASE 1 — Vertical slice

**Objective.** One complete path: upload a file, see a graph, click a node, read the source line it came from.

**Report sections.** 13, 16, 17, 18, 31, 32 (Tier 1), 33, 35.

> **This is the first demoable build.** Tag it and never let it break.

### Build

**Ingestion**
- Upload endpoint: extension and magic-byte check, size cap, SHA-256, stored outside the web root, never served by original filename
- `documents` and `records` tables
- Source adapter interface: detect, parse, describe schema
- Adapters for CDR CSV, transaction CSV, FIR text
- Normalisation: phone canonical form, dates to UTC, currency to integer paise, registration spacing, name casing
- Record-level deduplication on content hash
- Worker loop polling `jobs`, progress written back to the row

**Extraction (Tier 1 only)**
- Regex and gazetteers: phones, IMEIs, accounts, IFSC, registrations, dates, amounts
- `mentions` written with a `SourceLocator`, `extraction_method`, `confidence` — `text_span` for narrative text, `record_field` for tabular fields

**Entities, edges, graph**
- Entity creation **only** from exact identifier matches. Nothing about a person clusters automatically.
- Edges, all `edge_origin = system_observed`: `called` from CDR, `transferred_to` from transactions, `mentioned_in` from regex extraction over FIR text
- `edge_provenance` rows, mandatory, validated at write
- `GraphProjection.build(case_id, scenario)` — **scenario parameter present now**, only `confirmed` implemented
- Disk cache keyed by `(case_id, scenario, data_version)`, invalidated on write
- Degree centrality

**API**
- `GET /case/:id/evidence/:subjectType/:subjectId` — full evidence drawer contract
- Source document endpoint returning text plus mention spans
- Every route uses `get_case_context` and writes an audit row

**Frontend**
- Personal dashboard: case list, empty state
- Case workspace shell: sticky header with case number always visible, numbered side rail, eight section placeholders
- Upload UI with live job progress
- Cytoscape.js canvas, filtered subgraph ~40 nodes, thread styling per report §18
- Focus mode at `/case/:id/graph`
- **`EvidenceDrawer`** — one component, one contract, mounted at workspace level, driven by a Zustand store
- Hover preview; click opens the drawer
- Source viewer highlighting the exact span, row or field the locator names
- IntersectionObserver lazy-mount wrapper

### Tests

- Round-trip each source type: upload → records → mentions
- Every `text_span` mention's offsets slice back to its `surface_text` in the source; every `record_field` mention resolves to that field's value
- An edge without provenance is rejected
- Graph rebuild from an empty cache is deterministic
- Two people with identical names do **not** become one entity; two mentions of one phone number **do**
- Evidence endpoint returns a complete contract for a node, an edge and a document
- Same file uploaded twice produces one document
- Oversized, wrong-type and zero-byte uploads rejected cleanly
- Unauthenticated access to `/case/:id` redirects to login; non-member sees not-found
- `npm run typecheck` clean

### Verification

Upload a CDR file and an FIR from a clean database and confirm the whole path works with no manual steps. Delete the graph cache and rebuild — nothing is lost. **Confirm exactly one evidence panel component exists in the codebase.**

**Commit.** `Phase 1: Vertical slice — upload to evidence drawer` · tag `phase-1` and `v0.1-vertical-slice`

---

# PHASE 2 — NLP, entity resolution, identity questions

**Objective.** Hidden connections become visible as questions, never as assumptions.

**Report sections.** 4, 5, 6 (partial), 32 (Tiers 2–3), 37.

> The hardest phase. Budget more time than it looks like it needs.

### Build

- spaCy `en_core_web_md` over FIR narratives and surveillance notes
- Gazetteer boost for Indian given names and surnames
- Extraction benchmark against `holdout/` using `ground_truth.json`
- Name normalisation: honorifics (Shri, Thiru, S/o), initial expansion, name-order canonicalisation
- Blocking: Double Metaphone of surname, district, shared exact identifier, first letter plus length
- Scoring: rapidfuzz `token_set_ratio` and `partial_ratio`, exact identifier matches, contextual features, **contradicting features**
- `identity_hypotheses` with the full feature vector preserved
- Four-state lifecycle and `identity_decisions` with `evidence_snapshot`
- **Overlay merge** — underlying entities never mutated
- Reversal, re-deriving affected findings
- Identity-question edge rendering on the graph
- Review card UI exactly as report §5: supporting, contradicting, not-known, if-confirmed, four actions
- Question queue in the workspace chrome with a live count
- Evaluation harness: precision and recall on holdout

### Tests

- **The planted name collision is not auto-merged** — the defining test of the product
- No code path merges without a decision row
- Confirming changes the graph; reversing restores it exactly
- `evidence_snapshot` captures state at decision time, not current state
- `REJECTED` prevents re-proposal; `NEEDS_EVIDENCE` generates a lead
- Extraction and resolution precision and recall reported on holdout

**Commit.** `Phase 2: NLP, entity resolution, identity questions` · tag `phase-2`

---

# PHASE 3 — Graph analytics and scenarios

**Objective.** The system surfaces the broker nobody searched for, and is honest about which world the number came from.

**Report sections.** 6, 13, 33.

### Build

- Betweenness and closeness centrality, Louvain communities, shortest and k-shortest paths, articulation points, bridges
- Scenarios: `confirmed`, `hypothetical`, `single(hypothesis_id)`
- Scenario label rendered beside every metric — no unlabelled centrality anywhere
- Resolution prioritisation: structural delta per open hypothesis; question queue ranked by impact
- Structural role classification with metric values and thresholds shown
- Network fragility simulation with component and path-length deltas
- Path-between-two-entities UI, community colouring, role badges

### Tests

- The planted broker ranks top by betweenness in `confirmed` after the bridge merge
- The decoy ranks high on degree, low on betweenness, classified peripheral
- Scenario deltas arithmetically correct; fragility counts match a manual recomputation
- Analytics complete under 2s on the demo dataset
- No metric returned without its scenario

**Commit.** `Phase 3: Graph analytics and scenarios` · tag `phase-3`

---

# PHASE 4 — Timeline, map, pattern detection

**Objective.** Time, place and behaviour, all routed through the same evidence drawer.

**Report sections.** 10, 11, 13, 16, 34.

### Build

- Vertical timeline grouped by date; filters by person, phone, vehicle, account, event type, date range, source
- Leaflet map with OSM tiles, incident pins, tower locations, clustering, layer toggles
- Map tile decision resolved for offline operation (report §34) — decided here, when the map is built
- Focus modes at `/case/:id/timeline` and `/case/:id/map`
- Six deterministic pattern rules: burner handset continuity, co-presence without communication, circular fund flow, structuring, communication burst before an incident, newly formed connection
- `base_rate_context` computed and stored for co-presence
- `alternative_explanations` attached by each rule, not per instance
- IsolationForest anomaly scoring with feature attribution, secondary to rules
- `findings` and `leads` as separate tables with separate renderers
- Coverage gap derivation from `case_data_coverage`
- Attention counts in the workspace header

### Tests

- Each rule fires on its planted structure and does not fire on the benign coincidence
- Co-presence does not fire on a high-traffic tower with the same raw count
- Every finding carries supporting evidence, limitations and alternatives
- Every lead is phrased as a question or suggestion — asserted in the vocabulary test
- Anomaly scores always return feature attribution
- Both sections mount only on scroll into view; workspace memory stays flat

**Commit.** `Phase 4: Timeline, map, pattern detection` · tag `phase-4`

---

# PHASE 5 — Annotations, assertions, security UI, audit view

**Objective.** The investigator writes into the board under the same provenance standard the system holds itself to, and the security spine gets its screens.

**Report sections.** 8, 9, 21, 23, 24, 25.

### Build

**Annotation and assertion layer**
- `annotations` on any target type, plus free-standing board notes
- Asserted relationships via thread-drawing between two board items
- Asserted entities for people and objects present in no document
- **Mandatory basis field**, rejected at the API boundary if absent
- `edge_origin = investigator_asserted`, rendered warm and solid
- Edit and delete by author, revoke by lead, every version logged
- Pin-to-board working set; evidence board section
- Content origin filtering everywhere content appears

**Security screens on the Phase 0 spine**
- Login, registration, pending-account state
- Invitation lifecycle: send, seven-day expiry, revoke before acceptance, accept, decline
- Invitation cards on the personal dashboard
- Team management screen, lead only
- Membership revocation with reason; lead transfer; case close and reopen
- Audit section inside the workspace — a first-class section, not a settings page
- Audit filtering by actor, action, date

### Tests

- An assertion without a basis is rejected with a structured error
- Asserted edges participate in analytics as observed, render warm and solid, never dashed
- Annotations never affect analytics
- Only the lead can invite, remove or transfer; expired invitations cannot be accepted
- A revoked member's next request returns 404
- **A revoked member's notes and decisions remain in the case, attributed to them**
- A closed case rejects writes and accepts reads
- The audit chain still verifies after a hundred actions

**Commit.** `Phase 5: Annotations, assertions, security UI, audit view` · tag `phase-5`

---

# PHASE 6 — Constrained query layer and reports

**Objective.** Natural-language querying that never generates claims, and a brief assembled only from structured findings.

**Report sections.** 12, 32 (query layer), 10.

### Build

- Templated brief from structured findings only
- Sections: observed evidence, system inferences, investigator assertions, investigator decisions, unresolved questions, evidence gaps, suggested next steps
- Inline citations; hover reveals the source span
- Export with requesting user and timestamp watermark, audited
- **Optional** query layer: NL → structured query object, **interpreted query shown before it runs**, deterministic execution, results as records with citations
- Untranslatable questions declined plainly
- Manual filter controls as the fallback path

### Tests

- No brief statement exists without a citation; no banned phrase appears
- Missing information stated as missing, never omitted silently
- Export writes an audit row
- Query layer returns records, never prose
- With the model unavailable, filter controls still work

**Commit.** `Phase 6: Query layer and investigation reports` · tag `phase-6`

---

# PHASE 7 — Hardening and demonstration

**Objective.** Make it impossible for the demo to fail.

**Report sections.** 36, 38, 43, 44, 45, 46.

### Build

- Performance pass: lazy mounting verified, graph capped, query indexes checked
- Reset script — one command back to a clean seeded state
- Pre-seeded database snapshot as a demo fallback
- Offline verification: full flow with the network disconnected, including cached map tiles
- Evaluation report: extraction and resolution precision and recall on holdout
- Security pass: upload validation, error leakage, session handling, CORS, secrets audit
- Demo script from report §44, timed; deck

### Tests

- Full suite green; complete demo flow with the network cable pulled
- Reset script works from any state
- Every endpoint audited and case-scoped — verified by script, not by reading
- No secrets in repository history

**Commit.** `Phase 7: Hardening and demonstration readiness` · tag `v1.0-demo`

---

## Starting a phase with Claude Code

```
Read CLAUDE.md and docs/PHASES.md Phase N, plus the report sections
it lists. Do not write code yet.

Give me: the file list you will create or modify, the order you will
build in, anything in the phase that conflicts with the report or with
an earlier phase, and anything you need me to decide.
```

Then, once the plan looks right:

```
Implement Phase N. Work the full loop: implement, integrate, test,
debug, review against the report, verify the checklist, then stop
before committing and report what you found.
```

One phase per session where possible. Starting a fresh session at each phase boundary keeps context small; the phase plan carries state between them.
