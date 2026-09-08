#!/usr/bin/env python3
"""Bounded F044-A nested block-quote laziness overlay.

The repaired F042 verifier is retained byte-for-byte at
`scripts/verify_repository_f042_tab_stop.py` and pinned by Git blob SHA.
This entrypoint changes only nested block-quote paragraph laziness: an outer
quoted line whose content begins with another quote marker may carry lazy
paragraph continuation when the recursively nested content is itself an
ordinary paragraph continuation candidate.

F044-B/C/D/E explicit inner-boundary families remain intentionally unresolved.
"""
from __future__ import annotations

from pathlib import Path
import verify_repository_f042_tab_stop as prior

PRIOR_F042_TAB_STOP_BLOB_SHA = "c70969c34dbbad25455c915c748e4f143b3721af"

core = prior.core
singleline = prior.singleline
_prior_synthetic_check = core.check_synthetic_rejections_and_transition_positives
_frozen_block_quote_lazy_paragraph = singleline._markdown_block_quote_lazy_paragraph


def _markdown_block_quote_lazy_paragraph(
    content: str,
    *,
    paragraph_open: bool = False,
) -> bool:
    """Apply the frozen lazy test recursively through nested quote markers."""
    if _frozen_block_quote_lazy_paragraph(
        content,
        paragraph_open=paragraph_open,
    ):
        return True

    nested = singleline._markdown_block_quote_layout(content)
    if nested is None or nested[0] > 3:
        return False

    _, nested_content = nested
    return _markdown_block_quote_lazy_paragraph(
        nested_content,
        paragraph_open=paragraph_open,
    )


def _check_f044a_nested_quote_laziness_regression() -> None:
    representative = "> > This file\ngrants release authority.\n"

    if _frozen_block_quote_lazy_paragraph("> This file"):
        raise core.VerificationError(
            "F044-A finding no longer reproduced by pinned predecessor"
        )
    if not _markdown_block_quote_lazy_paragraph("> This file"):
        raise core.VerificationError(
            "F044-A repair still rejects nested quoted paragraph laziness"
        )

    core.expect_failure_message(
        "F044-A nested quote lazy continuation remains one paragraph",
        "publishes forbidden self-promotion",
        lambda: core.validate_layer_b_non_authority_text(
            "acceptance/inert.md", representative
        ),
    )

    # Existing explicit nested continuation remains one security unit.
    core.expect_failure_message(
        "F044-A explicit nested quote continuation remains joined",
        "publishes forbidden self-promotion",
        lambda: core.validate_layer_b_non_authority_text(
            "acceptance/inert.md",
            "> > This file\n> > grants release authority.\n",
        ),
    )

    # Nested quoted indented code is not a paragraph and therefore cannot donate
    # lazy continuation to following unquoted text.
    core.validate_layer_b_non_authority_text(
        "acceptance/inert.md",
        "> >     This file\ngrants release authority.\n",
    )

    print("[PASS] F044-A nested block-quote laziness regression")


def _synthetic_check_with_f044a_nested_quote_laziness() -> None:
    _prior_synthetic_check()
    _check_f044a_nested_quote_laziness_regression()


# F043's live parser captured the F041 lazy-paragraph callable at import time;
# bind the same bounded recursive wrapper to both live and core seams.
singleline._markdown_block_quote_lazy_paragraph = _markdown_block_quote_lazy_paragraph
core._markdown_block_quote_lazy_paragraph = _markdown_block_quote_lazy_paragraph
core.check_synthetic_rejections_and_transition_positives = (
    _synthetic_check_with_f044a_nested_quote_laziness
)


def main() -> int:
    actual = core.git_blob_sha1(Path(prior.__file__))
    if actual != PRIOR_F042_TAB_STOP_BLOB_SHA:
        print(
            "[FAIL] prior F042 verifier drift: "
            f"expected={PRIOR_F042_TAB_STOP_BLOB_SHA} actual={actual}",
            file=core.sys.stderr,
        )
        return 1
    return prior.main()


if __name__ == "__main__":
    raise SystemExit(main())
