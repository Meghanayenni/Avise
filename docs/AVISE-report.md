# AVISE
## Complete Project Report

AI-Powered Criminal Network Analysis System
Smart India Hackathon 2026 · Problem Statement 26189

This document consolidates every decision made across product design, user experience, access control, technical architecture, data strategy and delivery. It supersedes all earlier working documents.

---

# CONTENTS

**Part I — Foundations**
1. What AVISE is · 2. The problem · 3. Core principles · 4. The assumption rule

**Part II — Product model**
5. Identity · 6. Analytics under uncertainty · 7. Ontology · 8. Annotation and assertion · 9. Content taxonomy · 10. Findings, leads and gaps · 11. Attention · 12. Language · 13. Analysis capabilities · 14. Feature coverage

**Part III — Experience**
15. Two dashboards · 16. Case workspace · 17. Evidence drawer · 18. Visual language · 19. Interaction patterns

**Part IV — Access and accountability**
20. The access chain · 21. Standing · 22. Accounts and authentication · 23. Membership · 24. Resolution and revocation · 25. Audit

**Part V — Technical architecture**
26. System architecture · 27. Stack · 28. Frontend · 29. Backend · 30. Database · 31. Ingestion · 32. AI/NLP/ML · 33. Graph · 34. Map · 35. Provenance · 36. Security · 37. Responsible AI enforcement · 38. Local development · 39. What not to build

**Part VI — Data**
40. Data strategy · 41. Synthetic dataset · 42. Planted structures

**Part VII — Delivery**
43. Phases · 44. Demo · 45. Judging · 46. Risks · 47. Phase 0 checklist · 48. Decision log

---

# PART I — FOUNDATIONS

## 1. What AVISE is

A case-centric investigation workspace that turns fragmented evidence into an explainable network, and asks the investigator to resolve what it cannot resolve on its own.

Its defining behaviour is not that it finds connections. Many systems find connections. AVISE separates four things and never collapses them:

```
OBSERVED            present in a source record
INFERRED            derived by a stated rule from multiple observations
ASSERTED            a human placed it, from knowledge outside the data
UNKNOWN             nobody knows, and the system says so
```

The investigator is the decision-maker at every point that matters. AVISE supplies evidence, reasoning and questions. It does not conclude.

## 2. The problem

Law enforcement collects large volumes of data — FIRs, call detail records, financial transactions, surveillance notes, criminal history. Despite holding this information, investigators struggle to identify hidden relationships, because the data is fragmented across systems, largely unstructured, and recorded inconsistently. The same person appears under different spellings in different documents. Manual analysis is slow and misses connections.

The task is to uncover hidden networks, identify influential individuals, detect suspicious patterns, and produce actionable intelligence — without turning uncertain evidence into false conclusions about people.

That final clause is where most systems in this category fail, and it is where AVISE is designed to be different.

## 3. Core principles

These are architectural constraints, enforced in schema and build, not disclaimers on a slide.

**1. The system never issues verdicts.** It produces leads with evidence, never conclusions about guilt.

**2. Every claim is evidence-linked** to a source document and character span.

**3. Low confidence abstains.** An uncertain identity match goes to a human. It does not silently happen.

**4. Observation, inference and assertion are structurally distinct** in the schema, the API and the interface.

**5. The graph is a projection, not the source of truth.** Everything is rebuildable from documents plus provenance, which makes every conclusion reversible and every claim defensible.

**6. Absence of evidence is stated, not implied.** The system reports what it does not know.

## 4. The assumption rule

> An assumption may shape what the investigator **sees**. It may never shape what the system **asserts**.

**The visual layer may include assumptions**, marked as such. The graph shows a possible identity match from the moment it is detected, so a hidden bridge between two clusters is visible immediately rather than buried in a queue. The discovery happens.

**The assertion layer may not.** Centrality figures, structural roles, findings and reports compute on confirmed identities only. Where an assumption would change a conclusion, the system states it conditionally:

> *"If these two are the same person, this becomes the highest-betweenness entity in the case."*

This is how AVISE satisfies "uncover hidden networks" and "never assume" at the same time.

---

# PART II — PRODUCT MODEL

## 5. Identity

The hardest problem in the project, and the one most systems get wrong by making it invisible.

### Three states, not two

| State | Meaning | Graph rendering |
|---|---|---|
| Distinct | No hypothesis, or hypothesis rejected | Two nodes, no connector |
| Hypothesised | System proposes a link; awaiting a decision | Two nodes joined by an identity-question connector, unlike any relationship edge |
| Confirmed | Investigator confirmed same person | One merged node, both source identities listed in its detail view |

### What may cluster automatically

Only exact matches on structurally unambiguous identifiers: identical normalised phone number, account number, vehicle registration, IMEI. These are not inferences about people — they are the same string appearing twice.

**Nothing about a person is ever clustered automatically.** Name similarity, shared address, shared district, overlapping associates: none of these create or extend a person entity. They create hypotheses.

### Lifecycle

```
                    ┌─────────────┐
   system detects → │  PROPOSED   │
                    └──────┬──────┘
         ┌─────────────────┼─────────────────┬──────────────┐
         ▼                 ▼                 ▼              ▼
   ┌───────────┐    ┌────────────┐   ┌──────────────┐  ┌─────────┐
   │ CONFIRMED │    │  REJECTED  │   │NEEDS_EVIDENCE│  │ DEFERRED│
   └─────┬─────┘    └────────────┘   └──────┬───────┘  └─────────┘
         │                                  │
         │                                  ▼
         │                        generates a lead naming what
         │                        evidence would resolve it
         ▼
   graph re-derives; affected findings recomputed and flagged
```

`REJECTED` is a positive finding, not a dismissal. It carries its own evidence, prevents re-proposal, and appears in reports as an investigator decision. Most systems treat rejection as deleting a suggestion, which loses the fact that a human looked and said no.

`NEEDS_EVIDENCE` is distinct from `DEFERRED`. Deferred means not now. Needs-evidence means answerable, but not from what is held — and it produces a concrete lead.

### Merging is a view, never a data change

A confirmed merge writes an overlay record. The underlying entities and all their mentions remain intact and separate in the database permanently. Reversing a decision deletes an overlay row and recomputes.

This is what makes being wrong cheap, and it is the direct answer to "what if D. Rao and Deepak Rao are actually different people?"

### Decision records

```
identity_decisions
  id · hypothesis_id · from_state · to_state
  decided_by · decided_at
  evidence_snapshot     exact for/against evidence shown at decision time
  rationale_text        investigator's own note
  superseded_by         set when a later decision reverses this one
```

`evidence_snapshot` matters. When someone asks six months later why a merge was approved, the answer must be the evidence as it stood then, not as it stands now.

### The review card

```
POSSIBLE IDENTITY MATCH                        Open question · 1 of 7

  Entity P-0041                  Entity P-0088
  3 mentions · 2 documents       1 mention · 1 document
  FIR/2026/CBE/0412              SURV-0033

  SUPPORTING
  ✓ Name similarity 0.94                        [see comparison]
  ✓ Shared phone 98400-xxxxx (exact)            [CDR-0231, FIR-0412]
  ✓ Same district                               [2 sources]

  CONTRADICTING
  ✗ Recorded dates of birth differ by 4 years   [CR-0117, FIR-0412]
  ✗ No shared associates in current graph

  NOT KNOWN
  ? No photograph available for either entity
  ? No transaction records for P-0088

  IF CONFIRMED
  These entities sit in separate components. Confirming would
  connect them, joining 22 and 25 nodes.

  [Confirm same person]  [Keep separate]  [Need more evidence]  [Defer]
```

Contradicting evidence gets equal visual weight — same size, same position, never collapsed behind "show more." The NOT KNOWN block prevents absence being read as contradiction. The IF CONFIRMED block tells the investigator why this question is worth their time.

## 6. Analytics under identity uncertainty

Betweenness changes depending on which merges are confirmed. So "who is the broker" has no single answer while hypotheses are open. Most systems ignore this. AVISE makes it explicit.

### Scenarios

| Scenario | Includes | Use |
|---|---|---|
| `confirmed` | Confirmed merges only | Default. What is actually known. |
| `hypothetical` | Confirmed plus all open hypotheses | What if every question resolved as proposed |
| `single` | Confirmed plus one hypothesis | Impact preview for one decision |

Never show a centrality figure without stating its scenario.

### Resolution prioritisation

For each open hypothesis, compute the structural delta between `confirmed` and `single`: does confirming merge two components, how much does the largest component grow, how far does the entity move in betweenness ranking.

**Rank the question queue by structural impact, not by confidence or arrival order.**

> *"7 identity questions are open. Resolving this one would have the largest effect: the two entities currently sit in separate components, and confirming would make the merged entity the highest-betweenness node in the case."*

This is genuinely useful to an investigator, cheap to compute at case scale, and turns human-in-the-loop from a tax into a feature.

## 7. Ontology

The contract everything hangs off. Locked in Phase 0 before any code.

```
Node types    Person · Phone · Account · Vehicle · Location ·
              Organisation · Event · Document · Handset · Photo

Edge classes  RELATIONSHIP   link between entities
              IDENTITY       hypothesis or confirmed sameness

On the edge — interpretation: what the system concluded
  edge_origin                non-nullable
  confidence                 float [0,1]
  confidence_basis           list of contributing reasons
  first_seen_ts · last_seen_ts
  alternative_explanations[]
  inference_rule_id          set for system_inferred, else null
  base_rate_context          nullable

On edge_provenance — attribution: where it came from
  edge_id
  document_id · record_id · mention_id    nullable as appropriate
  locator                    SourceLocator (below)
  role                       supporting | contradicting
  extraction_method
  created_at
```

An edge may have many provenance rows. It cannot persist without at least one supporting row.

**Supporting and contradicting records are derived, not stored.** `supporting_record_ids[]` and `contradicting_record_ids[]` are views over `edge_provenance` filtered by `role`. Storing them as columns would create a second source of truth for the same fact.

