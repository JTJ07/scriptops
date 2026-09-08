#!/usr/bin/env python3
"""Bounded F044-D26 list-owned post-target-child-continuation overlay.

The repaired F044-D25 verifier is retained byte-for-byte at
`scripts/verify_repository_f044d25_list_owned_post_target_cardinality.py` and
pinned by Git blob SHA. D26 lifts exactly the already-repaired D15 shape into
the existing source-column-zero outer-list-owned quote family: a quoted parent
list item, at least two one-line preceding children, one target child at
position three or later with one-or-more ordinary continuation lines, exactly
one post-target child at the same child-marker indentation with its own run of
one-or-more ordinary continuation lines, and exactly one final sibling.

Marker-only post-target cardinality remains delegated to D25. Continuation in
preceding/final children, more post-target children, multiple final siblings,
deeper nesting, block transitions, multiple quoted parents, outer-list
siblings, nested outer lists and further list-owned quote recursion remain
outside this patch.
"""
from __future__ import annotations

from pathlib import Path
import verify_repository_f044d25_list_owned_post_target_cardinality as prior

PRIOR_F044D25_BLOB_SHA = "df2f7dcc4e2a8406c7c6b8dbae81c30676979849"

core = prior.core
singleline = prior.singleline
_prior_authority_soft_wrapped_units = core._authority_soft_wrapped_units
_prior_synthetic_check = core.check_synthetic_rejections_and_transition_positives


def _collect_quote_owned_ordinary_run(
    lines: list[str],
    start: int,
    quote_indent: int,
    owner_content_indent: int,
) -> tuple[list[int], int]:
    indexes: list[int] = []
    probe = start
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
            content, owner_content_indent
        )
        if (
            relative is None
            or not relative.strip()
            or not singleline._markdown_block_quote_lazy_paragraph(relative)
        ):
            break
        indexes.append(probe)
        probe += 1
    return indexes, probe


def _split_list_owned_post_target_child_continuation(text: str) -> str:
    """Normalize target+run -> post-target+run -> exactly one final sibling."""
    lines = text.splitlines()
    output: list[str] = []
    index = 0

    while index < len(lines):
        if index + 8 >= len(lines):
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
            if layout is None or layout[2] or layout[0] != parent_content_indent:
                break
            child_indexes.append(probe)
            child_content_indents.append(layout[1])
            probe += 1

        if len(child_indexes) < 3 or probe >= len(lines) or not lines[probe].strip():
            output.append(lines[index]); index += 1; continue

        target_index = child_indexes[-1]
        target_run, probe = _collect_quote_owned_ordinary_run(
            lines, probe, quote_indent, child_content_indents[-1]
        )
        if not target_run or probe >= len(lines) or not lines[probe].strip():
            output.append(lines[index]); index += 1; continue

        post_quote = singleline._markdown_block_quote_layout(
            lines[probe], allow_deep_indent=True
        )
        post_layout = (
            singleline._markdown_list_item_layout(
                post_quote[1], allow_deep_indent=True
            )
            if post_quote is not None and post_quote[0] == quote_indent
            else None
        )
        if (
            post_layout is None
            or post_layout[2]
            or post_layout[0] != parent_content_indent
        ):
            output.append(lines[index]); index += 1; continue

        post_index = probe
        post_run, probe = _collect_quote_owned_ordinary_run(
            lines, post_index + 1, quote_indent, post_layout[1]
        )
        if not post_run or probe >= len(lines) or not lines[probe].strip():
            output.append(lines[index]); index += 1; continue

        final_quote = singleline._markdown_block_quote_layout(
            lines[probe], allow_deep_indent=True
        )
        final_layout = (
            singleline._markdown_list_item_layout(
                final_quote[1], allow_deep_indent=True
            )
            if final_quote is not None and final_quote[0] == quote_indent
            else None
        )
        if (
            final_layout is None
            or final_layout[2]
            or final_layout[0] != parent_content_indent
        ):
            output.append(lines[index]); index += 1; continue

        final_index = probe
        bounded_after = final_index + 1 == len(lines) or not lines[final_index + 1].strip()
        if not bounded_after:
            output.append(lines[index]); index += 1; continue

        for child_index in child_indexes[:-1]:
            output.extend([outer_raw, quote_parent_raw, lines[child_index]])
            output.append("")

        output.extend([outer_raw, quote_parent_raw, lines[target_index]])
        output.extend(lines[pos] for pos in target_run)
        output.append("")
        output.extend([outer_raw, quote_parent_raw, lines[post_index]])
        output.extend(lines[pos] for pos in post_run)
        output.append("")
        output.extend([outer_raw, quote_parent_raw, lines[final_index]])
        index = final_index + 1

    result = "\n".join(output)
    if text.endswith(("\n", "\r")):
        result += "\n"
    return result


