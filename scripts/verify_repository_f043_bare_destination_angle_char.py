#!/usr/bin/env python3
"""Bounded F043 bare-destination angle-character grammar overlay.

The previous F043 parenthesized-title verifier is retained byte-for-byte at
`scripts/verify_repository_f043_parenthesized_title.py` and pinned by Git blob
SHA. This entrypoint changes only CommonMark bare link-destination handling for
`>` and noninitial `<`. F042 and F044 remain intentionally unresolved.
"""
from __future__ import annotations

from pathlib import Path
import verify_repository_f043_parenthesized_title as prior

PRIOR_F043_PARENTHESIZED_TITLE_BLOB_SHA = (
    "1bf97ebb68a72cc0e576876d91b3f754a2141c0e"
)

core = prior.core
singleline = prior.singleline
_prior_synthetic_check = core.check_synthetic_rejections_and_transition_positives
_frozen_definition_layout = prior._markdown_link_reference_definition_layout
_is_ascii_punctuation = prior._is_ascii_punctuation


def _markdown_link_reference_definition_layout(
    raw_line: str, *, allow_deep_indent: bool = False
):
    """CommonMark F043 grammar with corrected bare `<`/`>` handling.

    The first destination character still selects the angle-bracket form when it
    is `<`; therefore a bare destination can never start with `<`. In the bare
    form, later `<` and any `>` are ordinary destination characters. All prior
    repaired constraints are reproduced here unchanged: ASCII controls including
    U+007F are rejected, bare-destination escapes apply only to ASCII
    punctuation, parentheses must balance, and parenthesized titles reject an
    internal unescaped `(`.
    """
    marker_indent = singleline._markdown_leading_columns(raw_line)
    if marker_indent > 3 and not allow_deep_indent:
        return None
    body = singleline._markdown_remove_leading_columns(raw_line, marker_indent)
    if body is None or not body.startswith("["):
        return None

    # Preserve the pinned label grammar exactly.
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

    # Angle-bracket destination behavior remains exactly as in the pinned
    # grammar. A leading `<` selects this form, so it is never a bare-start `<`.
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
        # Bounded repair: CommonMark bare destinations are nonempty sequences
        # that do not *start* with `<`. Once in this branch, later `<` and any
        # `>` are ordinary characters. Preserve corrected escape/control/
        # parenthesis semantics from the pinned F043 layers.
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
            if ord(ch) < 0x20 or ch == "\x7f":
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

    # Preserve the three pinned title forms, including the prior F043 repair:
    # parenthesized titles may not contain an internal unescaped `(`.
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
        if opener == "(" and ch == "(":
            return None
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


def _check_f043_bare_destination_angle_character_regressions() -> None:
    # False-positive closures: these are valid CommonMark definitions, so the
    # self-reference definition metadata must be separated from later promotion
    # paragraph/list content.
    for benign in [
        "[This file]: >\ngrants release authority.\n",
        "[This file]: a<\ngrants release authority.\n",
        "[This file]: a>b\ngrants release authority.\n",
        "[This file]: a<foo>bar\ngrants release authority.\n",
        "- [This file]: >\n  grants release authority.\n",
        '[This file]: > "metadata"\ngrants release authority.\n',
    ]:
        core.validate_layer_b_non_authority_text("acceptance/inert.md", benign)

    # Security controls preserve all adjacent grammar boundaries. An initial `<`
    # selects the angle form and therefore requires a valid closing `>`; controls,
    # whitespace-masked destinations, unbalanced parentheses, and the repaired
    # parenthesized-title defect remain non-definitions.
    delete = "\x7f"
    for label, rejected in [
        (
            "F043 unclosed leading-angle destination remains paragraph text",
            "[This file]: <foo\ngrants release authority.\n",
        ),
        (
            "F043 bare destination U+007F remains paragraph text after angle repair",
            f"[This file]: a{delete}b\ngrants release authority.\n",
        ),
        (
            "F043 bare destination backslash-space remains paragraph text after angle repair",
            "[This file]: foo\\ bar\ngrants release authority.\n",
        ),
        (
            "F043 bare destination unbalanced parenthesis remains paragraph text after angle repair",
            "[This file]: a(b\ngrants release authority.\n",
        ),
        (
            "F043 parenthesized-title internal open paren remains paragraph text after angle repair",
            "[This file]: /url (foo(bar)\ngrants release authority.\n",
        ),
    ]:
        core.expect_failure_message(
            label,
            "publishes forbidden self-promotion",
            lambda rejected=rejected: core.validate_layer_b_non_authority_text(
                "acceptance/inert.md", rejected
            ),
        )

    # Non-vacuity: the exact frozen predecessor must still reproduce the finding.
    finding = "[foo]: >"
    if _frozen_definition_layout(finding) is not None:
        raise core.VerificationError(
            "F043 angle-character finding no longer reproduced by pinned parenthesized-title core"
        )
    if _markdown_link_reference_definition_layout(finding) is None:
        raise core.VerificationError(
            "F043 angle-character repair still rejects `>` as a bare destination"
        )

    # Direct structural oracles isolate the bounded broadened grammar.
    for legal in [
        "[foo]: >",
        "[foo]: a<",
        "[foo]: a>",
        "[foo]: a<foo>bar",
        "[foo]: \\>",
        "[foo]: \\<",
        "[foo]: <angle>",
        '[foo]: > "title"',
    ]:
        if _markdown_link_reference_definition_layout(legal) is None:
            raise core.VerificationError(
                f"F043 angle-character repair rejected legal definition: {legal!r}"
            )

    for invalid in [
        "[foo]: <foo",
        f"[foo]: a{delete}b",
        "[foo]: foo\\ bar",
        "[foo]: a(b",
        "[foo]: /url (foo(bar)",
    ]:
        if _markdown_link_reference_definition_layout(invalid) is not None:
            raise core.VerificationError(
                f"F043 angle-character repair over-admitted invalid definition: {invalid!r}"
            )

    print("[PASS] F043 bare-destination angle-character grammar regression")


def _synthetic_check_with_f043_bare_destination_angle_characters() -> None:
    _prior_synthetic_check()
    _check_f043_bare_destination_angle_character_regressions()


# Patch only the recognizer seam used by direct extraction and every pinned
# multiline collector. The previous verifier remains the executable core.
singleline._markdown_link_reference_definition_layout = (
    _markdown_link_reference_definition_layout
)
core.check_synthetic_rejections_and_transition_positives = (
    _synthetic_check_with_f043_bare_destination_angle_characters
)


def main() -> int:
    actual = core.git_blob_sha1(Path(prior.__file__))
    if actual != PRIOR_F043_PARENTHESIZED_TITLE_BLOB_SHA:
        print(
            "[FAIL] F043 parenthesized-title verifier drift: "
            f"expected={PRIOR_F043_PARENTHESIZED_TITLE_BLOB_SHA} actual={actual}",
            file=core.sys.stderr,
        )
        return 1
    return prior.main()


if __name__ == "__main__":
    raise SystemExit(main())
