"""An assertion without a stated basis is rejected - invariant 9.

The database CHECK enforces the same floor independently; that half is asserted
against information_schema once the migration exists.
"""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from avise.domain.assertion import MINIMUM_BASIS_LENGTH, InvestigatorAssertion
from tests.domain.factories import assertion


def payload_without(**overrides: object) -> dict[str, object]:
    data = assertion().model_dump(mode="json")
    data.update(overrides)
    return data


def test_basis_is_required() -> None:
    field = InvestigatorAssertion.model_fields["basis"]
    assert field.is_required()


def test_missing_basis_is_rejected() -> None:
    data = assertion().model_dump(mode="json")
    del data["basis"]
    with pytest.raises(ValidationError):
        InvestigatorAssertion.model_validate(data)


@pytest.mark.parametrize("basis", ["", "   ", "too short", "         "])
def test_empty_or_short_basis_is_rejected(basis: str) -> None:
    with pytest.raises(ValidationError):
        InvestigatorAssertion.model_validate(payload_without(basis=basis))


def test_whitespace_padded_basis_is_rejected() -> None:
    """Padding is not a basis: the floor applies after stripping."""
    padded = " " * 40
    with pytest.raises(ValidationError):
        InvestigatorAssertion.model_validate(payload_without(basis=padded))


def test_stated_basis_is_accepted() -> None:
    model = InvestigatorAssertion.model_validate(
        payload_without(basis="Told to me by the complainant on 14 March.")
    )
    assert len(model.basis.strip()) >= MINIMUM_BASIS_LENGTH


def test_revocation_records_both_when_and_by_whom() -> None:
    from uuid import uuid4

    with pytest.raises(ValidationError):
        InvestigatorAssertion.model_validate(
            payload_without(revoked_at="2026-03-20T10:00:00Z", revoked_by=None)
        )
    with pytest.raises(ValidationError):
        InvestigatorAssertion.model_validate(
            payload_without(revoked_at=None, revoked_by=str(uuid4()))
        )


def test_entity_assertion_does_not_produce_an_edge() -> None:
    from uuid import uuid4

    with pytest.raises(ValidationError):
        InvestigatorAssertion.model_validate(
            payload_without(assertion_kind="entity", produced_edge_id=str(uuid4()))
        )
