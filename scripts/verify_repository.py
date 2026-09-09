#!/usr/bin/env python3
"""Bounded F044 explicit-quote inner-ATX block-leaf boundary overlay.

The repaired multiple-quoted-parent F044 verifier is retained byte-for-byte at
`scripts/verify_repository_f044_multiple_quoted_parents.py` and pinned by Git
blob SHA. This overlay changes only one lifecycle boundary: a source-column-zero
explicit block quote whose current quoted paragraph is followed by an explicit
quoted ATX heading and then another explicit quoted paragraph.

The heading is recognized through the existing CommonMark ATX parser. The
repair flushes the prior quoted leaf before the heading and starts a fresh quoted
leaf after it. It does not generalize to fences, HTML, thematic breaks, list
ownership, recursion/cardinality variants, or generic block transitions.
"""
from __future__ import annotations

from pathlib import Path
import verify_repository_f044_multiple_quoted_parents as prior

PRIOR_MULTIPLE_QUOTED_PARENTS_BLOB_SHA = "88bce47c461836cb6db5452e2de02fa5f50630e3"

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


def _split_explicit_quote_inner_atx_boundaries(text: str) -> str:
    """Isolate only quoted ATX leaves between quoted paragraph leaves."""
    lines = text.splitlines()
    output: list[str] = []

    for index, raw_line in enumerate(lines):
        is_target = (
            0 < index < len(lines) - 1
            and _explicit_quote_inner_atx_layout(raw_line) is not None
            and _ordinary_explicit_quote_paragraph_line(lines[index - 1])
            and _ordinary_explicit_quote_paragraph_line(lines[index + 1])
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
        _split_explicit_quote_inner_atx_boundaries(text)
    )


def _control_ordinary_continuation() -> str:
    return (
        "> This file\n"
        "> ordinary continuation\n"
        "> grants release authority.\n"
    )


def _exact_atx_finding() -> str:
    return (
        "> This file\n"
        "> # neutral heading\n"
        "> grants release authority.\n"
    )


def _check_f044_explicit_quote_inner_atx_regression() -> None:
    control = _control_ordinary_continuation()
    if _split_explicit_quote_inner_atx_boundaries(control) != control:
        raise core.VerificationError(
            "F044 explicit-quote ATX repair modified ordinary continuation control"
        )
    control_units = _prior_authority_soft_wrapped_units(control)
    if len(control_units) != 1:
        raise core.VerificationError(
            f"F044 explicit-quote ordinary continuation control must remain one unit, got {len(control_units)}"
        )
    if not core.layer_b_self_promotion_claim(control_units[0]):
        raise core.VerificationError(
            "F044 explicit-quote ordinary continuation control no longer remains one joined claim unit"
        )

    finding = _exact_atx_finding()
    prior_units = _prior_authority_soft_wrapped_units(finding)
    if len(prior_units) != 1 or not core.layer_b_self_promotion_claim(prior_units[0]):
        raise core.VerificationError(
            "F044 explicit-quote ATX predecessor no longer reproduces one-unit boundary finding"
        )

    middle = finding.splitlines()[1]
    if _explicit_quote_inner_atx_layout(middle) is None:
        raise core.VerificationError(
            "F044 explicit-quote ATX repair did not recognize the exact heading structurally"
        )

    expected = (
        "> This file\n"
        "\n"
        "> # neutral heading\n"
        "\n"
        "> grants release authority.\n"
    )
    transformed = _split_explicit_quote_inner_atx_boundaries(finding)
    if transformed != expected:
        raise core.VerificationError(
            "F044 explicit-quote ATX boundary transform mismatch: "
            f"expected={expected!r} actual={transformed!r}"
        )

    units = _prior_authority_soft_wrapped_units(transformed)
    if len(units) != 3:
        raise core.VerificationError(
            f"F044 explicit-quote ATX repair must yield exactly three leaves, got {len(units)}"
        )
    normalized = [unit.upper() for unit in units]
    if "THIS FILE" not in normalized[0]:
        raise core.VerificationError(
            "F044 explicit-quote ATX first leaf lost the preceding quoted paragraph"
        )
    if "# NEUTRAL HEADING" not in normalized[1]:
        raise core.VerificationError(
            "F044 explicit-quote ATX middle leaf is not the quoted heading"
        )
    if "GRANTS RELEASE AUTHORITY" not in normalized[2]:
        raise core.VerificationError(
            "F044 explicit-quote ATX third leaf lost the following quoted paragraph"
        )
    if any(
        "THIS FILE" in unit and "GRANTS RELEASE AUTHORITY" in unit
        for unit in normalized
    ):
        raise core.VerificationError(
            "F044 explicit-quote ATX boundary still fuses pre/post heading paragraphs"
        )
    core.validate_layer_b_non_authority_text("acceptance/inert.md", finding)

    alternate_heading = finding.replace(
        "> # neutral heading\n",
        "> ###### structurally different heading\n",
        1,
    )
    if _split_explicit_quote_inner_atx_boundaries(alternate_heading) == alternate_heading:
        raise core.VerificationError(
            "F044 explicit-quote ATX repair depends on the exact heading text"
        )

    for untouched in [
        "> This file\n> ***\n> grants release authority.\n",
        "> This file\n> ```\n> grants release authority.\n",
        "> This file\n> <div>\n> grants release authority.\n",
        "- owner\n  > This file\n  > # neutral heading\n  > grants release authority.\n",
    ]:
        if _split_explicit_quote_inner_atx_boundaries(untouched) != untouched:
            raise core.VerificationError(
                "F044 explicit-quote ATX repair escaped its bounded block-transition scope"
            )

    print("[PASS] F044 explicit-quote ordinary continuation control remains one unit")
    print("[PASS] F044 explicit-quote inner ATX boundary yields three block leaves")
    print("[PASS] F044 explicit-quote inner ATX split is structural and text-independent")
    print("[PASS] F044 explicit-quote inner ATX repair remains bounded to ATX lifecycle")


def _synthetic_check_with_f044_explicit_quote_inner_atx() -> None:
    _prior_synthetic_check()
    _check_f044_explicit_quote_inner_atx_regression()


core._authority_soft_wrapped_units = _authority_soft_wrapped_units
core.check_synthetic_rejections_and_transition_positives = (
    _synthetic_check_with_f044_explicit_quote_inner_atx
)


def main() -> int:
    actual = core.git_blob_sha1(Path(prior.__file__))
    if actual != PRIOR_MULTIPLE_QUOTED_PARENTS_BLOB_SHA:
        print(
            "[FAIL] prior multiple-quoted-parent F044 verifier drift: "
            f"expected={PRIOR_MULTIPLE_QUOTED_PARENTS_BLOB_SHA} actual={actual}",
            file=core.sys.stderr,
        )
        return 1
    return prior.main()


if __name__ == "__main__":
    raise SystemExit(main())
