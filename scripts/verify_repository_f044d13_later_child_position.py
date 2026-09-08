#!/usr/bin/env python3
"""Bounded F044-D13 later-child-position continuation overlay.

The repaired F044-D12 verifier is retained byte-for-byte at
`scripts/verify_repository_f044d12_later_child_continuation.py` and pinned by
Git blob SHA. D8/D9 establish the continuation-to-sibling boundary for child
one, D12 establishes it for child two, and D13 reproduces the same root cause at
child three. This entrypoint generalizes only the newly proven position
dimension for target child positions three and later.

Scope: one nonempty source-column-zero quoted outer list item; at least two
consecutive one-line child siblings at the outer content indentation; then one
nonempty target child at that same indentation; a run of one or more ordinary
continuation lines owned by the target child; then exactly one nonempty final
sibling at the same child-marker indentation. BOF/blank bounds the fragment
before and EOF/blank bounds it after.

Each preceding child is a separate authority unit. The target child keeps its
continuation run. The final sibling is separate. The outer parent is repeated
into every unit. Child-two continuation remains delegated to D12; continuation
in preceding children, multiple siblings after the target, deeper nesting,
block transitions, outer-sibling transitions and list-owned outer quote
recursion remain outside this repair.
"""
from __future__ import annotations

from pathlib import Path
import verify_repository_f044d12_later_child_continuation as prior

PRIOR_F044D12_LATER_CHILD_BLOB_SHA = "6a71863f5488e287780ba536079ba6c19fa4e302"

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


def _split_later_child_position_continuation_sibling(text: str) -> str:
    """Normalize parent -> >=2 preceding children -> target+run -> final sibling."""
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

        # Collect consecutive one-line child markers. The last one becomes the
        # target only if it is followed by an ordinary continuation run.
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

        # Target child position >=3 means at least two preceding children plus
        # the target marker itself before its continuation begins.
        if len(child_indexes) < 3 or probe >= len(lines) or not lines[probe].strip():
            output.append(lines[index])
            index += 1
            continue

        target_index = child_indexes[-1]
        target_content_indent = child_content_indents[-1]
        continuation_indexes: list[int] = []
        final_sibling_index: int | None = None

        while probe < len(lines) and lines[probe].strip():
            content = _top_level_quote_content(lines[probe])
            if content is None:
                break

            any_list = singleline._markdown_list_item_layout(
                content,
                allow_deep_indent=True,
            )
            if any_list is not None:
                if (
                    continuation_indexes
                    and not any_list[2]
                    and any_list[0] == parent_content_indent
                ):
                    final_sibling_index = probe
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

        if final_sibling_index is None:
            output.append(lines[index])
            index += 1
            continue

        bounded_after = (
            final_sibling_index + 1 == len(lines)
            or not lines[final_sibling_index + 1].strip()
        )
        if not bounded_after:
            output.append(lines[index])
            index += 1
            continue

        preceding_indexes = child_indexes[:-1]
        for child_index in preceding_indexes:
            output.extend([lines[index], lines[child_index]])
            output.append("")

        output.extend([lines[index], lines[target_index]])
        output.extend(lines[pos] for pos in continuation_indexes)
        output.append("")
        output.extend([lines[index], lines[final_sibling_index]])
        index = final_sibling_index + 1

    result = "\n".join(output)
    if text.endswith(("\n", "\r")):
        result += "\n"
    return result


def _authority_soft_wrapped_units(text: str) -> list[str]:
    return _prior_authority_soft_wrapped_units(
        _split_later_child_position_continuation_sibling(text)
    )


