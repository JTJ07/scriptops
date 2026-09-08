#!/usr/bin/env python3
"""Bounded F044-D consecutive top-level quoted sibling-list overlay.

The repaired F044-C verifier is retained byte-for-byte at
`scripts/verify_repository_f044c_blank_boundary.py` and pinned by Git blob SHA.
This entrypoint changes only consecutive source-column-zero quoted list markers
at the same inner list-marker indentation: the second marker is presented as a
new authority-unit boundary.

F044-E quoted fenced-code parsing, nonconsecutive quoted siblings, nested-list
recursion and list-owned outer quote recursion remain intentionally unresolved.
"""
from __future__ import annotations

from pathlib import Path
import verify_repository_f044c_blank_boundary as prior

PRIOR_F044C_BLANK_BOUNDARY_BLOB_SHA = "6e5f33c9b19e2a5d18449c850987871c085e83ed"

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


def _split_consecutive_top_level_quoted_sibling_lists(text: str) -> str:
    """Split only consecutive same-level quoted list-marker lines.

    A tiny quoted-fence state is tracked solely as a scope guard so list-looking
    literal payload inside F044-E remains untouched.
    """
    lines = text.splitlines()
    output: list[str] = []
    previous_list_indent: int | None = None
    fence_marker: str | None = None
    fence_length = 0

    for raw_line in lines:
        content = _top_level_quote_content(raw_line)
        if content is None:
            previous_list_indent = None
            output.append(raw_line)
            continue

        if fence_marker is not None:
            closing = singleline._markdown_fenced_code_closing_layout(
                content,
                fence_marker,
                fence_length,
            )
            output.append(raw_line)
            previous_list_indent = None
            if closing is not None and closing <= 3:
                fence_marker = None
                fence_length = 0
            continue

        opening = singleline._markdown_fenced_code_opening_layout(content)
        if opening is not None and opening[0] <= 3:
            _, fence_marker, fence_length = opening
            output.append(raw_line)
            previous_list_indent = None
            continue

        layout = singleline._markdown_list_item_layout(content)
        current_list_indent = layout[0] if layout is not None else None

        if (
            current_list_indent is not None
            and previous_list_indent is not None
            and current_list_indent == previous_list_indent
            and output
            and output[-1].strip()
        ):
            output.append("")

        output.append(raw_line)
        previous_list_indent = current_list_indent

    result = "\n".join(output)
    if text.endswith(("\n", "\r")):
        result += "\n"
    return result


def _authority_soft_wrapped_units(text: str) -> list[str]:
    return _prior_authority_soft_wrapped_units(
        _split_consecutive_top_level_quoted_sibling_lists(text)
    )


def _check_f044d_quoted_sibling_list_regression() -> None:
    representative = "> - This file\n> - grants release authority.\n"

    prior_units = _prior_authority_soft_wrapped_units(representative)
    if not any(core.layer_b_self_promotion_claim(unit) for unit in prior_units):
        raise core.VerificationError(
            "F044-D sibling-list finding no longer reproduced by pinned predecessor"
        )

    expected = "> - This file\n\n> - grants release authority.\n"
    actual = _split_consecutive_top_level_quoted_sibling_lists(representative)
    if actual != expected:
        raise core.VerificationError(
            "F044-D sibling-list split mismatch: "
            f"expected={expected!r} actual={actual!r}"
        )

    core.validate_layer_b_non_authority_text("acceptance/inert.md", representative)

    for benign in [
        "> 1. This file\n> 2. grants release authority.\n",
        "> - This file\n> + grants release authority.\n",
    ]:
        core.validate_layer_b_non_authority_text("acceptance/inert.md", benign)

    # Same-item continuation and nested descendants remain joined to their item.
    for label, joined in [
        (
            "F044-D quoted list continuation remains same item",
            "> - This file\n>   grants release authority.\n",
        ),
        (
            "F044-D quoted nested list remains parent-scoped",
            "> - This file\n>   - grants release authority.\n",
        ),
    ]:
        core.expect_failure_message(
            label,
            "publishes forbidden self-promotion",
            lambda joined=joined: core.validate_layer_b_non_authority_text(
                "acceptance/inert.md", joined
            ),
        )

    # F044-E literal fenced payload is a strict scope guard, not part of D.
    fenced = (
        "> ```\n"
        "> - This file\n"
        "> - grants release authority.\n"
        "> ```\n"
    )
    if _split_consecutive_top_level_quoted_sibling_lists(fenced) != fenced:
        raise core.VerificationError(
            "F044-D repair escaped into quoted fenced-code payload"
        )

    print("[PASS] F044-D consecutive top-level quoted sibling-list regression")


def _synthetic_check_with_f044d_quoted_sibling_lists() -> None:
    _prior_synthetic_check()
    _check_f044d_quoted_sibling_list_regression()


core._authority_soft_wrapped_units = _authority_soft_wrapped_units
core.check_synthetic_rejections_and_transition_positives = (
    _synthetic_check_with_f044d_quoted_sibling_lists
)


def main() -> int:
    actual = core.git_blob_sha1(Path(prior.__file__))
    if actual != PRIOR_F044C_BLANK_BOUNDARY_BLOB_SHA:
        print(
            "[FAIL] prior F044-C verifier drift: "
            f"expected={PRIOR_F044C_BLANK_BOUNDARY_BLOB_SHA} actual={actual}",
            file=core.sys.stderr,
        )
        return 1
    return prior.main()


if __name__ == "__main__":
    raise SystemExit(main())
