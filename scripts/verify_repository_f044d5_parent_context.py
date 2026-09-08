#!/usr/bin/env python3
"""Bounded F044-D5 two-child parent-context preservation overlay.

The repaired F044-D3 verifier is retained byte-for-byte at
`scripts/verify_repository_f044d3_continuation_run.py` and pinned by Git blob
SHA. This entrypoint repairs only one security shape: one nonempty outer quoted
list item with exactly two consecutive nonempty child sibling markers at the
outer content indentation, where that three-line list fragment is bounded by
BOF/blank before and EOF/blank after.

The two child siblings remain separate authority units, but the outer parent
line is repeated into the second unit so established parent-context inheritance
is preserved. Larger child runs, child continuation, deeper nesting and other
container families remain outside this repair.
"""
from __future__ import annotations

from pathlib import Path
import verify_repository_f044d3_continuation_run as prior

PRIOR_F044D3_CONTINUATION_RUN_BLOB_SHA = "943e5f741f51f2e89aa2ac0264f511f31ea842b3"

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


def _preserve_parent_for_exact_two_child_siblings(text: str) -> str:
    """Duplicate one bounded outer parent across exactly two child units."""
    lines = text.splitlines()
    output: list[str] = []
    index = 0

    while index < len(lines):
        if index + 2 >= len(lines):
            output.append(lines[index])
            index += 1
            continue

        bounded_before = index == 0 or not lines[index - 1].strip()
        bounded_after = index + 3 == len(lines) or not lines[index + 3].strip()
        if not bounded_before or not bounded_after:
            output.append(lines[index])
            index += 1
            continue

        parent_content = _top_level_quote_content(lines[index])
        child_one_content = _top_level_quote_content(lines[index + 1])
        child_two_content = _top_level_quote_content(lines[index + 2])
        if (
            parent_content is None
            or child_one_content is None
            or child_two_content is None
        ):
            output.append(lines[index])
            index += 1
            continue

        parent_layout = singleline._markdown_list_item_layout(parent_content)
        child_one_layout = singleline._markdown_list_item_layout(child_one_content)
        child_two_layout = singleline._markdown_list_item_layout(child_two_content)
        if parent_layout is None or child_one_layout is None or child_two_layout is None:
            output.append(lines[index])
            index += 1
            continue

        _, parent_content_indent, parent_empty, _ = parent_layout
        child_one_marker, _, child_one_empty, _ = child_one_layout
        child_two_marker, _, child_two_empty, _ = child_two_layout
        if (
            parent_empty
            or child_one_empty
            or child_two_empty
            or child_one_marker != parent_content_indent
            or child_two_marker != child_one_marker
        ):
            output.append(lines[index])
            index += 1
            continue

        output.extend(
            [
                lines[index],
                lines[index + 1],
                "",
                lines[index],
                lines[index + 2],
            ]
        )
        index += 3

    result = "\n".join(output)
    if text.endswith(("\n", "\r")):
        result += "\n"
    return result


def _authority_soft_wrapped_units(text: str) -> list[str]:
    return _prior_authority_soft_wrapped_units(
        _preserve_parent_for_exact_two_child_siblings(text)
    )


def _check_f044d5_child_parent_context_regression() -> None:
    representative = (
        "> - This file\n"
        ">   - child one\n"
        ">   - grants release authority.\n"
    )

    prior_units = _prior_authority_soft_wrapped_units(representative)
    if any(core.layer_b_self_promotion_claim(unit) for unit in prior_units):
        raise core.VerificationError(
            "F044-D5 predecessor no longer reproduces lost parent context"
        )

    expected = (
        "> - This file\n"
        ">   - child one\n"
        "\n"
        "> - This file\n"
        ">   - grants release authority.\n"
    )
    actual = _preserve_parent_for_exact_two_child_siblings(representative)
    if actual != expected:
        raise core.VerificationError(
            "F044-D5 parent-context normalization mismatch: "
            f"expected={expected!r} actual={actual!r}"
        )

    core.expect_failure_message(
        "F044-D5 second child inherits outer self-reference",
        "publishes forbidden self-promotion",
        lambda: core.validate_layer_b_non_authority_text(
            "acceptance/inert.md", representative
        ),
    )

    # Child siblings must remain separate: one child's self-reference cannot
    # donate context to the other when the outer parent is neutral.
    core.validate_layer_b_non_authority_text(
        "acceptance/inert.md",
        "> - neutral parent\n"
        ">   - This file\n"
        ">   - grants release authority.\n",
    )

    # A promotion in the first child already inherits the parent directly.
    core.expect_failure_message(
        "F044-D5 first child still inherits outer self-reference",
        "publishes forbidden self-promotion",
        lambda: core.validate_layer_b_non_authority_text(
            "acceptance/inert.md",
            "> - This file\n"
            ">   - grants release authority.\n"
            ">   - child two\n",
        ),
    )

    # Larger/adjacent families remain outside this exact bounded repair.
    for untouched in [
        (
            "> - This file\n"
            ">   - child one\n"
            ">   - child two\n"
            ">   - grants release authority.\n"
        ),
        (
            "> - This file\n"
            ">   - child one\n"
            ">     child continuation\n"
            ">   - grants release authority.\n"
        ),
        (
            "> - This file\n"
            ">   - child one\n"
            ">     - grandchild\n"
            ">   - grants release authority.\n"
        ),
        (
            "- Parent:\n"
            "  > - This file\n"
            "  >   - child one\n"
            "  >   - grants release authority.\n"
        ),
    ]:
        if _preserve_parent_for_exact_two_child_siblings(untouched) != untouched:
            raise core.VerificationError(
                "F044-D5 repair escaped its exact two-child bounded scope"
            )

    print("[PASS] F044-D5 two-child parent-context preservation regression")


def _synthetic_check_with_f044d5_parent_context() -> None:
    _prior_synthetic_check()
    _check_f044d5_child_parent_context_regression()


core._authority_soft_wrapped_units = _authority_soft_wrapped_units
core.check_synthetic_rejections_and_transition_positives = (
    _synthetic_check_with_f044d5_parent_context
)


def main() -> int:
    actual = core.git_blob_sha1(Path(prior.__file__))
    if actual != PRIOR_F044D3_CONTINUATION_RUN_BLOB_SHA:
        print(
            "[FAIL] prior F044-D3 verifier drift: "
            f"expected={PRIOR_F044D3_CONTINUATION_RUN_BLOB_SHA} actual={actual}",
            file=core.sys.stderr,
        )
        return 1
    return prior.main()


if __name__ == "__main__":
    raise SystemExit(main())
