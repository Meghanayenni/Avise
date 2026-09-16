"""Valid sample instances of every domain model, used by the round-trip test.

A registry rather than a handful of examples: a model added without a sample
fails `test_every_model_has_a_sample`, so coverage cannot quietly lapse.
"""

from __future__ import annotations

from collections.abc import Callable
from datetime import UTC, datetime
from uuid import UUID, uuid4

from avise.domain.access import (
    Case,
    CaseInvitation,
    CaseMembership,
    CaseSummary,
    UserAccount,
    UserProfile,
)
from avise.domain.annotation import Annotation
from avise.domain.assertion import InvestigatorAssertion
from avise.domain.audit import AuditAction, AuditEntry
from avise.domain.base import AviseModel
from avise.domain.coverage import CaseDataCoverage
from avise.domain.edge import Edge
from avise.domain.entity import Entity, EntityAttribute
from avise.domain.enums import (
    AccountCapability,
    AccountStatus,
    CaseStatus,
    ConfidenceBand,
    ContentOrigin,
    CoverageStatus,
    EdgeClass,
    EdgeOrigin,
    EdgeType,
    EntityType,
    ExtractionMethod,
    IdentityState,
    JobKind,
    LeadSource,
    MentionType,
    ProvenanceRole,
    SourceType,
    Standing,
)
from avise.domain.evidence import (
    Confidence,
    DerivationStep,
    DrawerAction,
    EvidenceDrawer,
    EvidenceRef,
    EvidenceSubject,
)
from avise.domain.finding import Finding
from avise.domain.identity import IdentityDecision, IdentityFeature, IdentityHypothesis
from avise.domain.job import Job
from avise.domain.lead import Lead
from avise.domain.locator import RecordField, RecordRow, TextSpan
from avise.domain.mention import Mention
from avise.domain.provenance import EdgeProvenance, ProvenancedEdge

NOW = datetime(2026, 3, 14, 9, 32, tzinfo=UTC)
LATER = datetime(2026, 3, 15, 9, 32, tzinfo=UTC)

CASE_ID = UUID("11111111-1111-4111-8111-111111111111")
DOCUMENT_ID = UUID("22222222-2222-4222-8222-222222222222")
RECORD_ID = UUID("33333333-3333-4333-8333-333333333333")
EDGE_ID = UUID("44444444-4444-4444-8444-444444444444")
USER_ID = UUID("55555555-5555-4555-8555-555555555555")

TEXT_SPAN = TextSpan(document_id=DOCUMENT_ID, char_start=120, char_end=134)
RECORD_FIELD = RecordField(record_id=RECORD_ID, field_name="caller_msisdn")
RECORD_ROW = RecordRow(record_id=RECORD_ID)


def mention() -> Mention:
    return Mention(
        id=uuid4(),
        case_id=CASE_ID,
        document_id=DOCUMENT_ID,
        locator=TEXT_SPAN,
        surface_text="Deepak Rao",
        mention_type=MentionType.PERSON_NAME,
        extraction_method=ExtractionMethod.SPACY_NER,
        confidence=0.82,
        created_at=NOW,
    )


def entity() -> Entity:
    return Entity(
        id=uuid4(),
        case_id=CASE_ID,
        entity_type=EntityType.PERSON,
        canonical_form="Deepak Rao",
        display_ref="P-0041",
        created_from_mention_id=uuid4(),
        attributes=[EntityAttribute(name="district", value="Coimbatore")],
        first_seen_ts=NOW,
        last_seen_ts=LATER,
        created_at=NOW,
    )


def observed_edge() -> Edge:
    return Edge(
        id=EDGE_ID,
        case_id=CASE_ID,
        source_entity_id=uuid4(),
        target_entity_id=uuid4(),
        edge_class=EdgeClass.RELATIONSHIP,
        edge_type=EdgeType.CALLED,
        edge_origin=EdgeOrigin.SYSTEM_OBSERVED,
        confidence=1.0,
        confidence_basis=["exact identifier match"],
        first_seen_ts=NOW,
        last_seen_ts=LATER,
        created_at=NOW,
    )


def inferred_edge() -> Edge:
    return Edge(
        id=uuid4(),
        case_id=CASE_ID,
        source_entity_id=uuid4(),
        target_entity_id=uuid4(),
        edge_class=EdgeClass.RELATIONSHIP,
        edge_type=EdgeType.CO_PRESENT_WITH,
        edge_origin=EdgeOrigin.SYSTEM_INFERRED,
        confidence=0.61,
        confidence_basis=["6 co-locations", "low-traffic tower"],
        alternative_explanations=["shared workplace", "common transit route"],
        inference_rule_id="co_presence_without_communication",
        base_rate_context={"tower_id": "CBE-0114", "devices_per_hour": 11},
        created_at=NOW,
    )