def _authority_soft_wrapped_units(text: str) -> list[str]:
    return _prior_authority_soft_wrapped_units(
        _split_list_owned_post_target_child_continuation(text)
    )


def _check_f044d26_list_owned_post_target_continuation_regression() -> None:
    representative = (
        "- Parent:\n"
        "  > - neutral quoted parent\n"
        "  >   - child one\n"
        "  >   - child two\n"
        "  >   - This file\n"
        "  >     target continuation\n"
        "  >   - neutral post-target\n"
        "  >     post-target continuation\n"
        "  >   - grants release authority.\n"
    )
    prior_units = _prior_authority_soft_wrapped_units(representative)
    if not any(core.layer_b_self_promotion_claim(unit) for unit in prior_units):
        raise core.VerificationError(
            "F044-D26 predecessor no longer reproduces list-owned post-target-continuation finding"
        )
    core.validate_layer_b_non_authority_text("acceptance/inert.md", representative)

    # Existing run-length and target-position dimensions remain valid here.
    core.validate_layer_b_non_authority_text(
        "acceptance/inert.md",
        "- Parent:\n"
        "  > - neutral quoted parent\n"
        "  >   - child one\n"
        "  >   - child two\n"
        "  >   - child three\n"
        "  >   - This file\n"
        "  >     target one\n"
        "  >     target two\n"
        "  >   - neutral post-target\n"
        "  >     post one\n"
        "  >     post two\n"
        "  >   - grants release authority.\n",
    )

    core.expect_failure_message(
        "F044-D26 final sibling inherits outer-list self-reference",
        "publishes forbidden self-promotion",
        lambda: core.validate_layer_b_non_authority_text(
            "acceptance/inert.md",
            "- This file\n"
            "  > - neutral quoted parent\n"
            "  >   - child one\n"
            "  >   - child two\n"
            "  >   - neutral target\n"
            "  >     target continuation\n"
            "  >   - neutral post-target\n"
            "  >     post-target continuation\n"
            "  >   - grants release authority.\n",
        ),
    )
    core.expect_failure_message(
        "F044-D26 final sibling inherits quoted-parent self-reference",
        "publishes forbidden self-promotion",
        lambda: core.validate_layer_b_non_authority_text(
            "acceptance/inert.md",
            "- neutral outer\n"
            "  > - This file\n"
            "  >   - child one\n"
            "  >   - child two\n"
            "  >   - neutral target\n"
            "  >     target continuation\n"
            "  >   - neutral post-target\n"
            "  >     post-target continuation\n"
            "  >   - grants release authority.\n",
        ),
    )

    # Self-reference local to post-target child must not leak into final sibling.
    core.validate_layer_b_non_authority_text(
        "acceptance/inert.md",
        "- neutral outer\n"
        "  > - neutral quoted parent\n"
        "  >   - child one\n"
        "  >   - child two\n"
        "  >   - neutral target\n"
        "  >     target continuation\n"
        "  >   - This file\n"
        "  >     post-target continuation\n"
        "  >   - grants release authority.\n",
    )

    # Marker-only post-target siblings remain delegated to D25.
    delegated_d25 = (
        "- Parent:\n"
        "  > - neutral quoted parent\n"
        "  >   - child one\n"
        "  >   - child two\n"
        "  >   - This file\n"
        "  >     target continuation\n"
        "  >   - grants release authority.\n"
        "  >   - neutral later sibling\n"
    )
    if _split_list_owned_post_target_child_continuation(delegated_d25) != delegated_d25:
        raise core.VerificationError("F044-D26 escaped into D25 marker-only scope")
    core.validate_layer_b_non_authority_text("acceptance/inert.md", delegated_d25)

    for untouched in [
        (
            "- Parent:\n"
            "  > - neutral quoted parent\n"
            "  >   - child one\n"
            "  >     preceding continuation\n"
            "  >   - child two\n"
            "  >   - This file\n"
            "  >     target continuation\n"
            "  >   - neutral post-target\n"
            "  >     post-target continuation\n"
            "  >   - grants release authority.\n"
        ),
        (
            "- Parent:\n"
            "  > - neutral quoted parent\n"
            "  >   - child one\n"
            "  >   - child two\n"
            "  >   - This file\n"
            "  >     target continuation\n"
            "  >   - neutral post-target one\n"
            "  >     post-target continuation\n"
            "  >   - neutral post-target two\n"
            "  >   - grants release authority.\n"
        ),
        (
            "- Parent:\n"
            "  > - neutral quoted parent\n"
            "  >   - child one\n"
            "  >   - child two\n"
            "  >   - This file\n"
            "  >     target continuation\n"
            "  >   - neutral post-target\n"
            "  >     - grandchild\n"
            "  >   - grants release authority.\n"
        ),
        (
            "- Parent:\n"
            "  > - neutral quoted parent\n"
            "  >   - child one\n"
            "  >   - child two\n"
            "  >   - This file\n"
            "  >     target continuation\n"
            "  >   - neutral post-target\n"
            "  >     post-target continuation\n"
            "  >   - grants release authority.\n"
            "  >   - extra final sibling\n"
        ),
        (
            "- Parent:\n"
            "  > - neutral quoted parent\n"
            "  >   - child one\n"
            "  >   - child two\n"
            "  >   - This file\n"
            "  >     target continuation\n"
            "  >   - neutral post-target\n"
            "  >     post-target continuation\n"
            "  >   - grants release authority.\n"
            "- outer sibling\n"
        ),
        (
            "  - nested outer\n"
            "    > - neutral quoted parent\n"
            "    >   - child one\n"
            "    >   - child two\n"
            "    >   - This file\n"
            "    >     target continuation\n"
            "    >   - neutral post-target\n"
            "    >     post-target continuation\n"
            "    >   - grants release authority.\n"
        ),
    ]:
        if _split_list_owned_post_target_child_continuation(untouched) != untouched:
            raise core.VerificationError("F044-D26 repair escaped bounded list-owned D15 scope")

    print("[PASS] F044-D26 list-owned post-target-child continuation regression")


def _synthetic_check_with_f044d26() -> None:
    _prior_synthetic_check()
    _check_f044d26_list_owned_post_target_continuation_regression()


core._authority_soft_wrapped_units = _authority_soft_wrapped_units
core.check_synthetic_rejections_and_transition_positives = _synthetic_check_with_f044d26


def main() -> int:
    actual = core.git_blob_sha1(Path(prior.__file__))
    if actual != PRIOR_F044D25_BLOB_SHA:
        print(
            "[FAIL] prior F044-D25 verifier drift: "
            f"expected={PRIOR_F044D25_BLOB_SHA} actual={actual}",
            file=core.sys.stderr,
        )
        return 1
    return prior.main()


if __name__ == "__main__":
    raise SystemExit(main())
