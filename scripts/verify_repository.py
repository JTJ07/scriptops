#!/usr/bin/env python3
"""Isolated F044-D40 sixth-following-continuation probe over exact GREEN D39.

No repair is performed. The exact D39 entrypoint is retained byte-for-byte as
`scripts/verify_repository_probe_base.py`; this wrapper adds exactly one
adjacent representative where a sixth following sibling owns one ordinary
continuation line before a later same-level sibling carries promotion text.
"""
from __future__ import annotations

from pathlib import Path
import verify_repository_probe_base as prior

PRIOR_GREEN_D39_BLOB_SHA = "14a99f1bce97a08c84eb1cee2c1245af93b7fab3"

core = prior.core
_prior_synthetic_check = core.check_synthetic_rejections_and_transition_positives


def _check_f044d40_probe() -> None:
    source = prior._source(2, sixth_continuation=True)
    try:
        core.validate_layer_b_non_authority_text("acceptance/inert.md", source)
    except core.VerificationError as exc:
        if "publishes forbidden self-promotion" not in str(exc):
            raise
        print(
            "[PASS] F044-D40 probe reproduces sixth-following-continuation false positive"
        )
        return
    raise core.VerificationError(
        "F044-D40 probe expected predecessor false-positive rejection, but source passed"
    )


def _synthetic_check_with_f044d40_probe() -> None:
    _prior_synthetic_check()
    _check_f044d40_probe()


core.check_synthetic_rejections_and_transition_positives = (
    _synthetic_check_with_f044d40_probe
)


def main() -> int:
    actual = core.git_blob_sha1(Path(prior.__file__))
    if actual != PRIOR_GREEN_D39_BLOB_SHA:
        print(
            "[FAIL] F044-D40 probe base drift: "
            f"expected={PRIOR_GREEN_D39_BLOB_SHA} actual={actual}",
            file=core.sys.stderr,
        )
        return 1
    return prior.main()


if __name__ == "__main__":
    raise SystemExit(main())
