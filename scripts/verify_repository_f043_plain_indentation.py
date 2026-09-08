#!/usr/bin/env python3
"""Bounded F043 plain-multiline source-indentation overlay.

The previous F043 dash-setext verifier is retained byte-for-byte at
`scripts/verify_repository_f043_dash_setext_destination.py` and pinned by Git
blob SHA. This entrypoint changes only the plain multiline reference-definition
collector so block-precedence classification sees physical source indentation;
normalized payload remains the input to the already-reviewed definition grammar.

F042 and F044 remain intentionally unresolved.
"""
from __future__ import annotations

from pathlib import Path
import verify_repository_f043_dash_setext_destination as prior

PRIOR_F043_DASH_SETEXT_DESTINATION_BLOB_SHA = (
    "8f8f5e87912c6af0e63b38be1d574265c1962257"
)

core = prior.core
multiline = prior.multiline
_prior_synthetic_check = core.check_synthetic_rejections_and_transition_positives
_frozen_plain_definition = multiline._try_fold_plain_definition


def _try_fold_plain_definition(
    lines: list[str], start: int
) -> tuple[int, str] | None:
    """Fold plain definitions without erasing indentation before block tests."""
    prefix = multiline._leading_whitespace(lines[start])
    first_body = lines[start][len(prefix) :]
    if not first_body.startswith("["):
        return None

    parts = [first_body]
    best = multiline._longest_valid_definition(parts)

    for index in range(start + 1, len(lines)):
        raw_line = lines[index]
        if not raw_line.strip():
            break

        if multiline._QUOTE_LINE_RE.match(raw_line) is not None:
            break
        if multiline._LIST_LINE_RE.match(raw_line) is not None:
            break

        structural_body = raw_line
        body = raw_line.lstrip(" \t")
        if multiline._payload_interrupts_paragraph(structural_body):
            break
        parts.append(body)
        candidate = multiline._longest_valid_definition(parts)
        if candidate is not None:
            best = candidate

    if best is None or best[0] <= 1:
        return None
    return best[0], prefix + best[1]


def _check_f043_plain_indentation_regression() -> None:
    source = "[This file]:\n    #\ngrants release authority.\n"
    finding_lines = source.splitlines()

    if _frozen_plain_definition(finding_lines, 0) is not None:
        raise core.VerificationError(
            "F043 plain-indentation finding no longer reproduced by pinned predecessor"
        )

    repaired = _try_fold_plain_definition(finding_lines, 0)
    if repaired != (2, "[This file]: #"):
        raise core.VerificationError(
            "F043 plain-indentation repair did not isolate the valid definition prefix: "
            f"actual={repaired!r}"
        )

    core.validate_layer_b_non_authority_text("acceptance/inert.md", source)

    print("[PASS] F043 plain multiline source-indentation regression")


def _synthetic_check_with_f043_plain_indentation() -> None:
    _prior_synthetic_check()
    _check_f043_plain_indentation_regression()


multiline._try_fold_plain_definition = _try_fold_plain_definition
core.check_synthetic_rejections_and_transition_positives = (
    _synthetic_check_with_f043_plain_indentation
)


def main() -> int:
    actual = core.git_blob_sha1(Path(prior.__file__))
    if actual != PRIOR_F043_DASH_SETEXT_DESTINATION_BLOB_SHA:
        print(
            "[FAIL] F043 dash-setext verifier drift: "
            f"expected={PRIOR_F043_DASH_SETEXT_DESTINATION_BLOB_SHA} actual={actual}",
            file=core.sys.stderr,
        )
        return 1
    return prior.main()


if __name__ == "__main__":
    raise SystemExit(main())
