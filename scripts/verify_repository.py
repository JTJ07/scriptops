#!/usr/bin/env python3
"""Bounded fresh-final lazy-quote -> complete quoted HTML-comment lifecycle overlay.

The repaired fresh-final lazy-quote -> explicit quoted ATX verifier is retained
byte-for-byte at `scripts/verify_repository_fresh_final_lazy_quote_atx.py` and
pinned by Git blob SHA.

This overlay changes exactly one residual lifecycle shape: a source-column-zero
explicit quoted paragraph that remains open through one or more legal lazy
continuation lines without `>`, followed by one complete explicit quoted HTML
comment and then another explicit quoted paragraph. The lazy continuation stays
inside the first paragraph; the complete HTML comment starts a distinct leaf;
the following quoted paragraph starts another distinct leaf.

The repair is not a generic lazy-paragraph rewrite and does not generalize to
other HTML block types, incomplete comments, fences, thematic breaks, list-owned
quotes, arbitrary block transitions, interaction expansion, or all block-quote
lifecycle handling.
"""
from __future__ import annotations

from pathlib import Path
import verify_repository_fresh_final_lazy_quote_atx as prior

PRIOR_FRESH_FINAL_LAZY_QUOTE_ATX_BLOB_SHA = "9699fbe49d570f5b2e6ff0a9ec1ee569d93a2704"

core = prior.core
singleline = prior.singleline
_prior_authority_soft_wrapped_units = core._authority_soft_wrapped_units
_prior_synthetic_check = core.check_synthetic_rejections_and_transition_positives


def _explicit_quote_inner_complete_html_comment_layout(
    raw_line: str,
) -> tuple[int, int] | None:
    content = prior._top_level_quote_content(raw_line)
    if content is None:
        return None
    layout = singleline._markdown_html_block_start_layout(content)
    if layout is None:
        return None
    indent, block_type = layout
    if indent != 0 or block_type != 2:
        return None
    if not singleline._markdown_html_block_end_matches(content, block_type):
        return None
    return layout


def _lazy_quote_run_start_before_explicit_html_comment(
    lines: list[str],
    comment_index: int,
) -> int | None:
    """Return first lazy-line index for the bounded quoted-paragraph -> HTML shape."""
    if not (1 < comment_index < len(lines) - 1):
        return None
    if _explicit_quote_inner_complete_html_comment_layout(lines[comment_index]) is None:
        return None
    if not prior._ordinary_explicit_quote_paragraph_line(lines[comment_index + 1]):
        return None

    cursor = comment_index - 1
    if not prior._top_level_lazy_quote_continuation_candidate(lines[cursor]):
        return None

    while cursor >= 0 and prior._top_level_lazy_quote_continuation_candidate(lines[cursor]):
        cursor -= 1

    opener_index = cursor
    if opener_index < 0:
        return None
    if not prior._ordinary_explicit_quote_paragraph_line(lines[opener_index]):
        return None

    return opener_index + 1


def _split_lazy_quote_before_explicit_html_comment_boundaries(text: str) -> str:
    """Flush only a lazy-continued top-level quoted paragraph before complete HTML comment."""
    lines = text.splitlines()
    output: list[str] = []

    for index, raw_line in enumerate(lines):
        is_target = (
            _lazy_quote_run_start_before_explicit_html_comment(lines, index)
            is not None
        )
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
        _split_lazy_quote_before_explicit_html_comment_boundaries(text)
    )


def _direct_html_control() -> str:
    return (
        "> This file\n"
        "> <!-- neutral comment -->\n"
        "> grants release authority.\n"
    )


def _fresh_final_lazy_html_finding() -> str:
    return (
        "> This file\n"
        "lazy continuation\n"
        "> <!-- neutral comment -->\n"
        "> grants release authority.\n"
    )


def _lazy_atx_control() -> str:
    return (
        "> This file\n"
        "lazy continuation\n"
        "> # neutral heading\n"
        "> grants release authority.\n"
    )


def _direct_atx_control() -> str:
    return (
        "> This file\n"
        "> # neutral heading\n"
        "> grants release authority.\n"
    )


