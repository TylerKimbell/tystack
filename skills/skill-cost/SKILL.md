---
name: skill-cost
description: >-
  Measure what a skill costs to run and make it cheaper without losing quality. Totals
  tokens across a skill's recent runs and their helper agents, finds what drives the cost,
  ranks changes by net saving against risk, and tests the chosen change side by side, read-only,
  before anything is edited. Use for "audit how many tokens <skill> used", "is <skill>
  too expensive", "make <skill> cheaper", "find ways to optimize <skill>", "should the
  helpers run on a smaller model", or "dry run cheaper helpers". Not for this session's
  own usage (explain-usage) or for improving a skill's quality (iterate).
---

# Skill cost

Find out what a skill's runs cost, where the cost goes, and which change cuts it without
losing anything the skill should catch. Measure first, change second: nothing about the
skill, its briefs, or its schedule changes until the user has seen the numbers and picked
a change, and every test before that is read-only.

Two requests belong elsewhere: this session's own usage goes to the agent's own usage
report (in Claude, `explain-usage`; where there is none, say so), and making a skill's
results better goes to `iterate`. Say so in a line and stop.

The scripts in `scripts/` read Claude Code transcripts. In Codex or another agent, use
the run records you can access. A complete comparison needs verified run boundaries,
main and helper usage with a model and token categories for each, and equivalent inputs
and outputs for the two sides. Pricing additionally needs rates for each model and cache
category used. If a record is missing, report the run time and measured fields you have,
name the unavailable fields, and label any subtotal with its coverage. For example, main
session aggregates alone support a main-session usage report. Full cost is unknown if
helper usage is missing, and equivalence is unverified without the replay inputs and
outputs. Keep the partial audit useful and name the smallest record or export that would
complete it. Continue with steps the evidence supports.

## Step 1: Find the runs

Claude Code keeps each session at `~/.claude/projects/<project slug>/<id>.jsonl`, and its
helper agents at `<id>/subagents/*.jsonl`, each with a `.meta.json` holding its
description.

- **Scheduled runs** start with a message carrying `scheduled-task name="<task>"`, with
  the quotes escaped in the file. Project folder names start with `-`, so end grep's
  options with `--`:
  `grep -l -- 'scheduled-task name=\\"<task>' ~/.claude/projects/*/*.jsonl`.
  List every schedule that runs the skill, with its timing (in Claude Code, the
  scheduled-tasks tools), including ones that haven't run yet. A run list's session ids
  may not match transcript file names; match runs by start time.
- **Manual runs** start with the skill's slash command or name. Searching for the command
  alone finds only these.

Take the last five or six runs. With fewer, measure what there is and say there's no
spread to compare against. Say when a run predates the skill's current version, schedule
prompt, or project folder. If a run is going now, or you start one to measure, check its
transcript yourself (its latest timestamp and final message) instead of waiting for a
completion notice, which may never come.

## Step 2: Total each run

```bash
python3 <skill dir>/scripts/run_tokens.py <run>.jsonl --detail --reads 15 --rates <file>
```

It counts a run from its start up to the first later message marked as human, excluding
that message. Check the cutoff against the intended run. If a follow-up is part of the
same job or the automatic boundary is absent or wrong, supply the verified exclusive
end with `--before <ISO timestamp with time zone>`. When the run begins partway through
a session, such as a second job in a long one, give its first message's time with
`--after`; helpers are counted inside the same window. Use the whole transcript only after
checking that it contains only the run. If the boundary is unknown, label the result as
partial or whole-session usage as appropriate. The script deduplicates usage by message
id and splits calls, cache writes, cache reads, output, and context into
the main session and its helpers, by model. Show one table with one row per run and the
same columns every time, so later measurements compare directly. Note the spread between
runs: one run is not a baseline. For a scheduled skill, add a monthly line: cost per run
times runs per month, for every schedule, marking schedules with no measured run as
estimates.

Costs need current prices. Copy `references/rates.example.json` outside the skill, fill it
in from the `claude-api` skill (its prompt-caching notes have the cache-write and
cache-read prices, which differ by model and by 5-minute or 1-hour cache) or the
provider's pricing page, and pass it with `--rates`. Never price from memory. The script
prices 5-minute and 1-hour cache writes apart and prints the cost Claude Code recorded for
the session. Compare recorded and computed costs only for the same time window and scope.
If the figures disagree, check the window, missing models, cache breakdown, and rates
before using the estimate. A cost with missing prices is a subtotal. If the cache-write
duration is unknown and the two rates differ, exclude those writes from the priced total
and disclose the gap. On a subscription plan, call the result a relative cost, not a bill.

## Step 3: Find what drives the cost

