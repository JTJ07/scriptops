#!/usr/bin/env python3
"""Minimal F043 blockquote-lazy destination-continuation overlay.

The previous F043 bare-destination angle-character verifier is retained
byte-for-byte at
`scripts/verify_repository_f043_bare_destination_angle_char.py` and pinned by
Git blob SHA. This entrypoint repairs only one remaining CommonMark shape: an
explicit block-quote line containing `[label]:` may take its destination from
exactly one following legal lazy-continuation line that omits `>`.

F042 and F044 remain intentionally unresolved. This bounded overlay does not
attempt the wider blockquote-lazy multiline-definition family.
"""
from __future__ import annotations

from pathlib import Path
import re
import verify_repository_f043_bare_destination_angle_char as prior

PRIOR_F043_BARE_DESTINATION_ANGLE_CHAR_BLOB_SHA = (
    "a81ba336e7b324961988cee89e107680a5c6b76f"
)

core = prior.core
singleline = prior.singleline
_prior_soft_wrapped_units = core._authority_soft_wrapped_units
_prior_synthetic_check = core.check_synthetic_rejections_and_transition_positives

_QUOTE_LINE_RE = re.compile(r"^(?P<prefix> {0,3}>[ \t]?)(?P<body>.*)$")


def _fold_blockquote_lazy_destination_definition(text: str) -> str:
    """Fold only `> [label]:` plus one legal unmarked destination line.

    The current single-line recognizer remains the grammar oracle. The adapter
    activates only when the quoted first line ends at the definition colon, the
    next physical line is not itself quoted, that line is legal blockquote lazy
    paragraph continuation, and the two payloads together form a valid link
    reference definition under the already-repaired F043 grammar.
    """
    lines = text.splitlines()
    output: list[str] = []
    index = 0

    while index < len(lines):
        first = _QUOTE_LINE_RE.match(lines[index])
        if first is not None and index + 1 < len(lines):
            first_body = first.group("body").lstrip(" \t")
            next_raw = lines[index + 1]

            if (
                first_body.startswith("[")
                and first_body.rstrip().endswith(":")
                and singleline._markdown_link_reference_definition_layout(first_body)
                is None
                and _QUOTE_LINE_RE.match(next_raw) is None
                and next_raw.strip()
                and singleline._markdown_block_quote_lazy_paragraph(next_raw)
            ):
                candidate = f"{first_body} {next_raw.strip()}"
                if (
                    singleline._markdown_link_reference_definition_layout(candidate)
                    is not None
                ):
                    output.append(first.group("prefix") + candidate)
                    index += 2
                    continue

        output.append(lines[index])
        index += 1

    result = "\n".join(output)
    if text.endswith(("\n", "\r")):
        result += "\n"
    return result


def _authority_soft_wrapped_units(text: str) -> list[str]:
    return _prior_soft_wrapped_units(_fold_blockquote_lazy_destination_definition(text))


def _check_f043_blockquote_lazy_destination_regression() -> None:
    source = "> [This file]:\n/url\n> grants release authority.\n"

    # Non-vacuity: the pinned predecessor must still fuse the source into a
    # forbidden self-promotion unit, reproducing the reviewed finding.
    prior_units = _prior_soft_wrapped_units(source)
    if not any(core.layer_b_self_promotion_claim(unit) for unit in prior_units):
        raise core.VerificationError(
            "F043 blockquote-lazy finding no longer reproduced by pinned predecessor"
        )

    expected_fold = "> [This file]: /url\n> grants release authority.\n"
    actual_fold = _fold_blockquote_lazy_destination_definition(source)
    if actual_fold != expected_fold:
        raise core.VerificationError(
            "F043 blockquote-lazy destination fold mismatch: "
            f"expected={expected_fold!r} actual={actual_fold!r}"
        )

    # Exact reviewed counterexample must now be accepted as inert metadata plus
    # a separate quoted paragraph.
    core.validate_layer_b_non_authority_text("acceptance/inert.md", source)

    print("[PASS] F043 blockquote-lazy destination continuation regression")


def _synthetic_check_with_f043_blockquote_lazy_destination() -> None:
    _prior_synthetic_check()
    _check_f043_blockquote_lazy_destination_regression()


# Patch only the authority-unit input seam. All previously pinned link grammar
# and multiline/list collectors remain unchanged.
core._authority_soft_wrapped_units = _authority_soft_wrapped_units
core.check_synthetic_rejections_and_transition_positives = (
    _synthetic_check_with_f043_blockquote_lazy_destination
)


def main() -> int:
    actual = core.git_blob_sha1(Path(prior.__file__))
    if actual != PRIOR_F043_BARE_DESTINATION_ANGLE_CHAR_BLOB_SHA:
        print(
            "[FAIL] F043 bare-destination angle-character verifier drift: "
            f"expected={PRIOR_F043_BARE_DESTINATION_ANGLE_CHAR_BLOB_SHA} actual={actual}",
            file=core.sys.stderr,
        )
        return 1
    return prior.main()


if __name__ == "__main__":
    raise SystemExit(main())
