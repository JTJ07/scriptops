#!/usr/bin/env python3
"""Bounded F043 bare-destination backslash-escape grammar overlay.

The previous F043 destination-newline verifier is retained byte-for-byte at
`scripts/verify_repository_f043_destination_newline.py` and pinned by Git blob
SHA. This entrypoint changes only the single-line link-reference-definition
recognizer's bare-destination backslash semantics: a backslash escapes ASCII
punctuation only. F042 and F044 remain intentionally unresolved.
"""
from __future__ import annotations

from pathlib import Path
import verify_repository_f043_destination_newline as prior

PRIOR_F043_DESTINATION_NEWLINE_BLOB_SHA = "277eb91bbcf46dfb766e39ed23962b5179450c87"

core = prior.core
singleline = prior.singleline
_prior_synthetic_check = core.check_synthetic_rejections_and_transition_positives
_frozen_definition_layout = singleline._markdown_link_reference_definition_layout


def _is_ascii_punctuation(ch: str) -> bool:
    return len(ch) == 1 and (
        "!" <= ch <= "/"
        or ":" <= ch <= "@"
        or "[" <= ch <= "`"
        or "{" <= ch <= "~"
    )


def _markdown_link_reference_definition_layout(
    raw_line: str, *, allow_deep_indent: bool = False
):
    """Frozen F043 single-line grammar with corrected bare-destination escapes."""
    marker_indent = singleline._markdown_leading_columns(raw_line)
    if marker_indent > 3 and not allow_deep_indent:
        return None
    body = singleline._markdown_remove_leading_columns(raw_line, marker_indent)
    if body is None or not body.startswith("["):
        return None

    # Label behavior remains exactly as in the pinned single-line F043 layer.
    i = 1
    label = []
    escaped = False
    close = None
    while i < len(body):
        ch = body[i]
        if escaped:
            label.append(ch)
            escaped = False
            i += 1
            continue
        if ch == "\\":
            escaped = True
            label.append(ch)
            i += 1
            continue
        if ch == "[":
            return None
        if ch == "]":
            close = i
            break
        label.append(ch)
        i += 1
    if (
        close is None
        or not (1 <= len(label) <= 999)
        or not any(not c.isspace() for c in label)
    ):
        return None

    i = close + 1
    if i >= len(body) or body[i] != ":":
        return None
    i += 1
    while i < len(body) and body[i] in " \t":
        i += 1
    if i >= len(body):
        return None

    # Angle-bracket destination behavior remains frozen. Physical-newline
    # protection is supplied by the already-pinned destination-newline layer.
    if body[i] == "<":
        i += 1
        escaped = False
        closed = False
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
            if ch == "<":
                return None
            if ch == ">":
                i += 1
                closed = True
                break
            if ch in "\r\n":
                return None
            i += 1
        if not closed:
            return None
    else:
        # Bounded repair: CommonMark backslash escapes apply to ASCII
        # punctuation. Before a non-punctuation character, the backslash is
        # literal and the following character must still be processed normally.
        start = i
        depth = 0
        while i < len(body):
            ch = body[i]
            if ch == "\\":
                if i + 1 < len(body) and _is_ascii_punctuation(body[i + 1]):
                    i += 2
                    continue
                i += 1
                continue
            if ch in " \t\r\n":
                break
            if ord(ch) < 0x20 or ch in "<>":
                return None
            if ch == "(":
                depth += 1
            elif ch == ")":
                if depth == 0:
                    return None
                depth -= 1
            i += 1
        if i == start or depth:
            return None

    ws_start = i
    while i < len(body) and body[i] in " \t":
        i += 1
    if i == len(body):
        return marker_indent
    if i == ws_start:
        return None

    # Title behavior remains exactly as in the pinned single-line layer.
    opener = body[i]
    closer = {'"': '"', "'": "'", "(": ")"}.get(opener)
    if closer is None:
        return None
    i += 1
    escaped = False
    closed = False
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
        if ch == closer:
            i += 1
            closed = True
            break
        if ch in "\r\n":
            return None
        i += 1
    if not closed:
        return None
    while i < len(body) and body[i] in " \t":
        i += 1
    return marker_indent if i == len(body) else None


