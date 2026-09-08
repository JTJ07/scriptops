#!/usr/bin/env python3
"""Deterministic offline ScriptOps repository verification.

This verifier implements the X1B-FRAME two-layer closed-world authority model.
It verifies checkout-local coherence only. It never infers remote main,
deployment, release, or active-product remediation from the checkout.

F006 repair note: the same real runtime-profile validation path accepts both
recognized local transition profiles while the published active-product state
remains CURRENTNESS_UNESTABLISHED. Unknown/mixed profiles fail closed.

F008 repair note: Main_Theme Human-authorship promotion is rejected on the
real fenced document, and R14 verifies the intended rejection reason.

F009 repair note: Layer-B path denial is backed by a self-promotion validator
that rejects self-referential authority claims beyond the legacy exact-string
marker list. Representative free-form claims are exercised non-vacuously.

F010 repair note: ordinary inert technical wording such as effect-method
binding is not itself an authority-promotion verb.

F011 repair note: clear local negation around an authority-promotion phrase is
recognized structurally rather than only through a few exact negation strings.

F012 repair note: negation/currentness context is evaluated for each promotion
inside its local conjunction segment so one negative assertion cannot mask a
distinct positive self-promotion in the same clause.

F013 repair note: comma-separated/asydetic clause boundaries reset local
negation scope before a later authority promotion is evaluated.

F014 repair note: colon and explicit dash-style clause boundaries also reset
local negation scope without treating ordinary internal hyphens as separators.

F015 repair note: a later independent self-reference starts a fresh local
negation subject scope, so unenumerated delimiters cannot let an earlier
negative authority assertion mask a later positive self-promotion.

F016 repair note: fragment-local checks are backed by a whole-line normalized
self-promotion check, so punctuation or parenthetical splitting cannot sever a
self-referential subject from its positive authority predicate.

F017 repair note: physical Markdown soft wraps are folded into logical
authority units before parsing, so a line break cannot separate a
self-referential subject from its positive authority predicate.

F018 repair note: a physical Markdown newline is never treated as a security
boundary merely because the preceding line ends in sentence punctuation;
nonblank lines are folded by paragraph before authority parsing so ellipses,
abbreviations, or other false sentence tails cannot sever subject/predicate.

F019 repair note: blank lines are not security boundaries inside one Markdown
list item; indented continuation paragraphs remain folded with that item, while
sibling list items and dedented paragraphs start fresh authority units.

F020 repair note: list parsing tracks the active nested item path. Parent
context is inherited by descendants, but sibling items at any nesting depth
emit separate authority units so one sibling cannot donate a self-reference
to another sibling's promotion.

F021 repair note: deep list-marker recognition is context-aware. Top-level
Markdown list markers still require at most three leading columns, while an
active list path may recognize nested markers at four or more columns. This
closes deep-sibling collapsing without reclassifying standalone indented code.

F022 repair note: after a blank line, list-path ownership is resolved before
deep marker recognition. A line whose indentation leaves the current leaf is
first reattached to the nearest owning ancestor (or to ordinary paragraph
text); only then may a four-plus-column marker be interpreted as a nested list
item. This prevents a wide ordered item from absorbing a separate indented
code-like block while preserving valid deep descendants and continuations.

F023 repair note: marker-only empty bullet/ordered items are recognized as
real list-item boundaries, including nested siblings, but they may not
interrupt an active ordinary paragraph. This closes stale-frame absorption
after an empty sibling without creating a subject/predicate bypass through
an otherwise-invalid empty-marker paragraph interruption.

F024 repair note: an empty list item starts with a blank line even when its
marker line carries trailing spaces or tabs. Its ownership indentation is
therefore marker width plus one, not the physical trailing-whitespace width,
so same-item paragraphs cannot be split by whitespace-inflated content indent.

F025 repair note: an ordered list may interrupt an active ordinary paragraph
only when its start number is one. Non-one ordered markers remain paragraph
continuation there, but keep normal list-item semantics inside an active list.

F026 repair note: CommonMark ordered-list markers use ASCII digits `0-9` only.
Unicode decimal-digit lookalikes therefore remain ordinary Markdown text and
cannot create false list boundaries that split one authority claim into
separate security units.

F027 repair note: when a nonempty list item begins with an indented code
block, CommonMark treats post-marker whitespace beyond four columns as code
indentation rather than item-ownership indentation. The owning item therefore
uses marker width plus one so later same-item blocks cannot be split from the
initial code block by a whitespace-inflated ownership threshold.

F028 repair note: a non-one ordered-looking line inside an active list-item
paragraph remains lazy continuation when it cannot interrupt that paragraph.

F029 repair note: a dedented marker that resolves to an active ancestor list
level closes descendant frames and starts a fresh structural sibling path.

F030 repair note: a marker at an established structural level is a boundary
even when list family, bullet character, or ordered delimiter changes.

F031 repair note: ordinary lazy paragraph continuation may lose list-item
indentation. Nonblank indentation alone therefore never forces ownership
unwind; structural marker resolution is performed before paragraph-interrupt
semantics, while blank-line ownership handling remains fail-closed.

F032 repair note: CommonMark thematic breaks are resolved before list-marker
parsing. A thematic break outside the active list-item ownership path closes
that path, while an owned unambiguous thematic break forces the next line to
re-resolve ownership instead of borrowing F031 lazy-continuation semantics.
Dash-only current-leaf setext candidates keep setext precedence.

F033 repair note: top-level thematic-break syntax is also resolved as a block
boundary. A valid 0-3-column thematic marker flushes the current ordinary
paragraph before later text is folded; dash-only top-level setext underlines
likewise terminate that paragraph security unit.

F034 repair note: CommonMark ATX headings are resolved as block boundaries
before list-marker and lazy-continuation handling. Top-level headings terminate
ordinary paragraphs; owned headings remain in their list-item security context
while later dedented text must re-resolve ownership.

F035 repair note: CommonMark block quotes are resolved as containers before
ordinary paragraph fallback. Top-level quote openers interrupt prior paragraphs;
quoted paragraph continuation may lazily omit `>`, while list-owned quotes keep
the owning list-item security context.

F036 repair note: CommonMark fenced code blocks are resolved as leaf-block
boundaries before ordinary paragraph/list lazy fallback. Top-level fences
interrupt prior paragraphs, fenced literal payload is not reparsed as Markdown,
and list-owned fences keep only their owning list-item security context.

F037 repair note: CommonMark setext `=` underlines terminate an open paragraph
as a heading boundary. Empty/invalid underline lookalikes remain text, explicit
quoted underlines end quote-paragraph laziness, and current-list ownership is
re-resolved without changing the existing dash/thematic precedence.

F038 repair note: CommonMark HTML block types 1-6 interrupt paragraphs and
retain literal block contents until their normative end condition or container
end. Type 7 remains non-interrupting; this repair is not a generic HTML parser.

F039 repair note: complete CommonMark type-7 HTML tags start literal raw blocks
only when no paragraph is already open. Type 7 ends at a blank line/container/
EOF and suppresses Markdown block markers while its raw block remains active.

F040 repair note: CommonMark indented code is tracked as a literal leaf block.
It cannot interrupt an open paragraph; dedented nonblank text ends the code
block and is reprocessed without borrowing paragraph-only lazy continuation.

F041 repair note: top-level block quotes track quoted indented-code leaves. A
quoted nonblank dedent ends that code leaf before a new quoted paragraph starts,
while indentation still cannot interrupt an already-open quoted paragraph.
"""
from __future__ import annotations

import hashlib
import re
import sys
from pathlib import Path
from typing import Callable, Iterable

ROOT = Path(__file__).resolve().parents[1]

CURRENT_BOOTSTRAP = {
    "README.md",
    "PROJECT_STATE.md",
    "HANDOFF.md",
}

REGISTRY_ENTRIES = [
    ("README.md", "CURRENT_BOOTSTRAP_AUTHORITY"),
    ("PROJECT_STATE.md", "CURRENT_BOOTSTRAP_AUTHORITY"),
    ("HANDOFF.md", "CURRENT_BOOTSTRAP_AUTHORITY"),
    ("DECISION_LOG.md", "DECISION_PROVENANCE_ONLY"),
    ("RECONSTRUCTION_REPORT.md", "HISTORICAL_RECONSTRUCTION_PROVENANCE_ONLY"),
    ("SOURCES.md", "HISTORICAL_RECONSTRUCTION_PROVENANCE_ONLY"),
    ("SOURCE_AUDIT_SUMMARY.md", "HISTORICAL_RECONSTRUCTION_PROVENANCE_ONLY"),
    ("SOURCE_MANIFEST.md", "HISTORICAL_RECONSTRUCTION_PROVENANCE_ONLY"),
    ("sources/Decision_Summary_Current_State.md", "HISTORICAL_PRODUCT_GOVERNANCE_PROVENANCE_ONLY"),
    ("sources/RC1_SCOPE_LOCK.md", "HISTORICAL_PRODUCT_GOVERNANCE_PROVENANCE_ONLY"),
    ("sources/ScriptOps_Main_Theme_Summary.md", "HISTORICAL_PRODUCT_GOVERNANCE_PROVENANCE_ONLY"),
    ("CODEX_START.md", "PRE_FENCED_NONAUTHORITY_PROVENANCE"),
    ("IDEA_ARCHIVE.md", "PRE_FENCED_NONAUTHORITY_PROVENANCE"),
]

FROZEN_REGISTRY = {path for path, _ in REGISTRY_ENTRIES}

LAYER_B_PREFIXES = (
    "analysis/",
    "continuity/",
    "evidence/",
    "acceptance/",
    "sources/prototype/",
    "legacy/",
    "phase6/",
    "tests/",
    ".github/",
    "scripts/",
)

EXPECTED_FIELDS = {
    "X1B_RESEARCH_CLOSURE": "CLOSED",
    "X1B_ACTIVE_PRODUCT_REMEDIATION_ASSERTION": "CURRENTNESS_UNESTABLISHED",
    "X1B_ACTIVE_PRODUCT_ASSERTION_AUTHORITY": "EXTERNAL_CURRENTNESS_REBIND_REQUIRED",
    "X1B_ACTIVE_PRODUCT_ASSERTION_EVIDENCE": "NONE_ACCEPTED_FOR_THIS_STATUS_PUBLICATION",
    "X1B_REVIEWED_REMEDIATION_PROVENANCE": "PR #35 / REVIEWED HEAD 7c40a92165714023743e91c63b5b11b102fadd92 / UNMERGED",
    "X1B_CURRENT_AUTHORITY_BOOTSTRAP": "README.md -> PROJECT_STATE.md -> HANDOFF.md",
    "X1B_AUTHORITY_MODEL": "TWO_LAYER_CLOSED_WORLD_V1",
}

PROVENANCE_MARKERS = {
    "DECISION_LOG.md": [
        "DECISION_PROVENANCE_ONLY",
        "generic Human approval",
        "DEC-SO-010",
        "DEC-SO-011",
    ],
    "SOURCE_MANIFEST.md": [
        "HISTORICAL_RECONSTRUCTION_PROVENANCE_ONLY",
        "SOURCE_MANIFEST CANONICAL LABEL != CURRENT X1B AUTHORITY",
        "PATH-CLASS DENIAL != REGISTRY MEMBERSHIP",
    ],
    "SOURCES.md": [
        "HISTORICAL_RECONSTRUCTION_PROVENANCE_ONLY",
        "SOURCE_MANIFEST canonical label != current X1B authority",
        "Decision_Summary_Current_State filename != current X1B authority",
        "historical ACCESS CHECK gap != current next action",
    ],
    "SOURCE_AUDIT_SUMMARY.md": [
        "HISTORICAL_RECONSTRUCTION_PROVENANCE_ONLY",
        "not current X1B HumanDecision authorship evidence",
    ],
    "RECONSTRUCTION_REPORT.md": [
        "HISTORICAL_RECONSTRUCTION_PROVENANCE_ONLY",
        "OLD NEXT STEP != CURRENT NEXT ACTION",
        "HISTORICAL HUMAN APPROVAL != X1B HumanDecision AUTHORSHIP EVIDENCE",
    ],
    "sources/Decision_Summary_Current_State.md": [
        "HISTORICAL_PRODUCT_GOVERNANCE_PROVENANCE_ONLY",
        "filename word `Current` does not grant current authority",
        "GENERIC HUMAN APPROVAL",
        "X1B HumanDecision AUTHORSHIP EVIDENCE",
    ],
    "sources/RC1_SCOPE_LOCK.md": [
        "HISTORICAL_PRODUCT_GOVERNANCE_PROVENANCE_ONLY",
        "GENERIC HUMAN DECISION IN HISTORICAL RC1",
        "X1B HumanDecision AUTHORSHIP EVIDENCE",
    ],
    "sources/ScriptOps_Main_Theme_Summary.md": [
        "HISTORICAL_PRODUCT_GOVERNANCE_PROVENANCE_ONLY",
        "PRODUCT VISION / GENERIC HUMAN APPROVAL",
        "X1B HumanDecision AUTHORSHIP EVIDENCE",
    ],
}

FORBIDDEN_PROVENANCE_MARKERS = {
    "SOURCES.md": (
        "ACCESS CHECK REQUIRED = CURRENT NEXT",
    ),
    "sources/ScriptOps_Main_Theme_Summary.md": (
        "GENERIC HUMAN APPROVAL = X1B HumanDecision AUTHORSHIP EVIDENCE",
    ),
}

# Paths which are outside the frame/status correction surface and are not part
# of the separately reviewed X1B runtime transition profile remain immutable.
IMMUTABLE_PROTECTED_BLOBS = {
    "CODEX_START.md": "5f28888f98a245503fcfc28548133e9ef4b44961",
    "IDEA_ARCHIVE.md": "c7cde73b821e197b9fcf2f51105d466ab308e2f6",
    "phase6/bounded-proposal-view.py": "27f50f0df85fe6b66cfd3c33be00c6d975762b45",
    ".github/pull_request_template.md": "805cd965c6645a0ca8ee4700fb4fe23e1d78a528",
    ".github/workflows/phase6-scriptops-smoke.yml": "a811dc75b4d3c7a1ebd8375c24fc71c74586ddf5",
    ".github/workflows/verify-repository.yml": "7d896d425012479c97bf1e6539f9a861a4a17aa5",
    "tests/test_phase6_bounded_proposal_evidence.py": "dc2e51cad4580010f43ebf59b48c59ea53f81a95",
    "tests/test_phase6_bounded_proposal_view.py": "d5ed0e4e2186145c12ccde1f15886aa3bb93ec19",
    "tests/test_phase6_candidate_selection.py": "28448e2cd0b22cd5bf29df69a7a5c21961208f76",
    "tests/test_phase6_p3_evidence_record.py": "e4ac0b8f2bb6531e90aff0ae49f2a55ce8c1d7b5",
    "tests/test_phase6_p3_evidence_record_002.py": "8d61618e4cde290ade4d4ef329b01d3b46db9c62",
    "tests/test_phase6_p3_evidence_record_003.py": "cb3178ac706d6c6ee888c453284f610b5f81298b",
    "tests/test_phase6_p3_real_workload_001.py": "22b8f1176eb2bed65f763078a059359ba04894c4",
    "tests/test_phase6_p3_real_workload_002.py": "0c06ddd34049cd1608a892df6a86eff13d0c662b",
    "tests/test_phase6_p3_real_workload_003.py": "c0490aa8e9ee96d61d5179c31afafc9fd6499a17",
    "tests/test_phase6_review_task_identity.py": "55d1d6c0a5a5b0630be1f3e3c0d12c9363754a14",
}

# F006 repair: transition-sensitive files have exact, internally consistent
# profiles. The legacy profile is the frozen ScriptOps base. The V2 profile is
# the independently reviewed X1B implementation provenance at PR #35 HEAD
# 7c40a92165714023743e91c63b5b11b102fadd92. The current frame/status docs are
# deliberately not part of either runtime profile.
RUNTIME_PROFILES: dict[str, dict[str, str | None]] = {
    "LEGACY_PRE_X1B": {
        "legacy/scriptops-v2-single.py": "9baa7b3a1eb746e34b79207a382eea1f5dd4ec55",
        "phase6/scriptops-v2-hardening.py": "4f379960ed5677634dd234af6aa39626782b6133",
        "scripts/restore_v2.py": "fa2099d7d4530bce2256051690935625dab0e927",
        "sources/prototype/RESTORE.md": "8a79aca4c93b23c4842792bea9ecaae146e1fc48",
        "tests/test_phase6_scriptops_smoke.py": "d6065047268cee5591883a3065ce49886ec85bcf",
        "phase6/x1b_human_decision.py": None,
        "tests/test_x1b_human_decision.py": None,
        ".github/workflows/x1b-human-decision.yml": None,
    },
    "X1B_V2_CHECKOUT": {
        "legacy/scriptops-v2-single.py": "883669a4a141519483b56d9cde54897fb4c7b17c",
        "phase6/scriptops-v2-hardening.py": "9da50a3e33c982396049c7618f7154b360194350",
        "scripts/restore_v2.py": "20b0b506e537640d0859b687ba0d6ddc78e8ccd0",
        "sources/prototype/RESTORE.md": "fe84dc8d8fb066eaca2d196ecf1e41dc50c22f28",
        "tests/test_phase6_scriptops_smoke.py": "733e929bda33e30dd2de8a53c35eb910a84cbe0d",
        "phase6/x1b_human_decision.py": "1673a15060cc2a5c094acca1ceaf249eaa418c55",
        "tests/test_x1b_human_decision.py": "26ec92b789b38faf5cfc1fb5446ede4ffb2700a6",
        ".github/workflows/x1b-human-decision.yml": "4d71639b9afcb21d6e017a9dedd69459951f40a5",
    },
}

