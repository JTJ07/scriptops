#!/usr/bin/env python3
"""Isolated F044-D18 non-vacuity probe over exact GREEN D17.

No repair is performed. The exact D17 entrypoint is retained byte-for-byte as
`scripts/verify_repository_probe_base.py`; this wrapper runs all existing checks
and then probes only the adjacent list-owned outer-quote shape where the first
nested child owns two ordinary continuation lines before its sibling.
"""
from __future__ import annotations

from pathlib import Path
import verify_repository_probe_base as prior

PRIOR_GREEN_D17_BLOB_SHA = "bb159df7a1920b952d7a65ea741cca2460128b00"

core = prior.core
_prior_synthetic_check = core.check_synthetic_rejections_and_transition_positives


def _check_f044d18_probe() -> None:
    source = (
        "- Parent:\n"
        "  > - neutral quoted parent\n"
        "  >   - This file\n"
        "  >     continuation one\n"
        "  >     continuation two\n"
        "  >   - grants release authority.\n"
    )
    try:
        core.validate_layer_b_non_authority_text("acceptance/inert.md", source)
    except core.VerificationError as exc:
        if "publishes forbidden self-promotion" not in str(exc):
            raise
        print("[PASS] F044-D18 probe reproduces list-owned two-continuation false positive")
        return
    raise core.VerificationError(
        "F044-D18 probe NOT REPRODUCED: two-continuation representative is already accepted"
    )


def _synthetic_check_with_probe() -> None:
    _prior_synthetic_check()
    _check_f044d18_probe()


core.check_synthetic_rejections_and_transition_positives = _synthetic_check_with_probe


def main() -> int:
    actual = core.git_blob_sha1(Path(prior.__file__))
    if actual != PRIOR_GREEN_D17_BLOB_SHA:
        print(
            "[FAIL] D18 probe base drift: "
            f"expected={PRIOR_GREEN_D17_BLOB_SHA} actual={actual}",
            file=core.sys.stderr,
        )
        return 1
    return prior.main()


if __name__ == "__main__":
    raise SystemExit(main())
