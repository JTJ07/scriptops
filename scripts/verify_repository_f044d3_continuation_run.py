#!/usr/bin/env python3
"""Bounded F044-D3 ordinary-continuation-run quoted sibling-list overlay.

The repaired F044-D2 verifier is retained byte-for-byte at
`scripts/verify_repository_f044d2_one_continuation.py` and pinned by Git blob
SHA. This entrypoint generalizes only the same proven root cause: a top-level
quoted list item may carry one or more ordinary continuation lines owned by its
content indentation before a same-inner-level quoted sibling marker.

Nested child markers, blank/block transitions, fenced/heading/thematic/HTML
content and list-owned outer quote recursion terminate tracking and remain
outside this repair.
"""
from __future__ import annotations

from pathlib import Path
import verify_repository_f044d2_one_continuation as prior

PRIOR_F044D2_ONE_CONTINUATION_BLOB_SHA = "05856621e882f5559004c7e33f4804e3ba238be8"

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


def _split_ordinary_continuation_run_top_level_quoted_siblings(text: str) -> str:
    """Split same-level sibling after one-or-more owned ordinary lines."""
    lines = text.splitlines()
    output: list[str] = []

    active_marker_indent: int | None = None
    active_content_indent: int | None = None
    ordinary_count = 0

    for raw_line in lines:
        content = _top_level_quote_content(raw_line)
        if content is None:
            active_marker_indent = None
            active_content_indent = None
            ordinary_count = 0
            output.append(raw_line)
            continue

        list_layout = singleline._markdown_list_item_layout(content)
        if list_layout is not None:
            marker_indent, content_indent, empty_item, _ = list_layout

            if (
                not empty_item
                and active_marker_indent is not None
                and ordinary_count >= 1
                and marker_indent == active_marker_indent
                and output
                and output[-1].strip()
            ):
                output.append("")

            # A different-level marker is an adjacent nested/ownership family;
            # do not carry outer tracking through it in this bounded repair.
            if active_marker_indent is not None and marker_indent != active_marker_indent:
                active_marker_indent = None
                active_content_indent = None
                ordinary_count = 0
            elif not empty_item:
                active_marker_indent = marker_indent
                active_content_indent = content_indent
                ordinary_count = 0
            else:
                active_marker_indent = None
                active_content_indent = None
                ordinary_count = 0

            output.append(raw_line)
            continue

        if (
            active_marker_indent is not None
            and active_content_indent is not None
            and content.strip()
            and singleline._markdown_leading_columns(content) >= active_content_indent
            and singleline._markdown_block_quote_lazy_paragraph(content)
        ):
            ordinary_count += 1
            output.append(raw_line)
            continue

        active_marker_indent = None
        active_content_indent = None
        ordinary_count = 0
        output.append(raw_line)

    result = "\n".join(output)
    if text.endswith(("\n", "\r")):
        result += "\n"
    return result


def _authority_soft_wrapped_units(text: str) -> list[str]:
    return _prior_authority_soft_wrapped_units(
        _split_ordinary_continuation_run_top_level_quoted_siblings(text)
    )


def _check_f044d3_continuation_run_sibling_regression() -> None:
    representative = (
        "> - This file\n"
        ">   continuation one\n"
        ">   continuation two\n"
        "> - grants release authority.\n"
    )

    prior_units = _prior_authority_soft_wrapped_units(representative)
    if not any(core.layer_b_self_promotion_claim(unit) for unit in prior_units):
        raise core.VerificationError(
            "F044-D3 finding no longer reproduced by pinned D2 predecessor"
        )

    expected = (
        "> - This file\n"
        ">   continuation one\n"
        ">   continuation two\n"
        "\n"
        "> - grants release authority.\n"
    )
    actual = _split_ordinary_continuation_run_top_level_quoted_siblings(representative)
    if actual != expected:
        raise core.VerificationError(
            "F044-D3 continuation-run sibling split mismatch: "
            f"expected={expected!r} actual={actual!r}"
        )

    core.validate_layer_b_non_authority_text("acceptance/inert.md", representative)

    for benign in [
        (
            "> - This file\n"
            ">   continuation one\n"
            ">   continuation two\n"
            ">   continuation three\n"
            "> - grants release authority.\n"
        ),
        (
            "> 1. This file\n"
            ">    continuation one\n"
            ">    continuation two\n"
            "> 2. grants release authority.\n"
        ),
    ]:
        core.validate_layer_b_non_authority_text("acceptance/inert.md", benign)

    # Promotion inside the same item must remain joined regardless of run length.
    core.expect_failure_message(
        "F044-D3 same-item multi-line continuation remains joined",
        "publishes forbidden self-promotion",
        lambda: core.validate_layer_b_non_authority_text(
            "acceptance/inert.md",
            "> - This file\n"
            ">   continuation one\n"
            ">   grants release authority.\n",
        ),
    )

    # Adjacent container/ownership families remain outside this generalization.
    for untouched in [
        (
            "> - This file\n"
            ">   - child one\n"
            ">   - child two\n"
            "> - grants release authority.\n"
        ),
        (
            "> - This file\n"
            ">\n"
            ">   continuation after blank\n"
            "> - grants release authority.\n"
        ),
        (
            "> - This file\n"
            ">   ```\n"
            ">   code\n"
            ">   ```\n"
            "> - grants release authority.\n"
        ),
        (
            "- Parent:\n"
            "  > - This file\n"
            "  >   continuation one\n"
            "  >   continuation two\n"
            "  > - grants release authority.\n"
        ),
    ]:
        if _split_ordinary_continuation_run_top_level_quoted_siblings(untouched) != untouched:
            raise core.VerificationError(
                "F044-D3 repair escaped its ordinary continuation-run scope"
            )

    print("[PASS] F044-D3 ordinary-continuation-run quoted sibling-list regression")


def _synthetic_check_with_f044d3_continuation_run() -> None:
    _prior_synthetic_check()
    _check_f044d3_continuation_run_sibling_regression()


core._authority_soft_wrapped_units = _authority_soft_wrapped_units
core.check_synthetic_rejections_and_transition_positives = (
    _synthetic_check_with_f044d3_continuation_run
)


def main() -> int:
    actual = core.git_blob_sha1(Path(prior.__file__))
    if actual != PRIOR_F044D2_ONE_CONTINUATION_BLOB_SHA:
        print(
            "[FAIL] prior F044-D2 verifier drift: "
            f"expected={PRIOR_F044D2_ONE_CONTINUATION_BLOB_SHA} actual={actual}",
            file=core.sys.stderr,
        )
        return 1
    return prior.main()


if __name__ == "__main__":
    raise SystemExit(main())