**`extraction_method` lives on the provenance row, not the edge.** One edge may be supported by a regex match and a spaCy match; each carries its own method.

### Source locator

Character offsets are meaningful for narrative text and meaningless for a CDR or transaction row. Provenance therefore points at its source through a discriminated union:

```
SourceLocator =
  text_span      document_id · char_start · char_end    FIR narratives, surveillance notes
  record_field   record_id · field_name                 one field of a tabular record
  record_row     record_id                              a whole tabular record
```

Stored as `locator_kind` plus nullable `char_start`, `char_end`, `field_name`, with a CHECK constraint enforcing the correct fields per kind. The same locator applies to `mentions` and to `edge_provenance`. "Open the source" highlights the span for `text_span`, and the row or field for the other two.

### Three origins

```
edge_origin ∈ { system_observed, system_inferred, investigator_asserted }
```

`system_observed` — present in a source record.
`system_inferred` — derived by a rule from multiple observations.
`investigator_asserted` — a human placed it, from knowledge outside the data.

The third is not a note. It enters the graph and it enters analytics, because an investigator's knowledge is evidence. It simply has different provenance.

### Field notes

`alternative_explanations[]` is populated by the rule that produced the edge, not typed per instance. The co-presence rule always attaches *"may share a workplace, residence, or transit route."* This makes the requirement structural rather than something someone remembers to write.

`base_rate_context` records why an inference is non-trivial — for co-presence, the tower's background traffic. Six co-locations at a railway station means nothing; at a residential tower it means something. Without this field, the reasoning is not auditable.

`role = contradicting` on provenance exists because evidence against must be displayed. If it is not in the schema, it will not be shown.

## 8. Annotation and assertion

Investigators work on the whole board, not only the network section. Everything on the case dashboard is annotatable: nodes, edges, timeline events, map pins, photos, documents, findings, and the board itself.

Three author-created object types, deliberately separate:

### Annotation

Free text attached to any object, or free-standing on the board.

```
annotations
  id · case_id · target_type · target_id (nullable)
  body · author · created_at · edited_at · pinned
```

Never affects analytics. A note about a node does not change the graph.

### Asserted relationship

A relationship the investigator knows from outside the data — *"the complainant told me these two are brothers."*

Created by drawing a thread between two items on the board, which is the gesture the corkboard metaphor already implies. Enters the graph with `edge_origin = investigator_asserted`.

### Asserted entity

A person, phone or vehicle that exists in no document but came up in an interview. Same origin.

### Assertion schema

```
investigator_assertions
  id · case_id
  assertion_kind      relationship | entity
  payload             edge or entity definition
  basis               not null, at least 10 non-blank characters
  author_id · created_at · edited_at
  revoked_at · revoked_by
  produced_edge_id · produced_entity_id    nullable
  supersedes_id       previous version, nullable
```

Versions are kept by supersession: an edit that changes the claim writes a new row pointing at the old one, and the old row is revoked. Nothing is deleted. `edited_at` covers typo fixes that do not change meaning. The basis floor is enforced independently in the database CHECK and in the Pydantic model.

### The symmetry rule

**Every assertion requires a stated basis.** Not optional. Free text: *"witness statement of complainant, 14 Mar."*

The system must say how it knows. So must the investigator. Without this, investigator-added content becomes the one place in AVISE where claims appear without provenance — which is exactly the gap a defence lawyer would look for.

### Handling

- Asserted edges count as observed for analytics. A human is accountable for them, which makes them stronger than inference.
- They render in the human warm tone, solid. Not dashed — dashed is reserved for inference.
- Fully editable and deletable by their author, revocable by the lead, every version logged.
- Reports section them separately from observed and inferred.

### Pinning

Any object can be pinned to a curated working set within the case. This is what makes the board a board rather than a report — the investigator assembles their own view instead of staring at the whole graph.

## 9. Content taxonomy

Enforced in the schema, not by convention:

```
origin ∈ {
  observation       present in source data
  rule_finding      deterministic rule fired
  model_inference   statistical or ML derived
  suggestion        proposed next investigative step
  human_note        written by an investigator
  human_assertion   a claim an investigator placed into the graph
  decision          an investigator's recorded decision
}
```

Each gets its own card treatment, icon and placement. The last three are the only ones an investigator authors. `suggestion` is the only one phrased as a question. Filtering by origin is available wherever content appears.

## 10. Findings, leads and evidence gaps

### Findings and leads are different objects

```
findings                         leads
  what was found                   what question is open
  origin                           what evidence would answer it
  supporting[] contradicting[]     which sources to consult
  limitations[]                    why it matters now
  alternative_explanations[]       source: identity | gap | pattern
  confidence + basis               priority (structural impact)
  derived_from[]                   status: open | actioned | closed
  status: active | dismissed       linked_finding_id (nullable)
```

Findings may spawn leads. Not every lead comes from a finding — evidence gaps produce leads with no finding behind them.

Leads are always phrased as questions or suggestions. A lead reading as a statement is a bug.

**Finding format:**

> **Repeated co-presence between Entity A and Entity B**
> Evidence: 6 co-location events, same tower, within 15-minute windows
> Status: INFERRED
> Limitation: no direct communication observed between them
> Alternative explanation: both may regularly visit this location
> Base rate: this tower averages 11 unique devices per hour
> Suggested next step: review CCTV or vehicle records for the identified windows

### Evidence gaps must be computed

Saying "no transaction data for E-0044 between March and June" requires knowing what was supposed to exist. Otherwise it is decoration.

```
case_data_coverage
  case_id · source_type · subject_entity_id (nullable)
  period_from · period_to
  status ∈ {requested, received, partial, unavailable, not_requested}
  requested_at · received_at · note
```

Gaps become derivable: any period where an entity is active in one source and coverage shows `not_requested` or `unavailable` in another relevant source.

*"Transaction records were never requested"* is a different and far more actionable statement than *"no transaction records found."*

## 11. Attention

Replaces alerts and priority indicators. Flagging "high-priority entities" recreates a risk score with different wording.

**Priority attaches to questions, not to people.**

```
7 identity questions open       ranked by structural impact
3 findings unreviewed
2 evidence gaps
1 deferred question with new bearing evidence
```

This tells the investigator what needs their attention without the system implying anything about a person.

## 12. Language

The most important safeguard in the product is linguistic, and language requirements decay unless they are testable.

All system-generated user-facing text comes from one vocabulary module. No free-text string literals for claims anywhere in the codebase.

The module is `avise/domain/vocabulary.py` — a pure contract with no I/O. The first twenty templates:

```
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

Every template describes what is recorded or measured. None describes a person.

Plus a test that fails the build:

```
BANNED = ["criminal", "predicts", "definitely", "proves", "guilty",
          "dangerous", "risk score", "AI detected", "confirmed suspect",
          "certainly", "must be"]
```

| Not this | This |
|---|---|
| Criminal network detected | Connected component of interest |
| Key criminal identified | Highest-betweenness entity in this component |
| Suspicious person | Entity matching pattern: circular fund flow |
| Risk score 0.87 | Structural role: broker (betweenness 0.41, bridges 2 communities) |
| AI predicts | Inferred from 6 co-locations; no communication link observed |

Two hours of work, and the responsible-AI position becomes a property of the build.

## 13. Analysis capabilities

### Network analytics

Degree, betweenness and closeness centrality; Louvain community detection; shortest and k-shortest paths; articulation points; bridges. All NetworkX, all sub-second at case scale.

### Structural role classification

Instead of an importance score, interpretable roles derived from measurable signatures:

| Role | Signature |
|---|---|
| Broker | High betweenness, low degree, bridges two communities |
| Hub | High degree, high clustering, low betweenness |
| Mule | High transaction in-degree and out-degree, short holding time, low centrality elsewhere |
| Peripheral | Low everything, connected to a hub |
| Isolated leader | Low degree, high eigenvector centrality within one community |

Each role shows its metric values and thresholds on demand. "Broker between two cells" is actionable. "Risk 0.87" is not, and is indefensible.

### Network fragility simulation

Remove an entity, recompute components, largest-component size and average path length, report the disruption. Rank all candidates by impact.

Converts analysis into an operational question: not who is important, but what happens if we act. Visually dramatic, computationally trivial, instantly comprehensible to a non-technical judge.

### Pattern rules

Deterministic, named, each with a stated basis and an evidence list:

- **Burner handset continuity** — contact-set Jaccard similarity across a temporal handoff, boosted by shared IMEI and shared tower footprint
- **Co-presence without communication** — tower co-location windows, corrected for the tower's background traffic
- **Circular fund flow** — cycle detection on the directed transaction subgraph
- **Structuring** — repeated amounts below a reporting threshold
- **Communication burst before an incident** — windowed call-rate spike preceding a recorded event time
- **Newly formed connection** — first appearance of a relationship within a recent window

### Anomaly scoring

IsolationForest over per-entity behavioural features. Strictly secondary to rules, and it must always report which features drove the score. An unexplainable outlier flag is unusable here.

### Preprocessing

Deduplicating *records* is preprocessing — the same CDR row imported twice is one row, removed deterministically on a content hash.

Deduplicating *people* is the identity hypothesis system and never happens automatically.

These sound alike and are opposites. Keeping them separate mentally is important while building.

## 14. Feature coverage

| Requirement | Where |
|---|---|
| Case file management | §15, §16, Part IV |
| Multi-source integration | §31, §41 |
| Entity extraction | §32 |
| Relationship extraction | §7, §32 |
| Interactive network graph | §16, §18, §33 |
| Click-to-inspect nodes | §17 — hover preview, click opens drawer |
| Click-to-inspect relationships | §17 |
| Board annotation, investigator edits | §8 |
| Edit history and logs | §25, visible as workspace section 08 |
| Timeline | §16 section 02, vertical |
| Case assistant | §32 — constrained query layer |
| Natural-language queries | §32 |
| Evidence-linked insights | §7, §17, §35 |
| Key individual detection | §13, within case only |
| Community detection | §13 |
| Suspicious pattern detection | §13 |
| Investigation suggestions | §10 leads |
| Search and entity lookup | §16 section 07, §30 |
| Network analytics | §13 |
| Preprocessing and normalisation | §13, §31 |
| Investigation dashboard | §16 |
| Attention indicators | §11 |
| Secure environment | Part IV, §36 |
| Human-in-the-loop | §4, §5, §8 |

**Deliberately excluded — cross-case entity linkage.** Identifying entities recurring across multiple cases requires linking people across case boundaries without a legal basis: the exact failure mode this system exists to prevent. Within a case, key-individual detection is complete. Have the answer ready rather than the feature.

**Deliberately excluded — social media intelligence.** Weakest data source, an entire additional pipeline, and the hardest to defend on provenance. Listed as a future connector.

---

# PART III — EXPERIENCE

## 15. Two dashboards

### Personal dashboard

The only screen outside a case.

```
GET /me/cases           active memberships, standing per case
GET /me/invitations     pending, accept or decline inline
GET /me/questions       open identity questions across all their cases
GET /me/activity        recent activity on cases they belong to
```

No cross-case search, no global entity lookup, no way to discover a case exists. The query is `WHERE user_id = :me AND revoked_at IS NULL`, nothing more.

The last three endpoints stop this being a list of links everyone bookmarks past. Surfacing open questions across cases is the system's voice reaching the investigator wherever they are.

### Case workspace

Selecting a case enters its workspace. Everything from there is scoped to that case. A case switcher sits in the header so someone on five cases moves between them without going home.

**The hazard in a multi-case tool is writing into the wrong case.** The case number stays permanently visible in the chrome and each case carries a subtle persistent accent, so switching is unmistakable.

## 16. Case workspace

```
CASE HEADER                sticky · case number always visible
  title · status · team · open questions (7) · gaps (3) · case switcher
     ↓
