#!/usr/bin/env python3
"""Bounded F044-D4 one-nested-child outer-sibling overlay, retried on D5.

The repaired F044-D5 verifier is retained byte-for-byte at
`scripts/verify_repository_f044d5_parent_context.py` and pinned by Git blob
SHA. This entrypoint changes only one nested-list shape: one nonempty top-level
quoted outer list item, exactly one nonempty nested child marker beginning at
that outer item's content indentation, then a nonempty sibling returning to the
outer marker indentation.

Multiple child markers, child continuation, deeper nesting, blank/fence/block
transitions and list-owned outer quote recursion remain outside this repair.
"""
from __future__ import annotations

from pathlib import Path
import verify_repository_f044d5_parent_context as prior

PRIOR_F044D5_PARENT_CONTEXT_BLOB_SHA = "fd8290e38723f9b69ba06a60adec37e1797f25f4"

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


def _split_one_nested_child_top_level_quoted_outer_sibling(text: str) -> str:
    """Split only outer item -> one exact-content-indent child -> outer sibling."""
    lines = text.splitlines()
    output = list(lines)

    for index in range(0, len(lines) - 2):
        first_content = _top_level_quote_content(lines[index])
        child_content = _top_level_quote_content(lines[index + 1])
        sibling_content = _top_level_quote_content(lines[index + 2])
        if first_content is None or child_content is None or sibling_content is None:
            continue

        first_layout = singleline._markdown_list_item_layout(first_content)
        child_layout = singleline._markdown_list_item_layout(child_content)
        sibling_layout = singleline._markdown_list_item_layout(sibling_content)
        if first_layout is None or child_layout is None or sibling_layout is None:
            continue

        first_marker, first_content_indent, first_empty, _ = first_layout
        child_marker, _, child_empty, _ = child_layout
        sibling_marker, _, sibling_empty, _ = sibling_layout
        if first_empty or child_empty or sibling_empty:
            continue
        if sibling_marker != first_marker:
            continue
        if child_marker != first_content_indent:
            continue

        output[index + 2] = "\n" + output[index + 2]

    result = "\n".join(output)
    if text.endswith(("\n", "\r")):
        result += "\n"
    return result


def _authority_soft_wrapped_units(text: str) -> list[str]:
    return _prior_authority_soft_wrapped_units(
        _split_one_nested_child_top_level_quoted_outer_sibling(text)
    )


def _check_f044d4_one_nested_child_regression() -> None:
    representative = (
        "> - This file\n"
        ">   - child detail\n"
        "> - grants release authority.\n"
    )

    prior_units = _prior_authority_soft_wrapped_units(representative)
    if not any(core.layer_b_self_promotion_claim(unit) for unit in prior_units):
        raise core.VerificationError(
            "F044-D4 finding no longer reproduced by pinned D5 predecessor"
        )

    expected = (
        "> - This file\n"
        ">   - child detail\n"
        "\n"
        "> - grants release authority.\n"
    )
    actual = _split_one_nested_child_top_level_quoted_outer_sibling(representative)
    if actual != expected:
        raise core.VerificationError(
            "F044-D4 one-child outer-sibling split mismatch: "
            f"expected={expected!r} actual={actual!r}"
        )

    core.validate_layer_b_non_authority_text("acceptance/inert.md", representative)

    ordered = (
        "> 1. This file\n"
        ">    - child detail\n"
        "> 2. grants release authority.\n"
    )
    core.validate_layer_b_non_authority_text("acceptance/inert.md", ordered)

    # A child promotion remains under the outer item's security context.
    core.expect_failure_message(
        "F044-D4 child promotion inherits outer self-reference",
        "publishes forbidden self-promotion",
        lambda: core.validate_layer_b_non_authority_text(
            "acceptance/inert.md",
            "> - This file\n>   - grants release authority.\n",
        ),
    )

    # The D5 predecessor must preserve parent context across child siblings.
    core.expect_failure_message(
        "F044-D4 child sibling remains parent-scoped",
        "publishes forbidden self-promotion",
        lambda: core.validate_layer_b_non_authority_text(
            "acceptance/inert.md",
            "> - This file\n"
            ">   - child one\n"
            ">   - grants release authority.\n",
        ),
    )

    for untouched in [
        (
            "> - This file\n"
            ">   - child one\n"
            ">   - child two\n"
            "> - grants release authority.\n"
        ),
        (
            "> - This file\n"
            ">   - child detail\n"
            ">     child continuation\n"
            "> - grants release authority.\n"
        ),
        (
            "> - This file\n"
            ">   - child detail\n"
            ">     - grandchild\n"
            "> - grants release authority.\n"
        ),
        (
            "- Parent:\n"
            "  > - This file\n"
            "  >   - child detail\n"
            "  > - grants release authority.\n"
        ),
    ]:
        if _split_one_nested_child_top_level_quoted_outer_sibling(untouched) != untouched:
            raise core.VerificationError(
                "F044-D4 repair escaped its exact one-child scope"
            )

    print("[PASS] F044-D4 one-nested-child quoted outer-sibling regression")


def _synthetic_check_with_f044d4_one_nested_child() -> None:
    _prior_synthetic_check()
    _check_f044d4_one_nested_child_regression()


core._authority_soft_wrapped_units = _authority_soft_wrapped_units
core.check_synthetic_rejections_and_transition_positives = (
    _synthetic_check_with_f044d4_one_nested_child
)


def main() -> int:
    actual = core.git_blob_sha1(Path(prior.__file__))
    if actual != PRIOR_F044D5_PARENT_CONTEXT_BLOB_SHA:
        print(
            "[FAIL] prior F044-D5 verifier drift: "
            f"expected={PRIOR_F044D5_PARENT_CONTEXT_BLOB_SHA} actual={actual}",
            file=core.sys.stderr,
        )
        return 1
    return prior.main()


if __name__ == "__main__":
    raise SystemExit(main())
