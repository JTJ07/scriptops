#!/usr/bin/env python3
"""Bounded F043 parenthesized link-title grammar overlay.

The previous F043 bare-destination U+007F verifier is retained byte-for-byte at
`scripts/verify_repository_f043_bare_destination_u007f.py` and pinned by Git
blob SHA. This entrypoint changes only accepted parenthesized link titles that
contain an unescaped internal `(`. F042 and F044 remain intentionally
unresolved.
"""
from __future__ import annotations

from pathlib import Path
import verify_repository_f043_bare_destination_u007f as prior

PRIOR_F043_BARE_DESTINATION_U007F_BLOB_SHA = (
    "8dc5d3e207f3b1e82fc6384609ccc67c9c41495a"
)

core = prior.core
singleline = prior.singleline
_prior_synthetic_check = core.check_synthetic_rejections_and_transition_positives
_frozen_definition_layout = prior._markdown_link_reference_definition_layout
_is_ascii_punctuation = prior.prior._is_ascii_punctuation


def _accepted_parenthesized_title_has_unescaped_open_paren(
    raw_line: str, *, allow_deep_indent: bool = False
) -> bool:
    """Return True iff an otherwise accepted `(title)` contains unescaped `(`."""
    if "(" not in raw_line:
        return False

    marker_indent = singleline._markdown_leading_columns(raw_line)
    if marker_indent > 3 and not allow_deep_indent:
        return False
    body = singleline._markdown_remove_leading_columns(raw_line, marker_indent)
    if body is None or not body.startswith("["):
        return False

    # Locate the unescaped label close using the already-pinned label rules.
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
    if i >= len(body):
        return False

    # Walk exactly the destination span using the semantics already established
    # by the pinned F043 layers. This helper only narrows a definition after the
    # frozen recognizer has accepted it.
    if body[i] == "<":
        i += 1
        escaped = False
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
            if ch == ">":
                i += 1
                break
            i += 1
    else:
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
            i += 1

    ws_start = i
    while i < len(body) and body[i] in " \t":
        i += 1
    if i == len(body) or i == ws_start or body[i] != "(":
        return False

    # In the parenthesized title form, an internal `(` is only legal when
    # backslash-escaped. The first unescaped `)` is the title closer, exactly as
    # in the pinned recognizer. Preserve its existing backslash treatment so
    # this repair does not expand into another F043 grammar family.
    i += 1
    escaped = False
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
        if ch == ")":
            return False
        if ch == "(":
            return True
        i += 1
    return False


def _markdown_link_reference_definition_layout(
    raw_line: str, *, allow_deep_indent: bool = False
):
    """Pinned recognizer plus parenthesized-title internal-open-paren gate."""
    layout = _frozen_definition_layout(
        raw_line, allow_deep_indent=allow_deep_indent
    )
    if layout is None:
        return None
    if _accepted_parenthesized_title_has_unescaped_open_paren(
        raw_line, allow_deep_indent=allow_deep_indent
    ):
        return None
    return layout


def _check_f043_parenthesized_title_regressions() -> None:
    # Security closures: invalid parenthesized titles must remain ordinary
    # paragraph/list content so self-reference and promotion stay together.
    for label, rejected in [
        (
            "F043 parenthesized title internal open paren remains paragraph text",
            "[This file]: /url (foo(bar)\ngrants release authority.\n",
        ),
        (
            "F043 list parenthesized title internal open paren remains item text",
            "- [This file]: /url (foo(bar)\n  grants release authority.\n",
        ),
        (
            "F043 multiline parenthesized title internal open paren remains paragraph text",
            "[This file]: /url (\nfoo(bar\n)\ngrants release authority.\n",
        ),
    ]:
        core.expect_failure_message(
            label,
            "publishes forbidden self-promotion",
            lambda rejected=rejected: core.validate_layer_b_non_authority_text(
                "acceptance/inert.md", rejected
            ),
        )

    # Positive controls: escaped parentheses stay legal, while quoted-title
    # forms may contain literal parentheses and must remain unaffected.
    for benign in [
        "[This file]: /url (foo\\(bar)\ngrants release authority.\n",
        "[This file]: /url (foo\\)bar)\ngrants release authority.\n",
        '[This file]: /url "foo(bar)"\ngrants release authority.\n',
        "[This file]: /url 'foo(bar)'\ngrants release authority.\n",
        "[This file]: /url (\nfoo\\(bar\n)\ngrants release authority.\n",
    ]:
        core.validate_layer_b_non_authority_text("acceptance/inert.md", benign)

    finding = "[foo]: /url (foo(bar)"
    if _frozen_definition_layout(finding) is None:
        raise core.VerificationError(
            "F043 parenthesized-title finding no longer reproduced by pinned core"
        )
    if _markdown_link_reference_definition_layout(finding) is not None:
        raise core.VerificationError(
            "F043 parenthesized-title repair still accepts internal unescaped `(`"
        )
    if not _accepted_parenthesized_title_has_unescaped_open_paren(finding):
        raise core.VerificationError(
            "F043 parenthesized-title oracle failed to locate internal unescaped `(`"
        )

    escaped_open = "[foo]: /url (foo\\(bar)"
    if _markdown_link_reference_definition_layout(escaped_open) is None:
        raise core.VerificationError(
            "F043 parenthesized-title repair broke escaped internal `(`"
        )

    escaped_close = "[foo]: /url (foo\\)bar)"
    if _markdown_link_reference_definition_layout(escaped_close) is None:
        raise core.VerificationError(
            "F043 parenthesized-title repair broke escaped internal `)`"
        )

    quoted = '[foo]: /url "foo(bar)"'
    if _markdown_link_reference_definition_layout(quoted) is None:
        raise core.VerificationError(
            "F043 parenthesized-title repair leaked into quoted-title semantics"
        )

    print("[PASS] F043 parenthesized link-title grammar regression")


def _synthetic_check_with_f043_parenthesized_title() -> None:
    _prior_synthetic_check()
    _check_f043_parenthesized_title_regressions()


# Patch only the same recognizer seam used by direct extraction and all pinned
# multiline collectors. The previous verifier remains the executable core.
singleline._markdown_link_reference_definition_layout = (
    _markdown_link_reference_definition_layout
)
core.check_synthetic_rejections_and_transition_positives = (
    _synthetic_check_with_f043_parenthesized_title
)


def main() -> int:
    actual = core.git_blob_sha1(Path(prior.__file__))
    if actual != PRIOR_F043_BARE_DESTINATION_U007F_BLOB_SHA:
        print(
            "[FAIL] F043 bare-destination U+007F verifier drift: "
            f"expected={PRIOR_F043_BARE_DESTINATION_U007F_BLOB_SHA} actual={actual}",
            file=core.sys.stderr,
        )
        return 1
    return prior.main()


if __name__ == "__main__":
    raise SystemExit(main())
