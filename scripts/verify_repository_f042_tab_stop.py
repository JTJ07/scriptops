#!/usr/bin/env python3
"""Bounded F042 block-quote tab-stop/source-column overlay.

The previous fully repaired F043 verifier is retained byte-for-byte at
`scripts/verify_repository_f043_list_setext.py` and pinned by Git blob SHA.
This entrypoint changes only the known F042 quote-marker normalization case in
which one literal space after `>` is followed by a tab. The tab's remaining
indentation is preserved at its original source column before the frozen F041
quoted-indented-code classification runs.

F044 remains intentionally unresolved. No wider quote recursion/laziness change
is made here.
"""
from __future__ import annotations

from pathlib import Path
import re
import verify_repository_f043_list_setext as prior

PRIOR_F043_LIST_SETEXT_BLOB_SHA = "8583a2358c9cdb8b3a30130310f775da277c159a"

core = prior.core
singleline = prior.singleline
_prior_synthetic_check = core.check_synthetic_rejections_and_transition_positives
_frozen_block_quote_layout = singleline._markdown_block_quote_layout

_F042_SPACE_TAB_AFTER_QUOTE_RE = re.compile(r"^(?P<indent> {0,3})> \t")


def _markdown_block_quote_layout(
    raw_line: str,
    *,
    allow_deep_indent: bool = False,
) -> tuple[int, str] | None:
    """Preserve the source-column width of the F042 post-marker tab case."""
    layout = _frozen_block_quote_layout(
        raw_line,
        allow_deep_indent=allow_deep_indent,
    )
    if layout is None:
        return None

    marker_indent, content = layout
    match = _F042_SPACE_TAB_AFTER_QUOTE_RE.match(raw_line)
    if match is None or not content.startswith("\t"):
        return layout

    # The frozen parser has consumed the literal marker-following space and
    # detached the remaining tab from its source column. Re-express exactly the
    # tab width it had at that point as ordinary spaces so the frozen
    # zero-origin column counter sees the same indentation width.
    tab_column = len(match.group("indent")) + 2
    tab_width = 4 - (tab_column % 4)
    return marker_indent, (" " * tab_width) + content[1:]


def _check_f042_quote_tab_stop_regression() -> None:
    representative = "> \tThis file\n> grants release authority.\n"

    frozen = _frozen_block_quote_layout(representative.splitlines()[0])
    if frozen is None or core._markdown_leading_columns(frozen[1]) != 4:
        raise core.VerificationError(
            "F042 finding no longer reproduced by pinned predecessor"
        )

    repaired = _markdown_block_quote_layout(representative.splitlines()[0])
    if repaired is None or core._markdown_leading_columns(repaired[1]) != 2:
        raise core.VerificationError(
            "F042 repair did not preserve the original post-marker tab width"
        )

    if singleline._markdown_block_quote_layout is not _markdown_block_quote_layout:
        raise core.VerificationError("F042 live singleline quote-layout seam is not patched")

    core.expect_failure_message(
        "F042 quote space-tab remains one quoted paragraph",
        "publishes forbidden self-promotion",
        lambda: core.validate_layer_b_non_authority_text(
            "acceptance/inert.md", representative
        ),
    )

    # Existing controls from the frozen finding remain unchanged.
    core.expect_failure_message(
        "F042 direct post-marker tab remains non-code",
        "publishes forbidden self-promotion",
        lambda: core.validate_layer_b_non_authority_text(
            "acceptance/inert.md",
            ">\tThis file\n> grants release authority.\n",
        ),
    )
    core.validate_layer_b_non_authority_text(
        "acceptance/inert.md",
        ">\t\tThis file\n> grants release authority.\n",
    )

    print("[PASS] F042 block-quote tab-stop/source-column regression")


def _synthetic_check_with_f042_quote_tab_stop() -> None:
    _prior_synthetic_check()
    _check_f042_quote_tab_stop_regression()


# F043's single-line parser captured the F041 quote-layout callable at import
# time, so patch the live alias as well as the frozen core seam. The algorithm
# itself remains unchanged outside the one F042 source-column case above.
singleline._markdown_block_quote_layout = _markdown_block_quote_layout
core._markdown_block_quote_layout = _markdown_block_quote_layout
core.check_synthetic_rejections_and_transition_positives = (
    _synthetic_check_with_f042_quote_tab_stop
)


def main() -> int:
    actual = core.git_blob_sha1(Path(prior.__file__))
    if actual != PRIOR_F043_LIST_SETEXT_BLOB_SHA:
        print(
            "[FAIL] prior F043 verifier drift: "
            f"expected={PRIOR_F043_LIST_SETEXT_BLOB_SHA} actual={actual}",
            file=core.sys.stderr,
        )
        return 1
    return prior.main()


if __name__ == "__main__":
    raise SystemExit(main())
