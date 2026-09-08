#!/usr/bin/env python3
"""Bounded F044-D12 later-child-continuation sibling overlay.

The repaired F044-D11 verifier is retained byte-for-byte at
`scripts/verify_repository_f044d11_child_cardinality.py` and pinned by Git blob
SHA. This entrypoint repairs only one adjacent child-position shape: one
nonempty source-column-zero quoted outer list item, a first nonempty child at
the outer content indentation, a second nonempty sibling child at that same
indentation, a run of one or more ordinary continuation lines owned by child
two, and one nonempty third sibling returning to the same child-marker
indentation. The fragment remains bounded by BOF/blank before and EOF/blank
after.

The outer parent is repeated into all three child units. Child two keeps its
continuation run; child three is a separate authority unit. Continuation in
child one remains delegated to D8-D11. Continuation in child three or later,
more preceding/later child siblings, deeper nesting, block transitions,
outer-sibling transitions and list-owned outer quote recursion remain outside
this repair.
"""
from __future__ import annotations

from pathlib import Path
import verify_repository_f044d11_child_cardinality as prior

PRIOR_F044D11_CHILD_CARDINALITY_BLOB_SHA = (
    "9562a7bf8af9db20b45ea7f61907c41c4c7ad0d4"
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


def _split_second_child_continuation_sibling(text: str) -> str:
    """Normalize parent -> child1 -> child2 + ordinary run >=1 -> child3."""
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
        child_two_content = _top_level_quote_content(lines[index + 2])
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
        child_two_layout = (
            singleline._markdown_list_item_layout(child_two_content)
            if child_two_content is not None
            else None
        )
        if (
            parent_layout is None
            or child_one_layout is None
            or child_two_layout is None
            or parent_layout[2]
            or child_one_layout[2]
            or child_two_layout[2]
        ):
            output.append(lines[index])
            index += 1
            continue

        _, parent_content_indent, _, _ = parent_layout
        child_one_marker, _, _, _ = child_one_layout
        child_two_marker, child_two_content_indent, _, _ = child_two_layout
        if (
            child_one_marker != parent_content_indent
            or child_two_marker != child_one_marker
        ):
            output.append(lines[index])
            index += 1
            continue

        continuation_indexes: list[int] = []
        child_three_index: int | None = None
        probe = index + 3

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
                    and any_list[0] == child_two_marker
                ):
                    child_three_index = probe
                break

            relative = singleline._markdown_remove_leading_columns(
                content,
                child_two_content_indent,
            )
            if (
                relative is None
                or not relative.strip()
                or not singleline._markdown_block_quote_lazy_paragraph(relative)
            ):
                break

            continuation_indexes.append(probe)
            probe += 1

        if child_three_index is None:
            output.append(lines[index])
            index += 1
            continue

        bounded_after = (
            child_three_index + 1 == len(lines)
            or not lines[child_three_index + 1].strip()
        )
        if not bounded_after:
            output.append(lines[index])
            index += 1
            continue

        output.extend([lines[index], lines[index + 1]])
        output.append("")
        output.extend([lines[index], lines[index + 2]])
        output.extend(lines[pos] for pos in continuation_indexes)
        output.append("")
        output.extend([lines[index], lines[child_three_index]])
        index = child_three_index + 1

    result = "\n".join(output)
    if text.endswith(("\n", "\r")):
        result += "\n"
    return result


def _authority_soft_wrapped_units(text: str) -> list[str]:
    return _prior_authority_soft_wrapped_units(
        _split_second_child_continuation_sibling(text)
    )


