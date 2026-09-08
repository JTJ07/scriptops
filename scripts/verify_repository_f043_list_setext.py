#!/usr/bin/env python3
"""Bounded F043 list setext-inside-incomplete-definition overlay.

The previous F043 list-indentation verifier is retained byte-for-byte at
`scripts/verify_repository_f043_list_indentation.py` and pinned by Git blob SHA.
This entrypoint changes only one precedence edge in list multiline reference-
definition collection: already-bounded non-structural setext-looking content may
remain while no complete definition prefix exists yet.

F042 and F044 remain intentionally unresolved.
"""
from __future__ import annotations

from pathlib import Path
import verify_repository_f043_list_indentation as prior

PRIOR_F043_LIST_INDENTATION_BLOB_SHA = (
    "dc3ffcdf59fb23dffa20cffbdafe18bdef7ce659"
)

core = prior.core
multiline = prior.multiline
singleline = prior.singleline
_prior_synthetic_check = core.check_synthetic_rejections_and_transition_positives
_frozen_list_marker_definition = prior._try_fold_list_marker_definition
_setext_candidate_exception = prior.prior._setext_candidate_exception


def _try_fold_list_marker_definition(
    lines: list[str], start: int
) -> tuple[int, str] | None:
    """Allow bounded setext-looking text only inside an incomplete list definition."""
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
            structural_body = raw_line
            body = raw_line.lstrip(" \t")
        else:
            structural_body = relative_raw
            body = relative_raw.lstrip(" \t")

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


def _check_f043_list_setext_regressions() -> None:
    benign = "- [This file]:\n  ===\n  grants release authority.\n"
    benign_lines = benign.splitlines()

    if _frozen_list_marker_definition(benign_lines, 0) is not None:
        raise core.VerificationError(
            "F043 list-setext finding no longer reproduced by pinned predecessor"
        )

    repaired = _try_fold_list_marker_definition(benign_lines, 0)
    if repaired != (2, "- [This file]: ==="):
        raise core.VerificationError(
            "F043 list-setext repair did not isolate the valid definition prefix: "
            f"actual={repaired!r}"
        )
    core.validate_layer_b_non_authority_text("acceptance/inert.md", benign)

    # Security control: setext-looking content may occur inside an incomplete
    # multiline title, but the complete definition metadata remains one
    # security-visible authority unit.
    security = '- [This file]: /url "\n  ===\n  grants release authority\n  "\n'
    security_fold = _try_fold_list_marker_definition(security.splitlines(), 0)
    if security_fold != (
        4,
        '- [This file]: /url " === grants release authority "',
    ):
        raise core.VerificationError(
            "F043 list-setext repair failed multiline-title security fold: "
            f"actual={security_fold!r}"
        )
    core.expect_failure_message(
        "F043 list setext-title metadata remains security-relevant",
        "publishes forbidden self-promotion",
        lambda: core.validate_layer_b_non_authority_text(
            "acceptance/inert.md", security
        ),
    )

    # A definition already complete on its first line ends before later setext
    # looking list-item text.
    complete_then_equals = (
        "- [This file]: /url\n  ===\n  grants release authority.\n".splitlines()
    )
    if _try_fold_list_marker_definition(complete_then_equals, 0) is not None:
        raise core.VerificationError(
            "F043 list-setext repair absorbed `===` after a complete definition"
        )

    print("[PASS] F043 list setext inside incomplete definition regression")


def _synthetic_check_with_f043_list_setext() -> None:
    _prior_synthetic_check()
    _check_f043_list_setext_regressions()


multiline._try_fold_list_marker_definition = _try_fold_list_marker_definition
core.check_synthetic_rejections_and_transition_positives = (
    _synthetic_check_with_f043_list_setext
)


def main() -> int:
    actual = core.git_blob_sha1(Path(prior.__file__))
    if actual != PRIOR_F043_LIST_INDENTATION_BLOB_SHA:
        print(
            "[FAIL] F043 list-indentation verifier drift: "
            f"expected={PRIOR_F043_LIST_INDENTATION_BLOB_SHA} actual={actual}",
            file=core.sys.stderr,
        )
        return 1
    return prior.main()


if __name__ == "__main__":
    raise SystemExit(main())
