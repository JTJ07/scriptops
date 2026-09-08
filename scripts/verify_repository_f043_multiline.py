#!/usr/bin/env python3
"""Bounded F043 multiline overlay over the frozen single-line F043 verifier.

The previous F043 verifier is retained byte-for-byte at
`scripts/verify_repository_f043_singleline.py` and pinned by Git blob SHA.
This entrypoint adds only CommonMark §4.7 multiline link-reference-definition
candidate folding before the already-reviewed single-line F043 parser runs.
F042 and F044 remain intentionally unresolved.
"""
from __future__ import annotations

from pathlib import Path
import re
import verify_repository_f043_singleline as prior

PRIOR_F043_SINGLELINE_BLOB_SHA = "61bf107ad59da33a6576032d341b41c538d0453a"

core = prior.core
_prior_soft_wrapped_units = prior._authority_soft_wrapped_units
_prior_synthetic_check = core.check_synthetic_rejections_and_transition_positives

_QUOTE_LINE_RE = re.compile(r"^(?P<prefix> {0,3}>[ \t]?)(?P<body>.*)$")
_LIST_LINE_RE = re.compile(
    r"^(?P<prefix>[ \t]*(?:[-+*]|[0-9]{1,9}[.)])[ \t]+)(?P<body>.*)$"
)


def _leading_whitespace(raw_line: str) -> str:
    match = re.match(r"^[ \t]*", raw_line)
    return match.group(0) if match is not None else ""


def _normalized_definition_candidate(parts: list[str]) -> str:
    """Collapse physical definition lines without dropping security-visible text."""
    return " ".join(part.strip() for part in parts)


def _longest_valid_definition(parts: list[str]) -> tuple[int, str] | None:
    """Return the longest prefix that is a valid prior single-line definition.

    Longest-prefix selection matters because a destination-only definition may
    legally acquire a title on the next physical line (CommonMark examples 193,
    195 and 217), and a title itself may span multiple nonblank lines.
    """
    best: tuple[int, str] | None = None
    for count in range(1, len(parts) + 1):
        candidate = _normalized_definition_candidate(parts[:count])
        if prior._markdown_link_reference_definition_layout(candidate) is not None:
            best = (count, candidate)
    return best


def _payload_interrupts_paragraph(payload: str) -> bool:
    """Mirror frozen block precedence while collecting a paragraph candidate."""
    if not payload.strip():
        return True

    quote = prior._markdown_block_quote_layout(payload)
    if quote is not None and quote[0] <= 3:
        return True

    fence = prior._markdown_fenced_code_opening_layout(payload)
    if fence is not None and fence[0] <= 3:
        return True

    html = prior._markdown_html_block_start_layout(payload)
    if html is not None and html[0] <= 3:
        return True

    atx = prior._markdown_atx_heading_layout(payload)
    if atx is not None and atx <= 3:
        return True

    thematic = prior._markdown_thematic_break_layout(payload)
    if thematic is not None and thematic[0] <= 3:
        return True

    setext = prior._markdown_setext_heading_underline_layout(payload)
    if setext is not None and setext[0] <= 3:
        return True

    list_item = prior._markdown_list_item_layout(payload)
    if list_item is not None and list_item[3]:
        return True

    return False


def _try_fold_quoted_definition(
    lines: list[str], start: int
) -> tuple[int, str] | None:
    first = _QUOTE_LINE_RE.match(lines[start])
    if first is None:
        return None
    first_body = first.group("body").lstrip(" \t")
    if not first_body.startswith("["):
        return None

    parts = [first_body]
    best = _longest_valid_definition(parts)

    for index in range(start + 1, len(lines)):
        match = _QUOTE_LINE_RE.match(lines[index])
        if match is None:
            break
        body = match.group("body").lstrip(" \t")
        if not body.strip() or _payload_interrupts_paragraph(body):
            break
        parts.append(body)
        candidate = _longest_valid_definition(parts)
        if candidate is not None:
            best = candidate

    if best is None or best[0] <= 1:
        return None
    return best[0], first.group("prefix") + best[1]