def asserted_edge() -> Edge:
    return Edge(
        id=uuid4(),
        case_id=CASE_ID,
        source_entity_id=uuid4(),
        target_entity_id=uuid4(),
        edge_class=EdgeClass.RELATIONSHIP,
        edge_type=EdgeType.ASSOCIATED_WITH,
        edge_origin=EdgeOrigin.INVESTIGATOR_ASSERTED,
        confidence=1.0,
        created_at=NOW,
    )


def provenance_row(role: ProvenanceRole = ProvenanceRole.SUPPORTING) -> EdgeProvenance:
    return EdgeProvenance(
        id=uuid4(),
        edge_id=EDGE_ID,
        record_id=RECORD_ID,
        locator=RECORD_FIELD,
        role=role,
        extraction_method=ExtractionMethod.STRUCTURED_FIELD,
        created_at=NOW,
    )


def provenanced_edge() -> ProvenancedEdge:
    return ProvenancedEdge(
        edge=observed_edge(),
        provenance=[provenance_row(), provenance_row(ProvenanceRole.CONTRADICTING)],
    )


def hypothesis() -> IdentityHypothesis:
    return IdentityHypothesis(
        id=uuid4(),
        case_id=CASE_ID,
        left_entity_id=uuid4(),
        right_entity_id=uuid4(),
        score=0.71,
        features=[
            IdentityFeature(
                name="name_similarity",
                description="Name similarity 0.94",
                value=0.94,
                role="supporting",
            ),
            IdentityFeature(
                name="dob_mismatch",
                description="Recorded dates of birth differ by 4 years",
                value=-1.0,
                role="contradicting",
            ),
        ],
        blocking_key="RA-Coimbatore",
        created_at=NOW,
    )


def decision() -> IdentityDecision:
    return IdentityDecision(
        id=uuid4(),
        case_id=CASE_ID,
        hypothesis_id=uuid4(),
        from_state=IdentityState.PROPOSED,
        to_state=IdentityState.CONFIRMED,
        decided_by=USER_ID,
        decided_at=NOW,
        evidence_snapshot={"supporting": ["shared phone"], "contradicting": []},
        rationale_text="Complainant confirmed the alias in interview.",
    )


def annotation() -> Annotation:
    return Annotation(
        id=uuid4(),
        case_id=CASE_ID,
        target_type="entity",
        target_id=uuid4(),
        body="Ask the station for the vehicle transfer paperwork.",
        author_id=USER_ID,
        created_at=NOW,
        pinned=True,
    )


def assertion() -> InvestigatorAssertion:
    return InvestigatorAssertion(
        id=uuid4(),
        case_id=CASE_ID,
        assertion_kind="relationship",
        payload={"source_entity_id": str(uuid4()), "target_entity_id": str(uuid4())},
        basis="Witness statement of the complainant, 14 March.",
        author_id=USER_ID,
        created_at=NOW,
        produced_edge_id=uuid4(),
    )


def coverage() -> CaseDataCoverage:
    return CaseDataCoverage(
        id=uuid4(),
        case_id=CASE_ID,
        source_type=SourceType.TRANSACTION,
        subject_entity_id=uuid4(),
        period_from=NOW,
        period_to=LATER,
        status=CoverageStatus.NOT_REQUESTED,
        note="Bank records for this account were never requested.",
    )


def evidence_ref() -> EvidenceRef:
    return EvidenceRef(
        label="CDR-0231",
        locator=RECORD_ROW,
        source_type=SourceType.CDR,
        record_id=RECORD_ID,
    )


def evidence_drawer() -> EvidenceDrawer:
    return EvidenceDrawer(
        subject=EvidenceSubject(subject_type="edge", id=EDGE_ID, label="P-0041 - P-0092"),
        claim="Repeated co-presence observed between P-0041 and P-0092",
        origin=EdgeOrigin.SYSTEM_INFERRED,
        supporting=[evidence_ref()],
        contradicting=[],
        unknown=["No photograph available for either entity"],
        alternatives=["Shared workplace", "Common transit route"],
        derivation=[
            DerivationStep(order=1, statement="6 co-locations within 15-minute windows"),
            DerivationStep(
                order=2,
                statement="Tower averages 11 unique devices per hour",
                rule_id="co_presence_without_communication",
            ),
        ],
        confidence=Confidence(
            band=ConfidenceBand.MODERATE, basis=["repeated", "low-traffic tower"]
        ),
        actions=[DrawerAction(key="open_source", label="Open source records")],
    )