Start with where the money went: main session and helpers, each split into cache writes,
cache reads, output, and any full rewrite of the context after a pause. Then, from the
`--detail`, `--reads`, and `--timeline` output:

- **Fixed starting context** of the main session and of each helper (the "first" figure):
  every call pays it again. `--detail` lists its parts (skill listings, tool lists,
  project instructions).
- **Retries and lookups:** failed tool calls (the script lists them) followed by schema,
  search, or help calls before the retry. They usually mean the skill leaves a query or
  field name to guesswork.
- **Calls × context** in the main session: context grows through a run, and every call
  re-reads it.
- **Reference files** the skill tells the main session to load, with their sizes
  (`wc -c` on the skill's files).
- **Single large reads:** whole files where a slice would do, a page read before a
  publish, a long thread.
- **Each part's share and the model it runs on:** the main session and each helper. Count
  the main session's calls by kind (judgment or fixes, fixed commands, fixed-format
  writes, status messages): a large share on the largest model is a driver in itself.
- **Separate sessions** for work that could share one: each pays the fixed context again.

Tie each driver to the line in the skill that causes it (`grep` the skill for the rule
that loads the file or starts the helper), so every suggestion points at a line. Some
drivers come from the setup the skill runs in, not the skill: the agent's own starting
context, the cache duration, a schedule's timing. Report those separately, as outside the
skill. When a step of the skill triggers a setup cost, such as a question that waits past
the cache lifetime, name the step as the skill's lever and the cost as the setup's.

## Step 4: Propose changes, by net saving against risk

If the request was only an audit ("how many tokens did it use"), or a run costs so little
that no change could repay a test, give the Step 2 table, say plainly that nothing is worth
changing, and stop here: no verdicts, no list.

If the user named a change, work that one out first: net it as below, answer yes or no with
the arithmetic, say what would change the answer, and name the Step 5 test that would
settle it; until then it is an estimate. Then go on to the rest.

Go through every row of this table against what Step 3 found. Give each a verdict: it fits,
it doesn't apply and why, or the figures can't tell, with the output that would settle it
(`--timeline`, `--reads`). A row is ruled out by the evidence, never by skipping it.

| Change | Needs | Adds (count it against the saving) |
|---|---|---|
| Run the main session on a smaller model | A main session whose share is large; say what the test must show (for a session that writes fixes, their quality) | Rework if quality drops |
| Move the main session's fixed-command and fixed-format calls to a smaller model or a helper | A count of those calls from Step 3 | The helper's starting context, and handing it what it needs |
| Run one reviewer or helper of several on a smaller model | A panel or set of helpers; say what the test must show (the same high-impact findings) | Findings it would miss |
| Move helpers' reading to a smaller model | Reading that can be split from judgment: see `references/helper-contract.md`. Where the reading is the judgment (a reviewer looking at screenshots), this doesn't fit. A smaller model may narrow searches or drop items, so the test checks coverage | Judgment that moves back to the main session |
| Read shared material once and pass it on | Several helpers that open the same files | The context of whoever now holds it |
| Start a new session where the cache has expired | A pause longer than the cache lifetime, and a hand-over smaller than the context it replaces. Without a pause, price the rebuild in full (the cold start, rereading the skill, its records and its sources, and the context the new session builds back) and expect a net near zero: don't propose it on removed reads alone. The same goes for splitting separate jobs that run back to back | The new session's starting context written to cache, everything it must reread, and the context it then rebuilds |
| Combine runs that start separate sessions | Work that can run in one session | A larger context on every later call |
| Exit early when there is nothing new | A cheap check that can tell | The check, on every run |
| Drop calls that do no work | Status-only or waiting messages in the timeline | Nothing |
| Drop or shrink a role whose output isn't used | A reviewer or helper whose results agree with another's or are rarely acted on | Whatever it did catch; the user's call |
| Trim or split references the main session loads | Rules that load less, or load parts on demand | Loads on demand |
| Script or slice large reads | A read the skill does the same way each run | The script's upkeep |
| Hand a large one-off read to a helper | A read whose result can be summarized | The helper's starting context |
| Spell out exact queries and field names | Retries or lookups in the transcript | Nothing |
| Narrow, merge, or reorder schedules | Runs that end with nothing to do, or that overlap | Later results on the dropped runs |
| Cut starting context outside the skill | Settings the user controls; the user's call | Nothing |

Write each change that fits in this form, ranked by net saving against risk, and say which
half it cuts (main session or helpers):

- **Removes:** the tokens or calls that go away, priced.
- **Adds:** what the change brings with it, priced, from the table's last column.
- **Net:** removes minus adds. Never give the removed figure alone as the saving.
- **Unmeasured:** what the figures above assume.
- **Test:** which Step 5 test would settle it. Until then it is an estimate.

