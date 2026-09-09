#!/usr/bin/env python3
"""Bounded F044-D9 child-continuation-run sibling overlay.

The repaired F044-D8 verifier is retained byte-for-byte at
`scripts/verify_repository_f044d8_child_continuation.py` and pinned by Git blob
SHA. D8 (continuation count N=1) and the D9 adjacent probe (N=2) establish one
parameterized root cause, so this entrypoint generalizes only that proven
family: one nonempty top-level quoted outer item, one nonempty child item at the
outer content indentation, a run of one or more ordinary continuation lines
owned by that child, and one nonempty sibling child returning to the same child
marker indentation. The fragment remains bounded by BOF/blank before and
EOF/blank after.

The continuation run stays with child one; child two is a separate authority
unit; the outer parent is repeated into both units. Deeper nesting, block
transitions inside the run, more than two child items, outer-sibling transitions
and list-owned outer quote recursion remain outside this repair.
"""
from __future__ import annotations

from pathlib import Path
import verify_repository_f044d8_child_continuation as prior

PRIOR_F044D8_CHILD_CONTINUATION_BLOB_SHA = (
    "43b72994b538a872ebaa36991a5dd127ad47592b"
)

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


def _split_child_continuation_run_sibling(text: str) -> str:
    """Normalize parent -> child -> ordinary run >=1 -> same-level sibling."""
    lines = text.splitlines()
    output: list[str] = []
    index = 0

    while index < len(lines):
        if index + 3 >= len(lines):
            output.append(lines[index])
            index += 1
            continue

        bounded_before = index == 0 or not lines[index - 1].strip()
        if not bounded_before:
            output.append(lines[index])
            index += 1
            continue

        parent_content = _top_level_quote_content(lines[index])
        child_one_content = _top_level_quote_content(lines[index + 1])
        parent_layout = (
            singleline._markdown_list_item_layout(parent_content)
            if parent_content is not None
            else None
        )
        child_one_layout = (
            singleline._markdown_list_item_layout(child_one_content)
            if child_one_content is not None
            else None
        )
        if (
            parent_layout is None
            or child_one_layout is None
            or parent_layout[2]
            or child_one_layout[2]
        ):
            output.append(lines[index])
            index += 1
            continue

        _, parent_content_indent, _, _ = parent_layout
        child_marker_indent, child_content_indent, _, _ = child_one_layout
        if child_marker_indent != parent_content_indent:
            output.append(lines[index])
            index += 1
            continue

        continuation_indexes: list[int] = []
        sibling_index: int | None = None
        probe = index + 2

        while probe < len(lines) and lines[probe].strip():
            content = _top_level_quote_content(lines[probe])
            if content is None:
                break

            any_list = singleline._markdown_list_item_layout(
                content,
                allow_deep_indent=True,
            )
            if any_list is not None:
                if (
                    continuation_indexes
                    and not any_list[2]
                    and any_list[0] == child_marker_indent
                ):
                    sibling_index = probe
                break

            relative = singleline._markdown_remove_leading_columns(
                content,
                child_content_indent,
            )
            if (
                relative is None
                or not relative.strip()
                or not singleline._markdown_block_quote_lazy_paragraph(relative)
            ):
                break

            continuation_indexes.append(probe)
            probe += 1

        if sibling_index is None:
            output.append(lines[index])
            index += 1
            continue

        bounded_after = (
            sibling_index + 1 == len(lines)
            or not lines[sibling_index + 1].strip()
        )
        if not bounded_after:
            output.append(lines[index])
            index += 1
            continue

        output.extend([lines[index], lines[index + 1]])
        output.extend(lines[pos] for pos in continuation_indexes)
        output.append("")
        output.extend([lines[index], lines[sibling_index]])
        index = sibling_index + 1

    result = "\n".join(output)
    if text.endswith(("\n", "\r")):
        result += "\n"
    return result


def _authority_soft_wrapped_units(text: str) -> list[str]:
    return _prior_authority_soft_wrapped_units(
        _split_child_continuation_run_sibling(text)
    )