TRANSITION_COMMON_REQUIRED = {
    "legacy/scriptops-v2-single.py",
    "phase6/scriptops-v2-hardening.py",
    "scripts/restore_v2.py",
    "sources/prototype/RESTORE.md",
    "tests/test_phase6_scriptops_smoke.py",
}

POSITIVE_AUTHORITY_MARKERS = (
    "X1B_ACTIVE_PRODUCT_REMEDIATION_ASSERTION: CONFIRMED_NOT_REMEDIATED",
    "X1B_ACTIVE_PRODUCT_REMEDIATION_ASSERTION: CONFIRMED_REMEDIATED",
    "X1B_ACTIVE_PRODUCT_REMEDIATION_ASSERTION: YES",
    "X1B_ACTIVE_PRODUCT_REMEDIATION_ASSERTION: NO",
    "X1B_ACTIVE_PRODUCT_REMEDIATION_ASSERTION: TRUE",
    "X1B_ACTIVE_PRODUCT_REMEDIATION_ASSERTION: FALSE",
    "MERGE AUTHORITY = YES",
    "DEPLOYMENT AUTHORITY = YES",
    "RELEASE AUTHORITY = YES",
    "V1 AUTHORITY = YES",
    "CURRENT X1B AUTHORITY = YES",
)

# F009: Layer-B denial must not depend only on exact authority strings. These
# terms define a conservative self-referential promotion grammar. Historical
# statements remain readable; only claims that the text itself grants or is
# authority are rejected.
LAYER_B_SELF_REFERENCE_TERMS = (
    "THIS DOCUMENT",
    "THIS FILE",
    "THIS RECORD",
    "THIS PAGE",
    "THIS MARKDOWN",
    "THIS NOTE",
    "THIS ARTIFACT",
    "THESE WORDS",
    "THESE INSTRUCTIONS",
    "HEREBY",
)

# F015: HEREBY is self-referential/promotion context but not a grammatical
# subject boundary. The remaining phrases can introduce a fresh authority
# subject whose local negation must be evaluated independently.
LAYER_B_SELF_REFERENCE_SUBJECT_TERMS = tuple(
    term for term in LAYER_B_SELF_REFERENCE_TERMS if term != "HEREBY"
)

LAYER_B_PROMOTION_TERMS = (
    "AUTHORITY",
    "AUTHORITATIVE",
    "AUTHORIZE",
    "AUTHORIZES",
    "AUTHORIZED",
    "PERMIT",
    "PERMITS",
    "PERMITTED",
    "ALLOW",
    "ALLOWS",
    "ALLOWED",
    "GRANT",
    "GRANTS",
    "GOVERNS",
    "GOVERN",
    "CONTROLS",
    "CURRENT X1B",
    "CANONICAL X1B",
)

LAYER_B_LOCAL_NONCURRENT_TERMS = (
    "HISTORICAL",
    "PROVENANCE ONLY",
    "UNMERGED",
    "CURRENTNESS UNESTABLISHED",
    "WITHOUT SEPARATE HUMAN",
    "REQUIRES SEPARATE HUMAN",
)

LAYER_B_CONJUNCTION_BOUNDARIES = {
    "AND",
    "OR",
    "BUT",
    "HOWEVER",
    "YET",
}


class VerificationError(RuntimeError):
    pass


def read_text(relative_path: str) -> str:
    path = ROOT / relative_path
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        raise VerificationError(f"{relative_path} is not UTF-8: {exc}") from exc


def git_blob_sha1(path: Path) -> str:
    data = path.read_bytes()
    header = f"blob {len(data)}\0".encode("ascii")
    return hashlib.sha1(header + data).hexdigest()


def observed_blob(relative_path: str, root: Path = ROOT) -> str | None:
    path = root / relative_path
    if not path.is_file():
        return None
    return git_blob_sha1(path)


def registry_map_from_entries(entries: Iterable[tuple[str, str]]) -> dict[str, str]:
    result: dict[str, str] = {}
    for path, klass in entries:
        if path in result:
            raise VerificationError(f"duplicate registry class for {path}")
        result[path] = klass
    return result


def enumerate_registry_surface(root: Path = ROOT) -> list[str]:
    root_md = sorted(
        p.name for p in root.iterdir()
        if p.is_file() and p.suffix == ".md"
    )
    sources = root / "sources"
    direct_sources_md = sorted(
        f"sources/{p.name}" for p in sources.iterdir()
        if p.is_file() and p.suffix == ".md"
    )
    return root_md + direct_sources_md


def classify_nonregistry_markdown_path(relative_path: str) -> str:
    if relative_path in FROZEN_REGISTRY:
        raise VerificationError(f"registry member passed to Layer B: {relative_path}")
    for prefix in LAYER_B_PREFIXES:
        if relative_path.startswith(prefix):
            return "DENIED_BY_PATH_CLASS"
    raise VerificationError(f"UNCLASSIFIED_MARKDOWN_LOCATION: {relative_path}")


def enumerate_layer_b_markdown(root: Path = ROOT) -> list[str]:
    result: list[str] = []
    for path in sorted(root.rglob("*.md")):
        if not path.is_file():
            continue
        rel = path.relative_to(root).as_posix()
        if rel not in FROZEN_REGISTRY:
            result.append(rel)
    return result


def validate_registry(actual: Iterable[str], entries: Iterable[tuple[str, str]]) -> dict[str, str]:
    actual_set = set(actual)
    mapping = registry_map_from_entries(entries)
    if actual_set != FROZEN_REGISTRY:
        missing = sorted(FROZEN_REGISTRY - actual_set)
        extra = sorted(actual_set - FROZEN_REGISTRY)
        raise VerificationError(f"Layer-A registry mismatch missing={missing} extra={extra}")
    if len(actual_set) != 13:
        raise VerificationError(f"Layer-A registry cardinality must be 13, got {len(actual_set)}")
    if set(mapping) != actual_set:
        raise VerificationError("registry mapping keys do not equal Layer-A set")
    if len(mapping) != 13:
        raise VerificationError("registry mapping must contain exactly 13 keys")
    current = {p for p, klass in mapping.items() if klass == "CURRENT_BOOTSTRAP_AUTHORITY"}
    if current != CURRENT_BOOTSTRAP:
        raise VerificationError(f"current bootstrap set mismatch: {sorted(current)}")
    return mapping


def parse_x1b_fields(text: str) -> dict[str, str]:
    fields: dict[str, str] = {}
    for line in text.splitlines():
        stripped = line.strip()
        for key in EXPECTED_FIELDS:
            prefix = key + ":"
            if stripped.startswith(prefix):
                value = stripped[len(prefix):].strip()
                if key in fields and fields[key] != value:
                    raise VerificationError(f"conflicting {key} values")
                fields[key] = value
    return fields


def validate_current_schema(texts: dict[str, str]) -> None:
    if set(texts) != CURRENT_BOOTSTRAP:
        raise VerificationError("current schema must be checked on exactly the bootstrap trio")
    observed: dict[str, dict[str, str]] = {}
    for path, text in texts.items():
        fields = parse_x1b_fields(text)
        if fields != EXPECTED_FIELDS:
            raise VerificationError(f"{path} X1B schema mismatch: {fields}")
        observed[path] = fields
    first = next(iter(observed.values()))
    if any(fields != first for fields in observed.values()):
        raise VerificationError("current bootstrap trio disagrees")


def validate_provenance_text(path: str, text: str) -> None:
    for marker in PROVENANCE_MARKERS.get(path, []):
        if marker not in text:
            raise VerificationError(f"{path} missing provenance fence marker: {marker}")
    for marker in FORBIDDEN_PROVENANCE_MARKERS.get(path, ()):
        if marker in text:
            if path == "SOURCES.md":
                raise VerificationError(
                    f"{path} publishes forbidden stale current-next authority: {marker}"
                )
            if path == "sources/ScriptOps_Main_Theme_Summary.md":
                raise VerificationError(
                    f"{path} publishes forbidden Human-authorship promotion: {marker}"
                )
            raise VerificationError(f"{path} publishes forbidden provenance authority: {marker}")
    for marker in POSITIVE_AUTHORITY_MARKERS:
        if marker in text:
            raise VerificationError(f"{path} publishes forbidden current authority: {marker}")


def _normalized_authority_line(line: str) -> str:
    normalized = line.upper().replace("`", " ")
    for ch in "\t:;,()[]{}*#>_/\\|.-":
        normalized = normalized.replace(ch, " ")
    return " ".join(normalized.split())


def _term_positions(tokens: list[str], terms: Iterable[str]) -> list[tuple[int, int]]:
    positions: list[tuple[int, int]] = []
    for term in terms:
        parts = term.split()
        width = len(parts)
        for index in range(0, len(tokens) - width + 1):
            if tokens[index:index + width] == parts:
                positions.append((index, width))
    return sorted(set(positions))


def _promotion_positions(tokens: list[str]) -> list[int]:
    return [index for index, _ in _term_positions(tokens, LAYER_B_PROMOTION_TERMS)]


def _latest_independent_self_reference_start(
    tokens: list[str],
    promotion_index: int,
    segment_start: int,
) -> int:
    latest = segment_start
    for subject_index, width in _term_positions(tokens, LAYER_B_SELF_REFERENCE_SUBJECT_TERMS):
        if subject_index < segment_start or subject_index >= promotion_index:
            continue
        between = tokens[subject_index + width:promotion_index]
        # Preserve a negated embedded infinitive such as:
        # "This document does not authorize this file to grant authority."
        # In that shape THIS FILE is an object/complement, not a fresh subject.
        if "TO" in between:
            continue
        latest = max(latest, subject_index)
    return latest


def _promotion_locally_noncurrent(tokens: list[str], index: int) -> bool:
    segment_start = 0
    for prior in range(index - 1, -1, -1):
        if tokens[prior] in LAYER_B_CONJUNCTION_BOUNDARIES:
            segment_start = prior + 1
            break
    segment_start = _latest_independent_self_reference_start(
        tokens,
        index,
        segment_start,
    )
    prefix_tokens = tokens[segment_start:index]
    if any(token in {"NOT", "NO", "CANNOT"} for token in prefix_tokens):
        return True
    prefix_text = " ".join(prefix_tokens)
    return any(term in prefix_text for term in LAYER_B_LOCAL_NONCURRENT_TERMS)


def _all_promotions_locally_noncurrent(line: str) -> bool:
    tokens = line.split()
    positions = _promotion_positions(tokens)
    return bool(positions) and all(
        _promotion_locally_noncurrent(tokens, index)
        for index in positions
    )


def _authority_clauses(raw_line: str) -> list[str]:
    parts = re.split(
        r"[,;:.!?]+|\s+(?:—|–|--)\s+|\b(?:BUT|HOWEVER|YET)\b",
        raw_line.upper(),
    )
    return [
        normalized
        for part in parts
        if (normalized := _normalized_authority_line(part))
    ]


def _markdown_leading_columns(raw_line: str) -> int:
    columns = 0
    for char in raw_line:
        if char == " ":
            columns += 1
        elif char == "\t":
            columns += 4 - (columns % 4)
        else:
            break
    return columns


def _markdown_thematic_break_layout(
    raw_line: str,
    *,
    allow_deep_indent: bool = False,
) -> tuple[int, str, bool] | None:
    """Return indentation, marker, and setext ambiguity for a thematic break."""
    marker_indent = _markdown_leading_columns(raw_line)
    if marker_indent > 3 and not allow_deep_indent:
        return None

    # CommonMark thematic breaks contain at least three matching '-', '_', or
    # '*' characters. Spaces/tabs may occur between markers and at the end, but
    # no other non-whitespace payload is permitted.
    body = raw_line.lstrip(" \t").rstrip(" \t")
    compact = body.replace(" ", "").replace("\t", "")
    if len(compact) < 3 or compact[0] not in "-_*":
        return None
    marker = compact[0]
    if any(char != marker for char in compact):
        return None

    # A dash-only line without internal whitespace may instead be a setext
    # underline when it belongs to the current open paragraph. The caller has
    # the container/paragraph context needed to preserve that precedence.
    setext_candidate = marker == "-" and bool(re.fullmatch(r"-+", body))
    return marker_indent, marker, setext_candidate


def _markdown_setext_heading_underline_layout(
    raw_line: str,
    *,
    allow_deep_indent: bool = False,
) -> tuple[int, str] | None:
    """Return indentation and marker family for a setext heading underline."""
    marker_indent = _markdown_leading_columns(raw_line)
    if marker_indent > 3 and not allow_deep_indent:
        return None

    body = raw_line.lstrip(" \t")
    match = re.fullmatch(r"(?P<underline>=+|-+)[ \t]*", body)
    if match is None:
        return None
    return marker_indent, match.group("underline")[0]


_COMMONMARK_HTML_BLOCK_TYPE6_TAGS = {
    "address", "article", "aside", "base", "basefont", "blockquote", "body",
    "caption", "center", "col", "colgroup", "dd", "details", "dialog", "dir",
    "div", "dl", "dt", "fieldset", "figcaption", "figure", "footer", "form",
    "frame", "frameset", "h1", "h2", "h3", "h4", "h5", "h6", "head",
    "header", "hr", "html", "iframe", "legend", "li", "link", "main", "menu",
    "menuitem", "nav", "noframes", "ol", "optgroup", "option", "p", "param",
    "search", "section", "summary", "table", "tbody", "td", "tfoot", "th",
    "thead", "title", "tr", "track", "ul",
}


def _markdown_html_block_start_layout(
    raw_line: str,
    *,
    allow_deep_indent: bool = False,
) -> tuple[int, int] | None:
    """Return indentation and CommonMark HTML-block type for types 1-6."""
    marker_indent = _markdown_leading_columns(raw_line)
    if marker_indent > 3 and not allow_deep_indent:
        return None

    body = raw_line.lstrip(" \t")
    if re.match(r"^<(?:pre|script|style|textarea)(?:[ \t]|>|$)", body, re.I):
        return marker_indent, 1
    if body.startswith("<!--"):
        return marker_indent, 2
    if body.startswith("<?"):
        return marker_indent, 3
    if body.startswith("<![CDATA["):
        return marker_indent, 5
    if re.match(r"^<![A-Za-z]", body):
        return marker_indent, 4

    match = re.match(
        r"^</?(?P<tag>[A-Za-z][A-Za-z0-9-]*)(?=[ \t]|/?>|$)",
        body,
    )
    if (
        match is not None
        and match.group("tag").lower() in _COMMONMARK_HTML_BLOCK_TYPE6_TAGS
    ):
        return marker_indent, 6
    return None


def _markdown_html_block_type7_start_layout(
    raw_line: str,
    *,
    allow_deep_indent: bool = False,
) -> int | None:
    """Return indentation for a complete CommonMark type-7 HTML tag line."""
    marker_indent = _markdown_leading_columns(raw_line)
    if marker_indent > 3 and not allow_deep_indent:
        return None

    body = raw_line.lstrip(" \t")
    tag_name = r"[A-Za-z][A-Za-z0-9-]*"
    attribute_name = r"[A-Za-z_:][A-Za-z0-9_.:-]*"
    attribute_value = r"""(?:[^ \t"'=<>`]+|'[^']*'|"[^"]*")"""
    attribute = rf"(?:[ \t]+{attribute_name}(?:[ \t]*=[ \t]*{attribute_value})?)"

    open_match = re.fullmatch(
        rf"<(?P<tag>{tag_name})(?:{attribute})*[ \t]*/?>[ \t]*",
        body,
    )
    if (
        open_match is not None
        and open_match.group("tag").lower()
        not in {"pre", "script", "style", "textarea"}
    ):
        return marker_indent

    close_match = re.fullmatch(
        rf"</(?P<tag>{tag_name})[ \t]*>[ \t]*",
        body,
    )
    if close_match is not None:
        return marker_indent
    return None


def _markdown_html_block_end_matches(raw_line: str, block_type: int) -> bool:
    """Whether raw_line meets the end condition for HTML block types 1-7."""
    if block_type == 1:
        return re.search(
            r"</(?:pre|script|style|textarea)>",
            raw_line,
            re.I,
        ) is not None
    if block_type == 2:
        return "-->" in raw_line
    if block_type == 3:
        return "?>" in raw_line
    if block_type == 4:
        return ">" in raw_line
    if block_type == 5:
        return "]]>" in raw_line
    if block_type in {6, 7}:
        return not raw_line.strip()
    raise VerificationError(f"unknown HTML block type: {block_type}")