01  NETWORK               filtered subgraph ~40 nodes → focus mode
02  TIMELINE              vertical, recent 30 events → focus mode
03  MAP                   real map, clustered pins → focus mode
04  EVIDENCE BOARD        photos, documents, notes, pinned items
05  FINDINGS              explainable findings feed
06  LEADS & GAPS          open questions, evidence gaps, next steps
07  ENTITIES              typed, searchable entity index
08  ACTIVITY              case audit trail
```

**Summary-first, focus-on-demand.** Each heavy section renders a legible summary in the scroll. Full interaction happens in a focus mode taking the viewport. Scrolling is for orientation; focus mode is for work. Focus modes are routes, not modal state, so they are linkable and survive a refresh.

**Lazy mounting.** Heavy components mount on scroll-into-view and unmount when far out of view. This is a requirement, not an optimisation — otherwise Cytoscape, Leaflet and the timeline all initialise at once and the workspace stutters on a student laptop.

**Numbered side rail with live counts.** `05 Findings · 12`, `06 Questions · 7`. Navigation and status in one control, solving the orientation problem inherent in a long scroll.

**Section data loads independently.** Each section has its own endpoint and query key, so the workspace renders progressively and one failure does not blank the page.

### Timeline

Vertical, scrollable, grouped by date. Each event is clickable and opens the evidence drawer. Filters by person, phone, vehicle, account, event type, date range, source.

```
2026-03-14
│
├── 09:32  Phone call          9840012345 → 9003187654    CDR-0231
├── 11:15  Vehicle observed    TN 09 BX 1234              SURV-0019
├── 14:40  Transaction         ₹48,000  A/C 4471 → 8802   TXN-0455
└── 18:10  FIR incident        Theft, Poonamallee         FIR/2026/CHN/0188
      ↓
2026-03-15
│
├── 08:20  Number went dormant 9840012345                 derived
└── 15:20  New number active   9003187654                 derived
```

### Map

Leaflet with real geographic positioning, zoom and pan. Incident pins, tower locations, address markers, pinned photos and notes, marker clustering, layer toggles per entity type. Clicking a pin opens the evidence drawer, same as everything else.

### Graph

Default view is a filtered subgraph of roughly 40 nodes. Filters by entity type, evidence type, date, confidence, observed/inferred. Expand-neighbours, collapse, focus-on-entity, path-between-two-entities. Full canvas is a focus mode. Never render everything — a hairball communicates nothing and is the most common failure of projects in this category.

## 17. The evidence drawer

Every "why?" affordance anywhere in the application — graph edge, timeline event, map pin, finding, note, photo, identity question — opens the same right-side drawer, one contract:

```
EvidenceDrawer {
  subject       { type, id, label }
  claim         controlled vocabulary
  origin        observed | inferred | asserted
  supporting    EvidenceRef[]   each carries a SourceLocator (§7)
  contradicting EvidenceRef[]
  unknown       string[]        what would help but is absent
  alternatives  string[]
  derivation    DerivationStep[]
  confidence    { band, basis[] }
  actions       Action[]
}
```

Served by one polymorphic endpoint:

```
GET /case/:id/evidence/:subjectType/:subjectId
```

**This is the highest-leverage frontend decision in the project.** Six bespoke detail panels is how explainability decays into three good ones and three that print a percentage.

Hover gives a light preview — name, type, degree. Click opens the drawer. Popups cannot hold an evidence chain and are dismissed by stray clicks.

Example content:

```
WHY ARE THESE CONNECTED?

  Entity P-0041  ——  possible co-presence  ——  Entity P-0092

  STATUS      Inferred
  RULE        co_presence_without_communication

  SUPPORTING
  6 co-locations, same tower, within 15-minute windows
    14 Mar 18:22   Tower CBE-0114        CDR-0231, CDR-0233
    19 Mar 19:05   Tower CBE-0114        CDR-0277, CDR-0281
    ... 4 more

  CONTRADICTING
  No direct communication between these entities in held data

  BASE RATE
  Tower CBE-0114 averages 11 unique devices per hour.
  Six repeated co-locations are unlikely by chance here.

  ALTERNATIVE EXPLANATIONS
  Shared workplace · shared residence · common transit route

  CONFIDENCE   Moderate — repeated, low-traffic tower,
               but no corroborating source

  [Open source records]  [Dismiss this inference]  [Create lead]
```

## 18. Visual language

Derived from the corkboard reference, with meaning made explicit rather than decorative.

### Threads

Nobody strings red yarn for things they already know. Red is for theories.

| Thread | Meaning |
|---|---|
| Quiet steel, solid | Observed |
| Red, dashed | Inferred |
| Red, double-dashed, `?` marker | Identity question |
| Warm, solid | Investigator-asserted |

**Red appears nowhere else in the application.** No error states, no alerts, no priority flags.

### Colour

| Token | Value | Meaning |
|---|---|---|
| Surface | `#14161A` | Board |
| Surface raised | `#1C1F24` | Section |
| Card | `#22262C` | Content |
| Text | `#E8EAED` / `#9AA0A8` | Primary / secondary |
| Steel | `#7C8B9A` | Observed, neutral structure |
| Thread red | `#C8443C` | Inference only |
| Amber | `#D9A441` | Awaiting a decision only |
| Warm paper | `#2A2822` / `#B5A97E` | Human-authored only |

Three meaningful colours, three meanings, no overlap. Photographs render grayscale so colour never competes with imagery.

### Cards

| Type | Treatment |
|---|---|
| System finding | Charcoal card, neutral border, mono label |
| Suggested step | Charcoal card, amber left edge, square corners |
| Human note | Warm paper tone, rounded, author and timestamp |

### Typography

One sans for the interface. One mono, used exclusively for record identifiers — `CDR-0231`, `FIR/2026/CBE/0412`, phone numbers, timestamps. Mono signals "this is a record" and aids scanning. No display or handwriting faces.

### Board feeling without pastiche

Elevation, pinning and threading carry the board feeling. Not texture. No wood, cork, tape, torn edges or rotated cards — that is where it tips into detective-movie pastiche.

### Portraits

Composite-sketch style illustrations, as in the reference imagery. Domain-appropriate, unambiguously synthetic, and it avoids placing real faces in a criminal-network demo. A persistent unobtrusive synthetic-data marker sits in the chrome.

## 19. Interaction patterns

A marketing site optimises for a first-time visitor being led through a story. An investigation tool optimises for a returning user navigating to something. Take the wayfinding, leave the persuasion.

**Adopt:** numbered section index with a persistent side rail; progressive disclosure on cards (title and one line, detail on interaction); discrete labelled timeline stages with date anchor, title, short description, expand for detail; tabbed slicing of one dataset; numbering as a wayfinding device, which also echoes the numbered evidence markers in the reference imagery.

**Reject:** countdown timers and manufactured urgency; oversized decorative typography; scroll-triggered reveal animations, which insert delay between scrolling to something and being able to read it; full-page scroll snapping, which fights anyone comparing two sections; any animation near the graph or map, where it actively costs comprehension.

---

# PART IV — ACCESS AND ACCOUNTABILITY

## 20. The access chain

```
ACCOUNT        Who this person is. Provisioned, not self-created.
   │           Holds identity plus a few account-level capabilities.
   ▼
SESSION        Proof they are that person right now. Revocable.
   │           Carries no information about cases.
   ▼
CASE           A container with a case number, a lead and a status.
   │
   ▼
MEMBERSHIP     A grant: this account, on this case, issued by the
   │           lead, revocable. This is "the team."
   ▼
STANDING       lead · investigator. Nothing else.
```

**Two gates.** Membership decides whether a person reaches a case at all. Standing decides only who manages the case, not what data they see.

### Three rules

**The credential identifies the person and nothing else.** No case list, no standing, no permissions in the session. Membership is re-resolved from the database on every request. One indexed query, and revocation takes effect on the very next request.

**The group working a case is the membership list.** No separate team object. "Investigation team" is a label in the case header rendered from `case_members`. One table answers every access question, which is also exactly what the audit trail needs.

**Access is all-or-nothing within a case.** Every member sees the complete workspace. No per-feature, per-source or per-entity gating between teammates. The boundary that matters is between cases, and it is absolute.

## 21. Standing

