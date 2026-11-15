# Answer notes

Open this file only after you have written your output for all six scenarios.

## Scenario 1

What the evidence supports. The first three matter most.
1. **A new session only pays after a pause.** The $24.10 of re-caching is the large,
   certain saving, and it exists only when a run resumes after the cache has expired. For
   a run that continues without a pause, the estimate must set what is removed (re-reading
   a large context) against what is added (a 70k cold start written to cache, re-reading
   the skill, spec, log and source, and the context it then builds). An answer that
   quotes the removed reads alone, or promises most of the main-session cost back, is
   wrong: a real three-round test found no saving with a warm cache ($18.91 against
   $18.55 to $19.45).
2. **Model choice is raised for the main session and for the second reviewer**, each with
   what would have to be tested (fix quality; whether the cheaper panel finds the same
   high-impact issues). The main session is 71% of cost and all on the top model; 25 of
   budget C's 42 calls are fixed commands, log writing, or status messages.
3. **No small-model gatherer inside these reviewers**, with the reason: the reading is the
   judgment. A good answer may suggest the mechanical main-session work (captures, checks,
   log writing) go to a cheaper model or a helper, and must say this is unmeasured.
4. The pauses themselves and the 51k helper start are reported as outside the skill.
5. The 9 status-only calls (about $1.35 in budget C) are noticed as avoidable.
6. Every kind of change in the skill's table gets a verdict, including "does not apply".
7. One question at the end; nothing edited.

Wrong: recommending a shorter reviewer brief as a main saving (the brief is 800 tokens).

## Scenario 2

1. **Move the helpers' reading to the small model and keep "needs a reply" in the main
   session**, as the helper contract says: line 58 has helpers interpreting, which must
   move. Monthly line first: about 44 runs a month, about $147.
2. **Read the two shared files once**, not four times: the main session (or one step)
   reads them and passes each helper only what it needs. The estimate must net this: the
   main session's context grows by what it now holds.
3. **Exit early or drop the empty 13:00 runs**: 9 of 20 found nothing at about $2.90.
   Needs a cheap check that can tell; a schedule change is checked on the calendar.
4. Estimates say what is added: the main session now classifies from fact lines, so its
   cost rises while the helpers' falls. A side-by-side test is required before adopting,
   and the answer says a smaller model may narrow searches or miss items.
5. Every kind of change gets a verdict. One question at the end.

Wrong: moving the reply decision to the small model; quoting haiku prices times today's
tokens as the saving with nothing added back.

## Scenario 3

1. **The driver is outside the skill**: 92.5k of the 96k first write is the session's own
   starting context, and the second large cost is the cache expiring while the skill waits
   for an answer. Both are reported separately as the setup's cost and the user's call.
2. **No edit to the skill's text is recommended as a saving.** At most: ask the question
   first, before anything large is in context, or take the release range as an argument so
   no question is needed. That one is inside the skill and is worth naming.
3. The answer says the total is about $4 a month and that three runs is a thin sample.
4. Every kind of change gets a verdict. One question at the end.

Wrong: proposing to trim the skill's 3.5k of text, helpers, or a smaller model as the main
saving without noting that the cost is the starting context.

## Scenario 4

1. The request was an audit, so the answer is the table, the spread, and the monthly line
   ($0.17).
2. **Nothing is worth changing**, said plainly: any test would cost more than a year of
   runs. No padded list of changes, no side-by-side test proposed.

Wrong: proposing changes, or asking which change to try.

## Scenario 5

The split as proposed costs more, and the answer must show the netting.
- Removed: the second half's reads today, 20 calls at an average 350k = 7.0M tokens,
  $3.50.
- Added: writing the new session's start plus the clause table to cache, 210k at $10 per
  million = $2.10; then 20 calls reading an average of about 285k (210k growing to 360k)
  = 5.7M, $2.85. Total added $4.95.
- Net: about $1.45 more per run. Figures within about 20% of these are fine.

1. **Recommend against the split as proposed**, with the arithmetic.
2. Say what would change the answer: a much smaller hand-over than the 150k table, or a
   pause at the midpoint long enough for the cache to expire.
3. Say it is an estimate until tested, and what the test would be.

Wrong: quoting $3.50, or any figure from the removed reads alone, as the saving.

## Scenario 6

This is a quality request, not a cost request. The skill's description sends it to
`iterate`. The right answer is one or two lines saying so, with no audit started and no
cost changes proposed. Wrong: starting Step 1, or proposing cost changes.
