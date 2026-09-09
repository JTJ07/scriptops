#!/usr/bin/env python3
"""Bounded F044-C top-level quoted blank paragraph-boundary overlay.

The repaired F044-B verifier is retained byte-for-byte at
`scripts/verify_repository_f044b_thematic_boundary.py` and pinned by Git blob
SHA. This entrypoint changes only a source-column-zero explicit blank quote line
between two ordinary quoted paragraph lines: that inner blank is presented to
the frozen authority-unit parser as a paragraph boundary.

F044-D/E quoted sibling-list/fence families, nested blank recursion and
list-owned quote recursion remain intentionally unresolved.
"""
from __future__ import annotations

from pathlib import Path
import verify_repository_f044b_thematic_boundary as prior

PRIOR_F044B_THEMATIC_BOUNDARY_BLOB_SHA = "a491562c643768eb3cd585acc0d061e8ecb02cc6"

core = prior.core
singleline = prior.singleline
_prior_authority_soft_wrapped_units = core._authority_soft_wrapped_units
_prior_synthetic_check = core.check_synthetic_rejections_and_transition_positives


def _ordinary_top_level_quote_paragraph_content(raw_line: str) -> str | None:
    if not raw_line.startswith(">"):
        return None
    layout = singleline._markdown_block_quote_layout(raw_line)
    if layout is None or layout[0] != 0:
        return None
    _, content = layout
    if not content.strip() or content.lstrip(" \t").startswith(">"):
        return None

    # F044-D is a separate open family. The frozen lazy predicate does not
    # classify list starts as an inner boundary, so exclude them explicitly
    # here rather than broadening this F044-C repair into list parsing.
    if singleline._markdown_list_item_layout(content) is not None:
        return None

    if not singleline._markdown_block_quote_lazy_paragraph(content):
        return None
    return content


def _split_top_level_quoted_blank_paragraph_boundaries(text: str) -> str:
    """Turn only an ordinary-paragraph `>` inner blank into a parser blank."""
    lines = text.splitlines()
    output = list(lines)

    for index in range(1, len(lines) - 1):
        raw_line = lines[index]
        if not raw_line.startswith(">"):
            continue
        layout = singleline._markdown_block_quote_layout(raw_line)
        if layout is None or layout[0] != 0 or layout[1].strip():
            continue
        if _ordinary_top_level_quote_paragraph_content(lines[index - 1]) is None:
            continue
        if _ordinary_top_level_quote_paragraph_content(lines[index + 1]) is None:
            continue
        output[index] = ""

    result = "\n".join(output)
    if text.endswith(("\n", "\r")):
        result += "\n"
    return result


def _authority_soft_wrapped_units(text: str) -> list[str]:
    return _prior_authority_soft_wrapped_units(
        _split_top_level_quoted_blank_paragraph_boundaries(text)
    )


def _check_f044c_quoted_blank_boundary_regression() -> None:
    representative = "> This file\n>\n> grants release authority.\n"

    prior_units = _prior_authority_soft_wrapped_units(representative)
    if not any(core.layer_b_self_promotion_claim(unit) for unit in prior_units):
        raise core.VerificationError(
            "F044-C quoted-blank finding no longer reproduced by pinned predecessor"
        )

    expected = "> This file\n\n> grants release authority.\n"
    actual = _split_top_level_quoted_blank_paragraph_boundaries(representative)
    if actual != expected:
        raise core.VerificationError(
            "F044-C quoted-blank split mismatch: "
            f"expected={expected!r} actual={actual!r}"
        )

    core.validate_layer_b_non_authority_text("acceptance/inert.md", representative)

    for benign in [
        "> This file\n>   \n> grants release authority.\n",
        "> This file\n>\t\n> grants release authority.\n",
    ]:
        core.validate_layer_b_non_authority_text("acceptance/inert.md", benign)

    # Ordinary explicit quote continuation without a blank stays one paragraph.
    core.expect_failure_message(
        "F044-C ordinary explicit quote continuation remains joined",
        "publishes forbidden self-promotion",
        lambda: core.validate_layer_b_non_authority_text(
            "acceptance/inert.md",
            "> This file\n> ordinary text\n> grants release authority.\n",
        ),
    )

    # Do not reinterpret blank quote lines inside other unresolved inner blocks.
    for untouched in [
        "> ```\n>\n> This file\n> ```\n> grants release authority.\n",
        "> - This file\n>\n> - grants release authority.\n",
        "> > This file\n>\n> > grants release authority.\n",
        "- Parent:\n  > This file\n  >\n  > grants release authority.\n",
    ]:
        if _split_top_level_quoted_blank_paragraph_boundaries(untouched) != untouched:
            raise core.VerificationError(
                "F044-C repair escaped its ordinary top-level blank-boundary scope"
            )

    print("[PASS] F044-C top-level quoted blank paragraph-boundary regression")


def _synthetic_check_with_f044c_quoted_blank_boundary() -> None:
    _prior_synthetic_check()
    _check_f044c_quoted_blank_boundary_regression()


core._authority_soft_wrapped_units = _authority_soft_wrapped_units
core.check_synthetic_rejections_and_transition_positives = (
    _synthetic_check_with_f044c_quoted_blank_boundary
)


def main() -> int:
    actual = core.git_blob_sha1(Path(prior.__file__))
    if actual != PRIOR_F044B_THEMATIC_BOUNDARY_BLOB_SHA:
        print(
            "[FAIL] prior F044-B verifier drift: "
            f"expected={PRIOR_F044B_THEMATIC_BOUNDARY_BLOB_SHA} actual={actual}",
            file=core.sys.stderr,
        )
        return 1
    return prior.main()


if __name__ == "__main__":
    raise SystemExit(main())
