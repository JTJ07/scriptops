#!/usr/bin/env python3
"""Bounded F044-D14 post-target sibling-cardinality overlay.

The repaired F044-D13 verifier is retained byte-for-byte at
`scripts/verify_repository_f044d13_later_child_position.py` and pinned by Git
blob SHA. D13 establishes target-child positions three and later when exactly
one sibling follows the target continuation run. The D14 adjacent probe shows
the same continuation-to-sibling root cause when a second post-target sibling
is present. This entrypoint generalizes only that post-target sibling-cardinality
dimension.

Scope: one nonempty source-column-zero quoted outer list item; at least two
consecutive one-line child siblings at the outer content indentation; then one
nonempty target child at that same indentation; a run of one or more ordinary
continuation lines owned by the target child; then a bounded run of at least two
consecutive nonempty post-target sibling markers at the same child-marker
indentation. BOF/blank bounds the fragment before and EOF/blank bounds it after.

Each preceding child, the target child plus its continuation run, and every
post-target sibling are separate authority units. The same outer parent is
repeated into every unit. Exactly one post-target sibling remains delegated to
D13. Continuation in preceding/post-target children, deeper nesting, block
transitions, outer-sibling transitions and list-owned outer quote recursion
remain outside this repair.
"""
from __future__ import annotations

from pathlib import Path
import verify_repository_f044d13_later_child_position as prior

PRIOR_F044D13_LATER_CHILD_POSITION_BLOB_SHA = (
    "35f8fa0fa4004f00c57f1dc8e9d9432819022a84"
)

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


def _split_post_target_sibling_cardinality(text: str) -> str:
    """Normalize >=2 preceding children -> target+run -> >=2 later siblings."""
    lines = text.splitlines()
    output: list[str] = []
    index = 0

    while index < len(lines):
        bounded_before = index == 0 or not lines[index - 1].strip()
        parent_content = _top_level_quote_content(lines[index])
        parent_layout = (
            singleline._markdown_list_item_layout(parent_content)
            if parent_content is not None
            else None
        )
        if not bounded_before or parent_layout is None or parent_layout[2]:
            output.append(lines[index])
            index += 1
            continue

        _, parent_content_indent, _, _ = parent_layout
        child_indexes: list[int] = []
        child_content_indents: list[int] = []
        probe = index + 1

        # Collect consecutive one-line child markers before the target's
        # continuation begins. The last collected child is the target.
        while probe < len(lines) and lines[probe].strip():
            content = _top_level_quote_content(lines[probe])
            layout = (
                singleline._markdown_list_item_layout(
                    content,
                    allow_deep_indent=True,
                )
                if content is not None
                else None
            )
            if (
                layout is None
                or layout[2]
                or layout[0] != parent_content_indent
            ):
                break
            child_indexes.append(probe)
            child_content_indents.append(layout[1])
            probe += 1

        if len(child_indexes) < 3 or probe >= len(lines) or not lines[probe].strip():
            output.append(lines[index])
            index += 1
            continue

        target_index = child_indexes[-1]
        target_content_indent = child_content_indents[-1]
        continuation_indexes: list[int] = []

        while probe < len(lines) and lines[probe].strip():
            content = _top_level_quote_content(lines[probe])
            if content is None:
                break

            any_list = singleline._markdown_list_item_layout(
                content,
                allow_deep_indent=True,
            )
            if any_list is not None:
                break

            relative = singleline._markdown_remove_leading_columns(
                content,
                target_content_indent,
            )
            if (
                relative is None
                or not relative.strip()
                or not singleline._markdown_block_quote_lazy_paragraph(relative)
            ):
                break

            continuation_indexes.append(probe)
            probe += 1

        if not continuation_indexes:
            output.append(lines[index])
            index += 1
            continue

        post_target_indexes: list[int] = []
        while probe < len(lines) and lines[probe].strip():
            content = _top_level_quote_content(lines[probe])
            layout = (
                singleline._markdown_list_item_layout(
                    content,
                    allow_deep_indent=True,
                )
                if content is not None
                else None
            )
            if (
                layout is None
                or layout[2]
                or layout[0] != parent_content_indent
            ):
                break
            post_target_indexes.append(probe)
            probe += 1

        bounded_after = probe == len(lines) or not lines[probe].strip()
        if len(post_target_indexes) < 2 or not bounded_after:
            output.append(lines[index])
            index += 1
            continue

        for child_index in child_indexes[:-1]:
            output.extend([lines[index], lines[child_index]])
            output.append("")

        output.extend([lines[index], lines[target_index]])
        output.extend(lines[pos] for pos in continuation_indexes)
        for sibling_index in post_target_indexes:
            output.append("")
            output.extend([lines[index], lines[sibling_index]])
        index = probe

    result = "\n".join(output)
    if text.endswith(("\n", "\r")):
        result += "\n"
    return result


def _authority_soft_wrapped_units(text: str) -> list[str]:
    return _prior_authority_soft_wrapped_units(
        _split_post_target_sibling_cardinality(text)
    )


