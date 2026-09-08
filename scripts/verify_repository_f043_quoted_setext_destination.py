#!/usr/bin/env python3
"""Bounded F043 quoted setext-like destination precedence overlay.

The previous F043 quoted-indentation verifier is retained byte-for-byte at
`scripts/verify_repository_f043_quoted_indentation.py` and pinned by Git blob
SHA. This entrypoint changes only one precedence edge in the quoted multiline
reference-definition collector: an equals-style setext-looking continuation may
be consumed when, and only when, that physical line completes a valid link
reference definition under the already-reviewed grammar.

F042 and F044 remain intentionally unresolved.
"""
from __future__ import annotations

from pathlib import Path
import verify_repository_f043_quoted_indentation as prior
import verify_repository_f043_multiline as multiline

PRIOR_F043_QUOTED_INDENTATION_BLOB_SHA = (
    "3534b2551e1c9d82d1665464529d42e615dfc94d"
)

core = prior.core
_prior_synthetic_check = core.check_synthetic_rejections_and_transition_positives
_frozen_quoted_definition = prior._try_fold_quoted_definition


def _equals_setext_layout(payload: str):
    layout = multiline.prior._markdown_setext_heading_underline_layout(payload)
    if layout is None or layout[0] > 3:
        return None
    stripped = payload.lstrip(" \t")
    return layout if stripped.startswith("=") else None


def _try_fold_quoted_definition(
    lines: list[str], start: int
) -> tuple[int, str] | None:
    """Preserve real interrupters while allowing a completing `===` destination."""
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
            structural_body = raw_line
            body = raw_line.lstrip(" \t")

        if not body.strip():
            break

        interrupted = multiline._payload_interrupts_paragraph(structural_body)
        if interrupted:
            # Equals-style setext syntax is the one bounded exception. It is
            # admitted only when this very line completes the definition; a
            # previously complete definition therefore cannot absorb it.
            if _equals_setext_layout(structural_body) is None:
                break
            completing = multiline._longest_valid_definition(parts + [body])
            if completing is None or completing[0] != len(parts) + 1:
                break

        parts.append(body)
        candidate = multiline._longest_valid_definition(parts)
        if candidate is not None:
            best = candidate

    if best is None or best[0] <= 1:
        return None
    return best[0], first.group("prefix") + best[1]


def _check_f043_quoted_setext_destination_regression() -> None:
    source = "> [This file]:\n===\n> grants release authority.\n"
    finding_lines = source.splitlines()

    if _frozen_quoted_definition(finding_lines, 0) is not None:
        raise core.VerificationError(
            "F043 quoted setext-destination finding no longer reproduced by pinned predecessor"
        )

    repaired = _try_fold_quoted_definition(finding_lines, 0)
    if repaired != (2, "> [This file]: ==="):
        raise core.VerificationError(
            "F043 quoted setext-destination repair did not isolate the valid definition prefix: "
            f"actual={repaired!r}"
        )

    core.validate_layer_b_non_authority_text("acceptance/inert.md", source)

    print("[PASS] F043 quoted equals-setext destination precedence regression")


def _synthetic_check_with_f043_quoted_setext_destination() -> None:
    _prior_synthetic_check()
    _check_f043_quoted_setext_destination_regression()


multiline._try_fold_quoted_definition = _try_fold_quoted_definition
core.check_synthetic_rejections_and_transition_positives = (
    _synthetic_check_with_f043_quoted_setext_destination
)


def main() -> int:
    actual = core.git_blob_sha1(Path(prior.__file__))
    if actual != PRIOR_F043_QUOTED_INDENTATION_BLOB_SHA:
        print(
            "[FAIL] F043 quoted-indentation verifier drift: "
            f"expected={PRIOR_F043_QUOTED_INDENTATION_BLOB_SHA} actual={actual}",
            file=core.sys.stderr,
        )
        return 1
    return prior.main()


if __name__ == "__main__":
    raise SystemExit(main())
