# ScriptOps

Repozytorium lokalnego stanu projektu **Narzędzie pisarskie / ScriptOps**.

## X1B current authority bootstrap

This section is the current X1B recovery authority. Historical Phase-6 material below is provenance and must not override it.

```text
X1B_RESEARCH_CLOSURE: CLOSED
X1B_ACTIVE_PRODUCT_REMEDIATION_ASSERTION: CURRENTNESS_UNESTABLISHED
X1B_ACTIVE_PRODUCT_ASSERTION_AUTHORITY: EXTERNAL_CURRENTNESS_REBIND_REQUIRED
X1B_ACTIVE_PRODUCT_ASSERTION_EVIDENCE: NONE_ACCEPTED_FOR_THIS_STATUS_PUBLICATION
X1B_REVIEWED_REMEDIATION_PROVENANCE: PR #35 / REVIEWED HEAD 7c40a92165714023743e91c63b5b11b102fadd92 / UNMERGED
X1B_CURRENT_AUTHORITY_BOOTSTRAP: README.md -> PROJECT_STATE.md -> HANDOFF.md
X1B_AUTHORITY_MODEL: TWO_LAYER_CLOSED_WORLD_V1
```

Current bootstrap authority is exactly:

1. `README.md`
2. `PROJECT_STATE.md`
3. `HANDOFF.md`
4. verify that all three publish the same X1B fields
5. STOP before consequential work
6. load only task-relevant supporting provenance

`DECISION_LOG.md`, `SOURCE_MANIFEST.md`, `SOURCES.md`, `SOURCE_AUDIT_SUMMARY.md`, `RECONSTRUCTION_REPORT.md` and `sources/*.md` are supporting provenance, not current X1B authority.

Mandatory separations:

```text
X1B CLOSED != ACTIVE PRODUCT REMEDIATED
CURRENTNESS_UNESTABLISHED != CONFIRMED_NOT_REMEDIATED
CURRENTNESS_UNESTABLISHED != CONFIRMED_REMEDIATED
CURRENTNESS_UNESTABLISHED != FALSE
CURRENTNESS_UNESTABLISHED != TRUE
PR HEAD != ACTIVE DEFAULT BRANCH
GREEN VERIFICATION != DEPLOYED ENFORCEMENT
GENERIC HUMAN APPROVAL != X1B HumanDecision AUTHORSHIP EVIDENCE
```

The legacy Phase-6 `approve --why` route is historical workflow semantics. It is **not sufficient X1B HumanDecision authorship evidence** and must not be used as the next secure X1B-authorship effect route.

`FJ899/scriptops PR #35` is reviewed remediation provenance only. It is not merged and is not proof of active-product remediation. If this frame/status correction becomes active first, PR #35 must not later be merged as-is; any V2 integration requires a fresh reviewed integration preserving this authority boundary.

No current document in this repo establishes `CONFIRMED_NOT_REMEDIATED` or `CONFIRMED_REMEDIATED`. Either promotion requires external remote-main readback, runtime-identity binding, durable currentness evidence, separate Human acceptance and a separate status-promotion candidate.

## Historical Phase-6 state — provenance only

Historical controlled-workflow evidence established a bounded mechanism around the existing v2 substrate, bounded proposal view and Real Workload 003. The historical status string was:

```text
PHASE 6 CONTROLLED WORKFLOW MECHANISM PASS / BOUNDED PROPOSAL VIEW INTEGRATED / P3 RUN003 OBSERVED PASS / SCN-012+027 HUMAN SEMANTIC ACCEPTED / CANONICAL EFFECT PREPARED NOT APPLIED / GOAL DONE NO / NO MATURITY CLAIM
```

Historical workflow artifacts include:

- `legacy/scriptops-v2-single.py`;
- `phase6/scriptops-v2-hardening.py`;
- `phase6/bounded-proposal-view.py`;
- `evidence/PHASE6_CONTROLLED_WORKFLOW_PROOF_2026-08-10.md`;
- `evidence/P3_REAL_WORKLOAD_003_SCENE12_27_2026-08-19.md`;
- `evidence/P3_SCENE12_27_HUMAN_SEMANTIC_ACCEPTANCE_AND_CANONICAL_EFFECT_PREVIEW_2026-08-21.md`;
- `DEC-SO-011`.

Historical `CANONICAL_EFFECT_PREPARED / WAITING_FOR_SEPARATE_HUMAN_EFFECT_GATE` and historical `approve --why` wording are preserved as provenance only. They do not create a current secure X1B effect route.

PR #7 was historically verified and merged. Its merge checkpoint is `daa6e5dc210e09171a530eeffe5601e0e74ae041`; recorded SHA values are provenance/checkpoints, not perpetual live pointers.

The historical `materially-different bounded workload` was completed by Real Workloads 001–003 and is **not current NEXT**. The Human semantic decision for `SCN-012 + SCN-027` is also historically closed at the DEC-SO-011 semantic layer, while canonical effect remains not applied.

`CODEX_START.md` and `analysis/RC1_V2_GAP_2026-08-10.md` are historical RC1/planning provenance and are not the current recovery route.

## Verification

```bash
python scripts/verify_repository.py
python -m unittest discover -s tests -p 'test_phase6_*.py' -v
```

The verifier is offline. A green checkout verifies candidate-local coherence only; it does not infer remote `main`, deployment, release or active-product remediation.

## Capability boundary

Do not add browser helper, direct model/API automation, autonomous approval, atomic multi-scene approval, agent framework, multi-agent, GUI/dashboard, vector DB, semantic graph, multi-user or other capability without separate Human authority.

`MATURITY CLAIM`: **NONE**.
