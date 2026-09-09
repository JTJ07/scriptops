#!/usr/bin/env python3
"""Bounded F044-D20 list-owned post-continuation child-run overlay.

The repaired F044-D19 verifier is retained byte-for-byte at
`scripts/verify_repository_f044d19_list_owned_child_cardinality.py` and pinned
by Git blob SHA. D17 covers one sibling after exactly one continuation line and
D19 covers exactly two. D20 reproduces the same root cause with three sibling
markers. This layer generalizes only that cardinality dimension for runs of
three or more same-level nonempty child markers after exactly one continuation.

Longer continuation runs combined with this child-run shape, continuation in a
later child, deeper nesting, block transitions, multiple quoted parents,
outer-list siblings, nested outer lists and other list-owned quote recursion
remain outside.
"""
from __future__ import annotations

from pathlib import Path
import verify_repository_f044d19_list_owned_child_cardinality as prior

PRIOR_F044D19_LIST_OWNED_CARDINALITY_BLOB_SHA = (
    "0803d1d0bca814740f5336569c49b798e7fcdd46"
)

core = prior.core
singleline = prior.singleline
_prior_authority_soft_wrapped_units = core._authority_soft_wrapped_units
_prior_synthetic_check = core.check_synthetic_rejections_and_transition_positives


def _split_list_owned_post_continuation_child_run(text: str) -> str:
    lines = text.splitlines()
    output: list[str] = []
    index = 0

    while index < len(lines):
        if index + 6 >= len(lines):
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
        continuation_raw = lines[index + 3]

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
        continuation_quote = singleline._markdown_block_quote_layout(
            continuation_raw, allow_deep_indent=True
        )
        if quote_parent is None or child_one_quote is None or continuation_quote is None:
            output.append(lines[index]); index += 1; continue

        quote_indent, quote_parent_content = quote_parent
        child_quote_indent, child_one_content = child_one_quote
        continuation_quote_indent, continuation_content = continuation_quote
        if not (
            quote_indent == outer_content_indent
            and child_quote_indent == quote_indent
            and continuation_quote_indent == quote_indent
        ):
            output.append(lines[index]); index += 1; continue

        parent_list = singleline._markdown_list_item_layout(quote_parent_content)
        child_one_list = singleline._markdown_list_item_layout(
            child_one_content, allow_deep_indent=True
        )
        if parent_list is None or child_one_list is None:
            output.append(lines[index]); index += 1; continue
        parent_marker, parent_content_indent, parent_empty, _ = parent_list
        child_marker, child_content_indent, child_empty, _ = child_one_list
        if (
            parent_empty
            or child_empty
            or parent_marker != 0
            or child_marker != parent_content_indent
        ):
            output.append(lines[index]); index += 1; continue

        if singleline._markdown_list_item_layout(
            continuation_content, allow_deep_indent=True
        ) is not None:
            output.append(lines[index]); index += 1; continue
        relative = singleline._markdown_remove_leading_columns(
            continuation_content, child_content_indent
        )
        if (
            relative is None
            or not relative.strip()
            or not singleline._markdown_block_quote_lazy_paragraph(relative)
        ):
            output.append(lines[index]); index += 1; continue

        sibling_indexes: list[int] = []
        probe = index + 4
        while probe < len(lines) and lines[probe].strip():
            qlayout = singleline._markdown_block_quote_layout(
                lines[probe], allow_deep_indent=True
            )
            if qlayout is None or qlayout[0] != quote_indent:
                break
            layout = singleline._markdown_list_item_layout(
                qlayout[1], allow_deep_indent=True
            )
            if (
                layout is None
                or layout[2]
                or layout[0] != child_marker
            ):
                break
            sibling_indexes.append(probe)
            probe += 1

        bounded_after = probe == len(lines) or not lines[probe].strip()
        if len(sibling_indexes) < 3 or not bounded_after:
            output.append(lines[index]); index += 1; continue

        output.extend([outer_raw, quote_parent_raw, child_one_raw, continuation_raw])
        for sibling_index in sibling_indexes:
            output.append("")
            output.extend([outer_raw, quote_parent_raw, lines[sibling_index]])
        index = probe

    result = "\n".join(output)
    if text.endswith(("\n", "\r")):
        result += "\n"
    return result


def _authority_soft_wrapped_units(text: str) -> list[str]:
    return _prior_authority_soft_wrapped_units(
        _split_list_owned_post_continuation_child_run(text)
    )