def _check_f044d14_post_target_cardinality_regression() -> None:
    representative = (
        "> - neutral parent\n"
        ">   - child one\n"
        ">   - child two\n"
        ">   - This file\n"
        ">     target continuation\n"
        ">   - grants release authority.\n"
        ">   - neutral later sibling\n"
    )

    prior_units = _prior_authority_soft_wrapped_units(representative)
    if not any(core.layer_b_self_promotion_claim(unit) for unit in prior_units):
        raise core.VerificationError(
            "F044-D14 predecessor no longer reproduces post-target cardinality finding"
        )

    expected = (
        "> - neutral parent\n"
        ">   - child one\n"
        "\n"
        "> - neutral parent\n"
        ">   - child two\n"
        "\n"
        "> - neutral parent\n"
        ">   - This file\n"
        ">     target continuation\n"
        "\n"
        "> - neutral parent\n"
        ">   - grants release authority.\n"
        "\n"
        "> - neutral parent\n"
        ">   - neutral later sibling\n"
    )
    actual = _split_post_target_sibling_cardinality(representative)
    if actual != expected:
        raise core.VerificationError(
            "F044-D14 post-target cardinality normalization mismatch: "
            f"expected={expected!r} actual={actual!r}"
        )

    core.validate_layer_b_non_authority_text("acceptance/inert.md", representative)

    # Three post-target siblings are the same cardinality dimension.
    core.validate_layer_b_non_authority_text(
        "acceptance/inert.md",
        "> - neutral parent\n"
        ">   - child one\n"
        ">   - child two\n"
        ">   - This file\n"
        ">     target continuation\n"
        ">   - grants release authority.\n"
        ">   - neutral sibling five\n"
        ">   - neutral sibling six\n",
    )

    # A later target position remains the D13-proven position dimension while
    # post-target cardinality is varied here.
    core.validate_layer_b_non_authority_text(
        "acceptance/inert.md",
        "> - neutral parent\n"
        ">   - child one\n"
        ">   - child two\n"
        ">   - child three\n"
        ">   - This file\n"
        ">     target continuation\n"
        ">   - grants release authority.\n"
        ">   - neutral later sibling\n",
    )

    # Outer parent context reaches every post-target sibling, including the last.
    core.expect_failure_message(
        "F044-D14 last post-target sibling inherits outer self-reference",
        "publishes forbidden self-promotion",
        lambda: core.validate_layer_b_non_authority_text(
            "acceptance/inert.md",
            "> - This file\n"
            ">   - child one\n"
            ">   - child two\n"
            ">   - target child\n"
            ">     target continuation\n"
            ">   - neutral post-target sibling\n"
            ">   - grants release authority.\n",
        ),
    )

    # Target-local self-reference cannot leak to any post-target sibling when
    # the outer parent is neutral.
    core.validate_layer_b_non_authority_text(
        "acceptance/inert.md",
        "> - neutral parent\n"
        ">   - child one\n"
        ">   - child two\n"
        ">   - This file\n"
        ">     target continuation\n"
        ">   - neutral post-target sibling\n"
        ">   - grants release authority.\n",
    )

    # Exactly one post-target sibling remains delegated to D13; D14 itself must
    # not rewrite that shape.
    delegated_one = (
        "> - neutral parent\n"
        ">   - child one\n"
        ">   - child two\n"
        ">   - This file\n"
        ">     target continuation\n"
        ">   - grants release authority.\n"
    )
    if _split_post_target_sibling_cardinality(delegated_one) != delegated_one:
        raise core.VerificationError(
            "F044-D14 cardinality generalizer escaped into D13 one-sibling scope"
        )
    core.validate_layer_b_non_authority_text("acceptance/inert.md", delegated_one)

    # Adjacent families remain outside this cardinality-only repair.
    for untouched in [
        (
            "> - neutral parent\n"
            ">   - child one\n"
            ">     preceding continuation\n"
            ">   - child two\n"
            ">   - This file\n"
            ">     target continuation\n"
            ">   - child four\n"
            ">   - child five\n"
        ),
        (
            "> - neutral parent\n"
            ">   - child one\n"
            ">   - child two\n"
            ">   - This file\n"
            ">     target continuation\n"
            ">   - child four\n"
            ">     child four continuation\n"
            ">   - grants release authority.\n"
        ),
        (
            "> - neutral parent\n"
            ">   - child one\n"
            ">   - child two\n"
            ">   - This file\n"
            ">     - grandchild\n"
            ">   - child four\n"
            ">   - child five\n"
        ),
        (
            "> - neutral parent\n"
            ">   - child one\n"
            ">   - child two\n"
            ">   - This file\n"
            ">     target continuation\n"
            ">   - child four\n"
            ">   - child five\n"
            "> - outer sibling\n"
        ),
        (
            "- Parent:\n"
            "  > - neutral parent\n"
            "  >   - child one\n"
            "  >   - child two\n"
            "  >   - This file\n"
            "  >     target continuation\n"
            "  >   - child four\n"
            "  >   - child five\n"
        ),
    ]:
        if _split_post_target_sibling_cardinality(untouched) != untouched:
            raise core.VerificationError(
                "F044-D14 repair escaped its bounded post-target-cardinality scope"
            )

    print("[PASS] F044-D14 post-target sibling-cardinality regression")


def _synthetic_check_with_f044d14_post_target_cardinality() -> None:
    _prior_synthetic_check()
    _check_f044d14_post_target_cardinality_regression()


core._authority_soft_wrapped_units = _authority_soft_wrapped_units
core.check_synthetic_rejections_and_transition_positives = (
    _synthetic_check_with_f044d14_post_target_cardinality
)


def main() -> int:
    actual = core.git_blob_sha1(Path(prior.__file__))
    if actual != PRIOR_F044D13_LATER_CHILD_POSITION_BLOB_SHA:
        print(
            "[FAIL] prior F044-D13 verifier drift: "
            f"expected={PRIOR_F044D13_LATER_CHILD_POSITION_BLOB_SHA} actual={actual}",
            file=core.sys.stderr,
        )
        return 1
    return prior.main()


if __name__ == "__main__":
    raise SystemExit(main())
