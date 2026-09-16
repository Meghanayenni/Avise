"""An edge cannot persist without supporting provenance - invariant 2, clause 2."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from avise.domain.enums import ProvenanceRole
from avise.domain.provenance import ProvenancedEdge
from tests.domain.factories import (
    RECORD_ID,
    observed_edge,
    provenance_row,
    provenanced_edge,
)


def test_edge_with_supporting_provenance_is_valid() -> None:
    assert provenanced_edge().supporting


def test_edge_without_any_provenance_is_rejected() -> None:
    with pytest.raises(ValidationError):
        ProvenancedEdge(edge=observed_edge(), provenance=[])


def test_edge_with_only_contradicting_provenance_is_rejected() -> None:
    """Evidence against alone does not support an edge into the graph."""
    with pytest.raises(ValidationError):
        ProvenancedEdge(
            edge=observed_edge(),
            provenance=[provenance_row(ProvenanceRole.CONTRADICTING)],
        )


def test_provenance_must_reference_its_own_edge() -> None:
    from uuid import uuid4

    stray = provenance_row()
    stray = stray.model_copy(update={"edge_id": uuid4()})
    with pytest.raises(ValidationError):
        ProvenancedEdge(edge=observed_edge(), provenance=[stray])


def test_record_ids_are_derived_by_role_not_stored() -> None:
    edge = provenanced_edge()
    assert edge.supporting_record_ids == [RECORD_ID]
    assert edge.contradicting_record_ids == [RECORD_ID]
    # The derived views are not fields on the edge itself.
    assert "supporting_record_ids" not in edge.edge.model_dump()
    assert "contradicting_record_ids" not in edge.edge.model_dump()
