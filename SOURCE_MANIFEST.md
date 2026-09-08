# SOURCE_MANIFEST

> X1B AUTHORITY FENCE — `HISTORICAL_RECONSTRUCTION_PROVENANCE_ONLY`
>
> This manifest describes source provenance and recovery material. It is not current X1B state authority. Labels such as `canonical`, `current`, `operational`, `scope lock`, or `decision summary` in historical source names do not override the current bootstrap registry.
>
> `SOURCE_MANIFEST CANONICAL LABEL != CURRENT X1B AUTHORITY`

## Current authority boundary

Current X1B recovery authority is exactly:

```text
README.md -> PROJECT_STATE.md -> HANDOFF.md
```

Those three files must agree on:

```text
X1B_ACTIVE_PRODUCT_REMEDIATION_ASSERTION: CURRENTNESS_UNESTABLISHED
X1B_AUTHORITY_MODEL: TWO_LAYER_CLOSED_WORLD_V1
```

Everything listed below is supporting provenance unless it is one of those three current-bootstrap documents.

## Layer-A registry roles

Current bootstrap authority:

- `README.md`
- `PROJECT_STATE.md`
- `HANDOFF.md`

Decision provenance only:

- `DECISION_LOG.md`

Historical reconstruction provenance only:

- `SOURCE_MANIFEST.md`
- `SOURCES.md`
- `SOURCE_AUDIT_SUMMARY.md`
- `RECONSTRUCTION_REPORT.md`

Historical product-governance provenance only:

- `sources/Decision_Summary_Current_State.md`
- `sources/RC1_SCOPE_LOCK.md`
- `sources/ScriptOps_Main_Theme_Summary.md`

Pre-fenced non-authority provenance:

- `CODEX_START.md`
- `IDEA_ARCHIVE.md`

## Layer-B path-class provenance

Nested/supporting Markdown is outside the 13-member Layer-A registry. Known path classes are denied current X1B authority by location, including:

```text
analysis/
continuity/
evidence/
acceptance/
sources/prototype/
legacy/
phase6/
tests/
.github/
scripts/
```

`PATH-CLASS DENIAL != REGISTRY MEMBERSHIP`.

`sources/prototype/RESTORE.md` remains historical prototype reconstruction context. It contributes zero members to the Layer-A registry census.

## Historical source package

The repository retains historical material for reconstruction and audit, including:

- ScriptOps Final Master Package lineage;
- broad v5 specification provenance;
- `legacy/scriptops-v2-single.py` as the preserved v2 implementation artifact;
- Mądry Warsztat / S2 Studio material;
- RC1 scope and historical decision records;
- Phase-6 evidence;
- bounded proposal and Real Workload evidence;
- continuity/audit material.

The historical v2 canonical implementation artifact remains:

```text
legacy/scriptops-v2-single.py
SHA-256: 881dade6c6c506b9a9d41ebfbf68afb18b66db7583d35f746fb29ed7b36ac596
Size: 51980 B
```

Transport reconstruction material remains under `sources/prototype/` and is provenance only.

## Completeness boundary

This manifest does not assert active-product remediation, deployment, release, merge authority, current remote-main identity, X1B HumanDecision admission or V1 authority.

A future active-product assertion requires external currentness evidence and separate Human acceptance; it cannot be recovered from this manifest.
