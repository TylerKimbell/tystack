# Scenario 5: "Should contract-review split into two sessions?" (invented figures)

Steps 1 and 2 are done, and the user has a change in mind: "Context gets huge. Split the
run into two sessions at the midpoint so the second half starts small. How much would
that save?" Rates per million for its model: cache read 0.50, 1-hour cache write 10,
output 30.

One run today, measured:
- 40 main calls. Context grows from 60k to 400k. The first 20 calls average 145k
  of context; the last 20 average 350k.
- A new session starts at 60k tokens.
- The second half (clause comparison) uses the first half's extracted clause table, which
  is 150k tokens. Today it is already in context. A new session would have to read it in.
- During the second half the context grows by another 150k (evenly, from tool results).
- Output is the same either way.
- The user runs it start to finish without pausing.