| Action | Investigator | Lead |
|---|---|---|
| All case content, all features | ✓ | ✓ |
| Add notes, upload evidence, assert relationships | ✓ | ✓ |
| Make identity decisions | ✓ | ✓ |
| Reverse own decision | ✓ | ✓ |
| Reverse another member's decision | — | ✓ |
| Invite and remove members | — | ✓ |
| Transfer lead | — | ✓ |
| Close and reopen the case | — | ✓ |

Four extra powers on one person, not a permission system. The lead is a participating investigator who additionally manages the case.

**Why no analyst, observer or supervisor role.** An investigation team shares the case file — that is what a case file is. Splitting it so one member sees only financial records and another only communications creates friction, gets worked around informally within a week, and reproduces inside the product the exact fragmentation the product exists to solve. The oversight a supervisor role would have provided comes instead from the lead's reversal power and a visible audit trail.

**Consequence to respect:** the audit log is the only control operating inside a case. It must be a first-class section of the workspace, not a settings page.

### Account capabilities

Separate from case standing. Provisioned by an administrator, never self-selected.

```
case:create          may open new cases
audit:read_global    auditor — reads the audit stream, no case content
user:provision       may create, activate and deactivate accounts
```

An auditor is never a case member. They see that a named user opened a named entity in a named case at a timestamp; they do not see who that entity is. This is why "every member has full access" and "auditors exist" do not conflict.

Designation (SI, ASI, Inspector) is descriptive text and confers nothing.

## 22. Accounts and authentication

### Account creation

Accounts are provisioned, not opened by the public. The prototype equivalent with the same guarantee:

1. The person registers with service ID, full name, designation, official email, password.
2. The account is created with `status = pending_verification`.
3. A pending account can sign in and see one screen: its own status. No cases, no search, no data, and it cannot be invited onto a case.
4. An account holder with `user:provision` activates it.

Role is never self-declared. Designation is descriptive; account capabilities are provisioned; standing comes with each grant.

### Authentication

Server-side sessions in an httpOnly cookie, not a JWT in localStorage.

| Property | Value |
|---|---|
| Storage | `sessions` table, one row per active session |
| Transport | httpOnly, Secure, SameSite=Lax |
| Lifetime | 8 hours, sliding renewal |
| Revocation | Immediate |
| Hashing | Argon2id |
| Login protection | Rate limiting, generic failure messages, lockout |

**Revocation is why.** You asked what happens when an investigator is removed. With server-side sessions and no membership in the credential, their very next request is denied. Nothing is cached, nothing has to expire. A JWT carrying case claims would keep working until it expired.

**Generic failure messages** matter more than they look: if wrong-password and no-such-account differ, the login form becomes an account enumeration tool.

TOTP two-factor is a small optional addition.

## 23. Membership

### Opening a case

An account with `case:create` opens a case and becomes lead. That membership row is written in the same transaction as the case, so a case never exists without a lead.

### Joining a case

**Invitation.** The lead names a specific account by service ID or name. The invitation names that account, expires after seven days, and can be revoked before acceptance. The invitee accepts from their personal dashboard, which creates the membership. Declines are recorded.

Acceptance makes the grant two-sided and recorded from both ends.

**Request to join (optional).** Case numbers appear on paperwork and in briefings, so they are not secret. An investigator who learns of one may request access with a stated reason. The lead approves or denies. Knowing a case number lets a person ask; it never lets them in.

### Why not join codes

A code is a bearer credential, and the objections are structural rather than about entropy:

| Problem | Consequence |
|---|---|
| Held by many people | Cannot revoke one person without breaking everyone |
| Trivially forwardable | Ends up in messaging apps and on whiteboards |
| Inverts authority | Access is claimed by the holder, not granted by someone accountable |
| Weak audit | "Joined via code" does not record who authorised this person |

Making the code longer fixes none of these. Invitations naming a specific account are strictly better on every axis.

## 24. Resolution and revocation

```
1. Valid session?                     no → 401
2. Account active?                    no → 401
3. Active membership on this case?    no → 404
4. Lead-only action, and not lead?    no → 403
5. Audit row written
```

**Step 3 returns 404, not 403.** A 403 confirms the case exists, and existence is itself sensitive for criminal cases. Someone probing case numbers must learn nothing from the response.

Enforcement in two layers: a route dependency that resolves membership and rejects at the boundary, and a data layer where every query is scoped by `case_id` by construction.

**Revocation.** The lead sets `revoked_at` with a reason; an audit row records who and why. The row is never deleted. The next request against that case returns 404.

**Contributions survive.** Notes, identity decisions, assertions and annotations remain in the case, attributed to the person who made them. Removing access must not remove decisions — that would corrupt the investigative record.

**Closure.** A closed case freezes: members keep read access, no new content, no new members, audit continues. Reopening requires the lead and is audited.

## 25. Audit

Append-only, hash-chained. Each row stores the hash of the previous row, so tampering breaks the chain and is detectable. This is tamper-evidence without external infrastructure — and it is the answer when someone asks why you did not use a blockchain.

Recorded with actor, timestamp, case, target and before/after state:

- Sign-in, sign-out, failed sign-in, lockout
- Account creation, activation, suspension, capability change
- Case creation, closure, reopening, lead transfer
- Invitation sent, accepted, declined, revoked, expired
- Membership granted and revoked
- Every identity decision and every reversal
- Every assertion, annotation and edit
- Report generation and export
- Every view of a `restricted` entity, by any member including the lead

The full event enum is defined in Phase 0 (`docs/PHASE-0-DECISIONS.md` A6); later phases add emission sites, not migrations.

**Sensitive reads are bounded.** Entering a case writes one `case.opened` row, not one row per entity fetched. Unbounded read auditing would make `audit_log` the largest table in the database and chain verification slow enough to matter. The exception is `restricted.viewed`, written on every view of a restricted entity.

**Identity decisions matter most.** A merge changes what the system asserts about a person, so who decided, when, and on what evidence is part of the investigative record — not merely a system log.

---

# PART V — TECHNICAL ARCHITECTURE

## 26. System architecture

A modular monolith. One FastAPI process, one React application, one PostgreSQL database, one background worker. No message broker, no second datastore, no microservices.

```
┌───────────────────────────────────────────────────────────────┐
│  React + TypeScript SPA                                       │
│  personal dashboard · case workspace (8 sections)             │
│  graph · timeline · map · board · evidence drawer             │
└──────────────────────────┬────────────────────────────────────┘
                           │  REST / JSON · session cookie
┌──────────────────────────▼────────────────────────────────────┐
│  FastAPI  (single process, modular)                           │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │ auth · membership resolver · audit middleware           │  │
│  └─────────────────────────────────────────────────────────┘  │
│  ┌────────┬─────────┬─────────┬─────────┬────────┬─────────┐  │
│  │ingest  │extract  │identity │graph    │patterns│query    │  │
│  │parsers │regex +  │candidate│NetworkX │rules + │NL →     │  │
│  │per     │gazetteer│gen +    │analytics│Isolatn │structrd │  │
│  │source  │+ spaCy  │scoring  │scenarios│Forest  │query    │  │
│  └────────┴─────────┴─────────┴─────────┴────────┴─────────┘  │
└──────────────────────────┬────────────────────────────────────┘
                           │
        ┌──────────────────▼───────────────────┐
        │ PostgreSQL 16 — single source of truth│
        │ documents · mentions · entities ·     │
        │ edges · provenance · hypotheses ·     │
        │ decisions · annotations · findings ·  │
        │ leads · coverage · users · cases ·    │
        │ members · audit_log · jobs            │
        │ full-text search via tsvector         │
        └──────────────────┬────────────────────┘
                           │
        ┌──────────────────▼───────────────────┐
        │ Local filesystem — uploaded documents │
        │ and images, referenced by path + hash │
        └───────────────────────────────────────┘

        ┌───────────────────────────────────────┐
        │ Background worker (same codebase)     │
        │ polls jobs table: parse, extract,     │
        │ resolve candidates, recompute graph   │
        └───────────────────────────────────────┘

        Optional, never required:
        ┌───────────────────────────────────────┐
        │ LLM — natural-language query          │
        │ translation only. System fully        │
        │ functional without it.                │
        └───────────────────────────────────────┘
```

### Future production architecture

Same components, same contracts, different implementations. Because the contracts were fixed in Phase 0, this is swapping implementations, not rewriting.

| Component | Prototype | Production |
|---|---|---|
| Ingestion | Python workers, file upload | Kafka or Airflow, connectors to CCTNS, bank and telecom feeds |
| Extraction | spaCy + regex on CPU | Fine-tuned domain NER on GPU inference servers, multilingual |
| Identity | rapidfuzz + phonetic keys | Dedicated ER service with active learning from analyst decisions |
| Graph | NetworkX, in-process | Neo4j or TigerGraph cluster with incremental analytics |
| Storage | PostgreSQL, local disk | Encrypted object storage, KMS-managed keys, read replicas |
| Security | Sessions + membership + audit | SSO, MFA, SIEM integration, air-gapped deployment |

## 27. Stack

Laptop feasibility: 🟢 comfortable · 🟡 possible with care · 🟠 difficult locally · 🔴 not recommended

