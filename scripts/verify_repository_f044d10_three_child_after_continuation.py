#!/usr/bin/env python3
"""Bounded F044-D10 three-child-after-continuation overlay.

The repaired F044-D9 verifier is retained byte-for-byte at
`scripts/verify_repository_f044d9_child_continuation_run.py` and pinned by Git
blob SHA. This entrypoint changes only one adjacent child-cardinality shape: one
nonempty top-level quoted outer item, one nonempty child item at the outer
content indentation, a run of one or more ordinary continuation lines owned by
that child, then exactly two more consecutive nonempty sibling child markers at
the same child marker indentation. The fragment remains bounded by BOF/blank
before and EOF/blank after.

Child one plus its continuation run stays together. Child two and child three
are separate authority units. The outer parent line is repeated into all three
units. Four-or-more child items, continuation in later children, deeper
nesting, block transitions and outer-sibling/list-owned quote families remain
outside this repair.
"""
from __future__ import annotations

from pathlib import Path
import verify_repository_f044d9_child_continuation_run as prior

PRIOR_F044D9_CHILD_CONTINUATION_RUN_BLOB_SHA = (
    "e28213dbe6a1b9808ea57ffa437ce34caa29e614"
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


def _split_three_children_after_first_continuation_run(text: str) -> str:
    """Normalize parent -> child1 + ordinary run >=1 -> child2 -> child3."""
    lines = text.splitlines()
    output: list[str] = []
    index = 0

    while index < len(lines):
        if index + 4 >= len(lines):
            output.append(lines[index])
            index += 1
            continue

        bounded_before = index == 0 or not lines[index - 1].strip()
        if not bounded_before:
            output.append(lines[index])
            index += 1
            continue

        parent_content = _top_level_quote_content(lines[index])
        child_one_content = _top_level_quote_content(lines[index + 1])
        parent_layout = (
            singleline._markdown_list_item_layout(parent_content)
            if parent_content is not None
            else None
        )
        child_one_layout = (
            singleline._markdown_list_item_layout(child_one_content)
            if child_one_content is not None
            else None
        )
        if (
            parent_layout is None
            or child_one_layout is None
            or parent_layout[2]
            or child_one_layout[2]
        ):
            output.append(lines[index])
            index += 1
            continue

        _, parent_content_indent, _, _ = parent_layout
        child_marker_indent, child_content_indent, _, _ = child_one_layout
        if child_marker_indent != parent_content_indent:
            output.append(lines[index])
            index += 1
            continue

        continuation_indexes: list[int] = []
        child_two_index: int | None = None
        probe = index + 2

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
                    and any_list[0] == child_marker_indent
                ):
                    child_two_index = probe
                break

            relative = singleline._markdown_remove_leading_columns(
                content,
                child_content_indent,
            )
            if (
                relative is None
                or not relative.strip()
                or not singleline._markdown_block_quote_lazy_paragraph(relative)
            ):
                break

            continuation_indexes.append(probe)
            probe += 1

        if child_two_index is None or child_two_index + 1 >= len(lines):
            output.append(lines[index])
            index += 1
            continue

        child_three_content = _top_level_quote_content(lines[child_two_index + 1])
        child_three_layout = (
            singleline._markdown_list_item_layout(
                child_three_content,
                allow_deep_indent=True,
            )
            if child_three_content is not None
            else None
        )
        if (
            child_three_layout is None
            or child_three_layout[2]
            or child_three_layout[0] != child_marker_indent
        ):
            output.append(lines[index])
            index += 1
            continue

        child_three_index = child_two_index + 1
        bounded_after = (
            child_three_index + 1 == len(lines)
            or not lines[child_three_index + 1].strip()
        )
        if not bounded_after:
            output.append(lines[index])
            index += 1
            continue

        output.extend([lines[index], lines[index + 1]])
        output.extend(lines[pos] for pos in continuation_indexes)
        output.append("")
        output.extend([lines[index], lines[child_two_index]])
        output.append("")
        output.extend([lines[index], lines[child_three_index]])
        index = child_three_index + 1

    result = "\n".join(output)
    if text.endswith(("\n", "\r")):
        result += "\n"
    return result


def _authority_soft_wrapped_units(text: str) -> list[str]:
    return _prior_authority_soft_wrapped_units(
        _split_three_children_after_first_continuation_run(text)
    )


