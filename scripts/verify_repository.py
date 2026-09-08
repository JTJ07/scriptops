#!/usr/bin/env python3
"""Isolated F044-D37 fourth-following-continuation-run probe over exact GREEN D36.

No repair is performed. The exact D36 entrypoint is retained byte-for-byte as
`scripts/verify_repository_probe_base.py`; this wrapper adds exactly one
representative where the fourth following sibling owns two ordinary continuation
lines before a later same-level sibling carries promotion text.
"""
from __future__ import annotations

from pathlib import Path
import verify_repository_probe_base as prior

PRIOR_GREEN_D36_BLOB_SHA = "b4ef7f415b245f57fb04042e860802f6825e4988"

core = prior.core
_prior_synthetic_check = core.check_synthetic_rejections_and_transition_positives


def _check_f044d37_probe() -> None:
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
        "  >     still later continuation one\n"
        "  >     still later continuation two\n"
        "  >   - neutral following four\n"
        "  >     fourth continuation one\n"
        "  >     fourth continuation two\n"
        "  >   - grants release authority.\n"
    )
    try:
        core.validate_layer_b_non_authority_text("acceptance/inert.md", source)
    except core.VerificationError as exc:
        if "publishes forbidden self-promotion" not in str(exc):
            raise
        print(
            "[PASS] F044-D37 probe reproduces fourth-following-continuation-run false positive"
        )
        return
    raise core.VerificationError(
        "F044-D37 probe NOT REPRODUCED: fourth-following-continuation-run representative is already accepted"
    )


def _synthetic_check_with_probe() -> None:
    _prior_synthetic_check()
    _check_f044d37_probe()


core.check_synthetic_rejections_and_transition_positives = _synthetic_check_with_probe


def main() -> int:
    actual = core.git_blob_sha1(Path(prior.__file__))
    if actual != PRIOR_GREEN_D36_BLOB_SHA:
        print(
            "[FAIL] F044-D37 probe-base drift: "
            f"expected={PRIOR_GREEN_D36_BLOB_SHA} actual={actual}",
            file=core.sys.stderr,
        )
        return 1
    return prior.main()


if __name__ == "__main__":
    raise SystemExit(main())
