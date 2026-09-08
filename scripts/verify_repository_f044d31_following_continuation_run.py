#!/usr/bin/env python3
"""Bounded F044-D31 following-continuation-run overlay.

The repaired F044-D30 verifier is retained byte-for-byte at
`scripts/verify_repository_f044d30_following_child_continuation.py` and pinned
by Git blob SHA. D31 repairs only the proven continuation-run length dimension
inside the same source-column-zero outer-list-owned quote family: the first
following sibling may own two or more ordinary continuation lines before at
least one consecutive nonempty same-level sibling.

Exactly one continuation line remains delegated to D30. Continuation in later
following siblings, deeper nesting, block transitions, multiple quoted parents,
outer-list siblings, nested outer lists and further recursion remain outside.
"""
from __future__ import annotations

from pathlib import Path
import verify_repository_f044d30_following_child_continuation as prior

PRIOR_F044D30_BLOB_SHA = "2f2eaf443f30955d73beb7fd652cfa60f3605d7b"

core = prior.core
singleline = prior.singleline
d28 = prior.d28
_prior_authority_soft_wrapped_units = core._authority_soft_wrapped_units
_prior_synthetic_check = core.check_synthetic_rejections_and_transition_positives


def _split_following_child_continuation_run(text: str) -> str:
    """Normalize only D30-family shapes with >=2 first-following continuation lines."""
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

        first_follow_layout = d28._quoted_same_level_nonempty_item(
            lines, probe, quote_indent, child_marker_indent
        )
        if first_follow_layout is None:
            output.append(lines[index]); index += 1; continue
        first_follow_index = probe
        first_follow_run, probe = d28._collect_quote_owned_ordinary_run(
            lines, first_follow_index + 1, quote_indent, first_follow_layout[1]
        )
        if len(first_follow_run) < 2:
            output.append(lines[index]); index += 1; continue

        later_following_indexes: list[int] = []
        while probe < len(lines) and lines[probe].strip():
            layout = d28._quoted_same_level_nonempty_item(
                lines, probe, quote_indent, child_marker_indent
            )
            if layout is None:
                break
            later_following_indexes.append(probe)
            probe += 1

        bounded_after = probe == len(lines) or not lines[probe].strip()
        if not later_following_indexes or not bounded_after:
            output.append(lines[index]); index += 1; continue

        for child_index in child_indexes[:-1]:
            output.extend([outer_raw, quote_parent_raw, lines[child_index]])
            output.append("")

        output.extend([outer_raw, quote_parent_raw, lines[target_index]])
        output.extend(lines[pos] for pos in target_run)
        output.append("")
        output.extend([outer_raw, quote_parent_raw, lines[post_index]])
        output.extend(lines[pos] for pos in post_run)
        output.append("")
        output.extend([outer_raw, quote_parent_raw, lines[final_index]])
        output.extend(lines[pos] for pos in final_run)
        output.append("")
        output.extend([outer_raw, quote_parent_raw, lines[first_follow_index]])
        output.extend(lines[pos] for pos in first_follow_run)

        for sibling_index in later_following_indexes:
            output.append("")
            output.extend([outer_raw, quote_parent_raw, lines[sibling_index]])

        index = probe

    result = "\n".join(output)
    if text.endswith(("\n", "\r")):
        result += "\n"
    return result


def _authority_soft_wrapped_units(text: str) -> list[str]:
    return _prior_authority_soft_wrapped_units(
        _split_following_child_continuation_run(text)
    )


