#!/usr/bin/env python3
"""Bounded F043 quoted-multiline source-indentation overlay.

The previous F043 blockquote-lazy verifier is retained byte-for-byte at
`scripts/verify_repository_f043_blockquote_lazy.py` and pinned by Git blob SHA.
This entrypoint changes only structural-interrupter classification for quoted
multiline link-reference-definition continuation: source indentation is
preserved for block-structure classification, while normalized payload remains
used by the already-reviewed definition grammar oracle.

F042 and F044 remain intentionally unresolved.
"""
from __future__ import annotations

from pathlib import Path
import verify_repository_f043_blockquote_lazy as prior
import verify_repository_f043_multiline as multiline

PRIOR_F043_BLOCKQUOTE_LAZY_BLOB_SHA = (
    "36eeadeddd7cc255ff2d8d67020938d662456eeb"
)

core = prior.core
_prior_synthetic_check = core.check_synthetic_rejections_and_transition_positives
_frozen_quoted_definition = prior._try_fold_quoted_definition


def _try_fold_quoted_definition(
    lines: list[str], start: int
) -> tuple[int, str] | None:
    """Fold quoted definitions without erasing indentation before block tests."""
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
            structural_body = explicit.group("body")
            body = structural_body.lstrip(" \t")
        else:
            # Keep the physical indentation for block-precedence tests. Only
            # the payload passed to the definition grammar is normalized.
            structural_body = raw_line
            body = raw_line.lstrip(" \t")

        if not body.strip() or multiline._payload_interrupts_paragraph(
            structural_body
        ):
            break

        parts.append(body)
        candidate = multiline._longest_valid_definition(parts)
        if candidate is not None:
            best = candidate

    if best is None or best[0] <= 1:
        return None
    return best[0], first.group("prefix") + best[1]


def _check_f043_quoted_indentation_regression() -> None:
    source = "> [This file]:\n    #\n> grants release authority.\n"
    finding_lines = source.splitlines()

    # Non-vacuity: the pinned predecessor must still reproduce the reviewed
    # indentation-erasure failure.
    if _frozen_quoted_definition(finding_lines, 0) is not None:
        raise core.VerificationError(
            "F043 quoted-indentation finding no longer reproduced by pinned predecessor"
        )

    repaired = _try_fold_quoted_definition(finding_lines, 0)
    if repaired != (2, "> [This file]: #"):
        raise core.VerificationError(
            "F043 quoted-indentation repair did not isolate the valid definition prefix: "
            f"actual={repaired!r}"
        )

    core.validate_layer_b_non_authority_text("acceptance/inert.md", source)

    print("[PASS] F043 quoted multiline source-indentation regression")


def _synthetic_check_with_f043_quoted_indentation() -> None:
    _prior_synthetic_check()
    _check_f043_quoted_indentation_regression()


# Patch only the same top-level quoted-definition collector. All previous
# destination/title/list/block semantics remain pinned in the predecessor chain.
multiline._try_fold_quoted_definition = _try_fold_quoted_definition
core.check_synthetic_rejections_and_transition_positives = (
    _synthetic_check_with_f043_quoted_indentation
)


def main() -> int:
    actual = core.git_blob_sha1(Path(prior.__file__))
    if actual != PRIOR_F043_BLOCKQUOTE_LAZY_BLOB_SHA:
        print(
            "[FAIL] F043 blockquote-lazy verifier drift: "
            f"expected={PRIOR_F043_BLOCKQUOTE_LAZY_BLOB_SHA} actual={actual}",
            file=core.sys.stderr,
        )
        return 1
    return prior.main()


if __name__ == "__main__":
    raise SystemExit(main())
