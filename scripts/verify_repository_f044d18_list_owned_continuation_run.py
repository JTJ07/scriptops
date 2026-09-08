#!/usr/bin/env python3
"""Bounded F044-D18 list-owned quote continuation-run overlay.

The repaired F044-D17 verifier is retained byte-for-byte at
`scripts/verify_repository_f044d17_list_owned_outer_quote.py` and pinned by Git
blob SHA. D17 repairs exactly one ordinary continuation line in one exact
list-owned outer-quote child/sibling shape. D18 non-vacuously reproduces the
same root cause with two continuation lines. This layer generalizes only that
continuation-run-length dimension for runs of two or more lines.

Exactly one continuation line remains delegated to D17. Additional child
siblings, deeper nesting, block transitions, multiple quoted parents, outer-list
siblings, nested outer lists and other list-owned quote recursion remain outside.
"""
from __future__ import annotations

from pathlib import Path
import verify_repository_f044d17_list_owned_outer_quote as prior

PRIOR_F044D17_LIST_OWNED_QUOTE_BLOB_SHA = (
    "bb159df7a1920b952d7a65ea741cca2460128b00"
)

core = prior.core
singleline = prior.singleline
_prior_authority_soft_wrapped_units = core._authority_soft_wrapped_units
_prior_synthetic_check = core.check_synthetic_rejections_and_transition_positives


def _split_list_owned_quote_continuation_run(text: str) -> str:
    """Normalize D17 shape only when child-one owns >=2 ordinary lines."""
    lines = text.splitlines()
    output: list[str] = []
    index = 0

    while index < len(lines):
        bounded_before = index == 0 or not lines[index - 1].strip()
        if not bounded_before or index + 5 >= len(lines):
            output.append(lines[index])
            index += 1
            continue

        outer_raw = lines[index]
        quote_parent_raw = lines[index + 1]
        child_one_raw = lines[index + 2]

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
        if quote_parent_layout is None or child_one_quote is None:
            output.append(lines[index])
            index += 1
            continue

        quote_indent, quote_parent_content = quote_parent_layout
        child_one_quote_indent, child_one_content = child_one_quote
        if quote_indent != outer_content_indent or child_one_quote_indent != quote_indent:
            output.append(lines[index])
            index += 1
            continue

        quoted_parent_list = singleline._markdown_list_item_layout(quote_parent_content)
        child_one_list = singleline._markdown_list_item_layout(
            child_one_content,
            allow_deep_indent=True,
        )
        if quoted_parent_list is None or child_one_list is None:
            output.append(lines[index])
            index += 1
            continue

        quoted_parent_marker, quoted_parent_content_indent, quoted_parent_empty, _ = (
            quoted_parent_list
        )
        child_one_marker, child_one_content_indent, child_one_empty, _ = child_one_list
        if (
            quoted_parent_empty
            or child_one_empty
            or quoted_parent_marker != 0
            or child_one_marker != quoted_parent_content_indent
        ):
            output.append(lines[index])
            index += 1
            continue

        continuation_indexes: list[int] = []
        probe = index + 3
        child_two_index: int | None = None

        while probe < len(lines) and lines[probe].strip():
            quote_layout = singleline._markdown_block_quote_layout(
                lines[probe],
                allow_deep_indent=True,
            )
            if quote_layout is None or quote_layout[0] != quote_indent:
                break
            _, content = quote_layout

            list_layout = singleline._markdown_list_item_layout(
                content,
                allow_deep_indent=True,
            )
            if list_layout is not None:
                if (
                    len(continuation_indexes) >= 2
                    and not list_layout[2]
                    and list_layout[0] == child_one_marker
                ):
                    child_two_index = probe
                break

            relative = singleline._markdown_remove_leading_columns(
                content,
                child_one_content_indent,
            )
            if (
                relative is None
                or not relative.strip()
                or not singleline._markdown_block_quote_lazy_paragraph(relative)
            ):
                break

            continuation_indexes.append(probe)
            probe += 1

        if child_two_index is None:
            output.append(lines[index])
            index += 1
            continue

        bounded_after = (
            child_two_index + 1 == len(lines)
            or not lines[child_two_index + 1].strip()
        )
        if not bounded_after:
            output.append(lines[index])
            index += 1
            continue

        output.extend([outer_raw, quote_parent_raw, child_one_raw])
        output.extend(lines[pos] for pos in continuation_indexes)
        output.append("")
        output.extend([outer_raw, quote_parent_raw, lines[child_two_index]])
        index = child_two_index + 1

    result = "\n".join(output)
    if text.endswith(("\n", "\r")):
        result += "\n"
    return result


def _authority_soft_wrapped_units(text: str) -> list[str]:
    return _prior_authority_soft_wrapped_units(
        _split_list_owned_quote_continuation_run(text)
    )


