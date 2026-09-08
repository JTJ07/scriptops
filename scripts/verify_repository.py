#!/usr/bin/env python3
"""Bounded F044 multiple quoted-parent sibling-separation overlay.

The repaired depth-generic F044 verifier is retained byte-for-byte at
`scripts/verify_repository_f044_depth_generic_recursion.py` and pinned by Git
blob SHA. This overlay changes only sibling quoted-parent scope separation:
when a new quoted parent item begins at the same quote/list level, the previous
quoted parent's scope ends before authority units are folded.

This is a structural sibling-boundary rule, not a parent-count enumeration.
Outer-list sibling transitions, block transitions, new recursion-depth variants,
parent-count sweeps and other independent F044 dimensions remain outside scope.
"""
from __future__ import annotations

from pathlib import Path
import verify_repository_f044_depth_generic_recursion as prior

PRIOR_DEPTH_GENERIC_BLOB_SHA = "8535941463926c4b9101fc462e56eaa28aebf099"

core = prior.core
singleline = prior.singleline
_prior_authority_soft_wrapped_units = core._authority_soft_wrapped_units
_prior_synthetic_check = core.check_synthetic_rejections_and_transition_positives


def _quoted_layout_at(raw_line: str, quote_indent: int) -> tuple[int, str] | None:
    layout = singleline._markdown_block_quote_layout(
        raw_line,
        allow_deep_indent=True,
    )
    if layout is None or layout[0] != quote_indent:
        return None
    return layout


def _quoted_parent_layout(
    raw_line: str,
    quote_indent: int,
) -> tuple[int, int, bool, bool] | None:
    quote = _quoted_layout_at(raw_line, quote_indent)
    if quote is None:
        return None
    layout = singleline._markdown_list_item_layout(quote[1])
    if layout is None or layout[2] or layout[0] != 0:
        return None
    return layout


def _collect_bounded_parent_group(
    lines: list[str],
    start: int,
    quote_indent: int,
) -> tuple[list[str], int] | None:
    """Collect one parent -> exactly one child -> optional one ordinary line."""
    parent = _quoted_parent_layout(lines[start], quote_indent)
    if parent is None:
        return None
    _, parent_content_indent, _, _ = parent

    child_index = start + 1
    if child_index >= len(lines) or not lines[child_index].strip():
        return None
    child_quote = _quoted_layout_at(lines[child_index], quote_indent)
    if child_quote is None:
        return None
    child = singleline._markdown_list_item_layout(
        child_quote[1],
        allow_deep_indent=True,
    )
    if child is None or child[2] or child[0] != parent_content_indent:
        return None
    _, child_content_indent, _, _ = child

    group = [lines[start], lines[child_index]]
    probe = child_index + 1

    if probe < len(lines) and lines[probe].strip():
        if _quoted_parent_layout(lines[probe], quote_indent) is not None:
            return group, probe

        continuation_quote = _quoted_layout_at(lines[probe], quote_indent)
        if continuation_quote is None:
            return None
        if (
            singleline._markdown_list_item_layout(
                continuation_quote[1],
                allow_deep_indent=True,
            )
            is not None
        ):
            return None
        relative = singleline._markdown_remove_leading_columns(
            continuation_quote[1],
            child_content_indent,
        )
        if (
            relative is None
            or not relative.strip()
            or not singleline._markdown_block_quote_lazy_paragraph(relative)
        ):
            return None
        group.append(lines[probe])
        probe += 1

    return group, probe


def _split_sibling_quoted_parents(text: str) -> str:
    """Separate sibling quoted parents while preserving their outer owner path."""
    lines = text.splitlines()
    output: list[str] = []
    index = 0

    while index < len(lines):
        bounded_before = index == 0 or not lines[index - 1].strip()
        first_owner = singleline._markdown_list_item_layout(lines[index])
        if (
            not bounded_before
            or first_owner is None
            or first_owner[2]
            or first_owner[0] != 0
        ):
            output.append(lines[index])
            index += 1
            continue

        owners = [lines[index]]
        owner_content_indent = first_owner[1]
        probe = index + 1

        while probe < len(lines):
            nested_owner = singleline._markdown_list_item_layout(
                lines[probe],
                allow_deep_indent=True,
            )
            if (
                nested_owner is None
                or nested_owner[2]
                or nested_owner[0] != owner_content_indent
            ):
                break
            owners.append(lines[probe])
            owner_content_indent = nested_owner[1]
            probe += 1

        if probe >= len(lines):
            output.append(lines[index])
            index += 1
            continue

        first_quote = singleline._markdown_block_quote_layout(
            lines[probe],
            allow_deep_indent=True,
        )
        if first_quote is None or first_quote[0] != owner_content_indent:
            output.append(lines[index])
            index += 1
            continue
        quote_indent = first_quote[0]

        groups: list[list[str]] = []
        group_probe = probe
        invalid = False
        while group_probe < len(lines) and lines[group_probe].strip():
            collected = _collect_bounded_parent_group(
                lines,
                group_probe,
                quote_indent,
            )
            if collected is None:
                invalid = True
                break
            group, next_probe = collected
            groups.append(group)
            group_probe = next_probe

            if group_probe >= len(lines) or not lines[group_probe].strip():
                break
            if _quoted_parent_layout(lines[group_probe], quote_indent) is None:
                invalid = True
                break

        bounded_after = group_probe == len(lines) or not lines[group_probe].strip()
        if invalid or len(groups) < 2 or not bounded_after:
            output.append(lines[index])
            index += 1
            continue

        for group_number, group in enumerate(groups):
            if group_number:
                output.append("")
            output.extend(owners)
            output.extend(group)

        index = group_probe

    result = "\n".join(output)
    if text.endswith(("\n", "\r")):
        result += "\n"
    return result


