# Iterate log: returns desk handbook

Invented for the iterate self-test, the run log beside `resume-spec.md`. The shop, the
handbook, the hashes, and every name in it are made up.

## Flow: new staff walkthrough

**Run state:** 3 of 6 rounds logged, round 4 in hand; the primary's best score since the
round 1 baseline: 7, and for the whole run: 7; last round with progress: 3; starting
version: `handbook/returns.md` at commit 5d0c8a2; fixes in the working copy of
`handbook/returns.md`, uncommitted, as a draft for the owner.

**Checkpoint:**
Launch: these lines go above the brief, word for word, with the placeholders filled:
"Repository root: <repo root>. Scratch folder: <scratch root>/returns-round-<N>-<model>/,
empty; write only there." Agent type: a general-purpose subagent, with the model set per
evaluator (`opus`, `sonnet`) at high effort. Each launch is described as
`returns-round-<N>-<model>`; the tool gives each evaluator its own name when the call
returns. Scratch folders: `<scratch root>/returns-round-<N>-<model>/`, new and empty each
round. Reports are saved as they return to
`~/iterate-runs/returns-handbook/reports/round-<N>-<model>.md`, outside every scratch
folder.
Round in hand: round 4, stage: evaluators launched.
Versions: `handbook/returns.md` sha256 3b9e41c07d2a; `handbook/test/returns-cases.md`
sha256 8f20c6ae19b4; `handbook/test/till-sheet.md` sha256 c71d0e5a3f88.
Checks, run 2026-11-17 15:58 on those versions: sections passed (9 of 9 present); links
passed (14 of 14 land); amounts passed (6 of 6 examples add up).
Evaluators:
- `opus` (primary): launch recorded 2026-11-17 16:02; name: none yet; report: none saved
  (it would be `round-4-opus.md` in the reports folder).
- `sonnet`: launch recorded 2026-11-17 16:02; name: returns-round-4-sonnet; report saved
  2026-11-17 16:19 as `round-4-sonnet.md` in the reports folder.
Fixing: edit the working copy of `handbook/returns.md`, then rerun
`handbook/test/check_handbook.py` after every change. The owner's standing instructions:
never commit, and never touch the shop's real till or customer records.
Comparison: the starting version is `handbook/returns.md` at commit 5d0c8a2 and the final
version is the working copy; the comparing evaluator gets both texts labelled X and Y in
random order, on `opus` at high effort.

- **2026-11-16, round 1 (baseline). Panel: `opus` (primary), `sonnet`, high effort. Score
  of record 6/10.** Opus 6 (clear next step 6, findability 5, labels 7, timing 6, effort
  6); Sonnet 6 (6, 6, 7, 6, 6). Scenarios 1 to 6. Checks pass. Findings:
  - [direct][high] Opus, Sonnet: the no-receipt steps were split across two sections.
    Merged into one, with card and cash as two short lists.
  - [direct][high] Opus: the day-31 case had no answer. Added "Past 30 days" under the
    standard return, pointing to the shift lead.
  - [direct][low] Sonnet: "authorise" and "approve" used for the same step. Now "approve".
  - [proposal][low], open: Sonnet: let staff refund up to a set amount without the shift
    lead.
  High-impact [direct] fixes applied: 2. Next point (primary): in the thing. Cost: about
  60k and 58k tokens. Not covered within the flow: a customer who leaves mid-return.
- **2026-11-16, round 2. Panel as round 1. Score of record 7/10.** Opus 7 (7, 7, 7, 7, 6);
  Sonnet 7 (7, 7, 8, 7, 6). Checks pass. Findings:
  - [direct][high] Opus: the torn-seam case didn't say whether to refund or exchange.
    Added a two-line rule from the policy: damaged at sale, refund; worn, exchange only.
  - [direct][low] Opus: the till-short case was buried under "Cash". Moved to its own
    heading.
  High-impact [direct] fixes applied: 1. Progress: yes. Next point (primary): in the
  thing. Cost: about 61k and 57k tokens.
- **2026-11-17, round 3. Panel as round 1. Score of record 7/10.** Opus 7 (7, 7, 8, 7, 6);
  Sonnet 7 (7, 7, 8, 7, 7). Checks pass. Findings:
  - [direct][high] Opus, Sonnet: the shift lead's extension appeared only at the end.
    Added it to the top of the page and to each step that calls the shift lead.
  - [direct][low] Sonnet: the example refund total was written as a range. Now one
    amount.
  - [proposal][low], open: as round 1.
  High-impact [direct] fixes applied: 1. Progress: yes (best score unchanged at 7). Next
  point (primary): in the thing, "fewer steps for a card return without a receipt". Cost:
  about 59k and 58k tokens.
