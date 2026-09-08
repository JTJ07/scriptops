#!/usr/bin/env python3
"""Isolated F044-D22 two-sibling multi-continuation probe over exact GREEN D21.

No repair is performed. The exact D21 entrypoint is retained byte-for-byte as
`scripts/verify_repository_probe_base.py`; this wrapper adds exactly one
representative combining a continuation run of length two with exactly two later
same-level child siblings inside the same bounded list-owned quote family.
"""
from __future__ import annotations

from pathlib import Path
import verify_repository_probe_base as prior

PRIOR_GREEN_D21_BLOB_SHA = "d726566e683365d1071df2cd0930af88da96abd6"

core = prior.core
_prior_synthetic_check = core.check_synthetic_rejections_and_transition_positives


def _check_f044d22_probe() -> None:
    source = (
        "- Parent:\n"
        "  > - neutral quoted parent\n"
        "  >   - This file\n"
        "  >     continuation one\n"
        "  >     continuation two\n"
        "  >   - neutral child two\n"
        "  >   - grants release authority.\n"
    )
    try:
        core.validate_layer_b_non_authority_text("acceptance/inert.md", source)
    except core.VerificationError as exc:
        if "publishes forbidden self-promotion" not in str(exc):
            raise
        print(
            "[PASS] F044-D22 probe reproduces two-sibling multi-continuation false positive"
        )
        return
    raise core.VerificationError(
        "F044-D22 probe NOT REPRODUCED: representative is already accepted"
    )


def _synthetic_check_with_probe() -> None:
    _prior_synthetic_check()
    _check_f044d22_probe()


core.check_synthetic_rejections_and_transition_positives = _synthetic_check_with_probe


def main() -> int:
    actual = core.git_blob_sha1(Path(prior.__file__))
    if actual != PRIOR_GREEN_D21_BLOB_SHA:
        print(
            "[FAIL] F044-D22 probe-base drift: "
            f"expected={PRIOR_GREEN_D21_BLOB_SHA} actual={actual}",
            file=core.sys.stderr,
        )
        return 1
    return prior.main()


if __name__ == "__main__":
    raise SystemExit(main())
