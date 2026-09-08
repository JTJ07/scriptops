#!/usr/bin/env python3
"""Bounded F044-D25 list-owned post-target sibling-cardinality overlay.

The repaired F044-D24 verifier is retained byte-for-byte at
`scripts/verify_repository_f044d24_list_owned_later_child_position.py` and
pinned by Git blob SHA. D25 lifts exactly the already-repaired D14
post-target-cardinality dimension into the existing source-column-zero
outer-list-owned quote family: a quoted parent list item, at least two one-line
preceding children, one target child at position three or later with one-or-more
ordinary continuation lines, and a bounded run of at least two consecutive
post-target siblings at the same child-marker indentation.

Exactly one post-target sibling remains delegated to D24. Child-two target
continuation remains delegated to D23. Continuation in preceding/post-target
children, deeper nesting, block transitions, multiple quoted parents,
outer-list siblings, nested outer lists and further list-owned quote recursion
remain outside this patch.
"""
from __future__ import annotations

from pathlib import Path
import verify_repository_f044d24_list_owned_later_child_position as prior

PRIOR_F044D24_BLOB_SHA = "e3062750190721451548f241a8ae91acad6e6770"

core = prior.core
singleline = prior.singleline
_prior_authority_soft_wrapped_units = core._authority_soft_wrapped_units
_prior_synthetic_check = core.check_synthetic_rejections_and_transition_positives


