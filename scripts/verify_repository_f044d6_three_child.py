#!/usr/bin/env python3
"""Bounded F044-D6 three-child parent-context preservation overlay.

The repaired F044-D4 verifier is retained byte-for-byte at
`scripts/verify_repository_f044d4_one_child.py` and pinned by Git blob SHA.
This entrypoint repairs only one security shape: one nonempty outer quoted list
item with exactly three consecutive nonempty child sibling markers at the outer
content indentation, where that four-line fragment is bounded by BOF/blank
before and EOF/blank after.

The three child siblings remain separate authority units, while the outer
parent line is repeated into every child unit so established parent-context
inheritance is preserved. Four-or-more child siblings, child continuation,
deeper nesting, outer-sibling transitions and list-owned outer quotes remain
outside this repair.
"""
from __future__ import annotations

from pathlib import Path
import verify_repository_f044d4_one_child as prior

PRIOR_F044D4_ONE_CHILD_BLOB_SHA = "17cfdd6aec80aace8ed755040f025796c3e18488"

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


def _preserve_parent_for_exact_three_child_siblings(text: str) -> str:
    """Duplicate one bounded outer parent across exactly three child units."""
    lines = text.splitlines()
    output: list[str] = []
    index = 0

    while index < len(lines):
        if index + 3 >= len(lines):
            output.append(lines[index])
            index += 1
            continue

        bounded_before = index == 0 or not lines[index - 1].strip()
        bounded_after = index + 4 == len(lines) or not lines[index + 4].strip()
        if not bounded_before or not bounded_after:
            output.append(lines[index])
            index += 1
            continue

        parent_content = _top_level_quote_content(lines[index])
        child_contents = [
            _top_level_quote_content(lines[index + offset])
            for offset in (1, 2, 3)
        ]
        if parent_content is None or any(content is None for content in child_contents):
            output.append(lines[index])
            index += 1
            continue

        parent_layout = singleline._markdown_list_item_layout(parent_content)
        child_layouts = [
            singleline._markdown_list_item_layout(content)
            for content in child_contents
        ]
        if parent_layout is None or any(layout is None for layout in child_layouts):
            output.append(lines[index])
            index += 1
            continue

        _, parent_content_indent, parent_empty, _ = parent_layout
        child_markers = [layout[0] for layout in child_layouts]
        child_empty = [layout[2] for layout in child_layouts]
        if (
            parent_empty
            or any(child_empty)
            or child_markers[0] != parent_content_indent
            or any(marker != child_markers[0] for marker in child_markers[1:])
        ):
            output.append(lines[index])
            index += 1
            continue

        for child_offset in (1, 2, 3):
            if child_offset > 1:
                output.append("")
            output.extend([lines[index], lines[index + child_offset]])
        index += 4

    result = "\n".join(output)
    if text.endswith(("\n", "\r")):
        result += "\n"
    return result


def _authority_soft_wrapped_units(text: str) -> list[str]:
    return _prior_authority_soft_wrapped_units(
        _preserve_parent_for_exact_three_child_siblings(text)
    )


def _check_f044d6_three_child_parent_context_regression() -> None:
    representative = (
        "> - This file\n"
        ">   - child one\n"
        ">   - child two\n"
        ">   - grants release authority.\n"
    )

    prior_units = _prior_authority_soft_wrapped_units(representative)
    if any(core.layer_b_self_promotion_claim(unit) for unit in prior_units):
        raise core.VerificationError(
            "F044-D6 predecessor no longer reproduces lost third-child parent context"
        )

    expected = (
        "> - This file\n"
        ">   - child one\n"
        "\n"
        "> - This file\n"
        ">   - child two\n"
        "\n"
        "> - This file\n"
        ">   - grants release authority.\n"
    )
    actual = _preserve_parent_for_exact_three_child_siblings(representative)
    if actual != expected:
        raise core.VerificationError(
            "F044-D6 three-child parent-context normalization mismatch: "
            f"expected={expected!r} actual={actual!r}"
        )

    core.expect_failure_message(
        "F044-D6 third child inherits outer self-reference",
        "publishes forbidden self-promotion",
        lambda: core.validate_layer_b_non_authority_text(
            "acceptance/inert.md", representative
        ),
    )

    # Child siblings remain separate when the outer parent is neutral.
    core.validate_layer_b_non_authority_text(
        "acceptance/inert.md",
        "> - neutral parent\n"
        ">   - This file\n"
        ">   - child two\n"
        ">   - grants release authority.\n",
    )

    for child_index, source in enumerate(
        [
            (
                "> - This file\n"
                ">   - grants release authority.\n"
                ">   - child two\n"
                ">   - child three\n"
            ),
            (
                "> - This file\n"
                ">   - child one\n"
                ">   - grants release authority.\n"
                ">   - child three\n"
            ),
        ],
        start=1,
    ):
        core.expect_failure_message(
            f"F044-D6 child {child_index} promotion inherits outer self-reference",
            "publishes forbidden self-promotion",
            lambda source=source: core.validate_layer_b_non_authority_text(
                "acceptance/inert.md", source
            ),
        )

    # Adjacent families stay outside this exact repair.
    for untouched in [
        (
            "> - This file\n"
            ">   - child one\n"
            ">   - child two\n"
            ">   - child three\n"
            ">   - grants release authority.\n"
        ),
        (
            "> - This file\n"
            ">   - child one\n"
            ">     child continuation\n"
            ">   - child two\n"
            ">   - grants release authority.\n"
        ),
        (
            "> - This file\n"
            ">   - child one\n"
            ">     - grandchild\n"
            ">   - child two\n"
            ">   - grants release authority.\n"
        ),
        (
            "> - This file\n"
            ">   - child one\n"
            ">   - child two\n"
            "> - outer sibling\n"
        ),
        (
            "- Parent:\n"
            "  > - This file\n"
            "  >   - child one\n"
            "  >   - child two\n"
            "  >   - grants release authority.\n"
        ),
    ]:
        if _preserve_parent_for_exact_three_child_siblings(untouched) != untouched:
            raise core.VerificationError(
                "F044-D6 repair escaped its exact three-child bounded scope"
            )

    print("[PASS] F044-D6 three-child parent-context preservation regression")


def _synthetic_check_with_f044d6_parent_context() -> None:
    _prior_synthetic_check()
    _check_f044d6_three_child_parent_context_regression()


core._authority_soft_wrapped_units = _authority_soft_wrapped_units
core.check_synthetic_rejections_and_transition_positives = (
    _synthetic_check_with_f044d6_parent_context
)


def main() -> int:
    actual = core.git_blob_sha1(Path(prior.__file__))
    if actual != PRIOR_F044D4_ONE_CHILD_BLOB_SHA:
        print(
            "[FAIL] prior F044-D4 verifier drift: "
            f"expected={PRIOR_F044D4_ONE_CHILD_BLOB_SHA} actual={actual}",
            file=core.sys.stderr,
        )
        return 1
    return prior.main()


if __name__ == "__main__":
    raise SystemExit(main())
