#!/usr/bin/env python3
"""Read-only-equivalent F044 probe harness over the exact GREEN D15 candidate.

This isolated branch does not repair anything. It imports the exact D15 verifier
byte-for-byte, runs all of its existing checks, then asks whether one list-owned
outer-quote recursion representative is still rejected as forbidden
self-promotion. A PASS from this probe means the predecessor actually
reproduces the suspected false positive. A NOT-REPRODUCED failure means no
finding may be recorded for this representative.
"""
from __future__ import annotations

from pathlib import Path
import verify_repository_probe_base as prior

PRIOR_GREEN_D15_BLOB_SHA = "d12fcc3fbbadf52173d161b26d690e2bbb653bd2"

core = prior.core
_prior_synthetic_check = core.check_synthetic_rejections_and_transition_positives


def _check_list_owned_outer_quote_probe() -> None:
    source = (
        "- Parent:\n"
        "  > - neutral quoted parent\n"
        "  >   - This file\n"
        "  >     ordinary continuation\n"
        "  >   - grants release authority.\n"
    )
    try:
        core.validate_layer_b_non_authority_text("acceptance/inert.md", source)
    except core.VerificationError as exc:
        if "publishes forbidden self-promotion" not in str(exc):
            raise
        print("[PASS] F044 probe reproduces list-owned outer-quote false positive")
        return
    raise core.VerificationError(
        "F044 probe NOT REPRODUCED: list-owned outer quote representative is already accepted"
    )


def _synthetic_check_with_probe() -> None:
    _prior_synthetic_check()
    _check_list_owned_outer_quote_probe()


core.check_synthetic_rejections_and_transition_positives = _synthetic_check_with_probe


def main() -> int:
    actual = core.git_blob_sha1(Path(prior.__file__))
    if actual != PRIOR_GREEN_D15_BLOB_SHA:
        print(
            "[FAIL] probe base drift: "
            f"expected={PRIOR_GREEN_D15_BLOB_SHA} actual={actual}",
            file=core.sys.stderr,
        )
        return 1
    return prior.main()


if __name__ == "__main__":
    raise SystemExit(main())
