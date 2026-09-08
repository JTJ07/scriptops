#!/usr/bin/env python3
"""Isolated F044-D29 final-following-cardinality probe over exact GREEN D28.

No repair is performed. The exact D28 entrypoint is retained byte-for-byte as
`scripts/verify_repository_probe_base.py`; this wrapper adds exactly one
representative where the continued final child is followed by two consecutive
same-level final siblings instead of exactly one.
"""
from __future__ import annotations

from pathlib import Path
import verify_repository_probe_base as prior

PRIOR_GREEN_D28_BLOB_SHA = "897400e515a1bcf599cfa43901447a7ca695f7d8"

core = prior.core
_prior_synthetic_check = core.check_synthetic_rejections_and_transition_positives


def _check_f044d29_probe() -> None:
    source = (
        "- Parent:\n"
        "  > - neutral quoted parent\n"
        "  >   - child one\n"
        "  >   - child two\n"
        "  >   - This file\n"
        "  >     target continuation\n"
        "  >   - neutral post-target\n"
        "  >     post-target continuation\n"
        "  >   - neutral final one\n"
        "  >     final continuation\n"
        "  >   - grants release authority.\n"
        "  >   - neutral following two\n"
    )
    try:
        core.validate_layer_b_non_authority_text("acceptance/inert.md", source)
    except core.VerificationError as exc:
        if "publishes forbidden self-promotion" not in str(exc):
            raise
        print(
            "[PASS] F044-D29 probe reproduces continued-final following-cardinality false positive"
        )
        return
    raise core.VerificationError(
        "F044-D29 probe NOT REPRODUCED: two-following-sibling representative is already accepted"
    )


def _synthetic_check_with_probe() -> None:
    _prior_synthetic_check()
    _check_f044d29_probe()


core.check_synthetic_rejections_and_transition_positives = _synthetic_check_with_probe


def main() -> int:
    actual = core.git_blob_sha1(Path(prior.__file__))
    if actual != PRIOR_GREEN_D28_BLOB_SHA:
        print(
            "[FAIL] F044-D29 probe-base drift: "
            f"expected={PRIOR_GREEN_D28_BLOB_SHA} actual={actual}",
            file=core.sys.stderr,
        )
        return 1
    return prior.main()


if __name__ == "__main__":
    raise SystemExit(main())
