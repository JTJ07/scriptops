#!/usr/bin/env python3
"""Bounded position-generic F044 tail-sibling ownership overlay.

The repaired F044-D39 verifier is retained byte-for-byte at
`scripts/verify_repository_f044d39_fifth_following_continuation_run.py` and
pinned by Git blob SHA. This overlay replaces the D30-D40 positional ladder
with one rule inside the same source-column-zero outer-list-owned quote family:
a bounded tail of same-level quoted siblings is collected with each sibling's
own ordinary continuation run and split by sibling ownership, independent of
its ordinal position.

The scope remains the existing F044 tail-sibling parser boundary only. Deeper
nesting, block transitions, multiple quoted parents, outer-list siblings,
nested outer lists and further recursion remain outside this repair.
"""
from __future__ import annotations

from pathlib import Path
import verify_repository_f044d39_fifth_following_continuation_run as prior

PRIOR_F044D39_BLOB_SHA = "14a99f1bce97a08c84eb1cee2c1245af93b7fab3"

core = prior.core
singleline = prior.singleline
d28 = prior.d28
_prior_authority_soft_wrapped_units = core._authority_soft_wrapped_units
_prior_synthetic_check = core.check_synthetic_rejections_and_transition_positives


def _split_position_generic_tail_siblings(text: str) -> str:
    """Split the bounded F044 tail by ownership, never by sibling ordinal."""
    lines = text.splitlines()
    output: list[str] = []
    index = 0

    while index < len(lines):
        if index + 1 >= len(lines):
            output.append(lines[index]); index += 1; continue
        if index != 0 and lines[index - 1].strip():
            output.append(lines[index]); index += 1; continue

        outer_raw = lines[index]
        quote_parent_raw = lines[index + 1]
        outer_layout = singleline._markdown_list_item_layout(outer_raw)
        if outer_layout is None:
            output.append(lines[index]); index += 1; continue
        outer_marker, outer_content_indent, outer_empty, _ = outer_layout
        if outer_empty or outer_marker != 0:
            output.append(lines[index]); index += 1; continue

        quote_parent = singleline._markdown_block_quote_layout(
            quote_parent_raw, allow_deep_indent=True
        )
        if quote_parent is None or quote_parent[0] != outer_content_indent:
            output.append(lines[index]); index += 1; continue
        quote_indent, quote_parent_content = quote_parent

        parent_list = singleline._markdown_list_item_layout(quote_parent_content)
        if parent_list is None or parent_list[2] or parent_list[0] != 0:
            output.append(lines[index]); index += 1; continue
        _, child_marker_indent, _, _ = parent_list

        child_indexes: list[int] = []
        child_content_indents: list[int] = []
        probe = index + 2
        while probe < len(lines) and lines[probe].strip():
            qlayout = singleline._markdown_block_quote_layout(
                lines[probe], allow_deep_indent=True
            )
            if qlayout is None or qlayout[0] != quote_indent:
                break
            layout = singleline._markdown_list_item_layout(
                qlayout[1], allow_deep_indent=True
            )
            if layout is None or layout[2] or layout[0] != child_marker_indent:
                break
            child_indexes.append(probe)
            child_content_indents.append(layout[1])
            probe += 1

        if len(child_indexes) < 3:
            output.append(lines[index]); index += 1; continue

        target_index = child_indexes[-1]
        target_run, probe = d28._collect_quote_owned_ordinary_run(
            lines, probe, quote_indent, child_content_indents[-1]
        )
        if not target_run:
            output.append(lines[index]); index += 1; continue

        post_layout = d28._quoted_same_level_nonempty_item(
            lines, probe, quote_indent, child_marker_indent
        )
        if post_layout is None:
            output.append(lines[index]); index += 1; continue
        post_index = probe
        post_run, probe = d28._collect_quote_owned_ordinary_run(
            lines, post_index + 1, quote_indent, post_layout[1]
        )
        if not post_run:
            output.append(lines[index]); index += 1; continue

        final_layout = d28._quoted_same_level_nonempty_item(
            lines, probe, quote_indent, child_marker_indent
        )
        if final_layout is None:
            output.append(lines[index]); index += 1; continue
        final_index = probe
        final_run, probe = d28._collect_quote_owned_ordinary_run(
            lines, final_index + 1, quote_indent, final_layout[1]
        )
        if not final_run:
            output.append(lines[index]); index += 1; continue

        tail: list[tuple[int, list[int]]] = []
        while probe < len(lines) and lines[probe].strip():
            layout = d28._quoted_same_level_nonempty_item(
                lines, probe, quote_indent, child_marker_indent
            )
            if layout is None:
                break
            sibling_index = probe
            run, probe = d28._collect_quote_owned_ordinary_run(
                lines, sibling_index + 1, quote_indent, layout[1]
            )
            tail.append((sibling_index, run))

        bounded_after = probe == len(lines) or not lines[probe].strip()
        has_continued_sibling_with_later_peer = any(
            run and position + 1 < len(tail)
            for position, (_, run) in enumerate(tail)
        )
        if (
            len(tail) < 2
            or not bounded_after
            or not has_continued_sibling_with_later_peer
        ):
            output.append(lines[index]); index += 1; continue

        for child_index in child_indexes[:-1]:
            output.extend([outer_raw, quote_parent_raw, lines[child_index], ""])

        output.extend([outer_raw, quote_parent_raw, lines[target_index]])
        output.extend(lines[pos] for pos in target_run)
        output.append("")

        output.extend([outer_raw, quote_parent_raw, lines[post_index]])
        output.extend(lines[pos] for pos in post_run)
        output.append("")

        output.extend([outer_raw, quote_parent_raw, lines[final_index]])
        output.extend(lines[pos] for pos in final_run)

        for sibling_index, run in tail:
            output.append("")
            output.extend([outer_raw, quote_parent_raw, lines[sibling_index]])
            output.extend(lines[pos] for pos in run)

        index = probe

    result = "\n".join(output)
    if text.endswith(("\n", "\r")):
        result += "\n"
    return result


