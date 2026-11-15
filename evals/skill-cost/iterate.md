# Iterate spec for skill-cost

Evaluate the skill as an agent given a request for a cost audit. Read the skill and its
supporting files from the draft. Run the synthetic probes. Work read-only. Only the
reviewer’s own scratch space may receive output. Never use real transcripts or live
schedules. Do not open the run log.

## Scope

Evaluate run accounting, comparison integrity, judgment about savings and coverage,
and the fallback when usage records are incomplete. Fix directly within that purpose.
Changes to the skill's purpose, native transcript formats beyond Claude Code, and live
schedules are outside the run. Draft in tystack with no publishing.

## Flow: cost audit and recommendation

Reviewers are Sol (primary) and Terra, independently. Target 8/10 within three scored
rounds. Review the same scenarios and rubric each round. Run `python evals/skill-cost/check.py
--report` for probe outcomes. Before scoring, also make sure manifests parse and scripts
compile. Once a regression is fixed, its probe must continue passing.

1. Price a measured run with a known total, a streamed duplicate, mixed cache writes, and
   main and helper usage. Exclude a later task whether the cutoff can be inferred from
   record metadata or supplied explicitly when the transcript lacks a marker. Treat a
   price sheet with placeholder or missing rates as incomplete.
2. Re-run two helpers with the same display name, then attempt a comparison where two
   candidates tie for two identical briefs. Retain both reports and make identity or
   ambiguity explicit before comparing.
3. Compare matched reports and reports present on only one side. The candidate is
   cheaper and misses `item:2`, which is material. No recommendation should treat a
   matched subtotal or a cheaper headline as sufficient coverage.
4. Given Codex usage data with a run time and main-session aggregates but neither helper
   usage nor exact replay inputs, report what the records support, identify the specific
   gaps, and avoid a complete cost or equivalence claim. A question about only the
   current chat's usage stays on the current-chat usage path.

## Fixed evaluator brief

Walk through the four scenarios from the files as a fresh reader. For each, give the
observable result and cite a source or probe. Report the recommendation for scenario 3
and the usable partial report for scenario 4. Score goal achievement, architecture,
scope discipline, and supporting-file quality out of 10. The overall score is their
equal-weight average. Score 9 for ordinary use you would trust, 7 for a useful result with
a material gap, and 5 for failures that can undermine the result. Give high-impact fixes
first and identify what could not be exercised. Treat parsed synthetic records as
fixtures. Do not edit the draft, import data, open the run log, or use real transcripts.
