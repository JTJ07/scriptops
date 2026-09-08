#!/usr/bin/env python3
"""Bounded F044-D15 post-target-child continuation overlay.

The repaired F044-D14 verifier is retained byte-for-byte at
`scripts/verify_repository_f044d14_post_target_cardinality.py` and pinned by
Git blob SHA. D14 covers consecutive marker-only post-target siblings. D15
shows the adjacent case where the first post-target sibling owns ordinary
continuation text before one final sibling. This entrypoint repairs only that
shape.

Scope: one nonempty source-column-zero quoted outer list item; at least two
consecutive one-line child siblings at the outer content indentation; then one
target child at that same indentation with a run of one or more ordinary
continuation lines; then exactly one nonempty post-target sibling at the same
indentation with its own run of one or more ordinary continuation lines; then
exactly one nonempty final sibling returning to the same child-marker
indentation. BOF/blank bounds before and EOF/blank bounds after.

Every preceding child, target+run, post-target child+run, and final sibling are
separate authority units; the outer parent is repeated into every unit.
Marker-only post-target cardinality remains delegated to D14. More post-target
children, multiple final siblings, deeper nesting, block transitions,
outer-sibling transitions and list-owned outer quote recursion remain outside.
"""
from __future__ import annotations

from pathlib import Path
import verify_repository_f044d14_post_target_cardinality as prior

