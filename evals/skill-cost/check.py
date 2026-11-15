"""Synthetic behavioral checks for skill-cost. Use --report to see all probe outcomes."""
import argparse
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "skills/skill-cost/scripts"


def cli(script, *args):
    return subprocess.run(
        [sys.executable, str(SCRIPTS / script), *map(str, args)],
        capture_output=True, text=True, encoding="utf-8",
    )


def moment(second):
    return f"2026-01-01T00:00:{second:02}Z"


def user(second, text, **fields):
    return {"type": "user", "timestamp": moment(second), "message": {"content": text}, **fields}


def assistant(second, tokens, message_id, *, model="test-main", write=0, hour=0, read=0, out=0):
    return {
        "type": "assistant", "timestamp": moment(second),
        "message": {
            "id": message_id, "model": model, "content": [],
            "usage": {
                "input_tokens": tokens, "cache_creation_input_tokens": write,
                "cache_read_input_tokens": read, "output_tokens": out,
                "cache_creation": {"ephemeral_1h_input_tokens": hour},
            },
        },
    }


def json_file(path, value):
    path.write_text(json.dumps(value), encoding="utf-8")


def transcript(path, *records):
    path.write_text("".join(json.dumps(record) + "\n" for record in records), encoding="utf-8")


def accounting(root):
    run = root / "run.jsonl"
    main = assistant(3, 1_000_000, "main", write=1_000_000, hour=250_000, read=1_000_000, out=1_000_000)
    later = assistant(8, 2_000_000, "later")
    helpers = root / "run/subagents"
    helpers.mkdir(parents=True)
    transcript(helpers / "helper.jsonl", assistant(4, 1_000_000, "helper", model="test-helper"))
    rates = root / "rates.json"
    json_file(rates, {"models": {
        "test-main": {"input": 2, "output": 5, "cache_write_5m": 3, "cache_write_1h": 4, "cache_read": 1},
        "test-helper": {"input": 1, "output": 1},
    }})
    for name, marker, extra in (
        ("tagged human cutoff, dedup and split cache pricing", {"origin": {"kind": "human"}}, ()),
        ("legacy human cutoff", {"turnOrigin": "human"}, ()),
        ("explicit cutoff", {}, ("--before", moment(6))),
    ):
        transcript(run, user(1, "/audit"), main, main, user(6, "Later task", **marker),
                   assistant(6, 3_000_000, "on boundary"), later)
        result = cli("run_tokens.py", run, "--rates", rates, *extra)
        total = re.search(r"(?m)^  TOTAL .*?\$\s*([0-9.]+)", result.stdout)
        yield name, result.returncode == 0 and total is not None and float(total[1]) == 12.25
    transcript(run, user(0, "/earlier task"), assistant(1, 4_000_000, "earlier"), user(2, "/audit"),
               main, main, user(6, "Later task", origin={"kind": "human"}),
               assistant(6, 3_000_000, "on boundary"), later)
    result = cli("run_tokens.py", run, "--rates", rates, "--after", moment(2))
    total = re.search(r"(?m)^  TOTAL .*?\$\s*([0-9.]+)", result.stdout)
    whole = cli("run_tokens.py", run, "--rates", rates, "--before", moment(6))
    whole_total = re.search(r"(?m)^  TOTAL .*?\$\s*([0-9.]+)", whole.stdout)
    yield "start a run partway through a session", (
        result.returncode == 0 and total is not None and float(total[1]) == 12.25
        and whole_total is not None and float(whole_total[1]) > 12.25
    )
    transcript(run, user(1, "/audit"), main)
    result = cli("run_tokens.py", run, "--rates", ROOT / "skills/skill-cost/references/rates.example.json")
    yield "reject placeholder rate sheet", result.returncode != 0 and "placeholder" in result.stderr.lower()
    json_file(rates, {"models": {"test-main": {"input": 2, "output": 5}}})
    result = cli("run_tokens.py", run, "--rates", rates)
    yield "identify missing model rate", "test-helper" in result.stdout and "partial" in result.stdout.lower()
    json_file(rates, {"models": {"test-main": {"input": 2}, "test-helper": {"input": 1}}})
    result = cli("run_tokens.py", run, "--rates", rates)
    yield "identify missing used categories on known models", (
        result.returncode == 0 and "partial cost" in result.stdout
        and all(f"test-main/{key}" in result.stdout for key in ("cache_write_5m", "cache_write_1h", "cache_read", "output"))
    )
    cache_call = assistant(3, 1_000_000, "legacy-cache", write=1_000_000)
    del cache_call["message"]["usage"]["cache_creation"]
    transcript(run, user(1, "/audit"), cache_call)
    prices = {"models": {"test-main": {"input": 2, "cache_write_5m": 3, "cache_write_1h": 4},
                         "test-helper": {"input": 1}}}
    json_file(rates, prices)
    result = cli("run_tokens.py", run, "--rates", rates)
    yield "leave undifferentiated cache writes unpriced when duration matters", (
        result.returncode == 0 and "1,000,000 duration unknown" in result.stdout
        and "test-main/cache_write_duration_unknown" in result.stdout and "partial cost" in result.stdout
    )
    prices["models"]["test-main"] = {"input": 2}
    prices["cache_write_multiplier"] = 1.5
    json_file(rates, prices)
    result = cli("run_tokens.py", run, "--rates", rates)
    yield "apply an explicit common multiplier when supplied", (
        result.returncode == 0 and re.search(r"(?m)^  TOTAL .*?\$\s*6\.00$", result.stdout) is not None
    )


