#!/usr/bin/env python3
"""Bounded F043 plain setext-inside-incomplete-definition overlay.

The previous F043 plain-indentation verifier is retained byte-for-byte at
`scripts/verify_repository_f043_plain_indentation.py` and pinned by Git blob
SHA. This entrypoint changes only one precedence edge in the plain multiline
reference-definition collector: already-bounded non-structural setext-looking
content may remain in an incomplete definition candidate while no complete
definition prefix exists yet, allowing a later label/title closer.

F042 and F044 remain intentionally unresolved.
"""
from __future__ import annotations

from pathlib import Path
import verify_repository_f043_plain_indentation as prior

PRIOR_F043_PLAIN_INDENTATION_BLOB_SHA = (
    "d40169c63c95519e5e14805ffbd6957397eb47bf"
)

core = prior.core
multiline = prior.multiline
_prior_synthetic_check = core.check_synthetic_rejections_and_transition_positives
_frozen_plain_definition = prior._try_fold_plain_definition
_setext_candidate_exception = prior.prior._setext_candidate_exception


def _try_fold_plain_definition(
    lines: list[str], start: int
) -> tuple[int, str] | None:
    """Allow bounded setext-looking text only inside an incomplete definition."""
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
        interrupted = multiline._payload_interrupts_paragraph(structural_body)
        if interrupted:
            if _setext_candidate_exception(structural_body) is None:
                break
            # A setext-looking line can remain candidate content only while the
            # reference definition is still incomplete. A complete prefix ends
            # before this line, exactly as in CommonMark examples 215/216.
            if best is not None:
                break

        parts.append(body)
        candidate = multiline._longest_valid_definition(parts)
        if candidate is not None:
            best = candidate

    if best is None or best[0] <= 1:
        return None
    return best[0], prefix + best[1]


def _check_f043_plain_setext_title_regressions() -> None:
    security_source = '[This file]: /url "\n===\ngrants release authority\n"\n'
    security_lines = security_source.splitlines()

    if _frozen_plain_definition(security_lines, 0) is not None:
        raise core.VerificationError(
            "F043 plain setext-title finding no longer reproduced by pinned predecessor"
        )

    repaired = _try_fold_plain_definition(security_lines, 0)
    if repaired != (4, '[This file]: /url " === grants release authority "'):
        raise core.VerificationError(
            "F043 plain setext-title repair did not retain the complete definition: "
            f"actual={repaired!r}"
        )

    # The whole valid definition is security-visible metadata. Self-reference
    # and promotion may not be split by the setext-looking title line.
    core.expect_failure_message(
        "F043 plain setext-title metadata remains security-relevant",
        "publishes forbidden self-promotion",
        lambda: core.validate_layer_b_non_authority_text(
            "acceptance/inert.md", security_source
        ),
    )

    # Benign destination-only form must likewise be extracted before the later
    # paragraph rather than becoming a synthetic heading boundary.
    core.validate_layer_b_non_authority_text(
        "acceptance/inert.md",
        "[This file]:\n===\ngrants release authority.\n",
    )

    # Once a definition is already complete, a later setext-looking line is a
    # separate block and must not be absorbed into that definition.
    complete_then_equals = (
        "[This file]: /url\n===\ngrants release authority.\n".splitlines()
    )
    if _try_fold_plain_definition(complete_then_equals, 0) is not None:
        raise core.VerificationError(
            "F043 plain setext-title repair absorbed `===` after a complete definition"
        )

    print("[PASS] F043 plain setext inside incomplete definition regression")


def _synthetic_check_with_f043_plain_setext_title() -> None:
    _prior_synthetic_check()
    _check_f043_plain_setext_title_regressions()


multiline._try_fold_plain_definition = _try_fold_plain_definition
core.check_synthetic_rejections_and_transition_positives = (
    _synthetic_check_with_f043_plain_setext_title
)


def main() -> int:
    actual = core.git_blob_sha1(Path(prior.__file__))
    if actual != PRIOR_F043_PLAIN_INDENTATION_BLOB_SHA:
        print(
            "[FAIL] F043 plain-indentation verifier drift: "
            f"expected={PRIOR_F043_PLAIN_INDENTATION_BLOB_SHA} actual={actual}",
            file=core.sys.stderr,
        )
        return 1
    return prior.main()


if __name__ == "__main__":
    raise SystemExit(main())
