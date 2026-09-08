#!/usr/bin/env python3
"""Bounded F044-D7 child-sibling-run parent-context overlay.

The repaired F044-D6 verifier is retained byte-for-byte at
`scripts/verify_repository_f044d6_three_child.py` and pinned by Git blob SHA.
D5 (N=2), D6 (N=3), and the D7 adjacent probe (N=4) establish one parameterized
root cause, so this entrypoint generalizes only that proven family: one
nonempty top-level quoted outer list item followed by a bounded run of two or
more consecutive nonempty child sibling markers beginning exactly at the
outer item's content indentation.

Each child remains a separate authority unit while the same outer parent line
is repeated into every child unit. Child continuation, different-level/deeper
nesting, outer-sibling transitions, blank/fence/block transitions inside the
run, and list-owned outer quote recursion remain outside this repair.
"""
from __future__ import annotations

from pathlib import Path
import verify_repository_f044d6_three_child as prior

PRIOR_F044D6_THREE_CHILD_BLOB_SHA = "9353ae5d9d52536a7bce0c9ac8e1b5dc657cadc4"

core = prior.core
singleline = prior.singleline
_prior_authority_soft_wrapped_units = core._authority_soft_wrapped_units
_prior_synthetic_check = core.check_synthetic_rejections_and_transition_positives


def _top_level_quote_content(raw_line: str) -> str | None:
    if not raw_line.startswith(">"):
        return None
    layout = singleline._markdown_block_quote_layout(raw_line)
    if layout is None or layout[0] != 0:
        return None
    return layout[1]


def _preserve_parent_for_bounded_child_sibling_run(text: str) -> str:
    """Duplicate one bounded outer parent across a child run of length >= 2."""
    lines = text.splitlines()
    output: list[str] = []
    index = 0

    while index < len(lines):
        bounded_before = index == 0 or not lines[index - 1].strip()
        parent_content = _top_level_quote_content(lines[index])
        parent_layout = (
            singleline._markdown_list_item_layout(parent_content)
            if parent_content is not None
            else None
        )
        if not bounded_before or parent_layout is None or parent_layout[2]:
            output.append(lines[index])
            index += 1
            continue

        _, parent_content_indent, _, _ = parent_layout
        child_indexes: list[int] = []
        probe = index + 1
        while probe < len(lines) and lines[probe].strip():
            child_content = _top_level_quote_content(lines[probe])
            child_layout = (
                singleline._markdown_list_item_layout(child_content)
                if child_content is not None
                else None
            )
            if (
                child_layout is None
                or child_layout[2]
                or child_layout[0] != parent_content_indent
            ):
                break
            child_indexes.append(probe)
            probe += 1

        bounded_after = probe == len(lines) or not lines[probe].strip()
        if len(child_indexes) < 2 or not bounded_after:
            output.append(lines[index])
            index += 1
            continue

        for ordinal, child_index in enumerate(child_indexes):
            if ordinal:
                output.append("")
            output.extend([lines[index], lines[child_index]])
        index = probe

    result = "\n".join(output)
    if text.endswith(("\n", "\r")):
        result += "\n"
    return result


