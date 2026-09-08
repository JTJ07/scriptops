#!/usr/bin/env python3
"""Bounded F044-B top-level quoted thematic-boundary overlay.

The repaired F044-A verifier is retained byte-for-byte at
`scripts/verify_repository_f044a_nested_laziness.py` and pinned by Git blob SHA.
This entrypoint changes only one inner block boundary: a source-column-zero
explicit block-quote line whose quote content is a valid CommonMark thematic
break is isolated from the quoted leaf before and after it.

F044-C/D/E quoted blank/list/fence families and list-owned quote recursion remain
intentionally unresolved.
"""
from __future__ import annotations

from pathlib import Path
import verify_repository_f044a_nested_laziness as prior

PRIOR_F044A_NESTED_LAZINESS_BLOB_SHA = "4e7a187e468884ab3c89c1505a8c9c23bec283dc"

core = prior.core
singleline = prior.singleline
_prior_authority_soft_wrapped_units = core._authority_soft_wrapped_units
_prior_synthetic_check = core.check_synthetic_rejections_and_transition_positives


def _split_top_level_quoted_thematic_boundaries(text: str) -> str:
    """Isolate only source-column-zero quoted thematic-break lines."""
    lines = text.splitlines()
    output: list[str] = []

    for raw_line in lines:
        thematic_quote = False
        if raw_line.startswith(">"):
            quote_layout = singleline._markdown_block_quote_layout(raw_line)
            if quote_layout is not None and quote_layout[0] == 0:
                _, quote_content = quote_layout
                thematic = singleline._markdown_thematic_break_layout(quote_content)
                thematic_quote = thematic is not None and thematic[0] <= 3

        if not thematic_quote:
            output.append(raw_line)
            continue

        if output and output[-1].strip():
            output.append("")
        output.append(raw_line)
        output.append("")

    result = "\n".join(output)
    if text.endswith(("\n", "\r")):
        result += "\n"
    return result


def _authority_soft_wrapped_units(text: str) -> list[str]:
    return _prior_authority_soft_wrapped_units(
        _split_top_level_quoted_thematic_boundaries(text)
    )


def _check_f044b_quoted_thematic_boundary_regression() -> None:
    representative = "> This file\n> ***\n> grants release authority.\n"

    prior_units = _prior_authority_soft_wrapped_units(representative)
    if not any(core.layer_b_self_promotion_claim(unit) for unit in prior_units):
        raise core.VerificationError(
            "F044-B thematic-boundary finding no longer reproduced by pinned predecessor"
        )

    expected = "> This file\n\n> ***\n\n> grants release authority.\n"
    actual = _split_top_level_quoted_thematic_boundaries(representative)
    if actual != expected:
        raise core.VerificationError(
            "F044-B thematic-boundary split mismatch: "
            f"expected={expected!r} actual={actual!r}"
        )

    core.validate_layer_b_non_authority_text("acceptance/inert.md", representative)

    # The bounded recognizer covers the ordinary CommonMark thematic families.
    for benign in [
        "> This file\n> ---\n> grants release authority.\n",
        "> This file\n> ___\n> grants release authority.\n",
        "> This file\n> * * *\n> grants release authority.\n",
    ]:
        core.validate_layer_b_non_authority_text("acceptance/inert.md", benign)

    # Ordinary explicit quoted paragraph continuation is not a boundary.
    core.expect_failure_message(
        "F044-B ordinary explicit quote continuation remains joined",
        "publishes forbidden self-promotion",
        lambda: core.validate_layer_b_non_authority_text(
            "acceptance/inert.md",
            "> This file\n> ordinary text\n> grants release authority.\n",
        ),
    )

    # Other F044 families stay outside this patch.
    for untouched in [
        "> This file\n>\n> grants release authority.\n",
        "> - This file\n> - grants release authority.\n",
        "> ```\n> This file\n> ```\n> grants release authority.\n",
        "- Parent:\n  > This file\n  > ***\n  > grants release authority.\n",
    ]:
        if _split_top_level_quoted_thematic_boundaries(untouched) != untouched:
            raise core.VerificationError(
                "F044-B repair escaped its top-level thematic boundary scope"
            )

    print("[PASS] F044-B top-level quoted thematic-boundary regression")


def _synthetic_check_with_f044b_quoted_thematic_boundary() -> None:
    _prior_synthetic_check()
    _check_f044b_quoted_thematic_boundary_regression()


core._authority_soft_wrapped_units = _authority_soft_wrapped_units
core.check_synthetic_rejections_and_transition_positives = (
    _synthetic_check_with_f044b_quoted_thematic_boundary
)


def main() -> int:
    actual = core.git_blob_sha1(Path(prior.__file__))
    if actual != PRIOR_F044A_NESTED_LAZINESS_BLOB_SHA:
        print(
            "[FAIL] prior F044-A verifier drift: "
            f"expected={PRIOR_F044A_NESTED_LAZINESS_BLOB_SHA} actual={actual}",
            file=core.sys.stderr,
        )
        return 1
    return prior.main()


if __name__ == "__main__":
    raise SystemExit(main())
