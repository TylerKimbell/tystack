# Scenario 4: "Audit how many tokens changelog-lint used" (invented figures)

Steps 1 and 2 are done. `changelog-lint` is scheduled weekly (Mondays 09:00). Six runs,
all on the current version, cost $0.03 to $0.05 (average $0.04) on `haiku`. Monthly: about
$0.17.

Per run: 3 main calls, context 14k to 19k, no helpers, 600 tokens of output. The skill is
40 lines with no reference files. It reads the changelog's newest section (about 2k
tokens) and reports formatting problems. No failed tool calls. Five of the six runs found
at least one problem.
