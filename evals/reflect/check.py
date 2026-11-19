"""Checks for the reflect eval. Run from the repository root before every round.

Exits non-zero and names what failed, so a round never starts on a broken skill.

fixtures/sample-session.jsonl and fixtures/app-session.jsonl are invented sessions,
checked everywhere. The round's fixtures are private transcripts in evals/reflect/local/,
which git ignores. A clone without that folder (a fresh clone, CI) skips those checks and
says so; a round still needs them.
"""

import json
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
HERE = pathlib.Path(__file__).resolve().parent
LOCAL = HERE / "local"
SKILL = ROOT / "skills/reflect"
failures = []


def read(path):
    """Return a file's text, or record a failure and return "" if it can't be read."""
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, ValueError) as err:
        failures.append(f"{path.relative_to(ROOT).as_posix()}: {err}")
        return ""


def git(*args):
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True)


# Skill frontmatter: right name, description present and under the 1024-character limit.
skill = read(SKILL / "SKILL.md")
front = re.match(r"^---\n(.*?)\n---\n", skill, re.S)
if skill and not front:
    failures.append("SKILL.md has no frontmatter")
elif front:
    block = front.group(1)
    if not re.search(r"^name: reflect$", block, re.M):
        failures.append("SKILL.md frontmatter name is not 'reflect'")
    desc = re.search(r"^description: >-\n((?:  .*\n?)+)", block, re.M)
    if not desc:
        failures.append("SKILL.md frontmatter has no folded description")
    elif len(" ".join(desc.group(1).split())) >= 1024:
        failures.append("SKILL.md description is 1024 characters or longer")

# The Codex interface file must exist and name the skill.
interface = read(SKILL / "agents/openai.yaml")
if interface and "$reflect" not in interface:
    failures.append("agents/openai.yaml default_prompt doesn't name $reflect")

# Plugin manifests must parse.
for name in ("plugin.json", "marketplace.json"):
    try:
        json.loads((ROOT / ".claude-plugin" / name).read_text(encoding="utf-8"))
    except (OSError, ValueError) as err:
        failures.append(f".claude-plugin/{name}: {err}")

# The README must still describe the skill.
readme = read(ROOT / "README.md")
if readme and "| `reflect` |" not in readme:
    failures.append("README.md has no row for reflect")

# The digest script must compile and turn every fixture into at least one turn.
script = SKILL / "scripts/digest.py"
if subprocess.run([sys.executable, "-m", "py_compile", str(script)]).returncode:
    failures.append("scripts/digest.py does not compile")


def digest(*args):
    """Run digest.py and return (exit code, stdout)."""
    run = subprocess.run([sys.executable, str(script), *map(str, args)],
                         capture_output=True, text=True, encoding="utf-8", errors="replace")
    return run.returncode, run.stdout


# The public fixture is an invented session, so these run in every clone and in CI. They
# pin what the digest keeps, what it leaves out, and how --results brings output back.
SAMPLE = HERE / "fixtures/sample-session.jsonl"
if not SAMPLE.is_file():
    failures.append("evals/reflect/fixtures/sample-session.jsonl is missing")
else:
    code, plain = digest(SAMPLE)
    for want, why in (
        ("- User turns: 3\n", "three typed turns, with the reminder and meta records left out"),
        ("- User answered: Local clone", "the answer to a question the agent asked"),
        ("- Error: FAILED tools/tests/test_lint.py", "a tool error"),
        ("- Agent (general-purpose, haiku): Time the link checker", "a helper's setup"),
        ("- /work/tidepool/tools/tests/conftest.py", "a written file in the files section"),
    ):
        if code or want not in plain:
            failures.append(f"digest of the sample session lacks {why}")
    for leak in ("fetch tags: 38.9s", "14 passed", "SIDECHAIN-ONLY", "META-ONLY",
                 "REMINDER-ONLY"):
        if leak in plain:
            failures.append(f"digest of the sample session should leave out {leak!r}")
    code, full = digest(SAMPLE, "--turns", "1", "--results", "0")
    for want in ("fetch tags: 38.9s", "14 passed in 0.8s", "Result of Bash (an error):",
                 "expected 14 tags, got 0", "(showing [1])"):
        if code or want not in full:
            failures.append(f"--turns 1 --results 0 on the sample session lacks {want!r}")
    if "release branch" in full or "DNS lookups" in full:
        failures.append("--turns 1 on the sample session prints other turns")
    code, clipped = digest(SAMPLE, "--turns", "3", "--results", "20")
    if code or "Slowest stage: DNS" not in clipped or "more chars]" not in clipped:
        failures.append("--results 20 on the sample session does not clip a long output")
    if digest(SAMPLE, "--results", "-1")[0] == 0:
        failures.append("--results accepts a negative number")
    if "sent through the SDK" in plain:
        failures.append("digest of the sample session labels a typed turn as an SDK prompt")

