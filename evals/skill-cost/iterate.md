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

---

## Jobs

What skill-cost exists to do, from its own steps:
1. Find a skill's runs, scheduled and manual.
2. Total each run's tokens and price them.
3. Find what drives the cost.
4. Propose changes, with estimated savings, and ask which to try.
5. Test the chosen change side by side, read-only.
6. Report with one recommendation.
7. Apply the change on the user's word and re-measure.
8. Turn away what isn't its job (this session's usage, quality work).

The flow "cost audit and recommendation" above exercises jobs 2 and 5 (pairing and
comparing reports, the adopt-or-keep call) and the partial audit when records are
incomplete. It never touches jobs 1, 3, 4, 7, or the rerun itself in job 5.

## Flow: recommendations

**Card:** custom, adapted from the skill dry run: the evaluator carries out the skill's
Steps 3 and 4 on runs that are already totalled, then judges its own output against answer
notes.
**Who and what:** an agent that has just loaded skill-cost and been handed a totalled run.
It judges whether following the skill produces advice that fits the evidence: the right
drivers, every kind of change considered, estimates that count what a change adds as well
as what it removes, and one clear decision for the user.
**Coverage:** exercises jobs 3 and 4, the recommendation in job 6, and job 8. Never
touches jobs 1, 2, 5 and 7: a score here says nothing about whether the skill counts
correctly or whether its side-by-side test works.
**Target and budget:** 7/10 within 3 rounds.
**Evaluators:** `opus`, medium (primary).
**Publishing:** a draft for the owner, in
this repository. Nothing is committed.

### Guardrails for this flow
**In scope:** `SKILL.md` Steps 3, 4 and 6, the description's routing, and
`references/helper-contract.md`, as an agent meets them.
**Out of scope:** the scripts, the counting and pricing rules, Steps 1, 2, 5 and 7.
**Fix directly:** wording, order, and adding instructions or table rows inside Steps 3, 4
and 6 and the helper reference (the owner widened this on 2026-11-15).
**Propose to the owner:** script changes, the skill's purpose, its description, and any
change to another step.

### Fixtures for this flow
`evals/skill-cost/fixtures/recommendations/`: six scenario files, each a
run already totalled. Scenario 1 uses real token figures with no transcript content;
scenarios 2 to 6 are invented. `answers/answers.md` holds what the evidence in each
scenario supports; evaluators open it only after writing their own output. No reset is
needed. Real transcripts and schedules are off limits.

### Scenarios
1. `1-game-art-review.md`: "Find ways to make my iterate skill cheaper."
2. `2-morning-digest.md`: "Is morning-digest too expensive?"
3. `3-release-notes.md`: "Make release-notes cheaper."
4. `4-changelog-lint.md`: "Audit how many tokens changelog-lint used."
5. `5-contract-review.md`: "Should contract-review split into two sessions?"
6. `6-handoff.md`: a request to route.

### Questions at each scenario
- Following the skill as written, what do I tell the user?
- Where did the skill leave me guessing, and what did I guess?
- Against the answer notes: did I find the main driver, consider every kind of change,
  count what each change adds, keep the skill's cost apart from the setup's, and leave the
  user one clear decision?
- Where I matched the notes, was it because the skill told me to, or because I worked it
  out without it?

### Rubric
Score from 1 to 10, a judgement, not an average of the sub-scores.
Anchors: 10, in every scenario the skill led to the recommendation the evidence supports,
with every kind of change accounted for and every estimate net; 7, the first
recommendation is right everywhere, with some levers or added costs left unstated; 4, in
at least one scenario the skill led to a change that wouldn't pay or missed the main
lever; 1, the advice is unusable.
Sub-scores:
- Lever coverage: every kind of change that fits the evidence is raised, and the rest are
  ruled out with a reason.
- Fit to evidence: the first recommendation is the one the figures support.
- Estimate honesty: each estimate counts what the change adds as well as what it removes,
  and says what is unmeasured.
- Skill versus setup: costs the skill causes are kept apart from costs of the setup it
  runs in.
- Decision clarity: the user is left with one clear question, or told plainly there is
  nothing to change.

### Settled decisions
- The scripts and Steps 1, 2, 5 and 7 are not judged here: another flow covers them.
- Invented figures in scenarios 2 to 6 are stand-ins, not claims about real skills.

### Brief
You are an agent that has just loaded the skill-cost skill, working through sample
requests. Write what you would produce; don't run anything outward-facing.
Don't change the thing or its settings. Change data only in the fixtures the spec names,
and list what you changed. Write anything you produce only in the scratch folder named at
the top. Never touch real transcripts, schedules, or any copy of skill-cost other than the
one named below.

**What it's for:** skill-cost measures what a skill costs to run and proposes how to make
it cheaper without losing quality. This review tells its builder whether an agent that
follows the skill's Steps 3 and 4 gives advice that fits the evidence.

**Settled decisions:** the spec's Settled decisions for this flow; don't raise or score
them.

**Read:** `evals/skill-cost/iterate.md`,
the "Jobs" part and the "Flow: recommendations" section only, and any file that section
points to. Don't open the run log beside it; form your own view. Judge only what this
flow's Who and what covers.

**Scenarios:** the six in the flow's section, in order. For each: read the scenario file,
then follow the skill from Step 3 as written (Steps 1 and 2 are already done and their
results are in the file) and write, in a file in your scratch folder, exactly what you
would tell the user. Note every place you guessed. Do all six before opening
`answers/answers.md`. Then open it and ask the flow's questions of each output.
Do not revise an output after opening the answer notes.

**How to reach it:** the skill is in
`skills/skill-cost/` (`SKILL.md`
and `references/`). Read it with your file tools. You don't need to run its scripts, and
you can't reach real transcripts.

**Report, in about 700 words:**
1. Score N/10 as a whole number, one line on what holds it back, and the sub-scores
   (Lever coverage, Fit to evidence, Estimate honesty, Skill versus setup, Decision
   clarity), also whole numbers.
2. How well it serves this flow overall.
3. Findings ranked by impact: where, what's wrong, the concrete change, and what the
   change replaces. Tag each [direct] or [proposal] using the spec's guardrails, and
   [high] or [low] impact.
4. Next point: what would raise the score by one, and whether that lies in the thing or
   in the test (invented stand-ins, tools that can't reach part of it).
5. Alternatives: a different format or structure that would work better, and what it
   would replace.
6. Keep: what works and shouldn't change.
7. What you changed in the fixtures, and what you couldn't check.