def _ordinary_lazy_no_boundary_control() -> str:
    return (
        "> This file\n"
        "lazy continuation\n"
        "grants release authority.\n"
    )


def _check_fresh_final_lazy_quote_to_html_comment_regression() -> None:
    direct_html = _direct_html_control()
    if _split_lazy_quote_before_explicit_html_comment_boundaries(direct_html) != direct_html:
        raise core.VerificationError(
            "fresh-final lazy->HTML repair modified direct explicit-quote HTML control"
        )
    direct_html_units = _prior_authority_soft_wrapped_units(direct_html)
    if len(direct_html_units) != 3 or any(
        core.layer_b_self_promotion_claim(u) for u in direct_html_units
    ):
        raise core.VerificationError(
            "fresh-final lazy->HTML repair changed direct complete HTML-comment semantics"
        )

    lazy_atx = _lazy_atx_control()
    if _split_lazy_quote_before_explicit_html_comment_boundaries(lazy_atx) != lazy_atx:
        raise core.VerificationError(
            "fresh-final lazy->HTML repair modified repaired lazy->ATX control text"
        )
    lazy_atx_units = _prior_authority_soft_wrapped_units(lazy_atx)
    if len(lazy_atx_units) != 3 or any(
        core.layer_b_self_promotion_claim(u) for u in lazy_atx_units
    ):
        raise core.VerificationError(
            "fresh-final lazy->HTML repair regressed repaired lazy->ATX semantics"
        )

    direct_atx = _direct_atx_control()
    if _split_lazy_quote_before_explicit_html_comment_boundaries(direct_atx) != direct_atx:
        raise core.VerificationError(
            "fresh-final lazy->HTML repair modified direct explicit-quote ATX control"
        )
    direct_atx_units = _prior_authority_soft_wrapped_units(direct_atx)
    if len(direct_atx_units) != 3 or any(
        core.layer_b_self_promotion_claim(u) for u in direct_atx_units
    ):
        raise core.VerificationError(
            "fresh-final lazy->HTML repair changed direct explicit-quote ATX semantics"
        )

    lazy_control = _ordinary_lazy_no_boundary_control()
    if _split_lazy_quote_before_explicit_html_comment_boundaries(lazy_control) != lazy_control:
        raise core.VerificationError(
            "fresh-final lazy->HTML repair split ordinary lazy continuation without HTML boundary"
        )
    lazy_units = _prior_authority_soft_wrapped_units(lazy_control)
    if len(lazy_units) != 1 or not core.layer_b_self_promotion_claim(lazy_units[0]):
        raise core.VerificationError(
            "ordinary legal lazy continuation no longer remains one quoted paragraph"
        )

    finding = _fresh_final_lazy_html_finding()
    prior_units = _prior_authority_soft_wrapped_units(finding)
    if len(prior_units) != 1 or not core.layer_b_self_promotion_claim(prior_units[0]):
        raise core.VerificationError(
            "fresh-final lazy->HTML predecessor no longer reproduces fused finding"
        )

    lines = finding.splitlines()
    if _lazy_quote_run_start_before_explicit_html_comment(lines, 2) != 1:
        raise core.VerificationError(
            "fresh-final lazy->HTML repair did not recognize semantic lazy paragraph tail"
        )
    if _explicit_quote_inner_complete_html_comment_layout(lines[2]) != (0, 2):
        raise core.VerificationError(
            "fresh-final lazy->HTML repair did not recognize complete quoted type-2 comment"
        )

    expected = (
        "> This file\n"
        "lazy continuation\n"
        "\n"
        "> <!-- neutral comment -->\n"
        "\n"
        "> grants release authority.\n"
    )
    transformed = _split_lazy_quote_before_explicit_html_comment_boundaries(finding)
    if transformed != expected:
        raise core.VerificationError(
            "fresh-final lazy->HTML boundary transform mismatch: "
            f"expected={expected!r} actual={transformed!r}"
        )

    units = _prior_authority_soft_wrapped_units(transformed)
    if len(units) != 3:
        raise core.VerificationError(
            f"fresh-final lazy->HTML repair must yield exactly three leaves, got {len(units)}"
        )
    normalized = [unit.upper() for unit in units]
    if not (
        "THIS FILE" in normalized[0]
        and "LAZY CONTINUATION" in normalized[0]
        and "<!-- NEUTRAL COMMENT -->" in normalized[1]
        and "GRANTS RELEASE AUTHORITY" in normalized[2]
    ):
        raise core.VerificationError(
            "fresh-final lazy->HTML repair changed expected three-leaf semantics"
        )
    if any(
        "THIS FILE" in unit and "GRANTS RELEASE AUTHORITY" in unit
        for unit in normalized
    ):
        raise core.VerificationError(
            "fresh-final lazy->HTML repair still fuses security fragments across comment"
        )
    if any(core.layer_b_self_promotion_claim(unit) for unit in units):
        raise core.VerificationError(
            "fresh-final lazy->HTML repaired units still produce a false self-promotion claim"
        )
    core.validate_layer_b_non_authority_text("acceptance/inert.md", finding)

    alternate = (
        "> structurally different quoted paragraph\n"
        "different legal lazy wording\n"
        "> <!-- structurally different complete comment -->\n"
        "> structurally different quoted tail\n"
    )
    alternate_transformed = _split_lazy_quote_before_explicit_html_comment_boundaries(
        alternate
    )
    if alternate_transformed == alternate:
        raise core.VerificationError(
            "fresh-final lazy->HTML repair depends on exact payload text"
        )
    if len(_prior_authority_soft_wrapped_units(alternate_transformed)) != 3:
        raise core.VerificationError(
            "fresh-final lazy->HTML structural alternate does not yield three leaves"
        )

    for untouched in [
        "> This file\nlazy continuation\n> <!-- incomplete comment\n> grants release authority.\n",
        "> This file\nlazy continuation\n> <div>\n> grants release authority.\n",
        "> This file\nlazy continuation\n> <style>body{}</style>\n> grants release authority.\n",
        "> This file\nlazy continuation\n> <?raw?>\n> grants release authority.\n",
        "> This file\nlazy continuation\n> <!DOCTYPE html>\n> grants release authority.\n",
        "> This file\nlazy continuation\n> <![CDATA[ raw ]]>\n> grants release authority.\n",
        "> This file\nlazy continuation\n> <x-widget>\n> grants release authority.\n",
        "> This file\nlazy continuation\n> ***\n> grants release authority.\n",
        "> This file\nlazy continuation\n> ```\n> grants release authority.\n",
        "- owner\n  > This file\n  lazy continuation\n  > <!-- neutral comment -->\n  > grants release authority.\n",
    ]:
        if _split_lazy_quote_before_explicit_html_comment_boundaries(untouched) != untouched:
            raise core.VerificationError(
                "fresh-final lazy->HTML repair escaped bounded complete type-2 scope"
            )

    print("[PASS] fresh-final lazy quoted paragraph -> complete quoted HTML-comment reproduction repaired")
    print("[PASS] fresh-final lazy->HTML repair preserves first paragraph lazy continuation")
    print("[PASS] fresh-final lazy->HTML repair preserves direct HTML, lazy->ATX, and direct ATX controls")
    print("[PASS] fresh-final lazy->HTML repair leaves ordinary lazy continuation unsplit")
    print("[PASS] fresh-final lazy->HTML repair is structural/text-independent and bounded")


def _synthetic_check_with_fresh_final_lazy_quote_to_html_comment() -> None:
    _prior_synthetic_check()
    _check_fresh_final_lazy_quote_to_html_comment_regression()


core._authority_soft_wrapped_units = _authority_soft_wrapped_units
core.check_synthetic_rejections_and_transition_positives = (
    _synthetic_check_with_fresh_final_lazy_quote_to_html_comment
)


def main() -> int:
    actual = core.git_blob_sha1(Path(prior.__file__))
    if actual != PRIOR_FRESH_FINAL_LAZY_QUOTE_ATX_BLOB_SHA:
        print(
            "[FAIL] prior fresh-final lazy->ATX verifier drift: "
            f"expected={PRIOR_FRESH_FINAL_LAZY_QUOTE_ATX_BLOB_SHA} actual={actual}",
            file=core.sys.stderr,
        )
        return 1
    return prior.main()


if __name__ == "__main__":
    raise SystemExit(main())
