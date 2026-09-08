#!/usr/bin/env python3
"""Isolated F044-D19 child-cardinality probe over exact GREEN D18.

No repair is performed. The exact D18 entrypoint is retained byte-for-byte as
`scripts/verify_repository_probe_base.py`; this wrapper adds exactly one
list-owned outer-quote representative with one additional neutral child sibling
between the continuation-bearing self-reference child and the promotion child.
"""
from __future__ import annotations

from pathlib import Path
import verify_repository_probe_base as prior

PRIOR_GREEN_D18_BLOB_SHA = "b575f659b3b22ca8d2f5fef8d8c68f295e5faa5a"

core = prior.core
_prior_synthetic_check = core.check_synthetic_rejections_and_transition_positives


def _check_f044d19_probe() -> None:
    source = (
        "- Parent:\n"
        "  > - neutral quoted parent\n"
        "  >   - This file\n"
        "  >     ordinary continuation\n"
        "  >   - neutral child two\n"
        "  >   - grants release authority.\n"
    )
    try:
        core.validate_layer_b_non_authority_text("acceptance/inert.md", source)
    except core.VerificationError as exc:
        if "publishes forbidden self-promotion" not in str(exc):
            raise
        print("[PASS] F044-D19 probe reproduces list-owned child-cardinality false positive")
        return
    raise core.VerificationError(
        "F044-D19 probe NOT REPRODUCED: additional-child representative is already accepted"
    )


def _synthetic_check_with_probe() -> None:
    _prior_synthetic_check()
    _check_f044d19_probe()


core.check_synthetic_rejections_and_transition_positives = _synthetic_check_with_probe


def main() -> int:
    actual = core.git_blob_sha1(Path(prior.__file__))
    if actual != PRIOR_GREEN_D18_BLOB_SHA:
        print(
            "[FAIL] D19 probe base drift: "
            f"expected={PRIOR_GREEN_D18_BLOB_SHA} actual={actual}",
            file=core.sys.stderr,
        )
        return 1
    return prior.main()


if __name__ == "__main__":
    raise SystemExit(main())