def _check_f044d13_later_child_position_regression() -> None:
    representative = (
        "> - neutral parent\n"
        ">   - child one\n"
        ">   - child two\n"
        ">   - This file\n"
        ">     child three continuation\n"
        ">   - grants release authority.\n"
    )

    prior_units = _prior_authority_soft_wrapped_units(representative)
    if not any(core.layer_b_self_promotion_claim(unit) for unit in prior_units):
        raise core.VerificationError(
            "F044-D13 predecessor no longer reproduces third-child continuation finding"
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
        ">     child three continuation\n"
        "\n"
        "> - neutral parent\n"
        ">   - grants release authority.\n"
    )
    actual = _split_later_child_position_continuation_sibling(representative)
    if actual != expected:
        raise core.VerificationError(
            "F044-D13 later-position normalization mismatch: "
            f"expected={expected!r} actual={actual!r}"
        )

    core.validate_layer_b_non_authority_text("acceptance/inert.md", representative)

    # Child position four is the same proven position dimension, not a new
    # block/container family.
    core.validate_layer_b_non_authority_text(
        "acceptance/inert.md",
        "> - neutral parent\n"
        ">   - child one\n"
        ">   - child two\n"
        ">   - child three\n"
        ">   - This file\n"
        ">     child four continuation\n"
        ">   - grants release authority.\n",
    )

    # Continuation-run length remains the already-proven D9 parameter.
    core.validate_layer_b_non_authority_text(
        "acceptance/inert.md",
        "> - neutral parent\n"
        ">   - child one\n"
        ">   - child two\n"
        ">   - This file\n"
        ">     continuation one\n"
        ">     continuation two\n"
        ">   - grants release authority.\n",
    )

    # Outer parent context reaches the final sibling after normalization.
    core.expect_failure_message(
        "F044-D13 final sibling inherits outer self-reference",
        "publishes forbidden self-promotion",
        lambda: core.validate_layer_b_non_authority_text(
            "acceptance/inert.md",
            "> - This file\n"
            ">   - child one\n"
            ">   - child two\n"
            ">   - child three\n"
            ">     ordinary continuation\n"
            ">   - grants release authority.\n",
        ),
    )

    # Child-local self-reference cannot leak to the final sibling when the
    # outer parent is neutral.
    core.validate_layer_b_non_authority_text(
        "acceptance/inert.md",
        "> - neutral parent\n"
        ">   - child one\n"
        ">   - child two\n"
        ">   - This file\n"
        ">     ordinary continuation\n"
        ">   - grants release authority.\n",
    )

    # D12 remains responsible for target child position two; this layer must
    # not rewrite it itself.
    delegated_child_two = (
        "> - neutral parent\n"
        ">   - child one\n"
        ">   - This file\n"
        ">     child two continuation\n"
        ">   - grants release authority.\n"
    )
    if _split_later_child_position_continuation_sibling(delegated_child_two) != delegated_child_two:
        raise core.VerificationError(
            "F044-D13 position generalizer escaped into D12 child-two scope"
        )
    core.validate_layer_b_non_authority_text("acceptance/inert.md", delegated_child_two)

    # Adjacent structures stay outside this position-only generalization.
    for untouched in [
        (
            "> - neutral parent\n"
            ">   - child one\n"
            ">     preceding continuation\n"
            ">   - child two\n"
            ">   - This file\n"
            ">     target continuation\n"
            ">   - grants release authority.\n"
        ),
        (
            "> - neutral parent\n"
            ">   - child one\n"
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
            ">     - grandchild\n"
            ">   - grants release authority.\n"
        ),
        (
            "- Parent:\n"
            "  > - neutral parent\n"
            "  >   - child one\n"
            "  >   - child two\n"
            "  >   - This file\n"
            "  >     target continuation\n"
            "  >   - grants release authority.\n"
        ),
    ]:
        if _split_later_child_position_continuation_sibling(untouched) != untouched:
            raise core.VerificationError(
                "F044-D13 repair escaped its bounded later-position scope"
            )

    print("[PASS] F044-D13 later-child-position continuation regression")


def _synthetic_check_with_f044d13_later_child_position() -> None:
    _prior_synthetic_check()
    _check_f044d13_later_child_position_regression()


core._authority_soft_wrapped_units = _authority_soft_wrapped_units
core.check_synthetic_rejections_and_transition_positives = (
    _synthetic_check_with_f044d13_later_child_position
)


def main() -> int:
    actual = core.git_blob_sha1(Path(prior.__file__))
    if actual != PRIOR_F044D12_LATER_CHILD_BLOB_SHA:
        print(
            "[FAIL] prior F044-D12 verifier drift: "
            f"expected={PRIOR_F044D12_LATER_CHILD_BLOB_SHA} actual={actual}",
            file=core.sys.stderr,
        )
        return 1
    return prior.main()


if __name__ == "__main__":
    raise SystemExit(main())
