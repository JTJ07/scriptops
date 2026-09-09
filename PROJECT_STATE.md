---
project: "Narzędzie pisarskie / ScriptOps"
canonical_name: "ScriptOps"
state_owner: "PROJECT_STATE.md"
x1b_research_closure: "CLOSED"
x1b_active_product_remediation_assertion: "CURRENTNESS_UNESTABLISHED"
x1b_active_product_assertion_authority: "EXTERNAL_CURRENTNESS_REBIND_REQUIRED"
x1b_active_product_assertion_evidence: "NONE_ACCEPTED_FOR_THIS_STATUS_PUBLICATION"
x1b_current_authority_bootstrap: "README.md -> PROJECT_STATE.md -> HANDOFF.md"
x1b_authority_model: "TWO_LAYER_CLOSED_WORLD_V1"
updated_at: "2026-09-05"
---

# PROJECT_STATE — ScriptOps

## 1. Current X1B state authority

This file is one of exactly three `CURRENT_BOOTSTRAP_AUTHORITY` documents. The current X1B publication is:

```text
X1B_RESEARCH_CLOSURE: CLOSED
X1B_ACTIVE_PRODUCT_REMEDIATION_ASSERTION: CURRENTNESS_UNESTABLISHED
X1B_ACTIVE_PRODUCT_ASSERTION_AUTHORITY: EXTERNAL_CURRENTNESS_REBIND_REQUIRED
X1B_ACTIVE_PRODUCT_ASSERTION_EVIDENCE: NONE_ACCEPTED_FOR_THIS_STATUS_PUBLICATION
X1B_REVIEWED_REMEDIATION_PROVENANCE: PR #35 / REVIEWED HEAD 7c40a92165714023743e91c63b5b11b102fadd92 / UNMERGED
X1B_CURRENT_AUTHORITY_BOOTSTRAP: README.md -> PROJECT_STATE.md -> HANDOFF.md
X1B_AUTHORITY_MODEL: TWO_LAYER_CLOSED_WORLD_V1
```

The value `CURRENTNESS_UNESTABLISHED` is epistemic. It is neither an ontic `NO` nor an ontic `YES` about the active product.

```text
CURRENTNESS_UNESTABLISHED != CONFIRMED_NOT_REMEDIATED
CURRENTNESS_UNESTABLISHED != CONFIRMED_REMEDIATED
CURRENTNESS_UNESTABLISHED != FALSE
CURRENTNESS_UNESTABLISHED != TRUE
```

No local checkout, PR head, green verification result, source label, historical decision or reviewed candidate may promote this value.

## 2. Current authority model

Current recovery authority is exactly:

```text
README.md
PROJECT_STATE.md
HANDOFF.md
```

All other Markdown is either an explicitly classified Layer-A provenance member or Layer-B path-classed non-current material. Readable provenance cannot override the trio.

```text
AUTHORITY IS REGISTRY-GRANTED, NOT SELF-ASSERTED
REGISTRY CENSUS != PATH-CLASS SENTINEL SET
PR HEAD != ACTIVE DEFAULT BRANCH
GREEN VERIFICATION != DEPLOYED ENFORCEMENT
```

The active default branch must be resolved externally when a consequential active-product assertion is required. This offline repository state does not claim a live remote SHA as current truth.

## 3. Three different decision concepts

These concepts must remain separate:

```text
CONTENT SEMANTIC ACCEPTANCE
!=
X1B HumanDecision AUTHORSHIP EVIDENCE
!=
ACTIVE-PRODUCT REMEDIATION ASSERTION
```

Historical Phase-6 `human decision with why` / `approve --why` semantics are evidence of the historical workflow and DEC-SO-011 semantic decision process. They are **not sufficient X1B HumanDecision authorship evidence**.

The known legacy runtime on the frozen implementation baseline contains an `approve --why` path that writes `"approver": "human"`. That path is therefore classified as `LEGACY_PRE_X1B` for this frame/status correction; this status publication does not relabel it as secure X1B authorship enforcement.

