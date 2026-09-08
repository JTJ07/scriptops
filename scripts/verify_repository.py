#!/usr/bin/env python3
"""Bounded F044-D27 list-owned final-sibling-cardinality overlay.

The repaired F044-D26 verifier is retained byte-for-byte at
`scripts/verify_repository_f044d26_list_owned_post_target_continuation.py` and
pinned by Git blob SHA. D27 repairs only the proven list-owned cross-product:
the D26 target+run -> post-target+run shape followed by a bounded run of two or
more consecutive nonempty final siblings at the same child-marker indentation.

Exactly one final sibling remains delegated to D26. The withdrawn top-level D16
family remains untouched. Continuation inside a final sibling, additional
post-target children with their own continuation, deeper nesting, block
transitions, multiple quoted parents, outer-list siblings, nested outer lists
and further list-owned quote recursion remain outside this patch.
"""
from __future__ import annotations

from pathlib import Path
import verify_repository_f044d26_list_owned_post_target_continuation as prior

PRIOR_F044D26_BLOB_SHA = "ea830bc54b9c6bc4f07905fd964539885de841c6"

core = prior.core
singleline = prior.singleline
_prior_authority_soft_wrapped_units = core._authority_soft_wrapped_units
_prior_synthetic_check = core.check_synthetic_rejections_and_transition_positives


def _split_list_owned_final_sibling_run(text: str) -> str:
    """Normalize D26 shape only when its final sibling run has length >=2."""
    lines = text.splitlines()
    output: list[str] = []
    index = 0

    while index < len(lines):
        if index + 9 >= len(lines):
            output.append(lines[index])
            index += 1
            continue
        if index != 0 and lines[index - 1].strip():
            output.append(lines[index])
            index += 1
            continue

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
        _, parent_content_indent, _, _ = parent_list

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
            if layout is None or layout[2] or layout[0] != parent_content_indent:
                break
            child_indexes.append(probe)
            child_content_indents.append(layout[1])
            probe += 1

        if len(child_indexes) < 3 or probe >= len(lines) or not lines[probe].strip():
            output.append(lines[index]); index += 1; continue

        target_index = child_indexes[-1]
        target_run, probe = prior._collect_quote_owned_ordinary_run(
            lines, probe, quote_indent, child_content_indents[-1]
        )
        if not target_run or probe >= len(lines) or not lines[probe].strip():
            output.append(lines[index]); index += 1; continue

        post_quote = singleline._markdown_block_quote_layout(
            lines[probe], allow_deep_indent=True
        )
        post_layout = (
            singleline._markdown_list_item_layout(
                post_quote[1], allow_deep_indent=True
            )
            if post_quote is not None and post_quote[0] == quote_indent
            else None
        )
        if post_layout is None or post_layout[2] or post_layout[0] != parent_content_indent:
            output.append(lines[index]); index += 1; continue

        post_index = probe
        post_run, probe = prior._collect_quote_owned_ordinary_run(
            lines, post_index + 1, quote_indent, post_layout[1]
        )
        if not post_run:
            output.append(lines[index]); index += 1; continue

        final_indexes: list[int] = []
        while probe < len(lines) and lines[probe].strip():
            qlayout = singleline._markdown_block_quote_layout(
                lines[probe], allow_deep_indent=True
            )
            if qlayout is None or qlayout[0] != quote_indent:
                break
            layout = singleline._markdown_list_item_layout(
                qlayout[1], allow_deep_indent=True
            )
            if layout is None or layout[2] or layout[0] != parent_content_indent:
                break
            final_indexes.append(probe)
            probe += 1

        bounded_after = probe == len(lines) or not lines[probe].strip()
        if len(final_indexes) < 2 or not bounded_after:
            output.append(lines[index]); index += 1; continue

        for child_index in child_indexes[:-1]:
            output.extend([outer_raw, quote_parent_raw, lines[child_index]])
            output.append("")

        output.extend([outer_raw, quote_parent_raw, lines[target_index]])
        output.extend(lines[pos] for pos in target_run)
        output.append("")
        output.extend([outer_raw, quote_parent_raw, lines[post_index]])
        output.extend(lines[pos] for pos in post_run)
        for final_index in final_indexes:
            output.append("")
            output.extend([outer_raw, quote_parent_raw, lines[final_index]])
        index = probe

    result = "\n".join(output)
    if text.endswith(("\n", "\r")):
        result += "\n"
    return result


def _authority_soft_wrapped_units(text: str) -> list[str]:
    return _prior_authority_soft_wrapped_units(_split_list_owned_final_sibling_run(text))