def _markdown_atx_heading_layout(
    raw_line: str,
    *,
    allow_deep_indent: bool = False,
) -> int | None:
    """Return indentation for a CommonMark ATX-heading opening."""
    marker_indent = _markdown_leading_columns(raw_line)
    if marker_indent > 3 and not allow_deep_indent:
        return None

    # CommonMark ATX headings use 1-6 unescaped '#' characters followed by
    # space/tab or end-of-line. Seven hashes and hashtag-like forms are text.
    body = raw_line.lstrip(" \t")
    if re.match(r"^#{1,6}(?:[ \t]+|$)", body) is None:
        return None
    return marker_indent


def _markdown_fenced_code_opening_layout(
    raw_line: str,
    *,
    allow_deep_indent: bool = False,
) -> tuple[int, str, int] | None:
    """Return indentation, marker, and length for a fenced-code opening."""
    marker_indent = _markdown_leading_columns(raw_line)
    if marker_indent > 3 and not allow_deep_indent:
        return None

    body = raw_line.lstrip(" \t")
    match = re.match(r"^(?P<fence>`{3,}|~{3,})(?P<info>.*)$", body)
    if match is None:
        return None

    fence = match.group("fence")
    info = match.group("info")
    if fence[0] == "`" and "`" in info:
        return None
    return marker_indent, fence[0], len(fence)


def _markdown_fenced_code_closing_layout(
    raw_line: str,
    marker: str,
    minimum_length: int,
    *,
    allow_deep_indent: bool = False,
) -> int | None:
    """Return indentation for a matching fenced-code closing fence."""
    marker_indent = _markdown_leading_columns(raw_line)
    if marker_indent > 3 and not allow_deep_indent:
        return None

    body = raw_line.lstrip(" \t")
    match = re.fullmatch(r"(?P<fence>`+|~+)[ \t]*", body)
    if match is None:
        return None
    fence = match.group("fence")
    if fence[0] != marker or len(fence) < minimum_length:
        return None
    return marker_indent


def _markdown_block_quote_layout(
    raw_line: str,
    *,
    allow_deep_indent: bool = False,
) -> tuple[int, str] | None:
    """Return marker indentation and content after one block-quote marker."""
    marker_indent = _markdown_leading_columns(raw_line)
    if marker_indent > 3 and not allow_deep_indent:
        return None

    body = raw_line.lstrip(" \t")
    if not body.startswith(">"):
        return None

    content = body[1:]
    if content.startswith((" ", "\t")):
        content = content[1:]
    return marker_indent, content


def _markdown_block_quote_lazy_paragraph(
    content: str,
    *,
    paragraph_open: bool = False,
) -> bool:
    """Whether an explicitly quoted line can carry lazy paragraph text."""
    if not content.strip():
        return False
    # Four-plus columns start indented code only when no paragraph is already
    # open. If a quoted paragraph is open, indentation cannot interrupt it.
    if _markdown_leading_columns(content) >= 4:
        return paragraph_open
    if content.lstrip(" \t").startswith(">"):
        return False
    if _markdown_fenced_code_opening_layout(content) is not None:
        return False
    if _markdown_html_block_start_layout(content) is not None:
        return False
    if _markdown_setext_heading_underline_layout(content) is not None:
        return False
    if _markdown_atx_heading_layout(content) is not None:
        return False
    if _markdown_thematic_break_layout(content) is not None:
        return False
    return True


def _markdown_list_item_layout(
    raw_line: str,
    *,
    allow_deep_indent: bool = False,
) -> tuple[int, int, bool, bool] | None:
    match = re.match(
        r"^(?P<indent>[ \t]*)(?P<marker>[-+*]|[0-9]{1,9}[.)])(?:(?P<gap>[ \t]+)|$)",
        raw_line,
    )
    if match is None:
        return None
    marker_indent = len(match.group("indent").expandtabs(4))
    if marker_indent > 3 and not allow_deep_indent:
        return None
    empty_item = not raw_line[match.end():].strip()
    marker = match.group("marker")
    marker_width = len(marker)
    marker_end_indent = marker_indent + marker_width
    if empty_item:
        content_indent = marker_end_indent + 1
    else:
        physical_content_indent = len(raw_line[:match.end()].expandtabs(4))
        gap_columns = physical_content_indent - marker_end_indent
        # CommonMark list items normally use 1-4 columns after the marker.
        # If there are more than four, one column belongs to the item marker
        # and the remainder starts an indented code block inside that item.
        content_indent = (
            marker_end_indent + 1 if gap_columns > 4 else physical_content_indent
        )
    ordered_start = int(marker[:-1]) if marker[0].isdigit() else None
    can_interrupt_paragraph = (
        not empty_item
        and (ordered_start is None or ordered_start == 1)
    )
    return marker_indent, content_indent, empty_item, can_interrupt_paragraph


def _markdown_list_item_starts_indented_code(
    raw_line: str,
    *,
    allow_deep_indent: bool = False,
) -> bool:
    """Whether a valid list marker's first nonblank block is indented code."""
    match = re.match(
        r"^(?P<indent>[ \t]*)(?P<marker>[-+*]|[0-9]{1,9}[.)])(?:(?P<gap>[ \t]+)|$)",
        raw_line,
    )
    if match is None or match.group("gap") is None:
        return False
    marker_indent = len(match.group("indent").expandtabs(4))
    if marker_indent > 3 and not allow_deep_indent:
        return False
    if not raw_line[match.end():].strip():
        return False
    marker_end_indent = marker_indent + len(match.group("marker"))
    physical_content_indent = len(raw_line[:match.end()].expandtabs(4))
    return physical_content_indent - marker_end_indent > 4


