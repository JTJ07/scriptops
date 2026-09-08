# RC1 Scope Lock — historical product-governance provenance

> X1B AUTHORITY FENCE — `HISTORICAL_PRODUCT_GOVERNANCE_PROVENANCE_ONLY`
>
> `Scope Lock` in this file is a historical product-scope constraint. It cannot establish current X1B remediation, deployment, HumanDecision admission, canonical-effect authority, merge/release authority or V1 authority.
>
> Current X1B recovery authority is only `README.md -> PROJECT_STATE.md -> HANDOFF.md`.

## Historical RC1 goal

The historical goal was not to build the full ScriptOps vision. It was to prove a local control loop:

```text
project init
→ task
→ context bundle
→ WebAI candidate import
→ validation
→ impact report
→ human decision
→ decision log
→ Git commit
→ smoke test
```

For current X1B interpretation:

```text
GENERIC HUMAN DECISION IN HISTORICAL RC1
!=
X1B HumanDecision AUTHORSHIP EVIDENCE
```

## Historical RC1 includes

- local CLI;
- single-user mode;
- Git-backed project;
- SQLite metadata;
- task creation;
- context bundle;
- HANDSHAKE v2 generation;
- prompt-ready file;
- manual WebAI output import;
- structural validation;
- simple canon-impact report;
- approve / reject / revision request;
- decision log with `why`;
- integrity status check;
- smoke test.

These items are scope provenance, not a current deployment or remediation assertion.

## Historical RC1-light IdeaOps allowance

Only if low effort, the old scope allowed folder foundations such as:

```text
ideas/
  inbox/
  triaged/
  parked/
  rejected/
  promoted/

decisions/
```

No AI idea triage was part of that historical RC1 allowance.

## Historical RC1 exclusions

- browser helper;
- direct API calls to OpenAI / Claude / Gemini;
- ChatGPT Agent automation;
- autonomous writing;
- automatic approve;
- automatic canon edits from AI output;
- multi-user;
- dashboard;
- GUI/TUI;
- vector database;
- semantic graph automation;
- AI Guard;
- Rule Miner;
- Retcon Engine;
- export pipeline;
- voice interface;
- cloud sync.

## Current authority fence

Prefer the narrower historical RC1 scope when interpreting old product-governance provenance, but do not recover this file as current action authority.

```text
REGISTRY CLASS = HISTORICAL_PRODUCT_GOVERNANCE_PROVENANCE_ONLY
CURRENT X1B AUTHORITY = NO
```
