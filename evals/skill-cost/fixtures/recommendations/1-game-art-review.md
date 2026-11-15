# Scenario 1: "Make iterate cheaper" (real figures, token counts only)

The user asks: "Find ways to make my iterate skill cheaper." Steps 1 and 2 are done; this
is what they produced. `iterate` runs rounds: each round, fresh reviewer helpers score a
thing and report findings, and the main session writes the fixes, verifies them and logs
the round. The user chose a panel of two reviewers per round (large model `fable` as
primary, `opus` second) plus one blind before-and-after comparison per budget.

One session ran three budgets back to back on one project (an art review of a browser game
from screenshots). Rates per million tokens: fable input 8, output 40, cache read 0.20,
5-minute write 10, 1-hour write 16; opus input 4, output 20, cache read 0.20, 5-minute
write 5, 1-hour write 8. Subscription plan.

| Budget | Rounds | Main calls | Main context, first to peak | Main $ | Helpers | Helpers $ | Total $ |
|---|---|---|---|---|---|---|---|
| A | 2 + comparison | 58 | 82k to 411k | 20.14 | 5 | 5.76 | 25.89 |
| B | 4 + comparison | 47 | 412k to 648k | 33.57 | 9 | 11.86 | 45.43 |
| C | 3 + comparison | 42 | 649k to 804k | 12.64 | 7 | 9.41 | 22.05 |

Main session, all three budgets ($66.35, all on fable):
- $24.10: three calls that rewrote the whole context to cache (307k, 557k, 642k tokens at
  the 1-hour rate) after pauses of more than an hour. The pauses were usage-limit stops.
- $17.72: output, 443k tokens, mostly the fix code the main session writes.
- $13.74: cache reads. Every call re-reads the whole context; a call in budget C costs
  about $0.15 before it does anything.
- $10.80: ordinary cache writes as the context grows (about 55k tokens a round, mostly the
  session's own output).
- Budget C's 42 main calls by kind: 9 write or apply fixes, 12 run the screenshot capture
  and draw-time checks (fixed commands), 8 open screenshots to verify a fix, 4 write the
  log (a fixed format), 9 are status-only messages sent while waiting on reviewers.
- A new session starts at 70k tokens. To continue a run it must read the skill (9k
  tokens), the spec and log (10k), and the parts of the 300k-character source it edits.

Helpers ($27.03):
- 9 fable reviewers, average $1.49, 6 to 9 calls each. 9 opus reviewers, average $1.02,
  13 to 17 calls each. 3 fable comparisons, average $1.47.
- Every helper starts at 51k tokens (the general-purpose agent's own setup), written to
  cache on its first call: $0.51 on fable, $0.26 on opus.
- Each reviewer reads the spec (2.6k tokens), 25 screenshots, and 3 to 8 slices of the
  source. Looking at the screenshots is the review. The brief is 800 tokens.
- The two reviewers' scores were within one point in all nine rounds. The skill's rule is
  that the primary wins a conflict, and most findings only the second reviewer raised
  were not applied.

The skill's reference files are 8k tokens, loaded once. Five failed tool calls, none
followed by lookups. Nothing is scheduled.
