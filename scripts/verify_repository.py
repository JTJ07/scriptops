#!/usr/bin/env python3
"""Bounded F044 nested outer-list recursion overlay.

The repaired position-generic F044 verifier is retained byte-for-byte at
`scripts/verify_repository_f044_position_generic_tail.py` and pinned by Git
blob SHA. This overlay repairs exactly one additional outer-list ownership
layer around the already-supported list-owned quote sibling shape.

The rule is structural rather than ordinal: a source-column-zero outer item
owns one nested outer item at its content indentation; that nested item owns a
quote at its content indentation; inside the quote, one parent list item owns
one child with one ordinary continuation followed by one same-level sibling.
The two child authority units inherit both outer-list frames and the quoted
parent independently.

Further nested outer-list recursion, multiple child continuations, block
transitions, multiple quoted parents and other new F044 dimensions remain
outside this repair.
"""
from __future__ import annotations

from pathlib import Path
import verify_repository_f044_position_generic_tail as prior

PRIOR_POSITION_GENERIC_BLOB_SHA = "6e7981d64f06fa3638844e4e2f423afabab77faa"

core = prior.core
singleline = prior.singleline
_prior_authority_soft_wrapped_units = core._authority_soft_wrapped_units
_prior_synthetic_check = core.check_synthetic_rejections_and_transition_positives


def _split_one_nested_outer_list_owned_quote_siblings(text: str) -> str:
    """Split one structurally nested outer-list-owned quote sibling boundary."""
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
        nested_outer_raw = lines[index + 1]
        quote_parent_raw = lines[index + 2]
        child_raw = lines[index + 3]
        continuation_raw = lines[index + 4]
        sibling_raw = lines[index + 5]

        outer_layout = singleline._markdown_list_item_layout(outer_raw)
        nested_outer_layout = singleline._markdown_list_item_layout(
            nested_outer_raw,
            allow_deep_indent=True,
        )
        if outer_layout is None or nested_outer_layout is None:
            output.append(lines[index])
            index += 1
            continue

        outer_marker, outer_content_indent, outer_empty, _ = outer_layout
        nested_marker, nested_content_indent, nested_empty, _ = nested_outer_layout
        if (
            outer_empty
            or nested_empty
            or outer_marker != 0
            or nested_marker != outer_content_indent
        ):
            output.append(lines[index])
            index += 1
            continue

        quote_parent = singleline._markdown_block_quote_layout(
            quote_parent_raw,
            allow_deep_indent=True,
        )
        child_quote = singleline._markdown_block_quote_layout(
            child_raw,
            allow_deep_indent=True,
        )
        continuation_quote = singleline._markdown_block_quote_layout(
            continuation_raw,
            allow_deep_indent=True,
        )
        sibling_quote = singleline._markdown_block_quote_layout(
            sibling_raw,
            allow_deep_indent=True,
        )
        if any(
            layout is None
            for layout in (
                quote_parent,
                child_quote,
                continuation_quote,
                sibling_quote,
            )
        ):
            output.append(lines[index])
            index += 1
            continue

        quote_indent, quote_parent_content = quote_parent
        child_quote_indent, child_content = child_quote
        continuation_quote_indent, continuation_content = continuation_quote
        sibling_quote_indent, sibling_content = sibling_quote
        if not (
            quote_indent == nested_content_indent
            and child_quote_indent == quote_indent
            and continuation_quote_indent == quote_indent
            and sibling_quote_indent == quote_indent
        ):
            output.append(lines[index])
            index += 1
            continue

        parent_list = singleline._markdown_list_item_layout(quote_parent_content)
        child_list = singleline._markdown_list_item_layout(
            child_content,
            allow_deep_indent=True,
        )
        sibling_list = singleline._markdown_list_item_layout(
            sibling_content,
            allow_deep_indent=True,
        )
        if parent_list is None or child_list is None or sibling_list is None:
            output.append(lines[index])
            index += 1
            continue

        parent_marker, parent_content_indent, parent_empty, _ = parent_list
        child_marker, child_content_indent, child_empty, _ = child_list
        sibling_marker, _, sibling_empty, _ = sibling_list
        if (
            parent_empty
            or child_empty
            or sibling_empty
            or parent_marker != 0
            or child_marker != parent_content_indent
            or sibling_marker != child_marker
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

        continuation_relative = singleline._markdown_remove_leading_columns(
            continuation_content,
            child_content_indent,
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
                outer_raw,
                nested_outer_raw,
                quote_parent_raw,
                child_raw,
                continuation_raw,
                "",
                outer_raw,
                nested_outer_raw,
                quote_parent_raw,
                sibling_raw,
            ]
        )
        index += 6

    result = "\n".join(output)
    if text.endswith(("\n", "\r")):
        result += "\n"
    return result


def _authority_soft_wrapped_units(text: str) -> list[str]:
    return _prior_authority_soft_wrapped_units(
        _split_one_nested_outer_list_owned_quote_siblings(text)
    )


def _depth_one_control() -> str:
    return (
        "- neutral outer parent\n"
        "  > - neutral quoted parent\n"
        "  >   - This file\n"
        "  >     ordinary continuation\n"
        "  >   - grants release authority.\n"
    )


