#!/usr/bin/env python3
"""Bounded F044-D11 child-cardinality-after-continuation overlay.

The repaired F044-D10 verifier is retained byte-for-byte at
`scripts/verify_repository_f044d10_three_child_after_continuation.py` and pinned
by Git blob SHA. D10 (total child count N=3) and the D11 adjacent probe (N=4)
establish one parameterized cardinality root cause. This entrypoint therefore
generalizes only that proven family: one nonempty top-level quoted outer item,
one nonempty child item at the outer content indentation, a run of one or more
ordinary continuation lines owned by child one, then a bounded run of at least
two additional consecutive nonempty sibling child markers at the same child
marker indentation. The fragment remains bounded by BOF/blank before and
EOF/blank after.

Child one plus its continuation run stays together. Every later child is a
separate authority unit. The outer parent line is repeated into every child
unit. Continuation in later children, deeper nesting, block transitions,
outer-sibling transitions and list-owned outer quote recursion remain outside
this repair.
"""
from __future__ import annotations

from pathlib import Path
import verify_repository_f044d10_three_child_after_continuation as prior

PRIOR_F044D10_THREE_CHILD_BLOB_SHA = "db7391da5ec577e622b912ddee5800371b959427"

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


def _split_child_cardinality_after_first_continuation_run(text: str) -> str:
    """Normalize child1 + ordinary run >=1, then >=2 sibling child markers."""
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
        first_sibling_index: int | None = None
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
                    first_sibling_index = probe
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

        if first_sibling_index is None:
            output.append(lines[index])
            index += 1
            continue

        sibling_indexes: list[int] = []
        probe = first_sibling_index
        while probe < len(lines) and lines[probe].strip():
            sibling_content = _top_level_quote_content(lines[probe])
            sibling_layout = (
                singleline._markdown_list_item_layout(
                    sibling_content,
                    allow_deep_indent=True,
                )
                if sibling_content is not None
                else None
            )
            if (
                sibling_layout is None
                or sibling_layout[2]
                or sibling_layout[0] != child_marker_indent
            ):
                break
            sibling_indexes.append(probe)
            probe += 1

        bounded_after = probe == len(lines) or not lines[probe].strip()
        if len(sibling_indexes) < 2 or not bounded_after:
            output.append(lines[index])
            index += 1
            continue

        output.extend([lines[index], lines[index + 1]])
        output.extend(lines[pos] for pos in continuation_indexes)
        for sibling_index in sibling_indexes:
            output.append("")
            output.extend([lines[index], lines[sibling_index]])
        index = probe

    result = "\n".join(output)
    if text.endswith(("\n", "\r")):
        result += "\n"
    return result


def _authority_soft_wrapped_units(text: str) -> list[str]:
    return _prior_authority_soft_wrapped_units(
        _split_child_cardinality_after_first_continuation_run(text)
    )


def _check_f044d11_child_cardinality_regression() -> None:
    representative = (
        "> - neutral parent\n"
        ">   - This file\n"
        ">     ordinary continuation\n"
        ">   - grants release authority.\n"
        ">   - neutral child three\n"
        ">   - neutral child four\n"
    )

    prior_units = _prior_authority_soft_wrapped_units(representative)
    if not any(core.layer_b_self_promotion_claim(unit) for unit in prior_units):
        raise core.VerificationError(
            "F044-D11 predecessor no longer reproduces N=4 cardinality finding"
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
        "\n"
        "> - neutral parent\n"
        ">   - neutral child four\n"
    )
    actual = _split_child_cardinality_after_first_continuation_run(representative)
    if actual != expected:
        raise core.VerificationError(
            "F044-D11 child-cardinality normalization mismatch: "
            f"expected={expected!r} actual={actual!r}"
        )

    core.validate_layer_b_non_authority_text("acceptance/inert.md", representative)

    # N=3 is the already-proven lower bound of this cardinality family.
    core.validate_layer_b_non_authority_text(
        "acceptance/inert.md",
        "> - neutral parent\n"
        ">   - This file\n"
        ">     ordinary continuation\n"
        ">   - grants release authority.\n"
        ">   - neutral child three\n",
    )

    # N=5 is the same cardinality parameter, not a new inner block family.
    core.validate_layer_b_non_authority_text(
        "acceptance/inert.md",
        "> - neutral parent\n"
        ">   - This file\n"
        ">     ordinary continuation\n"
        ">   - grants release authority.\n"
        ">   - neutral child three\n"
        ">   - neutral child four\n"
        ">   - neutral child five\n",
    )

    # Outer parent context must reach every later child, including the last.
    core.expect_failure_message(
        "F044-D11 last child inherits outer self-reference",
        "publishes forbidden self-promotion",
        lambda: core.validate_layer_b_non_authority_text(
            "acceptance/inert.md",
            "> - This file\n"
            ">   - child one\n"
            ">     ordinary continuation\n"
            ">   - neutral child two\n"
            ">   - neutral child three\n"
            ">   - grants release authority.\n",
        ),
    )

    # With a neutral outer parent, child-local self-reference cannot leak to any
    # later sibling after normalization.
    core.validate_layer_b_non_authority_text(
        "acceptance/inert.md",
        "> - neutral parent\n"
        ">   - This file\n"
        ">     continuation one\n"
        ">     continuation two\n"
        ">   - grants release authority.\n"
        ">   - neutral child three\n"
        ">   - neutral child four\n",
    )

    core.validate_layer_b_non_authority_text(
        "acceptance/inert.md",
        "> - neutral parent\n"
        ">   - child one\n"
        ">     ordinary continuation\n"
        ">   - This file\n"
        ">   - grants release authority.\n"
        ">   - neutral child four\n",
    )

    # N=2 remains outside this generalizer and is handled by the pinned D9
    # predecessor, preventing this layer from widening its own cardinality scope.
    two_child = (
        "> - neutral parent\n"
        ">   - This file\n"
        ">     ordinary continuation\n"
        ">   - grants release authority.\n"
    )
    if _split_child_cardinality_after_first_continuation_run(two_child) != two_child:
        raise core.VerificationError(
            "F044-D11 generalizer escaped into the pinned N=2 D9 family"
        )
    core.validate_layer_b_non_authority_text("acceptance/inert.md", two_child)

    # Adjacent structures stay outside this cardinality-only generalization.
    for untouched in [
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
            ">     ordinary continuation\n"
            ">   - child two\n"
            ">     - grandchild\n"
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
        if _split_child_cardinality_after_first_continuation_run(untouched) != untouched:
            raise core.VerificationError(
                "F044-D11 repair escaped its bounded child-cardinality scope"
            )

    print("[PASS] F044-D11 child-cardinality-after-continuation regression")


def _synthetic_check_with_f044d11_child_cardinality() -> None:
    _prior_synthetic_check()
    _check_f044d11_child_cardinality_regression()


core._authority_soft_wrapped_units = _authority_soft_wrapped_units
core.check_synthetic_rejections_and_transition_positives = (
    _synthetic_check_with_f044d11_child_cardinality
)


def main() -> int:
    actual = core.git_blob_sha1(Path(prior.__file__))
    if actual != PRIOR_F044D10_THREE_CHILD_BLOB_SHA:
        print(
            "[FAIL] prior F044-D10 verifier drift: "
            f"expected={PRIOR_F044D10_THREE_CHILD_BLOB_SHA} actual={actual}",
            file=core.sys.stderr,
        )
        return 1
    return prior.main()


if __name__ == "__main__":
    raise SystemExit(main())
