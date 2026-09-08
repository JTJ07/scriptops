#!/usr/bin/env python3
"""Isolated F044-D21 combined run-length/cardinality probe over GREEN D20."""
from __future__ import annotations
from pathlib import Path
import verify_repository_probe_base as prior

PRIOR_GREEN_D20_BLOB_SHA = "0d3156b954b0988672b5b183b3e1149d211f9324"
core = prior.core
_prior_synthetic_check = core.check_synthetic_rejections_and_transition_positives


def _check_f044d21_probe() -> None:
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
        print("[PASS] F044-D21 probe reproduces combined run-length/cardinality false positive")
        return
    raise core.VerificationError(
        "F044-D21 probe NOT REPRODUCED: combined representative is already accepted"
    )


def _synthetic_check_with_probe() -> None:
    _prior_synthetic_check()
    _check_f044d21_probe()

core.check_synthetic_rejections_and_transition_positives = _synthetic_check_with_probe


def main() -> int:
    actual = core.git_blob_sha1(Path(prior.__file__))
    if actual != PRIOR_GREEN_D20_BLOB_SHA:
        print(
            "[FAIL] D21 probe base drift: "
            f"expected={PRIOR_GREEN_D20_BLOB_SHA} actual={actual}",
            file=core.sys.stderr,
        )
        return 1
    return prior.main()

if __name__ == "__main__":
    raise SystemExit(main())