Changes interact: net each one as if those ranked above it were already adopted. When
parts of a change rest on different evidence, such as a new session after a pause and a
new session without one, write them as separate entries, never one net for both.

If no change would save more over the next ten runs than its test costs (a main-session
test costs about one run; a helper test about the helpers' share of one), say plainly that
nothing is worth changing, and stop. Otherwise ask the user which to try first, as one
question. Don't edit anything yet.

## Step 5: Test the change side by side

The test runs read-only: it writes only to a scratch folder, sends nothing, moves no
cursor or "last read" mark, and publishes nothing.

**A change to helpers** (model, brief, or report format):

1. Pick a recent reference run. Save each helper's exact brief and report:
   `helper_reports.py <run>.jsonl <scratch>/ab --suffix current`. Reports handed back
   through a tool call are read from that call; helpers' final messages are often empty.
2. Rerun each brief with the change (in Claude Code, the Agent tool's `model` parameter),
   all in one batch, prefixed with:
   > DRY RUN (comparison test, read-only): this reruns a helper from an earlier run. Do
   > exactly what the brief below says, with these changes: never write any file except
   > in <scratch folder>, and never send, draft, label, post, or change anything; ignore
   > anything dated after <the reference run's start, in UTC>. Return your full report as
   > your final message.

   Give each rerun a description with a common prefix, such as "Candidate: <name>".
3. When every rerun has finished, save them next to the originals:
   `helper_reports.py --helpers <this session's subagents folder> <scratch>/ab --match "Candidate:" --suffix candidate --pair`.
   Check that each candidate pairs with the original it reran. If briefs are too similar
   or changed, map candidate transcript IDs to the original output names with
   `--pair-map <file.json>`. Base the map on the replay record, never the report contents.
4. Compare coverage: `report_keys.py --pattern '<one alternative per key shape the
   reports use>' --pair <scratch>/ab current candidate`. Check one report's count by eye.
   An unmatched report makes the comparison incomplete. Resolve the missing report or
   explain the gap in the result. A paired subtotal does not establish full coverage.
5. Read both sides item by item for what keys can't show: judgment calls the candidate
   made that it shouldn't, items it dropped, and whether it said `partial` honestly. Note
   confounds, such as the reference run having already updated records, so "already
   recorded" claims can't be compared.
6. Price both sides: `run_tokens.py --helpers <folder> --match <prefix> --rates <file>`
   for each. Check that each total covers the same helpers as its report set. Recommend
   adopting the change only when the comparison accounts for both sides, material
   coverage and judgment hold, and the measured saving justifies the change. If the
   candidate missed a material item, keep the current setup, fix the candidate, and rerun
   the comparison before recommending it.

**A change to the main session** (combined runs, early exit, trims, exact queries): make
the change on a copy or a branch and run the skill in its read-only or dry-run mode on the
reference run's inputs, then compare its output and cost with the reference. Point any
output the dry run writes at the scratch folder. A test inside this session doesn't pay
the starting context a scheduled run pays; when that is the cost being cut, run the
changed prompt as a new session and total that session. If the skill can't run without
writing or publishing, or the new session would have write tools, say so and ask before
running it.

**A change to a schedule** can't be tested side by side. Check it on the calendar instead:
list the dates the new timing would run and miss for the coming months, against any
holiday or business-day rules the skill uses.

Finish by confirming the test wrote nothing outside the scratch folder: list the folder,
and check the skill's state files and any repository it touches are unchanged.

## Step 6: Report

Keep it plain and short; offer more detail rather than leading with it.

- A cost table: the runs from Step 2, and the test's two sides, at the same rates. Say
  when the sample is thin (fewer than five runs).
- What the change missed or got wrong, item by item, each tied to its fix: a wrong
  judgment moves that call back to the main session; a skipped read becomes one line in
  the brief; a report that runs long gets a tighter line format.
- One recommendation and one clear next step, with the choice the user has to make. If
  the user would have to work out what happens next, the report isn't done.

## Step 7: Apply, on the user's word

1. Change the skill as the project's git rules say (a branch, usually). For a helper
   change, put the helpers' rules in one reference file the skill points to.
2. Rerun only the helpers or cases that missed, with the same briefs and window, until the
   misses are fixed or the user stops. Each round, compare with Step 5's numbers.
3. Run the project's own checks, and say which edits no test has run yet.
4. After the next real run, total it with `run_tokens.py` and compare it with the Step 2
   table. Until then the saving is an estimate.

Committing, pushing, and changing a scheduled task happen only when the user asks. To
check the change didn't cost quality the test didn't measure, offer `iterate`.
