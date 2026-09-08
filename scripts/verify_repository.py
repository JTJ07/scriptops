#!/usr/bin/env python3
"""Isolated F044-D32 later-following-continuation probe over exact GREEN D31.

No repair is performed. The exact D31 entrypoint is retained byte-for-byte as
`scripts/verify_repository_probe_base.py`; this wrapper adds exactly one
representative where the first following sibling owns the D31 continuation run,
the next same-level following sibling owns one ordinary continuation line, and
a later same-level sibling carries the promotion text.
"""
from __future__ import annotations

from pathlib import Path
import verify_repository_probe_base as prior

PRIOR_GREEN_D31_BLOB_SHA = "2b3d0af9e04f79cdc6f70e08404791e0159b4ef9"

core = prior.core
_prior_synthetic_check = core.check_synthetic_rejections_and_transition_positives


def _check_f044d32_probe() -> None:
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
        "  >     later continuation\n"
        "  >   - grants release authority.\n"
    )
    try:
        core.validate_layer_b_non_authority_text("acceptance/inert.md", source)
    except core.VerificationError as exc:
        if "publishes forbidden self-promotion" not in str(exc):
            raise
        print(
            "[PASS] F044-D32 probe reproduces later-following-continuation false positive"
        )
        return
    raise core.VerificationError(
        "F044-D32 probe NOT REPRODUCED: later-following-continuation representative is already accepted"
    )


def _synthetic_check_with_probe() -> None:
    _prior_synthetic_check()
    _check_f044d32_probe()


core.check_synthetic_rejections_and_transition_positives = _synthetic_check_with_probe


def main() -> int:
    actual = core.git_blob_sha1(Path(prior.__file__))
    if actual != PRIOR_GREEN_D31_BLOB_SHA:
        print(
            "[FAIL] F044-D32 probe-base drift: "
            f"expected={PRIOR_GREEN_D31_BLOB_SHA} actual={actual}",
            file=core.sys.stderr,
        )
        return 1
    return prior.main()


if __name__ == "__main__":
    raise SystemExit(main())