def _check_f044d9_child_continuation_run_regression() -> None:
    representative = (
        "> - neutral parent\n"
        ">   - This file\n"
        ">     continuation one\n"
        ">     continuation two\n"
        ">   - grants release authority.\n"
    )

    prior_units = _prior_authority_soft_wrapped_units(representative)
    if not any(core.layer_b_self_promotion_claim(unit) for unit in prior_units):
        raise core.VerificationError(
            "F044-D9 predecessor no longer reproduces two-continuation false positive"
        )

    expected = (
        "> - neutral parent\n"
        ">   - This file\n"
        ">     continuation one\n"
        ">     continuation two\n"
        "\n"
        "> - neutral parent\n"
        ">   - grants release authority.\n"
    )
    actual = _split_child_continuation_run_sibling(representative)
    if actual != expected:
        raise core.VerificationError(
            "F044-D9 continuation-run normalization mismatch: "
            f"expected={expected!r} actual={actual!r}"
        )

    core.validate_layer_b_non_authority_text("acceptance/inert.md", representative)

    # The N=1 representative remains covered by the generalized family.
    core.validate_layer_b_non_authority_text(
        "acceptance/inert.md",
        "> - neutral parent\n"
        ">   - This file\n"
        ">     continuation one\n"
        ">   - grants release authority.\n",
    )

    # N=3 is the same proven continuation-run family, not a new block shape.
    core.validate_layer_b_non_authority_text(
        "acceptance/inert.md",
        "> - neutral parent\n"
        ">   - This file\n"
        ">     continuation one\n"
        ">     continuation two\n"
        ">     continuation three\n"
        ">   - grants release authority.\n",
    )

    core.expect_failure_message(
        "F044-D9 second child inherits outer self-reference after continuation run",
        "publishes forbidden self-promotion",
        lambda: core.validate_layer_b_non_authority_text(
            "acceptance/inert.md",
            "> - This file\n"
            ">   - child one\n"
            ">     continuation one\n"
            ">     continuation two\n"
            ">   - grants release authority.\n",
        ),
    )

    core.expect_failure_message(
        "F044-D9 first child continuation run stays parent-scoped",
        "publishes forbidden self-promotion",
        lambda: core.validate_layer_b_non_authority_text(
            "acceptance/inert.md",
            "> - This file\n"
            ">   - grants release authority.\n"
            ">     continuation one\n"
            ">     continuation two\n"
            ">   - child two\n",
        ),
    )

    ordered = (
        "> 1. neutral parent\n"
        ">    - This file\n"
        ">      continuation one\n"
        ">      continuation two\n"
        ">    - grants release authority.\n"
    )
    core.validate_layer_b_non_authority_text("acceptance/inert.md", ordered)

    # Adjacent structures remain outside this generalized continuation family.
    for untouched in [
        (
            "> - neutral parent\n"
            ">   - This file\n"
            ">     continuation one\n"
            ">     - grandchild\n"
            ">   - grants release authority.\n"
        ),
        (
            "> - neutral parent\n"
            ">   - This file\n"
            ">     continuation one\n"
            ">     ```\n"
            ">     code\n"
            ">     ```\n"
            ">   - grants release authority.\n"
        ),
        (
            "> - neutral parent\n"
            ">   - This file\n"
            ">     continuation one\n"
            ">\n"
            ">     continuation after blank\n"
            ">   - grants release authority.\n"
        ),
        (
            "> - neutral parent\n"
            ">   - This file\n"
            ">     continuation one\n"
            ">   - child two\n"
            ">   - child three\n"
        ),
        (
            "> - neutral parent\n"
            ">   - This file\n"
            ">     continuation one\n"
            ">   - child two\n"
            "> - outer sibling\n"
        ),
        (
            "- Parent:\n"
            "  > - neutral parent\n"
            "  >   - This file\n"
            "  >     continuation one\n"
            "  >   - grants release authority.\n"
        ),
    ]:
        if _split_child_continuation_run_sibling(untouched) != untouched:
            raise core.VerificationError(
                "F044-D9 repair escaped its bounded child-continuation-run scope"
            )

    print("[PASS] F044-D9 child-continuation-run sibling-separation regression")


def _synthetic_check_with_f044d9_child_continuation_run() -> None:
    _prior_synthetic_check()
    _check_f044d9_child_continuation_run_regression()


core._authority_soft_wrapped_units = _authority_soft_wrapped_units
core.check_synthetic_rejections_and_transition_positives = (
    _synthetic_check_with_f044d9_child_continuation_run
)


def main() -> int:
    actual = core.git_blob_sha1(Path(prior.__file__))
    if actual != PRIOR_F044D8_CHILD_CONTINUATION_BLOB_SHA:
        print(
            "[FAIL] prior F044-D8 verifier drift: "
            f"expected={PRIOR_F044D8_CHILD_CONTINUATION_BLOB_SHA} actual={actual}",
            file=core.sys.stderr,
        )
        return 1
    return prior.main()


if __name__ == "__main__":
    raise SystemExit(main())
