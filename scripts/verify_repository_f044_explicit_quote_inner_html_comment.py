#!/usr/bin/env python3
"""Bounded F044 explicit-quote inner complete-HTML-comment block-leaf overlay.

The repaired explicit-quote inner-ATX verifier is retained byte-for-byte at
`scripts/verify_repository_f044_explicit_quote_inner_atx.py` and pinned by Git
blob SHA. This overlay changes only one adjacent lifecycle boundary: a
source-column-zero explicit block quote whose current quoted paragraph is
followed by one complete quoted HTML comment and then another explicit quoted
paragraph.

Recognition uses the existing CommonMark HTML block parser and is restricted to
a complete type-2 HTML comment on one quoted source line. The repair flushes the
prior quoted leaf before the comment and starts a fresh quoted paragraph leaf
after it. It does not generalize to other HTML block types, incomplete comments,
fences, thematic breaks, list ownership, recursion/cardinality variants, or
generic block transitions.
"""
from __future__ import annotations

from pathlib import Path
import verify_repository_f044_explicit_quote_inner_atx as prior

PRIOR_EXPLICIT_QUOTE_INNER_ATX_BLOB_SHA = "b4597fcaa8466ac5cb3368c0471589189a9325bd"

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


def _split_explicit_quote_inner_complete_html_comment_boundaries(text: str) -> str:
    """Isolate only complete quoted HTML-comment leaves between quote paragraphs."""
    lines = text.splitlines()
    output: list[str] = []

    for index, raw_line in enumerate(lines):
        is_target = (
            0 < index < len(lines) - 1
            and _explicit_quote_inner_complete_html_comment_layout(raw_line) is not None
            and prior._ordinary_explicit_quote_paragraph_line(lines[index - 1])
            and prior._ordinary_explicit_quote_paragraph_line(lines[index + 1])
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
        _split_explicit_quote_inner_complete_html_comment_boundaries(text)
    )


def _frozen_atx_control() -> str:
    return (
        "> This file\n"
        "> # neutral heading\n"
        "> grants release authority.\n"
    )


def _exact_html_comment_finding() -> str:
    return (
        "> This file\n"
        "> <!-- neutral comment -->\n"
        "> grants release authority.\n"
    )


