#!/usr/bin/env python3
"""Bounded F044-D19 list-owned quote child-cardinality overlay.

The repaired F044-D18 verifier is retained byte-for-byte at
`scripts/verify_repository_f044d18_list_owned_continuation_run.py` and pinned by
Git blob SHA. D19 non-vacuously reproduces one adjacent cardinality shape in the
same list-owned outer-quote family: one continuation-bearing child, exactly one
additional marker-only sibling, then exactly one final sibling.

This layer repairs only that exact child-cardinality step. The child owns
exactly one ordinary continuation line; D17/D18 continue to own the two-child
run-length family. Two-or-more intermediate siblings, continuation in the
intermediate child, deeper nesting, block transitions, multiple quoted parents,
outer-list siblings, nested outer lists and other list-owned quote recursion
remain outside.
"""
from __future__ import annotations

from pathlib import Path
import verify_repository_f044d18_list_owned_continuation_run as prior

PRIOR_F044D18_LIST_OWNED_RUN_BLOB_SHA = (
    "b575f659b3b22ca8d2f5fef8d8c68f295e5faa5a"
)

core = prior.core
singleline = prior.singleline
_prior_authority_soft_wrapped_units = core._authority_soft_wrapped_units
_prior_synthetic_check = core.check_synthetic_rejections_and_transition_positives


def _split_exact_list_owned_three_child_shape(text: str) -> str:
    """Normalize outer-list -> quoted parent -> child+1-line -> child -> child."""
    lines = text.splitlines()
    output: list[str] = []
    index = 0

    while index < len(lines):
        if index + 5 >= len(lines):
            output.append(lines[index])
            index += 1
            continue

        bounded_before = index == 0 or not lines[index - 1].strip()
        bounded_after = index + 6 == len(lines) or not lines[index + 6].strip()
        if not bounded_before or not bounded_after:
            output.append(lines[index])
            index += 1
            continue

        outer_raw = lines[index]
        quote_parent_raw = lines[index + 1]
        child_one_raw = lines[index + 2]
        continuation_raw = lines[index + 3]
        child_two_raw = lines[index + 4]
        child_three_raw = lines[index + 5]

        outer_layout = singleline._markdown_list_item_layout(outer_raw)
        if outer_layout is None:
            output.append(lines[index])
            index += 1
            continue
        outer_marker_indent, outer_content_indent, outer_empty, _ = outer_layout
        if outer_empty or outer_marker_indent != 0:
            output.append(lines[index])
            index += 1
            continue

        quoted_lines = []
        for raw in (
            quote_parent_raw,
            child_one_raw,
            continuation_raw,
            child_two_raw,
            child_three_raw,
        ):
            layout = singleline._markdown_block_quote_layout(
                raw,
                allow_deep_indent=True,
            )
            if layout is None:
                quoted_lines = []
                break
            quoted_lines.append(layout)
        if len(quoted_lines) != 5:
            output.append(lines[index])
            index += 1
            continue

        quote_indent, quote_parent_content = quoted_lines[0]
        if quote_indent != outer_content_indent or any(
            layout[0] != quote_indent for layout in quoted_lines[1:]
        ):
            output.append(lines[index])
            index += 1
            continue

        child_one_content = quoted_lines[1][1]
        continuation_content = quoted_lines[2][1]
        child_two_content = quoted_lines[3][1]
        child_three_content = quoted_lines[4][1]

        quoted_parent_list = singleline._markdown_list_item_layout(quote_parent_content)
        child_one_list = singleline._markdown_list_item_layout(
            child_one_content,
            allow_deep_indent=True,
        )
        child_two_list = singleline._markdown_list_item_layout(
            child_two_content,
            allow_deep_indent=True,
        )
        child_three_list = singleline._markdown_list_item_layout(
            child_three_content,
            allow_deep_indent=True,
        )
        if any(
            layout is None
            for layout in (
                quoted_parent_list,
                child_one_list,
                child_two_list,
                child_three_list,
            )
        ):
            output.append(lines[index])
            index += 1
            continue

        parent_marker, parent_content_indent, parent_empty, _ = quoted_parent_list
        child_one_marker, child_one_content_indent, child_one_empty, _ = child_one_list
        child_two_marker, _, child_two_empty, _ = child_two_list
        child_three_marker, _, child_three_empty, _ = child_three_list
        if (
            parent_empty
            or child_one_empty
            or child_two_empty
            or child_three_empty
            or parent_marker != 0
            or child_one_marker != parent_content_indent
            or child_two_marker != child_one_marker
            or child_three_marker != child_one_marker
        ):
            output.append(lines[index])
            index += 1
            continue

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
        relative = singleline._markdown_remove_leading_columns(
            continuation_content,
            child_one_content_indent,
        )
        if (
            relative is None
            or not relative.strip()
            or not singleline._markdown_block_quote_lazy_paragraph(relative)
        ):
            output.append(lines[index])
            index += 1
            continue

        output.extend(
            [
                outer_raw,
                quote_parent_raw,
                child_one_raw,
                continuation_raw,
                "",
                outer_raw,
                quote_parent_raw,
                child_two_raw,
                "",
                outer_raw,
                quote_parent_raw,
                child_three_raw,
            ]
        )
        index += 6

    result = "\n".join(output)
    if text.endswith(("\n", "\r")):
        result += "\n"
    return result


