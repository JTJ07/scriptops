#!/usr/bin/env python3
"""Bounded F043 non-structural dash-setext destination overlay.

The previous F043 setext-inside-incomplete-definition verifier is retained
byte-for-byte at `scripts/verify_repository_f043_setext_inside_title.py` and
pinned by Git blob SHA. This entrypoint extends only the setext exception to the
dash family when the same source line is neither an interrupting list item nor
a thematic break. Thus `--` may remain reference-definition candidate content,
while `-` and `---`/longer structural forms remain boundaries.

F042 and F044 remain intentionally unresolved.
"""
from __future__ import annotations

from pathlib import Path
import verify_repository_f043_setext_inside_title as prior

PRIOR_F043_SETEXT_INSIDE_TITLE_BLOB_SHA = (
    "1601a04573f3151a60ef861f4cb0757907173805"
)

core = prior.core
multiline = prior.multiline
_prior_synthetic_check = core.check_synthetic_rejections_and_transition_positives
_frozen_quoted_definition = prior._try_fold_quoted_definition
_equals_setext_layout = prior._equals_setext_layout


def _dash_setext_without_independent_interrupt(payload: str):
    setext = multiline.prior._markdown_setext_heading_underline_layout(payload)
    if setext is None or setext[0] > 3 or setext[1] != "-":
        return None

    thematic = multiline.prior._markdown_thematic_break_layout(payload)
    if thematic is not None and thematic[0] <= 3:
        return None

    list_item = multiline.prior._markdown_list_item_layout(payload)
    if list_item is not None and list_item[3]:
        return None

    # Defensive exact structural exclusion for marker-only `-` even if a
    # future list-layout refactor changes the interrupt flag representation.
    if payload.lstrip(" \t").rstrip(" \t") == "-":
        return None
    return setext


def _setext_candidate_exception(payload: str):
    return _equals_setext_layout(payload) or _dash_setext_without_independent_interrupt(
        payload
    )


def _try_fold_quoted_definition(
    lines: list[str], start: int
) -> tuple[int, str] | None:
    """Admit only non-structural setext-looking text in incomplete definitions."""
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
            if _setext_candidate_exception(structural_body) is None:
                break
            if best is not None:
                break

        parts.append(body)
        candidate = multiline._longest_valid_definition(parts)
        if candidate is not None:
            best = candidate

    if best is None or best[0] <= 1:
        return None
    return best[0], first.group("prefix") + best[1]


def _check_f043_dash_setext_destination_regressions() -> None:
    source = "> [This file]:\n--\n> grants release authority.\n"
    finding_lines = source.splitlines()

    if _frozen_quoted_definition(finding_lines, 0) is not None:
        raise core.VerificationError(
            "F043 dash-setext destination finding no longer reproduced by pinned predecessor"
        )

    repaired = _try_fold_quoted_definition(finding_lines, 0)
    if repaired != (2, "> [This file]: --"):
        raise core.VerificationError(
            "F043 dash-setext destination repair did not isolate the valid definition prefix: "
            f"actual={repaired!r}"
        )

    core.validate_layer_b_non_authority_text("acceptance/inert.md", source)

    # Structural negative controls: marker-only `-` is an empty list item and
    # `---` is a thematic break, so neither may be swallowed as a destination.
    for marker in ["-", "---", "----"]:
        structural = (
            f"> [This file]:\n{marker}\n> grants release authority.\n".splitlines()
        )
        if _try_fold_quoted_definition(structural, 0) is not None:
            raise core.VerificationError(
                f"F043 dash-setext repair absorbed structural marker: {marker!r}"
            )

    print("[PASS] F043 non-structural dash-setext destination regression")


def _synthetic_check_with_f043_dash_setext_destination() -> None:
    _prior_synthetic_check()
    _check_f043_dash_setext_destination_regressions()


multiline._try_fold_quoted_definition = _try_fold_quoted_definition
core.check_synthetic_rejections_and_transition_positives = (
    _synthetic_check_with_f043_dash_setext_destination
)


def main() -> int:
    actual = core.git_blob_sha1(Path(prior.__file__))
    if actual != PRIOR_F043_SETEXT_INSIDE_TITLE_BLOB_SHA:
        print(
            "[FAIL] F043 setext-inside-title verifier drift: "
            f"expected={PRIOR_F043_SETEXT_INSIDE_TITLE_BLOB_SHA} actual={actual}",
            file=core.sys.stderr,
        )
        return 1
    return prior.main()


if __name__ == "__main__":
    raise SystemExit(main())