| Layer | Choice | Feasibility | Essential |
|---|---|---|---|
| Language | Python 3.11+ | 🟢 | Yes |
| API | FastAPI + Uvicorn | 🟢 ~200 MB | Yes |
| Validation | Pydantic v2 | 🟢 | Yes |
| ORM | SQLAlchemy 2 + Alembic | 🟢 | Yes |
| Database | PostgreSQL 16 | 🟢 ~500 MB, <2 GB disk | Yes |
| Search | Postgres `tsvector` FTS | 🟢 | Yes |
| Graph | NetworkX | 🟢 ~200 MB at 5k nodes | Yes |
| Structured extraction | `re` + gazetteers | 🟢 | Yes |
| NER | spaCy `en_core_web_md` | 🟢 ~200 MB | Yes |
| Fuzzy matching | rapidfuzz | 🟢 | Yes |
| Phonetic keys | jellyfish | 🟢 | Yes |
| Anomaly detection | scikit-learn IsolationForest | 🟢 ~200 MB | No |
| Geo clustering | scikit-learn DBSCAN | 🟢 | No |
| Tabular | pandas | 🟢 ~500 MB | Yes |
| PDF text | pdfplumber | 🟢 | If PDFs used |
| Password hashing | argon2-cffi | 🟢 | Yes |
| Frontend | React 18 + Vite + TypeScript | 🟢 ~1 GB in dev | Yes |
| Styling | Tailwind | 🟢 | Yes |
| Server state | TanStack Query | 🟢 | Yes |
| UI state | Zustand | 🟢 | Yes |
| Graph canvas | Cytoscape.js | 🟢 | Yes |
| Charts | Recharts | 🟢 | No |
| Map | Leaflet + OSM raster tiles | 🟢 | Yes |
| Testing | pytest | 🟢 | Yes |
| Local Postgres | Docker Compose | 🟡 ~1 GB on Windows | No |
| LLM | Ollama + 4B quantised, or an API | 🟡 4–6 GB / 🟢 | No |

**Footprint without an LLM: roughly 3.5 GB of RAM in development.** An 8 GB laptop runs everything if you skip the local model. 16 GB runs everything including it. No GPU at any point.

## 28. Frontend

**React 18 + Vite + TypeScript.** TypeScript is not optional — the ontology is the contract holding the project together, and types keep the frontend honest against it. Vite because the dev server starts in under a second, which matters when three people iterate on laptops.

**TanStack Query for server state, Zustand for UI state.** Nearly everything on screen is server data. TanStack Query handles caching, refetching and loading states. Zustand holds genuinely local state: selected entity, drawer open, active scenario, applied filters. Redux is unnecessary at this size.

```
/login
/register
/dashboard                       personal
/case/:caseId                    workspace, 8 sections
/case/:caseId/graph              focus mode
/case/:caseId/timeline           focus mode
/case/:caseId/map                focus mode
/case/:caseId/entity/:entityId   entity analysis
/case/:caseId/questions          identity question queue
/case/:caseId/team               membership, lead only
```

Mock JSON fixtures matching the ontology exist from Phase 0, so the frontend never waits on the backend.

## 29. Backend

**Modular monolith, not microservices.**

Microservices solve independent scaling and independent deployment. You have neither problem. What they would cost: network calls between modules, distributed transactions across identity decisions, multiple processes to start before a demo, and debugging across service boundaries. For three people on laptops, each is a direct subtraction from build time.

```
avise/
  api/          routes, request/response schemas
  core/         config, security, session, audit middleware
  domain/       ontology models, controlled vocabulary — the contract
  ingest/       source parsers, normalisation
  extract/      regex, gazetteers, spaCy pipeline
  identity/     candidate generation, scoring, hypothesis lifecycle
  graph/        projection build, analytics, scenarios
  patterns/     rule engine, anomaly scoring
  query/        NL translation, structured query execution
  report/       templated brief generation
  db/           models, migrations, repositories
  worker/       job loop
```

Boundaries are layered:

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

Enforced by a structural test walking each module's imports, not by discipline. If a module later needs extracting, the seams are already correct.

**Background work without a broker.** Ingestion and extraction take seconds to minutes and must not block a request. Celery would require Redis — another service to install, run and explain. Instead: a `jobs` table and a single worker process from the same codebase, polling for queued work and writing progress back to the row. The UI polls the job. Zero extra infrastructure, and you get a visible processing panel for free.

## 30. Database

**PostgreSQL only.** One database serving every requirement.

| Requirement | How Postgres covers it |
|---|---|
| Relational data | Natively |
| Provenance, flexible attributes | JSONB |
| Full-text search | `tsvector` + GIN index |
| Path queries | Recursive CTEs, if ever needed |
| Graph analytics | Not in the database — NetworkX, from a projection |
| Files | Filesystem, with path and SHA-256 in a table |
| Audit integrity | Hash chain in an append-only table |

```
IDENTITY & ACCESS      users · account_capabilities · sessions
                       cases · case_members · case_invitations

SOURCE                 documents · records · case_data_coverage

EXTRACTION             mentions · entities · entity_attributes

GRAPH                  edges · edge_provenance

IDENTITY RESOLUTION    identity_hypotheses · identity_decisions

HUMAN CONTENT          annotations · investigator_assertions

ANALYSIS               findings · leads · analytics_runs

OPERATIONS             jobs · audit_log
```

Every table holding case content carries an indexed `case_id`, and no repository function accepts a query without one. Case isolation is structural rather than filtered.

## 31. Ingestion

**Source adapters behind one interface.** Each source type gets a small module that knows only its own format and emits normalised records.

```
Upload → document row (path, sha256, source_type, uploaded_by)
       → job queued
       → adapter parses → records (typed, normalised, with source locators)
       → records stored, extraction job queued
```

An adapter implements three things: does this file look like my format, parse it into records, describe my record schema. Adding a new source type later means adding one module and registering it. No other code changes.

**Normalisation happens at ingestion.** Phone numbers to canonical form, dates to UTC, currency to integer paise, vehicle registrations to canonical spacing. Unglamorous, and the single biggest determinant of whether the graph is connected or fragmented. Two spellings of one phone number produce two nodes and a hidden connection that stays hidden.

## 32. AI / NLP / ML

The guiding principle: use the cheapest method that produces an explainable result, and reserve statistical methods for where rules genuinely cannot reach.

### Extraction — three tiers

**Tier 1, regex and gazetteers.** 🟢 negligible. Phone numbers, IMEIs, account numbers, IFSC codes, vehicle registrations, dates, currency. These formats are strictly patterned — `TN 09 BX 1234`, IFSC as four letters then zero then six alphanumerics. Precision effectively 100%, and these entities carry most of the network structure. This tier does more real work than the NER model.

**Tier 2, spaCy NER.** `en_core_web_md`, 🟢 ~200 MB, roughly 1000 documents per minute on CPU. PERSON, ORG, GPE, DATE from FIR narratives and surveillance notes.

*Honest limitation:* off-the-shelf English NER has mediocre recall on Indian personal names in police-report prose. This is the weakest link. Mitigations: a gazetteer of common given names and surnames to boost candidates, and the fact that Tier 1 captures the high-value identifiers independently, so NER failure degrades the graph rather than breaking it.

**No third tier.** GLiNER was considered and removed: it requires `torch`, a multi-gigabyte dependency for a marginal NER gain on synthetic data we control. spaCy `en_core_web_md` plus gazetteers is the extraction path.

Not recommended: `en_core_web_trf` (🟠 ~2 GB with torch, slow, marginal gain). Fine-tuning (🔴 no GPU, no corpus).

### Identity resolution

```
1. NORMALISE      case, punctuation, honorifics (Shri, Thiru, S/o),
                  initial expansion, name-order canonicalisation

2. BLOCK          reduce candidate pairs cheaply
                  keys: Double Metaphone of surname · district ·
                        shared exact identifier · first letter + length
                  🟢 jellyfish

3. SCORE          rapidfuzz token_set_ratio and partial_ratio
                  + exact identifier matches (phone, account, IMEI)
                  + contextual features (shared address, shared
                    associates, co-occurring entities, date proximity)
                  + contradicting features (DOB mismatch, incompatible
                    locations at the same time)
                  🟢 negligible cost

4. HYPOTHESISE    every scored pair above a low floor becomes a
                  hypothesis with its feature vector preserved.
                  Nothing merges. Ever.

5. RANK           order the question queue by structural impact
```

**Do not use sentence embeddings for name matching.** Models like MiniLM are trained for sentence semantics, not for `Rajesh Kumar` / `Rajeshkumar` / `R. Kumar` / `RAJESH K`. They are unreliable on transliteration variance, initials and name-order inversion — exactly the variance in this data. String and phonetic methods are better, faster, and fully explainable, which matters because every feature is shown to an investigator as a reason. "0.94 cosine similarity" is not a reason.

**Evaluation harness in Phase 2, not Phase 6.** You generate the data, so you know ground truth. Precision and recall on a holdout split, including the planted name collision that must not be merged. Without negative cases precision is undefined; without the harness you will spend days guessing whether a change helped.

### Natural-language query layer

Replaces an open-ended case copilot. Free-form generated prose about case data is where unsupported claims enter a system like this.

```
1. Investigator types a question
2. Translated into a structured query object over the case graph
   (entity filters, time range, event types, relation types)
3. THE INTERPRETED QUERY IS SHOWN BEFORE IT RUNS,
   in plain language and as editable filter controls
4. Executed deterministically against case-scoped data
5. Results are records with citations, rendered into the
   relevant section — timeline filtered, graph filtered
6. Untranslatable questions are declined plainly, with a
   statement of what the layer can answer
```

*"Show all events where John is present"* becomes a real query returning real records. Nothing is generated prose, so nothing needs fact-checking — the answer **is** the records.

Only the translation step uses a model. Execution is deterministic. If the model is unavailable, the same filters remain usable by hand, so the feature degrades rather than breaks.

| Option | Feasibility | Note |
|---|---|---|
| Ollama + Qwen3 4B or Phi-4-mini, Q4 | 🟡 4–6 GB, 10–20 tok/s CPU | Preserves full offline operation |
| Hosted API | 🟢 locally | Cheap at this volume, breaks the offline story |
| 8B+ local | 🟠 ~8 GB, too slow live | Not worth it |

**The system is fully functional with no LLM at all.** Say this explicitly during the demo — it is a stronger statement than having a chatbot.

## 33. Graph

**NetworkX, in-process, rebuilt from Postgres.** 🟢

```
Postgres (entities, edges, confirmed identity overlays)
        │
        ▼
GraphProjection.build(case_id, scenario)
        │
        ├── cached in the worker, keyed by
        │   (case_id, scenario, data_version)
        ▼
NetworkX MultiDiGraph
        │
        ▼
degree · betweenness · closeness · Louvain communities ·
shortest and k-shortest paths · articulation points ·
bridges · fragility simulation
```

