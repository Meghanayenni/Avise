"""The projection contract, including the scenario parameter it carries from day one."""

from __future__ import annotations

from uuid import uuid4

import networkx as nx
import pytest

from avise.graph.projection import GraphProjection
from avise.graph.scenarios import Scenario, ScenarioSpec


def test_build_returns_a_multidigraph() -> None:
    graph = GraphProjection.build(uuid4(), Scenario.CONFIRMED)
    assert isinstance(graph, nx.MultiDiGraph)


def test_phase_0_projection_is_empty() -> None:
    graph = GraphProjection.build(uuid4(), Scenario.CONFIRMED)
    assert graph.number_of_nodes() == 0
    assert graph.number_of_edges() == 0


def test_graph_states_its_case_and_scenario() -> None:
    """A metric computed from this graph can always say which world it came from."""
    case_id = uuid4()
    graph = GraphProjection.build(case_id, Scenario.HYPOTHETICAL)
    assert graph.graph["case_id"] == case_id
    assert graph.graph["scenario"] is Scenario.HYPOTHETICAL
    assert graph.graph["scenario_label"] == "hypothetical"


def test_single_scenario_requires_a_hypothesis() -> None:
    with pytest.raises(ValueError):
        ScenarioSpec(Scenario.SINGLE)


def test_hypothesis_id_belongs_only_to_single() -> None:
    with pytest.raises(ValueError):
        ScenarioSpec(Scenario.CONFIRMED, hypothesis_id=uuid4())


def test_single_scenario_labels_its_hypothesis() -> None:
    hypothesis_id = uuid4()
    graph = GraphProjection.build(uuid4(), ScenarioSpec(Scenario.SINGLE, hypothesis_id))
    assert graph.graph["hypothesis_id"] == hypothesis_id
    assert graph.graph["scenario_label"] == f"single({hypothesis_id})"


def test_there_are_exactly_three_scenarios() -> None:
    assert {s.value for s in Scenario} == {"confirmed", "hypothetical", "single"}
