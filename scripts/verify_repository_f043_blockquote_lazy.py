#!/usr/bin/env python3
"""Bounded F043 blockquote-lazy multiline definition overlay.

The previous F043 bare-destination angle-character verifier is retained
byte-for-byte at `scripts/verify_repository_f043_bare_destination_angle_char.py`
and pinned by Git blob SHA. This entrypoint changes only top-level block-quote
multiline link-reference-definition collection so legal lazy paragraph
continuation may omit a repeated `>` marker. F042 and F044 remain intentionally
unresolved.
"""
from __future__ import annotations

from pathlib import Path
import verify_repository_f043_bare_destination_angle_char as prior
import verify_repository_f043_multiline as multiline

PRIOR_F043_BARE_DESTINATION_ANGLE_CHAR_BLOB_SHA = (
    "a81ba336e7b324961988cee89e107680a5c6b76f"
)

core = prior.core
_prior_synthetic_check = core.check_synthetic_rejections_and_transition_positives
_frozen_quoted_definition = multiline._try_fold_quoted_definition


def _try_fold_quoted_definition(
    lines: list[str], start: int
) -> tuple[int, str] | None:
    """Fold a quoted multiline definition, including legal lazy lines.

    CommonMark block-quote paragraph continuation may omit the `>` marker.
    Link-reference definitions are extracted from that paragraph candidate, so
    continuation lines must be considered after container-marker omission too.
    Structural paragraph interrupters remain boundaries exactly as in the
    frozen multiline overlay.
    """
    first = multiline._QUOTE_LINE_RE.match(lines[start])
    if first is None:
        return None
    first_body = first.group("body").lstrip(" \t")
    if not first_body.startswith("["):
        return None

    parts = [first_body]
    best = multiline._longest_valid_definition(parts)

    for index in range(start + 1, len(lines)):
        raw_line = lines[index]
        explicit = multiline._QUOTE_LINE_RE.match(raw_line)
        if explicit is not None:
            body = explicit.group("body").lstrip(" \t")
        else:
            # A missing quote marker is admissible only as paragraph lazy
            # continuation. The frozen block-precedence gate below rejects
            # lines that would start an interrupting block instead.
            body = raw_line.lstrip(" \t")

        if not body.strip() or multiline._payload_interrupts_paragraph(body):
            break

        parts.append(body)
        candidate = multiline._longest_valid_definition(parts)
        if candidate is not None:
            best = candidate

    if best is None or best[0] <= 1:
        return None
    return best[0], first.group("prefix") + best[1]


def _check_f043_blockquote_lazy_definition_regressions() -> None:
    # False-positive closures: missing `>` on a legal paragraph continuation
    # line does not end the block quote. The definition metadata is extracted
    # before the later promotion paragraph is checked.
    for benign in [
        "> [This file]:\n/url\n> grants release authority.\n",
        "> [\nThis file\n> ]: /url\n> grants release authority.\n",
        "> [This file]:\n/url \"metadata\"\n> grants release authority.\n",
    ]:
        core.validate_layer_b_non_authority_text("acceptance/inert.md", benign)

    # Security preservation: authority-bearing definition metadata remains in
    # the security-visible definition unit even when one continuation line is
    # lazy and omits the quote marker.
    core.expect_failure_message(
        "F043 blockquote-lazy definition metadata remains security-relevant",
        "publishes forbidden self-promotion",
        lambda: core.validate_layer_b_non_authority_text(
            "acceptance/inert.md",
            "> [This file grants release authority]:\n/url\n",
        ),
    )

    # Structural interruption must still stop collection rather than being
    # reclassified as a lazy definition continuation.
    structural_lines = "> [\n# heading\n> ]: /url\n".splitlines()
    if _try_fold_quoted_definition(structural_lines, 0) is not None:
        raise core.VerificationError(
            "F043 blockquote-lazy collector crossed a structural paragraph interrupter"
        )

    # Non-vacuity: the frozen collector must still reproduce the exact finding,
    # while this bounded collector must fold exactly the definition prefix.
    finding_lines = (
        "> [This file]:\n/url\n> grants release authority.\n".splitlines()
    )
    if _frozen_quoted_definition(finding_lines, 0) is not None:
        raise core.VerificationError(
            "F043 blockquote-lazy finding no longer reproduced by pinned multiline core"
        )
    repaired = _try_fold_quoted_definition(finding_lines, 0)
    if repaired != (2, "> [This file]: /url"):
        raise core.VerificationError(
            "F043 blockquote-lazy repair did not isolate the valid definition prefix: "
            f"actual={repaired!r}"
        )

    # Preserve the already-supported explicit-marker multiline quote form.
    explicit_lines = (
        "> [This file]:\n> /url\n> grants release authority.\n".splitlines()
    )
    explicit = _try_fold_quoted_definition(explicit_lines, 0)
    if explicit != (2, "> [This file]: /url"):
        raise core.VerificationError(
            "F043 blockquote-lazy repair broke explicit-marker quote folding: "
            f"actual={explicit!r}"
        )

    print("[PASS] F043 blockquote-lazy multiline definition regression")


def _synthetic_check_with_f043_blockquote_lazy_definition() -> None:
    _prior_synthetic_check()
    _check_f043_blockquote_lazy_definition_regressions()


# Patch only the top-level quoted-definition collector used by the frozen
# multiline folding pass. All other quote/list/core semantics remain pinned.
multiline._try_fold_quoted_definition = _try_fold_quoted_definition
core.check_synthetic_rejections_and_transition_positives = (
    _synthetic_check_with_f043_blockquote_lazy_definition
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