def _check_f044d20_list_owned_cardinality_regression() -> None:
    representative = (
        "- Parent:\n"
        "  > - neutral quoted parent\n"
        "  >   - This file\n"
        "  >     ordinary continuation\n"
        "  >   - neutral child two\n"
        "  >   - neutral child three\n"
        "  >   - grants release authority.\n"
    )
    prior_units = _prior_authority_soft_wrapped_units(representative)
    if not any(core.layer_b_self_promotion_claim(unit) for unit in prior_units):
        raise core.VerificationError(
            "F044-D20 predecessor no longer reproduces four-child finding"
        )

    core.validate_layer_b_non_authority_text("acceptance/inert.md", representative)

    # One more sibling is the same proven cardinality dimension.
    core.validate_layer_b_non_authority_text(
        "acceptance/inert.md",
        "- Parent:\n"
        "  > - neutral quoted parent\n"
        "  >   - This file\n"
        "  >     ordinary continuation\n"
        "  >   - neutral child two\n"
        "  >   - neutral child three\n"
        "  >   - neutral child four\n"
        "  >   - grants release authority.\n",
    )

    core.expect_failure_message(
        "F044-D20 final sibling inherits outer-list self-reference",
        "publishes forbidden self-promotion",
        lambda: core.validate_layer_b_non_authority_text(
            "acceptance/inert.md",
            "- This file\n"
            "  > - neutral quoted parent\n"
            "  >   - child one\n"
            "  >     ordinary continuation\n"
            "  >   - neutral child two\n"
            "  >   - neutral child three\n"
            "  >   - grants release authority.\n",
        ),
    )
    core.expect_failure_message(
        "F044-D20 final sibling inherits quoted-parent self-reference",
        "publishes forbidden self-promotion",
        lambda: core.validate_layer_b_non_authority_text(
            "acceptance/inert.md",
            "- neutral outer\n"
            "  > - This file\n"
            "  >   - child one\n"
            "  >     ordinary continuation\n"
            "  >   - neutral child two\n"
            "  >   - neutral child three\n"
            "  >   - grants release authority.\n",
        ),
    )

    # Shorter sibling cardinalities stay delegated to D17/D19.
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
            "  >     ordinary continuation\n"
            "  >   - neutral child two\n"
            "  >   - grants release authority.\n"
        ),
    ]:
        if _split_list_owned_post_continuation_child_run(delegated) != delegated:
            raise core.VerificationError(
                "F044-D20 cardinality layer escaped into shorter delegated scope"
            )
        core.validate_layer_b_non_authority_text("acceptance/inert.md", delegated)

    for untouched in [
        (
            "- Parent:\n"
            "  > - neutral quoted parent\n"
            "  >   - This file\n"
            "  >     continuation one\n"
            "  >     continuation two\n"
            "  >   - neutral child two\n"
            "  >   - neutral child three\n"
            "  >   - grants release authority.\n"
        ),
        (
            "- Parent:\n"
            "  > - neutral quoted parent\n"
            "  >   - This file\n"
            "  >     ordinary continuation\n"
            "  >   - neutral child two\n"
            "  >     child-two continuation\n"
            "  >   - neutral child three\n"
            "  >   - grants release authority.\n"
        ),
        (
            "- Parent:\n"
            "  > - neutral quoted parent\n"
            "  >   - This file\n"
            "  >     - grandchild\n"
            "  >   - neutral child two\n"
            "  >   - neutral child three\n"
            "  >   - grants release authority.\n"
        ),
        (
            "- Parent:\n"
            "  > - neutral quoted parent\n"
            "  >   - This file\n"
            "  >     ordinary continuation\n"
            "  >   - neutral child two\n"
            "  >   - neutral child three\n"
            "  >   - grants release authority.\n"
            "- outer sibling\n"
        ),
    ]:
        if _split_list_owned_post_continuation_child_run(untouched) != untouched:
            raise core.VerificationError(
                "F044-D20 repair escaped its one-line cardinality scope"
            )

    print("[PASS] F044-D20 list-owned post-continuation child-run regression")


def _synthetic_check_with_f044d20_cardinality() -> None:
    _prior_synthetic_check()
    _check_f044d20_list_owned_cardinality_regression()


core._authority_soft_wrapped_units = _authority_soft_wrapped_units
core.check_synthetic_rejections_and_transition_positives = (
    _synthetic_check_with_f044d20_cardinality
)


def main() -> int:
    actual = core.git_blob_sha1(Path(prior.__file__))
    if actual != PRIOR_F044D19_LIST_OWNED_CARDINALITY_BLOB_SHA:
        print(
            "[FAIL] prior F044-D19 verifier drift: "
            f"expected={PRIOR_F044D19_LIST_OWNED_CARDINALITY_BLOB_SHA} actual={actual}",
            file=core.sys.stderr,
        )
        return 1
    return prior.main()


if __name__ == "__main__":
    raise SystemExit(main())
