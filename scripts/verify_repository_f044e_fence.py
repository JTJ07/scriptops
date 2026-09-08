#!/usr/bin/env python3
"""Bounded F044-E complete top-level quoted fenced-code boundary overlay.

The repaired F044-D verifier is retained byte-for-byte at
`scripts/verify_repository_f044d_sibling_list.py` and pinned by Git blob SHA.
This entrypoint changes only complete source-column-zero block-quoted fenced-code
spans whose inner opening fence begins at indentation zero. The entire explicit
quoted fence is isolated as one authority leaf from adjacent quoted paragraphs.

Unclosed fences, indented inner fences, nested quotes and list-owned outer quote
recursion remain intentionally outside this repair.
"""
from __future__ import annotations

from pathlib import Path
import verify_repository_f044d_sibling_list as prior

PRIOR_F044D_SIBLING_LIST_BLOB_SHA = "4052f012fef7791e23f6ced77014f2fd6802b4a5"

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


def _isolate_complete_top_level_quoted_fences(text: str) -> str:
    """Add parser blanks around only complete explicit quoted fence spans."""
    lines = text.splitlines()
    output: list[str] = []
    index = 0

    while index < len(lines):
        content = _top_level_quote_content(lines[index])
        opening = (
            singleline._markdown_fenced_code_opening_layout(content)
            if content is not None
            else None
        )
        if opening is None or opening[0] != 0:
            output.append(lines[index])
            index += 1
            continue

        _, marker, fence_length = opening
        closing_index: int | None = None
        probe = index + 1
        while probe < len(lines):
            probe_content = _top_level_quote_content(lines[probe])
            if probe_content is None:
                break
            closing = singleline._markdown_fenced_code_closing_layout(
                probe_content,
                marker,
                fence_length,
            )
            if closing is not None and closing <= 3:
                closing_index = probe
                break
            probe += 1

        if closing_index is None:
            output.append(lines[index])
            index += 1
            continue

        if output and output[-1].strip():
            output.append("")
        output.extend(lines[index : closing_index + 1])
        output.append("")
        index = closing_index + 1

    result = "\n".join(output)
    if text.endswith(("\n", "\r")):
        result += "\n"
    return result


def _authority_soft_wrapped_units(text: str) -> list[str]:
    return _prior_authority_soft_wrapped_units(
        _isolate_complete_top_level_quoted_fences(text)
    )


def _check_f044e_quoted_fence_boundary_regression() -> None:
    representative = (
        "> ```\n"
        "> This file\n"
        "> ```\n"
        "> grants release authority.\n"
    )

    prior_units = _prior_authority_soft_wrapped_units(representative)
    if not any(core.layer_b_self_promotion_claim(unit) for unit in prior_units):
        raise core.VerificationError(
            "F044-E quoted-fence finding no longer reproduced by pinned predecessor"
        )

    expected = (
        "> ```\n"
        "> This file\n"
        "> ```\n"
        "\n"
        "> grants release authority.\n"
    )
    actual = _isolate_complete_top_level_quoted_fences(representative)
    if actual != expected:
        raise core.VerificationError(
            "F044-E quoted-fence isolation mismatch: "
            f"expected={expected!r} actual={actual!r}"
        )

    core.validate_layer_b_non_authority_text("acceptance/inert.md", representative)

    core.validate_layer_b_non_authority_text(
        "acceptance/inert.md",
        "> ~~~\n> This file\n> ~~~\n> grants release authority.\n",
    )

    # Security-visible content inside one quoted fence remains one leaf.
    for label, rejected in [
        (
            "F044-E same fenced line keeps self-promotion together",
            "> ```\n> This file grants release authority.\n> ```\n",
        ),
        (
            "F044-E multiline fenced payload remains one leaf",
            "> ```\n> This file\n> grants release authority.\n> ```\n",
        ),
    ]:
        core.expect_failure_message(
            label,
            "publishes forbidden self-promotion",
            lambda rejected=rejected: core.validate_layer_b_non_authority_text(
                "acceptance/inert.md", rejected
            ),
        )

    # Adjacent fence families remain outside this exact repair.
    for untouched in [
        "> ```\n> This file\n> grants release authority.\n",
        ">   ```\n> This file\n>   ```\n> grants release authority.\n",
        "> > ```\n> > This file\n> > ```\n> grants release authority.\n",
        "- Parent:\n  > ```\n  > This file\n  > ```\n  > grants release authority.\n",
    ]:
        if _isolate_complete_top_level_quoted_fences(untouched) != untouched:
            raise core.VerificationError(
                "F044-E repair escaped its complete top-level quoted-fence scope"
            )

    print("[PASS] F044-E complete top-level quoted fenced-code boundary regression")


def _synthetic_check_with_f044e_quoted_fence_boundary() -> None:
    _prior_synthetic_check()
    _check_f044e_quoted_fence_boundary_regression()


core._authority_soft_wrapped_units = _authority_soft_wrapped_units
core.check_synthetic_rejections_and_transition_positives = (
    _synthetic_check_with_f044e_quoted_fence_boundary
)


def main() -> int:
    actual = core.git_blob_sha1(Path(prior.__file__))
    if actual != PRIOR_F044D_SIBLING_LIST_BLOB_SHA:
        print(
            "[FAIL] prior F044-D verifier drift: "
            f"expected={PRIOR_F044D_SIBLING_LIST_BLOB_SHA} actual={actual}",
            file=core.sys.stderr,
        )
        return 1
    return prior.main()


if __name__ == "__main__":
    raise SystemExit(main())
