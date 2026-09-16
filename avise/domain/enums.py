"""Closed vocabularies. Every one of these is a contract, mirrored in TypeScript."""

from __future__ import annotations

from enum import StrEnum


class EntityType(StrEnum):
    """Report section 7. Ten node types, no more."""

    PERSON = "person"
    PHONE = "phone"
    ACCOUNT = "account"
    VEHICLE = "vehicle"
    LOCATION = "location"
    ORGANISATION = "organisation"
    EVENT = "event"
    DOCUMENT = "document"
    HANDSET = "handset"
    PHOTO = "photo"


class EdgeClass(StrEnum):
    RELATIONSHIP = "relationship"
    IDENTITY = "identity"


class EdgeType(StrEnum):
    """Relationship kinds. `SAME_AS` is the only IDENTITY-class edge."""

    CALLED = "called"
    TRANSFERRED_TO = "transferred_to"
    MENTIONED_IN = "mentioned_in"
    CO_PRESENT_WITH = "co_present_with"
    SHARED_HANDSET_WITH = "shared_handset_with"
    REGISTERED_TO = "registered_to"
    RESIDES_AT = "resides_at"
    ASSOCIATED_WITH = "associated_with"
    SAME_AS = "same_as"


class EdgeOrigin(StrEnum):
    """Non-nullable on every edge. Serialisers may not omit it."""

    SYSTEM_OBSERVED = "system_observed"
    SYSTEM_INFERRED = "system_inferred"
    INVESTIGATOR_ASSERTED = "investigator_asserted"


class ContentOrigin(StrEnum):
    """Report section 9. The last three are the only ones an investigator authors."""

    OBSERVATION = "observation"
    RULE_FINDING = "rule_finding"
    MODEL_INFERENCE = "model_inference"
    SUGGESTION = "suggestion"
    HUMAN_NOTE = "human_note"
    HUMAN_ASSERTION = "human_assertion"
    DECISION = "decision"


class SourceType(StrEnum):
    """The seven source types. `PRIOR_RECORD` is never labelled otherwise."""

    FIR = "fir"
    CDR = "cdr"
    TRANSACTION = "transaction"
    SURVEILLANCE_NOTE = "surveillance_note"
    PRIOR_RECORD = "prior_record"
    VEHICLE_REGISTRY = "vehicle_registry"
    TOWER = "tower"


class LocatorKind(StrEnum):
    TEXT_SPAN = "text_span"
    RECORD_FIELD = "record_field"
    RECORD_ROW = "record_row"


class ExtractionMethod(StrEnum):
    REGEX = "regex"
    GAZETTEER = "gazetteer"
    SPACY_NER = "spacy_ner"
    STRUCTURED_FIELD = "structured_field"
    INVESTIGATOR = "investigator"


class ProvenanceRole(StrEnum):
    SUPPORTING = "supporting"
    CONTRADICTING = "contradicting"


class MentionType(StrEnum):
    PERSON_NAME = "person_name"
    PHONE_NUMBER = "phone_number"
    ACCOUNT_NUMBER = "account_number"
    IFSC = "ifsc"
    IMEI = "imei"
    VEHICLE_REGISTRATION = "vehicle_registration"
    DATE = "date"
    AMOUNT = "amount"
    LOCATION_NAME = "location_name"
    ORGANISATION_NAME = "organisation_name"


class IdentityState(StrEnum):
    """Report section 5. `PROPOSED` persists indefinitely; no timeout resolves it."""

    PROPOSED = "proposed"
    CONFIRMED = "confirmed"
    REJECTED = "rejected"
    NEEDS_EVIDENCE = "needs_evidence"
    DEFERRED = "deferred"


class ConfidenceBand(StrEnum):
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"


class CoverageStatus(StrEnum):
    """Report section 10. `NOT_REQUESTED` is a different statement from `UNAVAILABLE`."""

    REQUESTED = "requested"
    RECEIVED = "received"
    PARTIAL = "partial"
    UNAVAILABLE = "unavailable"
    NOT_REQUESTED = "not_requested"


class FindingStatus(StrEnum):
    ACTIVE = "active"
    DISMISSED = "dismissed"


class LeadStatus(StrEnum):
    OPEN = "open"
    ACTIONED = "actioned"
    CLOSED = "closed"


class LeadSource(StrEnum):
    IDENTITY = "identity"
    GAP = "gap"
    PATTERN = "pattern"


class Standing(StrEnum):
    """Two standings. No analyst, observer or supervisor role."""

    LEAD = "lead"
    INVESTIGATOR = "investigator"


class AccountCapability(StrEnum):
    """Account-level, provisioned by an administrator, separate from case standing."""

    CASE_CREATE = "case:create"
    AUDIT_READ_GLOBAL = "audit:read_global"
    USER_PROVISION = "user:provision"


class AccountStatus(StrEnum):
    PENDING_VERIFICATION = "pending_verification"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    DEACTIVATED = "deactivated"


class CaseStatus(StrEnum):
    OPEN = "open"
    CLOSED = "closed"
    ARCHIVED = "archived"


class InvitationStatus(StrEnum):
    SENT = "sent"
    ACCEPTED = "accepted"
    DECLINED = "declined"
    REVOKED = "revoked"
    EXPIRED = "expired"


class JobKind(StrEnum):
    PARSE_DOCUMENT = "parse_document"
    EXTRACT_MENTIONS = "extract_mentions"
    RESOLVE_CANDIDATES = "resolve_candidates"
    REBUILD_GRAPH = "rebuild_graph"


class JobStatus(StrEnum):
    QUEUED = "queued"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
