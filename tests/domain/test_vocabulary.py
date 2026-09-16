"""The banned-phrase test, plus proof that the scanner detects a planted phrase.

The risk with a scanner is that it passes because it scanned nothing. Three
guards: a self-test on planted text, a coverage guard on the file list, and the
real scan itself.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from avise.domain.vocabulary import (
    BANNED,
    CLAIM_TEMPLATES,
    default_scan_files,
    render,
    scan_paths,
    scan_text,
    template_fields,
)

EXPECTED_KEYS = {
    "observed_call",
    "observed_transfer",
    "observed_mention",
    "co_presence",
    "handset_continuity",
    "shared_address",
    "asserted_relationship",
    "identity_candidate",
    "identity_confirmed",
    "identity_rejected",
    "identity_pending",
    "structural_role",
    "centrality_rank",
    "component_split",
    "burst_before",
    "circular_flow",
    "threshold_structuring",
    "new_connection",
    "coverage_gap",
    "insufficient_evidence",
}


def test_there_are_exactly_twenty_templates() -> None:
    assert len(CLAIM_TEMPLATES) == 20
    assert set(CLAIM_TEMPLATES) == EXPECTED_KEYS


@pytest.mark.parametrize("key", sorted(CLAIM_TEMPLATES))
def test_every_template_renders(key: str) -> None:
    values = {field: f"<{field}>" for field in template_fields(key)}
    rendered = render(key, **values)
    assert rendered
    assert "{" not in rendered


def test_unknown_template_key_raises() -> None:
    with pytest.raises(KeyError):
        render("no_such_claim")


@pytest.mark.parametrize("key", sorted(CLAIM_TEMPLATES))
def test_no_template_contains_a_banned_phrase(key: str) -> None:
    assert scan_text(CLAIM_TEMPLATES[key]) == []


# --- the scanner must actually work -----------------------------------------


@pytest.mark.parametrize("phrase", BANNED)
def test_scanner_detects_every_banned_phrase(tmp_path: Path, phrase: str) -> None:
    planted = tmp_path / "planted.ts"
    planted.write_text(f'export const label = "{phrase} here";\n', encoding="utf-8")
    violations = scan_paths([planted])
    assert [v.phrase for v in violations] == [phrase]
    assert violations[0].line_number == 1
    assert violations[0].path == planted


def test_scanner_detects_planted_phrase_in_context(tmp_path: Path) -> None:
    planted = tmp_path / "strings.ts"
    planted.write_text(
        "\n".join(
            [
                "export const strings = {",
                '  headline: "Connected component of interest",',
                '  score: "Risk score 0.87",',
                '  banner: "AI detected a network",',
                "};",
            ]
        ),
        encoding="utf-8",
    )
    violations = scan_paths([planted])
    assert {v.phrase for v in violations} == {"risk score", "AI detected"}
    assert {v.line_number for v in violations} == {3, 4}


def test_scanner_is_case_insensitive(tmp_path: Path) -> None:
    planted = tmp_path / "loud.tsx"
    planted.write_text("const x = 'PROVES it';\n", encoding="utf-8")
    assert [v.phrase for v in scan_paths([planted])] == ["proves"]


def test_scanner_respects_the_allow_marker(tmp_path: Path) -> None:
    planted = tmp_path / "allowed.py"
    planted.write_text('WORDS = ("guilty",)  # banned-phrase-allow\n', encoding="utf-8")
    assert scan_paths([planted]) == []


def test_scanner_skips_paths_that_do_not_exist(tmp_path: Path) -> None:
    assert scan_paths([tmp_path / "absent.ts"]) == []


# --- coverage guard and the real scan ---------------------------------------


def test_scan_covers_expected_files() -> None:
    """An empty or mis-rooted file list would make the real scan meaningless."""
    files = default_scan_files()
    assert files, "the banned-phrase scan found no files to scan"
    names = {path.name for path in files}
    assert "vocabulary.py" in names


def test_no_banned_phrase_in_scanned_files() -> None:
    violations = scan_paths(default_scan_files())
    assert violations == [], "\n".join(
        f"{v.path}:{v.line_number} contains {v.phrase!r}: {v.line}" for v in violations
    )
