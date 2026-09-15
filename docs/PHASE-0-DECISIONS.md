# AVISE — Phase 0 Decisions

Rulings on every question raised during Phase 0 reconciliation.
Place at `docs/PHASE-0-DECISIONS.md`, commit, and treat as binding.

Precedence from now on: **PHASE-0-DECISIONS.md → AVISE-report.md → PHASES.md → CLAUDE.md**.
Where this document settles a contradiction, the losing document is to be corrected, not left standing.

---

## A. Structural contradictions

### A1. Report filename

**Rename the file.** `docs/AVISE-complete-report.md` → `docs/AVISE-report.md`.

Remove the line in Phase 0A that lists `docs/AVISE-report.md` as something to create. It exists; it is not a deliverable.

### A2. Phase plan — §43 vs PHASES.md

**PHASES.md controls sequencing.** But do not leave a standing exception to "report wins" — that rule is load-bearing and should not have a carve-out.

Correct the report instead:
- Rewrite **§43** to the eight-phase structure in PHASES.md, with the access spine in Phase 0 and a one-line note explaining why it moved.
- Update **§47** (Phase 0 checklist) to match the Phase 0 deliverables in PHASES.md.

After that edit, report and roadmap agree and the precedence rule holds unmodified.

### A3. Provenance — §7 vs §35

**§35 is correct. §7 is wrong and must be rewritten.**

The split:

```
ON THE EDGE (interpretation — what the system concluded)
  edge_origin            non-nullable
  confidence             float[0,1]
  confidence_basis       jsonb, list of contributing reasons
  first_seen_ts · last_seen_ts
  alternative_explanations   jsonb list
  inference_rule_id      nullable, set for system_inferred
  base_rate_context      jsonb, nullable

ON edge_provenance (attribution — where it came from)
  edge_id
  document_id · record_id · mention_id   (nullable as appropriate)
  locator_kind + locator fields
  role                   supporting | contradicting
  extraction_method
  created_at
```

`supporting_record_ids[]` and `contradicting_record_ids[]` are **derived views** over `edge_provenance` filtered by `role`. They are not columns. Anything that stores them as columns creates a second source of truth for the same fact.

`extraction_method` belongs on the provenance row, not the edge — one edge may be supported by a regex match and a spaCy match, and each carries its own method.

### A4. Provenance locator — a problem not yet raised

Character offsets are meaningful for FIR narratives and surveillance notes. They are **meaningless for a CDR or transaction row**. The spec as written would force fabricated offsets onto tabular data, and "click evidence, see the highlighted source" would silently fail for the majority of records.

**Ruling — a discriminated union:**

```python
class TextSpan(BaseModel):
    kind: Literal["text_span"]
    document_id: UUID; char_start: int; char_end: int

class RecordField(BaseModel):
    kind: Literal["record_field"]
    record_id: UUID; field_name: str

class RecordRow(BaseModel):
    kind: Literal["record_row"]
    record_id: UUID

SourceLocator = Annotated[Union[TextSpan, RecordField, RecordRow],
                          Field(discriminator="kind")]
```

Mirrored in the database as `locator_kind` plus nullable `char_start`, `char_end`, `field_name`, with a CHECK constraint enforcing the correct fields per kind. Applies to both `mentions` and `edge_provenance`.

This must be settled in Phase 0. Retrofitting it means re-extracting the entire corpus.

### A5. Account status value

**`pending_verification` everywhere.** Correct the PHASES.md `users` table, which says `pending`.

Full enum: `pending_verification | active | suspended | deactivated`.

### A6. Audit event enum

**Define the complete enum in Phase 0. Emit only what Phase 0 can trigger.**

An enum is a contract, not behaviour. Defining it fully now means later phases add emission sites, not migrations.

```
auth.register · auth.activate · auth.login · auth.login_failed
auth.lockout · auth.logout
account.capability_granted · account.capability_revoked
account.suspended · account.reactivated
case.created · case.opened · case.closed · case.reopened
membership.granted · membership.revoked · membership.lead_transferred
invitation.sent · invitation.accepted · invitation.declined
invitation.revoked · invitation.expired
identity.decided · identity.reversed
annotation.created · annotation.edited · annotation.deleted
assertion.created · assertion.edited · assertion.revoked
restricted.viewed
report.generated · report.exported
```

