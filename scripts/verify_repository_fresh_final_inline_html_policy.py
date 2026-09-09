#!/usr/bin/env python3
"""Bounded fresh-final inline-HTML policy-semantic normalization overlay.

The repaired fresh-final character-reference policy verifier is retained byte-for-byte at
`scripts/verify_repository_fresh_final_character_reference_policy.py` and pinned by Git
blob SHA.

This overlay does not change Markdown parsing, block boundaries, ownership,
quote/list structure, lifecycle, whitespace policy, Unicode normalization, or
character-reference handling. Raw Markdown is parsed exactly as before. Only
after the existing parser emits an authority unit do we canonicalize a bounded
class of well-formed, transparent inline HTML for policy-visible text. The
result then flows through the predecessor's character-reference decoding and
existing self-reference/promotion/negation grammar.

This is not regex tag stripping, not a generic sanitizer/parser rewrite, and
not raw-Markdown pre-processing.
"""
from __future__ import annotations

from html.parser import HTMLParser
from pathlib import Path
import verify_repository_fresh_final_character_reference_policy as prior

PRIOR_CHARACTER_REFERENCE_POLICY_BLOB_SHA = "60d050b76673e2aa27bd778a8765fcd65b8b9c02"

core = prior.core
singleline = prior.singleline
_prior_authority_soft_wrapped_units = core._authority_soft_wrapped_units
_prior_layer_b_self_promotion_claim = core.layer_b_self_promotion_claim
_prior_synthetic_check = core.check_synthetic_rejections_and_transition_positives

# Deliberately narrow: paired inline phrasing tags that are text-transparent in
# this policy layer when used without attributes. Attributes are not accepted
# because their presentation semantics can depend on CSS/hidden state outside
# this verifier's bounded evidence.
_TRANSPARENT_INLINE_TAGS = frozenset(
    {
        "abbr",
        "b",
        "cite",
        "code",
        "del",
        "em",
        "i",
        "ins",
        "kbd",
        "mark",
        "s",
        "samp",
        "small",
        "span",
        "strong",
        "sub",
        "sup",
        "u",
        "var",
    }
)


class _TransparentInlineVisibleText(HTMLParser):
    """Validate a narrow transparent inline fragment and collect its text.

    Character references are preserved verbatim here so that the predecessor's
    strict policy character-reference decoder remains the next semantic stage.
    """

    def __init__(self) -> None:
        super().__init__(convert_charrefs=False)
        self.parts: list[str] = []
        self.stack: list[str] = []
        self.valid = True
        self.saw_markup = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag = tag.lower()
        if tag not in _TRANSPARENT_INLINE_TAGS or attrs:
            self.valid = False
            return
        self.saw_markup = True
        self.stack.append(tag)

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if tag not in _TRANSPARENT_INLINE_TAGS or not self.stack or self.stack[-1] != tag:
            self.valid = False
            return
        self.stack.pop()

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        # Self-closing/void-like markup is outside the text-transparent class.
        self.valid = False

    def handle_data(self, data: str) -> None:
        self.parts.append(data)

    def handle_entityref(self, name: str) -> None:
        self.parts.append(f"&{name};")

    def handle_charref(self, name: str) -> None:
        self.parts.append(f"&#{name};")

    def handle_comment(self, data: str) -> None:
        self.valid = False

    def handle_decl(self, decl: str) -> None:
        self.valid = False

    def handle_pi(self, data: str) -> None:
        self.valid = False

    def unknown_decl(self, data: str) -> None:
        self.valid = False


def _canonicalize_transparent_inline_html(text: str) -> str:
    """Return policy-visible text only for a strictly validated inline fragment.

    Conservative guards prevent this stage from interpreting markup inside
    Markdown code spans or backslash-escaped tag starts without implementing a
    second Markdown inline parser.
    """
    if "<" not in text or ">" not in text:
        return text
    if "`" in text or "\\<" in text:
        return text

    parser = _TransparentInlineVisibleText()
    try:
        parser.feed(text)
        parser.close()
    except Exception:
        return text

    if not parser.valid or parser.stack or not parser.saw_markup:
        return text
    return "".join(parser.parts)


def _policy_claim_from_extracted_unit(raw_unit: str) -> bool:
    visible_unit = _canonicalize_transparent_inline_html(raw_unit)
    return prior._policy_claim_from_extracted_unit(visible_unit)