def _try_fold_list_marker_definition(
    lines: list[str], start: int
) -> tuple[int, str] | None:
    first = _LIST_LINE_RE.match(lines[start])
    layout = prior._markdown_list_item_layout(lines[start], allow_deep_indent=True)
    if first is None or layout is None:
        return None

    first_body = first.group("body").lstrip(" \t")
    if not first_body.startswith("["):
        return None

    _, content_indent, empty_item, _ = layout
    if empty_item:
        return None

    parts = [first_body]
    best = _longest_valid_definition(parts)

    for index in range(start + 1, len(lines)):
        if not lines[index].strip():
            break
        relative = prior._markdown_remove_leading_columns(lines[index], content_indent)
        if relative is None:
            break
        relative = relative.lstrip(" \t")
        if not relative.strip() or _payload_interrupts_paragraph(relative):
            break
        parts.append(relative)
        candidate = _longest_valid_definition(parts)
        if candidate is not None:
            best = candidate

    if best is None or best[0] <= 1:
        return None
    return best[0], first.group("prefix") + best[1]


def _try_fold_plain_definition(
    lines: list[str], start: int
) -> tuple[int, str] | None:
    prefix = _leading_whitespace(lines[start])
    first_body = lines[start][len(prefix) :]
    if not first_body.startswith("["):
        return None

    parts = [first_body]
    best = _longest_valid_definition(parts)

    for index in range(start + 1, len(lines)):
        raw_line = lines[index]
        if not raw_line.strip():
            break

        # A new explicit container belongs to block structure, not to this
        # plain paragraph candidate. Direct quote/list multiline definitions
        # are handled by their dedicated adapters above.
        if _QUOTE_LINE_RE.match(raw_line) is not None:
            break
        if _LIST_LINE_RE.match(raw_line) is not None:
            break

        body = raw_line.lstrip(" \t")
        if _payload_interrupts_paragraph(body):
            break
        parts.append(body)
        candidate = _longest_valid_definition(parts)
        if candidate is not None:
            best = candidate

    if best is None or best[0] <= 1:
        return None
    return best[0], prefix + best[1]


def _fold_multiline_link_reference_definitions(text: str) -> str:
    """Fold only confirmed multiline §4.7 candidates to one physical line.

    The frozen single-line F043 parser still decides whether the folded line is
    extractable in its actual block/list/quote state. Thus folding does not make
    a definition capable of interrupting an already-open paragraph and does not
    alter literal fenced/HTML/indented-code handling.
    """
    lines = text.splitlines()
    output: list[str] = []
    index = 0

    while index < len(lines):
        folded = (
            _try_fold_quoted_definition(lines, index)
            or _try_fold_list_marker_definition(lines, index)
            or _try_fold_plain_definition(lines, index)
        )
        if folded is None:
            output.append(lines[index])
            index += 1
            continue

        consumed, folded_line = folded
        output.append(folded_line)
        index += consumed

    result = "\n".join(output)
    if text.endswith(("\n", "\r")):
        result += "\n"
    return result


def _authority_soft_wrapped_units(text: str) -> list[str]:
    return _prior_soft_wrapped_units(_fold_multiline_link_reference_definitions(text))


