#!/usr/bin/env python3
"""Bounded depth-generic F044 nested outer-list recursion overlay.

The repaired bounded depth=2 verifier is retained byte-for-byte at
`scripts/verify_repository_f044_nested_outer_depth2.py` and pinned by Git blob
SHA. This overlay replaces only the nested outer-list depth transition handling
with one structural recursion rule: starting from a source-column-zero list
item, follow repeated child list items whose marker indentation equals the
current owner's content indentation until the owned block quote is reached.

The rule never consults a numeric recursion depth. It remains limited to the
same semantic shape already isolated by the depth=2 repair: one quoted parent,
one child with exactly one ordinary continuation, and one same-level sibling.
Multiple quoted parents, block transitions, blank/fence/HTML boundaries,
outer-list siblings, continuation-run generalization, and other F044 dimensions
remain outside this repair.
"""
from __future__ import annotations

from pathlib import Path
import verify_repository_f044_nested_outer_depth2 as prior

PRIOR_DEPTH2_BLOB_SHA = "98ef815bd246d600a64de3f379ebd0d7483aa21d"

core = prior.core
singleline = prior.singleline
_prior_authority_soft_wrapped_units = core._authority_soft_wrapped_units
_prior_synthetic_check = core.check_synthetic_rejections_and_transition_positives


def _split_recursive_outer_list_owned_quote_siblings(text: str) -> str:
    """Split the bounded quote sibling shape across any structural owner chain."""
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

        if probe + 3 >= len(lines):
            output.append(lines[index])
            index += 1
            continue

        quote_parent_raw = lines[probe]
        child_raw = lines[probe + 1]
        continuation_raw = lines[probe + 2]
        sibling_raw = lines[probe + 3]
        bounded_after = probe + 4 == len(lines) or not lines[probe + 4].strip()
        if not bounded_after:
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
            quote_indent == owner_content_indent
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

        output.extend(owners)
        output.extend([quote_parent_raw, child_raw, continuation_raw, ""])
        output.extend(owners)
        output.extend([quote_parent_raw, sibling_raw])
        index = probe + 4

    result = "\n".join(output)
    if text.endswith(("\n", "\r")):
        result += "\n"
    return result


def _authority_soft_wrapped_units(text: str) -> list[str]:
    return _prior_authority_soft_wrapped_units(
        _split_recursive_outer_list_owned_quote_siblings(text)
    )


def _depth_invariance_source(
    depth: int,
    *,
    owner_self_reference_index: int | None = None,
    child_text: str = "This file",
    continuation_text: str = "ordinary continuation",
    sibling_text: str = "grants release authority.",
) -> str:
    if depth < 1:
        raise ValueError("depth must be positive")
    if owner_self_reference_index is not None and not 0 <= owner_self_reference_index < depth:
        raise ValueError("owner_self_reference_index outside owner chain")

    lines: list[str] = []
    for level in range(depth):
        label = "This file" if level == owner_self_reference_index else "neutral outer owner"
        lines.append(f"{'  ' * level}- {label}")

    quote_prefix = "  " * depth
    lines.extend(
        [
            f"{quote_prefix}> - neutral quoted parent",
            f"{quote_prefix}>   - {child_text}",
            f"{quote_prefix}>     {continuation_text}",
            f"{quote_prefix}>   - {sibling_text}",
        ]
    )
    return "\n".join(lines) + "\n"


def _semantic_payload_signature(source: str) -> tuple[str, ...]:
    return tuple(
        line.lstrip()
        for line in source.splitlines()
        if line.lstrip() != "- neutral outer owner"
    )


def _assert_intermediate_ownership_separation(source: str, depth: int) -> None:
    transformed = _split_recursive_outer_list_owned_quote_siblings(source)
    if transformed == source:
        raise core.VerificationError(
            f"F044 depth-generic rule did not cover recursion depth={depth}"
        )

    units = _prior_authority_soft_wrapped_units(transformed)
    normalized = [unit.upper() for unit in units]
    self_units = [unit for unit in normalized if "THIS FILE" in unit]
    promotion_units = [
        unit for unit in normalized if "GRANTS RELEASE AUTHORITY" in unit
    ]
    if not self_units or not promotion_units:
        raise core.VerificationError(
            f"F044 ownership invariant lost required semantic fragments at depth={depth}"
        )
    if any(
        "THIS FILE" in unit and "GRANTS RELEASE AUTHORITY" in unit
        for unit in normalized
    ):
        raise core.VerificationError(
            f"F044 ownership invariant fused separated fragments at depth={depth}"
        )


