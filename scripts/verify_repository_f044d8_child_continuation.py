#!/usr/bin/env python3
"""Bounded F044-D8 one child-continuation sibling overlay.

The repaired F044-D7 verifier is retained byte-for-byte at
`scripts/verify_repository_f044d7_child_run.py` and pinned by Git blob SHA.
This entrypoint repairs only one nested-list shape: one nonempty top-level
quoted outer item, one nonempty child item at the outer content indentation,
exactly one ordinary continuation line owned by that child, and one nonempty
sibling child returning to the same child marker indentation. The fragment is
bounded by BOF/blank before and EOF/blank after.

The continuation stays with child one; child two is a separate authority unit;
the outer parent line is repeated into both units. Two-or-more continuation
lines, deeper nesting, blank/fence/block transitions, outer-sibling transitions
and list-owned outer quote recursion remain outside this repair.
"""
from __future__ import annotations

from pathlib import Path
import verify_repository_f044d7_child_run as prior

PRIOR_F044D7_CHILD_RUN_BLOB_SHA = "fcf1920eae399bb0bc09b103e105d23116c2a5d0"

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


def _split_one_child_continuation_sibling(text: str) -> str:
    """Normalize only parent -> child -> one owned continuation -> sibling."""
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
        child_one_content = _top_level_quote_content(lines[index + 1])
        continuation_content = _top_level_quote_content(lines[index + 2])
        child_two_content = _top_level_quote_content(lines[index + 3])
        if any(
            content is None
            for content in (
                parent_content,
                child_one_content,
                continuation_content,
                child_two_content,
            )
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
        child_one_marker, child_one_content_indent, child_one_empty, _ = child_one_layout
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

        # Interpret the continuation relative to the owning child item's content
        # column. Testing the unadjusted four-plus-column source text with the
        # top-level lazy predicate would misclassify ordinary child text as
        # indented code. Deep list syntax is excluded before de-indentation.
        if (
            singleline._markdown_list_item_layout(
                continuation_content,
                allow_deep_indent=True,
            )
            is not None
        ):
            output.append(lines[index])
            index += 1
            continue
        continuation_relative = singleline._markdown_remove_leading_columns(
            continuation_content,
            child_one_content_indent,
        )
        if (
            continuation_relative is None
            or not continuation_relative.strip()
            or not singleline._markdown_block_quote_lazy_paragraph(
                continuation_relative
            )
        ):
            output.append(lines[index])
            index += 1
            continue

        output.extend(
            [
                lines[index],
                lines[index + 1],
                lines[index + 2],
                "",
                lines[index],
                lines[index + 3],
            ]
        )
        index += 4

    result = "\n".join(output)
    if text.endswith(("\n", "\r")):
        result += "\n"
    return result


def _authority_soft_wrapped_units(text: str) -> list[str]:
    return _prior_authority_soft_wrapped_units(
        _split_one_child_continuation_sibling(text)
    )


def _check_f044d8_child_continuation_sibling_regression() -> None:
    representative = (
        "> - neutral parent\n"
        ">   - This file\n"
        ">     ordinary continuation\n"
        ">   - grants release authority.\n"
    )

    prior_units = _prior_authority_soft_wrapped_units(representative)
    if not any(core.layer_b_self_promotion_claim(unit) for unit in prior_units):
        raise core.VerificationError(
            "F044-D8 predecessor no longer reproduces cross-child false positive"
        )

    expected = (
        "> - neutral parent\n"
        ">   - This file\n"
        ">     ordinary continuation\n"
        "\n"
        "> - neutral parent\n"
        ">   - grants release authority.\n"
    )
    actual = _split_one_child_continuation_sibling(representative)
    if actual != expected:
        raise core.VerificationError(
            "F044-D8 child-continuation sibling normalization mismatch: "
            f"expected={expected!r} actual={actual!r}"
        )

    core.validate_layer_b_non_authority_text("acceptance/inert.md", representative)

    core.expect_failure_message(
        "F044-D8 second child inherits outer self-reference",
        "publishes forbidden self-promotion",
        lambda: core.validate_layer_b_non_authority_text(
            "acceptance/inert.md",
            "> - This file\n"
            ">   - child one\n"
            ">     ordinary continuation\n"
            ">   - grants release authority.\n",
        ),
    )

    core.expect_failure_message(
        "F044-D8 first child continuation stays parent-scoped",
        "publishes forbidden self-promotion",
        lambda: core.validate_layer_b_non_authority_text(
            "acceptance/inert.md",
            "> - This file\n"
            ">   - grants release authority.\n"
            ">     ordinary continuation\n"
            ">   - child two\n",
        ),
    )

    ordered = (
        "> 1. neutral parent\n"
        ">    - This file\n"
        ">      ordinary continuation\n"
        ">    - grants release authority.\n"
    )
    core.validate_layer_b_non_authority_text("acceptance/inert.md", ordered)

    for untouched in [
        (
            "> - neutral parent\n"
            ">   - This file\n"
            ">     continuation one\n"
            ">     continuation two\n"
            ">   - grants release authority.\n"
        ),
        (
            "> - neutral parent\n"
            ">   - This file\n"
            ">     - grandchild\n"
            ">   - grants release authority.\n"
        ),
        (
            "> - neutral parent\n"
            ">   - This file\n"
            ">     ```\n"
            ">     code\n"
            ">     ```\n"
            ">   - grants release authority.\n"
        ),
        (
            "> - neutral parent\n"
            ">   - This file\n"
            ">     ordinary continuation\n"
            ">   - child two\n"
            "> - outer sibling\n"
        ),
        (
            "- Parent:\n"
            "  > - neutral parent\n"
            "  >   - This file\n"
            "  >     ordinary continuation\n"
            "  >   - grants release authority.\n"
        ),
    ]:
        if _split_one_child_continuation_sibling(untouched) != untouched:
            raise core.VerificationError(
                "F044-D8 repair escaped its exact one-continuation bounded scope"
            )

    print("[PASS] F044-D8 one child-continuation sibling-separation regression")


def _synthetic_check_with_f044d8_child_continuation() -> None:
    _prior_synthetic_check()
    _check_f044d8_child_continuation_sibling_regression()


core._authority_soft_wrapped_units = _authority_soft_wrapped_units
core.check_synthetic_rejections_and_transition_positives = (
    _synthetic_check_with_f044d8_child_continuation
)


def main() -> int:
    actual = core.git_blob_sha1(Path(prior.__file__))
    if actual != PRIOR_F044D7_CHILD_RUN_BLOB_SHA:
        print(
            "[FAIL] prior F044-D7 verifier drift: "
            f"expected={PRIOR_F044D7_CHILD_RUN_BLOB_SHA} actual={actual}",
            file=core.sys.stderr,
        )
        return 1
    return prior.main()


if __name__ == "__main__":
    raise SystemExit(main())