def _check_f044d7_child_run_parent_context_regression() -> None:
    representative = (
        "> - This file\n"
        ">   - child one\n"
        ">   - child two\n"
        ">   - child three\n"
        ">   - grants release authority.\n"
    )

    prior_units = _prior_authority_soft_wrapped_units(representative)
    if any(core.layer_b_self_promotion_claim(unit) for unit in prior_units):
        raise core.VerificationError(
            "F044-D7 predecessor no longer reproduces child-run-length finding"
        )

    expected = (
        "> - This file\n"
        ">   - child one\n"
        "\n"
        "> - This file\n"
        ">   - child two\n"
        "\n"
        "> - This file\n"
        ">   - child three\n"
        "\n"
        "> - This file\n"
        ">   - grants release authority.\n"
    )
    actual = _preserve_parent_for_bounded_child_sibling_run(representative)
    if actual != expected:
        raise core.VerificationError(
            "F044-D7 child-run normalization mismatch: "
            f"expected={expected!r} actual={actual!r}"
        )

    core.expect_failure_message(
        "F044-D7 fourth child inherits outer self-reference",
        "publishes forbidden self-promotion",
        lambda: core.validate_layer_b_non_authority_text(
            "acceptance/inert.md", representative
        ),
    )

    # Prove the generalization beyond the exact N=4 finding without adding a
    # new block family: N=5 is the same bounded run-length root cause.
    five_children = (
        "> - This file\n"
        ">   - child one\n"
        ">   - child two\n"
        ">   - child three\n"
        ">   - child four\n"
        ">   - grants release authority.\n"
    )
    core.expect_failure_message(
        "F044-D7 fifth child inherits outer self-reference",
        "publishes forbidden self-promotion",
        lambda: core.validate_layer_b_non_authority_text(
            "acceptance/inert.md", five_children
        ),
    )

    # Child siblings stay separate when the outer parent is neutral.
    core.validate_layer_b_non_authority_text(
        "acceptance/inert.md",
        "> - neutral parent\n"
        ">   - This file\n"
        ">   - child two\n"
        ">   - child three\n"
        ">   - grants release authority.\n",
    )

    # The already-repaired N=2 and N=3 representatives remain covered by the
    # generalized normalizer as the same family.
    for rejected in [
        (
            "> - This file\n"
            ">   - child one\n"
            ">   - grants release authority.\n"
        ),
        (
            "> - This file\n"
            ">   - child one\n"
            ">   - child two\n"
            ">   - grants release authority.\n"
        ),
    ]:
        core.expect_failure_message(
            "F044-D7 shorter child run preserves outer parent context",
            "publishes forbidden self-promotion",
            lambda rejected=rejected: core.validate_layer_b_non_authority_text(
                "acceptance/inert.md", rejected
            ),
        )

    # Adjacent structures deliberately remain outside this bounded family.
    for untouched in [
        (
            "> - This file\n"
            ">   - child one\n"
            ">     child continuation\n"
            ">   - grants release authority.\n"
        ),
        (
            "> - This file\n"
            ">   - child one\n"
            ">     - grandchild\n"
            ">   - grants release authority.\n"
        ),
        (
            "> - This file\n"
            ">   - child one\n"
            ">   - child two\n"
            "> - outer sibling\n"
        ),
        (
            "- Parent:\n"
            "  > - This file\n"
            "  >   - child one\n"
            "  >   - grants release authority.\n"
        ),
    ]:
        if _preserve_parent_for_bounded_child_sibling_run(untouched) != untouched:
            raise core.VerificationError(
                "F044-D7 repair escaped its bounded consecutive child-run scope"
            )

    print("[PASS] F044-D7 bounded child-sibling-run parent-context regression")


def _synthetic_check_with_f044d7_child_run() -> None:
    _prior_synthetic_check()
    _check_f044d7_child_run_parent_context_regression()


core._authority_soft_wrapped_units = _authority_soft_wrapped_units = lambda text: (
    _prior_authority_soft_wrapped_units(
        _preserve_parent_for_bounded_child_sibling_run(text)
    )
)
core.check_synthetic_rejections_and_transition_positives = (
    _synthetic_check_with_f044d7_child_run
)


def main() -> int:
    actual = core.git_blob_sha1(Path(prior.__file__))
    if actual != PRIOR_F044D6_THREE_CHILD_BLOB_SHA:
        print(
            "[FAIL] prior F044-D6 verifier drift: "
            f"expected={PRIOR_F044D6_THREE_CHILD_BLOB_SHA} actual={actual}",
            file=core.sys.stderr,
        )
        return 1
    return prior.main()


if __name__ == "__main__":
    raise SystemExit(main())
