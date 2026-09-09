#!/usr/bin/env python3
"""Bounded fresh-final character-reference policy-semantic normalization overlay.

The repaired fresh-final lazy-quote -> complete quoted HTML-comment verifier is
retained byte-for-byte at `scripts/verify_repository_fresh_final_lazy_quote_html.py`
and pinned by Git blob SHA.

This overlay does not change Markdown parsing, block boundaries, ownership,
quote/list structure, lifecycle, whitespace policy, or Unicode normalization.
Raw Markdown is parsed exactly as before. Only after the existing parser emits
an authority unit do we decode strict, semicolon-terminated legal-looking
character references for policy matching. The decoded semantic unit is then
checked by the existing self-reference/promotion/negation grammar.

This is semantic-equivalence preservation for self-promotion policy matching,
not generic HTML normalization and not raw-Markdown pre-decoding.
"""
from __future__ import annotations

import html
from pathlib import Path
import re
import verify_repository_fresh_final_lazy_quote_html as prior

PRIOR_FRESH_FINAL_LAZY_QUOTE_HTML_BLOB_SHA = "d82237f6ab6546dbf1a5c4eeddc9e26c906cdf05"

core = prior.core
singleline = prior.singleline
_prior_authority_soft_wrapped_units = core._authority_soft_wrapped_units
_prior_layer_b_self_promotion_claim = core.layer_b_self_promotion_claim
_prior_synthetic_check = core.check_synthetic_rejections_and_transition_positives

# Deliberately strict at this layer: only semicolon-terminated numeric or named
# references are candidates. Unknown named references remain unchanged because
# html.unescape() returns the original token. Missing-semicolon lookalikes are
# not silently normalized.
_STRICT_POLICY_CHARACTER_REFERENCE = re.compile(
    r"&(?:#[0-9]+|#[xX][0-9A-Fa-f]+|[A-Za-z][A-Za-z0-9]*);"
)


def _decode_policy_character_references(text: str) -> str:
    """Decode strict character references only in already-extracted policy text."""

    def replace(match: re.Match[str]) -> str:
        token = match.group(0)
        decoded = html.unescape(token)
        return decoded if decoded != token else token

    return _STRICT_POLICY_CHARACTER_REFERENCE.sub(replace, text)


def _policy_claim_from_extracted_unit(raw_unit: str) -> bool:
    """Apply the frozen self-promotion grammar to semantic text of one unit."""
    semantic_unit = _decode_policy_character_references(raw_unit)

    for line in core._authority_clauses(semantic_unit):
        self_referential = any(
            term in line for term in core.LAYER_B_SELF_REFERENCE_TERMS
        )
        promotion = any(term in line for term in core.LAYER_B_PROMOTION_TERMS)
        if self_referential and promotion:
            if core._all_promotions_locally_noncurrent(line):
                continue
            return True

    # Preserve the existing F016 whole-line safety check after semantic decode.
    whole_line = core._normalized_authority_line(semantic_unit)
    whole_self_referential = any(
        term in whole_line for term in core.LAYER_B_SELF_REFERENCE_TERMS
    )
    whole_promotion = any(
        term in whole_line for term in core.LAYER_B_PROMOTION_TERMS
    )
    return (
        whole_self_referential
        and whole_promotion
        and not core._all_promotions_locally_noncurrent(whole_line)
    )


def _layer_b_self_promotion_claim(text: str) -> str | None:
    """Parse raw Markdown first; decode only each extracted unit for policy matching."""
    for raw_unit in _prior_authority_soft_wrapped_units(text):
        if _policy_claim_from_extracted_unit(raw_unit):
            # Preserve the historical diagnostic surface: report the raw unit,
            # while detection itself is based on its decoded semantic text.
            return raw_unit.strip()
    return None


def _rejected(source: str) -> tuple[bool, str]:
    try:
        core.validate_layer_b_non_authority_text("acceptance/inert.md", source)
    except core.VerificationError as exc:
        return True, str(exc)
    return False, "ACCEPTED"


