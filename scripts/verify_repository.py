#!/usr/bin/env python3
"""Isolated F044-D39 fifth-following-continuation-run probe over exact GREEN D38.

No repair is performed. The exact D38 entrypoint is retained byte-for-byte as
`scripts/verify_repository_probe_base.py`; this wrapper adds exactly one
adjacent representative where the fifth following sibling owns two ordinary
continuation lines before a later same-level sibling carries promotion text.
"""
from __future__ import annotations

from pathlib import Path
import verify_repository_probe_base as prior

PRIOR_GREEN_D38_BLOB_SHA = "94f506fd07113733438a25a11ab625ede6274806"

core = prior.core
_prior_synthetic_check = core.check_synthetic_rejections_and_transition_positives


def _check_f044d39_probe() -> None:
    source = prior._source(2)
    try:
        core.validate_layer_b_non_authority_text("acceptance/inert.md", source)
    except core.VerificationError as exc:
        if "publishes forbidden self-promotion" not in str(exc):
            raise
        print(
            "[PASS] F044-D39 probe reproduces fifth-following-continuation-run false positive"
        )
        return
    raise core.VerificationError(
        "F044-D39 probe expected predecessor false-positive rejection, but source passed"
    )


def _synthetic_check_with_f044d39_probe() -> None:
    _prior_synthetic_check()
    _check_f044d39_probe()


core.check_synthetic_rejections_and_transition_positives = (
    _synthetic_check_with_f044d39_probe
)


def main() -> int:
    actual = core.git_blob_sha1(Path(prior.__file__))
    if actual != PRIOR_GREEN_D38_BLOB_SHA:
        print(
            "[FAIL] F044-D39 probe base drift: "
            f"expected={PRIOR_GREEN_D38_BLOB_SHA} actual={actual}",
            file=core.sys.stderr,
        )
        return 1
    return prior.main()


if __name__ == "__main__":
    raise SystemExit(main())
