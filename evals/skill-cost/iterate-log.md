# Iterate log for skill-cost

## Flow: cost audit and recommendation

**Run state:** Ended after round 3. Target reached and budget spent. Best primary score
8.50/10. Starting revision `daf1138`. Score order is goal achievement, architecture,
scope discipline, and supporting-file quality.

| Round | Sol (primary) | Terra | Synthetic checks | Result |
| --- | --- | --- | --- | --- |
| 1 | 6.00 (5, 6, 8, 5) | 6.00 (5, 6, 8, 5) | 2/9 | The cutoff missed follow-ups, reports could collide, and the comparison could omit unmatched helpers. |
| 2 | 8.25 (8, 8, 9, 8) | 7.75 (7, 8, 9, 7) | 11/11 | Both reviewers found that missing cache prices could still produce a complete-looking estimate. |
| 3 | 8.50 (9, 8, 9, 8) | 9.00 (9, 9, 9, 9) | 14/14 | Missing rate categories and unknown cache durations now show up as incomplete. Explicit common multipliers still work. |

Round 1 used the published skill and an initial synthetic harness. For round 2, the same
pairing scenario used independently seeded original briefs and checked explicit maps. For
round 3, the same accounting scenario gained probes for missing rate categories and cache
duration. The four scenarios and scoring criteria stayed fixed.

Both final reviewers kept the current setup in the cheaper-candidate scenario because it
missed a material item and had unmatched reports. They could produce a scoped partial
audit for the Codex scenario. That part was a walkthrough. No live transcript, schedule,
or helper replay was exercised.

**Blinded comparison:** A fresh Sol evaluator preferred the final version with strong
confidence overall, strong for scenarios 1–3 and clear for scenario 4. With the same
final harness on both versions, the starting version passed 1/14 and the final version
passed 14/14. The stricter cutoff probe includes a call exactly on the boundary, which
explains why the initial tagged-cutoff result differs. The evaluator noted the extra
work to verify time windows, fill rate sheets, and map ambiguous helpers from replay
records. Finding the relevant Codex records still depends on the operator.

## Flow: recommendations

**Run state:** ended after round 3: target reached (rule 1) and budget spent (rule 2). 3 of
3 rounds used, target 7; best score since the baseline and for this run: 7 (rounds 1 and 2
scored 6); last round that made progress: round 3. Starting version
the skill at the starting revision (tystack `main` at
`64146f2`); the fixes are in `skills/skill-cost/SKILL.md` (a draft,
not committed). Round 3's fixes were applied after the last scored round, so no evaluator
has scored them.

**Checkpoint:** for the runner, never sent to evaluators.
Launch: one fresh `general-purpose` agent, `model` `opus`, `effort` `medium`, described
"Round <N> recommendations review". The line added above the brief, word for word, then a
blank line, then the spec's Brief unchanged:
"Scratch folder for this round: `<scratch folder outside the repository>/round<N>/` (create it). Your final message is the report."
Round in hand: none (run ended).
Fixing: edit `skills/skill-cost/SKILL.md` and `references/helper-contract.md`
directly. After every change run, from the repository root: `python3 evals/skill-cost/check.py --report`
(16 of 16 must pass), `python3 -m py_compile` on the three scripts, and confirm every file
`SKILL.md` names exists.
Comparison: one fresh `opus`, medium evaluator gets the starting and final `SKILL.md` and
`helper-contract.md` as X and Y (random order), plus the six scenarios, questions and the
answer notes.

Entries: none yet.

### Round 1 (baseline), 2026-11-15
- **Evaluators:** `opus`, medium (primary). All six scenarios, on the starting version.
- **Score:** 6/10 (Lever coverage 6, Fit to evidence 6, Estimate honesty 5, Skill versus
  setup 8, Decision clarity 7).
- **Checks:** pass before and after the fixes (14 of 14 probes, scripts compile).
- **Findings and what changed** (all [direct], all inside Steps 3, 4 and 6):
  1. [high] Step 4 never asks for net estimates; in scenario 1 the reviewer recommended a
     new session per budget at $20 to $25, counting removed reads only. Changed: every
     proposal is written as Removes, Adds, Net, Unmeasured, Test, and the table has an
     "Adds" column.
  2. [high] No row for a new session, none for the main session's or a reviewer's model.
     Changed: the model row covers the main session, one reviewer of several, helpers'
     reading and fixed-command work, and says where it doesn't fit; a new-session row says
     it needs a pause longer than the cache lifetime.
  3. [high] Step 4 asks which change to try even when nothing pays. Changed: it says
     nothing is worth changing and stops; an audit-only request gets the table and that
     verdict.
  4. [high] No path for a change the user proposes. Changed: net it first, answer yes or
     no, say what would change the answer.
  5. [low] Rows could be skipped. Changed: every row gets a verdict.
  6. [low] Heading said "cheapest first", body said saving against risk. Changed: heading.
  7. [low] Setup cost triggered by a skill step. Changed: one line in Step 3.
  8. [low] Thin samples. Changed: one line in Step 6.
- **Owner direction applied with these** (not raised by the reviewer): a row for reading
  shared material once and passing it on, and a row for dropping calls that do no work.
- **High-impact [direct] fixes applied:** 4.
- **Next point (primary):** in the thing (net estimates, the missing rows). One test
  limit: the scenarios hold no skill text, so "tie each driver to a line" can't be checked.
- **Proposals and open decisions:** (open) the description still says "ranks changes
  cheapest first"; the description is the owner's to change.
- **Cost:** about 88k tokens for the evaluator.
- **Not covered within the flow:** tying drivers to lines; real `--detail` output.

