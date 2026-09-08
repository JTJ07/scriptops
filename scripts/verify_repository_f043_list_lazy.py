#!/usr/bin/env python3
"""Bounded F043 list-lazy multiline overlay over the frozen multiline verifier.

The previous F043 multiline verifier is retained byte-for-byte at
`scripts/verify_repository_f043_multiline.py` and pinned by Git blob SHA.
This entrypoint changes only list-marker multiline definition collection so
CommonMark list-item lazy continuation may omit some or all content indentation.
F042 and F044 remain intentionally unresolved.
"""
from __future__ import annotations

from pathlib import Path
import verify_repository_f043_multiline as prior

PRIOR_F043_MULTILINE_BLOB_SHA = "c2b5a356e744be802d204ab8eaea901e76aa1219"

core = prior.core
singleline = prior.prior
_prior_synthetic_check = core.check_synthetic_rejections_and_transition_positives
_frozen_list_marker_definition = prior._try_fold_list_marker_definition


def _try_fold_list_marker_definition(
    lines: list[str], start: int
) -> tuple[int, str] | None:
    """Fold a list-owned multiline definition, including legal lazy lines.

    CommonMark list laziness may delete some or all list-content indentation
    from paragraph continuation lines. Link-reference definitions are extracted
    from the paragraph candidate, so their physical continuation lines must be
    considered after this indentation deletion as well. Structural paragraph
    interrupters remain boundaries exactly as in the frozen multiline overlay.
    """
    first = prior._LIST_LINE_RE.match(lines[start])
    layout = singleline._markdown_list_item_layout(
        lines[start], allow_deep_indent=True
    )
    if first is None or layout is None:
        return None

    first_body = first.group("body").lstrip(" \t")
    if not first_body.startswith("["):
        return None

    _, content_indent, empty_item, _ = layout
    if empty_item:
        return None

    parts = [first_body]
    best = prior._longest_valid_definition(parts)

    for index in range(start + 1, len(lines)):
        raw_line = lines[index]
        if not raw_line.strip():
            break

        relative = singleline._markdown_remove_leading_columns(
            raw_line, content_indent
        )
        if relative is None:
            # List-item laziness permits deleting some or all indentation only
            # when the resulting line is paragraph continuation text. Reuse the
            # frozen block-precedence gate before admitting such a line.
            relative = raw_line.lstrip(" \t")
        else:
            relative = relative.lstrip(" \t")

        if not relative.strip() or prior._payload_interrupts_paragraph(relative):
            break

        parts.append(relative)
        candidate = prior._longest_valid_definition(parts)
        if candidate is not None:
            best = candidate

    if best is None or best[0] <= 1:
        return None
    return best[0], first.group("prefix") + best[1]


def _check_f043_list_lazy_multiline_regressions() -> None:
    # False-positive closures: indentation may be fully or partially omitted
    # from continuation lines while the definition remains list-owned.
    for benign in [
        "- [\nThis file\n]: /url\ngrants release authority.\n",
        "- [\n This file\n ]: /url\ngrants release authority.\n",
        "- [This file]:\n/url\ngrants release authority.\n",
        "- [This file]: /url '\nmetadata\n'\ngrants release authority.\n",
        "10) [\nThis file\n]: /url\ngrants release authority.\n",
        "- Parent:\n  - [\nThis file\n]: /url\ngrants release authority.\n",
    ]:
        core.validate_layer_b_non_authority_text("acceptance/inert.md", benign)

    # Security controls: lazy folding may not allow a definition to interrupt
    # an already-open paragraph or erase authority-bearing definition metadata.
    for label, rejected in [
        (
            "F043 list-lazy multiline definition cannot interrupt item paragraph",
            "- This file\n[\nx\n]: /url\ngrants release authority.\n",
        ),
        (
            "F043 list-lazy multiline metadata remains security-relevant",
            "- [\nThis file grants release authority\n]: /url\n",
        ),
    ]:
        core.expect_failure_message(
            label,
            "publishes forbidden self-promotion",
            lambda rejected=rejected: core.validate_layer_b_non_authority_text(
                "acceptance/inert.md", rejected
            ),
        )

    folding_oracles = [
        (
            "F043 list-lazy full-indent deletion",
            "- [\nfoo\n]: /url\nbar\n",
            "- [ foo ]: /url\nbar\n",
        ),
        (
            "F043 list-lazy partial-indent deletion",
            "- [\n foo\n ]: /url\nbar\n",
            "- [ foo ]: /url\nbar\n",
        ),
        (
            "F043 list-lazy destination-next-line",
            "- [foo]:\n/url\nbar\n",
            "- [foo]: /url\nbar\n",
        ),
        (
            "F043 nested-list lazy folding",
            "- Parent:\n  - [\nfoo\n]: /url\nbar\n",
            "- Parent:\n  - [ foo ]: /url\nbar\n",
        ),
    ]
    for label, source, expected in folding_oracles:
        actual = prior._fold_multiline_link_reference_definitions(source)
        if actual != expected:
            raise core.VerificationError(
                f"{label} mismatch: expected={expected!r} actual={actual!r}"
            )

    structural_lines = "- [\nThis file\n# heading\n]: /url\ngrants release authority.\n".splitlines()
    if _try_fold_list_marker_definition(structural_lines, 0) is not None:
        raise core.VerificationError(
            "F043 list-lazy collector crossed a structural paragraph interrupter"
        )

    # Non-vacuity: the frozen collector must still reproduce the exact finding.
    finding_lines = "- [\nThis file\n]: /url\ngrants release authority.\n".splitlines()
    if _frozen_list_marker_definition(finding_lines, 0) is not None:
        raise core.VerificationError(
            "F043 list-lazy finding no longer reproduced by pinned multiline core"
        )

    print("[PASS] F043 list-lazy multiline link-reference-definition regression")


def _synthetic_check_with_f043_list_lazy() -> None:
    _prior_synthetic_check()
    _check_f043_list_lazy_multiline_regressions()


# Patch only the list-marker collector used by the frozen multiline folding pass.
prior._try_fold_list_marker_definition = _try_fold_list_marker_definition
core.check_synthetic_rejections_and_transition_positives = (
    _synthetic_check_with_f043_list_lazy
)


def main() -> int:
    actual = core.git_blob_sha1(Path(prior.__file__))
    if actual != PRIOR_F043_MULTILINE_BLOB_SHA:
        print(
            "[FAIL] F043 multiline verifier drift: "
            f"expected={PRIOR_F043_MULTILINE_BLOB_SHA} actual={actual}",
            file=core.sys.stderr,
        )
        return 1
    return prior.main()


if __name__ == "__main__":
    raise SystemExit(main())