def _authority_soft_wrapped_units(text: str) -> list[str]:
    """Fold Markdown authority text along paragraph/list-item paths."""
    units: list[str] = []
    paragraph: list[str] = []
    list_frames: list[tuple[int, int, list[str]]] = []
    block_quote_parts: list[str] = []
    block_quote_lazy = False
    block_quote_indented_code = False
    fenced_code_marker: str | None = None
    fenced_code_length = 0
    fenced_code_owner_indent: int | None = None
    fenced_code_parts: list[str] = []
    html_block_type: int | None = None
    html_block_owner_indent: int | None = None
    html_block_parts: list[str] = []
    indented_code_active = False
    indented_code_owner_indent: int | None = None
    indented_code_parts: list[str] = []
    blank_seen = False

    def emit(parts: list[str]) -> None:
        if parts:
            units.append(" ".join(parts))

    def flush_paragraph() -> None:
        nonlocal paragraph
        emit(paragraph)
        paragraph = []

    def flush_block_quote() -> None:
        nonlocal block_quote_parts, block_quote_lazy, block_quote_indented_code
        emit(block_quote_parts)
        block_quote_parts = []
        block_quote_lazy = False
        block_quote_indented_code = False

    def emit_active_list_path() -> None:
        if list_frames:
            emit([
                part
                for _, _, frame_parts in list_frames
                for part in frame_parts
            ])

    def activate_list_indented_code(starts_indented_code: bool) -> None:
        nonlocal indented_code_active, indented_code_owner_indent
        if starts_indented_code and list_frames:
            indented_code_active = True
            indented_code_owner_indent = list_frames[-1][1]

    for raw_line in text.splitlines():
        # F040: once indented code starts, its payload is literal. A nonblank
        # dedent ends the leaf block and the same line is reprocessed normally.
        if indented_code_active:
            if not raw_line.strip():
                continue
            leading_in_code = _markdown_leading_columns(raw_line)
            required_indent = (
                4
                if indented_code_owner_indent is None
                else indented_code_owner_indent + 4
            )
            if leading_in_code >= required_indent:
                if indented_code_owner_indent is None:
                    indented_code_parts.append(raw_line.strip())
                else:
                    list_frames[-1][2].append(raw_line.strip())
                continue

            if indented_code_owner_indent is None:
                emit(indented_code_parts)
                indented_code_parts = []
                indented_code_active = False
            else:
                indented_code_active = False
                indented_code_owner_indent = None
                # Paragraph-only lazy continuation cannot cross a code block.
                blank_seen = True

        # F038/F039: raw HTML block contents are literal until the CommonMark
        # block end condition or the end of their containing list item. Run this
        # before every other Markdown marker so raw payload cannot be reparsed.
        if html_block_type is not None:
            html_ends = _markdown_html_block_end_matches(
                raw_line,
                html_block_type,
            )

            if html_block_owner_indent is None:
                if html_block_type in {6, 7} and html_ends:
                    emit(html_block_parts)
                    html_block_parts = []
                    html_block_type = None
                    # Fall through so the blank line gets ordinary blank handling.
                else:
                    if raw_line.strip():
                        html_block_parts.append(raw_line.strip())
                    if html_block_type not in {6, 7} and html_ends:
                        emit(html_block_parts)
                        html_block_parts = []
                        html_block_type = None
                    continue
            else:
                leading_in_html = _markdown_leading_columns(raw_line)
                if raw_line.strip() and leading_in_html < html_block_owner_indent:
                    # The raw block ends with its containing item. Reprocess the
                    # same dedented line under the surviving outer structure.
                    html_block_type = None
                    html_block_owner_indent = None
                    blank_seen = True
                elif html_block_type in {6, 7} and html_ends:
                    html_block_type = None
                    html_block_owner_indent = None
                    blank_seen = True
                    # Fall through so the terminating blank resolves ownership.
                else:
                    if raw_line.strip():
                        list_frames[-1][2].append(raw_line.strip())
                    if html_block_type not in {6, 7} and html_ends:
                        html_block_type = None
                        html_block_owner_indent = None
                        blank_seen = True
                    continue

        # F036: once a fence opens, its contents are literal. This state must
        # run before blank handling and before every other Markdown marker.
        if fenced_code_marker is not None:
            closing_indent = _markdown_fenced_code_closing_layout(
                raw_line,
                fenced_code_marker,
                fenced_code_length,
                allow_deep_indent=fenced_code_owner_indent is not None,
            )

            if fenced_code_owner_indent is None:
                if closing_indent is not None and closing_indent <= 3:
                    emit(fenced_code_parts)
                    fenced_code_parts = []
                    fenced_code_marker = None
                    fenced_code_length = 0
                    blank_seen = False
                    continue
                if raw_line.strip():
                    fenced_code_parts.append(raw_line.strip())
                continue

            leading_in_fence = _markdown_leading_columns(raw_line)
            if (
                closing_indent is not None
                and fenced_code_owner_indent
                <= closing_indent
                <= fenced_code_owner_indent + 3
            ):
                fenced_code_marker = None
                fenced_code_length = 0
                fenced_code_owner_indent = None
                # A fenced leaf block ended inside the item. Following text may
                # not use paragraph-only lazy continuation to escape ownership.
                blank_seen = True
                continue

            if raw_line.strip() and leading_in_fence < fenced_code_owner_indent:
                # An unclosed fence ends at the end of its containing list item.
                # Reprocess this same dedented line under the surviving structure.
                fenced_code_marker = None
                fenced_code_length = 0
                fenced_code_owner_indent = None
                blank_seen = True
            else:
                if raw_line.strip():
                    list_frames[-1][2].append(raw_line.strip())
                continue

        stripped = raw_line.strip()
        if not stripped:
            if block_quote_parts:
                flush_block_quote()
            if list_frames:
                blank_seen = True
            else:
                flush_paragraph()
            continue

        leading = _markdown_leading_columns(raw_line)
        fence_layout = _markdown_fenced_code_opening_layout(
            raw_line,
            allow_deep_indent=bool(list_frames),
        )

        # F035: a block quote is a container that can interrupt an ordinary
        # paragraph without a blank line. At top level we retain an explicit
        # quote unit so lazy paragraph continuation cannot become a bypass.
        quote_layout = _markdown_block_quote_layout(
            raw_line,
            allow_deep_indent=bool(list_frames),
        )

        if block_quote_parts:
            if quote_layout is not None and quote_layout[0] <= 3:
                _, quote_content = quote_layout
                if block_quote_indented_code:
                    quote_content_indent = _markdown_leading_columns(quote_content)
                    if not quote_content.strip() or quote_content_indent >= 4:
                        block_quote_parts.append(stripped)
                        continue

                    # F041: a nonblank quoted dedent ends the quoted code leaf.
                    # Reuse the same explicit quote line as the first line of
                    # the following quoted leaf instead of donating code context.
                    flush_block_quote()
                    block_quote_parts.append(stripped)
                    block_quote_lazy = _markdown_block_quote_lazy_paragraph(
                        quote_content
                    )
                    continue

                block_quote_parts.append(stripped)
                block_quote_lazy = _markdown_block_quote_lazy_paragraph(
                    quote_content,
                    paragraph_open=block_quote_lazy,
                )
                continue

            if block_quote_lazy:
                top_fence = _markdown_fenced_code_opening_layout(raw_line)
                top_html = _markdown_html_block_start_layout(raw_line)
                top_atx = _markdown_atx_heading_layout(raw_line)
                top_thematic = _markdown_thematic_break_layout(raw_line)
                top_list = _markdown_list_item_layout(raw_line)
                top_list_interrupts = top_list is not None and top_list[3]
                if (
                    top_fence is None
                    and top_html is None
                    and top_atx is None
                    and top_thematic is None
                    and not top_list_interrupts
                ):
                    block_quote_parts.append(stripped)
                    continue

            flush_block_quote()

        # F040: indented code starts only when no paragraph leaf is open. In a
        # list, a closed leaf may start code four columns beyond a surviving
        # item content indent. Resolve an ancestor owner before block markers.
        if not list_frames and not paragraph and leading >= 4:
            indented_code_active = True
            indented_code_owner_indent = None
            indented_code_parts = [stripped]
            blank_seen = False
            continue

        if list_frames and blank_seen:
            surviving_owner_index = next(
                (
                    index
                    for index in range(len(list_frames) - 1, -1, -1)
                    if leading >= list_frames[index][1]
                ),
                None,
            )
            if surviving_owner_index is not None:
                owner_content_indent = list_frames[surviving_owner_index][1]
                if leading >= owner_content_indent + 4:
                    if surviving_owner_index < len(list_frames) - 1:
                        emit_active_list_path()
                        list_frames = list_frames[:surviving_owner_index + 1]
                    list_frames[-1][2].append(stripped)
                    indented_code_active = True
                    indented_code_owner_indent = list_frames[-1][1]
                    blank_seen = False
                    continue

            if surviving_owner_index is None and leading >= 4:
                emit_active_list_path()
                list_frames = []
                indented_code_active = True
                indented_code_owner_indent = None
                indented_code_parts = [stripped]
                blank_seen = False
                continue

        if quote_layout is not None:
            quote_indent, quote_content = quote_layout

            if not list_frames and quote_indent <= 3:
                flush_paragraph()
                block_quote_parts.append(stripped)
                block_quote_indented_code = (
                    bool(quote_content.strip())
                    and _markdown_leading_columns(quote_content) >= 4
                )
                block_quote_lazy = _markdown_block_quote_lazy_paragraph(quote_content)
                blank_seen = False
                continue

            if list_frames:
                quote_host_index = next(
                    (
                        index
                        for index in range(len(list_frames) - 1, -1, -1)
                        if list_frames[index][1]
                        <= quote_indent
                        <= list_frames[index][1] + 3
                    ),
                    None,
                )

                if quote_host_index is None and quote_indent <= 3:
                    # The quote is top level, so the old list path cannot donate
                    # its self-reference into quoted authority text.
                    emit_active_list_path()
                    list_frames = []
                    block_quote_parts.append(stripped)
                    block_quote_indented_code = (
                        bool(quote_content.strip())
                        and _markdown_leading_columns(quote_content) >= 4
                    )
                    block_quote_lazy = _markdown_block_quote_lazy_paragraph(quote_content)
                    blank_seen = False
                    continue

                if quote_host_index is not None:
                    # An owned quote remains inside the nearest owning item. A
                    # quote at an ancestor closes descendants before inheriting
                    # only that surviving ancestor path.
                    if quote_host_index < len(list_frames) - 1:
                        emit_active_list_path()
                        list_frames = list_frames[:quote_host_index + 1]
                    list_frames[-1][2].append(stripped)
                    blank_seen = False
                    continue

        # F036: fenced code is a leaf block that can interrupt paragraphs.
        # Top-level fences form their own authority unit; list-owned fences keep
        # the owning item context while their literal contents suppress markers.
        if fence_layout is not None:
            fence_indent, fence_marker, fence_length = fence_layout

            if not list_frames and fence_indent <= 3:
                flush_paragraph()
                fenced_code_marker = fence_marker
                fenced_code_length = fence_length
                fenced_code_owner_indent = None
                fenced_code_parts = []
                blank_seen = False
                continue

            if list_frames:
                fence_host_index = next(
                    (
                        index
                        for index in range(len(list_frames) - 1, -1, -1)
                        if list_frames[index][1]
                        <= fence_indent
                        <= list_frames[index][1] + 3
                    ),
                    None,
                )

                if fence_host_index is None and fence_indent <= 3:
                    emit_active_list_path()
                    list_frames = []
                    fenced_code_marker = fence_marker
                    fenced_code_length = fence_length
                    fenced_code_owner_indent = None
                    fenced_code_parts = []
                    blank_seen = False
                    continue

                if fence_host_index is not None:
                    if fence_host_index < len(list_frames) - 1:
                        emit_active_list_path()
                        list_frames = list_frames[:fence_host_index + 1]
                    fenced_code_marker = fence_marker
                    fenced_code_length = fence_length
                    fenced_code_owner_indent = list_frames[-1][1]
                    blank_seen = False
                    continue

        # F038/F039: types 1-6 may interrupt paragraphs. A complete type-7
        # tag starts raw HTML only when no paragraph is currently open; in a
        # list path, blank_seen is the bounded proof that paragraph laziness has
        # already ended. This preserves type 7's normative non-interruption.
        html_layout = _markdown_html_block_start_layout(
            raw_line,
            allow_deep_indent=bool(list_frames),
        )
        if html_layout is None:
            type7_indent = _markdown_html_block_type7_start_layout(
                raw_line,
                allow_deep_indent=bool(list_frames),
            )
            if type7_indent is not None:
                if not list_frames and not paragraph:
                    html_layout = (type7_indent, 7)
                elif list_frames and blank_seen:
                    html_layout = (type7_indent, 7)

        if html_layout is not None:
            html_indent, new_html_type = html_layout

            if not list_frames and html_indent <= 3:
                flush_paragraph()
                html_block_type = new_html_type
                html_block_owner_indent = None
                html_block_parts = [stripped]
                blank_seen = False
                if (
                    new_html_type not in {6, 7}
                    and _markdown_html_block_end_matches(raw_line, new_html_type)
                ):
                    emit(html_block_parts)
                    html_block_parts = []
                    html_block_type = None
                continue

            if list_frames:
                html_host_index = next(
                    (
                        index
                        for index in range(len(list_frames) - 1, -1, -1)
                        if list_frames[index][1]
                        <= html_indent
                        <= list_frames[index][1] + 3
                    ),
                    None,
                )

                if html_host_index is None and html_indent <= 3:
                    emit_active_list_path()
                    list_frames = []
                    html_block_type = new_html_type
                    html_block_owner_indent = None
                    html_block_parts = [stripped]
                    blank_seen = False
                    if (
                        new_html_type not in {6, 7}
                        and _markdown_html_block_end_matches(raw_line, new_html_type)
                    ):
                        emit(html_block_parts)
                        html_block_parts = []
                        html_block_type = None
                    continue

                if html_host_index is not None:
                    if html_host_index < len(list_frames) - 1:
                        emit_active_list_path()
                        list_frames = list_frames[:html_host_index + 1]
                    list_frames[-1][2].append(stripped)
                    if (
                        new_html_type not in {6, 7}
                        and _markdown_html_block_end_matches(raw_line, new_html_type)
                    ):
                        blank_seen = True
                    else:
                        html_block_type = new_html_type
                        html_block_owner_indent = list_frames[-1][1]
                        blank_seen = False
                    continue

        # F034: ATX headings may interrupt paragraphs without blank lines.
        # Resolve them before list markers and before F031 lazy continuation.
        atx_indent = _markdown_atx_heading_layout(
            raw_line,
            allow_deep_indent=bool(list_frames),
        )
        if not list_frames and atx_indent is not None:
            # Top-level heading text is still security-relevant on its own.
            flush_paragraph()
            emit([stripped])
            blank_seen = False
            continue

        if list_frames and atx_indent is not None:
            atx_host_index = next(
                (
                    index
                    for index in range(len(list_frames) - 1, -1, -1)
                    if list_frames[index][1]
                    <= atx_indent
                    <= list_frames[index][1] + 3
                ),
                None,
            )

            if atx_host_index is None and atx_indent <= 3:
                # A valid top-level heading closes the active list path.
                emit_active_list_path()
                list_frames = []
                emit([stripped])
                blank_seen = False
                continue

            if atx_host_index is not None:
                # An owned heading remains inside its owning item security
                # context. Close deeper descendants, then force the following
                # line to re-resolve ownership because lazy continuation is a
                # paragraph rule and cannot flow out of an ATX block.
                if atx_host_index < len(list_frames) - 1:
                    emit_active_list_path()
                    list_frames = list_frames[:atx_host_index + 1]
                list_frames[-1][2].append(stripped)
                blank_seen = True
                continue

        # F037: an equals-family setext underline turns the immediately open
        # paragraph into a heading. It is structural only when heading text
        # exists; a bare top-level underline is ordinary paragraph text. Dash
        # setext/thematic precedence remains on the existing F032/F033 path.
        setext = _markdown_setext_heading_underline_layout(
            raw_line,
            allow_deep_indent=bool(list_frames),
        )
        if setext is not None and setext[1] == "=":
            setext_indent, _ = setext

            if not list_frames and paragraph:
                flush_paragraph()
                blank_seen = False
                continue

            if list_frames:
                setext_host_index = next(
                    (
                        index
                        for index in range(len(list_frames) - 1, -1, -1)
                        if list_frames[index][1]
                        <= setext_indent
                        <= list_frames[index][1] + 3
                    ),
                    None,
                )

                if setext_host_index is None and setext_indent <= 3:
                    # A setext underline cannot be a lazy list continuation.
                    # With no owning paragraph it is ordinary top-level text.
                    emit_active_list_path()
                    list_frames = []
                    paragraph.append(stripped)
                    blank_seen = False
                    continue

                if (
                    setext_host_index == len(list_frames) - 1
                    and not blank_seen
                ):
                    # The current item owns the heading. Keep its security
                    # context, but paragraph laziness ends at the underline.
                    list_frames[-1][2].append(stripped)
                    blank_seen = True
                    continue

        # F032: thematic-break precedence is resolved before list markers.
        # This is deliberately list-context-aware: a deep thematic-looking
        # line is structural only when some active item owns its indentation,
        # while a 0-3-column break outside every owner closes the list path.
        thematic = _markdown_thematic_break_layout(
            raw_line,
            allow_deep_indent=bool(list_frames),
        )
        if not list_frames and thematic is not None:
            # F033: at top level, a valid thematic break is a block boundary.
            # A dash-only candidate after an open paragraph is a setext
            # underline, which likewise terminates that paragraph before later
            # text. In either case the marker may not be treated as a soft wrap.
            flush_paragraph()
            blank_seen = False
            continue

        if list_frames and thematic is not None:
            thematic_indent, _, setext_candidate = thematic
            thematic_host_index = next(
                (
                    index
                    for index in range(len(list_frames) - 1, -1, -1)
                    if list_frames[index][1]
                    <= thematic_indent
                    <= list_frames[index][1] + 3
                ),
                None,
            )

            if thematic_host_index is None and thematic_indent <= 3:
                # The break is outside every active list-item container. It is
                # therefore a top-level block boundary, not F031 lazy text.
                emit_active_list_path()
                list_frames = []
                blank_seen = False
                continue

            if thematic_host_index is not None and not (
                setext_candidate
                and thematic_host_index == len(list_frames) - 1
                and not blank_seen
            ):
                # An unambiguous owned thematic break outranks list-item marker
                # parsing. Descendants below its owner are closed. Keep the
                # owning item itself, but require the next line to re-resolve
                # indentation ownership as it would after a block boundary.
                if thematic_host_index < len(list_frames) - 1:
                    emit_active_list_path()
                    list_frames = list_frames[:thematic_host_index + 1]
                blank_seen = True
                continue

        ownership_unwound = False
        if list_frames and blank_seen and leading < list_frames[-1][1]:
            # After a blank line, resolve list-item ownership before deciding
            # whether a deeply indented marker is a descendant. Otherwise a
            # four-space code-like block can be absorbed by a wide list item.
            emit_active_list_path()
            old_depth = len(list_frames)
            while list_frames and leading < list_frames[-1][1]:
                list_frames.pop()
            ownership_unwound = len(list_frames) < old_depth
            blank_seen = False

        layout = _markdown_list_item_layout(
            raw_line,
            allow_deep_indent=bool(list_frames),
        )

        if layout is not None:
            marker_indent, content_indent, empty_item, can_interrupt_paragraph = layout
            starts_indented_code = _markdown_list_item_starts_indented_code(
                raw_line,
                allow_deep_indent=bool(list_frames),
            )

            if not list_frames:
                if paragraph and not can_interrupt_paragraph:
                    # Empty items and non-one ordered items cannot interrupt an
                    # active ordinary paragraph under CommonMark.
                    paragraph.append(stripped)
                    blank_seen = False
                    continue
                flush_paragraph()
                list_frames.append((marker_indent, content_indent, [stripped]))
                activate_list_indented_code(starts_indented_code)
                blank_seen = False
                continue

            same_level_index = next(
                (
                    index
                    for index in range(len(list_frames) - 1, -1, -1)
                    if list_frames[index][0] == marker_indent
                ),
                None,
            )
            if same_level_index is not None:
                # Same structural list level is always a boundary. A family,
                # bullet-character, or ordered-delimiter change starts a new
                # list rather than donating context across distinct items.
                emit_active_list_path()
                list_frames = list_frames[:same_level_index]
                list_frames.append((marker_indent, content_indent, [stripped]))
                activate_list_indented_code(starts_indented_code)
                blank_seen = False
                continue

            host_index = next(
                (
                    index
                    for index in range(len(list_frames) - 1, -1, -1)
                    if list_frames[index][1]
                    <= marker_indent
                    <= list_frames[index][1] + 3
                ),
                None,
            )

            if host_index is not None:
                if host_index < len(list_frames) - 1:
                    # The marker dedents out of one or more descendants and is
                    # a new block under the nearest surviving owner. Paragraph
                    # interruption no longer applies after those blocks close.
                    emit_active_list_path()
                    list_frames = list_frames[:host_index + 1]
                    list_frames.append((marker_indent, content_indent, [stripped]))
                    activate_list_indented_code(starts_indented_code)
                    blank_seen = False
                    continue

                if ownership_unwound or blank_seen or can_interrupt_paragraph:
                    # A blank/closed block permits any valid list start. With
                    # an open current-leaf paragraph, only bullets and ordered
                    # start=1 may interrupt it.
                    list_frames.append((marker_indent, content_indent, [stripped]))
                    activate_list_indented_code(starts_indented_code)
                    blank_seen = False
                    continue

                # F028/F031: a non-one/empty marker-looking line inside the
                # current open item paragraph is lazy continuation.
                list_frames[-1][2].append(stripped)
                blank_seen = False
                continue

            if marker_indent <= 3:
                # No active owner can host the marker, but it is valid at top
                # level. Close the old path and begin a distinct list.
                emit_active_list_path()
                list_frames = [(marker_indent, content_indent, [stripped])]
                activate_list_indented_code(starts_indented_code)
                blank_seen = False
                continue

            # More than three columns beyond every owning content indent is not
            # a nested list marker for this path. Keep it as paragraph/code-like
            # content rather than manufacturing a boundary from deep indentation.
            list_frames[-1][2].append(stripped)
            blank_seen = False
            continue

        if list_frames:
            # Without a blank line, Markdown permits lazy continuation text.
            # After a blank, ownership was already resolved above.
            list_frames[-1][2].append(stripped)
            blank_seen = False
            continue

        paragraph.append(stripped)
        blank_seen = False

    if indented_code_active and indented_code_owner_indent is None:
        emit(indented_code_parts)
    if html_block_type is not None and html_block_owner_indent is None:
        emit(html_block_parts)
    if fenced_code_marker is not None and fenced_code_owner_indent is None:
        # CommonMark closes an unclosed top-level fence at end-of-document.
        emit(fenced_code_parts)
    if block_quote_parts:
        flush_block_quote()
    if list_frames:
        emit_active_list_path()
    else:
        flush_paragraph()
    return units


def layer_b_self_promotion_claim(text: str) -> str | None:
    """Return the first self-referential Layer-B authority claim, if any."""
    for raw_line in _authority_soft_wrapped_units(text):
        for line in _authority_clauses(raw_line):
            self_referential = any(term in line for term in LAYER_B_SELF_REFERENCE_TERMS)
            promotion = any(term in line for term in LAYER_B_PROMOTION_TERMS)
            if self_referential and promotion:
                if _all_promotions_locally_noncurrent(line):
                    continue
                return raw_line.strip()

        # F016: clause splitting is useful for negation-scope isolation, but it
        # must not become a prerequisite for recognizing the subject/predicate
        # relationship itself. Re-check the normalized whole line so commas or
        # parenthetical discourse markers cannot separate a self-reference from
        # a later positive authority predicate.
        whole_line = _normalized_authority_line(raw_line)
        whole_self_referential = any(
            term in whole_line for term in LAYER_B_SELF_REFERENCE_TERMS
        )
        whole_promotion = any(
            term in whole_line for term in LAYER_B_PROMOTION_TERMS
        )
        if (
            whole_self_referential
            and whole_promotion
            and not _all_promotions_locally_noncurrent(whole_line)
        ):
            return raw_line.strip()
    return None


def validate_layer_b_non_authority_text(path: str, text: str) -> None:
    for marker in POSITIVE_AUTHORITY_MARKERS:
        if marker in text:
            raise VerificationError(f"Layer-B document {path} publishes forbidden authority: {marker}")
    claim = layer_b_self_promotion_claim(text)
    if claim is not None:
        raise VerificationError(
            f"Layer-B document {path} publishes forbidden self-promotion: {claim}"
        )


def classify_runtime_text(text: str) -> str:
    legacy = (
        'approve.add_argument("--why", required=True)' in text
        and '"approver": "human"' in text
        and "x1b.approve_scene(" not in text
        and '"--decision-pr"' not in text
    )
    if legacy:
        return "LEGACY_PRE_X1B"
    v2 = (
        "x1b.approve_scene(" in text
        and 'approve.add_argument("--decision-pr", required=True, type=int)' in text
        and "HumanDecision=TRUE" in text
    )
    if v2:
        return "X1B_V2_CHECKOUT"
    return "UNKNOWN"


def validate_runtime_currentness(runtime_class: str, assertion: str) -> None:
    if assertion != "CURRENTNESS_UNESTABLISHED":
        raise VerificationError("local runtime class may not promote active-product state")
    if runtime_class not in {"LEGACY_PRE_X1B", "X1B_V2_CHECKOUT"}:
        raise VerificationError(f"unknown local runtime class: {runtime_class}")


def observe_runtime_profile(root: Path = ROOT) -> dict[str, str | None]:
    all_paths: set[str] = set()
    for profile in RUNTIME_PROFILES.values():
        all_paths.update(profile)
    return {path: observed_blob(path, root) for path in sorted(all_paths)}


def validate_runtime_profile(
    runtime_class: str,
    observed: dict[str, str | None],
    assertion: str,
) -> None:
    """Validate the real transition profile used by repository verification.

    Both recognized rows are admissible only with CURRENTNESS_UNESTABLISHED.
    Exact profile matching prevents a legacy/V2 Frankenstein checkout from
    borrowing the semantic label of either reviewed runtime.
    """
    validate_runtime_currentness(runtime_class, assertion)
    expected = RUNTIME_PROFILES[runtime_class]
    if set(observed) != set(expected):
        missing = sorted(set(expected) - set(observed))
        extra = sorted(set(observed) - set(expected))
        raise VerificationError(
            f"runtime profile key mismatch for {runtime_class}: missing={missing} extra={extra}"
        )
    mismatches = [
        f"{path}: expected={expected[path]} actual={observed[path]}"
        for path in sorted(expected)
        if observed[path] != expected[path]
    ]
    if mismatches:
        raise VerificationError(
            f"runtime profile mismatch for {runtime_class}: " + "; ".join(mismatches)
        )


def check_required_paths() -> None:
    required = (
        FROZEN_REGISTRY
        | set(IMMUTABLE_PROTECTED_BLOBS)
        | TRANSITION_COMMON_REQUIRED
        | {"scripts/verify_repository.py"}
    )
    missing = sorted(path for path in required if not (ROOT / path).is_file())
    if missing:
        raise VerificationError(f"missing required paths: {missing}")
    print(f"[PASS] required bounded/protected paths present: {len(required)}")


def check_immutable_blobs() -> None:
    mismatches: list[str] = []
    for relative_path, expected in IMMUTABLE_PROTECTED_BLOBS.items():
        actual = git_blob_sha1(ROOT / relative_path)
        if actual != expected:
            mismatches.append(f"{relative_path}: expected={expected} actual={actual}")
    if mismatches:
        raise VerificationError("immutable protected baseline drift: " + "; ".join(mismatches))
    print(f"[PASS] immutable protected sentinels unchanged: {len(IMMUTABLE_PROTECTED_BLOBS)} blobs")


def check_layer_a() -> None:
    actual = enumerate_registry_surface()
    validate_registry(actual, REGISTRY_ENTRIES)
    if "sources/prototype/RESTORE.md" in actual:
        raise VerificationError("RESTORE.md must not enter Layer-A registry")
    print("[PASS] Layer A exact: 13 root/direct-sources Markdown registry members")


