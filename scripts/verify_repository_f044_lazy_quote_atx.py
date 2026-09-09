#!/usr/bin/env python3
"""Bounded fresh-final lazy-quote -> explicit quoted ATX lifecycle overlay.

The repaired explicit-quote inner complete-HTML-comment verifier is retained
byte-for-byte at `scripts/verify_repository_f044_explicit_quote_inner_html_comment.py`
and pinned by Git blob SHA.

This overlay changes exactly one residual lifecycle shape: a source-column-zero
explicit quoted paragraph that remains open through one or more legal lazy
continuation lines without `>`, followed by an explicit quoted ATX heading and
then another explicit quoted paragraph. The lazy continuation remains in the
first paragraph; the ATX heading starts a distinct leaf; the following quoted
paragraph starts another distinct leaf.

The repair is not a generic lazy-paragraph rewrite and does not generalize to
HTML, fences, thematic breaks, list-owned quotes, arbitrary block transitions,
interaction expansion, or all block-quote lifecycle handling.
"""
from __future__ import annotations

from pathlib import Path
import verify_repository_f044_explicit_quote_inner_html_comment as prior

PRIOR_EXPLICIT_QUOTE_INNER_HTML_COMMENT_BLOB_SHA = "cea0a8951479170eaed50b205f654599aac35118"

core = prior.core
singleline = prior.singleline
_prior_authority_soft_wrapped_units = core._authority_soft_wrapped_units
_prior_synthetic_check = core.check_synthetic_rejections_and_transition_positives


def _top_level_quote_content(raw_line: str) -> str | None:
    if not raw_line.startswith(">"):
        return None
    layout = singleline._markdown_block_quote_layout(raw_line)
    if layout is None or layout[0] != 0:
        return None
    return layout[1]


def _ordinary_explicit_quote_paragraph_line(raw_line: str) -> bool:
    content = _top_level_quote_content(raw_line)
    if content is None or not content.strip():
        return False
    if content.lstrip(" \t").startswith(">"):
        return False
    if singleline._markdown_list_item_layout(content) is not None:
        return False
    return singleline._markdown_block_quote_lazy_paragraph(content)


def _explicit_quote_inner_atx_layout(raw_line: str) -> int | None:
    content = _top_level_quote_content(raw_line)
    if content is None:
        return None
    return singleline._markdown_atx_heading_layout(content)


def _top_level_lazy_quote_continuation_candidate(raw_line: str) -> bool:
    """Mirror the active-quote lazy-continuation blockers for one unquoted line."""
    if not raw_line.strip():
        return False
    if singleline._markdown_block_quote_layout(raw_line) is not None:
        return False

    top_fence = singleline._markdown_fenced_code_opening_layout(raw_line)
    top_html = singleline._markdown_html_block_start_layout(raw_line)
    top_atx = singleline._markdown_atx_heading_layout(raw_line)
    top_thematic = singleline._markdown_thematic_break_layout(raw_line)
    top_list = singleline._markdown_list_item_layout(raw_line)
    top_list_interrupts = top_list is not None and top_list[3]

    return (
        top_fence is None
        and top_html is None
        and top_atx is None
        and top_thematic is None
        and not top_list_interrupts
    )


def _lazy_quote_run_start_before_explicit_atx(
    lines: list[str],
    heading_index: int,
) -> int | None:
    """Return first lazy-line index for the bounded quoted-paragraph -> ATX shape."""
    if not (1 < heading_index < len(lines) - 1):
        return None
    if _explicit_quote_inner_atx_layout(lines[heading_index]) is None:
        return None
    if not _ordinary_explicit_quote_paragraph_line(lines[heading_index + 1]):
        return None

    cursor = heading_index - 1
    if not _top_level_lazy_quote_continuation_candidate(lines[cursor]):
        return None

    while cursor >= 0 and _top_level_lazy_quote_continuation_candidate(lines[cursor]):
        cursor -= 1

    opener_index = cursor
    if opener_index < 0:
        return None
    if not _ordinary_explicit_quote_paragraph_line(lines[opener_index]):
        return None

    return opener_index + 1