def _check_f044d12_later_child_continuation_regression() -> None:
    representative = (
        "> - neutral parent\n"
        ">   - child one\n"
        ">   - This file\n"
        ">     child two continuation\n"
        ">   - grants release authority.\n"
    )

    prior_units = _prior_authority_soft_wrapped_units(representative)
    if not any(core.layer_b_self_promotion_claim(unit) for unit in prior_units):
        raise core.VerificationError(
            "F044-D12 predecessor no longer reproduces later-child continuation finding"
        )

    expected = (
        "> - neutral parent\n"
        ">   - child one\n"
        "\n"
        "> - neutral parent\n"
        ">   - This file\n"
        ">     child two continuation\n"
        "\n"
        "> - neutral parent\n"
        ">   - grants release authority.\n"
    )
    actual = _split_second_child_continuation_sibling(representative)
    if actual != expected:
        raise core.VerificationError(
            "F044-D12 later-child normalization mismatch: "
            f"expected={expected!r} actual={actual!r}"
        )

    core.validate_layer_b_non_authority_text("acceptance/inert.md", representative)

    # Continuation-run length was already parameterized by D9; preserve that
    # proven dimension while changing only the child position.
    core.validate_layer_b_non_authority_text(
        "acceptance/inert.md",
        "> - neutral parent\n"
        ">   - child one\n"
        ">   - This file\n"
        ">     continuation one\n"
        ">     continuation two\n"
        ">   - grants release authority.\n",
    )

    # Outer parent context must still reach child three.
    core.expect_failure_message(
        "F044-D12 child three inherits outer self-reference",
        "publishes forbidden self-promotion",
        lambda: core.validate_layer_b_non_authority_text(
            "acceptance/inert.md",
            "> - This file\n"
            ">   - child one\n"
            ">   - child two\n"
            ">     ordinary continuation\n"
            ">   - grants release authority.\n",
        ),
    )

    # A self-reference in child one or child two must not leak into a later
    # sibling when the outer parent itself is neutral.
    core.validate_layer_b_non_authority_text(
        "acceptance/inert.md",
        "> - neutral parent\n"
        ">   - This file\n"
        ">   - child two\n"
        ">     ordinary continuation\n"
        ">   - grants release authority.\n",
    )
    core.validate_layer_b_non_authority_text(
        "acceptance/inert.md",
        "> - neutral parent\n"
        ">   - child one\n"
        ">   - This file\n"
        ">     ordinary continuation\n"
        ">   - grants release authority.\n",
    )

    # Adjacent structures remain outside this position-only repair.
    for untouched in [
        (
            "> - neutral parent\n"
            ">   - child one\n"
            ">     child one continuation\n"
            ">   - child two\n"
            ">     child two continuation\n"
            ">   - grants release authority.\n"
        ),
        (
            "> - neutral parent\n"
            ">   - child one\n"
            ">   - child two\n"
            ">   - This file\n"
            ">     child three continuation\n"
            ">   - grants release authority.\n"
        ),
        (
            "> - neutral parent\n"
            ">   - child one\n"
            ">   - This file\n"
            ">     child two continuation\n"
            ">   - child three\n"
            ">   - child four\n"
        ),
        (
            "> - neutral parent\n"
            ">   - child one\n"
            ">   - This file\n"
            ">     - grandchild\n"
            ">   - grants release authority.\n"
        ),
        (
            "- Parent:\n"
            "  > - neutral parent\n"
            "  >   - child one\n"
            "  >   - This file\n"
            "  >     child two continuation\n"
            "  >   - grants release authority.\n"
        ),
    ]:
        if _split_second_child_continuation_sibling(untouched) != untouched:
            raise core.VerificationError(
                "F044-D12 repair escaped its bounded second-child scope"
            )

    print("[PASS] F044-D12 later-child-continuation sibling regression")


def _synthetic_check_with_f044d12_later_child_continuation() -> None:
    _prior_synthetic_check()
    _check_f044d12_later_child_continuation_regression()


core._authority_soft_wrapped_units = _authority_soft_wrapped_units
core.check_synthetic_rejections_and_transition_positives = (
    _synthetic_check_with_f044d12_later_child_continuation
)


def main() -> int:
    actual = core.git_blob_sha1(Path(prior.__file__))
    if actual != PRIOR_F044D11_CHILD_CARDINALITY_BLOB_SHA:
        print(
            "[FAIL] prior F044-D11 verifier drift: "
            f"expected={PRIOR_F044D11_CHILD_CARDINALITY_BLOB_SHA} actual={actual}",
            file=core.sys.stderr,
        )
        return 1
    return prior.main()


if __name__ == "__main__":
    raise SystemExit(main())