# A second invented session, recorded the way an app built on the Agent SDK records one:
# the user's messages carry turnOrigin "sdk" and no origin. Every one of them is a turn.
APP = HERE / "fixtures/app-session.jsonl"
if not APP.is_file():
    failures.append("evals/reflect/fixtures/app-session.jsonl is missing")
else:
    code, app = digest(APP)
    for want, why in (
        ("- User turns: 3\n", "three turns, one for each prompt sent through the SDK"),
        ("## Turn 2: prompt sent through the SDK", "the label on a later SDK prompt"),
        ("Keep the old anchors working.", "the text of a later SDK prompt"),
        ("came from an app or a script", "the note that explains the label"),
        ("(The session was compacted here.", "the note where the session was compacted"),
        ("Command: /recap the anchors still work", "a slash command with its arguments"),
    ):
        if code or want not in app:
            failures.append(f"digest of the app session lacks {why}")
    for leak in ("SUMMARY-ONLY", "META-ONLY", "REMINDER-ONLY", "<command-"):
        if leak in app:
            failures.append(f"digest of the app session should leave out {leak!r}")

HAVE_FIXTURES = LOCAL.is_dir()
sessions = sorted((LOCAL / "sessions").glob("*.jsonl"))
if HAVE_FIXTURES and not sessions:
    failures.append("no fixture transcripts in evals/reflect/local/sessions/")
for path in sessions:
    run = subprocess.run([sys.executable, str(script), str(path)],
                         capture_output=True, text=True, encoding="utf-8", errors="replace")
    out = run.stdout
    turns = re.search(r"^- User turns: (\d+)", out, re.M)
    if run.returncode or not turns or int(turns.group(1)) < 1:
        failures.append(f"digest of {path.name} has no turns: {run.stderr.strip()[:200]}")
    elif "## Files written or edited" not in out:
        failures.append(f"digest of {path.name} has no files section")

# Every file the spec's fixtures depend on must exist.
if HAVE_FIXTURES:
    for rel in ("sessions.md", "artifacts/run_tokens.py"):
        if not (LOCAL / rel).is_file():
            failures.append(f"evals/reflect/local/{rel} is missing")
    if not list((LOCAL / "heldout").glob("*.jsonl")):
        failures.append("no held-out runs in evals/reflect/local/heldout/")

# The private fixtures must be ignored and untracked.
if git("check-ignore", "-q", "evals/reflect/local/sessions.md").returncode:
    failures.append("evals/reflect/local/ is not ignored by git")
if git("ls-files", "evals/reflect/local").stdout.strip():
    failures.append("files under evals/reflect/local/ are tracked by git")

# The run log and Run state live only in iterate-log.md, so evaluators can't read scores.
spec = read(HERE / "iterate.md")
if not (HERE / "iterate-log.md").is_file():
    failures.append("evals/reflect/iterate-log.md is missing")
if re.search(r"^\*\*Run state:\*\*", spec, re.M):
    failures.append("iterate.md holds a Run state; it belongs in iterate-log.md")

if failures:
    print("FAIL")
    for item in failures:
        print(f"- {item}")
    sys.exit(1)
if not HAVE_FIXTURES:
    print("OK: reflect checks pass (private fixture checks skipped: no evals/reflect/local/ here)")
else:
    print("OK: reflect checks pass")
