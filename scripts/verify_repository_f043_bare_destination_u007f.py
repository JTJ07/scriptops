#!/usr/bin/env python3
"""Bounded F043 bare-destination ASCII-control overlay.

The previous F043 bare-destination escape verifier is retained byte-for-byte at
`scripts/verify_repository_f043_bare_destination_escape.py` and pinned by Git
blob SHA. This entrypoint changes only accepted bare link destinations that
contain ASCII control U+007F DELETE. F042 and F044 remain intentionally
unresolved.
"""
from __future__ import annotations

from pathlib import Path
import verify_repository_f043_bare_destination_escape as prior

PRIOR_F043_BARE_DESTINATION_ESCAPE_BLOB_SHA = (
    "e20d7b4036c13d9cb74152e57c6242aad90415f0"
)

core = prior.core
singleline = prior.singleline
_prior_synthetic_check = core.check_synthetic_rejections_and_transition_positives
_frozen_definition_layout = prior._markdown_link_reference_definition_layout


def _accepted_bare_destination_contains_delete(
    raw_line: str, *, allow_deep_indent: bool = False
) -> bool:
    """Return True iff an otherwise accepted bare destination contains U+007F."""
    if "\x7f" not in raw_line:
        return False

    marker_indent = singleline._markdown_leading_columns(raw_line)
    if marker_indent > 3 and not allow_deep_indent:
        return False
    body = singleline._markdown_remove_leading_columns(raw_line, marker_indent)
    if body is None or not body.startswith("["):
        return False

    # Find the unescaped label close using the same boundary rules as the
    # already-pinned recognizer. This helper is only a narrowing gate after the
    # pinned recognizer has accepted the full definition.
    i = 1
    escaped = False
    close = None
    while i < len(body):
        ch = body[i]
        if escaped:
            escaped = False
            i += 1
            continue
        if ch == "\\":
            escaped = True
            i += 1
            continue
        if ch == "[":
            return False
        if ch == "]":
            close = i
            break
        i += 1

    if close is None:
        return False
    i = close + 1
    if i >= len(body) or body[i] != ":":
        return False
    i += 1
    while i < len(body) and body[i] in " \t":
        i += 1
    if i >= len(body) or body[i] == "<":
        return False

    # The pinned recognizer already proved that this is a syntactically
    # accepted bare destination. Walk only that destination span, preserving
    # its corrected ASCII-punctuation backslash semantics.
    while i < len(body):
        ch = body[i]
        if ch == "\\":
            if i + 1 < len(body) and prior._is_ascii_punctuation(body[i + 1]):
                i += 2
                continue
            i += 1
            continue
        if ch in " \t\r\n":
            break
        if ch == "\x7f":
            return True
        i += 1
    return False


def _markdown_link_reference_definition_layout(
    raw_line: str, *, allow_deep_indent: bool = False
):
    """Pinned recognizer plus the missing CommonMark U+007F bare-destination gate."""
    layout = _frozen_definition_layout(
        raw_line, allow_deep_indent=allow_deep_indent
    )
    if layout is None:
        return None
    if _accepted_bare_destination_contains_delete(
        raw_line, allow_deep_indent=allow_deep_indent
    ):
        return None
    return layout


def _check_f043_bare_destination_ascii_control_regressions() -> None:
    delete = "\x7f"

    # Security closures: U+007F is an ASCII control and therefore cannot be
    # destination content in the bare form. The text must remain paragraph/list
    # content so self-reference and promotion stay in one security unit.
    for label, rejected in [
        (
            "F043 bare destination U+007F remains paragraph text",
            f"[This file]: foo{delete}bar\ngrants release authority.\n",
        ),
        (
            "F043 list bare destination U+007F remains item text",
            f"- [This file]: foo{delete}bar\n  grants release authority.\n",
        ),
        (
            "F043 bare destination U+007F after literal backslash remains paragraph text",
            f"[This file]: foo\\bar{delete}baz\ngrants release authority.\n",
        ),
    ]:
        core.expect_failure_message(
            label,
            "publishes forbidden self-promotion",
            lambda rejected=rejected: core.validate_layer_b_non_authority_text(
                "acceptance/inert.md", rejected
            ),
        )

    # Positive controls: adjacent legal code points and the previously repaired
    # escape/title families remain accepted.
    for benign in [
        "[This file]: foo~bar\ngrants release authority.\n",
        "[This file]: foo\u0080bar\ngrants release authority.\n",
        "[This file]: foo\\)bar\ngrants release authority.\n",
        '[This file]: foo\\ "title"\ngrants release authority.\n',
    ]:
        core.validate_layer_b_non_authority_text("acceptance/inert.md", benign)

    finding = f"[foo]: foo{delete}bar"
    if _frozen_definition_layout(finding) is None:
        raise core.VerificationError(
            "F043 U+007F finding no longer reproduced by pinned bare-destination core"
        )
    if _markdown_link_reference_definition_layout(finding) is not None:
        raise core.VerificationError(
            "F043 bare-destination ASCII-control repair still accepts U+007F"
        )

    if not _accepted_bare_destination_contains_delete(finding):
        raise core.VerificationError(
            "F043 bare-destination U+007F oracle failed to locate DELETE"
        )

    label_delete = f"[foo{delete}]: bar"
    if _frozen_definition_layout(label_delete) is not None:
        if _markdown_link_reference_definition_layout(label_delete) is None:
            raise core.VerificationError(
                "F043 U+007F repair leaked beyond bare destination into label semantics"
            )

    angle_delete = f"[foo]: <bar{delete}baz>"
    if _frozen_definition_layout(angle_delete) is not None:
        if _markdown_link_reference_definition_layout(angle_delete) is None:
            raise core.VerificationError(
                "F043 U+007F repair leaked beyond bare destination into angle destination"
            )

    print("[PASS] F043 bare-destination ASCII-control U+007F regression")


def _synthetic_check_with_f043_bare_destination_ascii_control() -> None:
    _prior_synthetic_check()
    _check_f043_bare_destination_ascii_control_regressions()


# Patch only the recognizer used by direct extraction and all pinned multiline
# collectors. The previous verifier remains the executable core.
singleline._markdown_link_reference_definition_layout = (
    _markdown_link_reference_definition_layout
)
core.check_synthetic_rejections_and_transition_positives = (
    _synthetic_check_with_f043_bare_destination_ascii_control
)


def main() -> int:
    actual = core.git_blob_sha1(Path(prior.__file__))
    if actual != PRIOR_F043_BARE_DESTINATION_ESCAPE_BLOB_SHA:
        print(
            "[FAIL] F043 bare-destination escape verifier drift: "
            f"expected={PRIOR_F043_BARE_DESTINATION_ESCAPE_BLOB_SHA} actual={actual}",
            file=core.sys.stderr,
        )
        return 1
    return prior.main()


if __name__ == "__main__":
    raise SystemExit(main())
