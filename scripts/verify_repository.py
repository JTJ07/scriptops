#!/usr/bin/env python3
"""Isolated F044-D34 still-later-following-continuation probe over exact GREEN D33.

No repair is performed. The exact D33 entrypoint is retained byte-for-byte as
`scripts/verify_repository_probe_base.py`; this wrapper adds exactly one
representative where a third following sibling owns one ordinary continuation
line before a later same-level sibling carries promotion text.
"""
from __future__ import annotations

from pathlib import Path
import verify_repository_probe_base as prior

PRIOR_GREEN_D33_BLOB_SHA = "dc0f6904ea0236f00d27367b006f08357a5eaab6"

core = prior.core
_prior_synthetic_check = core.check_synthetic_rejections_and_transition_positives


def _check_f044d34_probe() -> None:
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
        "  >   - neutral following one\n"
        "  >     following continuation one\n"
        "  >     following continuation two\n"
        "  >   - neutral following two\n"
        "  >     later continuation one\n"
        "  >     later continuation two\n"
        "  >   - neutral following three\n"
        "  >     still later continuation\n"
        "  >   - grants release authority.\n"
    )
    try:
        core.validate_layer_b_non_authority_text("acceptance/inert.md", source)
    except core.VerificationError as exc:
        if "publishes forbidden self-promotion" not in str(exc):
            raise
        print(
            "[PASS] F044-D34 probe reproduces still-later-following-continuation false positive"
        )
        return
    raise core.VerificationError(
        "F044-D34 probe NOT REPRODUCED: still-later-following-continuation representative is already accepted"
    )


def _synthetic_check_with_probe() -> None:
    _prior_synthetic_check()
    _check_f044d34_probe()


core.check_synthetic_rejections_and_transition_positives = _synthetic_check_with_probe


def main() -> int:
    actual = core.git_blob_sha1(Path(prior.__file__))
    if actual != PRIOR_GREEN_D33_BLOB_SHA:
        print(
            "[FAIL] F044-D34 probe-base drift: "
            f"expected={PRIOR_GREEN_D33_BLOB_SHA} actual={actual}",
            file=core.sys.stderr,
        )
        return 1
    return prior.main()


if __name__ == "__main__":
    raise SystemExit(main())
