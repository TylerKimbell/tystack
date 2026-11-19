# Iterate spec: returns desk handbook

Invented for the iterate self-test. The shop, the handbook, and every name in it are made
up.

## The thing

`handbook/returns.md`, a document for new staff at the returns desk of Larkspur Outdoor
Supply, an invented shop. A new staff member reads it on their first shift and comes back
to it when a return doesn't fit the usual case. Evaluators read it on disk with their file
tools.
**Jobs:** take a standard return; handle a return without a receipt; handle a damaged or
used item; know when to call a supervisor; close the till at the end of a shift.

## Guardrails

**In scope:** whether a new staff member can find and follow the right steps for each
return, the order of sections, labels, and examples.
**Out of scope:** the shop's return policy itself, such as the 30-day window.
**Fix directly:** wording, section order, headings, examples, and a missing step that the
policy already implies.
**Propose to the owner:** changing the policy, adding or removing a kind of return, or
changing who a supervisor is.

## Fixtures

- `handbook/test/returns-cases.md`: six invented returns, one per scenario, each with the
  customer's words and what they bring to the desk.
- `handbook/test/till-sheet.md`: an invented end-of-shift till sheet with every field
  blank.
- Neither file is included in this fixture; the run log records their hashes.
- A scratch folder for the evaluator's output: a new empty folder each round. Nothing in
  the handbook or the fixtures changes during a round, so no other reset is needed. The
  shop's real till and customer records are off limits.

## Checks

Run `handbook/test/check_handbook.py` before every round. It checks that every section
the table of contents names exists, that every link lands, and that every amount in the
examples adds up. All three must pass.

---

## Flow: new staff walkthrough
**Card:** user walkthrough
**Who and what:** a new staff member on their first shift at the returns desk, using the
handbook to handle each return without asking a colleague.
**Coverage:** exercises taking a standard return, a return without a receipt, a damaged
or used item, and when to call a supervisor; never touches closing the till.
**Target and budget:** 8/10 within 6 rounds.
**Evaluators:** `opus` (primary) and `sonnet`, both at high effort.
**Publishing:** a draft for the owner: changes stay in the working copy of
`handbook/returns.md`, which evaluators read on disk.

### Scenarios
1. A standard return with a receipt, inside 30 days.
2. A return with no receipt, paid by card.
3. A return with no receipt, paid in cash.
4. A jacket returned worn, with a torn seam.
5. A return on day 31.
6. A customer who asks for a refund larger than the till holds.

### Questions at each scenario
- What do I do now? What do I say to the customer? Where do I record it?
- The next step is obvious without reading everything; labels say what they do in the
  staff member's words; missing information has a clear consequence; nothing that loses
  money happens without a check.

### Rubric
Score from 1 to 10, a judgement, not an average of the sub-scores.
Anchors: 10, every scenario done without help or guessing; 7, all done with some
hesitation; 4, stuck in at least one; 1, unusable.
Sub-scores:
- Clear next step: at each scenario, what to do now is obvious from the top.
- Findability: anything the user needs is reached without hunting.
- Labels: titles, buttons, and notes say what they do in the user's words.
- Timing: every item says when it's due, and shows up when it matters.
- Effort: the scrolls, clicks, and reading each task takes.

### Settled decisions
- Supervisor calls go to the shift lead, never the store manager: the owner chose this.

### Brief

> You are a new staff member at the returns desk doing your first shift for the first
> time. Don't change the thing or its settings. Change data only in the fixtures the spec
> names, and list what you changed. Write anything you produce only in the scratch folder
> named at the top. Never touch the shop's real till or customer records.
>
> **What it's for:** the handbook tells new returns desk staff how to handle each kind of
> return on their own, and when to call the shift lead.
>
> **Settled decisions:** the spec's Settled decisions for this flow; don't raise or score
> them.
>
> **Read:** this spec, the shared part and the "Flow: new staff walkthrough" section, and
> any file they point to. Don't open the run log beside it; form your own view. Judge only
> what this flow's Who and what covers, even where the shared In scope is wider.
>
> **Scenarios:** the six in the flow's section. For each, take the matching case from
> `handbook/test/returns-cases.md` and follow the handbook as written.
>
> **How to reach it:** `handbook/returns.md` on disk, read with your file tools. You can't
> reach the shop's till or its customer records.
>
> **Report, in about 700 words:**
> 1. Score N/10 as a whole number, one line on what holds it back, and the sub-scores
>    (clear next step, findability, labels, timing, effort), also whole numbers.
> 2. How well it serves this flow overall.
> 3. Findings ranked by impact: where, what's wrong, the concrete change, and what the
>    change replaces. Tag each [direct] or [proposal] using the spec's guardrails, and
>    [high] or [low] impact.
> 4. Next point: what would raise the score by one, and whether that lies in the thing or
>    in the test (invented stand-ins, tools that can't reach part of it).
> 5. Alternatives: a different format or structure that would work better, and what it
>    would replace.
> 6. Keep: what works and shouldn't change.
> 7. What you changed in the fixtures, and what you couldn't check.