Phase 0 emits: the six `auth.*`, `account.capability_*`, `case.created`, `case.opened`, `case.closed`, `membership.granted`, `membership.revoked`.

### A7. Assertions table — schema was missing

My omission. Schema:

```sql
investigator_assertions
  id uuid pk
  case_id uuid fk cases not null
  assertion_kind text not null check (assertion_kind in ('relationship','entity'))
  payload jsonb not null                -- edge or entity definition
  basis text not null check (length(btrim(basis)) >= 10)
  author_id uuid fk users not null
  created_at timestamptz not null
  edited_at timestamptz null
  revoked_at timestamptz null
  revoked_by uuid fk users null
  produced_edge_id uuid fk edges null
  produced_entity_id uuid fk entities null
  supersedes_id uuid fk investigator_assertions null
```

Version history is by supersession, not in-place edit: an edit writes a new row with `supersedes_id` pointing at the old one, and the old row gets `revoked_at`. Nothing is deleted. `edited_at` exists for trivial typo fixes that do not change meaning; anything that changes the claim goes through supersession.

The `basis` CHECK is a database-level floor. Pydantic enforces `min_length` as well — both, independently, per the pattern used for `edge_origin`.

### A8. `restricted` flag

**Include in Phase 0's migration.** `entities.restricted boolean not null default false`. No gating UI, no permission check — Phase 5. Reserving the column now means adding the behaviour later is not a schema migration.

### A9. Design tokens sample

§47 is right and Phase 0A is underspecified. Add one deliverable: `web/src/theme/TokenSheet.tsx` — a single static component rendering the four thread types, the three card variants and the palette swatches. Not a page, not routed, not styled beyond the tokens themselves. It exists so the visual language is verifiable before any UI is built on it.

---

## B. Smaller mismatches

| Item | Ruling |
|---|---|
| Seed script path | `tools/seed.py`, invoked `python -m tools.seed`. Correct report §38. |
| Map tile decision | **Phase 4**, when the map is built. Report §34 is right; correct PHASES.md. |
| Demo districts | Two districts (Chennai, Coimbatore), **three stations**. The report's demo narrative says stations; correct anywhere it says districts. |
| Phase 1 edge types | **All three.** `called` and `transferred_to` from structured sources, `mentioned_in` from regex extraction over FIR text. Correct PHASES.md. |

---

## C. The six blocking decisions

### C1. Report filename
See A1. **Rename.**

### C2. Phase plan authority
See A2. **PHASES.md controls; correct §43 and §47 so the conflict disappears.**

### C3. Provenance model
See A3 and A4. **§35's separate table, plus `extraction_method` on the provenance row, plus the `SourceLocator` union. §7 to be rewritten.**

### C4. The word "criminal"

Real conflict, and the resolution is to change the vocabulary rather than weaken the test.

**Rename the source type.** `criminal_records` → `prior_records` throughout: the generator, the source-type enum, the UI label ("Prior records"), and report §41.

Rationale: "criminal records" as a label on a data source in an investigative tool asserts something about the people in it. "Prior records" is accurate, neutral, and is the language that survives a defence lawyer reading the screen. This is the same reasoning that produced the banned-phrase list in the first place, so the list is right and the source name was wrong.

The banned-phrase test then needs no allow-list. Keep it strict.

The problem statement title is external and unchanged — it simply never appears in UI strings.

### C5. Which routes Phase 0 may build

Phase 0 needs enough real surface to prove the spine end to end. Permitted:

```
GET    /api/health
POST   /api/auth/register
POST   /api/auth/activate/{user_id}      requires user:provision
POST   /api/auth/login
POST   /api/auth/logout
GET    /api/auth/me
POST   /api/cases                        requires case:create; writes lead membership
GET    /api/cases                        active memberships only
GET    /api/cases/{case_id}              via get_case_context; audits case.opened
POST   /api/cases/{case_id}/close        LEAD-ONLY — exists to route-test the 403 rung
```

`POST /cases/{case_id}/close` is deliberately included. Without one lead-only route, the 403 rung of the ladder is only tested at service level, and the route-level enforcement path ships untested.

**Membership grant and revoke are service-level functions in Phase 0**, used by `seed.py` and by tests. Their routes and UI are Phase 5. Revocation immediacy is tested by revoking through the service, then issuing an HTTP request and asserting 404.

### C6. `make` on Windows

**Do not require `make`.** Provide both:

```
Makefile                    for parity on Unix
scripts/dev.ps1
scripts/test.ps1
scripts/seed.ps1
scripts/reset.ps1
scripts/lint.ps1
```

Amend the definition of done: "the dev, test, seed and reset scripts run" rather than naming `make`.

Also: use `py -3.11` explicitly on Windows, since bare `python` resolves to 3.10 on this machine. Record the interpreter in `README.md`.

---

## D. Dependencies

**Approved additions for Phase 0** — these are implementation necessities of the locked stack, not new architecture:

```
uvicorn[standard] · psycopg[binary] · pydantic-settings · httpx · argon2-cffi
python-multipart · ruff · mypy · pytest · pytest-asyncio
react-router-dom
```

**Portraits:** generate **SVG**, no Pillow. Composite-sketch style is line art; SVG is the right format, it scales, and it drops a dependency.

**Deferred, do not install yet:** `pandas`, `pdfplumber` (Phase 1); `cytoscape` + `cytoscape-fcose` (Phase 1); `spacy` + `en_core_web_md`, `rapidfuzz`, `jellyfish` (Phase 2); `scikit-learn`, `leaflet`, `react-leaflet`, `leaflet.markercluster`, `recharts` (Phase 4).

**GLiNER — removed entirely.** It requires `torch`, which is banned, and the ban is correct: a multi-gigabyte dependency for a marginal NER benchmark on synthetic data we control is a bad trade on a laptop. Delete the optional GLiNER step from PHASES.md Phase 2. spaCy `en_core_web_md` plus gazetteers is the extraction path.

---

## E. Specification gaps — filled

### E1. Lockout and rate limits

```
LOGIN_MAX_ATTEMPTS        5
LOGIN_ATTEMPT_WINDOW      15 minutes
LOGIN_LOCKOUT_MINUTES     15
RATE_LIMIT_LOGIN_PER_IP   10 per minute
```

Failure counters in `users.failed_login_count` / `users.locked_until`. IP rate limiting in-process (`core/ratelimit.py`), a simple sliding window in memory. No Redis. Losing the counter on restart is acceptable at prototype scale; the database-backed account lockout is the real control.

### E2. "Sensitive read" defined

**Phase 0:** one audit row when a user enters a case — `case.opened` — not one per entity fetched.

Unbounded read auditing makes `audit_log` the largest table in the database by Phase 4 and makes chain verification slow enough to matter.

**Phase 5:** adds `restricted.viewed`, written on every view of an entity with `restricted = true`, regardless of standing, including for the lead.

### E3. Assertion fields
See A7.

### E4. The twenty vocabulary templates

```python
CLAIM_TEMPLATES = {
  # relationships
  "observed_call":        "{a} called {b} on {date}",
  "observed_transfer":    "{a} transferred {amount} to {b} on {date}",
  "observed_mention":     "{a} and {b} are mentioned in the same record",
  "co_presence":          "Repeated co-presence observed between {a} and {b}",
  "handset_continuity":   "Possible handset continuity between {a} and {b}",
  "shared_address":       "{a} and {b} are recorded at the same address",
  "asserted_relationship":"{author} recorded a relationship between {a} and {b}",

  # identity
  "identity_candidate":   "Possible identity match between {a} and {b}",
  "identity_confirmed":   "{author} confirmed {a} and {b} as the same person",
  "identity_rejected":    "{author} recorded {a} and {b} as separate people",
  "identity_pending":     "Identity match awaiting investigator review",

  # structure
  "structural_role":      "Structural role: {role}",
  "centrality_rank":      "Ranked {rank} by {measure} in this component ({scenario})",
  "component_split":      "Removing {entity} separates the network into {n} components",

  # patterns
  "burst_before":         "Communication burst recorded {hours} hours before {event}",
  "circular_flow":        "Circular transfer observed across {n} accounts over {days} days",
  "threshold_structuring":"Repeated transfers recorded below the reporting threshold",
  "new_connection":       "Relationship first recorded within the last {days} days",

  # absence and uncertainty
  "coverage_gap":         "No {source} data held for {entity} between {from} and {to}",
  "insufficient_evidence":"Available records are insufficient to resolve this question",
}
```

Exactly twenty. Every one describes what is recorded or measured. None describes a person.

### E5. Import rules — corrected

The rule as written in CLAUDE.md is wrong: it forbids the worker from importing processing modules, which it must do. Replace with a layered rule:

```
domain/      imports nothing internal
core/        may import domain
db/          may import domain, core
processing/  ingest · extract · identity · graph · patterns · query
             · report · storage
             may import domain, core, db — not each other
worker/      may import domain, core, db, processing
api/         may import anything
             NOTHING imports api
```

`vocabulary.py` **moves from `core/` to `domain/`** — it is a pure contract with no I/O, and leaving it in `core/` is what created the apparent need for `domain` to import `core`.

Enforced by `tests/structural/test_import_boundaries.py` walking the AST of each module.

---

## F. Dataset rulings

### F1. Structure 6 — vehicle ownership

The five source types genuinely cannot carry it. **Add a sixth source: `vehicle_registry.csv`.**

```
registration_number · owner_name · owner_address · registered_on · vehicle_class
```

Roughly 40 rows. It is a legitimate law-enforcement source type (vehicle records appear in the problem statement) and it is the smallest possible addition that makes structure 6 discoverable. Add to report §41 and to the source-type enum.

### F2. Structure 3 — base rate

The base rate must be **derivable from data, not asserted**. Two additions:

**`towers.csv`** — `tower_id · lat · lon · area_type (residential | commercial | transit)`. Around 25 towers.

**Background traffic.** Generate ~120 filler numbers, not part of any planted structure, producing ordinary call traffic weighted toward commercial and transit towers. The co-presence base rate is then computed from the CDR itself: unique devices per tower per hour.

This also makes the decoy realistic — the taxi driver's high degree comes from genuine background contact, not from a hand-placed set of edges.

### F3. Demo / holdout split

The §41 volumes describe the **demo** set.

The holdout is an independent generation at roughly 40% of demo volume, with its **own** nine planted structures using entirely different entities. It is not a duplicate of demo, and it is not a subset.

Never look at holdout during development. It exists so that the Phase 2 precision and recall figures are honest.

### F4. Graph size

~2,500 nodes is reachable once Event nodes are counted: each call, transaction and incident becomes an Event node, alongside Person, Phone, Account, Vehicle, Location, Organisation, Handset and Document.

With the background traffic from F2 added, the count lands in range naturally. Treat ~2,500 as an expectation, not a target — do not pad the dataset to hit a number.

---

## G. Corrections to make before implementation

These are documentation edits, not code. Do them first, in one commit.

- [ ] Rename `docs/AVISE-complete-report.md` → `docs/AVISE-report.md`
- [ ] Report §7 — rewrite provenance per A3 and A4
- [ ] Report §41 — rename `criminal_records` → `prior_records`; add `vehicle_registry`; add `towers` and background traffic; clarify two districts / three stations
- [ ] Report §43 — rewrite to the eight-phase structure
- [ ] Report §47 — align the Phase 0 checklist with PHASES.md
- [ ] Report §38 — seed path `python -m tools.seed`
- [ ] PHASES.md — `pending` → `pending_verification`
- [ ] PHASES.md — map tile decision moves to Phase 4
- [ ] PHASES.md — Phase 1 edge types: `called`, `transferred_to`, `mentioned_in`
- [ ] PHASES.md — delete the optional GLiNER step from Phase 2
- [ ] PHASES.md Phase 0A — remove `docs/AVISE-report.md` from the create list; add `TokenSheet.tsx`
- [ ] CLAUDE.md — replace the import rule with the layered rule in E5
- [ ] CLAUDE.md — note that `vocabulary.py` lives in `domain/`
- [ ] CLAUDE.md — definition of done references the scripts, not `make`

Commit message: `docs: reconcile specification contradictions found in Phase 0 review`

---

## H. Unchanged and non-negotiable

Nothing above alters any of these:

- No silent identity merges. Overlays require a `decision_id`. Underlying entities are never mutated.
- `edge_origin` non-nullable in Pydantic and in PostgreSQL.
- An edge cannot persist without supporting provenance.
- Non-members receive 404, never 403.
- Session payload carries the opaque token and nothing else.
- Session tokens stored as SHA-256 only.
- `/auth/me` returns exactly `id, service_id, full_name, designation, status`.
- `CaseScopedRepository` genuinely filters by `case_id` and raises without one.
- Two standings only: `lead`, `investigator`. No global override.
- Audit is append-only and hash-chained; one global chain with a `case_id` column.
- No cross-case entity linkage.
- Synthetic data only.
- Banned dependency list stands, torch included.
