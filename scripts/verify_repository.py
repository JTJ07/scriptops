#!/usr/bin/env python3
"""Bounded fresh-final inline-link policy-semantic normalization overlay.

The repaired fresh-final inline-HTML policy verifier is retained byte-for-byte at
`scripts/verify_repository_fresh_final_inline_html_policy.py` and pinned by Git
blob SHA.

This overlay does not change Markdown block parsing, boundaries, ownership,
quote/list structure, lifecycle, whitespace policy, Unicode normalization,
inline-HTML handling, or character-reference handling. Raw Markdown is parsed
exactly as before. Only after the existing parser emits an authority unit do we
canonicalize a bounded class of direct inline Markdown links to their visible
label text for policy matching. The result then flows through the predecessor's
inline-HTML canonicalization, character-reference decoding, and existing
self-reference/promotion/negation grammar.

This is not regex destination stripping, not a generic Markdown renderer, and
not raw-Markdown pre-processing. Images, reference links, autolinks, code-span
interactions, and malformed link syntax remain outside this bounded class.
"""
from __future__ import annotations

from pathlib import Path
import string
import verify_repository_fresh_final_inline_html_policy as prior

PRIOR_INLINE_HTML_POLICY_BLOB_SHA = "71404ab4921e2abc4887487636f83717bec7ffce"

core = prior.core
singleline = prior.singleline
_prior_authority_soft_wrapped_units = core._authority_soft_wrapped_units
_prior_layer_b_self_promotion_claim = core.layer_b_self_promotion_claim
_prior_synthetic_check = core.check_synthetic_rejections_and_transition_positives

_COMMONMARK_ESCAPABLE = frozenset(string.punctuation)
_MAX_INLINE_LINK_NESTING = 32


def _escaped_punctuation_at(text: str, index: int) -> bool:
    return (
        index + 1 < len(text)
        and text[index] == "\\"
        and text[index + 1] in _COMMONMARK_ESCAPABLE
    )


def _is_unescaped_bang_before(text: str, index: int) -> bool:
    if index == 0 or text[index - 1] != "!":
        return False
    backslashes = 0
    cursor = index - 2
    while cursor >= 0 and text[cursor] == "\\":
        backslashes += 1
        cursor -= 1
    return backslashes % 2 == 0


def _parse_link_label(text: str, start: int) -> tuple[str, int] | None:
    """Parse one balanced direct-link label beginning at `[`.

    Nested brackets and CommonMark punctuation escapes are tracked structurally.
    The returned label remains raw so later, already-established policy stages
    keep responsibility for inline HTML and character references.
    """
    if start >= len(text) or text[start] != "[":
        return None

    depth = 1
    cursor = start + 1
    while cursor < len(text):
        if _escaped_punctuation_at(text, cursor):
            cursor += 2
            continue

        char = text[cursor]
        if char in "\r\n":
            return None
        if char == "[":
            depth += 1
            if depth > _MAX_INLINE_LINK_NESTING:
                return None
        elif char == "]":
            depth -= 1
            if depth == 0:
                return text[start + 1 : cursor], cursor + 1
        cursor += 1
    return None


def _skip_link_space(text: str, cursor: int) -> int:
    while cursor < len(text) and text[cursor] in " \t":
        cursor += 1
    return cursor


def _parse_angle_destination(text: str, cursor: int) -> int | None:
    if cursor >= len(text) or text[cursor] != "<":
        return None
    cursor += 1
    while cursor < len(text):
        if _escaped_punctuation_at(text, cursor):
            cursor += 2
            continue
        char = text[cursor]
        if char in "\r\n" or ord(char) < 0x20 or char == "<":
            return None
        if char == ">":
            return cursor + 1
        cursor += 1
    return None


def _parse_bare_destination(text: str, cursor: int) -> tuple[int, bool] | None:
    """Parse a bounded CommonMark-style bare destination.

    Returns `(cursor, closed_outer)` where `closed_outer=True` means the outer
    link `)` was consumed directly after the destination. Balanced destination
    parentheses are tracked separately from the link's outer parentheses.
    """
    depth = 0
    saw = False
    while cursor < len(text):
        if _escaped_punctuation_at(text, cursor):
            saw = True
            cursor += 2
            continue

        char = text[cursor]
        if char in " \t\r\n" or ord(char) < 0x20:
            return (cursor, False) if saw else None
        if char in "<>[]":
            return None
        if char == "(":
            depth += 1
            if depth > _MAX_INLINE_LINK_NESTING:
                return None
            saw = True
            cursor += 1
            continue
        if char == ")":
            if depth:
                depth -= 1
                saw = True
                cursor += 1
                continue
            return (cursor + 1, True) if saw else None

        saw = True
        cursor += 1

    return None