def _authority_soft_wrapped_units(text: str) -> list[str]:
    return _prior_authority_soft_wrapped_units(
        _split_exact_list_owned_three_child_shape(text)
    )


def _check_f044d19_list_owned_child_cardinality_regression() -> None:
    representative = (
        "- Parent:\n"
        "  > - neutral quoted parent\n"
        "  >   - This file\n"
        "  >     ordinary continuation\n"
        "  >   - neutral child two\n"
        "  >   - grants release authority.\n"
    )

    prior_units = _prior_authority_soft_wrapped_units(representative)
    if not any(core.layer_b_self_promotion_claim(unit) for unit in prior_units):
        raise core.VerificationError(
            "F044-D19 predecessor no longer reproduces child-cardinality finding"
        )

    expected = (
        "- Parent:\n"
        "  > - neutral quoted parent\n"
        "  >   - This file\n"
        "  >     ordinary continuation\n"
        "\n"
        "- Parent:\n"
        "  > - neutral quoted parent\n"
        "  >   - neutral child two\n"
        "\n"
        "- Parent:\n"
        "  > - neutral quoted parent\n"
        "  >   - grants release authority.\n"
    )
    actual = _split_exact_list_owned_three_child_shape(representative)
    if actual != expected:
        raise core.VerificationError(
            "F044-D19 child-cardinality normalization mismatch: "
            f"expected={expected!r} actual={actual!r}"
        )

    core.validate_layer_b_non_authority_text("acceptance/inert.md", representative)

    # Outer and quoted-parent authority remain inherited by the final child.
    core.expect_failure_message(
        "F044-D19 final child inherits outer-list self-reference",
        "publishes forbidden self-promotion",
        lambda: core.validate_layer_b_non_authority_text(
            "acceptance/inert.md",
            "- This file\n"
            "  > - neutral quoted parent\n"
            "  >   - child one\n"
            "  >     ordinary continuation\n"
            "  >   - neutral child two\n"
            "  >   - grants release authority.\n",
        ),
    )
    core.expect_failure_message(
        "F044-D19 final child inherits quoted-parent self-reference",
        "publishes forbidden self-promotion",
        lambda: core.validate_layer_b_non_authority_text(
            "acceptance/inert.md",
            "- neutral outer\n"
            "  > - This file\n"
            "  >   - child one\n"
            "  >     ordinary continuation\n"
            "  >   - neutral child two\n"
            "  >   - grants release authority.\n",
        ),
    )

    # A self-reference local to the intermediate child must not leak into child three.
    core.validate_layer_b_non_authority_text(
        "acceptance/inert.md",
        "- neutral outer\n"
        "  > - neutral quoted parent\n"
        "  >   - neutral child one\n"
        "  >     ordinary continuation\n"
        "  >   - This file\n"
        "  >   - grants release authority.\n",
    )

    # Two-child D17 and D18 shapes remain delegated and untouched by D19 itself.
    for delegated in [
        (
            "- Parent:\n"
            "  > - neutral quoted parent\n"
            "  >   - This file\n"
            "  >     ordinary continuation\n"
            "  >   - grants release authority.\n"
        ),
        (
            "- Parent:\n"
            "  > - neutral quoted parent\n"
            "  >   - This file\n"
            "  >     continuation one\n"
            "  >     continuation two\n"
            "  >   - grants release authority.\n"
        ),
    ]:
        if _split_exact_list_owned_three_child_shape(delegated) != delegated:
            raise core.VerificationError(
                "F044-D19 cardinality repair escaped into D17/D18 two-child scope"
            )
        core.validate_layer_b_non_authority_text("acceptance/inert.md", delegated)

    # Adjacent structures remain outside this exact cardinality step.
    for untouched in [
        (
            "- Parent:\n"
            "  > - neutral quoted parent\n"
            "  >   - This file\n"
            "  >     ordinary continuation\n"
            "  >   - neutral child two\n"
            "  >   - neutral child three\n"
            "  >   - grants release authority.\n"
        ),
        (
            "- Parent:\n"
            "  > - neutral quoted parent\n"
            "  >   - This file\n"
            "  >     continuation one\n"
            "  >     continuation two\n"
            "  >   - neutral child two\n"
            "  >   - grants release authority.\n"
        ),
        (
            "- Parent:\n"
            "  > - neutral quoted parent\n"
            "  >   - This file\n"
            "  >     ordinary continuation\n"
            "  >   - neutral child two\n"
            "  >     child-two continuation\n"
            "  >   - grants release authority.\n"
        ),
        (
            "- Parent:\n"
            "  > - neutral quoted parent\n"
            "  >   - This file\n"
            "  >     - grandchild\n"
            "  >   - neutral child two\n"
            "  >   - grants release authority.\n"
        ),
        (
            "- Parent:\n"
            "  > - neutral quoted parent\n"
            "  >   - This file\n"
            "  >     ordinary continuation\n"
            "  >   - neutral child two\n"
            "  >   - grants release authority.\n"
            "- outer sibling\n"
        ),
        (
            "  - nested outer\n"
            "    > - neutral quoted parent\n"
            "    >   - This file\n"
            "    >     ordinary continuation\n"
            "    >   - neutral child two\n"
            "    >   - grants release authority.\n"
        ),
    ]:
        if _split_exact_list_owned_three_child_shape(untouched) != untouched:
            raise core.VerificationError(
                "F044-D19 repair escaped its exact three-child scope"
            )

    print("[PASS] F044-D19 list-owned quote child-cardinality regression")


def _synthetic_check_with_f044d19_child_cardinality() -> None:
    _prior_synthetic_check()
    _check_f044d19_list_owned_child_cardinality_regression()


core._authority_soft_wrapped_units = _authority_soft_wrapped_units
core.check_synthetic_rejections_and_transition_positives = (
    _synthetic_check_with_f044d19_child_cardinality
)


def main() -> int:
    actual = core.git_blob_sha1(Path(prior.__file__))
    if actual != PRIOR_F044D18_LIST_OWNED_RUN_BLOB_SHA:
        print(
            "[FAIL] prior F044-D18 verifier drift: "
            f"expected={PRIOR_F044D18_LIST_OWNED_RUN_BLOB_SHA} actual={actual}",
            file=core.sys.stderr,
        )
        return 1
    return prior.main()


if __name__ == "__main__":
    raise SystemExit(main())