Betweenness centrality is the most expensive routine and runs in well under a second on a 5k-node graph. Rebuild on data change, cache to disk, invalidate on write.

**Why not a graph database.** A case graph is 2–5k nodes. Adding Neo4j means a second datastore to synchronise with the source of truth, a second service to install and start, more RAM, and a synchronisation bug class that does not otherwise exist. The scalability story is better told than built: *"the graph is a projection, so swapping NetworkX for Neo4j at scale changes one module."*

**Visualisation: Cytoscape.js.** Chosen for specific reasons: first-class edge styling, which you need because solid, dashed, double-dashed and warm-solid carry the entire visual language; good layout algorithms (fcose, cola) at this size; compound nodes, which is how a confirmed merge renders; and a straightforward event model for node and edge clicks.

sigma.js is faster above 10,000 nodes but has weaker edge styling — the wrong trade here. react-force-graph is prettier by default and harder to control precisely.

## 34. Map

**Leaflet + OpenStreetMap raster tiles.** 🟢 negligible, no API key.

Chosen over MapLibre because MapLibre needs vector tiles, meaning a tile server or a paid provider. Leaflet with raster tiles does everything AVISE needs: pins, clustering, popups, layers, click handling.

**One honest caveat.** The map is the only component with a live external dependency, which conflicts with the fully-offline demo. Pre-caching tiles for the case bounding box is the fix, but bulk tile downloading is restricted under OpenStreetMap's tile usage policy — check it, and consider generating raster tiles locally from a regional OSM extract instead. Decide this in Phase 4, not on demo day.

## 35. Provenance

Provenance is a schema property, not a display feature. Nothing enters the graph without it.

```
mentions
  id · document_id · record_id
  locator_kind · char_start · char_end · field_name
  surface_text · mention_type · extraction_method · confidence

entities
  id · case_id · entity_type · canonical_form · created_from_mention_id
  restricted boolean not null default false

edges
  id · case_id · source_entity_id · target_entity_id · edge_type
  edge_origin ∈ {system_observed, system_inferred, investigator_asserted}
  confidence · confidence_basis · first_seen_ts · last_seen_ts
  alternative_explanations[] · inference_rule_id · base_rate_context

edge_provenance
  edge_id · document_id · record_id · mention_id
  locator_kind · char_start · char_end · field_name
  role ∈ {supporting, contradicting}
  extraction_method · created_at
```

`locator_kind ∈ {text_span, record_field, record_row}`, with a CHECK constraint enforcing the fields each kind requires (§7).

| Question | Answered by |
|---|---|
| Where did this come from? | `edge_provenance → documents` |
| Which source produced it? | `document.source_type`, `document.sha256` |
| What part of the source supports it? | The source locator — a character span highlighted in narrative text, or the row and field in a tabular record |
| Observed, inferred or asserted? | `edge_origin` |
| What confidence, and why? | `confidence` plus stored feature contributions |
| Who confirmed or rejected it? | `identity_decisions`, with `evidence_snapshot` |

**The locator is what makes this real rather than decorative.** Clicking evidence opens the source with the exact span, row or field highlighted. Storing a locator costs a few columns; retrofitting one costs re-extracting everything.

## 36. Security

| Area | Prototype | Production |
|---|---|---|
| Passwords | argon2id, never logged | Same, plus policy enforcement |
| Sessions | Server-side rows, httpOnly, Secure, SameSite=Lax, 8h sliding | Plus device binding |
| Login | Rate limited, generic failures, lockout | Plus MFA |
| Case isolation | `case_id` in every repository query; 404 for non-members | Plus row-level security |
| Uploads | Extension and magic-byte check, size cap, SHA-256, stored outside the web root, never served by original filename | Plus malware scanning, sandboxed parsing |
| API | Pydantic validation everywhere, CORS locked to the dev origin, no raw SQL | Plus WAF, mTLS between tiers |
| Transport | HTTPS with a local certificate | Managed certificates |
| Audit | Append-only, hash-chained | Plus SIEM export |
| Export | Watermarked with requesting user and timestamp, logged | Plus DLP |
| Secrets | `.env`, never committed | Vault or KMS |

**Restricted entities — schema now, UI later.** Keep a `restricted` boolean on entities for informants, protected witnesses and minors. Do not build the gating UI for the prototype. Source protection is not about distrusting the team; it limits how many people can be compelled to disclose a source. Reserving the column means adding the behaviour later is not a migration.

## 37. Responsible AI enforcement

Enforced in schema and build, not in interface copy.

| Principle | Enforced by |
|---|---|
| No silent merges | No code path writes a person-entity merge without an `identity_decisions` row. Merges are overlays; underlying entities never mutate. |
| Observed vs inferred vs asserted | `edge_origin` is non-nullable. Serialisers cannot omit it. |
| Evidence-linked conclusions | `edge_provenance` required for every edge. An edge without provenance fails validation. |
| Uncertainty preserved | Hypotheses persist in `PROPOSED` indefinitely. No timeout resolves them. |
| Alternative explanations | Attached by the inference rule, not typed per instance. |
| Human confirmation | State transitions require a `decided_by`. |
| Suggestions separate from conclusions | `leads` and `findings` are different tables with different renderers. |
| No verdicts | Controlled vocabulary plus a banned-phrase test that fails the build. |
| Investigator accountability | Assertions require a stated basis — the same standard the system holds itself to. |

### Bias — named, not hidden

Sources of bias worth stating out loud in the pitch:

- **Data collection bias.** Heavier policing in some areas produces more records, which produces higher centrality, which looks like higher importance. On real data the system would amplify this.
- **Name-based bias.** Fuzzy name matching performs unevenly across naming conventions, so resolution errors would not be evenly distributed across communities.
- **Feedback loops.** If investigative attention follows system output, and the system learns from investigative attention, it converges on its own priors.

Prototype mitigations: no learning from analyst behaviour, no demographic attributes anywhere in the model, explicit documentation of these risks. Being able to articulate this clearly is worth more than any mitigation you could build in the time available.

## 38. Local development

```
Prerequisites
  Python 3.11+      🟢
  Node 20+          🟢
  PostgreSQL 16     🟢  via Docker Compose, or native
  Ollama            🟡  optional

One-time
  docker compose up -d db
  py -3.11 -m venv .venv && pip install -r requirements.txt
  python -m spacy download en_core_web_md
  alembic upgrade head
  python -m tools.seed          synthetic data + demo accounts
  cd web && npm install

Running — three terminals
  uvicorn avise.api:app --reload
  python -m avise.worker
  cd web && npm run dev
```

**Docker for Postgres only.** Containerising the Python app adds rebuild friction and Docker Desktop already costs around a gigabyte on Windows. Postgres in a container makes every teammate's database identical, removing a class of "works on my machine" problem.

On Windows, use `py -3.11` explicitly — a bare `python` may resolve to an older interpreter.

**Seed and reset must be one command.** You will run it dozens of times, and on demo day it is your recovery path. `make` is not required: the dev, test, seed, reset and lint tasks exist as `scripts/*.ps1`, with a `Makefile` for parity on Unix.

**Deployment.** For SIH, do not deploy. Run locally and demonstrate offline operation deliberately. If you want a backup, one small VM running the same three processes behind nginx suffices. Kubernetes and managed services are 🔴.

### Optional external components

| Component | Fallback |
|---|---|
| Hosted LLM for query translation | Local model, or manual filter controls |
| Map tiles | Pre-cached tiles for the case bounding box |
| Email for invitations | In-app notification only |
| Hosted deployment | Local |

If any becomes load-bearing, the offline demo stops working — and the offline demo is one of your strongest differentiators.

## 39. What not to build

| | Why |
|---|---|
| Graph database 🔴 | 2–5k nodes. NetworkX is faster to build with and has nothing to synchronise. |
| Vector database 🔴 | Nothing in AVISE needs vector similarity. |
| Elasticsearch 🔴 | A gigabyte of RAM to duplicate Postgres FTS at this corpus size. |
| Celery + Redis 🔴 | A jobs table and one worker do the same with no extra service. |
| Microservices 🔴 | Operational cost for three people, no scaling problem to solve. |
| Kafka / Spark / Airflow 🔴 | No benefit at prototype scale, real failure risk during a demo. |
| S3 / MinIO 🔴 | Local filesystem with hashes is sufficient. |
| GNNs 🔴 | No labels, no GPU, unexplainable output — a liability in a system built on "here is why". |
| Fine-tuned transformers 🔴 | No GPU, no labelled corpus, no time. |
| Face recognition 🔴 | Ethically loaded, adds nothing the graph does not provide. |
| Free-form LLM chatbot over case data 🔴 | The largest single source of unsupported claims in a system like this. |
| Cross-case entity linkage 🔴 | Linking people across cases without a legal basis is the failure mode the product exists to prevent. |
| Social media ingestion 🔴 | Weakest source, entire extra pipeline, hardest to defend on provenance. |
| Real-time streaming 🔴 | Batch is correct for this data and far easier to demonstrate. |
| Blockchain 🔴 | A hash-chained append-only audit table gives the same tamper-evidence at no cost. |
| Predictive crime forecasting 🔴 | Scientifically contested and reputationally dangerous. |
| Kubernetes 🔴 | It is a student prototype on a laptop. |

---

# PART VI — DATA

## 40. Data strategy

**Fully synthetic. No real FIRs, no scraped social media, no real personal data.**

State this to judges proactively rather than waiting to be asked, and frame it as a design decision: synthetic data with known ground truth lets you *measure* accuracy, which real data would not. The constraint becomes an advantage.

Public data is used only for realism scaffolding — Indian district and station names, IFSC prefixes, vehicle registration series codes, cell tower coordinate ranges. Never for entities.

**Photographs.** Composite-sketch style illustrations, procedurally varied. Real faces in a synthetic criminal-network demo are a serious problem regardless of intent — reputational for the subject, and disqualifying if a judge asks where the images came from. Photorealism also encourages viewers to read synthetic data as real, which is the wrong instinct to cultivate. A persistent synthetic-data marker sits in the application chrome.