def finding() -> Finding:
    return Finding(
        id=uuid4(),
        case_id=CASE_ID,
        claim_key="co_presence",
        claim_values={"a": "P-0041", "b": "P-0092"},
        origin=ContentOrigin.RULE_FINDING,
        supporting=[evidence_ref()],
        limitations=["No direct communication observed between them"],
        alternative_explanations=["Both may regularly visit this location"],
        confidence=Confidence(band=ConfidenceBand.MODERATE, basis=["6 co-locations"]),
        created_at=NOW,
    )


def lead() -> Lead:
    return Lead(
        id=uuid4(),
        case_id=CASE_ID,
        question="Would CCTV for the identified windows resolve this co-presence?",
        what_would_answer_it=["CCTV for tower CBE-0114 windows"],
        sources_to_consult=["Station CCTV archive"],
        source=LeadSource.PATTERN,
        priority=0.62,
        created_at=NOW,
    )


def audit_entry() -> AuditEntry:
    return AuditEntry(
        id=uuid4(),
        actor_user_id=USER_ID,
        action=AuditAction.CASE_OPENED,
        case_id=CASE_ID,
        target_type="case",
        target_id=CASE_ID,
        at=NOW,
        ip="127.0.0.1",
        prev_hash="a" * 64,
        row_hash="b" * 64,
    )


def job() -> Job:
    return Job(id=uuid4(), case_id=CASE_ID, kind=JobKind.PARSE_DOCUMENT, created_at=NOW)


def user_profile() -> UserProfile:
    return UserProfile(
        id=USER_ID,
        service_id="TN-SI-4471",
        full_name="A. Investigator",
        designation="Sub-Inspector",
        status=AccountStatus.ACTIVE,
    )


def user_account() -> UserAccount:
    return UserAccount(
        id=USER_ID,
        service_id="TN-SI-4471",
        full_name="A. Investigator",
        designation="Sub-Inspector",
        email="investigator@example.gov.in",
        status=AccountStatus.ACTIVE,
        capabilities=[AccountCapability.CASE_CREATE],
        created_at=NOW,
    )


def case() -> Case:
    return Case(
        id=CASE_ID,
        case_number="CASE-2026-0001",
        title="Inter-district distribution network",
        status=CaseStatus.OPEN,
        created_by=USER_ID,
        opened_at=NOW,
    )


def case_summary() -> CaseSummary:
    return CaseSummary(
        id=CASE_ID,
        case_number="CASE-2026-0001",
        title="Inter-district distribution network",
        status=CaseStatus.OPEN,
        standing=Standing.LEAD,
        opened_at=NOW,
    )


def membership() -> CaseMembership:
    return CaseMembership(
        id=uuid4(),
        case_id=CASE_ID,
        user_id=USER_ID,
        standing=Standing.INVESTIGATOR,
        granted_by=uuid4(),
        granted_at=NOW,
    )


def invitation() -> CaseInvitation:
    return CaseInvitation(
        id=uuid4(),
        case_id=CASE_ID,
        invited_user_id=uuid4(),
        invited_by=USER_ID,
        created_at=NOW,
        expires_at=LATER,
    )


#: model class -> a factory producing a valid instance
SAMPLES: dict[type[AviseModel], Callable[[], AviseModel]] = {
    Mention: mention,
    Entity: entity,
    EntityAttribute: lambda: EntityAttribute(name="district", value="Chennai"),
    Edge: observed_edge,
    EdgeProvenance: provenance_row,
    ProvenancedEdge: provenanced_edge,
    IdentityHypothesis: hypothesis,
    IdentityFeature: lambda: hypothesis().features[0],
    IdentityDecision: decision,
    Annotation: annotation,
    InvestigatorAssertion: assertion,
    CaseDataCoverage: coverage,
    EvidenceRef: evidence_ref,
    EvidenceSubject: lambda: evidence_drawer().subject,
    DerivationStep: lambda: evidence_drawer().derivation[0],
    Confidence: lambda: Confidence(band=ConfidenceBand.HIGH, basis=["exact match"]),
    DrawerAction: lambda: DrawerAction(key="create_lead", label="Create lead"),
    EvidenceDrawer: evidence_drawer,
    Finding: finding,
    Lead: lead,
    AuditEntry: audit_entry,
    Job: job,
    UserProfile: user_profile,
    UserAccount: user_account,
    Case: case,
    CaseSummary: case_summary,
    CaseMembership: membership,
    CaseInvitation: invitation,
    TextSpan: lambda: TEXT_SPAN,
    RecordField: lambda: RECORD_FIELD,
    RecordRow: lambda: RECORD_ROW,
}