def _authority_soft_wrapped_units(text: str) -> list[str]:
    return _prior_authority_soft_wrapped_units(
        _split_position_generic_tail_siblings(text)
    )


def _position_invariance_source(
    continuation_position: int,
    *,
    run_length: int,
    tail_count: int = 24,
) -> str:
    if not 1 <= continuation_position <= tail_count:
        raise ValueError("continuation_position outside fixed tail topology")
    if run_length < 1:
        raise ValueError("run_length must be positive")

    lines = [
        "- Parent:",
        "  > - neutral quoted parent",
        "  >   - child one",
        "  >   - child two",
        "  >   - This file",
        "  >     target continuation",
        "  >   - neutral post-target",
        "  >     post-target continuation",
        "  >   - neutral final",
        "  >     final continuation",
    ]

    for position in range(1, tail_count + 1):
        lines.append(f"  >   - neutral invariant tail {position:02d}")
        if position == continuation_position:
            lines.extend(
                f"  >     position-invariance continuation {ordinal}"
                for ordinal in range(1, run_length + 1)
            )

    lines.append("  >   - grants release authority.")
    return "\n".join(lines) + "\n"


def _shape_without_variable_continuation(source: str) -> tuple[str, ...]:
    return tuple(
        line
        for line in source.splitlines()
        if "position-invariance continuation " not in line
    )


def _security_tail_self_promotion_source() -> str:
    return (
        "- neutral outer:\n"
        "  > - neutral quoted parent\n"
        "  >   - child one\n"
        "  >   - child two\n"
        "  >   - neutral target\n"
        "  >     target continuation\n"
        "  >   - neutral post-target\n"
        "  >     post-target continuation\n"
        "  >   - neutral final\n"
        "  >     final continuation\n"
        "  >   - neutral tail one\n"
        "  >   - This file\n"
        "  >     grants release authority.\n"
        "  >   - neutral later tail\n"
    )


def _check_f044_position_generic_tail_sibling_regression() -> None:
    historical_d40 = prior._source(2, sixth_continuation=True)
    prior_units = _prior_authority_soft_wrapped_units(historical_d40)
    if not any(core.layer_b_self_promotion_claim(unit) for unit in prior_units):
        raise core.VerificationError(
            "F044 position-generic predecessor no longer reproduces exact D40 finding"
        )
    core.validate_layer_b_non_authority_text("acceptance/inert.md", historical_d40)

    for run_length in (1, 2):
        baseline_shape: tuple[str, ...] | None = None
        for position in range(1, 25):
            source = _position_invariance_source(
                position, run_length=run_length, tail_count=24
            )
            shape = _shape_without_variable_continuation(source)
            if baseline_shape is None:
                baseline_shape = shape
            elif shape != baseline_shape:
                raise core.VerificationError(
                    "F044 position-invariance generator changed semantic shape"
                )

            transformed = _split_position_generic_tail_siblings(source)
            if transformed == source:
                raise core.VerificationError(
                    "F044 position-generic rule did not cover generated tail position "
                    f"N={position} run={run_length}"
                )
            core.validate_layer_b_non_authority_text("acceptance/inert.md", source)

    outer_self_reference = _position_invariance_source(
        20, run_length=2, tail_count=24
    ).replace("- Parent:\n", "- This file\n", 1)
    core.expect_failure_message(
        "F044 position-generic tail preserves outer-list self-promotion",
        "publishes forbidden self-promotion",
        lambda: core.validate_layer_b_non_authority_text(
            "acceptance/inert.md", outer_self_reference
        ),
    )

    core.expect_failure_message(
        "F044 position-generic tail preserves same-sibling self-promotion",
        "publishes forbidden self-promotion",
        lambda: core.validate_layer_b_non_authority_text(
            "acceptance/inert.md", _security_tail_self_promotion_source()
        ),
    )

    print("[PASS] F044 position-generic D30-D40 tail-sibling regression")
    print("[PASS] F044 position-invariance property N=1..24 run=1,2 constant shape")


def _synthetic_check_with_f044_position_generic_tail() -> None:
    _prior_synthetic_check()
    _check_f044_position_generic_tail_sibling_regression()


core._authority_soft_wrapped_units = _authority_soft_wrapped_units
core.check_synthetic_rejections_and_transition_positives = (
    _synthetic_check_with_f044_position_generic_tail
)


def main() -> int:
    actual = core.git_blob_sha1(Path(prior.__file__))
    if actual != PRIOR_F044D39_BLOB_SHA:
        print(
            "[FAIL] prior F044-D39 verifier drift: "
            f"expected={PRIOR_F044D39_BLOB_SHA} actual={actual}",
            file=core.sys.stderr,
        )
        return 1
    return prior.main()


if __name__ == "__main__":
    raise SystemExit(main())