def _depth_two_finding() -> str:
    return (
        "- neutral outer parent\n"
        "  - neutral nested outer\n"
        "    > - neutral quoted parent\n"
        "    >   - This file\n"
        "    >     ordinary continuation\n"
        "    >   - grants release authority.\n"
    )


def _check_f044_nested_outer_list_depth_regression() -> None:
    depth_one = _depth_one_control()
    if _split_one_nested_outer_list_owned_quote_siblings(depth_one) != depth_one:
        raise core.VerificationError(
            "F044 nested-outer repair modified supported depth-one control"
        )
    core.validate_layer_b_non_authority_text("acceptance/inert.md", depth_one)

    depth_two = _depth_two_finding()
    prior_units = _prior_authority_soft_wrapped_units(depth_two)
    if not any(core.layer_b_self_promotion_claim(unit) for unit in prior_units):
        raise core.VerificationError(
            "F044 nested-outer predecessor no longer reproduces depth-two finding"
        )

    transformed = _split_one_nested_outer_list_owned_quote_siblings(depth_two)
    if transformed == depth_two:
        raise core.VerificationError(
            "F044 nested-outer structural rule did not cover depth-two finding"
        )
    core.validate_layer_b_non_authority_text("acceptance/inert.md", depth_two)

    outer_self_reference = depth_two.replace(
        "- neutral outer parent\n",
        "- This file\n",
        1,
    ).replace(
        "    >   - This file\n",
        "    >   - neutral child\n",
        1,
    )
    core.expect_failure_message(
        "F044 nested-outer repair preserves outer-owner self-promotion",
        "publishes forbidden self-promotion",
        lambda: core.validate_layer_b_non_authority_text(
            "acceptance/inert.md", outer_self_reference
        ),
    )

    nested_owner_self_reference = depth_two.replace(
        "  - neutral nested outer\n",
        "  - This file\n",
        1,
    ).replace(
        "    >   - This file\n",
        "    >   - neutral child\n",
        1,
    )
    core.expect_failure_message(
        "F044 nested-outer repair preserves nested-owner self-promotion",
        "publishes forbidden self-promotion",
        lambda: core.validate_layer_b_non_authority_text(
            "acceptance/inert.md", nested_owner_self_reference
        ),
    )

    quoted_parent_self_reference = depth_two.replace(
        "    > - neutral quoted parent\n",
        "    > - This file\n",
        1,
    ).replace(
        "    >   - This file\n",
        "    >   - neutral child\n",
        1,
    )
    core.expect_failure_message(
        "F044 nested-outer repair preserves quoted-parent self-promotion",
        "publishes forbidden self-promotion",
        lambda: core.validate_layer_b_non_authority_text(
            "acceptance/inert.md", quoted_parent_self_reference
        ),
    )

    same_child_self_promotion = depth_two.replace(
        "    >     ordinary continuation\n",
        "    >     grants release authority.\n",
        1,
    ).replace(
        "    >   - grants release authority.\n",
        "    >   - neutral sibling\n",
        1,
    )
    core.expect_failure_message(
        "F044 nested-outer repair keeps same-child continuation security context",
        "publishes forbidden self-promotion",
        lambda: core.validate_layer_b_non_authority_text(
            "acceptance/inert.md", same_child_self_promotion
        ),
    )

    further_nested = (
        "- neutral outer parent\n"
        "  - neutral nested outer\n"
        "    - further nested outer\n"
        "      > - neutral quoted parent\n"
        "      >   - This file\n"
        "      >     ordinary continuation\n"
        "      >   - grants release authority.\n"
    )
    if _split_one_nested_outer_list_owned_quote_siblings(further_nested) != further_nested:
        raise core.VerificationError(
            "F044 nested-outer repair escaped into further recursion"
        )

    multiple_continuations = depth_two.replace(
        "    >     ordinary continuation\n",
        "    >     continuation one\n"
        "    >     continuation two\n",
        1,
    )
    if (
        _split_one_nested_outer_list_owned_quote_siblings(multiple_continuations)
        != multiple_continuations
    ):
        raise core.VerificationError(
            "F044 nested-outer repair escaped into continuation-run dimension"
        )

    print("[PASS] F044 nested outer-list depth=1 control preserved")
    print("[PASS] F044 nested outer-list depth=2 finding repaired structurally")
    print("[PASS] F044 nested outer-list repair remains bounded before further recursion")


def _synthetic_check_with_f044_nested_outer_list_depth() -> None:
    _prior_synthetic_check()
    _check_f044_nested_outer_list_depth_regression()


core._authority_soft_wrapped_units = _authority_soft_wrapped_units
core.check_synthetic_rejections_and_transition_positives = (
    _synthetic_check_with_f044_nested_outer_list_depth
)


def main() -> int:
    actual = core.git_blob_sha1(Path(prior.__file__))
    if actual != PRIOR_POSITION_GENERIC_BLOB_SHA:
        print(
            "[FAIL] prior position-generic F044 verifier drift: "
            f"expected={PRIOR_POSITION_GENERIC_BLOB_SHA} actual={actual}",
            file=core.sys.stderr,
        )
        return 1
    return prior.main()


if __name__ == "__main__":
    raise SystemExit(main())