def pairing(root):
    sources = root / "helpers"
    sources.mkdir()
    brief = "Read every synthetic item before reporting the results."
    for index in (1, 2):
        name = f"agent-{index}"
        json_file(sources / f"{name}.meta.json", {"description": "Candidate: same name"})
        transcript(
            sources / f"{name}.jsonl",
            user(1, brief),
            {"type": "assistant", "message": {"content": [
                {"type": "tool_use", "name": "SendMessage", "input": {"message": f"item:{index}"}}
            ]}},
        )
    reports = root / "reports"
    result = cli("helper_reports.py", "--helpers", sources, reports, "--suffix", "current")
    found = {path.read_text(encoding="utf-8").strip() for path in reports.glob("*.current.md")}
    yield "retain helpers with duplicate descriptions", result.returncode == 0 and found == {"item:1", "item:2"}
    pair_targets = root / "pair-targets"
    pair_targets.mkdir()
    for side in ("first", "second"):
        (pair_targets / f"{side}.brief.md").write_text(brief, encoding="utf-8")
    args = ("--helpers", sources, pair_targets, "--suffix", "candidate", "--pair")
    result = cli("helper_reports.py", *args)
    yield "reject ambiguous brief matches before writing", (
        result.returncode != 0 and "ambiguous" in result.stderr.lower()
        and not list(pair_targets.glob("*.candidate*.md"))
    )
    mapping = root / "pairing.json"
    json_file(mapping, {"agent-1": "first", "agent-2": "first"})
    result = cli("helper_reports.py", *args, "--pair-map", mapping)
    yield "reject a map that reuses an original", (
        result.returncode != 0 and not list(pair_targets.glob("*.candidate*.md"))
    )
    json_file(mapping, {"agent-1": "first", "agent-2": "second"})
    result = cli("helper_reports.py", *args, "--pair-map", mapping)
    yield "accept an explicit one-to-one map", result.returncode == 0 and all(
        (pair_targets / f"{side}.candidate.md").read_text(encoding="utf-8") == f"item:{index}"
        for index, side in enumerate(("first", "second"), 1)
    )


def coverage(root):
    reports = root / "coverage"
    reports.mkdir()
    for name, contents in {
        "paired.current.md": "item:1 item:1 item:2",
        "paired.candidate.md": "item:1 item:3",
        "missing.current.md": "item:4",
        "extra.candidate.md": "item:5",
    }.items():
        (reports / name).write_text(contents, encoding="utf-8")
    result = cli("report_keys.py", "--pattern", r"item:\d+", "--pair", reports, "current", "candidate")
    yield "compare deduplicated keys in matched pair", "only current: item:2" in result.stdout and "only candidate: item:3" in result.stdout
    yield "show keys on both unmatched sides and mark comparison incomplete", (
        result.returncode == 2 and "item:4" in result.stdout and "item:5" in result.stdout
        and "incomplete" in result.stdout.lower()
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", action="store_true", help="show probe failures without a nonzero exit")
    args = parser.parse_args()
    with tempfile.TemporaryDirectory(prefix="skill-cost-check-") as directory:
        root = Path(directory)
        results = [*accounting(root), *pairing(root), *coverage(root)]
    for name, passed in results:
        print(f"{'PASS' if passed else 'FAIL'} {name}")
    failures = sum(not passed for _, passed in results)
    print(f"{len(results) - failures}/{len(results)} probes passed")
    return int(bool(failures and not args.report))


if __name__ == "__main__":
    sys.exit(main())