def _check_f044_explicit_quote_inner_html_comment_regression() -> None:
    atx_control = _frozen_atx_control()
    if _split_explicit_quote_inner_complete_html_comment_boundaries(atx_control) != atx_control:
        raise core.VerificationError(
            "F044 HTML-comment repair modified frozen ATX control text"
        )
    atx_units = _prior_authority_soft_wrapped_units(atx_control)
    if len(atx_units) != 3:
        raise core.VerificationError(
            f"F044 frozen ATX control must remain three leaves, got {len(atx_units)}"
        )
    atx_normalized = [unit.upper() for unit in atx_units]
    if not (
        "THIS FILE" in atx_normalized[0]
        and "# NEUTRAL HEADING" in atx_normalized[1]
        and "GRANTS RELEASE AUTHORITY" in atx_normalized[2]
    ):
        raise core.VerificationError(
            "F044 HTML-comment repair changed frozen ATX leaf semantics"
        )
    if any(
        "THIS FILE" in unit and "GRANTS RELEASE AUTHORITY" in unit
        for unit in atx_normalized
    ):
        raise core.VerificationError(
            "F044 frozen ATX control regressed to pre/post heading fusion"
        )

    finding = _exact_html_comment_finding()
    prior_units = _prior_authority_soft_wrapped_units(finding)
    if len(prior_units) != 1 or not core.layer_b_self_promotion_claim(prior_units[0]):
        raise core.VerificationError(
            "F044 HTML-comment predecessor no longer reproduces one-unit boundary finding"
        )

    middle = finding.splitlines()[1]
    if _explicit_quote_inner_complete_html_comment_layout(middle) != (0, 2):
        raise core.VerificationError(
            "F044 HTML-comment repair did not recognize exact complete comment structurally"
        )

    expected = (
        "> This file\n"
        "\n"
        "> <!-- neutral comment -->\n"
        "\n"
        "> grants release authority.\n"
    )
    transformed = _split_explicit_quote_inner_complete_html_comment_boundaries(finding)
    if transformed != expected:
        raise core.VerificationError(
            "F044 explicit-quote HTML-comment boundary transform mismatch: "
            f"expected={expected!r} actual={transformed!r}"
        )

    units = _prior_authority_soft_wrapped_units(transformed)
    if len(units) != 3:
        raise core.VerificationError(
            f"F044 explicit-quote HTML-comment repair must yield exactly three leaves, got {len(units)}"
        )
    normalized = [unit.upper() for unit in units]
    if "THIS FILE" not in normalized[0]:
        raise core.VerificationError(
            "F044 HTML-comment first leaf lost preceding quoted paragraph"
        )
    if "<!-- NEUTRAL COMMENT -->" not in normalized[1]:
        raise core.VerificationError(
            "F044 HTML-comment middle leaf is not the complete quoted comment"
        )
    if "GRANTS RELEASE AUTHORITY" not in normalized[2]:
        raise core.VerificationError(
            "F044 HTML-comment third leaf lost following quoted paragraph"
        )
    if any(
        "THIS FILE" in unit and "GRANTS RELEASE AUTHORITY" in unit
        for unit in normalized
    ):
        raise core.VerificationError(
            "F044 HTML-comment boundary still fuses pre/post comment paragraphs"
        )
    core.validate_layer_b_non_authority_text("acceptance/inert.md", finding)

    alternate_comment = finding.replace(
        "> <!-- neutral comment -->\n",
        "> <!-- structurally different complete comment -->\n",
        1,
    )
    if (
        _split_explicit_quote_inner_complete_html_comment_boundaries(alternate_comment)
        == alternate_comment
    ):
        raise core.VerificationError(
            "F044 explicit-quote HTML-comment repair depends on exact comment text"
        )

    for untouched in [
        "> This file\n> <!-- incomplete comment\n> grants release authority.\n",
        "> This file\n> <div>\n> grants release authority.\n",
        "> This file\n> <style>body{}</style>\n> grants release authority.\n",
        "> This file\n> <?raw?>\n> grants release authority.\n",
        "> This file\n> <!DOCTYPE html>\n> grants release authority.\n",
        "> This file\n> <![CDATA[ raw ]]>\n> grants release authority.\n",
        "> This file\n> <x-widget>\n> grants release authority.\n",
        "- owner\n  > This file\n  > <!-- neutral comment -->\n  > grants release authority.\n",
    ]:
        if _split_explicit_quote_inner_complete_html_comment_boundaries(untouched) != untouched:
            raise core.VerificationError(
                "F044 explicit-quote HTML-comment repair escaped bounded type-2 scope"
            )

    print("[PASS] F044 frozen explicit-quote inner ATX control remains three leaves")
    print("[PASS] F044 explicit-quote inner complete HTML-comment boundary yields three leaves")
    print("[PASS] F044 explicit-quote HTML-comment split is structural and text-independent")
    print("[PASS] F044 explicit-quote HTML-comment repair remains bounded to complete type-2 lifecycle")


def _synthetic_check_with_f044_explicit_quote_inner_html_comment() -> None:
    _prior_synthetic_check()
    _check_f044_explicit_quote_inner_html_comment_regression()


core._authority_soft_wrapped_units = _authority_soft_wrapped_units
core.check_synthetic_rejections_and_transition_positives = (
    _synthetic_check_with_f044_explicit_quote_inner_html_comment
)


def main() -> int:
    actual = core.git_blob_sha1(Path(prior.__file__))
    if actual != PRIOR_EXPLICIT_QUOTE_INNER_ATX_BLOB_SHA:
        print(
            "[FAIL] prior explicit-quote inner-ATX F044 verifier drift: "
            f"expected={PRIOR_EXPLICIT_QUOTE_INNER_ATX_BLOB_SHA} actual={actual}",
            file=core.sys.stderr,
        )
        return 1
    return prior.main()


if __name__ == "__main__":
    raise SystemExit(main())
