#!/usr/bin/env python3
"""Bounded F043 list-multiline source-indentation overlay.

The previous F043 plain setext-title verifier is retained byte-for-byte at
`scripts/verify_repository_f043_plain_setext_title.py` and pinned by Git blob
SHA. This entrypoint changes only list-marker multiline definition collection:
indentation remaining after removal of the owning item content indent is
preserved for block-precedence classification, while normalized payload remains
the input to the already-reviewed definition grammar.

F042 and F044 remain intentionally unresolved.
"""
from __future__ import annotations

from pathlib import Path
import verify_repository_f043_plain_setext_title as prior

PRIOR_F043_PLAIN_SETEXT_TITLE_BLOB_SHA = (
    "7ccdfe7500ffb342396b0883918a9b4cf403d554"
)

core = prior.core
multiline = prior.multiline
singleline = multiline.prior
_prior_synthetic_check = core.check_synthetic_rejections_and_transition_positives
_frozen_list_marker_definition = multiline._try_fold_list_marker_definition


def _try_fold_list_marker_definition(
    lines: list[str], start: int
) -> tuple[int, str] | None:
    """Fold list definitions without erasing source-relative indentation."""
    first = multiline._LIST_LINE_RE.match(lines[start])
    layout = singleline._markdown_list_item_layout(
        lines[start], allow_deep_indent=True
    )
    if first is None or layout is None:
        return None

    first_body = first.group("body").lstrip(" \t")
    if not first_body.startswith("["):
        return None

    _, content_indent, empty_item, _ = layout
    if empty_item:
        return None

    parts = [first_body]
    best = multiline._longest_valid_definition(parts)

    for index in range(start + 1, len(lines)):
        raw_line = lines[index]
        if not raw_line.strip():
            break

        relative_raw = singleline._markdown_remove_leading_columns(
            raw_line, content_indent
        )
        if relative_raw is None:
            # Legal list-item lazy continuation may omit the content indent.
            # In that branch, preserve the physical line for block precedence.
            structural_body = raw_line
            body = raw_line.lstrip(" \t")
        else:
            # Preserve indentation remaining *inside* the owning list item for
            # structural tests. Only the grammar payload is normalized.
            structural_body = relative_raw
            body = relative_raw.lstrip(" \t")

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


def _check_f043_list_indentation_regression() -> None:
    source = "- [This file]:\n      #\n  grants release authority.\n"
    finding_lines = source.splitlines()

    if _frozen_list_marker_definition(finding_lines, 0) is not None:
        raise core.VerificationError(
            "F043 list-indentation finding no longer reproduced by pinned predecessor"
        )

    repaired = _try_fold_list_marker_definition(finding_lines, 0)
    if repaired != (2, "- [This file]: #"):
        raise core.VerificationError(
            "F043 list-indentation repair did not isolate the valid definition prefix: "
            f"actual={repaired!r}"
        )

    core.validate_layer_b_non_authority_text("acceptance/inert.md", source)

    # A real ATX heading at item content indentation remains an interrupter.
    structural = (
        "- [This file]:\n  # heading\n  grants release authority.\n".splitlines()
    )
    if _try_fold_list_marker_definition(structural, 0) is not None:
        raise core.VerificationError(
            "F043 list-indentation repair crossed a real list-owned ATX interrupter"
        )

    print("[PASS] F043 list multiline source-indentation regression")


def _synthetic_check_with_f043_list_indentation() -> None:
    _prior_synthetic_check()
    _check_f043_list_indentation_regression()


multiline._try_fold_list_marker_definition = _try_fold_list_marker_definition
core.check_synthetic_rejections_and_transition_positives = (
    _synthetic_check_with_f043_list_indentation
)


def main() -> int:
    actual = core.git_blob_sha1(Path(prior.__file__))
    if actual != PRIOR_F043_PLAIN_SETEXT_TITLE_BLOB_SHA:
        print(
            "[FAIL] F043 plain setext-title verifier drift: "
            f"expected={PRIOR_F043_PLAIN_SETEXT_TITLE_BLOB_SHA} actual={actual}",
            file=core.sys.stderr,
        )
        return 1
    return prior.main()


if __name__ == "__main__":
    raise SystemExit(main())