PRIOR_F044D14_POST_TARGET_CARDINALITY_BLOB_SHA = (
    "a1b4f8666ec8915532b3e12addb3abdda549dd3f"
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


def _collect_ordinary_run(
    lines: list[str],
    start: int,
    owner_content_indent: int,
) -> tuple[list[int], int]:
    indexes: list[int] = []
    probe = start
    while probe < len(lines) and lines[probe].strip():
        content = _top_level_quote_content(lines[probe])
        if content is None:
            break
        if (
            singleline._markdown_list_item_layout(
                content,
                allow_deep_indent=True,
            )
            is not None
        ):
            break
        relative = singleline._markdown_remove_leading_columns(
            content,
            owner_content_indent,
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


def _split_post_target_child_continuation(text: str) -> str:
    """Normalize target+run -> post-target+run -> exactly one final sibling."""
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
        target_run, probe = _collect_ordinary_run(
            lines,
            probe,
            child_content_indents[-1],
        )
        if not target_run or probe >= len(lines) or not lines[probe].strip():
            output.append(lines[index])
            index += 1
            continue

        post_content = _top_level_quote_content(lines[probe])
        post_layout = (
            singleline._markdown_list_item_layout(
                post_content,
                allow_deep_indent=True,
            )
            if post_content is not None
            else None
        )
        if (
            post_layout is None
            or post_layout[2]
            or post_layout[0] != parent_content_indent
        ):
            output.append(lines[index])
            index += 1
            continue

        post_index = probe
        post_content_indent = post_layout[1]
        post_run, probe = _collect_ordinary_run(
            lines,
            post_index + 1,
            post_content_indent,
        )
        if not post_run or probe >= len(lines) or not lines[probe].strip():
            output.append(lines[index])
            index += 1
            continue

        final_content = _top_level_quote_content(lines[probe])
        final_layout = (
            singleline._markdown_list_item_layout(
                final_content,
                allow_deep_indent=True,
            )
            if final_content is not None
            else None
        )
        if (
            final_layout is None
            or final_layout[2]
            or final_layout[0] != parent_content_indent
        ):
            output.append(lines[index])
            index += 1
            continue

        final_index = probe
        bounded_after = final_index + 1 == len(lines) or not lines[final_index + 1].strip()
        if not bounded_after:
            output.append(lines[index])
            index += 1
            continue

        for child_index in child_indexes[:-1]:
            output.extend([lines[index], lines[child_index]])
            output.append("")

        output.extend([lines[index], lines[target_index]])
        output.extend(lines[pos] for pos in target_run)
        output.append("")
        output.extend([lines[index], lines[post_index]])
        output.extend(lines[pos] for pos in post_run)
        output.append("")
        output.extend([lines[index], lines[final_index]])
        index = final_index + 1

    result = "\n".join(output)
    if text.endswith(("\n", "\r")):
        result += "\n"
    return result


def _authority_soft_wrapped_units(text: str) -> list[str]:
    return _prior_authority_soft_wrapped_units(
        _split_post_target_child_continuation(text)
    )


def _check_f044d15_post_target_continuation_regression() -> None:
    representative = (
        "> - neutral parent\n"
        ">   - child one\n"
        ">   - child two\n"
        ">   - This file\n"
        ">     target continuation\n"
        ">   - neutral post-target\n"
        ">     post-target continuation\n"
        ">   - grants release authority.\n"
    )

    prior_units = _prior_authority_soft_wrapped_units(representative)
    if not any(core.layer_b_self_promotion_claim(unit) for unit in prior_units):
        raise core.VerificationError(
            "F044-D15 predecessor no longer reproduces post-target-continuation finding"
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
        ">   - neutral post-target\n"
        ">     post-target continuation\n"
        "\n"
        "> - neutral parent\n"
        ">   - grants release authority.\n"
    )
    actual = _split_post_target_child_continuation(representative)
    if actual != expected:
        raise core.VerificationError(
            "F044-D15 post-target-continuation normalization mismatch: "
            f"expected={expected!r} actual={actual!r}"
        )

    core.validate_layer_b_non_authority_text("acceptance/inert.md", representative)

    # Existing continuation-run-length parameter applies to both target and
    # post-target child without introducing a new structural family.
    core.validate_layer_b_non_authority_text(
        "acceptance/inert.md",
        "> - neutral parent\n"
        ">   - child one\n"
        ">   - child two\n"
        ">   - This file\n"
        ">     target one\n"
        ">     target two\n"
        ">   - neutral post-target\n"
        ">     post one\n"
        ">     post two\n"
        ">   - grants release authority.\n",
    )

    # D13's target-position dimension remains valid here.
    core.validate_layer_b_non_authority_text(
        "acceptance/inert.md",
        "> - neutral parent\n"
        ">   - child one\n"
        ">   - child two\n"
        ">   - child three\n"
        ">   - This file\n"
        ">     target continuation\n"
        ">   - neutral post-target\n"
        ">     post-target continuation\n"
        ">   - grants release authority.\n",
    )

    # Parent-scoped authority remains inherited by the final sibling.
    core.expect_failure_message(
        "F044-D15 final sibling inherits outer self-reference",
        "publishes forbidden self-promotion",
        lambda: core.validate_layer_b_non_authority_text(
            "acceptance/inert.md",
            "> - This file\n"
            ">   - child one\n"
            ">   - child two\n"
            ">   - target child\n"
            ">     target continuation\n"
            ">   - neutral post-target\n"
            ">     post-target continuation\n"
            ">   - grants release authority.\n",
        ),
    )

    # A self-reference local to the post-target child also cannot leak into the
    # final sibling when the outer parent is neutral.
    core.validate_layer_b_non_authority_text(
        "acceptance/inert.md",
        "> - neutral parent\n"
        ">   - child one\n"
        ">   - child two\n"
        ">   - neutral target\n"
        ">     target continuation\n"
        ">   - This file\n"
        ">     post-target continuation\n"
        ">   - grants release authority.\n",
    )

    # Marker-only post-target siblings remain delegated to D14; this layer must
    # not rewrite them itself.
    delegated_marker_only = (
        "> - neutral parent\n"
        ">   - child one\n"
        ">   - child two\n"
        ">   - This file\n"
        ">     target continuation\n"
        ">   - grants release authority.\n"
        ">   - neutral later sibling\n"
    )
    if _split_post_target_child_continuation(delegated_marker_only) != delegated_marker_only:
        raise core.VerificationError(
            "F044-D15 repair escaped into D14 marker-only post-target scope"
        )
    core.validate_layer_b_non_authority_text("acceptance/inert.md", delegated_marker_only)

    # Adjacent families remain outside this bounded repair.
    for untouched in [
        (
            "> - neutral parent\n"
            ">   - child one\n"
            ">     preceding continuation\n"
            ">   - child two\n"
            ">   - This file\n"
            ">     target continuation\n"
            ">   - neutral post-target\n"
            ">     post-target continuation\n"
            ">   - grants release authority.\n"
        ),
        (
            "> - neutral parent\n"
            ">   - child one\n"
            ">   - child two\n"
            ">   - This file\n"
            ">     target continuation\n"
            ">   - neutral post-target one\n"
            ">     post-target continuation\n"
            ">   - neutral post-target two\n"
            ">   - grants release authority.\n"
        ),
        (
            "> - neutral parent\n"
            ">   - child one\n"
            ">   - child two\n"
            ">   - This file\n"
            ">     target continuation\n"
            ">   - neutral post-target\n"
            ">     - grandchild\n"
            ">   - grants release authority.\n"
        ),
        (
            "> - neutral parent\n"
            ">   - child one\n"
            ">   - child two\n"
            ">   - This file\n"
            ">     target continuation\n"
            ">   - neutral post-target\n"
            ">     post-target continuation\n"
            ">   - grants release authority.\n"
            ">   - extra final sibling\n"
        ),
        (
            "- Parent:\n"
            "  > - neutral parent\n"
            "  >   - child one\n"
            "  >   - child two\n"
            "  >   - This file\n"
            "  >     target continuation\n"
            "  >   - neutral post-target\n"
            "  >     post-target continuation\n"
            "  >   - grants release authority.\n"
        ),
    ]:
        if _split_post_target_child_continuation(untouched) != untouched:
            raise core.VerificationError(
                "F044-D15 repair escaped its bounded post-target-continuation scope"
            )

    print("[PASS] F044-D15 post-target-child continuation regression")


def _synthetic_check_with_f044d15_post_target_continuation() -> None:
    _prior_synthetic_check()
    _check_f044d15_post_target_continuation_regression()


core._authority_soft_wrapped_units = _authority_soft_wrapped_units
core.check_synthetic_rejections_and_transition_positives = (
    _synthetic_check_with_f044d15_post_target_continuation
)


def main() -> int:
    actual = core.git_blob_sha1(Path(prior.__file__))
    if actual != PRIOR_F044D14_POST_TARGET_CARDINALITY_BLOB_SHA:
        print(
            "[FAIL] prior F044-D14 verifier drift: "
            f"expected={PRIOR_F044D14_POST_TARGET_CARDINALITY_BLOB_SHA} actual={actual}",
            file=core.sys.stderr,
        )
        return 1
    return prior.main()


if __name__ == "__main__":
    raise SystemExit(main())