def _check_f044d10_three_child_continuation_regression() -> None:
    representative = (
        "> - neutral parent\n"
        ">   - This file\n"
        ">     ordinary continuation\n"
        ">   - grants release authority.\n"
        ">   - neutral child three\n"
    )

    prior_units = _prior_authority_soft_wrapped_units(representative)
    if not any(core.layer_b_self_promotion_claim(unit) for unit in prior_units):
        raise core.VerificationError(
            "F044-D10 predecessor no longer reproduces child1-child2 false positive"
        )

    expected = (
        "> - neutral parent\n"
        ">   - This file\n"
        ">     ordinary continuation\n"
        "\n"
        "> - neutral parent\n"
        ">   - grants release authority.\n"
        "\n"
        "> - neutral parent\n"
        ">   - neutral child three\n"
    )
    actual = _split_three_children_after_first_continuation_run(representative)
    if actual != expected:
        raise core.VerificationError(
            "F044-D10 three-child normalization mismatch: "
            f"expected={expected!r} actual={actual!r}"
        )

    core.validate_layer_b_non_authority_text("acceptance/inert.md", representative)

    # Outer parent context must reach child two and child three.
    for label, rejected in [
        (
            "F044-D10 child two inherits outer self-reference",
            "> - This file\n"
            ">   - child one\n"
            ">     ordinary continuation\n"
            ">   - grants release authority.\n"
            ">   - neutral child three\n",
        ),
        (
            "F044-D10 child three inherits outer self-reference",
            "> - This file\n"
            ">   - child one\n"
            ">     ordinary continuation\n"
            ">   - neutral child two\n"
            ">   - grants release authority.\n",
        ),
    ]:
        core.expect_failure_message(
            label,
            "publishes forbidden self-promotion",
            lambda rejected=rejected: core.validate_layer_b_non_authority_text(
                "acceptance/inert.md", rejected
            ),
        )

    # With a neutral outer parent, child-local self-reference cannot leak to
    # either later sibling.
    core.validate_layer_b_non_authority_text(
        "acceptance/inert.md",
        "> - neutral parent\n"
        ">   - This file\n"
        ">     continuation one\n"
        ">     continuation two\n"
        ">   - grants release authority.\n"
        ">   - neutral child three\n",
    )
    core.validate_layer_b_non_authority_text(
        "acceptance/inert.md",
        "> - neutral parent\n"
        ">   - This file\n"
        ">     ordinary continuation\n"
        ">   - neutral child two\n"
        ">   - grants release authority.\n",
    )

    ordered = (
        "> 1. neutral parent\n"
        ">    - This file\n"
        ">      ordinary continuation\n"
        ">    - grants release authority.\n"
        ">    - neutral child three\n"
    )
    core.validate_layer_b_non_authority_text("acceptance/inert.md", ordered)

    # Adjacent cardinality/container families remain outside this exact repair.
    for untouched in [
        (
            "> - neutral parent\n"
            ">   - This file\n"
            ">     ordinary continuation\n"
            ">   - grants release authority.\n"
            ">   - child three\n"
            ">   - child four\n"
        ),
        (
            "> - neutral parent\n"
            ">   - This file\n"
            ">     ordinary continuation\n"
            ">   - child two\n"
            ">     child two continuation\n"
            ">   - grants release authority.\n"
        ),
        (
            "> - neutral parent\n"
            ">   - This file\n"
            ">     - grandchild\n"
            ">   - child two\n"
            ">   - grants release authority.\n"
        ),
        (
            "> - neutral parent\n"
            ">   - This file\n"
            ">     ordinary continuation\n"
            ">   - child two\n"
            ">   - child three\n"
            "> - outer sibling\n"
        ),
        (
            "- Parent:\n"
            "  > - neutral parent\n"
            "  >   - This file\n"
            "  >     ordinary continuation\n"
            "  >   - child two\n"
            "  >   - grants release authority.\n"
        ),
    ]:
        if _split_three_children_after_first_continuation_run(untouched) != untouched:
            raise core.VerificationError(
                "F044-D10 repair escaped its exact three-child bounded scope"
            )

    print("[PASS] F044-D10 three-child-after-continuation sibling regression")


def _synthetic_check_with_f044d10_three_children() -> None:
    _prior_synthetic_check()
    _check_f044d10_three_child_continuation_regression()


core._authority_soft_wrapped_units = _authority_soft_wrapped_units
core.check_synthetic_rejections_and_transition_positives = (
    _synthetic_check_with_f044d10_three_children
)


def main() -> int:
    actual = core.git_blob_sha1(Path(prior.__file__))
    if actual != PRIOR_F044D9_CHILD_CONTINUATION_RUN_BLOB_SHA:
        print(
            "[FAIL] prior F044-D9 verifier drift: "
            f"expected={PRIOR_F044D9_CHILD_CONTINUATION_RUN_BLOB_SHA} actual={actual}",
            file=core.sys.stderr,
        )
        return 1
    return prior.main()


if __name__ == "__main__":
    raise SystemExit(main())