def _parse_link_title(text: str, cursor: int) -> int | None:
    if cursor >= len(text) or text[cursor] not in "\"'(":
        return None

    opener = text[cursor]
    closer = ")" if opener == "(" else opener
    cursor += 1
    while cursor < len(text):
        if _escaped_punctuation_at(text, cursor):
            cursor += 2
            continue
        char = text[cursor]
        if char in "\r\n":
            return None
        if char == closer:
            return cursor + 1
        # Parenthesized titles are deliberately conservative: nested raw
        # parentheses are not accepted in this bounded parser.
        if opener == "(" and char == "(":
            return None
        cursor += 1
    return None


def _parse_inline_link_suffix(text: str, open_paren: int) -> int | None:
    """Return the index after a validated direct inline-link suffix `(…)`."""
    if open_paren >= len(text) or text[open_paren] != "(":
        return None

    cursor = _skip_link_space(text, open_paren + 1)
    if cursor >= len(text):
        return None

    # Empty destination.
    if text[cursor] == ")":
        return cursor + 1

    if text[cursor] == "<":
        parsed = _parse_angle_destination(text, cursor)
        if parsed is None:
            return None
        cursor = parsed
    else:
        parsed_bare = _parse_bare_destination(text, cursor)
        if parsed_bare is None:
            return None
        cursor, closed_outer = parsed_bare
        if closed_outer:
            return cursor

    before_space = cursor
    cursor = _skip_link_space(text, cursor)
    if cursor >= len(text):
        return None
    if text[cursor] == ")":
        return cursor + 1

    # A title requires separating whitespace from the destination.
    if cursor == before_space:
        return None
    title_end = _parse_link_title(text, cursor)
    if title_end is None:
        return None
    cursor = _skip_link_space(text, title_end)
    if cursor < len(text) and text[cursor] == ")":
        return cursor + 1
    return None


def _canonicalize_direct_inline_links(text: str) -> str:
    """Replace validated direct inline links with their visible label source.

    The parser is intentionally narrow and fail-closed. It does not implement
    images, reference links, autolinks, or code-span interactions. If a code span
    marker is present anywhere in the authority unit, this stage leaves the unit
    unchanged rather than pretending to be a general Markdown inline parser.
    """
    if "[" not in text or "](" not in text:
        return text
    if "`" in text:
        return text

    output: list[str] = []
    cursor = 0
    changed = False
    while cursor < len(text):
        if _escaped_punctuation_at(text, cursor):
            output.append(text[cursor : cursor + 2])
            cursor += 2
            continue

        if text[cursor] != "[" or _is_unescaped_bang_before(text, cursor):
            output.append(text[cursor])
            cursor += 1
            continue

        label_result = _parse_link_label(text, cursor)
        if label_result is None:
            output.append(text[cursor])
            cursor += 1
            continue

        label, after_label = label_result
        if after_label >= len(text) or text[after_label] != "(":
            output.append(text[cursor])
            cursor += 1
            continue

        suffix_end = _parse_inline_link_suffix(text, after_label)
        if suffix_end is None:
            output.append(text[cursor])
            cursor += 1
            continue

        output.append(label)
        cursor = suffix_end
        changed = True

    return "".join(output) if changed else text


def _policy_claim_from_extracted_unit(raw_unit: str) -> bool:
    link_visible_unit = _canonicalize_direct_inline_links(raw_unit)
    return prior._policy_claim_from_extracted_unit(link_visible_unit)


def _layer_b_self_promotion_claim(text: str) -> str | None:
    """Parse raw Markdown first; canonicalize links only in extracted units."""
    for raw_unit in _prior_authority_soft_wrapped_units(text):
        if _policy_claim_from_extracted_unit(raw_unit):
            return raw_unit.strip()
    return None