def _check_f044d18_list_owned_continuation_run_regression() -> None:
    representative = (
        "- Parent:\n"
        "  > - neutral quoted parent\n"
        "  >   - This file\n"
        "  >     continuation one\n"
        "  >     continuation two\n"
        "  >   - grants release authority.\n"
    )

    prior_units = _prior_authority_soft_wrapped_units(representative)
    if not any(core.layer_b_self_promotion_claim(unit) for unit in prior_units):
        raise core.VerificationError(
            "F044-D18 predecessor no longer reproduces two-continuation finding"
        )

    expected = (
        "- Parent:\n"
        "  > - neutral quoted parent\n"
        "  >   - This file\n"
        "  >     continuation one\n"
        "  >     continuation two\n"
        "\n"
        "- Parent:\n"
        "  > - neutral quoted parent\n"
        "  >   - grants release authority.\n"
    )
    actual = _split_list_owned_quote_continuation_run(representative)
    if actual != expected:
        raise core.VerificationError(
            "F044-D18 continuation-run normalization mismatch: "
            f"expected={expected!r} actual={actual!r}"
        )

    core.validate_layer_b_non_authority_text("acceptance/inert.md", representative)

    # Three lines are the same newly proven run-length dimension.
    core.validate_layer_b_non_authority_text(
        "acceptance/inert.md",
        "- Parent:\n"
        "  > - neutral quoted parent\n"
        "  >   - This file\n"
        "  >     continuation one\n"
        "  >     continuation two\n"
        "  >     continuation three\n"
        "  >   - grants release authority.\n",
    )

    # Outer and quoted-parent authority context remains inherited by child two.
    core.expect_failure_message(
        "F044-D18 sibling inherits outer-list self-reference",
        "publishes forbidden self-promotion",
        lambda: core.validate_layer_b_non_authority_text(
            "acceptance/inert.md",
            "- This file\n"
            "  > - neutral quoted parent\n"
            "  >   - child one\n"
            "  >     continuation one\n"
            "  >     continuation two\n"
            "  >   - grants release authority.\n",
        ),
    )
    core.expect_failure_message(
        "F044-D18 sibling inherits quoted-parent self-reference",
        "publishes forbidden self-promotion",
        lambda: core.validate_layer_b_non_authority_text(
            "acceptance/inert.md",
            "- neutral outer\n"
            "  > - This file\n"
            "  >   - child one\n"
            "  >     continuation one\n"
            "  >     continuation two\n"
            "  >   - grants release authority.\n",
        ),
    )

    # Exactly one continuation remains delegated to D17 and must not be
    # rewritten by this D18 layer itself.
    delegated_one = (
        "- Parent:\n"
        "  > - neutral quoted parent\n"
        "  >   - This file\n"
        "  >     ordinary continuation\n"
        "  >   - grants release authority.\n"
    )
    if _split_list_owned_quote_continuation_run(delegated_one) != delegated_one:
        raise core.VerificationError(
            "F044-D18 run-length generalizer escaped into D17 one-line scope"
        )
    core.validate_layer_b_non_authority_text("acceptance/inert.md", delegated_one)

    # Neighboring structural families stay outside this run-length repair.
    for untouched in [
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
            "  >     continuation one\n"
            "  >     - grandchild\n"
            "  >   - grants release authority.\n"
        ),
        (
            "- Parent:\n"
            "  > - neutral quoted parent\n"
            "  >   - This file\n"
            "  >     continuation one\n"
            "  >     continuation two\n"
            "  >   - grants release authority.\n"
            "- outer sibling\n"
        ),
        (
            "  - nested outer\n"
            "    > - neutral quoted parent\n"
            "    >   - This file\n"
            "    >     continuation one\n"
            "    >     continuation two\n"
            "    >   - grants release authority.\n"
        ),
    ]:
        if _split_list_owned_quote_continuation_run(untouched) != untouched:
            raise core.VerificationError(
                "F044-D18 repair escaped its bounded run-length scope"
            )

    print("[PASS] F044-D18 list-owned quote continuation-run regression")


def _synthetic_check_with_f044d18_continuation_run() -> None:
    _prior_synthetic_check()
    _check_f044d18_list_owned_continuation_run_regression()


core._authority_soft_wrapped_units = _authority_soft_wrapped_units
core.check_synthetic_rejections_and_transition_positives = (
    _synthetic_check_with_f044d18_continuation_run
)


def main() -> int:
    actual = core.git_blob_sha1(Path(prior.__file__))
    if actual != PRIOR_F044D17_LIST_OWNED_QUOTE_BLOB_SHA:
        print(
            "[FAIL] prior F044-D17 verifier drift: "
            f"expected={PRIOR_F044D17_LIST_OWNED_QUOTE_BLOB_SHA} actual={actual}",
            file=core.sys.stderr,
        )
        return 1
    return prior.main()


if __name__ == "__main__":
    raise SystemExit(main())
