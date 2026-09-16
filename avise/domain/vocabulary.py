"""The controlled vocabulary: every system-generated user-facing claim.

No free-text claim strings anywhere else in the codebase. Each template states
what was recorded or measured; none describes a person.

The banned-phrase scanner is the enforcement. It reads files rather than trusting
review, and it is exercised against planted text in the test suite so that a
scanner which has stopped working fails loudly instead of passing quietly.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from string import Formatter

REPO_ROOT = Path(__file__).resolve().parents[2]

#: A line carrying this marker is skipped by the scanner. It exists for the
#: banned list itself and for tests, which have to name the phrases to check them.
ALLOW_MARKER = "banned-phrase-allow"

CLAIM_TEMPLATES: dict[str, str] = {
    # relationships
    "observed_call": "{a} called {b} on {date}",
    "observed_transfer": "{a} transferred {amount} to {b} on {date}",
    "observed_mention": "{a} and {b} are mentioned in the same record",
    "co_presence": "Repeated co-presence observed between {a} and {b}",
    "handset_continuity": "Possible handset continuity between {a} and {b}",
    "shared_address": "{a} and {b} are recorded at the same address",
    "asserted_relationship": "{author} recorded a relationship between {a} and {b}",
    # identity
    "identity_candidate": "Possible identity match between {a} and {b}",
    "identity_confirmed": "{author} confirmed {a} and {b} as the same person",
    "identity_rejected": "{author} recorded {a} and {b} as separate people",
    "identity_pending": "Identity match awaiting investigator review",
    # structure
    "structural_role": "Structural role: {role}",
    "centrality_rank": "Ranked {rank} by {measure} in this component ({scenario})",
    "component_split": "Removing {entity} separates the network into {n} components",
    # patterns
    "burst_before": "Communication burst recorded {hours} hours before {event}",
    "circular_flow": "Circular transfer observed across {n} accounts over {days} days",
    "threshold_structuring": "Repeated transfers recorded below the reporting threshold",
    "new_connection": "Relationship first recorded within the last {days} days",
    # absence and uncertainty
    "coverage_gap": "No {source} data held for {entity} between {from_date} and {to_date}",
    "insufficient_evidence": "Available records are insufficient to resolve this question",
}

BANNED: tuple[str, ...] = (
    "criminal", "predicts", "definitely", "proves",  # banned-phrase-allow
    "guilty", "dangerous", "risk score", "AI detected",  # banned-phrase-allow
    "confirmed suspect", "certainly", "must be",  # banned-phrase-allow
)


@dataclass(frozen=True)
class Violation:
    """One banned phrase, located precisely enough to fix."""

    path: Path
    line_number: int
    phrase: str
    line: str


def render(key: str, **values: object) -> str:
    """Render one claim. An unknown key is a programming error, raised as KeyError."""
    template = CLAIM_TEMPLATES[key]
    return template.format(**values)


def template_fields(key: str) -> list[str]:
    """The placeholder names a template expects."""
    return [name for _, name, _, _ in Formatter().parse(CLAIM_TEMPLATES[key]) if name]


def scan_text(text: str, path: Path | None = None) -> list[Violation]:
    """Every banned phrase in `text`, case-insensitively, skipping marked lines."""
    found: list[Violation] = []
    for number, line in enumerate(text.splitlines(), start=1):
        if ALLOW_MARKER in line:
            continue
        lowered = line.lower()
        for phrase in BANNED:
            if phrase.lower() in lowered:
                found.append(
                    Violation(
                        path=path or Path("<text>"),
                        line_number=number,
                        phrase=phrase,
                        line=line.strip(),
                    )
                )
    return found


def scan_paths(paths: list[Path]) -> list[Violation]:
    """Scan each readable file. A path that does not exist is skipped, not guessed."""
    found: list[Violation] = []
    for path in paths:
        if not path.is_file():
            continue
        found.extend(scan_text(path.read_text(encoding="utf-8"), path))
    return found


def default_scan_files(root: Path | None = None) -> list[Path]:
    """The files the banned-phrase test covers.

    This module, the report templates, and the frontend string tables. Documents
    are excluded: the problem statement title is external and unchanged.
    """
    base = root or REPO_ROOT
    files: list[Path] = [base / "avise" / "domain" / "vocabulary.py"]

    report_package = base / "avise" / "report"
    if report_package.is_dir():
        files.extend(sorted(report_package.rglob("*.py")))

    web_source = base / "web" / "src"
    if web_source.is_dir():
        for pattern in ("*.ts", "*.tsx", "*.json"):
            files.extend(sorted(web_source.rglob(pattern)))

    return [path for path in files if path.is_file()]