def _check_f043_bare_destination_escape_regressions() -> None:
    # Security closures: backslash cannot mask a space or tab in a bare
    # destination. These remain ordinary paragraph/list content and must reject.
    for label, rejected in [
        (
            "F043 bare destination backslash-space remains paragraph text",
            "[This file]: foo\\ bar\ngrants release authority.\n",
        ),
        (
            "F043 bare destination backslash-tab remains paragraph text",
            "[This file]: foo\\\tbar\ngrants release authority.\n",
        ),
        (
            "F043 list bare destination backslash-space remains item text",
            "- [This file]: foo\\ bar\n  grants release authority.\n",
        ),
    ]:
        core.expect_failure_message(
            label,
            "publishes forbidden self-promotion",
            lambda rejected=rejected: core.validate_layer_b_non_authority_text(
                "acceptance/inert.md", rejected
            ),
        )

    # Positive controls: escaped ASCII punctuation stays legal; a backslash
    # before non-punctuation remains literal; and a following space can still
    # separate a valid title rather than being incorrectly absorbed.
    for benign in [
        "[This file]: foo\\)bar\ngrants release authority.\n",
        "[This file]: foo\\bar\ngrants release authority.\n",
        "[This file]: foo\\ \"title\"\ngrants release authority.\n",
        "- [This file]: foo\\)bar\n  grants release authority.\n",
    ]:
        core.validate_layer_b_non_authority_text("acceptance/inert.md", benign)

    finding = "[foo]: foo\\ bar"
    if _frozen_definition_layout(finding) is None:
        raise core.VerificationError(
            "F043 backslash-space finding no longer reproduced by pinned single-line core"
        )
    if _markdown_link_reference_definition_layout(finding) is not None:
        raise core.VerificationError(
            "F043 bare-destination escape repair still accepts backslash-space"
        )

    escaped_punctuation = "[foo]: foo\\)bar"
    if _markdown_link_reference_definition_layout(escaped_punctuation) is None:
        raise core.VerificationError(
            "F043 bare-destination escape repair broke escaped ASCII punctuation"
        )

    literal_nonpunct = "[foo]: foo\\bar"
    if _markdown_link_reference_definition_layout(literal_nonpunct) is None:
        raise core.VerificationError(
            "F043 bare-destination escape repair broke literal backslash before non-punctuation"
        )

    title_separator = '[foo]: foo\\ "title"'
    if _markdown_link_reference_definition_layout(title_separator) is None:
        raise core.VerificationError(
            "F043 bare-destination escape repair broke title separation after literal backslash"
        )

    print("[PASS] F043 bare-destination backslash-escape grammar regression")


def _synthetic_check_with_f043_bare_destination_escape() -> None:
    _prior_synthetic_check()
    _check_f043_bare_destination_escape_regressions()


# Patch only the single-line definition recognizer. Existing direct extraction
# and all pinned multiline collectors resolve this module global dynamically.
singleline._markdown_link_reference_definition_layout = (
    _markdown_link_reference_definition_layout
)
core.check_synthetic_rejections_and_transition_positives = (
    _synthetic_check_with_f043_bare_destination_escape
)


def main() -> int:
    actual = core.git_blob_sha1(Path(prior.__file__))
    if actual != PRIOR_F043_DESTINATION_NEWLINE_BLOB_SHA:
        print(
            "[FAIL] F043 destination-newline verifier drift: "
            f"expected={PRIOR_F043_DESTINATION_NEWLINE_BLOB_SHA} actual={actual}",
            file=core.sys.stderr,
        )
        return 1
    return prior.main()


if __name__ == "__main__":
    raise SystemExit(main())
