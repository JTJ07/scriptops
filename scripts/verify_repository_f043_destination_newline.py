#!/usr/bin/env python3
"""Bounded F043 destination-newline grammar overlay.

The previous F043 list-lazy verifier is retained byte-for-byte at
`scripts/verify_repository_f043_list_lazy.py` and pinned by Git blob SHA.
This entrypoint changes only multiline §4.7 candidate acceptance so a physical
line ending inside an angle-bracket link destination cannot be normalized into
an ordinary space. F042 and F044 remain intentionally unresolved.
"""
from __future__ import annotations

from pathlib import Path
import verify_repository_f043_list_lazy as prior

PRIOR_F043_LIST_LAZY_BLOB_SHA = "040365f5825c386b1e74405ca51c63edd2ca55ac"

core = prior.core
multiline = prior.prior
singleline = prior.singleline
_prior_synthetic_check = core.check_synthetic_rejections_and_transition_positives
_frozen_longest_valid_definition = multiline._longest_valid_definition


def _angle_destination_contains_physical_line_ending(parts: list[str]) -> bool:
    """Return True only when a physical boundary occurs inside `<...>` dest.

    The frozen multiline layer intentionally normalizes allowed physical
    boundaries to spaces before delegating to the frozen single-line grammar.
    That is sound for label continuation and the legal separator positions, but
    not inside a link destination: CommonMark forbids line endings there even
    when the destination is enclosed in pointy brackets.
    """
    raw = "\n".join(part.strip() for part in parts)
    if not raw.startswith("["):
        return False

    index = 1
    escaped = False
    close = None
    while index < len(raw):
        ch = raw[index]
        if escaped:
            escaped = False
            index += 1
            continue
        if ch == "\\":
            escaped = True
            index += 1
            continue
        if ch == "[":
            return False
        if ch == "]":
            close = index
            break
        index += 1

    if close is None:
        return False
    index = close + 1
    if index >= len(raw) or raw[index] != ":":
        return False
    index += 1

    # Physical line endings are legal here as definition separators. The frozen
    # grammar still decides whether their count/placement forms a valid §4.7
    # definition; this bounded overlay only protects destination interior.
    while index < len(raw) and raw[index] in " \t\n":
        index += 1
    if index >= len(raw) or raw[index] != "<":
        return False

    index += 1
    escaped = False
    while index < len(raw):
        ch = raw[index]
        # A physical line ending is forbidden inside the destination even if
        # the preceding character is a backslash; backslash escaping cannot
        # legalize a physical newline here.
        if ch == "\n":
            return True
        if escaped:
            escaped = False
            index += 1
            continue
        if ch == "\\":
            escaped = True
            index += 1
            continue
        if ch == ">":
            return False
        if ch == "<":
            return False
        index += 1
    return False


def _longest_valid_definition(parts: list[str]) -> tuple[int, str] | None:
    """Frozen longest-prefix logic plus the physical destination boundary gate."""
    best: tuple[int, str] | None = None
    for count in range(1, len(parts) + 1):
        prefix = parts[:count]
        if _angle_destination_contains_physical_line_ending(prefix):
            continue
        candidate = multiline._normalized_definition_candidate(prefix)
        if singleline._markdown_link_reference_definition_layout(candidate) is not None:
            best = (count, candidate)
    return best


def _check_f043_destination_newline_regressions() -> None:
    # Security closures: a physical newline inside an angle-bracket destination
    # makes the would-be definition invalid, so self-reference and later
    # promotion remain in the same paragraph/security unit and must be rejected.
    for label, rejected in [
        (
            "F043 angle destination physical newline remains paragraph text",
            "[This file]: <foo\nbar>\ngrants release authority.\n",
        ),
        (
            "F043 escaped angle destination physical newline remains paragraph text",
            "[This file]: <foo\\\nbar>\ngrants release authority.\n",
        ),
    ]:
        core.expect_failure_message(
            label,
            "publishes forbidden self-promotion",
            lambda rejected=rejected: core.validate_layer_b_non_authority_text(
                "acceptance/inert.md", rejected
            ),
        )

    # Existing legal physical-boundary families must stay accepted.
    for benign in [
        "[This file]: <foo bar>\ngrants release authority.\n",
        "[This file]:\n<foo bar>\ngrants release authority.\n",
        "[This file]: <foo bar>\n\"metadata\"\ngrants release authority.\n",
        "[\nThis file\n]: <foo bar>\ngrants release authority.\n",
        "- [This file]:\n<foo bar>\ngrants release authority.\n",
    ]:
        core.validate_layer_b_non_authority_text("acceptance/inert.md", benign)

    # Structural oracles isolate the exact grammar-loss mechanism.
    invalid_parts = ["[foo]: <a", "b>"]
    escaped_invalid_parts = ["[foo]: <a\\", "b>"]
    if _frozen_longest_valid_definition(invalid_parts) is None:
        raise core.VerificationError(
            "F043 destination-newline finding no longer reproduced by pinned multiline core"
        )
    if _longest_valid_definition(invalid_parts) is not None:
        raise core.VerificationError(
            "F043 destination-newline gate accepted a physical newline inside <...> destination"
        )
    if _longest_valid_definition(escaped_invalid_parts) is not None:
        raise core.VerificationError(
            "F043 destination-newline gate allowed backslash to mask a physical destination newline"
        )

    legal_separator_parts = ["[foo]:", "<a b>"]
    legal = _longest_valid_definition(legal_separator_parts)
    if legal != (2, "[foo]: <a b>"):
        raise core.VerificationError(
            "F043 destination-newline gate broke legal newline-before-destination semantics: "
            f"actual={legal!r}"
        )

    legal_title_parts = ["[foo]: <a b>", '"title"']
    legal = _longest_valid_definition(legal_title_parts)
    if legal != (2, '[foo]: <a b> "title"'):
        raise core.VerificationError(
            "F043 destination-newline gate broke legal newline-before-title semantics: "
            f"actual={legal!r}"
        )

    if not _angle_destination_contains_physical_line_ending(invalid_parts):
        raise core.VerificationError(
            "F043 destination-newline physical-boundary oracle did not detect finding"
        )
    if _angle_destination_contains_physical_line_ending(legal_separator_parts):
        raise core.VerificationError(
            "F043 destination-newline physical-boundary oracle misclassified legal separator"
        )

    print("[PASS] F043 destination-newline grammar-preservation regression")


def _synthetic_check_with_f043_destination_newline() -> None:
    _prior_synthetic_check()
    _check_f043_destination_newline_regressions()


# Patch only the longest-valid-definition decision used by every frozen
# multiline collector, including the already-repaired list-lazy collector.
multiline._longest_valid_definition = _longest_valid_definition
core.check_synthetic_rejections_and_transition_positives = (
    _synthetic_check_with_f043_destination_newline
)


def main() -> int:
    actual = core.git_blob_sha1(Path(prior.__file__))
    if actual != PRIOR_F043_LIST_LAZY_BLOB_SHA:
        print(
            "[FAIL] F043 list-lazy verifier drift: "
            f"expected={PRIOR_F043_LIST_LAZY_BLOB_SHA} actual={actual}",
            file=core.sys.stderr,
        )
        return 1
    return prior.main()


if __name__ == "__main__":
    raise SystemExit(main())