def _check_fresh_final_character_reference_policy_regression() -> None:
    literal = "This file grants release authority.\n"
    finding = "This&#32;file grants release authority.\n"

    # The predecessor must still reproduce the fresh-final finding.
    if _prior_layer_b_self_promotion_claim(literal) is None:
        raise core.VerificationError(
            "character-reference policy predecessor lost literal self-promotion control"
        )
    if _prior_layer_b_self_promotion_claim(finding) is not None:
        raise core.VerificationError(
            "character-reference policy predecessor no longer reproduces encoded bypass"
        )

    literal_units = _prior_authority_soft_wrapped_units(literal)
    finding_units = _prior_authority_soft_wrapped_units(finding)
    if len(literal_units) != 1 or len(finding_units) != 1:
        raise core.VerificationError(
            "character-reference policy finding must remain one raw authority unit"
        )

    # Structural invariance: this overlay must not replace the parser or change
    # unit membership for the exact raw inputs.
    if core._authority_soft_wrapped_units is not _prior_authority_soft_wrapped_units:
        raise core.VerificationError(
            "character-reference policy repair modified authority-unit parser binding"
        )
    if core._authority_soft_wrapped_units(literal) != literal_units:
        raise core.VerificationError(
            "character-reference policy repair changed literal unit structure"
        )
    if core._authority_soft_wrapped_units(finding) != finding_units:
        raise core.VerificationError(
            "character-reference policy repair changed encoded unit structure"
        )

    literal_semantic = _decode_policy_character_references(literal_units[0])
    finding_semantic = _decode_policy_character_references(finding_units[0])
    if literal_semantic != finding_semantic:
        raise core.VerificationError(
            "exact character-reference finding does not canonicalize to literal policy text"
        )

    literal_claim = _layer_b_self_promotion_claim(literal)
    finding_claim = _layer_b_self_promotion_claim(finding)
    if literal_claim is None or finding_claim is None:
        raise core.VerificationError(
            "character-reference policy repair does not preserve equivalent claim detection"
        )

    literal_rejected, _ = _rejected(literal)
    finding_rejected, _ = _rejected(finding)
    if not literal_rejected or not finding_rejected:
        raise core.VerificationError(
            "character-reference semantic equivalents must both be rejected"
        )

    # Small, bounded mechanism proof: different legal references that decode to
    # the same semantic literal must yield the same policy result. This is not
    # a sweep of HTML/entity behavior.
    alternates = [
        "This&#x20;file grants release authority.\n",
        "Th&#105;s file grants release authority.\n",
        "This f&#x69;le grants release authority.\n",
    ]
    for alternate in alternates:
        units = _prior_authority_soft_wrapped_units(alternate)
        if len(units) != 1:
            raise core.VerificationError(
                "character-reference alternate changed raw interpretive-unit membership"
            )
        if _decode_policy_character_references(units[0]) != literal_units[0]:
            raise core.VerificationError(
                f"character-reference alternate is not semantic-equivalent: {alternate!r}"
            )
        if _layer_b_self_promotion_claim(alternate) is None:
            raise core.VerificationError(
                f"character-reference alternate bypasses self-promotion matcher: {alternate!r}"
            )
        rejected, _ = _rejected(alternate)
        if not rejected:
            raise core.VerificationError(
                f"character-reference alternate is not rejected: {alternate!r}"
            )

    # Existing negation semantics remain delegated to the frozen grammar even
    # when the self-reference contains a legal character reference.
    negated = "This&#32;file does not grant authority.\n"
    if _layer_b_self_promotion_claim(negated) is not None:
        raise core.VerificationError(
            "character-reference decoding changed existing local-negation semantics"
        )

    # Malformed/unknown spellings are not silently normalized by this repair.
    malformed = [
        "This&#32file grants release authority.\n",
        "This&#x20file grants release authority.\n",
        "This&DefinitelyNotARealEntity;file grants release authority.\n",
    ]
    for source in malformed:
        if _decode_policy_character_references(source) != source:
            raise core.VerificationError(
                f"character-reference policy repair over-normalized malformed/unknown text: {source!r}"
            )
        if core._authority_soft_wrapped_units(source) != _prior_authority_soft_wrapped_units(source):
            raise core.VerificationError(
                "malformed character-reference guard changed raw unit structure"
            )

    # Non-security entity usage may decode for policy text but must not invent a
    # self-promotion result; parser structure remains untouched.
    inert = "This file mentions AT&T &amp; provenance only.\n"
    if _layer_b_self_promotion_claim(inert) is not None:
        raise core.VerificationError(
            "character-reference policy decoding invented an unrelated authority claim"
        )
    if core._authority_soft_wrapped_units(inert) != _prior_authority_soft_wrapped_units(inert):
        raise core.VerificationError(
            "character-reference policy decoding changed inert raw unit structure"
        )

    print("[PASS] fresh-final exact character-reference self-promotion bypass repaired")
    print("[PASS] character-reference semantic equivalents yield identical policy rejection")
    print("[PASS] policy decoding occurs after raw authority-unit extraction")
    print("[PASS] character-reference repair preserves block/ownership/unit structure")
    print("[PASS] malformed/unknown references are not silently over-normalized")
    print("[PASS] character-reference repair remains bounded to policy semantics")


def _synthetic_check_with_character_reference_policy_normalization() -> None:
    _prior_synthetic_check()
    _check_fresh_final_character_reference_policy_regression()


# Only the policy matcher is replaced. The parser and every structural helper
# remain exactly as provided by the predecessor.
core.layer_b_self_promotion_claim = _layer_b_self_promotion_claim
core.check_synthetic_rejections_and_transition_positives = (
    _synthetic_check_with_character_reference_policy_normalization
)


def main() -> int:
    actual = core.git_blob_sha1(Path(prior.__file__))
    if actual != PRIOR_FRESH_FINAL_LAZY_QUOTE_HTML_BLOB_SHA:
        print(
            "[FAIL] prior fresh-final lazy-HTML verifier drift: "
            f"expected={PRIOR_FRESH_FINAL_LAZY_QUOTE_HTML_BLOB_SHA} actual={actual}",
            file=core.sys.stderr,
        )
        return 1
    return prior.main()


if __name__ == "__main__":
    raise SystemExit(main())