def _check_f044d27_list_owned_tail_cardinality_regression() -> None:
    representative = (
        "- Parent:\n"
        "  > - neutral quoted parent\n"
        "  >   - child one\n"
        "  >   - child two\n"
        "  >   - This file\n"
        "  >     target continuation\n"
        "  >   - neutral post-target\n"
        "  >     post-target continuation\n"
        "  >   - grants release authority.\n"
        "  >   - neutral extra final sibling\n"
    )
    prior_units = _prior_authority_soft_wrapped_units(representative)
    if not any(core.layer_b_self_promotion_claim(unit) for unit in prior_units):
        raise core.VerificationError(
            "F044-D27 predecessor no longer reproduces list-owned tail-cardinality finding"
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
        "  >   - grants release authority.\n"
        "  >   - neutral final two\n"
        "  >   - neutral final three\n",
    )

    core.expect_failure_message(
        "F044-D27 later final sibling inherits outer-list self-reference",
        "publishes forbidden self-promotion",
        lambda: core.validate_layer_b_non_authority_text(
            "acceptance/inert.md",
            "- This file\n"
            "  > - neutral quoted parent\n"
            "  >   - child one\n"
            "  >   - child two\n"
            "  >   - neutral target\n"
            "  >     target continuation\n"
            "  >   - neutral post-target\n"
            "  >     post-target continuation\n"
            "  >   - neutral final one\n"
            "  >   - grants release authority.\n",
        ),
    )
    core.expect_failure_message(
        "F044-D27 later final sibling inherits quoted-parent self-reference",
        "publishes forbidden self-promotion",
        lambda: core.validate_layer_b_non_authority_text(
            "acceptance/inert.md",
            "- neutral outer\n"
            "  > - This file\n"
            "  >   - child one\n"
            "  >   - child two\n"
            "  >   - neutral target\n"
            "  >     target continuation\n"
            "  >   - neutral post-target\n"
            "  >     post-target continuation\n"
            "  >   - neutral final one\n"
            "  >   - grants release authority.\n",
        ),
    )

    core.validate_layer_b_non_authority_text(
        "acceptance/inert.md",
        "- neutral outer\n"
        "  > - neutral quoted parent\n"
        "  >   - child one\n"
        "  >   - child two\n"
        "  >   - This file\n"
        "  >     target continuation\n"
        "  >   - neutral post-target\n"
        "  >     post-target continuation\n"
        "  >   - grants release authority.\n"
        "  >   - neutral final two\n",
    )
    core.validate_layer_b_non_authority_text(
        "acceptance/inert.md",
        "- neutral outer\n"
        "  > - neutral quoted parent\n"
        "  >   - child one\n"
        "  >   - child two\n"
        "  >   - neutral target\n"
        "  >     target continuation\n"
        "  >   - This file\n"
        "  >     post-target continuation\n"
        "  >   - grants release authority.\n"
        "  >   - neutral final two\n",
    )

    delegated_d26 = (
        "- Parent:\n"
        "  > - neutral quoted parent\n"
        "  >   - child one\n"
        "  >   - child two\n"
        "  >   - This file\n"
        "  >     target continuation\n"
        "  >   - neutral post-target\n"
        "  >     post-target continuation\n"
        "  >   - grants release authority.\n"
    )
    if _split_list_owned_final_sibling_run(delegated_d26) != delegated_d26:
        raise core.VerificationError("F044-D27 escaped into D26 one-final-sibling scope")
    core.validate_layer_b_non_authority_text("acceptance/inert.md", delegated_d26)

    # Exact withdrawn D16 representative from FJ899/8 PR #464.
    top_level_d16 = (
        "> - neutral parent\n"
        ">   - child one\n"
        ">   - child two\n"
        ">   - This file\n"
        ">     target continuation\n"
        ">   - neutral post-target one\n"
        ">     post-target continuation\n"
        ">   - neutral post-target two\n"
        ">   - grants release authority.\n"
    )
    if _split_list_owned_final_sibling_run(top_level_d16) != top_level_d16:
        raise core.VerificationError("F044-D27 escaped into withdrawn top-level D16 family")
    core.validate_layer_b_non_authority_text("acceptance/inert.md", top_level_d16)

    for untouched in [
        (
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
            "  >   - grants release authority.\n"
        ),
        (
            "- Parent:\n"
            "  > - neutral quoted parent\n"
            "  >   - child one\n"
            "  >   - child two\n"
            "  >   - This file\n"
            "  >     target continuation\n"
            "  >   - neutral post-target one\n"
            "  >     post-target one continuation\n"
            "  >   - neutral post-target two\n"
            "  >     post-target two continuation\n"
            "  >   - grants release authority.\n"
            "  >   - neutral final two\n"
        ),
        (
            "- Parent:\n"
            "  > - neutral quoted parent\n"
            "  >   - child one\n"
            "  >   - child two\n"
            "  >   - This file\n"
            "  >     target continuation\n"
            "  >   - neutral post-target\n"
            "  >     post-target continuation\n"
            "  >   - neutral final one\n"
            "  >   - grants release authority.\n"
            "- outer sibling\n"
        ),
        (
            "  - nested outer\n"
            "    > - neutral quoted parent\n"
            "    >   - child one\n"
            "    >   - child two\n"
            "    >   - This file\n"
            "    >     target continuation\n"
            "    >   - neutral post-target\n"
            "    >     post-target continuation\n"
            "    >   - neutral final one\n"
            "    >   - grants release authority.\n"
        ),
    ]:
        if _split_list_owned_final_sibling_run(untouched) != untouched:
            raise core.VerificationError("F044-D27 repair escaped bounded list-owned tail scope")

    print("[PASS] F044-D27 list-owned final-sibling-cardinality regression")


def _synthetic_check_with_f044d27() -> None:
    _prior_synthetic_check()
    _check_f044d27_list_owned_tail_cardinality_regression()


core._authority_soft_wrapped_units = _authority_soft_wrapped_units
core.check_synthetic_rejections_and_transition_positives = _synthetic_check_with_f044d27


def main() -> int:
    actual = core.git_blob_sha1(Path(prior.__file__))
    if actual != PRIOR_F044D26_BLOB_SHA:
        print(
            "[FAIL] prior F044-D26 verifier drift: "
            f"expected={PRIOR_F044D26_BLOB_SHA} actual={actual}",
            file=core.sys.stderr,
        )
        return 1
    return prior.main()


if __name__ == "__main__":
    raise SystemExit(main())