## 4. Reviewed remediation provenance

The independently reviewed remediation candidate remains:

```text
FJ899/scriptops PR #35
HEAD = 7c40a92165714023743e91c63b5b11b102fadd92
STATE = REVIEWED / UNMERGED PROVENANCE
```

PR #35 is not active-product proof. If this frame/status correction is integrated first, PR #35 must not later be merged as-is; a later V2 integration requires a fresh reviewed integration against then-current default branch while preserving both runtime/security and frame boundaries.

## 5. Historical Phase-6 provenance

The historical controlled-workflow line remains valuable evidence but is not current X1B authority:

```text
PHASE 6 CONTROLLED WORKFLOW MECHANISM PASS / BOUNDED PROPOSAL VIEW INTEGRATED / P3 RUN003 OBSERVED PASS / SCN-012+027 HUMAN SEMANTIC ACCEPTED / CANONICAL EFFECT PREPARED NOT APPLIED / GOAL DONE NO / NO MATURITY CLAIM
```

Historical implementation/proof material includes:

- `legacy/scriptops-v2-single.py`;
- `phase6/scriptops-v2-hardening.py`;
- `phase6/bounded-proposal-view.py`;
- `tests/test_phase6_scriptops_smoke.py`;
- `tests/test_phase6_candidate_selection.py`;
- `tests/test_phase6_review_task_identity.py`;
- `tests/test_phase6_bounded_proposal_view.py`;
- `tests/test_phase6_p3_real_workload_001.py`;
- `tests/test_phase6_p3_real_workload_002.py`;
- `tests/test_phase6_p3_real_workload_003.py`;
- `tests/test_phase6_p3_evidence_record_003.py`;
- `evidence/PHASE6_CONTROLLED_WORKFLOW_PROOF_2026-08-10.md`;
- `evidence/P3_REAL_WORKLOAD_003_SCENE12_27_2026-08-19.md`;
- `evidence/P3_SCENE12_27_HUMAN_SEMANTIC_ACCEPTANCE_AND_CANONICAL_EFFECT_PREVIEW_2026-08-21.md`.

Historical milestones include PR #7 Phase-6 proof, PR #10 candidate-selection maintenance, PR #15 review-task identity hardening, PR #14 bounded proposal view and PR #16 Real Workload 003 evidence.

## 6. DEC-SO-011 remains historical semantic provenance

`DEC-SO-011` records Human semantic acceptance of the bounded `SCN-012 -> SCN-027` proposal state and authorization to prepare, but not execute, a canonical effect.

That decision remains valid as semantic/provenance history. It does not itself establish X1B HumanDecision authorship admission for a present effect and does not establish active-product remediation.

Historical `CANONICAL_EFFECT_PREPARED / WAITING_FOR_SEPARATE_HUMAN_EFFECT_GATE` is therefore not a current secure X1B execution route.

## 7. Current consequential-work rule

Before consequential X1B-authorship work:

```text
1. complete README -> PROJECT_STATE -> HANDOFF bootstrap;
2. confirm the three documents agree;
3. treat supporting documents as provenance only;
4. do not infer active-product state from the checkout;
5. require separate authority for any runtime integration, merge, deployment or canonical effect.
```

No current `approve --why` / canonical-write instruction is authorized by this file.

## 8. Future active-product confirmation is separate

A future status promotion requires, separately:

```text
external read-only resolution of actual refs/heads/main
-> bind that commit to expected runtime identity/class
-> durable currentness evidence
-> separate Human acceptance
-> separate status-only promotion candidate
-> verify publication still matches active runtime identity
```

Until then:

```text
X1B_ACTIVE_PRODUCT_REMEDIATION_ASSERTION: CURRENTNESS_UNESTABLISHED
```

## 9. Capability and maturity boundary

No browser helper, model/API automation, autonomous approval, atomic multi-scene approval, agent framework, multi-agent, GUI/dashboard, vector DB, semantic graph, multi-user or other new capability is authorized by this correction.

`MATURITY CLAIM: NONE`.