def _rejected(source: str) -> tuple[bool, str]:
    try:
        core.validate_layer_b_non_authority_text("acceptance/inert.md", source)
    except core.VerificationError as exc:
        return True, str(exc)
    return False, "ACCEPTED"


def _check_fresh_final_inline_link_policy_regression() -> None:
    literal = "This file grants release authority.\n"
    finding = "[This](https://example.invalid) file grants release authority.\n"

    # The predecessor must reproduce the finding on this exact freeze.
    if _prior_layer_b_self_promotion_claim(literal) is None:
        raise core.VerificationError(
            "inline-link predecessor lost literal self-promotion control"
        )
    if _prior_layer_b_self_promotion_claim(finding) is not None:
        raise core.VerificationError(
            "inline-link predecessor no longer reproduces direct-link bypass"
        )

    literal_units = _prior_authority_soft_wrapped_units(literal)
    finding_units = _prior_authority_soft_wrapped_units(finding)
    if len(literal_units) != 1 or len(finding_units) != 1:
        raise core.VerificationError(
            "inline-link finding must remain one raw authority unit"
        )

    # Structural invariance: this repair never replaces the block/unit parser.
    if core._authority_soft_wrapped_units is not _prior_authority_soft_wrapped_units:
        raise core.VerificationError(
            "inline-link repair modified authority-unit parser binding"
        )
    if core._authority_soft_wrapped_units(literal) != literal_units:
        raise core.VerificationError(
            "inline-link repair changed literal unit structure"
        )
    if core._authority_soft_wrapped_units(finding) != finding_units:
        raise core.VerificationError(
            "inline-link repair changed link unit structure"
        )

    if _canonicalize_direct_inline_links(finding_units[0]) != literal_units[0]:
        raise core.VerificationError(
            "exact inline-link finding does not canonicalize to visible label text"
        )

    literal_claim = _layer_b_self_promotion_claim(literal)
    finding_claim = _layer_b_self_promotion_claim(finding)
    if literal_claim is None or finding_claim is None:
        raise core.VerificationError(
            "inline-link visible-text equivalents must preserve claim detection"
        )

    literal_rejected, _ = _rejected(literal)
    finding_rejected, _ = _rejected(finding)
    if not literal_rejected or not finding_rejected:
        raise core.VerificationError(
            "inline-link visible-text equivalents must both be rejected"
        )

    # Small mechanism proof across destination grammar shapes. This proves link
    # semantics rather than one URL spelling and is intentionally not a sweep of
    # reference links, autolinks, images, or general inline Markdown.
    alternates = [
        "[This](/local/path) file grants release authority.\n",
        "[This](<https://example.invalid/a b>) file grants release authority.\n",
        "[This](https://example.invalid/a_(b) \"neutral title\") file grants release authority.\n",
        "[This]() file grants release authority.\n",
    ]
    for alternate in alternates:
        units = _prior_authority_soft_wrapped_units(alternate)
        if len(units) != 1:
            raise core.VerificationError(
                "inline-link alternate changed raw interpretive-unit membership"
            )
        if _canonicalize_direct_inline_links(units[0]) != literal_units[0]:
            raise core.VerificationError(
                f"inline-link alternate is not visible-text equivalent: {alternate!r}"
            )
        if _layer_b_self_promotion_claim(alternate) is None:
            raise core.VerificationError(
                f"inline-link alternate bypasses self-promotion matcher: {alternate!r}"
            )
        rejected, _ = _rejected(alternate)
        if not rejected:
            raise core.VerificationError(
                f"inline-link alternate is not rejected: {alternate!r}"
            )

    # Existing semantic stages remain in their established order after the new
    # link-visible-text stage.
    composed_html = "[This <span>file</span>](https://example.invalid) grants release authority.\n"
    html_units = _prior_authority_soft_wrapped_units(composed_html)
    if len(html_units) != 1:
        raise core.VerificationError(
            "inline-link + HTML composition changed unit membership"
        )
    link_visible_html = _canonicalize_direct_inline_links(html_units[0])
    if link_visible_html != "This <span>file</span> grants release authority.":
        raise core.VerificationError(
            "inline-link stage consumed or reordered inline-HTML semantics"
        )
    if prior._canonicalize_transparent_inline_html(link_visible_html) != literal_units[0]:
        raise core.VerificationError(
            "inline-HTML canonicalization no longer follows inline-link stage"
        )
    if _layer_b_self_promotion_claim(composed_html) is None:
        raise core.VerificationError(
            "inline-link + inline-HTML equivalent bypasses policy matcher"
        )

    composed_ref = "[This&#32;file](https://example.invalid) grants release authority.\n"
    ref_units = _prior_authority_soft_wrapped_units(composed_ref)
    if len(ref_units) != 1:
        raise core.VerificationError(
            "inline-link + character-reference composition changed unit membership"
        )
    link_visible_ref = _canonicalize_direct_inline_links(ref_units[0])
    if link_visible_ref != "This&#32;file grants release authority.":
        raise core.VerificationError(
            "inline-link stage consumed or reordered character-reference semantics"
        )
    if _layer_b_self_promotion_claim(composed_ref) is None:
        raise core.VerificationError(
            "inline-link + character-reference equivalent bypasses policy matcher"
        )

    # Existing local-negation semantics remain unchanged.
    negated = "[This](https://example.invalid) file does not grant authority.\n"
    if _layer_b_self_promotion_claim(negated) is not None:
        raise core.VerificationError(
            "inline-link canonicalization changed local-negation semantics"
        )

    # Out-of-scope or malformed constructs remain raw rather than being
    # superficially stripped as if they were valid direct links.
    untouched = [
        "![This](https://example.invalid) file grants release authority.\n",
        "[This][policy-ref] file grants release authority.\n",
        "<https://example.invalid> This file grants release authority.\n",
        "[This](https://example.invalid file grants release authority.\n",
        "[This](https://example.invalid \"unterminated) file grants release authority.\n",
        "[This](https://example.invalid/(broken) file grants release authority.\n",
        "\\[This](https://example.invalid) file grants release authority.\n",
        "`[This](https://example.invalid)` file grants release authority.\n",
    ]
    for source in untouched:
        if _canonicalize_direct_inline_links(source) != source:
            raise core.VerificationError(
                f"inline-link policy repair over-canonicalized guarded syntax: {source!r}"
            )
        if core._authority_soft_wrapped_units(source) != _prior_authority_soft_wrapped_units(source):
            raise core.VerificationError(
                "inline-link guard changed raw authority-unit structure"
            )

    inert = "See [provenance](https://example.invalid) for neutral history only.\n"
    if _layer_b_self_promotion_claim(inert) is not None:
        raise core.VerificationError(
            "inline-link visible-text canonicalization invented an unrelated authority claim"
        )
    if core._authority_soft_wrapped_units(inert) != _prior_authority_soft_wrapped_units(inert):
        raise core.VerificationError(
            "inline-link policy canonicalization changed inert raw unit structure"
        )

    print("[PASS] fresh-final exact inline-link self-promotion bypass repaired")
    print("[PASS] direct inline-link destination/title alternates preserve visible-text policy equivalence")
    print("[PASS] inline-link canonicalization occurs after raw authority-unit extraction")
    print("[PASS] inline-link repair preserves block/ownership/unit structure")
    print("[PASS] inline-HTML and character-reference stages remain ordered after link visible text")
    print("[PASS] images/reference-links/autolinks/malformed syntax are not superficially stripped")
    print("[PASS] inline-link repair remains bounded to direct inline-link policy semantics")


def _synthetic_check_with_inline_link_policy_normalization() -> None:
    _prior_synthetic_check()
    _check_fresh_final_inline_link_policy_regression()


# Only the policy matcher is replaced. The block/unit parser and all structural
# helpers remain exactly as provided by the predecessor.
core.layer_b_self_promotion_claim = _layer_b_self_promotion_claim
core.check_synthetic_rejections_and_transition_positives = (
    _synthetic_check_with_inline_link_policy_normalization
)


def main() -> int:
    actual = core.git_blob_sha1(Path(prior.__file__))
    if actual != PRIOR_INLINE_HTML_POLICY_BLOB_SHA:
        print(
            "[FAIL] prior inline-HTML policy verifier drift: "
            f"expected={PRIOR_INLINE_HTML_POLICY_BLOB_SHA} actual={actual}",
            file=core.sys.stderr,
        )
        return 1
    return prior.main()


if __name__ == "__main__":
    raise SystemExit(main())