def check_layer_b() -> None:
    paths = enumerate_layer_b_markdown()
    for path in paths:
        result = classify_nonregistry_markdown_path(path)
        if result != "DENIED_BY_PATH_CLASS":
            raise VerificationError(f"unexpected Layer-B classification: {path} -> {result}")
    if "sources/prototype/RESTORE.md" not in paths:
        raise VerificationError("RESTORE.md must be present in Layer B")
    print(f"[PASS] Layer B path-class denial: {len(paths)} Markdown files; registry count unchanged")


def check_current_bootstrap() -> None:
    texts = {path: read_text(path) for path in CURRENT_BOOTSTRAP}
    validate_current_schema(texts)
    readme = texts["README.md"]
    state = texts["PROJECT_STATE.md"]
    handoff = texts["HANDOFF.md"]
    required_separations = [
        "CURRENTNESS_UNESTABLISHED != FALSE",
        "CURRENTNESS_UNESTABLISHED != TRUE",
        "PR HEAD != ACTIVE DEFAULT BRANCH",
        "GREEN VERIFICATION != DEPLOYED ENFORCEMENT",
        "GENERIC HUMAN APPROVAL != X1B HumanDecision AUTHORSHIP EVIDENCE",
    ]
    for marker in required_separations:
        if marker not in readme:
            raise VerificationError(f"README missing boundary: {marker}")
    if "No current `approve --why` / canonical-write instruction is authorized by this file." not in state:
        raise VerificationError("PROJECT_STATE does not fence legacy effect route")
    if "PR #35 must not be merged as-is" not in handoff:
        raise VerificationError("HANDOFF does not fence stale PR #35")
    print("[PASS] current bootstrap trio agrees on CURRENTNESS_UNESTABLISHED and TWO_LAYER_CLOSED_WORLD_V1")


def check_provenance_surfaces() -> None:
    for path in PROVENANCE_MARKERS:
        validate_provenance_text(path, read_text(path))
    for path in enumerate_layer_b_markdown():
        validate_layer_b_non_authority_text(path, read_text(path))
    print("[PASS] registry provenance fences and Layer-B non-current authority are explicit")


def check_runtime_separation() -> None:
    hardening = read_text("phase6/scriptops-v2-hardening.py")
    runtime_class = classify_runtime_text(hardening)
    profile = observe_runtime_profile()
    validate_runtime_profile(
        runtime_class,
        profile,
        EXPECTED_FIELDS["X1B_ACTIVE_PRODUCT_REMEDIATION_ASSERTION"],
    )
    print(
        f"[PASS] checkout runtime profile = {runtime_class}; "
        "active-product state remains CURRENTNESS_UNESTABLISHED"
    )


def check_historical_decision_preservation() -> None:
    decision_log = read_text("DECISION_LOG.md")
    for marker in [
        "DEC-SO-001",
        "DEC-SO-010",
        "DEC-SO-011",
        "BASE: legacy/scriptops-v2-single.py",
        "REWRITE: NO",
        "NEW CAPABILITY: NO",
        "MATURITY CLAIM: NONE",
        "CANONICAL EFFECT EXECUTION:",
        "NOT AUTHORIZED WITHOUT SEPARATE HUMAN GATE",
    ]:
        if marker not in decision_log:
            raise VerificationError(f"historical decision marker missing: {marker}")
    scope = read_text("sources/RC1_SCOPE_LOCK.md")
    for marker in [
        "browser helper",
        "direct API calls",
        "autonomous writing",
        "multi-user",
        "AI Guard",
        "Retcon Engine",
        "cloud sync",
    ]:
        if marker not in scope:
            raise VerificationError(f"historical RC1 exclusion missing: {marker}")
    print("[PASS] historical decisions/scope preserved behind non-current authority fences")


def expect_failure(label: str, func: Callable[[], object]) -> None:
    try:
        func()
    except VerificationError:
        return
    raise VerificationError(f"synthetic rejection did not fail: {label}")


def expect_failure_message(
    label: str,
    expected_message: str,
    func: Callable[[], object],
) -> None:
    try:
        func()
    except VerificationError as exc:
        if expected_message not in str(exc):
            raise VerificationError(
                f"synthetic rejection failed for wrong reason: {label}: {exc}"
            ) from exc
        return
    raise VerificationError(f"synthetic rejection did not fail: {label}")


