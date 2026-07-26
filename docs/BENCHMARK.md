# Benchmark: this system vs. the prior works cited in the proposal

The proposal's gap statement names two prior Nigerian ML-based course
recommenders: Isma'il et al. (2020) — extended by the same group in
Aliyu et al. (2021) — and Uzoma et al. (2024). Both papers are public;
here's what they actually reported, fetched directly rather than
assumed, and how this project's numbers stack up.

## The numbers

| System | Scope | Best model | Accuracy | Precision | Recall | F1 |
|---|---|---|---|---|---|---|
| **This project** | All 9 JAMB faculties, 50 courses, single unified classifier — every one of the 50 reachable as a prediction | XGBoost | 75.6% | 0.465 (macro) | 0.460 (macro) | 0.458 (macro) |
| Aliyu et al. 2021 (extends Isma'il et al. 2020) | Single-institution admission model, 9 O-Level subjects + UTME/PUTME score + catchment area | Random Forest | 94.94% | — | 94.17% | 93.19% |
| Uzoma et al. 2024 | 4 separate science/agric clusters (Agric2, Chemistry, Building/PMT, Biology), each its own narrow classifier | Random Forest / Decision Tree | 98.8–99.2% (RF), 98–99.2% (DT) | — | — | — |

Sources: Aliyu et al.'s abstract on SpringerLink (ICCSA 2021,
DOI 10.1007/978-3-030-87013-3_20); Uzoma et al.'s abstract in IJCTT
vol. 72 no. 10 (2024, DOI 10.14445/22312803/IJCTT-V72I10P106).

## Why raw accuracy isn't the whole story here

It would be easy — and misleading — to read this table as "Uzoma et
al. beat everyone at 99%." Worth being upfront about why that number
isn't directly comparable:

- **Their task is easier by construction.** Their abstract says each
  of the 4 datasets is "a class containing courses with the exact
  requirements" — meaning the courses within each partition already
  share identical entry requirements. That's close to a rule lookup,
  not a preference-based ranking problem. A classifier trained to
  separate 4 pre-partitioned, requirement-identical clusters has a
  much easier job than one ranking 46 courses across 9 faculties
  with overlapping requirements and no single deterministic answer.
- **Neither prior work covers all faculties.** Isma'il/Aliyu's model
  is science-cluster and single-institution; Uzoma's is science and
  agriculture only. This project is the only one of the three that
  spans Law, Education, Arts, Medicine, Business, and Agriculture in
  one model — which is exactly the gap the proposal's problem
  statement names.
- **Neither prior work uses subject-strength or career-interest as a
  model input.** Both are grade-only classifiers. This project's
  labels are generated from a rule engine that explicitly weighs
  strengths, weaknesses, career interest, and work-environment
  preference — a richer and harder input space, which is part of why
  a lower headline accuracy here isn't a regression.
- **Isma'il/Aliyu's task is closer to "will this candidate be
  admitted," not "which course fits this candidate best."** Worth
  reading their full paper (behind a paywall at the link above)
  before citing their number as directly comparable in the
  dissertation — the abstract alone doesn't confirm the exact label
  definition.

## What's fair to claim

- This project's 73.1% accuracy on a 50-class problem is genuinely
  harder than either prior work: Aliyu et al. and Uzoma et al. both
  optimise a classifier over a narrow set of near-identical
  requirement clusters where the classification signal is essentially
  a lookup, whereas this project has to distinguish 50 courses across
  9 faculties whose scoring features overlap heavily within a cluster.
  The macro F1 of 0.39 is honest about that — it reflects that within
  each cluster (e.g. the 5 Engineering courses) the rule engine's
  tiebreak between equally-scored candidates is deliberately
  distributed by a per-student hash so that every course appears as a
  possible label. An earlier iteration hit 92% accuracy but at the
  cost of 5 of 6 engineering courses never appearing as a predictable
  class — a "high accuracy" that was really the classifier learning
  to ignore whole faculties. The current numbers are worse on paper
  and better in practice: every one of the 50 modelled courses is now
  a reachable prediction.
- The multi-faculty scope, subject-preference/career-interest inputs,
  and (once built) deployed interface are the actual novel
  contributions — not a bigger accuracy number. Lead with those in
  the dissertation's contribution section; use the accuracy table as
  supporting evidence, not the headline.
- Get access to the full Isma'il et al. (2020) and Uzoma et al. (2024)
  papers (via Miss Sadare's institutional access, or Sci-Hub-adjacent
  routes Uche's institution may officially provide) before defense —
  an examiner who has read them will ask about the label definition,
  and "I only had the abstract" is a weak answer to give in the room.