def _layer_b_self_promotion_claim(text: str) -> str | None:
    """Parse raw Markdown first; canonicalize only each extracted policy unit."""
    for raw_unit in _prior_authority_soft_wrapped_units(text):
        if _policy_claim_from_extracted_unit(raw_unit):
            # Preserve historical diagnostics: report raw source spelling.
            return raw_unit.strip()
    return None


def _rejected(source: str) -> tuple[bool, str]:
    try:
        core.validate_layer_b_non_authority_text("acceptance/inert.md", source)
    except core.VerificationError as exc:
        return True, str(exc)
    return False, "ACCEPTED"


def _check_fresh_final_inline_html_policy_regression() -> None:
    literal = "This file grants release authority.\n"
    finding = "This <span>file</span> grants release authority.\n"

    # The predecessor must still reproduce the fresh-final finding while
    # keeping both inputs in one raw interpretive unit.
    if _prior_layer_b_self_promotion_claim(literal) is None:
        raise core.VerificationError(
            "inline-HTML policy predecessor lost literal self-promotion control"
        )
    if _prior_layer_b_self_promotion_claim(finding) is not None:
        raise core.VerificationError(
            "inline-HTML policy predecessor no longer reproduces markup bypass"
        )

    literal_units = _prior_authority_soft_wrapped_units(literal)
    finding_units = _prior_authority_soft_wrapped_units(finding)
    if len(literal_units) != 1 or len(finding_units) != 1:
        raise core.VerificationError(
            "inline-HTML policy finding must remain one raw authority unit"
        )

    # Structural invariance: this repair does not replace or mutate the parser.
    if core._authority_soft_wrapped_units is not _prior_authority_soft_wrapped_units:
        raise core.VerificationError(
            "inline-HTML policy repair modified authority-unit parser binding"
        )
    if core._authority_soft_wrapped_units(literal) != literal_units:
        raise core.VerificationError(
            "inline-HTML policy repair changed literal unit structure"
        )
    if core._authority_soft_wrapped_units(finding) != finding_units:
        raise core.VerificationError(
            "inline-HTML policy repair changed markup unit structure"
        )

    if _canonicalize_transparent_inline_html(finding_units[0]) != literal_units[0]:
        raise core.VerificationError(
            "exact inline-HTML finding does not canonicalize to literal visible policy text"
        )

    literal_claim = _layer_b_self_promotion_claim(literal)
    finding_claim = _layer_b_self_promotion_claim(finding)
    if literal_claim is None or finding_claim is None:
        raise core.VerificationError(
            "inline-HTML visible-text equivalents must preserve claim detection"
        )

    literal_rejected, _ = _rejected(literal)
    finding_rejected, _ = _rejected(finding)
    if not literal_rejected or not finding_rejected:
        raise core.VerificationError(
            "inline-HTML visible-text equivalents must both be rejected"
        )

    # Small mechanism proof across distinct transparent tag shapes. This is not
    # an HTML sweep and deliberately excludes attributes/void/script-like tags.
    alternates = [
        "This <em>file</em> grants release authority.\n",
        "This <strong>fi<em>le</em></strong> grants release authority.\n",
        "This f<i>i</i>le grants release authority.\n",
    ]
    for alternate in alternates:
        units = _prior_authority_soft_wrapped_units(alternate)
        if len(units) != 1:
            raise core.VerificationError(
                "inline-HTML alternate changed raw interpretive-unit membership"
            )
        if _canonicalize_transparent_inline_html(units[0]) != literal_units[0]:
            raise core.VerificationError(
                f"inline-HTML alternate is not visible-text equivalent: {alternate!r}"
            )
        if _layer_b_self_promotion_claim(alternate) is None:
            raise core.VerificationError(
                f"inline-HTML alternate bypasses self-promotion matcher: {alternate!r}"
            )
        rejected, _ = _rejected(alternate)
        if not rejected:
            raise core.VerificationError(
                f"inline-HTML alternate is not rejected: {alternate!r}"
            )

    # Composition order is preserved: visible-text canonicalization first,
    # predecessor strict character-reference decoding second.
    composed = "This <span>f&#105;le</span> grants release authority.\n"
    composed_units = _prior_authority_soft_wrapped_units(composed)
    if len(composed_units) != 1:
        raise core.VerificationError(
            "inline-HTML + character-reference composition changed unit membership"
        )
    visible_composed = _canonicalize_transparent_inline_html(composed_units[0])
    if visible_composed != "This f&#105;le grants release authority.":
        raise core.VerificationError(
            "inline-HTML canonicalizer consumed or reordered character-reference stage"
        )
    if prior._decode_policy_character_references(visible_composed) != literal_units[0]:
        raise core.VerificationError(
            "character-reference decoding no longer follows inline visible-text stage"
        )
    if _layer_b_self_promotion_claim(composed) is None:
        raise core.VerificationError(
            "inline-HTML + character-reference equivalent bypasses policy matcher"
        )

    # Existing direct character-reference repair stays GREEN.
    encoded = "This&#32;file grants release authority.\n"
    if _layer_b_self_promotion_claim(encoded) is None:
        raise core.VerificationError(
            "inline-HTML repair regressed character-reference policy normalization"
        )

    # Existing local-negation semantics remain delegated unchanged.
    negated = "This <span>file</span> does not grant authority.\n"
    if _layer_b_self_promotion_claim(negated) is not None:
        raise core.VerificationError(
            "inline-HTML canonicalization changed local-negation semantics"
        )

    # Malformed or potentially non-equivalent markup must remain raw rather than
    # being blindly stripped. Each guard also remains structurally unchanged.
    untouched = [
        "This <span class=\"neutral\">file</span> grants release authority.\n",
        "This <span>file grants release authority.\n",
        "This <span>file</em> grants release authority.\n",
        "This <!-- file --> grants release authority.\n",
        "This <br>file grants release authority.\n",
        "This <script>file</script> grants release authority.\n",
        "This `<span>file</span>` grants release authority.\n",
        "This \\<span>file</span> grants release authority.\n",
    ]
    for source in untouched:
        if _canonicalize_transparent_inline_html(source) != source:
            raise core.VerificationError(
                f"inline-HTML policy repair over-canonicalized guarded markup: {source!r}"
            )
        if core._authority_soft_wrapped_units(source) != _prior_authority_soft_wrapped_units(source):
            raise core.VerificationError(
                "inline-HTML guard changed raw authority-unit structure"
            )

    inert = "This file mentions <span>provenance</span> only.\n"
    if _layer_b_self_promotion_claim(inert) is not None:
        raise core.VerificationError(
            "inline-HTML visible-text canonicalization invented an unrelated authority claim"
        )
    if core._authority_soft_wrapped_units(inert) != _prior_authority_soft_wrapped_units(inert):
        raise core.VerificationError(
            "inline-HTML policy canonicalization changed inert raw unit structure"
        )

    print("[PASS] fresh-final exact inline-HTML self-promotion bypass repaired")
    print("[PASS] transparent inline-tag alternates preserve visible-text policy equivalence")
    print("[PASS] inline-HTML canonicalization occurs after raw authority-unit extraction")
    print("[PASS] inline-HTML repair preserves block/ownership/unit structure")
    print("[PASS] character-reference decoding remains the next semantic stage")
    print("[PASS] attributes/comments/malformed/non-transparent markup are not blindly stripped")
    print("[PASS] inline-HTML repair remains bounded to transparent policy-visible text")


def _synthetic_check_with_inline_html_policy_normalization() -> None:
    _prior_synthetic_check()
    _check_fresh_final_inline_html_policy_regression()


# Only the policy matcher is replaced. The parser and structural helpers remain
# exactly as provided by the predecessor.
core.layer_b_self_promotion_claim = _layer_b_self_promotion_claim
core.check_synthetic_rejections_and_transition_positives = (
    _synthetic_check_with_inline_html_policy_normalization
)


def main() -> int:
    actual = core.git_blob_sha1(Path(prior.__file__))
    if actual != PRIOR_CHARACTER_REFERENCE_POLICY_BLOB_SHA:
        print(
            "[FAIL] prior character-reference policy verifier drift: "
            f"expected={PRIOR_CHARACTER_REFERENCE_POLICY_BLOB_SHA} actual={actual}",
            file=core.sys.stderr,
        )
        return 1
    return prior.main()


if __name__ == "__main__":
    raise SystemExit(main())