def _check_f043_multiline_regressions() -> None:
    # False-positive closures: all self-reference text belongs to definition
    # metadata while the later promotion belongs to a distinct paragraph.
    for benign in [
        "[\nThis file\n]: /url\ngrants release authority.\n",
        "[This file]:\n/url\ngrants release authority.\n",
        "[This file]:\n<my url>\n'title'\ngrants release authority.\n",
        "[This file]: /url '\nmetadata\nline two\n'\ngrants release authority.\n",
        "   [This file]:\n      /url\n           'metadata'\ngrants release authority.\n",
        "[This file]: /a\n[x]: /b\n  'metadata'\ngrants release authority.\n",
        "- [\n  This file\n  ]: /url\n  grants release authority.\n",
        "- Parent:\n  - [\n    This file\n    ]: /url\n    grants release authority.\n",
        "> [\n> This file\n> ]: /url\n> grants release authority.\n",
        # CommonMark example 210 shape: invalid would-be title text after a
        # complete destination is a new paragraph, not part of the definition.
        "[This file]: /url\n\"title\" ok\ngrants release authority.\n",
    ]:
        core.validate_layer_b_non_authority_text("acceptance/inert.md", benign)

    # Security controls: folding may not erase metadata authority or create a
    # paragraph-interruption bypass.
    for label, rejected in [
        (
            "F043 multiline definition metadata remains security-relevant",
            "[\nThis file grants release authority\n]: /url\n",
        ),
        (
            "F043 multiline title remains in definition authority unit",
            "[This file]: /url '\ngrants release authority\n'\n",
        ),
        (
            "F043 multiline definition cannot interrupt top-level paragraph",
            "This file\n[\nx\n]: /url\ngrants release authority.\n",
        ),
        (
            "F043 multiline definition cannot interrupt list paragraph",
            "- This file\n  [\n  x\n  ]: /url\n  grants release authority.\n",
        ),
        (
            "F043 multiline definition cannot interrupt quoted paragraph",
            "> This file\n> [\n> x\n> ]: /url\n> grants release authority.\n",
        ),
    ]:
        core.expect_failure_message(
            label,
            "publishes forbidden self-promotion",
            lambda rejected=rejected: core.validate_layer_b_non_authority_text(
                "acceptance/inert.md", rejected
            ),
        )

    # Structural folding oracles. These exercise the exact normative families
    # that escaped the previous single-physical-line recognizer.
    folding_oracles = [
        (
            "F043 Example-208 label folding",
            "[\nfoo\n]: /url\nbar\n",
            "[ foo ]: /url\nbar\n",
        ),
        (
            "F043 destination-next-line folding",
            "[foo]:\n/url\nbar\n",
            "[foo]: /url\nbar\n",
        ),
        (
            "F043 multiline-title folding",
            "[foo]: /url '\ntitle\nline2\n'\nbar\n",
            "[foo]: /url ' title line2 '\nbar\n",
        ),
        (
            "F043 list-container folding",
            "- [\n  foo\n  ]: /url\n  bar\n",
            "- [ foo ]: /url\n  bar\n",
        ),
        (
            "F043 quote-container folding",
            "> [\n> foo\n> ]: /url\n> bar\n",
            "> [ foo ]: /url\n> bar\n",
        ),
    ]
    for label, source, expected in folding_oracles:
        actual = _fold_multiline_link_reference_definitions(source)
        if actual != expected:
            raise core.VerificationError(
                f"{label} mismatch: expected={expected!r} actual={actual!r}"
            )

    print("[PASS] F043 multiline CommonMark link-reference-definition regression")


def _synthetic_check_with_f043_multiline() -> None:
    _prior_synthetic_check()
    _check_f043_multiline_regressions()


# Patch only the same parser seam already used by the prior F043 overlay.
core._authority_soft_wrapped_units = _authority_soft_wrapped_units
core.check_synthetic_rejections_and_transition_positives = (
    _synthetic_check_with_f043_multiline
)


def main() -> int:
    actual = core.git_blob_sha1(Path(prior.__file__))
    if actual != PRIOR_F043_SINGLELINE_BLOB_SHA:
        print(
            "[FAIL] F043 single-line verifier drift: "
            f"expected={PRIOR_F043_SINGLELINE_BLOB_SHA} actual={actual}",
            file=core.sys.stderr,
        )
        return 1
    return prior.main()


if __name__ == "__main__":
    raise SystemExit(main())
