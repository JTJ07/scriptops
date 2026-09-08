#!/usr/bin/env python3
"""Bounded F044-D37 fourth-following-continuation-run overlay.

The repaired F044-D36 verifier is retained byte-for-byte at
`scripts/verify_repository_f044d36_fourth_following_continuation.py` and pinned
by Git blob SHA. D37 repairs only the proven run-length dimension inside the
same source-column-zero outer-list-owned quote family: after the D35 third-
following continuation run, the fourth following sibling may own two or more
ordinary continuation lines before at least one later same-level sibling.

Exactly one continuation line on that fourth following sibling remains delegated
to D36. Continuation in fifth/later following siblings, deeper nesting, block
transitions, multiple quoted parents, outer-list siblings, nested outer lists
and further recursion remain outside this patch.
"""
from __future__ import annotations

from pathlib import Path
import verify_repository_f044d36_fourth_following_continuation as prior

PRIOR_F044D36_BLOB_SHA = "b4ef7f415b245f57fb04042e860802f6825e4988"

core = prior.core
singleline = prior.singleline
d28 = prior.d28
_prior_authority_soft_wrapped_units = core._authority_soft_wrapped_units
_prior_synthetic_check = core.check_synthetic_rejections_and_transition_positives


def _split_fourth_following_continuation_run(text: str) -> str:
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

        following: list[tuple[int, list[int]]] = []
        for required_run in (2, 2, 2):
            layout = d28._quoted_same_level_nonempty_item(
                lines, probe, quote_indent, child_marker_indent
            )
            if layout is None:
                break
            sibling_index = probe
            run, probe = d28._collect_quote_owned_ordinary_run(
                lines, sibling_index + 1, quote_indent, layout[1]
            )
            if len(run) < required_run:
                break
            following.append((sibling_index, run))
        if len(following) != 3:
            output.append(lines[index]); index += 1; continue

        fourth_layout = d28._quoted_same_level_nonempty_item(
            lines, probe, quote_indent, child_marker_indent
        )
        if fourth_layout is None:
            output.append(lines[index]); index += 1; continue
        fourth_index = probe
        fourth_run, probe = d28._collect_quote_owned_ordinary_run(
            lines, fourth_index + 1, quote_indent, fourth_layout[1]
        )
        if len(fourth_run) < 2:
            output.append(lines[index]); index += 1; continue

        later_indexes: list[int] = []
        while probe < len(lines) and lines[probe].strip():
            layout = d28._quoted_same_level_nonempty_item(
                lines, probe, quote_indent, child_marker_indent
            )
            if layout is None:
                break
            later_indexes.append(probe)
            probe += 1

        if not later_indexes or not (probe == len(lines) or not lines[probe].strip()):
            output.append(lines[index]); index += 1; continue

        for child_index in child_indexes[:-1]:
            output.extend([outer_raw, quote_parent_raw, lines[child_index], ""])

        output.extend([outer_raw, quote_parent_raw, lines[target_index]])
        output.extend(lines[pos] for pos in target_run); output.append("")
        output.extend([outer_raw, quote_parent_raw, lines[post_index]])
        output.extend(lines[pos] for pos in post_run); output.append("")
        output.extend([outer_raw, quote_parent_raw, lines[final_index]])
        output.extend(lines[pos] for pos in final_run)

        for sibling_index, run in following:
            output.append("")
            output.extend([outer_raw, quote_parent_raw, lines[sibling_index]])
            output.extend(lines[pos] for pos in run)

        output.append("")
        output.extend([outer_raw, quote_parent_raw, lines[fourth_index]])
        output.extend(lines[pos] for pos in fourth_run)
        for sibling_index in later_indexes:
            output.append("")
            output.extend([outer_raw, quote_parent_raw, lines[sibling_index]])

        index = probe

    result = "\n".join(output)
    if text.endswith(("\n", "\r")):
        result += "\n"
    return result


def _authority_soft_wrapped_units(text: str) -> list[str]:
    return _prior_authority_soft_wrapped_units(
        _split_fourth_following_continuation_run(text)
    )


def _source(fourth_run: int = 2, fifth_continuation: bool = False) -> str:
    lines = [
        "- Parent:",
        "  > - neutral quoted parent",
        "  >   - child one",
        "  >   - child two",
        "  >   - This file",
        "  >     target continuation",
        "  >   - neutral post-target",
        "  >     post-target continuation",
        "  >   - neutral final one",
        "  >     final continuation",
        "  >   - neutral following one",
        "  >     following continuation one",
        "  >     following continuation two",
        "  >   - neutral following two",
        "  >     later continuation one",
        "  >     later continuation two",
        "  >   - neutral following three",
        "  >     still later continuation one",
        "  >     still later continuation two",
        "  >   - neutral following four",
    ]
    lines.extend(
        f"  >     fourth continuation {i}" for i in range(1, fourth_run + 1)
    )
    if fifth_continuation:
        lines.extend(["  >   - neutral following five", "  >     fifth continuation"])
    lines.append("  >   - grants release authority.")
    return "\n".join(lines) + "\n"


def _check_f044d37_fourth_following_continuation_run_regression() -> None:
    representative = _source(2)
    prior_units = _prior_authority_soft_wrapped_units(representative)
    if not any(core.layer_b_self_promotion_claim(unit) for unit in prior_units):
        raise core.VerificationError(
            "F044-D37 predecessor no longer reproduces fourth-following-continuation-run finding"
        )
    core.validate_layer_b_non_authority_text("acceptance/inert.md", representative)
    core.validate_layer_b_non_authority_text("acceptance/inert.md", _source(3))

    one_line = _source(1)
    if _split_fourth_following_continuation_run(one_line) != one_line:
        raise core.VerificationError("F044-D37 escaped into D36 one-line scope")
    core.validate_layer_b_non_authority_text("acceptance/inert.md", one_line)

    fifth = _source(2, fifth_continuation=True)
    if _split_fourth_following_continuation_run(fifth) != fifth:
        raise core.VerificationError(
            "F044-D37 escaped into fifth-following-continuation scope"
        )

    core.expect_failure_message(
        "F044-D37 fourth-following child keeps its own self-promotion together",
        "publishes forbidden self-promotion",
        lambda: core.validate_layer_b_non_authority_text(
            "acceptance/inert.md",
            _source(2).replace("- Parent:", "- neutral outer:").replace(
                "  >   - neutral following four\n  >     fourth continuation 1",
                "  >   - This file\n  >     fourth continuation 1",
            ).replace(
                "  >     fourth continuation 2",
                "  >     grants release authority.",
            ).replace("  >   - grants release authority.\n", "  >   - neutral following five\n"),
        ),
    )

    print("[PASS] F044-D37 fourth-following-continuation-run regression")


def _synthetic_check_with_f044d37() -> None:
    _prior_synthetic_check()
    _check_f044d37_fourth_following_continuation_run_regression()


core._authority_soft_wrapped_units = _authority_soft_wrapped_units
core.check_synthetic_rejections_and_transition_positives = _synthetic_check_with_f044d37


def main() -> int:
    actual = core.git_blob_sha1(Path(prior.__file__))
    if actual != PRIOR_F044D36_BLOB_SHA:
        print(
            "[FAIL] prior F044-D36 verifier drift: "
            f"expected={PRIOR_F044D36_BLOB_SHA} actual={actual}",
            file=core.sys.stderr,
        )
        return 1
    return prior.main()


if __name__ == "__main__":
    raise SystemExit(main())
