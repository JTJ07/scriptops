#!/usr/bin/env python3
"""Isolated F044-D27 list-owned tail-cardinality probe over exact GREEN D26.

No repair is performed. The exact D26 entrypoint is retained byte-for-byte as
`scripts/verify_repository_probe_base.py`; this wrapper adds exactly one
representative extending the repaired list-owned D15 shape by one additional
final same-level sibling after the promotion-bearing final child.

This is not a repeat of withdrawn top-level D16. It probes only the cross-product
with the list-owned D26 family, whose bounded repair explicitly stops at exactly
one final sibling.
"""
from __future__ import annotations

from pathlib import Path
import verify_repository_probe_base as prior

PRIOR_GREEN_D26_BLOB_SHA = "ea830bc54b9c6bc4f07905fd964539885de841c6"

core = prior.core
_prior_synthetic_check = core.check_synthetic_rejections_and_transition_positives


def _check_f044d27_probe() -> None:
    source = (
        "- Parent:\n"
        "  > - neutral quoted parent\n"
        "  >   - child one\n"
        "  >   - child two\n"
        "  >   - This file\n"
        "  >     target continuation\n"
        "  >   - neutral post-target\n"
        "  >     post-target continuation\n"
        "  >   - grants release authority.\n"
        "  >   - neutral extra final sibling\n"
    )
    try:
        core.validate_layer_b_non_authority_text("acceptance/inert.md", source)
    except core.VerificationError as exc:
        if "publishes forbidden self-promotion" not in str(exc):
            raise
        print(
            "[PASS] F044-D27 probe reproduces list-owned tail-cardinality false positive"
        )
        return
    raise core.VerificationError(
        "F044-D27 probe NOT REPRODUCED: list-owned extra-final-sibling representative is already accepted"
    )


def _synthetic_check_with_probe() -> None:
    _prior_synthetic_check()
    _check_f044d27_probe()


core.check_synthetic_rejections_and_transition_positives = _synthetic_check_with_probe


def main() -> int:
    actual = core.git_blob_sha1(Path(prior.__file__))
    if actual != PRIOR_GREEN_D26_BLOB_SHA:
        print(
            "[FAIL] F044-D27 probe-base drift: "
            f"expected={PRIOR_GREEN_D26_BLOB_SHA} actual={actual}",
            file=core.sys.stderr,
        )
        return 1
    return prior.main()


if __name__ == "__main__":
    raise SystemExit(main())
