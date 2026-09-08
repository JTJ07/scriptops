#!/usr/bin/env python3
"""Bounded F044-D17 list-owned outer-quote sibling overlay.

The repaired F044-D15 verifier is retained byte-for-byte at
`scripts/verify_repository_f044d15_post_target_continuation.py` and pinned by
Git blob SHA. This entrypoint repairs exactly one non-vacuously reproduced
list-owned quote shape:

- one nonempty source-column-zero outer list item;
- one block quote whose marker begins at that outer item's content indentation;
- inside the quote, one nonempty quoted parent list item at quote-content column 0;
- exactly one nonempty nested child at the quoted parent's content indentation;
- exactly one ordinary continuation line owned by that child;
- exactly one nonempty sibling child returning to the same child marker indent;
- BOF/blank before and EOF/blank after.

The outer list item and quoted parent are repeated into both child authority
units. The first child keeps its one continuation line; the sibling is separate.
Multiple continuation lines, additional child siblings, deeper nesting,
blank/fence/heading/HTML transitions, multiple quoted parent items, outer-list
siblings, nested outer lists and other list-owned quote recursion remain outside.
"""
from __future__ import annotations

from pathlib import Path
import verify_repository_f044d15_post_target_continuation as prior

PRIOR_F044D15_POST_TARGET_CONTINUATION_BLOB_SHA = (
    "d12fcc3fbbadf52173d161b26d690e2bbb653bd2"
)

core = prior.core
singleline = prior.singleline
_prior_authority_soft_wrapped_units = core._authority_soft_wrapped_units
_prior_synthetic_check = core.check_synthetic_rejections_and_transition_positives


def _split_exact_list_owned_outer_quote_siblings(text: str) -> str:
    """Normalize only outer-list -> quote-parent -> child+1-line -> sibling."""
    lines = text.splitlines()
    output: list[str] = []
    index = 0

    while index < len(lines):
        if index + 4 >= len(lines):
            output.append(lines[index])
            index += 1
            continue

        bounded_before = index == 0 or not lines[index - 1].strip()
        bounded_after = index + 5 == len(lines) or not lines[index + 5].strip()
        if not bounded_before or not bounded_after:
            output.append(lines[index])
            index += 1
            continue

        outer_raw = lines[index]
        quote_parent_raw = lines[index + 1]
        child_one_raw = lines[index + 2]
        continuation_raw = lines[index + 3]
        child_two_raw = lines[index + 4]

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

        quote_parent_layout = singleline._markdown_block_quote_layout(
            quote_parent_raw,
            allow_deep_indent=True,
        )
        child_one_quote = singleline._markdown_block_quote_layout(
            child_one_raw,
            allow_deep_indent=True,
        )
        continuation_quote = singleline._markdown_block_quote_layout(
            continuation_raw,
            allow_deep_indent=True,
        )
        child_two_quote = singleline._markdown_block_quote_layout(
            child_two_raw,
            allow_deep_indent=True,
        )
        if any(
            layout is None
            for layout in (
                quote_parent_layout,
                child_one_quote,
                continuation_quote,
                child_two_quote,
            )
        ):
            output.append(lines[index])
            index += 1
            continue

        quote_indent, quote_parent_content = quote_parent_layout
        child_one_quote_indent, child_one_content = child_one_quote
        continuation_quote_indent, continuation_content = continuation_quote
        child_two_quote_indent, child_two_content = child_two_quote
        if not (
            quote_indent == outer_content_indent
            and child_one_quote_indent == quote_indent
            and continuation_quote_indent == quote_indent
            and child_two_quote_indent == quote_indent
        ):
            output.append(lines[index])
            index += 1
            continue

        quoted_parent_list = singleline._markdown_list_item_layout(
            quote_parent_content
        )
        child_one_list = singleline._markdown_list_item_layout(
            child_one_content,
            allow_deep_indent=True,
        )
        child_two_list = singleline._markdown_list_item_layout(
            child_two_content,
            allow_deep_indent=True,
        )
        if (
            quoted_parent_list is None
            or child_one_list is None
            or child_two_list is None
        ):
            output.append(lines[index])
            index += 1
            continue

        quoted_parent_marker, quoted_parent_content_indent, quoted_parent_empty, _ = (
            quoted_parent_list
        )
        child_one_marker, child_one_content_indent, child_one_empty, _ = child_one_list
        child_two_marker, _, child_two_empty, _ = child_two_list
        if (
            quoted_parent_empty
            or child_one_empty
            or child_two_empty
            or quoted_parent_marker != 0
            or child_one_marker != quoted_parent_content_indent
            or child_two_marker != child_one_marker
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
                outer_raw,
                quote_parent_raw,
                child_one_raw,
                continuation_raw,
                "",
                outer_raw,
                quote_parent_raw,
                child_two_raw,
            ]
        )
        index += 5

    result = "\n".join(output)
    if text.endswith(("\n", "\r")):
        result += "\n"
    return result


def _authority_soft_wrapped_units(text: str) -> list[str]:
    return _prior_authority_soft_wrapped_units(
        _split_exact_list_owned_outer_quote_siblings(text)
    )


