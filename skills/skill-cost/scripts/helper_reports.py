#!/usr/bin/env python3
"""Save each helper agent's exact brief and its returned report from a past run.

Usage:
  helper_reports.py RUN.jsonl OUT_DIR [--match TEXT] [--suffix NAME]
  helper_reports.py --helpers DIR OUT_DIR [--match TEXT] [--suffix NAME]
      [--pair [--pair-map FILE]]

For every helper transcript in RUN/subagents/ (or DIR), writes:
  OUT_DIR/<helper>.brief.md      the first message the helper got: its brief, word for word
  OUT_DIR/<helper>.<suffix>.md   the report it returned (suffix defaults to "report")

<helper> combines the description with the transcript ID. Use --suffix to keep two
sides of a side-by-side test apart (such as "current" and "candidate").

--pair names each helper after the brief already in OUT_DIR that shares the most lines
with its own brief, so a rerun lands next to the original it reran even when its
description differs. Save the original run first, then the rerun with --pair. The rerun's
own brief is then written as <helper>.<suffix>.brief.md, leaving the original's in place.
When briefs tie, don't match, or would reuse an original, pass --pair-map FILE with
a JSON object mapping candidate transcript IDs to original output names (without .brief.md).

Where the report is: a helper that hands its result back with a tool call (a tool whose
name contains "handback", or SendMessage) has an empty or short final message, and the
report is that tool call's input. Otherwise the report is the helper's last text reply.
"""

import argparse
import glob
import json
import os
import re
import sys

REPORT_KEYS = ("report", "message", "content", "text", "result")


def records(path):
    with open(path, encoding="utf-8", errors="replace") as f:
        for line in f:
            try:
                yield json.loads(line)
            except ValueError:
                continue


def text_of(content):
    if isinstance(content, str):
        return content
    return "\n".join(b.get("text", "") for b in content or []
                     if isinstance(b, dict) and b.get("type") == "text")


def brief_and_report(path):
    """Return (brief, report, where the report came from) for one helper transcript."""
    brief, final, handback = None, None, None
    for d in records(path):
        m = d.get("message") or {}
        if d.get("type") == "user" and brief is None:
            brief = text_of(m.get("content"))
        if d.get("type") != "assistant":
            continue
        text = text_of(m.get("content"))
        if text.strip():
            final = text
        for b in m.get("content") or []:
            if not (isinstance(b, dict) and b.get("type") == "tool_use"):
                continue
            name = b.get("name", "")
            if "andback" in name.lower() or name == "SendMessage":
                inp = b.get("input") or {}
                found = next((inp[k] for k in REPORT_KEYS if isinstance(inp.get(k), str)), None)
                handback = found or json.dumps(inp, indent=1)
    if handback:
        return brief or "", handback, "hand-back tool call"
    return brief or "", final or "", "final message"


def best_pair(brief, originals):
    """Find a unique original brief or report why an explicit map is needed."""
    lines = {l.strip() for l in brief.splitlines() if len(l.strip()) > 20}
    matches, score = [], 0.5
    for name, path in originals.items():
        with open(path, encoding="utf-8") as f:
            theirs = {l.strip() for l in f.read().splitlines() if len(l.strip()) > 20}
        overlap = len(lines & theirs) / max(1, len(theirs))
        if overlap > score:
            matches, score = [name], overlap
        elif overlap == score:
            matches.append(name)
    if len(matches) != 1:
        problem = "ambiguous original briefs" if matches else "no matching original brief"
        raise ValueError(f"{problem}; use --pair-map")
    return matches[0]


def slug(desc, match):
    if match and desc.lower().startswith(match.lower()):
        desc = desc[len(match):]
    return re.sub(r"[^a-z0-9]+", "-", desc.lower()).strip("-") or "helper"


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("source", nargs="?", help="a run's transcript (.jsonl)")
    ap.add_argument("out", help="folder to write the briefs and reports into")
    ap.add_argument("--helpers", metavar="DIR", help="read helper transcripts from DIR instead")
    ap.add_argument("--match", help="only helpers whose description contains this text")
    ap.add_argument("--suffix", default="report", help="name for the report files")
    ap.add_argument("--pair", action="store_true",
                    help="name each helper after the matching brief already in OUT_DIR")
    ap.add_argument("--pair-map", help="with --pair, JSON mapping candidate transcript IDs to original output names")
    args = ap.parse_args()
    if not re.fullmatch(r"[a-zA-Z0-9_-]+", args.suffix):
        ap.error("--suffix must contain only letters, digits, underscores or hyphens")
    if args.pair_map and not args.pair:
        ap.error("--pair-map requires --pair")
    pair_map = None
    if args.pair_map:
        try:
            with open(args.pair_map, encoding="utf-8") as f:
                pair_map = json.load(f)
            if not isinstance(pair_map, dict) or not all(isinstance(name, str) for name in pair_map.values()):
                ap.error("--pair-map must map transcript IDs to original output names")
        except (OSError, ValueError) as err:
            ap.error(f"could not read --pair-map: {err}")

    folder = args.helpers or os.path.join(os.path.splitext(args.source or "")[0], "subagents")
    if not os.path.isdir(folder):
        sys.exit(f"No helper folder at {folder}")
    originals = {}
    if args.pair:
        for path in sorted(glob.glob(os.path.join(args.out, "*.brief.md"))):
            name = os.path.basename(path)[:-len(".brief.md")]
            if "." not in name:
                originals[name] = path
    exports = []
    used_names = set()
    for sp in sorted(glob.glob(os.path.join(folder, "*.jsonl"))):
        transcript_id = os.path.basename(sp)[:-len(".jsonl")]
        try:
            with open(sp[:-6] + ".meta.json", encoding="utf-8") as f:
                desc = json.load(f).get("description", "")
        except (OSError, ValueError):
            desc = transcript_id
        if args.match and args.match.lower() not in desc.lower():
            continue
        brief, report, where = brief_and_report(sp)
        if not brief.strip() or not report.strip():
            sys.exit(f"{transcript_id}: helper brief or report is missing")
        name = f"{slug(desc, args.match)}--{slug(transcript_id, None)}"
        brief_file = f"{name}.brief.md"
        if args.pair:
            try:
                name = best_pair(brief, originals) if pair_map is None else pair_map.get(transcript_id)
            except ValueError as err:
                sys.exit(f"{transcript_id}: {err}")
            if name not in originals:
                sys.exit(f"{transcript_id}: --pair-map must name an existing original brief")
            brief_file = f"{name}.{args.suffix}.brief.md"
        if name in used_names:
            sys.exit(f"{transcript_id}: ambiguous output name {name!r}; use a unique --pair-map for comparisons")
        used_names.add(name)
        report_file = f"{name}.{args.suffix}.md"
        for path in (brief_file, report_file):
            if os.path.exists(os.path.join(args.out, path)):
                sys.exit(f"{path} already exists; choose a fresh output folder or comparison suffix")
        exports.append((transcript_id, brief_file, report_file, brief, report, where))
    if not exports:
        sys.exit("No helper transcripts matched.")

    os.makedirs(args.out, exist_ok=True)
    for transcript_id, brief_file, report_file, brief, report, where in exports:
        with open(os.path.join(args.out, brief_file), "x", encoding="utf-8",
                  newline="\n") as f:
            f.write(brief)
        with open(os.path.join(args.out, report_file), "x", encoding="utf-8",
                  newline="\n") as f:
            f.write(report)
        print(f"{transcript_id}: {report_file}, {len(report):,} chars ({where})")


if __name__ == "__main__":
    main()