def _check_f044d31_following_continuation_run_regression() -> None:
    representative = (
        "- Parent:\n"
        "  > - neutral quoted parent\n"
        "  >   - child one\n"
        "  >   - child two\n"
        "  >   - This file\n"
        "  >     target continuation\n"
        "  >   - neutral post-target\n"
        "  >     post-target continuation\n"
        "  >   - neutral final one\n"
        "  >     final continuation\n"
        "  >   - neutral following one\n"
        "  >     following continuation one\n"
        "  >     following continuation two\n"
        "  >   - grants release authority.\n"
    )
    prior_units = _prior_authority_soft_wrapped_units(representative)
    if not any(core.layer_b_self_promotion_claim(unit) for unit in prior_units):
        raise core.VerificationError(
            "F044-D31 predecessor no longer reproduces following-continuation-run finding"
        )
    core.validate_layer_b_non_authority_text("acceptance/inert.md", representative)

    core.validate_layer_b_non_authority_text(
        "acceptance/inert.md",
        "- Parent:\n"
        "  > - neutral quoted parent\n"
        "  >   - child one\n"
        "  >   - child two\n"
        "  >   - This file\n"
        "  >     target continuation\n"
        "  >   - neutral post-target\n"
        "  >     post-target continuation\n"
        "  >   - neutral final one\n"
        "  >     final continuation\n"
        "  >   - neutral following one\n"
        "  >     following continuation one\n"
        "  >     following continuation two\n"
        "  >     following continuation three\n"
        "  >   - grants release authority.\n"
        "  >   - neutral following three\n",
    )

    core.expect_failure_message(
        "F044-D31 continued following child keeps its own self-promotion together",
        "publishes forbidden self-promotion",
        lambda: core.validate_layer_b_non_authority_text(
            "acceptance/inert.md",
            "- neutral outer\n"
            "  > - neutral quoted parent\n"
            "  >   - child one\n"
            "  >   - child two\n"
            "  >   - neutral target\n"
            "  >     target continuation\n"
            "  >   - neutral post-target\n"
            "  >     post-target continuation\n"
            "  >   - neutral final one\n"
            "  >     final continuation\n"
            "  >   - This file\n"
            "  >     ordinary continuation\n"
            "  >     grants release authority.\n"
            "  >   - neutral following two\n",
        ),
    )

    delegated_d30 = (
        "- Parent:\n"
        "  > - neutral quoted parent\n"
        "  >   - child one\n"
        "  >   - child two\n"
        "  >   - This file\n"
        "  >     target continuation\n"
        "  >   - neutral post-target\n"
        "  >     post-target continuation\n"
        "  >   - neutral final one\n"
        "  >     final continuation\n"
        "  >   - neutral following one\n"
        "  >     following continuation\n"
        "  >   - grants release authority.\n"
    )
    if _split_following_child_continuation_run(delegated_d30) != delegated_d30:
        raise core.VerificationError("F044-D31 escaped into D30 one-line scope")
    core.validate_layer_b_non_authority_text("acceptance/inert.md", delegated_d30)

    later_continuation = (
        "- Parent:\n"
        "  > - neutral quoted parent\n"
        "  >   - child one\n"
        "  >   - child two\n"
        "  >   - This file\n"
        "  >     target continuation\n"
        "  >   - neutral post-target\n"
        "  >     post-target continuation\n"
        "  >   - neutral final one\n"
        "  >     final continuation\n"
        "  >   - neutral following one\n"
        "  >     following continuation one\n"
        "  >     following continuation two\n"
        "  >   - neutral following two\n"
        "  >     later continuation\n"
        "  >   - grants release authority.\n"
    )
    if _split_following_child_continuation_run(later_continuation) != later_continuation:
        raise core.VerificationError(
            "F044-D31 escaped into later-following-continuation scope"
        )

    print("[PASS] F044-D31 following-continuation-run regression")


def _synthetic_check_with_f044d31() -> None:
    _prior_synthetic_check()
    _check_f044d31_following_continuation_run_regression()


core._authority_soft_wrapped_units = _authority_soft_wrapped_units
core.check_synthetic_rejections_and_transition_positives = _synthetic_check_with_f044d31


def main() -> int:
    actual = core.git_blob_sha1(Path(prior.__file__))
    if actual != PRIOR_F044D30_BLOB_SHA:
        print(
            "[FAIL] prior F044-D30 verifier drift: "
            f"expected={PRIOR_F044D30_BLOB_SHA} actual={actual}",
            file=core.sys.stderr,
        )
        return 1
    return prior.main()


if __name__ == "__main__":
    raise SystemExit(main())
