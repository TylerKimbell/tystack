# Scenario 2: "Is morning-digest too expensive?" (invented figures)

Steps 1 and 2 are done. `morning-digest` is scheduled twice every weekday (07:00 and
13:00). Each run, the main session starts four helpers, one per source (mail, chat,
tickets, shared documents). Each helper lists and reads everything new since the last
run, then decides which items need the user's reply, and returns a written summary. The
main session merges the four summaries into one digest. All models are `opus`. Rates per
million: opus input 4, output 20, cache read 0.20, 5-minute write 5, 1-hour write 8;
haiku input 0.80, output 4, cache read 0.08, 5-minute write 1, 1-hour write 1.60.

Six recent runs, all on the current version, cost $3.10 to $3.60 (average $3.35):

| Part | Model | Calls | Context, first to peak | $ per run |
|---|---|---|---|---|
| Main session | opus | 9 | 62k to 95k | 0.75 |
| Mail helper | opus | 14 | 40k to 170k | 0.70 |
| Chat helper | opus | 16 | 40k to 185k | 0.78 |
| Tickets helper | opus | 11 | 40k to 140k | 0.55 |
| Documents helper | opus | 12 | 40k to 150k | 0.57 |

- Every helper's first read is the same two files: the team directory and the project
  list, 50k tokens together. The skill's line 41 says "each helper reads
  `people.md` and `projects.md` first".
- After that, 85% of each helper's tokens are listing and reading source items. Deciding
  what needs a reply is the last one or two calls.
- The skill's line 58 says helpers "decide which items need a reply".
- The 13:00 run found nothing new on 9 of the last 20 weekdays and still cost about $2.90.
- No failed tool calls.
