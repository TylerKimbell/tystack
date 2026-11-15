# Scenario 3: "Make release-notes cheaper" (invented figures)

Steps 1 and 2 are done. `release-notes` is run by hand, about twice a month. Three runs
exist, all on the current version: $1.92, $2.05, $1.98. No helpers. Model `opus` (input 4,
output 20, cache read 0.20, 1-hour write 8 per million).

Per run, on average:
- 7 main calls, context 96k to 118k.
- First call: 96k tokens written to cache at the 1-hour rate ($0.77). Of those 96k,
  the skill's own text is 1.5k and its one reference file 2k. The rest is the session's
  starting context: 41k of tool definitions from six connected servers, 22k skill listing,
  18k project instructions, 11.5k system prompt.
- Cache reads $0.14, later writes $0.18, output 4.2k tokens ($0.08). The remaining cost is
  a second full cache write in two of the three runs, when the user answered the skill's
  one question more than an hour later.
- The skill reads `git log` for the release range (about 6k tokens) and writes the notes.
- No failed tool calls.
