"""The graph is a projection, rebuilt from PostgreSQL. It is never the truth.

The scenario parameter is present from the first version deliberately: a
projection that cannot say which identity world it was built in produces
centrality figures that cannot be interpreted, and retrofitting the parameter
means revisiting every caller.

Phase 0 fixes the contract. Phase 1 fills the projection from the database.
"""

from __future__ import annotations

from uuid import UUID

import networkx as nx

from avise.graph.scenarios import Scenario, ScenarioSpec


class GraphProjection:
    """Builds a case's graph for one identity scenario."""

    @staticmethod
    def build(case_id: UUID, scenario: Scenario | ScenarioSpec) -> nx.MultiDiGraph:
        """Return the case graph under `scenario`.

        The returned graph always carries `case_id` and `scenario` in
        `graph.graph`, so a metric computed from it can state which world it
        came from.

        Phase 0 returns the empty graph: no entities or edges are loaded yet.
        """
        spec = scenario if isinstance(scenario, ScenarioSpec) else ScenarioSpec(scenario)
        graph: nx.MultiDiGraph = nx.MultiDiGraph()
        graph.graph["case_id"] = case_id
        graph.graph["scenario"] = spec.scenario
        graph.graph["scenario_label"] = spec.label
        graph.graph["hypothesis_id"] = spec.hypothesis_id
        return graph