def _check_f044_depth_generic_recursion_regression() -> None:
    historical_depth_three = _depth_invariance_source(3)
    prior_units = _prior_authority_soft_wrapped_units(historical_depth_three)
    if not any(core.layer_b_self_promotion_claim(unit) for unit in prior_units):
        raise core.VerificationError(
            "F044 depth-generic predecessor no longer reproduces depth=3 finding"
        )

    baseline_signature: tuple[str, ...] | None = None
    for depth in range(1, 17):
        source = _depth_invariance_source(depth)
        signature = _semantic_payload_signature(source)
        if baseline_signature is None:
            baseline_signature = signature
        elif signature != baseline_signature:
            raise core.VerificationError(
                "F044 depth-invariance generator changed semantic payload shape"
            )

        _assert_intermediate_ownership_separation(source, depth)
        core.validate_layer_b_non_authority_text("acceptance/inert.md", source)

    for depth in (1, 2, 3):
        core.validate_layer_b_non_authority_text(
            "acceptance/inert.md",
            _depth_invariance_source(depth),
        )

    deep_outer_self_reference = _depth_invariance_source(
        16,
        owner_self_reference_index=0,
        child_text="neutral child",
    )
    core.expect_failure_message(
        "F044 depth-generic recursion preserves outer-owner self-promotion",
        "publishes forbidden self-promotion",
        lambda: core.validate_layer_b_non_authority_text(
            "acceptance/inert.md", deep_outer_self_reference
        ),
    )

    deep_inner_owner_self_reference = _depth_invariance_source(
        16,
        owner_self_reference_index=15,
        child_text="neutral child",
    )
    core.expect_failure_message(
        "F044 depth-generic recursion preserves deepest-owner self-promotion",
        "publishes forbidden self-promotion",
        lambda: core.validate_layer_b_non_authority_text(
            "acceptance/inert.md", deep_inner_owner_self_reference
        ),
    )

    same_child_self_promotion = _depth_invariance_source(
        16,
        continuation_text="grants release authority.",
        sibling_text="neutral sibling",
    )
    core.expect_failure_message(
        "F044 depth-generic recursion preserves same-child security context",
        "publishes forbidden self-promotion",
        lambda: core.validate_layer_b_non_authority_text(
            "acceptance/inert.md", same_child_self_promotion
        ),
    )

    multiple_continuations = _depth_invariance_source(8).replace(
        "                >     ordinary continuation\n",
        "                >     continuation one\n"
        "                >     continuation two\n",
        1,
    )
    if (
        _split_recursive_outer_list_owned_quote_siblings(multiple_continuations)
        != multiple_continuations
    ):
        raise core.VerificationError(
            "F044 depth-generic repair escaped into continuation-run dimension"
        )

    print("[PASS] F044 nested outer-list depth=1,2,3 regression under common rule")
    print("[PASS] F044 depth-invariance property depth=1..16 constant semantic shape")
    print("[PASS] F044 depth-generic intermediate ownership separation invariant")
    print("[PASS] F044 depth-generic repair remains bounded to isolated recursion shape")


def _synthetic_check_with_f044_depth_generic_recursion() -> None:
    _prior_synthetic_check()
    _check_f044_depth_generic_recursion_regression()


core._authority_soft_wrapped_units = _authority_soft_wrapped_units
core.check_synthetic_rejections_and_transition_positives = (
    _synthetic_check_with_f044_depth_generic_recursion
)


def main() -> int:
    actual = core.git_blob_sha1(Path(prior.__file__))
    if actual != PRIOR_DEPTH2_BLOB_SHA:
        print(
            "[FAIL] prior bounded depth=2 F044 verifier drift: "
            f"expected={PRIOR_DEPTH2_BLOB_SHA} actual={actual}",
            file=core.sys.stderr,
        )
        return 1
    return prior.main()


if __name__ == "__main__":
    raise SystemExit(main())
