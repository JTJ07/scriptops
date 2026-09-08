#!/usr/bin/env python3
"""Isolated F044-D21 cross-parameter probe over exact GREEN D20.

No repair is performed. The exact D20 entrypoint is retained byte-for-byte as
`scripts/verify_repository_probe_base.py`; this wrapper adds exactly one
representative combining a continuation run of length two with three later
same-level child siblings inside the already bounded list-owned quote family.
"""
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
        "  >   - neutral child three\n"
        "  >   - grants release authority.\n"
    )
    try:
        core.validate_layer_b_non_authority_text("acceptance/inert.md", source)
    except core.VerificationError as exc:
        if "publishes forbidden self-promotion" not in str(exc):
            raise
        print(
            "[PASS] F044-D21 probe reproduces continuation-run x child-cardinality false positive"
        )
        return
    raise core.VerificationError(
        "F044-D21 probe NOT REPRODUCED: cross-parameter representative is already accepted"
    )


def _synthetic_check_with_probe() -> None:
    _prior_synthetic_check()
    _check_f044d21_probe()


core.check_synthetic_rejections_and_transition_positives = _synthetic_check_with_probe


def main() -> int:
    actual = core.git_blob_sha1(Path(prior.__file__))
    if actual != PRIOR_GREEN_D20_BLOB_SHA:
        print(
            "[FAIL] F044-D21 probe-base drift: "
            f"expected={PRIOR_GREEN_D20_BLOB_SHA} actual={actual}",
            file=core.sys.stderr,
        )
        return 1
    return prior.main()


if __name__ == "__main__":
    raise SystemExit(main())
