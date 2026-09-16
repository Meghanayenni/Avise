"""edge_origin is non-nullable and no serialiser may omit it - invariant 3.

Asserted against the model itself rather than a hand-written example, so the
guarantee cannot rot when fields move.
"""

from __future__ import annotations

from uuid import uuid4

import pytest
from pydantic import ValidationError

from avise.domain.edge import Edge
from avise.domain.enums import EdgeClass, EdgeOrigin, EdgeType
from tests.domain.factories import NOW, asserted_edge, inferred_edge, observed_edge


def test_edge_origin_is_required_with_no_default() -> None:
    field = Edge.model_fields["edge_origin"]
    assert field.is_required()
    assert field.default is not None or field.is_required()
    assert field.annotation is EdgeOrigin


def test_edge_cannot_be_built_without_an_origin() -> None:
    with pytest.raises(ValidationError) as caught:
        Edge(
            id=uuid4(),
            case_id=uuid4(),
            source_entity_id=uuid4(),
            target_entity_id=uuid4(),
            edge_class=EdgeClass.RELATIONSHIP,
            edge_type=EdgeType.CALLED,
            confidence=1.0,
            created_at=NOW,
        )
    assert any(error["loc"] == ("edge_origin",) for error in caught.value.errors())


@pytest.mark.parametrize("factory", [observed_edge, inferred_edge, asserted_edge])
def test_no_dump_flag_can_omit_edge_origin(factory) -> None:  # type: ignore[no-untyped-def]
    edge = factory()
    dumps = [
        edge.model_dump(),
        edge.model_dump(exclude_unset=True),
        edge.model_dump(exclude_defaults=True),
        edge.model_dump(exclude_none=True),
        edge.model_dump(mode="json"),
    ]
    for dumped in dumps:
        assert dumped["edge_origin"] == edge.edge_origin
    assert '"edge_origin"' in edge.model_dump_json()


def test_only_the_three_origins_are_accepted() -> None:
    assert {origin.value for origin in EdgeOrigin} == {
        "system_observed",
        "system_inferred",
        "investigator_asserted",
    }
    with pytest.raises(ValidationError):
        Edge.model_validate({**observed_edge().model_dump(mode="json"), "edge_origin": "assumed"})


def test_inferred_edge_must_name_its_rule() -> None:
    payload = inferred_edge().model_dump(mode="json")
    payload["inference_rule_id"] = None
    with pytest.raises(ValidationError):
        Edge.model_validate(payload)


def test_observed_edge_may_not_carry_an_inference_rule() -> None:
    payload = observed_edge().model_dump(mode="json")
    payload["inference_rule_id"] = "co_presence_without_communication"
    with pytest.raises(ValidationError):
        Edge.model_validate(payload)
