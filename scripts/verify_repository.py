#!/usr/bin/env python3
"""Bounded F044-D23 list-owned later-child-continuation overlay.

The repaired F044-D22 verifier is retained byte-for-byte at
`scripts/verify_repository_f044d22_two_sibling_multi_continuation.py` and pinned
by Git blob SHA. D23 lifts exactly the already-repaired D12 shape into the
existing source-column-zero outer-list-owned quote family: one quoted parent
list item, child one, child two with one-or-more ordinary continuation lines,
and one child-three sibling returning to the same child-marker indentation.

Continuation in child one remains delegated to D17-D22. Continuation in child
three or later, more preceding/later siblings, deeper nesting, block
transitions, multiple quoted parents, outer-list siblings, nested outer lists
and additional list-owned quote recursion remain outside this patch.
"""
from __future__ import annotations

from pathlib import Path
import verify_repository_f044d22_two_sibling_multi_continuation as prior

PRIOR_F044D22_BLOB_SHA = "ccf89daf24a4241331f62b363cc1a4358db5e07a"

core = prior.core
singleline = prior.singleline
_prior_authority_soft_wrapped_units = core._authority_soft_wrapped_units
_prior_synthetic_check = core.check_synthetic_rejections_and_transition_positives


def _split_list_owned_second_child_continuation(text: str) -> str:
    """Normalize outer-list -> quoted parent -> child1 -> child2+run -> child3."""
    lines = text.splitlines()
    output: list[str] = []
    index = 0

    while index < len(lines):
        if index + 5 >= len(lines):
            output.append(lines[index])
            index += 1
            continue
        if index != 0 and lines[index - 1].strip():
            output.append(lines[index])
            index += 1
            continue

        outer_raw = lines[index]
        quote_parent_raw = lines[index + 1]
        child_one_raw = lines[index + 2]
        child_two_raw = lines[index + 3]

        outer_layout = singleline._markdown_list_item_layout(outer_raw)
        if outer_layout is None:
            output.append(lines[index]); index += 1; continue
        outer_marker, outer_content_indent, outer_empty, _ = outer_layout
        if outer_empty or outer_marker != 0:
            output.append(lines[index]); index += 1; continue

        quote_parent = singleline._markdown_block_quote_layout(
            quote_parent_raw, allow_deep_indent=True
        )
        child_one_quote = singleline._markdown_block_quote_layout(
            child_one_raw, allow_deep_indent=True
        )
        child_two_quote = singleline._markdown_block_quote_layout(
            child_two_raw, allow_deep_indent=True
        )
        if quote_parent is None or child_one_quote is None or child_two_quote is None:
            output.append(lines[index]); index += 1; continue

        quote_indent, quote_parent_content = quote_parent
        child_one_quote_indent, child_one_content = child_one_quote
        child_two_quote_indent, child_two_content = child_two_quote
        if not (
            quote_indent == outer_content_indent
            and child_one_quote_indent == quote_indent
            and child_two_quote_indent == quote_indent
        ):
            output.append(lines[index]); index += 1; continue

        parent_list = singleline._markdown_list_item_layout(quote_parent_content)
        child_one_list = singleline._markdown_list_item_layout(
            child_one_content, allow_deep_indent=True
        )
        child_two_list = singleline._markdown_list_item_layout(
            child_two_content, allow_deep_indent=True
        )
        if parent_list is None or child_one_list is None or child_two_list is None:
            output.append(lines[index]); index += 1; continue

        parent_marker, parent_content_indent, parent_empty, _ = parent_list
        child_one_marker, _, child_one_empty, _ = child_one_list
        child_two_marker, child_two_content_indent, child_two_empty, _ = child_two_list
        if (
            parent_empty
            or child_one_empty
            or child_two_empty
            or parent_marker != 0
            or child_one_marker != parent_content_indent
            or child_two_marker != child_one_marker
        ):
            output.append(lines[index]); index += 1; continue

        continuation_indexes: list[int] = []
        child_three_index: int | None = None
        probe = index + 4
        while probe < len(lines) and lines[probe].strip():
            qlayout = singleline._markdown_block_quote_layout(
                lines[probe], allow_deep_indent=True
            )
            if qlayout is None or qlayout[0] != quote_indent:
                break
            content = qlayout[1]

            any_list = singleline._markdown_list_item_layout(
                content, allow_deep_indent=True
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
                content, child_two_content_indent
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
            output.append(lines[index]); index += 1; continue

        bounded_after = (
            child_three_index + 1 == len(lines)
            or not lines[child_three_index + 1].strip()
        )
        if not bounded_after:
            output.append(lines[index]); index += 1; continue

        output.extend([outer_raw, quote_parent_raw, child_one_raw])
        output.append("")
        output.extend([outer_raw, quote_parent_raw, child_two_raw])
        output.extend(lines[pos] for pos in continuation_indexes)
        output.append("")
        output.extend([outer_raw, quote_parent_raw, lines[child_three_index]])
        index = child_three_index + 1

    result = "\n".join(output)
    if text.endswith(("\n", "\r")):
        result += "\n"
    return result


def _authority_soft_wrapped_units(text: str) -> list[str]:
    return _prior_authority_soft_wrapped_units(
        _split_list_owned_second_child_continuation(text)
    )


def _check_f044d23_list_owned_later_child_continuation_regression() -> None:
    representative = (
        "- Parent:\n"
        "  > - neutral quoted parent\n"
        "  >   - child one\n"
        "  >   - This file\n"
        "  >     child two continuation\n"
        "  >   - grants release authority.\n"
    )
    prior_units = _prior_authority_soft_wrapped_units(representative)
    if not any(core.layer_b_self_promotion_claim(unit) for unit in prior_units):
        raise core.VerificationError(
            "F044-D23 predecessor no longer reproduces list-owned later-child finding"
        )
    core.validate_layer_b_non_authority_text("acceptance/inert.md", representative)

    # D12 already established continuation-run length as the same dimension.
    core.validate_layer_b_non_authority_text(
        "acceptance/inert.md",
        "- Parent:\n"
        "  > - neutral quoted parent\n"
        "  >   - child one\n"
        "  >   - This file\n"
        "  >     continuation one\n"
        "  >     continuation two\n"
        "  >   - grants release authority.\n",
    )

    # Both inherited parent contexts must remain visible to child three.
    core.expect_failure_message(
        "F044-D23 child three inherits outer-list self-reference",
        "publishes forbidden self-promotion",
        lambda: core.validate_layer_b_non_authority_text(
            "acceptance/inert.md",
            "- This file\n"
            "  > - neutral quoted parent\n"
            "  >   - child one\n"
            "  >   - child two\n"
            "  >     ordinary continuation\n"
            "  >   - grants release authority.\n",
        ),
    )
    core.expect_failure_message(
        "F044-D23 child three inherits quoted-parent self-reference",
        "publishes forbidden self-promotion",
        lambda: core.validate_layer_b_non_authority_text(
            "acceptance/inert.md",
            "- neutral outer\n"
            "  > - This file\n"
            "  >   - child one\n"
            "  >   - child two\n"
            "  >     ordinary continuation\n"
            "  >   - grants release authority.\n",
        ),
    )

    # Child-local self-reference must not leak to child three.
    core.validate_layer_b_non_authority_text(
        "acceptance/inert.md",
        "- neutral outer\n"
        "  > - neutral quoted parent\n"
        "  >   - This file\n"
        "  >   - child two\n"
        "  >     ordinary continuation\n"
        "  >   - grants release authority.\n",
    )
    core.validate_layer_b_non_authority_text(
        "acceptance/inert.md",
        "- neutral outer\n"
        "  > - neutral quoted parent\n"
        "  >   - child one\n"
        "  >   - This file\n"
        "  >     ordinary continuation\n"
        "  >   - grants release authority.\n",
    )

    # Top-level D12 remains delegated to the pinned predecessor.
    delegated_d12 = (
        "> - neutral parent\n"
        ">   - child one\n"
        ">   - This file\n"
        ">     child two continuation\n"
        ">   - grants release authority.\n"
    )
    if _split_list_owned_second_child_continuation(delegated_d12) != delegated_d12:
        raise core.VerificationError("F044-D23 escaped into top-level D12 scope")
    core.validate_layer_b_non_authority_text("acceptance/inert.md", delegated_d12)

    # Child-one continuation in this list-owned family remains delegated to D17-D22.
    delegated_child_one = (
        "- Parent:\n"
        "  > - neutral quoted parent\n"
        "  >   - This file\n"
        "  >     ordinary continuation\n"
        "  >   - grants release authority.\n"
    )
    if _split_list_owned_second_child_continuation(delegated_child_one) != delegated_child_one:
        raise core.VerificationError("F044-D23 escaped into child-one continuation scope")
    core.validate_layer_b_non_authority_text("acceptance/inert.md", delegated_child_one)

    # Adjacent shapes remain explicitly outside this one-position repair.
    for untouched in [
        (
            "- Parent:\n"
            "  > - neutral quoted parent\n"
            "  >   - child one\n"
            "  >   - child two\n"
            "  >     ordinary continuation\n"
            "  >   - child three\n"
            "  >     child three continuation\n"
            "  >   - grants release authority.\n"
        ),
        (
            "- Parent:\n"
            "  > - neutral quoted parent\n"
            "  >   - extra child zero\n"
            "  >   - child one\n"
            "  >   - child two\n"
            "  >     ordinary continuation\n"
            "  >   - grants release authority.\n"
        ),
        (
            "- Parent:\n"
            "  > - neutral quoted parent\n"
            "  >   - child one\n"
            "  >   - child two\n"
            "  >     ordinary continuation\n"
            "  >   - child three\n"
            "  >   - child four\n"
        ),
        (
            "- Parent:\n"
            "  > - neutral quoted parent\n"
            "  >   - child one\n"
            "  >   - child two\n"
            "  >     ordinary continuation\n"
            "  >     - grandchild\n"
            "  >   - grants release authority.\n"
        ),
        (
            "- Parent:\n"
            "  > - neutral quoted parent\n"
            "  >   - child one\n"
            "  >   - child two\n"
            "  >     ordinary continuation\n"
            "  >   - grants release authority.\n"
            "- outer sibling\n"
        ),
        (
            "  - nested outer\n"
            "    > - neutral quoted parent\n"
            "    >   - child one\n"
            "    >   - child two\n"
            "    >     ordinary continuation\n"
            "    >   - grants release authority.\n"
        ),
    ]:
        if _split_list_owned_second_child_continuation(untouched) != untouched:
            raise core.VerificationError("F044-D23 repair escaped bounded list-owned D12 scope")

    print("[PASS] F044-D23 list-owned later-child-continuation regression")


def _synthetic_check_with_f044d23() -> None:
    _prior_synthetic_check()
    _check_f044d23_list_owned_later_child_continuation_regression()


core._authority_soft_wrapped_units = _authority_soft_wrapped_units
core.check_synthetic_rejections_and_transition_positives = _synthetic_check_with_f044d23


def main() -> int:
    actual = core.git_blob_sha1(Path(prior.__file__))
    if actual != PRIOR_F044D22_BLOB_SHA:
        print(
            "[FAIL] prior F044-D22 verifier drift: "
            f"expected={PRIOR_F044D22_BLOB_SHA} actual={actual}",
            file=core.sys.stderr,
        )
        return 1
    return prior.main()


if __name__ == "__main__":
    raise SystemExit(main())
