# DECISION_LOG

> X1B AUTHORITY FENCE — `DECISION_PROVENANCE_ONLY`
>
> This file preserves historical/semantic decisions. `Status: ACTIVE`, generic Human approval, `approve --why`, canonical wording, or a historical authorization in this log do **not** establish current active-product remediation, deployment state, X1B HumanDecision authorship admission, merge authority, release authority or V1 authority. Current X1B state is recovered only through `README.md -> PROJECT_STATE.md -> HANDOFF.md`.
>
> `DECISION_PROVENANCE_ONLY != CURRENT_BOOTSTRAP_AUTHORITY`

Ten plik przechowuje wyłącznie decyzje semantyczne: cel, zakres, kanon, aktywację, kolejność pracy i świadome wyłączenia. Zwykłe zmiany techniczne należą do historii Git.

Nowy wpis powinien, gdy to możliwe, wskazać:

- `Evidence` — dowód lub źródło decyzji;
- `Implemented by` — commit lub PR realizujący decyzję.

Brak takiego odnośnika nie unieważnia starszej decyzji, ale nie wolno tworzyć osobnego wpisu tylko po to, aby opisać techniczny diff.

## DEC-SO-001 — człowiek pozostaje właścicielem kanonu

Status: `ACTIVE`

AI tworzy kandydatów i analizy. Nie zatwierdza i nie zmienia samodzielnie kanonu. Techniczne commity mogą realizować wcześniej zatwierdzoną decyzję, ale nie stanowią nowej decyzji kierunkowej.

## DEC-SO-002 — lokalne źródło prawdy

Status: `ACTIVE`

Szczegółowy stan ScriptOps należy do repo `litrgratis-pixel/scriptops`. `PROJECT_STATE.md` jest kanonicznym stanem operacyjnym.

## DEC-SO-003 — zakres RC1

Status: `ACTIVE`

RC1 ma udowodnić tylko pętlę:

`task → context → candidate import → validation → impact → human decision → decision log → Git commit`.

## DEC-SO-004 — wyłączenia z RC1

Status: `ACTIVE`

Poza RC1 pozostają: browser helper, API, autonomiczny agent, AI Guard, automatyczny graf semantyczny, pełny IdeaOps, dashboard, eksport i multi-user.

## DEC-SO-005 — specyfikacja nie jest produktem

Status: `ACTIVE`

`ScriptOps_FINAL_MASTER_PACKAGE` i v5 są źródłami zakresu i architektury, ale nie dowodem wykonania RC1.

## DEC-SO-006 — prototyp v2 nie jest automatycznie bazą RC1

Status: `SUPERSEDED BY DEC-SO-010`

Decyzja o bazie implementacji wymaga porównania `legacy/scriptops-v2-single.py` z `sources/RC1_SCOPE_LOCK.md`.

Porównanie zostało wykonane w `analysis/RC1_V2_GAP_2026-08-10.md`; decyzję o bazie podjęto w DEC-SO-010.

## DEC-SO-007 — kolejność pracy

Status: `ACTIVE`

1. zabezpieczenie stanu i źródeł;
2. `ACCESS CHECK`;
3. porównanie v2 z RC1, jeżeli nie ma późniejszego kodu;
4. decyzja o bazie implementacji;
5. dopiero potem test end-to-end.

## DEC-SO-008 — projekt nie jest jeszcze aktywowany

Status: `ACTIVE WITH PHASE-6 BOUNDED IMPLEMENTATION EXCEPTION`

ScriptOps pozostaje bez ogólnej aktywacji produktu. Jawna decyzja DEC-SO-010 zezwala wyłącznie na ograniczony Phase-6 proof slice B1–B5; nie aktywuje szerszego roadmapu ani funkcji post-MVP.

## DEC-SO-009 — pojedyncza kanoniczna kopia prototypu v2

Status: `ACTIVE`

Pełny historyczny prototyp jest dostępny jako `legacy/scriptops-v2-single.py`. Siedem części w `sources/prototype/` pozostaje zapisem transportowym i dowodem odtwarzalności, ale nie jest drugim kanonicznym plikiem roboczym.

Evidence: niezależny cold start wykazał tarcie wynikające z konieczności ręcznego składania pliku.

Implemented by: PR wprowadzający usprawnienia Lean po audytach ciągłości.

## DEC-SO-010 — v2 jest bazą Phase 6; reuse + hardening + proof

Status: `ACTIVE`
Owner: `USER`
Date: `2026-08-10`

Decision:

```text
YES
BASE: legacy/scriptops-v2-single.py
REWRITE: NO
NEW CAPABILITY: NO
PHASE 6: reuse + hardening + proof
MATURITY CLAIM: NONE
FUNCTIONAL_SADDLE_ACCEPTED: NOT YET
```

Zakres wykonawczy jest zamrożony do znanych blockerów B1–B5:

1. spójny lifecycle / clean-tree checkpoints;
2. spójny lifecycle artefaktów przed approval;
3. przeliczenie accepted scene hash po zmianie statusu;
4. obowiązkowe ludzkie `why` przed kanonicznym zapisem;
5. minimalny impact report i deterministyczny smoke proof.

Zasady:

- historyczny `legacy/scriptops-v2-single.py` pozostaje kanonicznym źródłem bazowym i dowodem v2;
- Phase-6 hardening może być małym audytowalnym shimem nad v2 zamiast przepisywania historycznego artefaktu;
- kandydat przed approval jest proposal artifact, nie kanonicznym efektem;
- kanoniczny zapis sceny następuje dopiero po jawnej decyzji człowieka z `why`;
- ScriptOps nie dostaje własnej authority, interpretacji celu ani autonomicznego planowania;
- brak browser/API automation, agent framework, multi-agent, GUI, vector DB, semantic graph, multi-user i innych nowych capability.

Evidence: jawna decyzja użytkownika w Saddle Phase 6 + `analysis/RC1_V2_GAP_2026-08-10.md`.

## DEC-SO-011 — Human semantic acceptance SCN-012 + SCN-027; canonical effect preparation only

Status: `ACTIVE`
Owner: `USER`
Date: `2026-08-21`

Decision:

```text
SCN-012 → SCN-027 WYCZERPUJE ZAMIERZONY ZAKRES TEJ DECYZJI.

SCN-012 + SCN-027 PROPOSAL STATE:
HUMAN SEMANTIC ACCEPTED

NO-CARRIER GOAL FOR THIS BOUNDED SCOPE:
SEMANTICALLY SATISFIED

ACCEPTED MAPPING:
PHYSICAL CARRIER CONTROL
→
ACCESS CONTROL OF ENCRYPTED AUTHORITATIVE SOURCE

LOSS OF PHYSICAL PENDRIVE / DRAWER BEAT:
NOT A BLOCKER

CANONICAL EFFECT PREPARATION:
AUTHORIZED

CANONICAL EFFECT EXECUTION:
NOT AUTHORIZED WITHOUT SEPARATE HUMAN GATE
```

Boundaries:

- no additional downstream material is required for this Human decision;
- no canonical write has been authorized or executed;
- no `approve --why` has been executed;
- no atomic multi-scene approval is authorized or implied;
- no new capability, product activation or maturity claim is created;
- `GOAL DONE` remains `NO` until the accepted effect is actually applied to a canonical target.

Evidence: `evidence/P3_SCENE12_27_HUMAN_SEMANTIC_ACCEPTANCE_AND_CANONICAL_EFFECT_PREVIEW_2026-08-21.md`.

Implemented by: `NOT YET — CANONICAL EFFECT REQUIRES SEPARATE HUMAN GATE`.