## 41. Synthetic dataset

**Scenario:** an inter-district narcotics distribution network with hawala-style financing, spanning two districts — Chennai and Coimbatore — and three police stations, over a six-month window.

Chosen because it naturally produces every data type, involves both communication and money, and gives a plausible reason for two apparently unrelated case clusters to share a hidden intermediary.

### Volumes

These volumes describe the **demo** set. The holdout set is generated separately (see Generation).

| Source | Volume | Rationale |
|---|---|---|
| FIRs | 40 documents, 200–600 words | Enough for NER to look real, small enough to hand-check |
| CDR | ~8,000 rows, 30 structure numbers plus ~120 background numbers, 6 months | Enough for burner and co-presence patterns to be statistically visible |
| Towers | ~25 towers | Location and area type, so base rates are computed rather than asserted |
| Transactions | ~1,200 rows, 18 accounts | Enough for cycles and structuring to emerge |
| Surveillance notes | 25 short narratives | The unstructured source where name variants live |
| Prior records | 60 person records | Identity attributes for resolution |
| Vehicle registry | ~40 rows | Registered ownership, so structure 6 is discoverable |
| Total graph | ~2,500 nodes, ~9,000 edges | Comfortable for NetworkX, non-trivial to eyeball |

**Why "prior records".** The source type is `prior_records`, labelled "Prior records". "Criminal records" as a source label asserts something about the people in it; "prior records" is accurate and neutral.

**Background traffic.** The ~120 background numbers belong to no planted structure. They produce ordinary call traffic weighted toward commercial and transit towers. The co-presence base rate is computed from the CDR itself — unique devices per tower per hour — and the decoy's high degree comes from genuine background contact rather than hand-placed edges.

**Graph size.** ~2,500 nodes is reached by counting each call, transaction and incident as an Event node, alongside Person, Phone, Account, Vehicle, Location, Organisation, Handset and Document nodes. It is an expectation, not a target: the dataset is never padded to hit it.

### Schema

```
FIR:            fir_id, station, district, date, sections,
                complainant, narrative_text, incident_datetime,
                incident_lat, incident_lon

CDR:            call_id, caller_msisdn, callee_msisdn, start_ts,
                duration_s, caller_imei, callee_imei,
                tower_id, tower_lat, tower_lon, call_type

Transaction:    txn_id, from_account, to_account, amount, ts,
                channel, from_name, to_name, from_ifsc, to_ifsc

Surveillance:   note_id, officer_id, date, location, narrative_text

PriorRecord:    person_id, name, aliases[], dob, address,
                prior_cases[], known_associates_text

VehicleRegistry: registration_number, owner_name, owner_address,
                registered_on, vehicle_class

Tower:          tower_id, lat, lon,
                area_type ∈ {residential, commercial, transit}
```

### Realism details

Indian phone numbers start 6–9 and are 10 digits. Vehicle registrations follow `TN 09 BX 1234`. IFSC is four letters, a zero, then six alphanumerics. FIR numbers follow a station/year format. Names include realistic transliteration variance — the same person as "Rajesh", "Rajeshkumar", "R. Kumar", "Rajesh K." These details are what make the data credible to an Indian judge.

### Generation

Fixed random seed. Emit both the data files and a `ground_truth.json` listing every planted structure, every true identity mapping, and every intended negative case.

Split into `demo/` (used live, tuned for narrative clarity) and `holdout/` (never examined during development, used only for final evaluation numbers). This gives you an honest answer when a judge asks whether you tuned on your test set.

The holdout is an independent generation at roughly 40% of demo volume, with its own nine planted structures built from entirely different entities. It is neither a duplicate nor a subset of demo.

## 42. Planted structures

These are what AVISE must discover. Written down before generating, so they double as ground truth.

| # | Structure | What it proves |
|---|---|---|
| 1 | **The bridge.** Two clusters connected only through one person, appearing as "Deepak Rao" in an FIR, "D. Rao" in a surveillance note, and "RAO DEEPAK" as an account holder. Linked by a shared phone in two of the three. | Identity resolution and betweenness centrality together |
| 2 | **Burner handoff.** Number A dormant day 84; number B active day 85, same IMEI, 78% contact overlap. | Communication analysis, identity migration |
| 3 | **Co-presence.** Two numbers in the same low-traffic tower within 15 minutes on 6 occasions, never calling each other. | Inference of unrecorded relationships |
| 4 | **Circular flow.** A→B→C→A over 9 days, each leg just under the reporting threshold. | Financial cycle plus structuring detection |
| 5 | **Temporal coordination.** Call bursts from the broker to 4 numbers, 5–7 hours before each of 3 FIR incident times. | Temporal reasoning across sources |
| 6 | **Vehicle link.** One registration in two FIRs from different districts, registered to a third party. | Cross-document structured linking |
| 7 | **The decoy.** A taxi driver with the highest degree in the graph, near-zero betweenness, no financial edges, one-directional contacts. | That the system does not just flag the loudest node |
| 8 | **The benign coincidence.** Two unrelated people sharing an address because they rent from the same landlord. | That co-occurrence alone does not create an association |
| 9 | **The name collision.** Two genuinely different people with the same common name in different districts, who must NOT be merged. | Resolution precision, not just recall |

**Structures 7, 8 and 9 are the ones most teams skip, and they are what make your evaluation numbers meaningful.** Without negative cases, precision is undefined. Structure 9 in particular is the direct test of the "what if they really are different people?" worry.

---

# PART VII — DELIVERY

## 43. Phases

Eight phases. The detailed roadmap — build lists, tests and verification per phase — is `docs/PHASES.md`.

| Phase | Objective | Done when |
|---|---|---|
| 0 | Contracts, access spine, synthetic data: ontology, vocabulary, visual tokens, users, sessions, cases, membership, case-scoping dependency, audit chain, generator with ground truth | The ontology is frozen, the access ladder is enforced by one dependency, the audit chain verifies, and the dataset regenerates deterministically |
| 1 | Vertical slice: upload → regex extraction → graph → evidence drawer | You click a node and see the source it came from |
| 2 | spaCy extraction, identity hypotheses, review queue, evaluation harness | You can state resolution precision and recall on a holdout split |
| 3 | Graph analytics, scenarios, resolution prioritisation, fragility | The planted broker surfaces without being searched for |
| 4 | Timeline, map, pattern rules, anomaly scoring | Every finding renders with its full evidence chain |
| 5 | Annotation and assertion layer; security screens, invitations, team management and audit view on the Phase 0 spine | Removing a member takes effect on their next request, and the audit shows it |
| 6 | Constrained query layer and investigation reports | No brief statement exists without a citation |
| 7 | Hardening, evaluation report, rehearsal, deck | Two clean end-to-end runs with the network cable pulled |

**Why the access spine is in Phase 0.** Every endpoint from Phase 1 onward must be case-scoped and audited; building routes first would mean retrofitting both into each one, and missing some. Only the security *screens* wait for Phase 5.

**One tagged demoable build maintained throughout.** The frontend builds against mock JSON from Phase 0 and never waits on the backend.

**What the first working prototype looks like (end of Phase 1):** upload a CDR CSV and an FIR text file; regex pulls phone numbers, vehicle numbers and dates; a graph appears with person and phone nodes and `called`, `transferred_to` and `mentioned_in` edges; clicking a node shows the source with the extracted span or record highlighted. Inaccurate and unstyled, and already more than many teams have in week three.

### Order of work

| # | Task | Owner |
|---|---|---|
| 1 | Ontology, API contract, mock JSON fixtures | Whole team, together |
| 2 | Synthetic generator + ground truth | Data |
| 3 | Postgres schema + migrations, including access tables | Backend |
| 4 | Sessions, membership resolver, case-scoping dependency, audit chain | Backend |
| 5 | UI shell against mock JSON | Frontend, in parallel from step 1 |
| 6 | Ingest + regex extraction + graph build | Backend |
| 7 | Wire UI to real API — **first demoable build, tag it** | Both |
| 8 | spaCy NER | Backend |
| 9 | Identity hypotheses + evaluation harness | Backend, allow generous time |
| 10 | Question queue UI | Frontend |
| 11 | Graph analytics, scenarios, role classification | Third / backend |
| 12 | Pattern rules | Third / backend |
| 13 | Timeline, map, money flow | Frontend |
| 14 | Fragility simulation | Either |
| 15 | Annotation and assertion layer | Both |
| 16 | Security screens, invitations, team management, audit view | Both |
| 17 | Templated brief; optional query layer | Either |
| 18 | Hardening, evaluation report, deck, rehearsals | Whole team |

## 44. The demo

Eight minutes. Shape: fragmented data → automated processing → hidden connection revealed → reasoning shown → operational recommendation.

**Beat 0 — Setup (30s).** A case dashboard listing five FIRs from three stations across two districts. *"Five separate FIRs, three stations, four months. On paper, unrelated."* Then, on camera, unplug the network cable. *"Everything from here runs locally."*

**Beat 1 — Ingestion (60s).** Upload FIRs, CDR, transactions. Live processing panel: documents parsed, mentions by type, entities created. Show one FIR beside its highlighted extractions. *"Every extracted entity points back to the exact span it came from."*

**Beat 2 — The identity question (90s).** Open the question queue. Show the review card: three surfaces of one possible person, evidence for, evidence against, what is not known, and what confirming would do to the network. Confirm it. *"AVISE never merges silently. An investigator decides, the decision is recorded with their name, and it can be reversed."* The graph restructures visibly.

**Beat 3 — The hidden connection (60s).** Two previously separate clusters now join through one node. *"Chennai cases and Coimbatore cases were separate investigations. They share exactly one person, and no single document contains that fact."* Betweenness ranking: number one, by a wide margin. Role badge: Broker.

