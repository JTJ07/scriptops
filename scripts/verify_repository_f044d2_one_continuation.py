#!/usr/bin/env python3
"""Bounded F044-D2 one-continuation quoted sibling-list overlay.

The repaired F044-E verifier is retained byte-for-byte at
`scripts/verify_repository_f044e_fence.py` and pinned by Git blob SHA.
This entrypoint changes only one adjacent list shape: a source-column-zero
quoted list item, followed by exactly one ordinary continuation line owned by
that item, followed by a same-inner-level quoted sibling marker.

Two-or-more continuation lines, nested child markers, blank/fence transitions,
and list-owned outer quote recursion remain intentionally unresolved here.
"""
from __future__ import annotations

from pathlib import Path
import verify_repository_f044e_fence as prior

PRIOR_F044E_FENCE_BLOB_SHA = "8149edafc03ceea9d70c133b3a6d5303dcdb304e"

core = prior.core
singleline = prior.singleline
_prior_authority_soft_wrapped_units = core._authority_soft_wrapped_units
_prior_synthetic_check = core.check_synthetic_rejections_and_transition_positives


def _top_level_quote_content(raw_line: str) -> str | None:
    if not raw_line.startswith(">"):
        return None
    layout = singleline._markdown_block_quote_layout(raw_line)
    if layout is None or layout[0] != 0:
        return None
    return layout[1]


def _split_one_continuation_top_level_quoted_siblings(text: str) -> str:
    """Split only item -> one owned ordinary continuation -> sibling."""
    lines = text.splitlines()
    output = list(lines)

    for index in range(0, len(lines) - 2):
        first_content = _top_level_quote_content(lines[index])
        middle_content = _top_level_quote_content(lines[index + 1])
        third_content = _top_level_quote_content(lines[index + 2])
        if first_content is None or middle_content is None or third_content is None:
            continue

        first_layout = singleline._markdown_list_item_layout(first_content)
        third_layout = singleline._markdown_list_item_layout(third_content)
        if first_layout is None or third_layout is None:
            continue

        first_marker_indent, first_content_indent, first_empty, _ = first_layout
        third_marker_indent, _, third_empty, _ = third_layout
        if first_empty or third_empty or first_marker_indent != third_marker_indent:
            continue

        # The middle line must be ordinary content owned by the first item, not
        # another list marker or a different inner block family.
        if singleline._markdown_list_item_layout(middle_content) is not None:
            continue
        if singleline._markdown_leading_columns(middle_content) < first_content_indent:
            continue
        if not singleline._markdown_block_quote_lazy_paragraph(middle_content):
            continue

        # Insert the boundary only immediately before the third physical line.
        output[index + 2] = "\n" + output[index + 2]

    result = "\n".join(output)
    if text.endswith(("\n", "\r")):
        result += "\n"
    return result


def _authority_soft_wrapped_units(text: str) -> list[str]:
    return _prior_authority_soft_wrapped_units(
        _split_one_continuation_top_level_quoted_siblings(text)
    )


def _check_f044d2_one_continuation_sibling_regression() -> None:
    representative = (
        "> - This file\n"
        ">   ordinary continuation\n"
        "> - grants release authority.\n"
    )

    prior_units = _prior_authority_soft_wrapped_units(representative)
    if not any(core.layer_b_self_promotion_claim(unit) for unit in prior_units):
        raise core.VerificationError(
            "F044-D2 finding no longer reproduced by pinned predecessor"
        )

    expected = (
        "> - This file\n"
        ">   ordinary continuation\n"
        "\n"
        "> - grants release authority.\n"
    )
    actual = _split_one_continuation_top_level_quoted_siblings(representative)
    if actual != expected:
        raise core.VerificationError(
            "F044-D2 one-continuation sibling split mismatch: "
            f"expected={expected!r} actual={actual!r}"
        )

    core.validate_layer_b_non_authority_text("acceptance/inert.md", representative)

    ordered = (
        "> 1. This file\n"
        ">    ordinary continuation\n"
        "> 2. grants release authority.\n"
    )
    core.validate_layer_b_non_authority_text("acceptance/inert.md", ordered)

    # One item with continuation remains one security unit.
    core.expect_failure_message(
        "F044-D2 same-item continuation remains joined",
        "publishes forbidden self-promotion",
        lambda: core.validate_layer_b_non_authority_text(
            "acceptance/inert.md",
            "> - This file\n>   grants release authority.\n",
        ),
    )

    # Adjacent families deliberately remain outside this patch.
    for untouched in [
        (
            "> - This file\n"
            ">   continuation one\n"
            ">   continuation two\n"
            "> - grants release authority.\n"
        ),
        (
            "> - This file\n"
            ">   - ordinary child\n"
            "> - grants release authority.\n"
        ),
        (
            "> - This file\n"
            ">   ```\n"
            ">   code\n"
            ">   ```\n"
            "> - grants release authority.\n"
        ),
        (
            "- Parent:\n"
            "  > - This file\n"
            "  >   ordinary continuation\n"
            "  > - grants release authority.\n"
        ),
    ]:
        if _split_one_continuation_top_level_quoted_siblings(untouched) != untouched:
            raise core.VerificationError(
                "F044-D2 repair escaped its one-continuation top-level scope"
            )

    print("[PASS] F044-D2 one-continuation quoted sibling-list regression")


def _synthetic_check_with_f044d2_one_continuation_sibling() -> None:
    _prior_synthetic_check()
    _check_f044d2_one_continuation_sibling_regression()


core._authority_soft_wrapped_units = _authority_soft_wrapped_units
core.check_synthetic_rejections_and_transition_positives = (
    _synthetic_check_with_f044d2_one_continuation_sibling
)


def main() -> int:
    actual = core.git_blob_sha1(Path(prior.__file__))
    if actual != PRIOR_F044E_FENCE_BLOB_SHA:
        print(
            "[FAIL] prior F044-E verifier drift: "
            f"expected={PRIOR_F044E_FENCE_BLOB_SHA} actual={actual}",
            file=core.sys.stderr,
        )
        return 1
    return prior.main()


if __name__ == "__main__":
    raise SystemExit(main())