def check_synthetic_rejections_and_transition_positives() -> None:
    base = list(FROZEN_REGISTRY)

    # R1-R2: new Layer-A members.
    expect_failure("R1 new root Markdown", lambda: validate_registry(base + ["CURRENT_STATUS.md"], REGISTRY_ENTRIES))
    expect_failure("R2 new direct sources Markdown", lambda: validate_registry(base + ["sources/CurrentFoo.md"], REGISTRY_ENTRIES))

    # R3-R5: registry mapping integrity/current authority count.
    duplicate = list(REGISTRY_ENTRIES) + [("README.md", "HISTORICAL_RECONSTRUCTION_PROVENANCE_ONLY")]
    expect_failure("R3 duplicate registry class", lambda: validate_registry(base, duplicate))
    expect_failure("R4 omitted registry class", lambda: validate_registry(base, REGISTRY_ENTRIES[:-1]))
    four_current = [
        (p, "CURRENT_BOOTSTRAP_AUTHORITY" if p in CURRENT_BOOTSTRAP | {"DECISION_LOG.md"} else c)
        for p, c in REGISTRY_ENTRIES
    ]
    expect_failure("R5 four current bootstrap members", lambda: validate_registry(base, four_current))

    # R6-R8: nested RESTORE cannot enter Layer A or cardinality 14.
    expect_failure("R6 recursive RESTORE inclusion", lambda: validate_registry(base + ["sources/prototype/RESTORE.md"], REGISTRY_ENTRIES))
    expect_failure("R7 special-case RESTORE append", lambda: validate_registry(base + ["sources/prototype/RESTORE.md"], REGISTRY_ENTRIES))
    expect_failure("R8 Layer-A cardinality 14", lambda: validate_registry(base + ["extra.md"], REGISTRY_ENTRIES))

    # R9-R10: Layer-B known prefix allowed; unknown location fails closed.
    if classify_nonregistry_markdown_path("sources/prototype/extra.md") != "DENIED_BY_PATH_CLASS":
        raise VerificationError("R9 known nested provenance path not denied")
    expect_failure("R10 unknown docs prefix", lambda: classify_nonregistry_markdown_path("docs/Current.md"))

    # R11-R16: provenance fences cannot disappear or promote authority.
    expect_failure("R11 SOURCES fence removed", lambda: validate_provenance_text("SOURCES.md", "historical text only"))
    sources_with_stale_current_next = (
        read_text("SOURCES.md") + "\nACCESS CHECK REQUIRED = CURRENT NEXT\n"
    )
    expect_failure_message(
        "R12 ACCESS CHECK restored as current next",
        "publishes forbidden stale current-next authority",
        lambda: validate_provenance_text("SOURCES.md", sources_with_stale_current_next),
    )
    expect_failure(
        "R13 decision provenance mapped active",
        lambda: validate_provenance_text(
            "DECISION_LOG.md",
            read_text("DECISION_LOG.md")
            + "\nX1B_ACTIVE_PRODUCT_REMEDIATION_ASSERTION: CONFIRMED_REMEDIATED\n",
        ),
    )
    main_theme_with_authorship_promotion = (
        read_text("sources/ScriptOps_Main_Theme_Summary.md")
        + "\nGENERIC HUMAN APPROVAL = X1B HumanDecision AUTHORSHIP EVIDENCE\n"
    )
    expect_failure_message(
        "R14 Main Theme generic approval promoted",
        "publishes forbidden Human-authorship promotion",
        lambda: validate_provenance_text(
            "sources/ScriptOps_Main_Theme_Summary.md",
            main_theme_with_authorship_promotion,
        ),
    )
    expect_failure(
        "R15 RC1 scope promoted",
        lambda: validate_provenance_text(
            "sources/RC1_SCOPE_LOCK.md",
            read_text("sources/RC1_SCOPE_LOCK.md") + "\nCURRENT X1B AUTHORITY = YES\n",
        ),
    )
    expect_failure("R16 source audit fence removed", lambda: validate_provenance_text("SOURCE_AUDIT_SUMMARY.md", "audit"))

    # R17-R20: current trio disagreement / ontic promotion.
    good = {p: read_text(p) for p in CURRENT_BOOTSTRAP}
    disagree = dict(good)
    disagree["HANDOFF.md"] = disagree["HANDOFF.md"].replace(
        "X1B_ACTIVE_PRODUCT_ASSERTION_EVIDENCE: NONE_ACCEPTED_FOR_THIS_STATUS_PUBLICATION",
        "X1B_ACTIVE_PRODUCT_ASSERTION_EVIDENCE: SOMETHING_ELSE",
        1,
    )
    expect_failure("R17 trio disagreement", lambda: validate_current_schema(disagree))

    for label, value in [
        ("R18 confirmed not remediated", "CONFIRMED_NOT_REMEDIATED"),
        ("R19 confirmed remediated", "CONFIRMED_REMEDIATED"),
        ("R20 boolean collapse", "YES"),
    ]:
        bad = dict(good)
        bad["README.md"] = bad["README.md"].replace(
            "X1B_ACTIVE_PRODUCT_REMEDIATION_ASSERTION: CURRENTNESS_UNESTABLISHED",
            f"X1B_ACTIVE_PRODUCT_REMEDIATION_ASSERTION: {value}",
            1,
        )
        expect_failure(label, lambda bad=bad: validate_current_schema(bad))

    # P7/P8 and R21-R23: exercise the same full profile validator used by main().
    legacy_text = 'approve.add_argument("--why", required=True)\n"approver": "human"\n'
    v2_text = (
        'x1b.approve_scene(scene, decision_pr)\n'
        'approve.add_argument("--decision-pr", required=True, type=int)\n'
        'HumanDecision=TRUE\n'
    )
    if classify_runtime_text(legacy_text) != "LEGACY_PRE_X1B":
        raise VerificationError("synthetic legacy classifier failed")
    if classify_runtime_text(v2_text) != "X1B_V2_CHECKOUT":
        raise VerificationError("synthetic V2 classifier failed")

    validate_runtime_profile(
        "LEGACY_PRE_X1B",
        dict(RUNTIME_PROFILES["LEGACY_PRE_X1B"]),
        "CURRENTNESS_UNESTABLISHED",
    )
    validate_runtime_profile(
        "X1B_V2_CHECKOUT",
        dict(RUNTIME_PROFILES["X1B_V2_CHECKOUT"]),
        "CURRENTNESS_UNESTABLISHED",
    )

    expect_failure(
        "R21 V2 promotes active state",
        lambda: validate_runtime_profile(
            "X1B_V2_CHECKOUT",
            dict(RUNTIME_PROFILES["X1B_V2_CHECKOUT"]),
            "CONFIRMED_REMEDIATED",
        ),
    )
    expect_failure(
        "R22 legacy promotes negative active state",
        lambda: validate_runtime_profile(
            "LEGACY_PRE_X1B",
            dict(RUNTIME_PROFILES["LEGACY_PRE_X1B"]),
            "CONFIRMED_NOT_REMEDIATED",
        ),
    )
    expect_failure(
        "R23 unknown runtime class",
        lambda: validate_runtime_currentness("UNKNOWN", "CURRENTNESS_UNESTABLISHED"),
    )

    # R24 supporting document cannot publish consequential authority.
    expect_failure(
        "R24 supporting merge authority",
        lambda: validate_provenance_text(
            "DECISION_LOG.md",
            read_text("DECISION_LOG.md") + "\nMERGE AUTHORITY = YES\n",
        ),
    )

    # F006-specific mixed-profile regression: a recognized V2 label cannot pass
    # with legacy transition blobs (or vice versa).
    expect_failure(
        "F006 mixed V2/legacy runtime profile",
        lambda: validate_runtime_profile(
            "X1B_V2_CHECKOUT",
            dict(RUNTIME_PROFILES["LEGACY_PRE_X1B"]),
            "CURRENTNESS_UNESTABLISHED",
        ),
    )

    # F009: free-form Layer-B self-promotion must fail through the same
    # validator used by production check_provenance_surfaces().
    layer_b_baseline = "Historical supporting provenance. No current authority is granted here."
    for label, claim in [
        ("F009 current authority self-promotion", "THIS DOCUMENT IS THE CURRENT X1B AUTHORITY"),
        ("F009 merge authorization self-promotion", "MERGE IS AUTHORIZED BY THIS DOCUMENT"),
        ("F009 free-form grant self-promotion", "THIS FILE GRANTS CANONICAL X1B AUTHORITY"),
    ]:
        expect_failure_message(
            label,
            "publishes forbidden self-promotion",
            lambda claim=claim: validate_layer_b_non_authority_text(
                "sources/prototype/extra.md",
                layer_b_baseline + "\n" + claim + "\n",
            ),
        )
    validate_layer_b_non_authority_text(
        "sources/prototype/extra.md",
        "HISTORICAL: MERGE IS NOT AUTHORIZED BY THIS DOCUMENT.\n",
    )

    # F010: inert technical binding language must not be promoted into an
    # authority verb merely because a sentence is self-referential.
    validate_layer_b_non_authority_text(
        "acceptance/inert.md",
        "This file is the inert canonical payload for the X1D-A5 effect-method-binding live acceptance sequence.\n",
    )

    # F011: negation may include local modifiers between NOT and the authority
    # verb; those modifiers must not turn an explicit denial into promotion.
    validate_layer_b_non_authority_text(
        "acceptance/inert.md",
        "This artifact does not itself authorize a merge, Human D0, OperationAdmission, corrective closure, release, deployment, or tag.\n",
    )
    validate_layer_b_non_authority_text(
        "acceptance/inert.md",
        "This document does not by itself grant release authority.\n",
    )

    # F012: one negative promotion may not mask a distinct positive promotion
    # in the same conjunction clause. Boundary-local context resets at AND/OR.
    for label, mixed_claim in [
        (
            "F012 second self-reference promotion",
            "This document does not authorize merge and this file grants canonical X1B authority.",
        ),
        (
            "F012 same-subject second promotion",
            "This document does not authorize merge and grants release authority.",
        ),
        (
            "F012 historical first conjunct cannot mask positive second",
            "Historical: this document authorized merge and this file grants canonical X1B authority.",
        ),
    ]:
        expect_failure_message(
            label,
            "publishes forbidden self-promotion",
            lambda mixed_claim=mixed_claim: validate_layer_b_non_authority_text(
                "acceptance/inert.md",
                mixed_claim + "\n",
            ),
        )
    validate_layer_b_non_authority_text(
        "acceptance/inert.md",
        "This document does not authorize merge and does not grant release authority.\n",
    )

    # F013: punctuation-only/asydetic clause boundaries must also reset local
    # negation scope; the repair is generic comma segmentation, not a literal
    # match for the finding sentence.
    for label, comma_claim in [
        (
            "F013 comma asydetic hereby promotion",
            "This document does not grant release authority, it hereby authorizes merge.",
        ),
        (
            "F013 comma second self-reference promotion",
            "This record is not authoritative, these words grant merge authority.",
        ),
    ]:
        expect_failure_message(
            label,
            "publishes forbidden self-promotion",
            lambda comma_claim=comma_claim: validate_layer_b_non_authority_text(
                "acceptance/inert.md",
                comma_claim + "\n",
            ),
        )

    # F014: colon and explicit dash-style clause boundaries must reset local
    # negation scope without treating ordinary internal hyphens as separators.
    for label, boundary_claim in [
        (
            "F014 em-dash second self-reference promotion",
            "This document does not authorize merge — this file grants canonical X1B authority.",
        ),
        (
            "F014 colon second self-reference promotion",
            "This record is not authoritative: these words authorize deployment.",
        ),
        (
            "F014 spaced double-hyphen second promotion",
            "This document does not authorize merge -- this file grants release authority.",
        ),
    ]:
        expect_failure_message(
            label,
            "publishes forbidden self-promotion",
            lambda boundary_claim=boundary_claim: validate_layer_b_non_authority_text(
                "acceptance/inert.md",
                boundary_claim + "\n",
            ),
        )
    validate_layer_b_non_authority_text(
        "acceptance/inert.md",
        "This document does not authorize: merge, release, deployment, or tag.\n",
    )
    validate_layer_b_non_authority_text(
        "acceptance/inert.md",
        "This file is historical — this file does not grant merge authority.\n",
    )

    # F015: a later independent self-reference must reset negation subject
    # scope even when the delimiter is not enumerated by _authority_clauses().
    for label, subject_claim in [
        (
            "F015 parenthetical second self-reference promotion",
            "This document does not authorize merge (this file grants canonical X1B authority).",
        ),
        (
            "F015 bracket-delimited second self-reference promotion",
            "This document does not authorize merge [this file grants release authority].",
        ),
        (
            "F015 slash-delimited second self-reference promotion",
            "This record is not authoritative / these words authorize deployment.",
        ),
    ]:
        expect_failure_message(
            label,
            "publishes forbidden self-promotion",
            lambda subject_claim=subject_claim: validate_layer_b_non_authority_text(
                "acceptance/inert.md",
                subject_claim + "\n",
            ),
        )

    # A self-reference used as the object of a negated infinitive is not a
    # fresh authority subject and must remain an accepted negative statement.
    validate_layer_b_non_authority_text(
        "acceptance/inert.md",
        "This document does not authorize this file to grant release authority.\n",
    )
    validate_layer_b_non_authority_text(
        "acceptance/inert.md",
        "This document does not authorize merge (this file does not grant release authority).\n",
    )

    # F016: punctuation/parenthetical splitting may not sever a self-referential
    # subject from its positive authority predicate.
    for label, fragmented_claim in [
        (
            "F016 comma parenthetical subject-predicate promotion",
            "This file, therefore, grants release authority.",
        ),
        (
            "F016 descriptive parenthetical subject-predicate promotion",
            "This document, for clarity, authorizes merge.",
        ),
        (
            "F016 discourse-parenthetical subject-predicate promotion",
            "This file, however, grants canonical X1B authority.",
        ),
    ]:
        expect_failure_message(
            label,
            "publishes forbidden self-promotion",
            lambda fragmented_claim=fragmented_claim: validate_layer_b_non_authority_text(
                "acceptance/inert.md",
                fragmented_claim + "\n",
            ),
        )
    validate_layer_b_non_authority_text(
        "acceptance/inert.md",
        "This file, however, does not grant release authority.\n",
    )
    validate_layer_b_non_authority_text(
        "acceptance/inert.md",
        "This document, for clarity, does not authorize merge.\n",
    )

    # F017: Markdown soft wrapping is whitespace, not an authority boundary.
    # A self-referential subject and its predicate must therefore be evaluated
    # as one logical authority unit even when split over two or more lines.
    for label, multiline_claim in [
        (
            "F017 comma soft-wrap subject-predicate promotion",
            "This file,\ntherefore grants release authority.",
        ),
        (
            "F017 multi-soft-wrap subject-predicate promotion",
            "This document,\nfor clarity,\nauthorizes merge.",
        ),
        (
            "F017 unpunctuated soft-wrap subject-predicate promotion",
            "This record\ntherefore controls current X1B authority.",
        ),
        (
            "F017 multiline fresh-subject promotion after negation",
            "This document does not authorize merge,\nthis file grants canonical X1B authority.",
        ),
    ]:
        expect_failure_message(
            label,
            "publishes forbidden self-promotion",
            lambda multiline_claim=multiline_claim: validate_layer_b_non_authority_text(
                "acceptance/inert.md",
                multiline_claim + "\n",
            ),
        )

    # Benign multiline negation remains non-authoritative, including an
    # embedded self-reference used as the object of a negated infinitive.
    validate_layer_b_non_authority_text(
        "acceptance/inert.md",
        "This file,\ntherefore does not grant release authority.\n",
    )
    validate_layer_b_non_authority_text(
        "acceptance/inert.md",
        "This document,\nfor clarity,\ndoes not authorize merge.\n",
    )
    validate_layer_b_non_authority_text(
        "acceptance/inert.md",
        "This document does not authorize\nthis file to grant release authority.\n",
    )

    # F018: punctuation at a physical Markdown line end cannot be trusted as a
    # security boundary. Ellipses, abbreviations, and other apparent sentence
    # tails may still be ordinary soft wraps inside one authority claim.
    for label, false_tail_claim in [
        (
            "F018 ellipsis soft-wrap subject-predicate promotion",
            "This file...\ntherefore grants release authority.",
        ),
        (
            "F018 abbreviation soft-wrap subject-predicate promotion",
            "This document, e.g.\ntherefore authorizes merge.",
        ),
        (
            "F018 period-tail soft-wrap subject-predicate promotion",
            "This record.\ntherefore controls current X1B authority.",
        ),
    ]:
        expect_failure_message(
            label,
            "publishes forbidden self-promotion",
            lambda false_tail_claim=false_tail_claim: validate_layer_b_non_authority_text(
                "acceptance/inert.md",
                false_tail_claim + "\n",
            ),
        )

    # The broader paragraph folding remains fail-safe for explicit negative
    # authority statements, including the same ellipsis/abbreviation shapes.
    validate_layer_b_non_authority_text(
        "acceptance/inert.md",
        "This file...\ntherefore does not grant release authority.\n",
    )
    validate_layer_b_non_authority_text(
        "acceptance/inert.md",
        "This document, e.g.\ntherefore does not authorize merge.\n",
    )
    validate_layer_b_non_authority_text(
        "acceptance/inert.md",
        "This document does not authorize merge.\nThis file does not grant release authority.\n",
    )

    # F019: a blank physical line may separate continuation paragraphs inside
    # one Markdown list item. The item remains one security unit, but sibling
    # items and dedented paragraphs must not be globally joined.
    for label, list_item_claim in [
        (
            "F019 bullet blank-paragraph continuation promotion",
            "- This file...\n\n  therefore grants release authority.",
        ),
        (
            "F019 ordered-list blank-paragraph continuation promotion",
            "1. This document, e.g.\n\n   therefore authorizes merge.",
        ),
        (
            "F019 multi-paragraph list-item subject-predicate promotion",
            "- This document,\n\n  for clarity,\n\n  authorizes merge.",
        ),
    ]:
        expect_failure_message(
            label,
            "publishes forbidden self-promotion",
            lambda list_item_claim=list_item_claim: validate_layer_b_non_authority_text(
                "acceptance/inert.md",
                list_item_claim + "\n",
            ),
        )

    validate_layer_b_non_authority_text(
        "acceptance/inert.md",
        "- This file...\n\n  therefore does not grant release authority.\n",
    )
    validate_layer_b_non_authority_text(
        "acceptance/inert.md",
        "- This file contains background notes.\n- Release authority belongs to a separate Human gate.\n",
    )
    validate_layer_b_non_authority_text(
        "acceptance/inert.md",
        "- This file contains background notes.\n\nRelease authority belongs to a separate Human gate.\n",
    )

    # F020: nested siblings are distinct authority units, while each active
    # parent -> child path remains one unit so nesting cannot split a claim.
    for label, nested_claim in [
        (
            "F020 nested bullet continuation promotion",
            "- Parent context:\n  - This file...\n\n    therefore grants release authority.",
        ),
        (
            "F020 parent-child split promotion",
            "- This file:\n  - grants release authority.",
        ),
        (
            "F020 ordered-parent nested bullet continuation promotion",
            "1. Parent context:\n   - This document, e.g.\n\n     therefore authorizes merge.",
        ),
    ]:
        expect_failure_message(
            label,
            "publishes forbidden self-promotion",
            lambda nested_claim=nested_claim: validate_layer_b_non_authority_text(
                "acceptance/inert.md",
                nested_claim + "\n",
            ),
        )

    validate_layer_b_non_authority_text(
        "acceptance/inert.md",
        "- Parent context:\n  - This file contains background notes.\n\n"
        "  - Release authority belongs to a separate Human gate.\n",
    )
    validate_layer_b_non_authority_text(
        "acceptance/inert.md",
        "1. Parent context:\n   1. This file contains background notes.\n\n"
        "   2. Release authority belongs to a separate Human gate.\n",
    )
    validate_layer_b_non_authority_text(
        "acceptance/inert.md",
        "- Parent context:\n  - This file...\n\n"
        "    therefore does not grant release authority.\n",
    )

    # F021: once a list path is active, deeper valid nested markers may begin
    # at four or more absolute columns. Deep siblings remain separate units,
    # while a continuation within one deep leaf remains folded with that leaf.
    for label, deep_nested_claim in [
        (
            "F021 third-level bullet continuation promotion",
            "- Parent:\n  - Child context:\n    - This file...\n\n"
            "      therefore grants release authority.",
        ),
        (
            "F021 mixed ordered/unordered deep continuation promotion",
            "1. Parent:\n   - Child context:\n     1. This document, e.g.\n\n"
            "        therefore authorizes merge.",
        ),
    ]:
        expect_failure_message(
            label,
            "publishes forbidden self-promotion",
            lambda deep_nested_claim=deep_nested_claim: validate_layer_b_non_authority_text(
                "acceptance/inert.md",
                deep_nested_claim + "\n",
            ),
        )

    validate_layer_b_non_authority_text(
        "acceptance/inert.md",
        "- Parent:\n  - Child context:\n"
        "    - This file contains background notes.\n\n"
        "    - Release authority belongs to a separate Human gate.\n",
    )
    validate_layer_b_non_authority_text(
        "acceptance/inert.md",
        "1. Parent:\n   - Child context:\n"
        "     1. This file contains background notes.\n\n"
        "     2. Release authority belongs to a separate Human gate.\n",
    )
    validate_layer_b_non_authority_text(
        "acceptance/inert.md",
        "- Parent:\n  - Child context:\n    - This file...\n\n"
        "      therefore does not grant release authority.\n",
    )
    # F040 sharpens the F021 control: blank lines separate indented chunks but
    # do not split one indented code block. Rejecting this pair preserves F021's
    # invariant that four-space bullet-looking text is not a top-level list.
    expect_failure_message(
        "F021 standalone four-space bullet-like chunks remain one code block",
        "publishes forbidden self-promotion",
        lambda: validate_layer_b_non_authority_text(
            "acceptance/inert.md",
            "    - This file contains background notes.\n\n"
            "    - Release authority belongs to a separate Human gate.\n",
        ),
    )

    # F022: after a blank line, deep-marker parsing is permitted only after
    # indentation ownership has been resolved against the active list path.
    # A wide ordered item therefore cannot absorb a separate four-space
    # bullet-like code block, while truly owned descendants/continuations keep
    # their inherited security context.
    validate_layer_b_non_authority_text(
        "acceptance/inert.md",
        "10)  This file contains background notes.\n\n"
        "    - Release authority belongs to a separate Human gate.\n",
    )

    for label, owned_after_blank_claim in [
        (
            "F022 wide ordered valid nested descendant promotion",
            "10)  This file...\n\n"
            "     - grants release authority.",
        ),
        (
            "F022 wide ordered same-item continuation promotion",
            "10)  This file...\n\n"
            "     therefore grants release authority.",
        ),
    ]:
        expect_failure_message(
            label,
            "publishes forbidden self-promotion",
            lambda owned_after_blank_claim=owned_after_blank_claim: validate_layer_b_non_authority_text(
                "acceptance/inert.md",
                owned_after_blank_claim + "\n",
            ),
        )

    # F023: marker-only empty list items are real boundaries, including nested
    # siblings, but an empty item may not interrupt an active ordinary
    # paragraph. The benign controls close stale-frame absorption; the positive
    # controls ensure the new boundary handling cannot split a promotion.
    validate_layer_b_non_authority_text(
        "acceptance/inert.md",
        "- This file contains background notes.\n-\n\n"
        "Release authority belongs to a separate Human gate.\n",
    )
    validate_layer_b_non_authority_text(
        "acceptance/inert.md",
        "1. This file contains background notes.\n2.\n\n"
        "Release authority belongs to a separate Human gate.\n",
    )
    validate_layer_b_non_authority_text(
        "acceptance/inert.md",
        "- Parent:\n  - This file contains background notes.\n  -\n\n"
        "  Release authority belongs to a separate Human gate.\n",
    )

    for label, empty_marker_claim in [
        (
            "F023 bare bullet cannot interrupt paragraph",
            "This file\n-\ngrants release authority.",
        ),
        (
            "F023 whitespace-only bullet cannot interrupt paragraph",
            "This file\n-   \ngrants release authority.",
        ),
        (
            "F023 bare ordered item cannot interrupt paragraph",
            "This document\n2.\nauthorizes merge.",
        ),
        (
            "F023 marker-only parent retains nested promotion",
            "-\n  - This file grants release authority.",
        ),
    ]:
        expect_failure_message(
            label,
            "publishes forbidden self-promotion",
            lambda empty_marker_claim=empty_marker_claim: validate_layer_b_non_authority_text(
                "acceptance/inert.md",
                empty_marker_claim + "\n",
            ),
        )

    # F024: an empty marker starts an item with a blank line. Trailing marker
    # whitespace cannot inflate content indentation and split later paragraphs
    # that CommonMark keeps inside that same item.
    for label, blank_start_item_claim in [
        (
            "F024 bullet trailing-spaces blank-start continuation promotion",
            "-    \n  This file contains background notes.\n\n"
            "  therefore grants release authority.",
        ),
        (
            "F024 ordered trailing-spaces blank-start continuation promotion",
            "10)    \n    This document, e.g.\n\n"
            "    therefore authorizes merge.",
        ),
        (
            "F024 bullet trailing-tab blank-start continuation promotion",
            "-\t\n  This record\n\n"
            "  therefore controls current X1B authority.",
        ),
        (
            "F024 nested trailing-spaces blank-start continuation promotion",
            "- Parent:\n  -    \n    This file...\n\n"
            "    therefore grants release authority.",
        ),
    ]:
        expect_failure_message(
            label,
            "publishes forbidden self-promotion",
            lambda blank_start_item_claim=blank_start_item_claim: validate_layer_b_non_authority_text(
                "acceptance/inert.md",
                blank_start_item_claim + "\n",
            ),
        )

    validate_layer_b_non_authority_text(
        "acceptance/inert.md",
        "-    \n  Background notes only.\n\n"
        "  Release authority belongs to a separate Human gate.\n",
    )
    validate_layer_b_non_authority_text(
        "acceptance/inert.md",
        "10)   \n    This document is historical.\n\n"
        "    therefore does not authorize merge.\n",
    )

    # F025: a nonempty ordered marker may interrupt an active ordinary
    # paragraph only when its start number is one. Non-one markers remain
    # paragraph continuation, while valid bullet/one-start interruptions and
    # non-one siblings inside an established list remain distinct units.
    for label, nonone_ordered_claim in [
        (
            "F025 exact non-one ordered paragraph continuation promotion",
            "This file\n2. grants release authority.",
        ),
        (
            "F025 zero-paren ordered paragraph continuation promotion",
            "This document\n0) authorizes merge.",
        ),
        (
            "F025 multi-digit ordered paragraph continuation promotion",
            "This record\n42. controls current X1B authority.",
        ),
    ]:
        expect_failure_message(
            label,
            "publishes forbidden self-promotion",
            lambda nonone_ordered_claim=nonone_ordered_claim: validate_layer_b_non_authority_text(
                "acceptance/inert.md",
                nonone_ordered_claim + "\n",
            ),
        )

    # These markers may legally start a new list and therefore a new authority
    # unit when the item is nonempty.
    validate_layer_b_non_authority_text(
        "acceptance/inert.md",
        "This file contains background notes.\n"
        "- Release authority belongs to a separate Human gate.\n",
    )
    validate_layer_b_non_authority_text(
        "acceptance/inert.md",
        "This file contains background notes.\n"
        "1. Release authority belongs to a separate Human gate.\n",
    )
    validate_layer_b_non_authority_text(
        "acceptance/inert.md",
        "This document contains background notes.\n"
        "1) Merge authority belongs to a separate Human gate.\n",
    )
    validate_layer_b_non_authority_text(
        "acceptance/inert.md",
        "1. This file contains background notes.\n"
        "2. Release authority belongs to a separate Human gate.\n",
    )
    validate_layer_b_non_authority_text(
        "acceptance/inert.md",
        "This file\n2. does not grant release authority.\n",
    )

    # F026: CommonMark ordered-list markers are ASCII decimal digits only.
    # Unicode decimal-digit lookalikes must remain ordinary paragraph text;
    # otherwise a lookalike `1.` can create a false list boundary and split a
    # self-referential subject from its authority predicate.
    unicode_digit_markers = [
        ("Arabic-Indic", "١."),
        ("fullwidth", "１."),
        ("Devanagari", "१."),
    ]
    for label, marker in unicode_digit_markers:
        if _markdown_list_item_layout(f"{marker} grants release authority.") is not None:
            raise VerificationError(
                f"F026 {label} decimal-digit lookalike recognized as Markdown list marker"
            )

        unicode_digit_claim = f"This file\n{marker} grants release authority."
        expect_failure_message(
            f"F026 {label} digit lookalike paragraph continuation promotion",
            "publishes forbidden self-promotion",
            lambda unicode_digit_claim=unicode_digit_claim: validate_layer_b_non_authority_text(
                "acceptance/inert.md",
                unicode_digit_claim + "\n",
            ),
        )

    # Benign Unicode-digit text remains permitted when the authority predicate
    # is locally negated; F026 changes Markdown structure recognition only.
    validate_layer_b_non_authority_text(
        "acceptance/inert.md",
        "This file\n١. does not grant release authority.\n",
    )

    # F027: if a nonempty item starts with indented code, five-or-more columns
    # after the marker do not inflate the item's ownership indentation. One
    # structural column follows the marker; the rest belongs to the code block.
    ordered_code_layout = _markdown_list_item_layout("1.     This file")
    if ordered_code_layout is None or ordered_code_layout[1] != 3:
        raise VerificationError(
            "F027 ordered indented-code item ownership is not marker width plus one"
        )

    bullet_code_layout = _markdown_list_item_layout("-     This document")
    if bullet_code_layout is None or bullet_code_layout[1] != 2:
        raise VerificationError(
            "F027 bullet indented-code item ownership is not marker width plus one"
        )

    four_column_layout = _markdown_list_item_layout("1.    This file")
    if four_column_layout is None or four_column_layout[1] != 6:
        raise VerificationError(
            "F027 ordinary four-column post-marker indentation changed unexpectedly"
        )

    for label, indented_code_item_claim in [
        (
            "F027 ordered indented-code same-item promotion",
            "1.     This file\n\n   grants release authority.",
        ),
        (
            "F027 bullet indented-code same-item promotion",
            "-     This document\n\n  authorizes merge.",
        ),
        (
            "F027 nested indented-code same-item promotion",
            "- Parent:\n  1.     This file\n\n     grants release authority.",
        ),
    ]:
        expect_failure_message(
            label,
            "publishes forbidden self-promotion",
            lambda indented_code_item_claim=indented_code_item_claim: validate_layer_b_non_authority_text(
                "acceptance/inert.md",
                indented_code_item_claim + "\n",
            ),
        )

    # Benign controls: the W+1 correction must not absorb truly dedented text
    # or a following sibling into the preceding item.
    validate_layer_b_non_authority_text(
        "acceptance/inert.md",
        "1.     This file contains background notes.\n\n"
        "Release authority belongs to a separate Human gate.\n",
    )
    validate_layer_b_non_authority_text(
        "acceptance/inert.md",
        "1.     This file contains background notes.\n\n"
        "2. Release authority belongs to a separate Human gate.\n",
    )

    # F028: a non-one ordered-looking marker cannot interrupt an open paragraph
    # merely because it appears inside an active list path.
    for label, lazy_marker_claim in [
        (
            "F028 nested dot-marker lazy continuation promotion",
            "- Parent\n  10. This file\n  2. grants release authority.",
        ),
        (
            "F028 nested paren-marker lazy continuation promotion",
            "- Parent\n  10) This document\n  2) authorizes merge.",
        ),
    ]:
        expect_failure_message(
            label,
            "publishes forbidden self-promotion",
            lambda lazy_marker_claim=lazy_marker_claim: validate_layer_b_non_authority_text(
                "acceptance/inert.md",
                lazy_marker_claim + "\n",
            ),
        )

    # F029/F030 benign controls: ancestor/same-level structural boundaries must
    # not donate a self-reference to an unrelated following item/list.
    validate_layer_b_non_authority_text(
        "acceptance/inert.md",
        "1. Parent context\n"
        "   - This file contains background notes.\n"
        "2. grants release authority.\n",
    )
    validate_layer_b_non_authority_text(
        "acceptance/inert.md",
        "- This file contains background notes.\n"
        "2. grants release authority.\n",
    )
    validate_layer_b_non_authority_text(
        "acceptance/inert.md",
        "- This file contains background notes.\n"
        "+ grants release authority.\n",
    )
    validate_layer_b_non_authority_text(
        "acceptance/inert.md",
        "1. This file contains background notes.\n"
        "2) grants release authority.\n",
    )

    # F031: ordinary lazy continuation may lose some or all item indentation.
    for label, lazy_text_claim in [
        (
            "F031 unindented bullet-item lazy continuation promotion",
            "- This file\ngrants release authority.",
        ),
        (
            "F031 partially dedented bullet-item lazy continuation promotion",
            "- This document\n authorizes merge.",
        ),
        (
            "F031 nested lazy continuation promotion",
            "- Parent\n  - This file\ngrants release authority.",
        ),
    ]:
        expect_failure_message(
            label,
            "publishes forbidden self-promotion",
            lambda lazy_text_claim=lazy_text_claim: validate_layer_b_non_authority_text(
                "acceptance/inert.md",
                lazy_text_claim + "\n",
            ),
        )

    # F032: thematic breaks are structural boundaries and take precedence over
    # possible list-item parsing. A top-level break after a list closes that
    # list; later ordinary paragraph text may not inherit its self-reference.
    for label, thematic_boundary_text in [
        (
            "F032 dash thematic break closes list",
            "- This file\n---\ngrants release authority.",
        ),
        (
            "F032 star thematic break closes list",
            "- This file\n***\ngrants release authority.",
        ),
        (
            "F032 underscore thematic break closes list",
            "- This file\n___\ngrants release authority.",
        ),
        (
            "F032 spaced dash thematic break closes list",
            "- This file\n- - -\ngrants release authority.",
        ),
        (
            "F032 one-column dash thematic break closes list",
            "- This file\n ---\ngrants release authority.",
        ),
        (
            "F032 owned star break outranks nested bullet parsing",
            "- This file\n  * * *\ngrants release authority.",
        ),
    ]:
        validate_layer_b_non_authority_text(
            "acceptance/inert.md",
            thematic_boundary_text + "\n",
        )

    # The helper accepts the CommonMark marker shape and rejects lookalikes.
    for thematic_line in ["---", "***", "___", "- - -", "* * *", "_ _ _", "   ---"]:
        if _markdown_thematic_break_layout(thematic_line) is None:
            raise VerificationError(
                f"F032 valid thematic break not recognized: {thematic_line!r}"
            )
    for non_thematic_line in ["--", "**", "__", "*-*", "---a---", "++++", "    ---"]:
        if _markdown_thematic_break_layout(non_thematic_line) is not None:
            raise VerificationError(
                f"F032 non-thematic line recognized as thematic break: {non_thematic_line!r}"
            )

    # A dash-only underline owned by the current open leaf remains a setext
    # candidate in this bounded repair; it must not be silently reclassified as
    # a thematic break just to satisfy F032.
    expect_failure_message(
        "F032 current-leaf setext precedence preserved",
        "publishes forbidden self-promotion",
        lambda: validate_layer_b_non_authority_text(
            "acceptance/inert.md",
            "- This file\n  ---\n  grants release authority.\n",
        ),
    )

    # More than three columns beyond every owning content indent is not a
    # thematic break for that list path merely because a list frame exists.
    expect_failure_message(
        "F032 deep code-like thematic text not promoted to boundary",
        "publishes forbidden self-promotion",
        lambda: validate_layer_b_non_authority_text(
            "acceptance/inert.md",
            "- This file\n      ***\n  grants release authority.\n",
        ),
    )

    # Invalid thematic-break shapes remain paragraph/list-item text and cannot
    # be used to manufacture a security boundary.
    for label, invalid_line in [
        ("too few markers", "--"),
        ("mixed markers", "*-*"),
        ("payload after markers", "---a---"),
    ]:
        invalid_claim = f"- This file\n{invalid_line}\ngrants release authority."
        expect_failure_message(
            f"F032 {label}",
            "publishes forbidden self-promotion",
            lambda invalid_claim=invalid_claim: validate_layer_b_non_authority_text(
                "acceptance/inert.md",
                invalid_claim + "\n",
            ),
        )

    # F033: top-level thematic breaks also interrupt ordinary paragraphs. The
    # following paragraph must not inherit a self-reference from the preceding
    # paragraph merely because there is no blank line around the block marker.
    for label, top_level_boundary_text in [
        (
            "F033 top-level star thematic break",
            "This file\n***\ngrants release authority.",
        ),
        (
            "F033 top-level underscore thematic break",
            "This document\n___\nauthorizes merge.",
        ),
        (
            "F033 top-level spaced thematic break",
            "This record\n* * *\ncontrols current X1B authority.",
        ),
        (
            "F033 three-column thematic break",
            "This file\n   ***\ngrants release authority.",
        ),
        (
            "F033 top-level dash setext underline",
            "This file\n---\ngrants release authority.",
        ),
    ]:
        validate_layer_b_non_authority_text(
            "acceptance/inert.md",
            top_level_boundary_text + "\n",
        )

    # Invalid top-level lookalikes remain ordinary paragraph text. F033 must not
    # manufacture a boundary from too few markers, mixed markers, or payload.
    for label, invalid_top_level_line in [
        ("too few markers", "**"),
        ("mixed markers", "*-*"),
        ("payload after markers", "***payload"),
    ]:
        invalid_top_level_claim = (
            f"This file\n{invalid_top_level_line}\ngrants release authority."
        )
        expect_failure_message(
            f"F033 {label}",
            "publishes forbidden self-promotion",
            lambda invalid_top_level_claim=invalid_top_level_claim: validate_layer_b_non_authority_text(
                "acceptance/inert.md",
                invalid_top_level_claim + "\n",
            ),
        )

    # F034: valid CommonMark ATX headings interrupt paragraphs. Top-level
    # headings are separate authority units, while headings owned by one list
    # item inherit that item's security context.
    for label, atx_boundary_text in [
        (
            "F034 top-level h1 boundary",
            "This file\n# grants release authority.",
        ),
        (
            "F034 top-level h6 boundary",
            "This document\n###### authorizes merge.",
        ),
        (
            "F034 three-column top-level boundary",
            "This record\n   ### controls current X1B authority.",
        ),
        (
            "F034 empty heading boundary",
            "This file\n#\ngrants release authority.",
        ),
        (
            "F034 top-level heading closes list",
            "- This file\n# grants release authority.",
        ),
        (
            "F034 ancestor-owned heading closes nested child",
            "- Parent context\n  - This file\n  # grants release authority.",
        ),
    ]:
        validate_layer_b_non_authority_text(
            "acceptance/inert.md",
            atx_boundary_text + "\n",
        )

    # A heading remains security-relevant on its own, and an owned heading
    # keeps the owning list item's context rather than manufacturing a bypass.
    for label, owned_or_self_claim in [
        (
            "F034 heading self-promotion remains rejected",
            "# This file grants release authority.",
        ),
        (
            "F034 current-item heading inherits self-reference",
            "- This file\n  # grants release authority.",
        ),
        (
            "F034 ancestor-owned heading inherits parent self-reference",
            "- This file\n  - Child context\n  # grants release authority.",
        ),
    ]:
        expect_failure_message(
            label,
            "publishes forbidden self-promotion",
            lambda owned_or_self_claim=owned_or_self_claim: validate_layer_b_non_authority_text(
                "acceptance/inert.md",
                owned_or_self_claim + "\n",
            ),
        )

    # The helper accepts only the CommonMark ATX opening shape. Invalid
    # lookalikes must stay paragraph/lazy text and therefore cannot split a
    # subject from a later authority predicate.
    for atx_line in ["#", "# heading", "###### heading", "   ### heading", "### heading ###"]:
        if _markdown_atx_heading_layout(atx_line) is None:
            raise VerificationError(
                f"F034 valid ATX heading not recognized: {atx_line!r}"
            )
    for non_atx_line in ["####### heading", "#hashtag", "#5 bolt", "\\# heading", "    # heading"]:
        if _markdown_atx_heading_layout(non_atx_line) is not None:
            raise VerificationError(
                f"F034 non-ATX line recognized as heading: {non_atx_line!r}"
            )

    for label, invalid_atx_line in [
        ("seven hashes", "#######"),
        ("hashtag", "#hashtag"),
        ("escaped opener", "\\#"),
        ("four-column indent", "    #"),
    ]:
        invalid_atx_claim = (
            f"This file\n{invalid_atx_line} grants release authority."
        )
        expect_failure_message(
            f"F034 {label}",
            "publishes forbidden self-promotion",
            lambda invalid_atx_claim=invalid_atx_claim: validate_layer_b_non_authority_text(
                "acceptance/inert.md",
                invalid_atx_claim + "\n",
            ),
        )

    # F035: block quotes interrupt ordinary paragraphs, but quoted paragraph
    # continuation may lazily omit the marker. Top-level quotes are separate
    # security units; list-owned quotes inherit only their owning list path.
    for label, quote_boundary_text in [
        (
            "F035 top-level quote boundary",
            "This file\n> grants release authority.",
        ),
        (
            "F035 three-column quote boundary",
            "This document\n   > authorizes merge.",
        ),
        (
            "F035 no-space quote marker boundary",
            "This record\n>controls current X1B authority.",
        ),
        (
            "F035 top-level quote closes list",
            "- This file\n> grants release authority.",
        ),
        (
            "F035 quoted paragraph followed by ATX",
            "> This file\n# grants release authority.",
        ),
        (
            "F035 quoted paragraph followed by thematic break",
            "> This file\n***\ngrants release authority.",
        ),
        (
            "F035 quoted paragraph followed by bullet",
            "> This file\n- grants release authority.",
        ),
        (
            "F035 quoted heading does not donate to outside paragraph",
            "> # This file\ngrants release authority.",
        ),
    ]:
        validate_layer_b_non_authority_text(
            "acceptance/inert.md",
            quote_boundary_text + "\n",
        )

    for label, quoted_or_owned_claim in [
        (
            "F035 explicit quoted continuation promotion",
            "> This file\n> grants release authority.",
        ),
        (
            "F035 lazy quoted continuation promotion",
            "> This file\ngrants release authority.",
        ),
        (
            "F035 non-one ordered lazy quote continuation",
            "> This file\n2. grants release authority.",
        ),
        (
            "F035 current-item owned quote promotion",
            "- This file\n  > grants release authority.",
        ),
        (
            "F035 ancestor-owned quote promotion",
            "- This file\n  - Child context\n  > grants release authority.",
        ),
    ]:
        expect_failure_message(
            label,
            "publishes forbidden self-promotion",
            lambda quoted_or_owned_claim=quoted_or_owned_claim: validate_layer_b_non_authority_text(
                "acceptance/inert.md",
                quoted_or_owned_claim + "\n",
            ),
        )

    for quote_line in ["> quote", ">quote", "   > quote"]:
        if _markdown_block_quote_layout(quote_line) is None:
            raise VerificationError(
                f"F035 valid block-quote marker not recognized: {quote_line!r}"
            )
    for non_quote_line in ["\\> quote", "    > quote"]:
        if _markdown_block_quote_layout(non_quote_line) is not None:
            raise VerificationError(
                f"F035 non-quote line recognized as block quote: {non_quote_line!r}"
            )

    for label, non_boundary_claim in [
        ("escaped quote marker", "This file\n\\> grants release authority."),
        ("four-column quote-like text", "This file\n    > grants release authority."),
    ]:
        expect_failure_message(
            f"F035 {label}",
            "publishes forbidden self-promotion",
            lambda non_boundary_claim=non_boundary_claim: validate_layer_b_non_authority_text(
                "acceptance/inert.md",
                non_boundary_claim + "\n",
            ),
        )

    # F036: fenced code blocks interrupt paragraphs without blank lines. Their
    # literal payload is a separate top-level unit, while list-owned fenced
    # payload remains in the owning list-item security context.
    for label, fenced_boundary_text in [
        (
            "F036 top-level backtick fence boundary",
            "This file\n```\ngrants release authority.\n```",
        ),
        (
            "F036 top-level tilde fence boundary",
            "This document\n~~~\nauthorizes merge.\n~~~",
        ),
        (
            "F036 three-column top-level fence boundary",
            "This record\n   ```\ncontrols current X1B authority.\n   ```",
        ),
        (
            "F036 unclosed top-level fence reaches EOF",
            "This file\n```\ngrants release authority.",
        ),
        (
            "F036 paragraph immediately after closing fence",
            "This file\n```\nbackground only\n```\ngrants release authority.",
        ),
        (
            "F036 top-level fence closes active list",
            "- This file\n```\ngrants release authority.\n```",
        ),
        (
            "F036 quoted fence opener blocks lazy outside donation",
            "> This file\n> ```\ngrants release authority.",
        ),
        (
            "F036 owned fence close re-resolves dedented text",
            "- This file\n  ```\n  background\n  ```\ngrants release authority.",
        ),
    ]:
        validate_layer_b_non_authority_text(
            "acceptance/inert.md",
            fenced_boundary_text + "\n",
        )

    for label, fenced_claim in [
        (
            "F036 fenced payload self-promotion",
            "```\nThis file\ngrants release authority.\n```",
        ),
        (
            "F036 current-item owned fenced promotion",
            "- This file\n  ```\n  grants release authority.\n  ```",
        ),
        (
            "F036 ancestor-owned fenced promotion",
            "- This file\n  - Child context\n  ```\n  grants release authority.\n  ```",
        ),
        (
            "F036 too-short closing fence remains literal",
            "````\nThis file\n```\ngrants release authority.\n````",
        ),
        (
            "F036 wrong-character closing fence remains literal",
            "~~~\nThis file\n```\ngrants release authority.\n~~~",
        ),
    ]:
        expect_failure_message(
            label,
            "publishes forbidden self-promotion",
            lambda fenced_claim=fenced_claim: validate_layer_b_non_authority_text(
                "acceptance/inert.md",
                fenced_claim + "\n",
            ),
        )

    for fence_line in ["```", "```` python", "~~~ text", "   ```"]:
        if _markdown_fenced_code_opening_layout(fence_line) is None:
            raise VerificationError(
                f"F036 valid fenced-code opener not recognized: {fence_line!r}"
            )

    for non_fence_line in ["``", "~~", "    ```", "``` bad`info", "` ``"]:
        if _markdown_fenced_code_opening_layout(non_fence_line) is not None:
            raise VerificationError(
                f"F036 invalid fenced-code opener recognized: {non_fence_line!r}"
            )

    if _markdown_fenced_code_closing_layout("````  ", "`", 4) != 0:
        raise VerificationError("F036 matching backtick closing fence not recognized")
    if _markdown_fenced_code_closing_layout("```", "`", 4) is not None:
        raise VerificationError("F036 too-short closing fence recognized")
    if _markdown_fenced_code_closing_layout("~~~~", "`", 4) is not None:
        raise VerificationError("F036 wrong-character closing fence recognized")

    for label, invalid_opening_claim in [
        ("too few backticks", "This file\n``\ngrants release authority."),
        ("four-column opening", "This file\n    ```\ngrants release authority."),
        ("backtick in info string", "This file\n``` bad`info\ngrants release authority."),
    ]:
        expect_failure_message(
            f"F036 {label}",
            "publishes forbidden self-promotion",
            lambda invalid_opening_claim=invalid_opening_claim: validate_layer_b_non_authority_text(
                "acceptance/inert.md",
                invalid_opening_claim + "\n",
            ),
        )

    # F037: equals-family setext underlines terminate open paragraphs/headings
    # without requiring a blank line afterward. List/quote container controls
    # preserve their own ownership and CommonMark lazy-continuation rules.
    for label, setext_boundary_text in [
        (
            "F037 top-level equals boundary",
            "This file\n===\ngrants release authority.",
        ),
        (
            "F037 single-equals boundary",
            "This document\n=\nauthorizes merge.",
        ),
        (
            "F037 three-column equals boundary",
            "This record\n   ===\ncontrols current X1B authority.",
        ),
        (
            "F037 multiline heading boundary",
            "This\nfile\n===\ngrants release authority.",
        ),
        (
            "F037 equals line closes active list",
            "- This file\n===\ngrants release authority.",
        ),
        (
            "F037 current-item owned heading then dedented paragraph",
            "- This file\n  ===\ngrants release authority.",
        ),
        (
            "F037 explicit quoted heading blocks outside lazy donation",
            "> This file\n> ===\ngrants release authority.",
        ),
    ]:
        validate_layer_b_non_authority_text(
            "acceptance/inert.md",
            setext_boundary_text + "\n",
        )

    for label, setext_owned_claim in [
        (
            "F037 heading text self-promotion remains rejected",
            "This file grants release authority.\n===",
        ),
        (
            "F037 owned list heading keeps same-item security context",
            "- This file\n  ===\n  grants release authority.",
        ),
        (
            "F037 quoted heading keeps quoted security context",
            "> This file\n> ===\n> grants release authority.",
        ),
        (
            "F037 unmarked equals remains block-quote lazy text",
            "> This file\ngrants release authority.\n===",
        ),
    ]:
        expect_failure_message(
            label,
            "publishes forbidden self-promotion",
            lambda setext_owned_claim=setext_owned_claim: validate_layer_b_non_authority_text(
                "acceptance/inert.md",
                setext_owned_claim + "\n",
            ),
        )

    for setext_line in ["=", "===", "   ===", "---", "  ---\t"]:
        if _markdown_setext_heading_underline_layout(setext_line) is None:
            raise VerificationError(
                f"F037 valid setext underline not recognized: {setext_line!r}"
            )

    for non_setext_line in ["= =", "=== payload", "\\===", "    ==="]:
        if _markdown_setext_heading_underline_layout(non_setext_line) is not None:
            raise VerificationError(
                f"F037 invalid setext underline recognized: {non_setext_line!r}"
            )

    for label, invalid_setext_claim in [
        ("internal spaces", "This file\n= =\ngrants release authority."),
        ("payload", "This file\n=== payload\ngrants release authority."),
        ("escaped underline", "This file\n\\===\ngrants release authority."),
        ("four-column underline", "This file\n    ===\ngrants release authority."),
    ]:
        expect_failure_message(
            f"F037 {label}",
            "publishes forbidden self-promotion",
            lambda invalid_setext_claim=invalid_setext_claim: validate_layer_b_non_authority_text(
                "acceptance/inert.md",
                invalid_setext_claim + "\n",
            ),
        )

    # F038: CommonMark HTML block types 1-6 may interrupt paragraphs and
    # retain literal raw contents until their normative end condition. Type 7
    # remains non-interrupting, so it may not manufacture a security boundary.
    for label, html_boundary_text in [
        (
            "F038 type-6 div boundary",
            "This file\n<div>\ngrants release authority.\n</div>",
        ),
        (
            "F038 type-1 same-line close boundary",
            "This file\n<style>body{}</style>\ngrants release authority.",
        ),
        (
            "F038 comment boundary",
            "This file\n<!-- raw -->\ngrants release authority.",
        ),
        (
            "F038 processing-instruction boundary",
            "This file\n<?raw?>\ngrants release authority.",
        ),
        (
            "F038 declaration boundary",
            "This file\n<!DOCTYPE html>\ngrants release authority.",
        ),
        (
            "F038 CDATA boundary",
            "This file\n<![CDATA[ raw ]]>\ngrants release authority.",
        ),
        (
            "F038 type-6 blank termination",
            "This file\n<div>\nbackground\n\ngrants release authority.",
        ),
        (
            "F038 top-level HTML closes active list",
            "- This file\n<div>\ngrants release authority.\n</div>",
        ),
        (
            "F038 quoted HTML opener blocks lazy outside donation",
            "> This file\n> <div>\ngrants release authority.",
        ),
        (
            "F038 list-owned HTML ends before dedented paragraph",
            "- This file\n  <div>\n  background\n\ngrants release authority.",
        ),
    ]:
        validate_layer_b_non_authority_text(
            "acceptance/inert.md",
            html_boundary_text + "\n",
        )

    for label, html_claim in [
        (
            "F038 HTML payload self-promotion",
            "<div>\nThis file\ngrants release authority.\n</div>",
        ),
        (
            "F038 list-owned HTML promotion",
            "- This file\n  <div>\n  grants release authority.\n",
        ),
        (
            "F038 Markdown-looking fence stays literal inside HTML",
            "<div>\nThis file\n```\ngrants release authority.\n```",
        ),
        (
            "F038 four-column HTML-looking text is not a boundary",
            "This file\n    <div>\ngrants release authority.",
        ),
        (
            "F038 escaped HTML opener is not a boundary",
            "This file\n\\<div>\ngrants release authority.",
        ),
        (
            "F038 type-7 custom tag cannot interrupt paragraph",
            "This file\n<x-widget>\ngrants release authority.",
        ),
    ]:
        expect_failure_message(
            label,
            "publishes forbidden self-promotion",
            lambda html_claim=html_claim: validate_layer_b_non_authority_text(
                "acceptance/inert.md",
                html_claim + "\n",
            ),
        )

    for html_line, expected_type in [
        ("<div>", 6),
        ("</TABLE>", 6),
        ("   <div class=x", 6),
        ("<pre>", 1),
        ("<!-- x", 2),
        ("<?x", 3),
        ("<!DOCTYPE", 4),
        ("<![CDATA[", 5),
    ]:
        html_layout = _markdown_html_block_start_layout(html_line)
        if html_layout is None or html_layout[1] != expected_type:
            raise VerificationError(
                f"F038 valid HTML block opener not recognized: {html_line!r}"
            )

    for non_html_line in ["    <div>", "\\<div>", "<divx>", "<x-widget>"]:
        if _markdown_html_block_start_layout(non_html_line) is not None:
            raise VerificationError(
                f"F038 non-HTML-block line recognized as type 1-6: {non_html_line!r}"
            )

    for html_end_line, html_type in [
        ("x </style> y", 1),
        ("x --> y", 2),
        ("x ?> y", 3),
        ("x > y", 4),
        ("x ]]> y", 5),
        ("", 6),
    ]:
        if not _markdown_html_block_end_matches(html_end_line, html_type):
            raise VerificationError(
                f"F038 HTML block end not recognized: type={html_type} line={html_end_line!r}"
            )

    # F039: type-7 HTML blocks start only from complete standalone tags when no
    # paragraph is already open. Once started, Markdown-looking payload remains
    # literal until a blank line, container end, or EOF.
    for label, type7_claim in [
        (
            "F039 representative Warning raw ATX",
            "<Warning>\nThis file\n# grants release authority.\n</Warning>",
        ),
        (
            "F039 raw list marker remains literal",
            "<x-widget data-id=\"7\">\nThis document\n- authorizes merge.\n</x-widget>",
        ),
        (
            "F039 raw thematic marker remains literal",
            "<del>\nThis record\n***\ncontrols current X1B authority.\n</del>",
        ),
        (
            "F039 nested type-6 opener stays raw",
            "<Warning>\nThis file\n<div>\n# grants release authority.\n</Warning>",
        ),
        (
            "F039 unclosed type-7 reaches EOF",
            "<Warning>\nThis file\n# grants release authority.",
        ),
        (
            "F039 type-7 cannot interrupt open paragraph",
            "This file\n<Warning>\ngrants release authority.",
        ),
        (
            "F039 incomplete tag remains paragraph text",
            "This file\n<Warning\ngrants release authority.",
        ),
        (
            "F039 trailing payload prevents type-7 start",
            "This file\n<Warning> trailing\ngrants release authority.",
        ),
    ]:
        expect_failure_message(
            label,
            "publishes forbidden self-promotion",
            lambda type7_claim=type7_claim: validate_layer_b_non_authority_text(
                "acceptance/inert.md",
                type7_claim + "\n",
            ),
        )

    # A blank line ends type 7, so a later heading cannot borrow the raw block's
    # self-reference. Conversely, when type 7 appears inside an already-open
    # paragraph, a following ATX heading still interrupts that paragraph.
    validate_layer_b_non_authority_text(
        "acceptance/inert.md",
        "<Warning>\nThis file\n\n# grants release authority.\n",
    )
    validate_layer_b_non_authority_text(
        "acceptance/inert.md",
        "This file\n<Warning>\n# grants release authority.\n",
    )

    for type7_line in [
        "<Warning>",
        "   <x-widget data-id=\"7\">",
        "<a foo=bar />",
        "<i class='foo'>",
        "</ins>",
        "</pre>",
    ]:
        if _markdown_html_block_type7_start_layout(type7_line) is None:
            raise VerificationError(
                f"F039 valid type-7 tag line not recognized: {type7_line!r}"
            )

    for non_type7_line in [
        "    <Warning>",
        "<Warning",
        "<Warning> trailing",
        "<33>",
        "<__>",
        "</a href=\"x\">",
        "<pre>",
        "<script>",
    ]:
        if _markdown_html_block_type7_start_layout(non_type7_line) is not None:
            raise VerificationError(
                f"F039 invalid type-7 tag line recognized: {non_type7_line!r}"
            )

    if not _markdown_html_block_end_matches("", 7):
        raise VerificationError("F039 type-7 blank-line end not recognized")
    if _markdown_html_block_end_matches("payload", 7):
        raise VerificationError("F039 nonblank line ended type-7 HTML block")

    # F040: indented code is a literal leaf block. It cannot interrupt an open
    # paragraph, and dedented nonblank text after code must be reprocessed as a
    # new block rather than borrowed through paragraph-only lazy continuation.
    for benign_indented_code_boundary in [
        "    This file\ngrants release authority.",
        "    This file\n\n    background\ngrants release authority.",
        ">     This file\ngrants release authority.",
        "-     This file\ngrants release authority.",
        "- Parent\n\n      This file\ngrants release authority.",
    ]:
        validate_layer_b_non_authority_text(
            "acceptance/inert.md",
            benign_indented_code_boundary + "\n",
        )

    for label, indented_code_claim in [
        (
            "F040 top-level indented-code payload remains security-relevant",
            "    This file\n    grants release authority.",
        ),
        (
            "F040 indented code cannot interrupt open paragraph",
            "This file\n    grants release authority.",
        ),
        (
            "F040 three columns are not indented code",
            "   This file\ngrants release authority.",
        ),
        (
            "F040 quoted indented-code payload remains one quote context",
            ">     This file\n>     grants release authority.",
        ),
        (
            "F040 quoted open paragraph preserves non-interruption",
            "> This file\n>     background\ngrants release authority.",
        ),
        (
            "F040 initial list-owned code followed by same-item paragraph",
            "-     This file\n  grants release authority.",
        ),
        (
            "F040 later list-owned code followed by same-item paragraph",
            "- Parent\n\n      This file\n  grants release authority.",
        ),
    ]:
        expect_failure_message(
            label,
            "publishes forbidden self-promotion",
            lambda indented_code_claim=indented_code_claim: validate_layer_b_non_authority_text(
                "acceptance/inert.md",
                indented_code_claim + "\n",
            ),
        )

    if not _markdown_list_item_starts_indented_code("-     This file"):
        raise VerificationError("F040 bullet indented-code list start not recognized")
    if not _markdown_list_item_starts_indented_code("1.     This file"):
        raise VerificationError("F040 ordered indented-code list start not recognized")
    if _markdown_list_item_starts_indented_code("-    This file"):
        raise VerificationError("F040 four-column post-marker gap misclassified as code")

    # F041: a quoted indented-code leaf ends on the first explicit nonblank
    # quoted dedent. The new quoted paragraph is a separate top-level security
    # unit, but blank quoted lines remain inside one indented-code block.
    for benign_quoted_code_boundary in [
        ">     This file\n> grants release authority.",
        ">     This file\n> background\ngrants release authority.",
    ]:
        validate_layer_b_non_authority_text(
            "acceptance/inert.md",
            benign_quoted_code_boundary + "\n",
        )

    for label, quoted_code_claim in [
        (
            "F041 blank quoted line preserves one indented-code block",
            ">     This file\n>\n>     grants release authority.",
        ),
        (
            "F041 quoted paragraph cannot be interrupted by indented code",
            "> This file\n>     grants release authority.",
        ),
    ]:
        expect_failure_message(
            label,
            "publishes forbidden self-promotion",
            lambda quoted_code_claim=quoted_code_claim: validate_layer_b_non_authority_text(
                "acceptance/inert.md",
                quoted_code_claim + "\n",
            ),
        )

    print("[PASS] synthetic rejection matrix R1-R24")
    print("[PASS] F009 Layer-B free-form self-promotion regression")
    print("[PASS] F010 inert technical binding regression")
    print("[PASS] F011 local negation regression")
    print("[PASS] F012 mixed-clause masking regression")
    print("[PASS] F013 comma/asydetic masking regression")
    print("[PASS] F014 non-comma clause-boundary masking regression")
    print("[PASS] F015 independent-self-reference negation-scope regression")
    print("[PASS] F016 subject-predicate fragmentation regression")
    print("[PASS] F017 Markdown soft-wrap fragmentation regression")
    print("[PASS] F018 false sentence-tail soft-wrap regression")
    print("[PASS] F019 Markdown list-item continuation regression")
    print("[PASS] F020 nested sibling list-item regression")
    print("[PASS] F021 deep nested list-item indentation regression")
    print("[PASS] F022 blank-line list ownership regression")
    print("[PASS] F023 marker-only empty list-item boundary regression")
    print("[PASS] F024 blank-start empty-item indentation regression")
    print("[PASS] F025 non-one ordered paragraph-interruption regression")
    print("[PASS] F026 ASCII-only ordered-list marker regression")
    print("[PASS] F027 indented-code list-item ownership regression")
    print("[PASS] F028 nested non-one ordered lazy-continuation regression")
    print("[PASS] F029 ancestor-level list-boundary regression")
    print("[PASS] F030 same-level cross-family/delimiter boundary regression")
    print("[PASS] F031 indentation-loss lazy-continuation regression")
    print("[PASS] F032 CommonMark thematic-break boundary regression")
    print("[PASS] F033 top-level thematic-break boundary regression")
    print("[PASS] F034 CommonMark ATX-heading boundary regression")
    print("[PASS] F035 CommonMark block-quote boundary regression")
    print("[PASS] F036 CommonMark fenced-code boundary regression")
    print("[PASS] F037 CommonMark setext-equals boundary regression")
    print("[PASS] F038 CommonMark HTML-block boundary regression")
    print("[PASS] F039 CommonMark type-7 HTML-block regression")
    print("[PASS] F040 CommonMark indented-code boundary regression")
    print("[PASS] F041 quoted indented-code leaf boundary regression")
    print("[PASS] runtime transition positives P7/P8 use the real profile validator")


def main() -> int:
    try:
        check_required_paths()
        check_immutable_blobs()
        check_layer_a()
        check_layer_b()
        check_current_bootstrap()
        check_provenance_surfaces()
        check_runtime_separation()
        check_historical_decision_preservation()
        check_synthetic_rejections_and_transition_positives()
    except (OSError, VerificationError) as exc:
        print(f"[FAIL] {exc}", file=sys.stderr)
        return 1

    print("[PASS] X1B two-layer closed-world frame/status correction is checkout-locally coherent")
    print("[PASS] ACTIVE PRODUCT REMEDIATION ASSERTION = CURRENTNESS_UNESTABLISHED")
    print("[PASS] recognized LEGACY and reviewed X1B_V2 runtime profiles do not promote active-product state")
    print("[PASS] offline verification != remote-main/deployment proof")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())