def _split_list_owned_post_target_cardinality(text: str) -> str:
    """Normalize outer-list -> quote parent -> target+run -> >=2 later siblings."""
    lines = text.splitlines()
    output: list[str] = []
    index = 0

    while index < len(lines):
        if index + 7 >= len(lines):
            output.append(lines[index])
            index += 1
            continue
        if index != 0 and lines[index - 1].strip():
            output.append(lines[index])
            index += 1
            continue

        outer_raw = lines[index]
        quote_parent_raw = lines[index + 1]

        outer_layout = singleline._markdown_list_item_layout(outer_raw)
        if outer_layout is None:
            output.append(lines[index]); index += 1; continue
        outer_marker, outer_content_indent, outer_empty, _ = outer_layout
        if outer_empty or outer_marker != 0:
            output.append(lines[index]); index += 1; continue

        quote_parent = singleline._markdown_block_quote_layout(
            quote_parent_raw, allow_deep_indent=True
        )
        if quote_parent is None or quote_parent[0] != outer_content_indent:
            output.append(lines[index]); index += 1; continue

        quote_indent, quote_parent_content = quote_parent
        parent_list = singleline._markdown_list_item_layout(quote_parent_content)
        if parent_list is None or parent_list[2] or parent_list[0] != 0:
            output.append(lines[index]); index += 1; continue
        _, parent_content_indent, _, _ = parent_list

        child_indexes: list[int] = []
        child_content_indents: list[int] = []
        probe = index + 2
        while probe < len(lines) and lines[probe].strip():
            qlayout = singleline._markdown_block_quote_layout(
                lines[probe], allow_deep_indent=True
            )
            if qlayout is None or qlayout[0] != quote_indent:
                break
            layout = singleline._markdown_list_item_layout(
                qlayout[1], allow_deep_indent=True
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
            output.append(lines[index]); index += 1; continue

        target_index = child_indexes[-1]
        target_content_indent = child_content_indents[-1]
        continuation_indexes: list[int] = []

        while probe < len(lines) and lines[probe].strip():
            qlayout = singleline._markdown_block_quote_layout(
                lines[probe], allow_deep_indent=True
            )
            if qlayout is None or qlayout[0] != quote_indent:
                break
            content = qlayout[1]

            if singleline._markdown_list_item_layout(
                content, allow_deep_indent=True
            ) is not None:
                break

            relative = singleline._markdown_remove_leading_columns(
                content, target_content_indent
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
            output.append(lines[index]); index += 1; continue

        post_target_indexes: list[int] = []
        while probe < len(lines) and lines[probe].strip():
            qlayout = singleline._markdown_block_quote_layout(
                lines[probe], allow_deep_indent=True
            )
            if qlayout is None or qlayout[0] != quote_indent:
                break
            layout = singleline._markdown_list_item_layout(
                qlayout[1], allow_deep_indent=True
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
            output.append(lines[index]); index += 1; continue

        for child_index in child_indexes[:-1]:
            output.extend([outer_raw, quote_parent_raw, lines[child_index]])
            output.append("")

        output.extend([outer_raw, quote_parent_raw, lines[target_index]])
        output.extend(lines[pos] for pos in continuation_indexes)
        for sibling_index in post_target_indexes:
            output.append("")
            output.extend([outer_raw, quote_parent_raw, lines[sibling_index]])
        index = probe

    result = "\n".join(output)
    if text.endswith(("\n", "\r")):
        result += "\n"
    return result


def _authority_soft_wrapped_units(text: str) -> list[str]:
    return _prior_authority_soft_wrapped_units(
        _split_list_owned_post_target_cardinality(text)
    )


def _check_f044d25_list_owned_post_target_cardinality_regression() -> None:
    representative = (
        "- Parent:\n"
        "  > - neutral quoted parent\n"
        "  >   - child one\n"
        "  >   - child two\n"
        "  >   - This file\n"
        "  >     target continuation\n"
        "  >   - grants release authority.\n"
        "  >   - neutral later sibling\n"
    )
    prior_units = _prior_authority_soft_wrapped_units(representative)
    if not any(core.layer_b_self_promotion_claim(unit) for unit in prior_units):
        raise core.VerificationError(
            "F044-D25 predecessor no longer reproduces list-owned post-target-cardinality finding"
        )
    core.validate_layer_b_non_authority_text("acceptance/inert.md", representative)

    # Three post-target siblings are the same D14 cardinality dimension.
    core.validate_layer_b_non_authority_text(
        "acceptance/inert.md",
        "- Parent:\n"
        "  > - neutral quoted parent\n"
        "  >   - child one\n"
        "  >   - child two\n"
        "  >   - This file\n"
        "  >     target continuation\n"
        "  >   - grants release authority.\n"
        "  >   - neutral sibling five\n"
        "  >   - neutral sibling six\n",
    )

    # Later target position and longer continuation remain proven dimensions.
    core.validate_layer_b_non_authority_text(
        "acceptance/inert.md",
        "- Parent:\n"
        "  > - neutral quoted parent\n"
        "  >   - child one\n"
        "  >   - child two\n"
        "  >   - child three\n"
        "  >   - This file\n"
        "  >     continuation one\n"
        "  >     continuation two\n"
        "  >   - grants release authority.\n"
        "  >   - neutral later sibling\n",
    )

    core.expect_failure_message(
        "F044-D25 last post-target sibling inherits outer-list self-reference",
        "publishes forbidden self-promotion",
        lambda: core.validate_layer_b_non_authority_text(
            "acceptance/inert.md",
            "- This file\n"
            "  > - neutral quoted parent\n"
            "  >   - child one\n"
            "  >   - child two\n"
            "  >   - target child\n"
            "  >     target continuation\n"
            "  >   - neutral post-target sibling\n"
            "  >   - grants release authority.\n",
        ),
    )
    core.expect_failure_message(
        "F044-D25 last post-target sibling inherits quoted-parent self-reference",
        "publishes forbidden self-promotion",
        lambda: core.validate_layer_b_non_authority_text(
            "acceptance/inert.md",
            "- neutral outer\n"
            "  > - This file\n"
            "  >   - child one\n"
            "  >   - child two\n"
            "  >   - target child\n"
            "  >     target continuation\n"
            "  >   - neutral post-target sibling\n"
            "  >   - grants release authority.\n",
        ),
    )

    # Target-local self-reference must not leak into post-target siblings.
    core.validate_layer_b_non_authority_text(
        "acceptance/inert.md",
        "- neutral outer\n"
        "  > - neutral quoted parent\n"
        "  >   - child one\n"
        "  >   - child two\n"
        "  >   - This file\n"
        "  >     target continuation\n"
        "  >   - neutral post-target sibling\n"
        "  >   - grants release authority.\n",
    )

    # Exactly one post-target sibling remains delegated to D24.
    delegated_d24 = (
        "- Parent:\n"
        "  > - neutral quoted parent\n"
        "  >   - child one\n"
        "  >   - child two\n"
        "  >   - This file\n"
        "  >     target continuation\n"
        "  >   - grants release authority.\n"
    )
    if _split_list_owned_post_target_cardinality(delegated_d24) != delegated_d24:
        raise core.VerificationError("F044-D25 escaped into D24 one-sibling scope")
    core.validate_layer_b_non_authority_text("acceptance/inert.md", delegated_d24)

    # Adjacent families remain explicitly outside this cardinality-only lift.
    for untouched in [
        (
            "- Parent:\n"
            "  > - neutral quoted parent\n"
            "  >   - child one\n"
            "  >     preceding continuation\n"
            "  >   - child two\n"
            "  >   - This file\n"
            "  >     target continuation\n"
            "  >   - child four\n"
            "  >   - child five\n"
        ),
        (
            "- Parent:\n"
            "  > - neutral quoted parent\n"
            "  >   - child one\n"
            "  >   - child two\n"
            "  >   - This file\n"
            "  >     target continuation\n"
            "  >   - child four\n"
            "  >     child four continuation\n"
            "  >   - grants release authority.\n"
        ),
        (
            "- Parent:\n"
            "  > - neutral quoted parent\n"
            "  >   - child one\n"
            "  >   - child two\n"
            "  >   - This file\n"
            "  >     - grandchild\n"
            "  >   - child four\n"
            "  >   - child five\n"
        ),
        (
            "- Parent:\n"
            "  > - neutral quoted parent\n"
            "  >   - child one\n"
            "  >   - child two\n"
            "  >   - This file\n"
            "  >     target continuation\n"
            "  >   - child four\n"
            "  >   - child five\n"
            "- outer sibling\n"
        ),
        (
            "  - nested outer\n"
            "    > - neutral quoted parent\n"
            "    >   - child one\n"
            "    >   - child two\n"
            "    >   - This file\n"
            "    >     target continuation\n"
            "    >   - child four\n"
            "    >   - child five\n"
        ),
    ]:
        if _split_list_owned_post_target_cardinality(untouched) != untouched:
            raise core.VerificationError("F044-D25 repair escaped bounded list-owned D14 scope")

    print("[PASS] F044-D25 list-owned post-target sibling-cardinality regression")


def _synthetic_check_with_f044d25() -> None:
    _prior_synthetic_check()
    _check_f044d25_list_owned_post_target_cardinality_regression()


core._authority_soft_wrapped_units = _authority_soft_wrapped_units
core.check_synthetic_rejections_and_transition_positives = _synthetic_check_with_f044d25


def main() -> int:
    actual = core.git_blob_sha1(Path(prior.__file__))
    if actual != PRIOR_F044D24_BLOB_SHA:
        print(
            "[FAIL] prior F044-D24 verifier drift: "
            f"expected={PRIOR_F044D24_BLOB_SHA} actual={actual}",
            file=core.sys.stderr,
        )
        return 1
    return prior.main()


if __name__ == "__main__":
    raise SystemExit(main())