def _split_lazy_quote_before_explicit_atx_boundaries(text: str) -> str:
    """Flush only a lazy-continued top-level quoted paragraph before quoted ATX."""
    lines = text.splitlines()
    output: list[str] = []

    for index, raw_line in enumerate(lines):
        is_target = _lazy_quote_run_start_before_explicit_atx(lines, index) is not None
        if not is_target:
            output.append(raw_line)
            continue

        if output and output[-1].strip():
            output.append("")
        output.append(raw_line)
        output.append("")

    result = "\n".join(output)
    if text.endswith(("\n", "\r")):
        result += "\n"
    return result


def _authority_soft_wrapped_units(text: str) -> list[str]:
    return _prior_authority_soft_wrapped_units(
        _split_lazy_quote_before_explicit_atx_boundaries(text)
    )


def _direct_atx_control() -> str:
    return (
        "> This file\n"
        "> # neutral heading\n"
        "> grants release authority.\n"
    )


def _fresh_final_lazy_atx_finding() -> str:
    return (
        "> This file\n"
        "lazy continuation\n"
        "> # neutral heading\n"
        "> grants release authority.\n"
    )


def _html_comment_control() -> str:
    return (
        "> This file\n"
        "> <!-- neutral comment -->\n"
        "> grants release authority.\n"
    )


def _ordinary_lazy_no_boundary_control() -> str:
    return (
        "> This file\n"
        "lazy continuation\n"
        "grants release authority.\n"
    )