**Beat 4 — The decoy (45s).** Point at the most visually prominent node. *"More connections than anyone here. He's a taxi driver. High degree, near-zero betweenness, no financial links, one-directional contacts. The system classifies him peripheral — which is why we don't use a single importance score."* This beat costs 45 seconds and buys enormous credibility.

**Beat 5 — Burner continuity (60s).** *"98400-xxx31 dormant 14 March. 90031-xxx87 active 31 hours later. 11 of 14 contacts shared. Same IMEI."* Confirm. The graph grows. *"One person, two identities, and the link exists in no record — it's inferred from behaviour."*

**Beat 6 — Time and money (60s).** Timeline: three call bursts, each 5–7 hours before an FIR incident time. Money flow: circular transfer over nine days, each leg under the reporting threshold, flagged as structuring. *"Both rule-based, both fully explainable."*

**Beat 7 — Fragility (45s).** Invite a judge to choose a node. Remove the broker. The graph splits. *"Two components. Largest drops 47 → 22. Average path length 3.1 → 5.8. The operational question isn't who is important, it's what happens if we act."*

**Beat 8 — Brief and guardrails (60s).** Generate the investigation brief. Inline citations; hover reveals the source span. Scroll to the bottom: observed versus inferred, confidence on each inference, coverage gaps. *"Nothing here is a conclusion. Every item is a lead with an evidence chain, and the system says what it doesn't know."*

**Beat 9 — Access (30s).** Log out, log in as someone not on the case. The case does not exist for them. Then as the lead: revoke a member, show the audit entry, show their notes still attributed in the case.

**Beat 10 — Close (20s).** *"Everything you saw ran on this laptop, offline, on synthetic data with known ground truth — which is why we can tell you our resolution precision is X and recall is Y."*

### Demo rules

Rehearse twice, timed. One-command reset script. Pre-processed database snapshot as fallback. Never let a live external call sit on the critical path. Every team member must be able to answer questions about every module.

## 45. Judging

### Top 10 things that would make AVISE stand out

1. Planted ground truth, with precision and recall numbers stated out loud.
2. Full offline operation — pull the cable on purpose.
3. Evidence chain on every claim, one click away.
4. Burner handset continuity detection.
5. Network fragility simulation, run live with a judge choosing the node.
6. Observation, inference and assertion as first-class distinctions in schema and UI.
7. The identity question model — discovery without assumption.
8. A coverage panel stating what the system does not know.
9. An architecture where prototype and production are the same diagram with different implementations, each swap explainable.
10. A planted decoy, used to show the system distinguishes real brokers from coincidence.

Point 10 deserves emphasis: deliberately demonstrating a false positive and how the system handles it is more persuasive than any accuracy claim, because it shows you tested for failure rather than only for success.

### Top 10 mistakes to avoid

1. **A graph with no story.** A hairball of 500 nodes proves nothing.
2. **Hardcoding the demo.** Judges deviate. If the second click fails, everything before it is discounted.
3. **Risk scores with no explanation.** The fastest way to lose a judge who is paying attention.
4. **Real scraped data.** "We scraped social media" is a losing answer on a privacy-sensitive problem statement.
5. **LLM as the extractor.** One hallucinated entity sinks the pitch.
6. **Beautiful UI, no backend.** Transparent to technical judges within two questions.
7. **No identity resolution.** Duplicate nodes everywhere, and the core problem unsolved.
8. **Feature sprawl.** Five polished features beat fifteen half-features every time.
9. **A live API on the critical path.** Venue wifi fails.
10. **Being unable to answer "how do you know?"** If the answer is "the model said so", the project is finished.

One more: **a team that cannot explain its own system.** If a judge asks how identity resolution works and gets a vague answer, they will assume you used AI tools without understanding the output. Everyone in the demo should be able to whiteboard every module.

## 46. Risks

| Risk | Mitigation |
|---|---|
| Identity resolution underperforms | Start Phase 2 early, build the eval harness alongside, keep exact-identifier matching as a floor that always works |
| spaCy misses Indian names in FIR prose | Gazetteer boost; Tier 1 regex captures structure independently so the graph survives poor NER |
| The graph becomes an unreadable hairball | Default to ~40 filtered nodes, never render everything, full canvas only in focus mode |
| The workspace stutters on a laptop | Lazy-mount heavy sections — a requirement, not an optimisation |
| Demo fails live | Offline operation, one-command reset, pre-seeded snapshot, two full rehearsals |
| Integration failure between modules | Contract-first; ontology locked in Phase 0; frontend on mock JSON |
| Scope creep into advanced features before core is solid | The phase table is the arbiter; revisit weekly |
| Running two SIH problem statements at once | Keep AVISE's conventions internally consistent so context-switching is cheap |

**The honest summary:** the stack is not the hard part. Every technology chosen is boring on purpose. Identity resolution and provenance discipline are the hard parts, and both are solved with ordinary Python and a schema you get right in Phase 0.

## 47. Phase 0 checklist

Nothing else starts until these exist and two people describe them identically. Mirrors Phase 0 in `docs/PHASES.md`; binding rulings are in `docs/PHASE-0-DECISIONS.md`.

**Repository and tooling**
- [ ] Module structure and layered import boundaries, with a structural test
- [ ] PostgreSQL 16 via Docker Compose; Alembic wired to an initial revision
- [ ] FastAPI skeleton with `/api/health`, structured error envelope, CORS locked to the dev origin
- [ ] Vite + React + TypeScript + Tailwind skeleton with routing shell
- [ ] Dev, test, seed, reset and lint scripts (`scripts/*.ps1`, plus a `Makefile`)

**Ontology and contracts**
- [ ] Ontology: node types, edge classes, three origins, edge fields, provenance fields, `SourceLocator`
- [ ] Identity state machine and decision record schema
- [ ] Annotation and assertion schema, with the mandatory basis field
- [ ] Content origin taxonomy
- [ ] Controlled vocabulary module in `domain/`, twenty templates, banned-phrase test
- [ ] Coverage declaration schema
- [ ] Evidence drawer contract
- [ ] TypeScript mirrors of every domain model; mock JSON fixtures for all eight workspace sections
- [ ] Visual identity: `TokenSheet.tsx` rendering the four thread types, three card variants and palette

**Access spine** *(no user-facing screens)*
- [ ] Access tables: users, capabilities, sessions, cases, members, invitations, audit log, jobs
- [ ] Argon2id hashing, server-side sessions, login rate limiting and lockout
- [ ] `get_case_context` enforcing 401 / 404 / 403, and a repository that refuses queries without `case_id`
- [ ] Case creation writes the lead membership in the same transaction
- [ ] Full audit event enum; hash-chained append-only audit log with a verification utility

**Synthetic data**
- [ ] Generator with fixed seed and `ground_truth.json`, all nine structures including 7, 8 and 9
- [ ] Prior records, vehicle registry, towers and background traffic
- [ ] Independent `demo/` and `holdout/` generations sharing no entities
- [ ] SVG composite-sketch portraits; seed script with demo accounts, one open case, one non-member

## 48. Decision log

Reversals and rejections made during design, recorded so they are not relitigated.

| Decision | Outcome | Reason |
|---|---|---|
| Graph database (Neo4j) | **Cut** | 2–5k nodes. Second datastore to synchronise, second service to fail, no benefit. |
| Vector search (pgvector) | **Cut** | Nothing needs vector similarity at this corpus size. |
| Sentence embeddings for name matching | **Cut** | Poor on transliteration variance, initials and name-order inversion — the actual problem. String and phonetic methods are better and explainable. |
| Docker for the full stack | **Postgres only** | Container rebuild friction; Docker Desktop costs ~1 GB on Windows. |
| Five case roles | **Two** | Compartmentalising inside a case team reproduces the fragmentation the product exists to solve. |
| Separate team entity | **Cut** | A team is exactly one case's membership. Two sources of truth for access is a security bug waiting to happen. |
| Join / team codes | **Cut** | Bearer credential: shared, forwardable, revocable only for everyone, records no authoriser. |
| Auto-merge above a confidence threshold | **Cut** | Identity hypotheses with three states instead. Discovery without assumption. |
| Free-form LLM case copilot | **Replaced** | Constrained NL → structured query, with the query shown before it runs. |
| Alerts on high-priority entities | **Replaced** | Priority attaches to questions, not people. |
| Cross-case entity linkage | **Excluded** | Linking people across cases without a legal basis is the failure mode the product prevents. |
| Social media ingestion | **Excluded** | Weakest source, hardest to defend on provenance. |
| GNN link prediction | **Rejected** | No labels, no GPU, unexplainable — a liability in an explainability-first system. |
| Face recognition | **Rejected** | Ethically loaded, adds nothing the graph does not provide. |
| Blockchain for evidence integrity | **Rejected** | Hash-chained append-only audit table gives the same property at no cost. |
| Predictive crime forecasting | **Rejected** | Scientifically contested, reputationally dangerous. |
| JWT authentication | **Rejected** | Cannot revoke mid-life; removal must take effect immediately. |
| Microservices | **Rejected** | No scaling problem; high cost for a three-person team. |
| Reusing another project's skeleton | **Rejected** | AVISE has its own identity, conventions and visual language. |
| Access spine in Phase 5 | **Moved to Phase 0** | Every endpoint must be case-scoped and audited from the first; retrofitting both misses some. Screens stay in Phase 5. |
| Character offsets on every provenance row | **Replaced** | A `SourceLocator` union — text span, record field, record row. Offsets are meaningless for tabular data. |
| `supporting_record_ids[]` as columns | **Derived** | Views over `edge_provenance` by role. Columns would be a second source of truth. |
| "Criminal records" source type | **Renamed** | `prior_records`. A source label must not assert something about the people in it. |
| GLiNER NER benchmark | **Removed** | Requires `torch`; marginal gain on synthetic data we control. |
| Per-entity read auditing | **Bounded** | One `case.opened` row per case entry; `restricted.viewed` on every restricted-entity view. |
| Required `make` | **Dropped** | PowerShell scripts plus a `Makefile` for parity; the team develops on Windows. |

---

*End of report.*
