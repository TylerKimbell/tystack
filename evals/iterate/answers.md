# Answer key: dry run

For the runner only. Evaluators never open this file, and nothing in it goes into the brief
or the launch lines.

It gives the expected outcome for each scenario with one right answer under the skill's
current text: 5, 6, 7, and 8. Scenarios 1 to 4 have no section; they are judged on the
evaluators' reports alone.

**How to use it.** After every report in the round has returned, compare each evaluator's
`scenario-5.md` to `scenario-8.md` with the matching section below. A mismatch is a
finding to check against the skill's rule text: either the skill is unclear (a fix to the
skill, tagged and handled in Step 5 as usual) or this key is wrong (fix the key, and say
so). Log each mismatch and what you concluded in the round's entry. A mismatch never
changes the evaluator's score; the score is the evaluator's own.

When the skill's text changes in a way that changes an outcome, update this key in the
same change and log it with the break.

## Scenario 5

A single defect with a clear done state: the route table's last row.

- Say in one line that this isn't an iterate job.
- Reproduce the error, fix it, and verify the fix as usual.
- Deploying the fix to the live page needs the user's go-ahead.
- No spec, brief, log, or score, and `templates.md` isn't loaded.
- Offering a line for the spec's Checks, and for the page's own test tool, applies only if
  a spec exists. The scenario stands alone and names none, so the offer is optional.

Wrong: starting Step 1, a report-only round, or a single pass.

## Scenario 6

Stop after round 13 under rules 3 and 6.

Budget 100, so N is a tenth of it rounded up and at least 3: N = 10, and 2N = 20. Round 1
is the only baseline; 13 rounds are scored. One evaluator, so it is the primary. The best
score reached 8 in round 3 and hasn't risen since.

1. Target reached: does not hold. 8 is below the target of 9.
2. Budget spent: does not hold. 13 of 100 rounds.
3. No progress: holds. The last 10 rounds, counting this one, are rounds 4 to 13. None
   raised the best score (8 throughout) and none applied a high-impact [direct] fix (the
   log shows 0 [direct][high] for each). 13 rounds are scored since the baseline, so the
   window is full.
4. Flat score: cannot hold yet. It needs 20 rounds scored in this run, and there are 13.
   (The best score has also been flat for only 10 rounds, since round 3.)
5. Nothing to change: does not hold. Round 13 applied a [direct][low] fix (a tooltip), so
   it produced a [direct] finding Step 5 applied.
6. Ceiling in the test: holds. Rounds 12 and 13 both place the next point in the test
   (placeholder content), and neither applied a high-impact fix.
7. Can't go on safely: does not hold. No check fails, and the next point is in the test,
   not a fix to the page that needs the owner. Open proposals alone don't end the run.

Expected decision:
- Stop. Name rules 3 and 6 in round 13's entry, and set the Run state to "ended after
  round 13" with them.
- The run applied fixes, so the before-and-after comparison runs: one fresh evaluator on
  the primary's model, the version from before round 1's fixes against the current draft,
  labelled X and Y at random. The scenario says the page's history holds that version.
- Then the final summary to the user, the first contact since the run began. It names
  both rules with their evidence, says the score speaks only for the jobs the flow covers,
  lists the scores by round, gives the comparison's verdict, says the fixes stay in a
  draft for the owner, and places the next point in the test: real course content instead
  of placeholders. The open proposal (AI toolkit courses to week 3) is listed for the
  owner.

Earlier rounds' evaluators named rules 3 and 5 for this fixture. That was under an older
numbering; under the current text, rule 5 does not hold and rule 6 does. Wrong: naming
rule 4, continuing, or asking the user whether to stop.

## Scenario 7

Continue to round 7 without contacting the user.

Budget 100, so N = 10 and 2N = 20. Round 1 is the only baseline; 6 rounds are scored. Each
of rounds 1 to 6 applied at least one [direct][high] fix.

1. Target reached: does not hold. 8 is below the target of 9.
2. Budget spent: does not hold. 6 of 100 rounds.
3. No progress: cannot hold yet. It needs 10 rounds scored since the baseline, and there
   are 6. (Every round made progress anyway.)
4. Flat score: cannot hold yet. It needs 20 rounds scored in this run, and there are 6.
5. Nothing to change: does not hold. Round 6 applied two [direct][high] fixes.
6. Ceiling in the test: does not hold. Round 6 places the next point in the thing.
7. Can't go on safely: does not hold. There are no checks to fail, and the next point
   (consistency across the two billing emails) is a fix to the prompt that needs nothing
   from the owner. The open proposal on competitors and the pending decision on reply
   length don't end the run.

Expected decision:
- Continue: round 7 goes on from Step 4 with fresh evaluators and the saved brief.
- No comparison yet, and no message to the user.
- Not part of the key: how the answer fills the fixture's missing Run state, Checkpoint,
  and Evaluators line. The fixture is in the older layout, and the skill leaves room
  there (see the log entry of 2026-11-18).

Wrong: stopping, asking the user whether to continue, or treating the open proposal as a
reason to stop under rule 7.

## Scenario 8

Pick up round 4 at the stage "evaluators launched", under the sub-case "the tool can't
tell, or has no record of it". Round 4 is logged as incomplete with `sonnet` as its
primary, and the run goes on from Step 5 with `sonnet`'s report.

- Route: a run under way (the Run state doesn't say it ended), and the Checkpoint shows a
  round in hand, so pick it up as Step 6 says, before any stop rule. The log lacks
  nothing, so there is nothing to fill, and the spec is left alone.
- Checks aren't rerun and nothing is relaunched: the stage is past "checks run", and the
  versions still match.
- `sonnet`: its saved report is written against the recorded version, so it is used.
- `opus`: no saved report, so ask the tool. The tool has no record of it, which is the
  "can't tell, or has no record" case: write that in the Checkpoint and don't brief a
  fresh `opus`, since it could be a duplicate. Count it as returning no report.
- Log round 4 as incomplete, with `sonnet`, the strongest evaluator whose report is in
  hand, as the round's primary: its score is round 4's score of record for the target and
  the stop rules, and Step 5 applies its [direct] findings. Rule 7 doesn't apply, because
  a report is in hand.
- No message to the user.

Wrong: briefing a fresh `opus` (the "never started" branch), relaunching the round or
rerunning the checks, discarding `sonnet`'s report, ending the run under rule 7, checking
the stop rules before picking up the round, or asking the user.