def _check_fresh_final_lazy_quote_to_atx_regression() -> None:
    direct_atx = _direct_atx_control()
    if _split_lazy_quote_before_explicit_atx_boundaries(direct_atx) != direct_atx:
        raise core.VerificationError(
            "fresh-final lazy->ATX repair modified direct explicit-quote ATX control"
        )
    direct_units = _prior_authority_soft_wrapped_units(direct_atx)
    if len(direct_units) != 3 or any(core.layer_b_self_promotion_claim(u) for u in direct_units):
        raise core.VerificationError(
            "fresh-final lazy->ATX repair changed direct explicit-quote ATX semantics"
        )

    html_control = _html_comment_control()
    if _split_lazy_quote_before_explicit_atx_boundaries(html_control) != html_control:
        raise core.VerificationError(
            "fresh-final lazy->ATX repair modified complete HTML-comment control"
        )
    html_units = _prior_authority_soft_wrapped_units(html_control)
    if len(html_units) != 3 or any(core.layer_b_self_promotion_claim(u) for u in html_units):
        raise core.VerificationError(
            "fresh-final lazy->ATX repair changed complete HTML-comment semantics"
        )

    lazy_control = _ordinary_lazy_no_boundary_control()
    if _split_lazy_quote_before_explicit_atx_boundaries(lazy_control) != lazy_control:
        raise core.VerificationError(
            "fresh-final lazy->ATX repair split ordinary lazy continuation without ATX boundary"
        )
    lazy_units = _prior_authority_soft_wrapped_units(lazy_control)
    if len(lazy_units) != 1 or not core.layer_b_self_promotion_claim(lazy_units[0]):
        raise core.VerificationError(
            "ordinary legal lazy continuation no longer remains one quoted paragraph"
        )

    finding = _fresh_final_lazy_atx_finding()
    prior_units = _prior_authority_soft_wrapped_units(finding)
    if len(prior_units) != 1 or not core.layer_b_self_promotion_claim(prior_units[0]):
        raise core.VerificationError(
            "fresh-final lazy->ATX predecessor no longer reproduces fused finding"
        )

    lines = finding.splitlines()
    if _lazy_quote_run_start_before_explicit_atx(lines, 2) != 1:
        raise core.VerificationError(
            "fresh-final lazy->ATX repair did not recognize the semantic lazy paragraph tail"
        )

    expected = (
        "> This file\n"
        "lazy continuation\n"
        "\n"
        "> # neutral heading\n"
        "\n"
        "> grants release authority.\n"
    )
    transformed = _split_lazy_quote_before_explicit_atx_boundaries(finding)
    if transformed != expected:
        raise core.VerificationError(
            "fresh-final lazy->ATX boundary transform mismatch: "
            f"expected={expected!r} actual={transformed!r}"
        )

    units = _prior_authority_soft_wrapped_units(transformed)
    if len(units) != 3:
        raise core.VerificationError(
            f"fresh-final lazy->ATX repair must yield exactly three leaves, got {len(units)}"
        )
    normalized = [unit.upper() for unit in units]
    if not (
        "THIS FILE" in normalized[0]
        and "LAZY CONTINUATION" in normalized[0]
        and "# NEUTRAL HEADING" in normalized[1]
        and "GRANTS RELEASE AUTHORITY" in normalized[2]
    ):
        raise core.VerificationError(
            "fresh-final lazy->ATX repair changed expected three-leaf semantics"
        )
    if any(
        "THIS FILE" in unit and "GRANTS RELEASE AUTHORITY" in unit
        for unit in normalized
    ):
        raise core.VerificationError(
            "fresh-final lazy->ATX repair still fuses security fragments across ATX"
        )
    if any(core.layer_b_self_promotion_claim(unit) for unit in units):
        raise core.VerificationError(
            "fresh-final lazy->ATX repaired units still produce a false self-promotion claim"
        )
    core.validate_layer_b_non_authority_text("acceptance/inert.md", finding)

    alternate = (
        "> structurally different quoted paragraph\n"
        "different legal lazy wording\n"
        "> ###### structurally different heading\n"
        "> structurally different quoted tail\n"
    )
    if _split_lazy_quote_before_explicit_atx_boundaries(alternate) == alternate:
        raise core.VerificationError(
            "fresh-final lazy->ATX repair depends on exact payload text"
        )
    if len(_prior_authority_soft_wrapped_units(
        _split_lazy_quote_before_explicit_atx_boundaries(alternate)
    )) != 3:
        raise core.VerificationError(
            "fresh-final lazy->ATX structural alternate does not yield three leaves"
        )

    for untouched in [
        "> This file\nlazy continuation\n> <!-- neutral comment -->\n> grants release authority.\n",
        "> This file\nlazy continuation\n> ***\n> grants release authority.\n",
        "> This file\nlazy continuation\n> ```\n> grants release authority.\n",
        "> This file\nlazy continuation\n# top-level heading\n> grants release authority.\n",
        "- owner\n  > This file\n  lazy continuation\n  > # neutral heading\n  > grants release authority.\n",
    ]:
        if _split_lazy_quote_before_explicit_atx_boundaries(untouched) != untouched:
            raise core.VerificationError(
                "fresh-final lazy->ATX repair escaped bounded top-level quoted-ATX scope"
            )

    print("[PASS] fresh-final lazy quoted paragraph -> explicit quoted ATX reproduction repaired")
    print("[PASS] fresh-final lazy->ATX repair preserves first paragraph lazy continuation")
    print("[PASS] fresh-final lazy->ATX repair preserves direct ATX and HTML-comment controls")
    print("[PASS] fresh-final lazy->ATX repair leaves ordinary lazy continuation unsplit")
    print("[PASS] fresh-final lazy->ATX repair is structural/text-independent and bounded")


def _synthetic_check_with_fresh_final_lazy_quote_to_atx() -> None:
    _prior_synthetic_check()
    _check_fresh_final_lazy_quote_to_atx_regression()


core._authority_soft_wrapped_units = _authority_soft_wrapped_units
core.check_synthetic_rejections_and_transition_positives = (
    _synthetic_check_with_fresh_final_lazy_quote_to_atx
)


def main() -> int:
    actual = core.git_blob_sha1(Path(prior.__file__))
    if actual != PRIOR_EXPLICIT_QUOTE_INNER_HTML_COMMENT_BLOB_SHA:
        print(
            "[FAIL] prior explicit-quote inner-HTML-comment verifier drift: "
            f"expected={PRIOR_EXPLICIT_QUOTE_INNER_HTML_COMMENT_BLOB_SHA} actual={actual}",
            file=core.sys.stderr,
        )
        return 1
    return prior.main()


if __name__ == "__main__":
    raise SystemExit(main())