def _authority_soft_wrapped_units(text: str) -> list[str]:
    return _prior_authority_soft_wrapped_units(
        _split_sibling_quoted_parents(text)
    )


def _control_one_parent() -> str:
    return (
        "- neutral outer\n"
        "  > - neutral quoted parent A\n"
        "  >   - This file\n"
        "  >     ordinary continuation\n"
        "  >   - grants release authority.\n"
    )


def _two_parent_finding() -> str:
    return (
        "- neutral outer\n"
        "  > - neutral quoted parent A\n"
        "  >   - This file\n"
        "  >     ordinary continuation\n"
        "  > - neutral quoted parent B\n"
        "  >   - grants release authority.\n"
    )


def _check_f044_multiple_quoted_parents_regression() -> None:
    control = _control_one_parent()
    if _split_sibling_quoted_parents(control) != control:
        raise core.VerificationError(
            "F044 multiple-parent repair modified one-parent control"
        )
    core.validate_layer_b_non_authority_text("acceptance/inert.md", control)

    finding = _two_parent_finding()
    prior_units = _prior_authority_soft_wrapped_units(finding)
    if not any(core.layer_b_self_promotion_claim(unit) for unit in prior_units):
        raise core.VerificationError(
            "F044 multiple-parent predecessor no longer reproduces parent-scope finding"
        )

    transformed = _split_sibling_quoted_parents(finding)
    if transformed == finding:
        raise core.VerificationError(
            "F044 multiple-parent structural boundary did not transform reproduced finding"
        )
    transformed_units = _prior_authority_soft_wrapped_units(transformed)
    if any(
        "THIS FILE" in unit.upper()
        and "GRANTS RELEASE AUTHORITY" in unit.upper()
        for unit in transformed_units
    ):
        raise core.VerificationError(
            "F044 multiple-parent boundary still fuses sibling parent scopes"
        )
    core.validate_layer_b_non_authority_text("acceptance/inert.md", finding)

    outer_self_reference = finding.replace(
        "- neutral outer\n",
        "- This file\n",
        1,
    ).replace(
        "  >   - This file\n",
        "  >   - neutral child\n",
        1,
    )
    core.expect_failure_message(
        "F044 multiple-parent split preserves outer-owner self-promotion",
        "publishes forbidden self-promotion",
        lambda: core.validate_layer_b_non_authority_text(
            "acceptance/inert.md", outer_self_reference
        ),
    )

    same_parent_self_promotion = finding.replace(
        "  >     ordinary continuation\n",
        "  >     grants release authority.\n",
        1,
    ).replace(
        "  >   - grants release authority.\n",
        "  >   - neutral child B\n",
        1,
    )
    core.expect_failure_message(
        "F044 multiple-parent split preserves same-parent child self-promotion",
        "publishes forbidden self-promotion",
        lambda: core.validate_layer_b_non_authority_text(
            "acceptance/inert.md", same_parent_self_promotion
        ),
    )

    print("[PASS] F044 one-quoted-parent control remains GREEN")
    print("[PASS] F044 multiple quoted parents parent-scope separation regression")
    print("[PASS] F044 multiple-parent implementation is structural, not count-enumerated")


def _synthetic_check_with_f044_multiple_quoted_parents() -> None:
    _prior_synthetic_check()
    _check_f044_multiple_quoted_parents_regression()


core._authority_soft_wrapped_units = _authority_soft_wrapped_units
core.check_synthetic_rejections_and_transition_positives = (
    _synthetic_check_with_f044_multiple_quoted_parents
)


def main() -> int:
    actual = core.git_blob_sha1(Path(prior.__file__))
    if actual != PRIOR_DEPTH_GENERIC_BLOB_SHA:
        print(
            "[FAIL] prior depth-generic F044 verifier drift: "
            f"expected={PRIOR_DEPTH_GENERIC_BLOB_SHA} actual={actual}",
            file=core.sys.stderr,
        )
        return 1
    return prior.main()


if __name__ == "__main__":
    raise SystemExit(main())