def _check_f044d17_list_owned_outer_quote_regression() -> None:
    representative = (
        "- Parent:\n"
        "  > - neutral quoted parent\n"
        "  >   - This file\n"
        "  >     ordinary continuation\n"
        "  >   - grants release authority.\n"
    )

    # Mandatory non-vacuity: exact GREEN D15 must reproduce the finding.
    prior_units = _prior_authority_soft_wrapped_units(representative)
    if not any(core.layer_b_self_promotion_claim(unit) for unit in prior_units):
        raise core.VerificationError(
            "F044-D17 predecessor no longer reproduces list-owned outer-quote finding"
        )

    expected = (
        "- Parent:\n"
        "  > - neutral quoted parent\n"
        "  >   - This file\n"
        "  >     ordinary continuation\n"
        "\n"
        "- Parent:\n"
        "  > - neutral quoted parent\n"
        "  >   - grants release authority.\n"
    )
    actual = _split_exact_list_owned_outer_quote_siblings(representative)
    if actual != expected:
        raise core.VerificationError(
            "F044-D17 list-owned quote normalization mismatch: "
            f"expected={expected!r} actual={actual!r}"
        )

    core.validate_layer_b_non_authority_text("acceptance/inert.md", representative)

    # Outer-list self-reference must remain inherited by the promoted child.
    core.expect_failure_message(
        "F044-D17 promoted child inherits outer list self-reference",
        "publishes forbidden self-promotion",
        lambda: core.validate_layer_b_non_authority_text(
            "acceptance/inert.md",
            "- This file\n"
            "  > - neutral quoted parent\n"
            "  >   - child one\n"
            "  >     ordinary continuation\n"
            "  >   - grants release authority.\n",
        ),
    )

    # Quoted-parent self-reference must likewise remain inherited.
    core.expect_failure_message(
        "F044-D17 promoted child inherits quoted parent self-reference",
        "publishes forbidden self-promotion",
        lambda: core.validate_layer_b_non_authority_text(
            "acceptance/inert.md",
            "- neutral outer\n"
            "  > - This file\n"
            "  >   - child one\n"
            "  >     ordinary continuation\n"
            "  >   - grants release authority.\n",
        ),
    )

    # Child-local self-reference must not leak into its sibling.
    core.validate_layer_b_non_authority_text(
        "acceptance/inert.md",
        "- neutral outer\n"
        "  > - neutral quoted parent\n"
        "  >   - This file\n"
        "  >     ordinary continuation\n"
        "  >   - grants release authority.\n",
    )

    # Neighboring structures remain intentionally untouched.
    for untouched in [
        (
            "- Parent:\n"
            "  > - neutral quoted parent\n"
            "  >   - This file\n"
            "  >     continuation one\n"
            "  >     continuation two\n"
            "  >   - grants release authority.\n"
        ),
        (
            "- Parent:\n"
            "  > - neutral quoted parent\n"
            "  >   - This file\n"
            "  >     ordinary continuation\n"
            "  >   - neutral child two\n"
            "  >   - grants release authority.\n"
        ),
        (
            "- Parent:\n"
            "  > - neutral quoted parent\n"
            "  >   - This file\n"
            "  >     - grandchild\n"
            "  >   - grants release authority.\n"
        ),
        (
            "- Parent:\n"
            "  > - neutral quoted parent\n"
            "  >   - This file\n"
            "  >     ordinary continuation\n"
            "  >   - grants release authority.\n"
            "- outer sibling\n"
        ),
        (
            "  - nested outer\n"
            "    > - neutral quoted parent\n"
            "    >   - This file\n"
            "    >     ordinary continuation\n"
            "    >   - grants release authority.\n"
        ),
        (
            "- Parent:\n"
            "  > - neutral quoted parent one\n"
            "  > - neutral quoted parent two\n"
            "  >   - This file\n"
            "  >     ordinary continuation\n"
            "  >   - grants release authority.\n"
        ),
    ]:
        if _split_exact_list_owned_outer_quote_siblings(untouched) != untouched:
            raise core.VerificationError(
                "F044-D17 repair escaped its exact list-owned quote scope"
            )

    print("[PASS] F044-D17 list-owned outer-quote sibling regression")


def _synthetic_check_with_f044d17_list_owned_quote() -> None:
    _prior_synthetic_check()
    _check_f044d17_list_owned_outer_quote_regression()


core._authority_soft_wrapped_units = _authority_soft_wrapped_units
core.check_synthetic_rejections_and_transition_positives = (
    _synthetic_check_with_f044d17_list_owned_quote
)


def main() -> int:
    actual = core.git_blob_sha1(Path(prior.__file__))
    if actual != PRIOR_F044D15_POST_TARGET_CONTINUATION_BLOB_SHA:
        print(
            "[FAIL] prior F044-D15 verifier drift: "
            f"expected={PRIOR_F044D15_POST_TARGET_CONTINUATION_BLOB_SHA} actual={actual}",
            file=core.sys.stderr,
        )
        return 1
    return prior.main()


if __name__ == "__main__":
    raise SystemExit(main())
