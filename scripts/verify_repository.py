#!/usr/bin/env python3
"""Isolated F044-D25 list-owned post-target-cardinality probe over exact GREEN D24.

No repair is performed. The exact D24 entrypoint is retained byte-for-byte as
`scripts/verify_repository_probe_base.py`; this wrapper adds exactly one
representative lifting the already-repaired top-level D14 post-target sibling
cardinality shape into one source-column-zero outer list item owning the quote.
"""
from __future__ import annotations

from pathlib import Path
import verify_repository_probe_base as prior

PRIOR_GREEN_D24_BLOB_SHA = "e3062750190721451548f241a8ae91acad6e6770"

core = prior.core
_prior_synthetic_check = core.check_synthetic_rejections_and_transition_positives


def _check_f044d25_probe() -> None:
    source = (
        "- Parent:\n"
        "  > - neutral quoted parent\n"
        "  >   - child one\n"
        "  >   - child two\n"
        "  >   - This file\n"
        "  >     target continuation\n"
        "  >   - grants release authority.\n"
        "  >   - neutral later sibling\n"
    )
    try:
        core.validate_layer_b_non_authority_text("acceptance/inert.md", source)
    except core.VerificationError as exc:
        if "publishes forbidden self-promotion" not in str(exc):
            raise
        print(
            "[PASS] F044-D25 probe reproduces list-owned post-target-cardinality false positive"
        )
        return
    raise core.VerificationError(
        "F044-D25 probe NOT REPRODUCED: list-owned D14-shaped representative is already accepted"
    )


def _synthetic_check_with_probe() -> None:
    _prior_synthetic_check()
    _check_f044d25_probe()


core.check_synthetic_rejections_and_transition_positives = _synthetic_check_with_probe


def main() -> int:
    actual = core.git_blob_sha1(Path(prior.__file__))
    if actual != PRIOR_GREEN_D24_BLOB_SHA:
        print(
            "[FAIL] F044-D25 probe-base drift: "
            f"expected={PRIOR_GREEN_D24_BLOB_SHA} actual={actual}",
            file=core.sys.stderr,
        )
        return 1
    return prior.main()


if __name__ == "__main__":
    raise SystemExit(main())
