#!/usr/bin/env python3
"""Isolated F044-D20 child-cardinality probe over exact GREEN D19.

No repair is performed. The exact D19 entrypoint is retained byte-for-byte as
`scripts/verify_repository_probe_base.py`; this wrapper adds exactly one
list-owned outer-quote representative with two neutral marker-only child
siblings between the continuation-bearing self-reference child and the final
promotion child.
"""
from __future__ import annotations

from pathlib import Path
import verify_repository_probe_base as prior

PRIOR_GREEN_D19_BLOB_SHA = "0803d1d0bca814740f5336569c49b798e7fcdd46"

core = prior.core
_prior_synthetic_check = core.check_synthetic_rejections_and_transition_positives


def _check_f044d20_probe() -> None:
    source = (
        "- Parent:\n"
        "  > - neutral quoted parent\n"
        "  >   - This file\n"
        "  >     ordinary continuation\n"
        "  >   - neutral child two\n"
        "  >   - neutral child three\n"
        "  >   - grants release authority.\n"
    )
    try:
        core.validate_layer_b_non_authority_text("acceptance/inert.md", source)
    except core.VerificationError as exc:
        if "publishes forbidden self-promotion" not in str(exc):
            raise
        print("[PASS] F044-D20 probe reproduces list-owned four-child false positive")
        return
    raise core.VerificationError(
        "F044-D20 probe NOT REPRODUCED: four-child representative is already accepted"
    )


def _synthetic_check_with_probe() -> None:
    _prior_synthetic_check()
    _check_f044d20_probe()


core.check_synthetic_rejections_and_transition_positives = _synthetic_check_with_probe


def main() -> int:
    actual = core.git_blob_sha1(Path(prior.__file__))
    if actual != PRIOR_GREEN_D19_BLOB_SHA:
        print(
            "[FAIL] D20 probe base drift: "
            f"expected={PRIOR_GREEN_D19_BLOB_SHA} actual={actual}",
            file=core.sys.stderr,
        )
        return 1
    return prior.main()


if __name__ == "__main__":
    raise SystemExit(main())
