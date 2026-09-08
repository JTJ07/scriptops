#!/usr/bin/env python3
"""Isolated F044-D24 list-owned later-child-position probe over exact GREEN D23.

No repair is performed. The exact D23 entrypoint is retained byte-for-byte as
`scripts/verify_repository_probe_base.py`; this wrapper adds exactly one
representative lifting the already-repaired top-level D13 target-child-position
shape into one source-column-zero outer list item owning the quote.
"""
from __future__ import annotations

from pathlib import Path
import verify_repository_probe_base as prior

PRIOR_GREEN_D23_BLOB_SHA = "595b0e461261fb56710a9e48c6865da61ef3177f"

core = prior.core
_prior_synthetic_check = core.check_synthetic_rejections_and_transition_positives


def _check_f044d24_probe() -> None:
    source = (
        "- Parent:\n"
        "  > - neutral quoted parent\n"
        "  >   - child one\n"
        "  >   - child two\n"
        "  >   - This file\n"
        "  >     target continuation\n"
        "  >   - grants release authority.\n"
    )
    try:
        core.validate_layer_b_non_authority_text("acceptance/inert.md", source)
    except core.VerificationError as exc:
        if "publishes forbidden self-promotion" not in str(exc):
            raise
        print(
            "[PASS] F044-D24 probe reproduces list-owned later-child-position false positive"
        )
        return
    raise core.VerificationError(
        "F044-D24 probe NOT REPRODUCED: list-owned D13-shaped representative is already accepted"
    )


def _synthetic_check_with_probe() -> None:
    _prior_synthetic_check()
    _check_f044d24_probe()


core.check_synthetic_rejections_and_transition_positives = _synthetic_check_with_probe


def main() -> int:
    actual = core.git_blob_sha1(Path(prior.__file__))
    if actual != PRIOR_GREEN_D23_BLOB_SHA:
        print(
            "[FAIL] F044-D24 probe-base drift: "
            f"expected={PRIOR_GREEN_D23_BLOB_SHA} actual={actual}",
            file=core.sys.stderr,
        )
        return 1
    return prior.main()


if __name__ == "__main__":
    raise SystemExit(main())