### Round 2, 2026-11-15
- **Evaluators:** `opus`, medium (primary). All six scenarios, with round 1's fixes.
- **Score:** 6/10 (Lever coverage 7, Fit to evidence 6, Estimate honesty 7, Skill versus
  setup 9, Decision clarity 9). No rise; progress by fixes applied. Scenarios 2 to 6
  matched the answer notes, each from the skill's own text; scenario 5's arithmetic matched
  exactly. Scenario 1 still went wrong in two places.
- **Checks:** pass before and after the fixes (14 of 14 probes, scripts compile).
- **Findings and what changed** (all [direct]):
  1. [high] Step 3 never sends the reader to the main session's model, so moving the main
     session to a cheaper model never came up. Changed: the driver is now each part's
     share and model, main session included, with its calls counted by kind.
  2. [high] The new-session row let a warm-cache split through. Changed: without a pause,
     price the rebuild in full and expect a net near zero; don't propose it on removed
     reads alone.
  3. [low] A user-named change wasn't given a test. Changed: name the Step 5 test.
  4. [low] "Nothing worth changing" had no time horizon. Changed: a month, or ten runs.
  5. [low] No row for a role whose output isn't used. Changed: added.
  6. [low] Changes that interact weren't re-netted. Changed: one line.
- **Fixture fix, not a break:** scenario 5 said the context grew "evenly" while giving a
  second-half average that even growth can't produce. The word was removed; the figures
  and the answer notes are unchanged.
- **High-impact [direct] fixes applied:** 2.
- **Stop rules:** none holds (target 7 not reached; one round left; both rounds made
  progress).
- **Next point (primary):** in the thing (scenario 1's first recommendation). In the test:
  tying drivers to lines can't be exercised without the target skills' text.
- **Proposals and open decisions:** (open) the description's "cheapest first"; (open) the
  reviewer's alternatives: one output table for Step 4, and a cost breakdown by part and
  category at the top of Step 3.
- **Cost:** about 95k tokens for the evaluator.
- **Not covered within the flow:** tying drivers to lines; real `--detail` output.

### Round 3, 2026-11-15
- **Evaluators:** `opus`, medium (primary). All six scenarios, with round 2's fixes.
- **Score:** 7/10 (Lever coverage 6, Fit to evidence 7, Estimate honesty 8, Skill versus
  setup 9, Decision clarity 8). The best score rose from 6 to 7: progress. The first
  recommendation was right in five of six scenarios, each from the skill's text.
- **Checks:** pass before and after the fixes (14 of 14 probes, scripts compile).
- **Findings and what changed** (fixes applied after the last scored round; no evaluator
  has scored them):
  1. [direct][high] One row covered every role's model, so it got one verdict and the main
     session's model was never raised. Changed: four separate rows (main session, its
     fixed-command calls, one reviewer or helper of several, helpers' reading).
  2. [direct][high] A restart after a pause and a restart without one were blended into
     one figure. Changed: parts resting on different evidence are separate entries; the
     new-session row also covers separate jobs run back to back.
  3. [direct][low] No verdict for a row the figures can't settle. Changed: a third verdict
     that names the output that would settle it.
  4. [direct][low] No way to price a test. Changed: a rule of thumb.
  5. [direct][low] The smaller-model risk sat only in the reference file. Changed: it is in
     the row.
  6. [proposal][low] Routing to iterate lives only in the description. Open.
- **High-impact [direct] fixes applied:** 2.
- **Stop rules:** rule 1, target reached (7 against a target of 7); rule 2, budget spent.
- **Next point (primary):** in the thing (the per-role model verdicts, now applied).
- **Proposals and open decisions:** (open) the description's "cheapest first"; (open) a
  routing line in the body; (open) a two-axis checklist (parts by kinds of change) in
  place of the table; (open) one output table for Step 4; (open) a cost breakdown by part
  and category at the top of Step 3.
- **Cost:** about 96k tokens for the evaluator; about 280k for the three rounds.
- **Not covered within the flow:** tying drivers to lines; real `--detail` output;
  agreement between evaluators (one evaluator per round).

### Before and after, 2026-11-15
One fresh `opus`, medium evaluator compared the starting version (shown as Y) and the final
version (shown as X) blind, on the six scenarios and the answer notes. Verdict: the final
version is better in five scenarios and level in one (the hand-off), with **strong**
confidence. Where it found the final version worse: Step 4 is longer (16 rows and a third
column, some cells dense); the every-row verdicts come before the nothing-worth-changing
check, so an audit-only request could get a padded list first; "a month, or the next ten
runs" doesn't say which applies when they disagree; "rework if quality drops" can't be
priced; re-netting each change against those above it is arithmetic an agent may skip; the
description still says "cheapest first". None of these were changed after the comparison.

### After the run, 2026-11-15: owner follow-ups applied (no review round)
- The owner took the open proposals and the comparison's notes. Changed: the description
  says "by net saving against risk"; a routing line at the top of the body sends this
  session's usage and quality work elsewhere; an audit-only or very cheap run stops before
  the row-by-row verdicts; the test threshold is the next ten runs; Step 3 opens with a
  breakdown by part and category. Not done: the parts-by-change grid and a single output
  table for Step 4.
- `run_tokens.py` gained `--after`, an inclusive start for a run that begins partway
  through a session, with a probe for it (15 of 15 pass). On a real session it reproduced
  a window that had been sliced by hand.
- Paths in this flow's spec section, brief and Checkpoint were rewritten from a scratch
  draft to this repository. A path-only change: not a break.
- None of these has been scored by an evaluator.
