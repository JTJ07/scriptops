#!/usr/bin/env python3
"""Bounded F043 equals-setext continuation inside incomplete definition overlay.

The previous F043 quoted setext-destination verifier is retained byte-for-byte
at `scripts/verify_repository_f043_quoted_setext_destination.py` and pinned by
Git blob SHA. This entrypoint changes only one precedence edge: equals-style
setext-looking content may remain in a quoted multiline reference-definition
candidate while no complete definition prefix exists yet, allowing a later line
to close an open label or title. Once a complete definition prefix exists, a
following equals-style line remains a separate block.

F042 and F044 remain intentionally unresolved.
"""
from __future__ import annotations

from pathlib import Path
import verify_repository_f043_quoted_setext_destination as prior

PRIOR_F043_QUOTED_SETEXT_DESTINATION_BLOB_SHA = (
    "d84ec2ead5cddea796bfbaa8a372faa92efce471"
)

core = prior.core
multiline = prior.multiline
_prior_synthetic_check = core.check_synthetic_rejections_and_transition_positives
_frozen_quoted_definition = prior._try_fold_quoted_definition
_equals_setext_layout = prior._equals_setext_layout


def _try_fold_quoted_definition(
    lines: list[str], start: int
) -> tuple[int, str] | None:
    """Allow `===` inside an incomplete definition, never after a complete one."""
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
            if _equals_setext_layout(structural_body) is None:
                break
            # If a complete definition prefix already exists, CommonMark has
            # finished the definition before this line. Do not absorb a later
            # setext-looking block. Otherwise retain the line as candidate text;
            # it may itself complete a destination or may sit inside an open
            # multiline label/title that is completed by a later line.
            if best is not None:
                break

        parts.append(body)
        candidate = multiline._longest_valid_definition(parts)
        if candidate is not None:
            best = candidate

    if best is None or best[0] <= 1:
        return None
    return best[0], first.group("prefix") + best[1]


def _check_f043_setext_inside_title_regressions() -> None:
    source = '> [This file]: /url "\n===\n> "\n> grants release authority.\n'
    finding_lines = source.splitlines()

    if _frozen_quoted_definition(finding_lines, 0) is not None:
        raise core.VerificationError(
            "F043 setext-inside-title finding no longer reproduced by pinned predecessor"
        )

    repaired = _try_fold_quoted_definition(finding_lines, 0)
    if repaired != (3, '> [This file]: /url " === "'):
        raise core.VerificationError(
            "F043 setext-inside-title repair did not isolate the valid definition prefix: "
            f"actual={repaired!r}"
        )

    core.validate_layer_b_non_authority_text("acceptance/inert.md", source)

    # Negative control: once the first line is already a complete definition,
    # a following equals-style line is not part of that definition.
    complete_then_equals = (
        "> [This file]: /url\n===\n> grants release authority.\n".splitlines()
    )
    if _try_fold_quoted_definition(complete_then_equals, 0) is not None:
        raise core.VerificationError(
            "F043 setext-inside-title repair absorbed `===` after a complete definition"
        )

    print("[PASS] F043 equals-setext inside incomplete definition regression")


def _synthetic_check_with_f043_setext_inside_title() -> None:
    _prior_synthetic_check()
    _check_f043_setext_inside_title_regressions()


multiline._try_fold_quoted_definition = _try_fold_quoted_definition
core.check_synthetic_rejections_and_transition_positives = (
    _synthetic_check_with_f043_setext_inside_title
)


def main() -> int:
    actual = core.git_blob_sha1(Path(prior.__file__))
    if actual != PRIOR_F043_QUOTED_SETEXT_DESTINATION_BLOB_SHA:
        print(
            "[FAIL] F043 quoted setext-destination verifier drift: "
            f"expected={PRIOR_F043_QUOTED_SETEXT_DESTINATION_BLOB_SHA} actual={actual}",
            file=core.sys.stderr,
        )
        return 1
    return prior.main()


if __name__ == "__main__":
    raise SystemExit(main())
