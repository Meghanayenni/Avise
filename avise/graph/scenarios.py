"""Which world a number came from.

Betweenness changes depending on which merges are confirmed, so "who is the
broker" has no single answer while hypotheses are open. Every metric states its
scenario; a metric without one is not reportable.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from uuid import UUID


class Scenario(StrEnum):
    #: Confirmed merges only. The default: what is actually known.
    CONFIRMED = "confirmed"
    #: Confirmed plus every open hypothesis: what if each resolved as proposed.
    HYPOTHETICAL = "hypothetical"
    #: Confirmed plus exactly one hypothesis: the impact preview for one decision.
    SINGLE = "single"


@dataclass(frozen=True)
class ScenarioSpec:
    """A scenario and, for `single`, the hypothesis it turns on."""

    scenario: Scenario = Scenario.CONFIRMED
    hypothesis_id: UUID | None = None

    def __post_init__(self) -> None:
        if self.scenario is Scenario.SINGLE and self.hypothesis_id is None:
            raise ValueError("scenario 'single' requires a hypothesis_id")
        if self.scenario is not Scenario.SINGLE and self.hypothesis_id is not None:
            raise ValueError("hypothesis_id applies only to scenario 'single'")

    @property
    def label(self) -> str:
        """The label rendered beside every metric."""
        if self.scenario is Scenario.SINGLE:
            return f"single({self.hypothesis_id})"
        return str(self.scenario)
