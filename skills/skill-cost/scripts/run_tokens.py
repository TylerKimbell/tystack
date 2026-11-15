#!/usr/bin/env python3
"""Token totals, and optionally a cost, for Claude Code runs and their helper agents.

Usage:
  run_tokens.py RUN.jsonl [--after TIMESTAMP] [--before TIMESTAMP] [--detail] [--reads N] [--timeline] [--rates FILE]
      One run: the main session plus the helper transcripts in RUN/subagents/.
  run_tokens.py --helpers DIR [--match TEXT] [--rates FILE]
      Only helper transcripts in DIR (a subagents/ folder) whose description contains
      TEXT. Use it to total the helpers of a side-by-side test, which live in the session
      that ran the test, not in the run being compared.

Counting rules:
- A run is counted from its start, or from --after (inclusive) when the run begins
  partway through a session, up to, but excluding, --before or the first later message
  explicitly marked as human. Both take an ISO timestamp with a time zone. Helpers are
  counted inside the same window.
- Usage is deduplicated by message id: a streamed reply logs the same usage once per
  content block.
- "Context" for a call is input + cache write + cache read. "First" is the first call's
  context: the fixed cost every call of that session starts from.

Prices are never built in. --rates names a JSON file shaped like
references/rates.example.json, filled in from current prices (in Claude Code, the
claude-api skill). Cache writes are priced at their own rate: the 5-minute and 1-hour
writes in each call's usage are priced apart. Costs printed are at those rates, which on
a subscription plan are a relative cost, not a bill. Where the transcript records Claude
Code's own cost for the session, it is printed beside the computed one as a cross-check.
"""

import argparse
import glob
import json
import os
import sys
from collections import defaultdict
from datetime import datetime
from math import isfinite

USAGE_KEYS = ("input_tokens", "cache_creation_input_tokens", "cache_read_input_tokens",
              "output_tokens")


def utf8_output():
    """Print UTF-8 on every console, so non-ASCII text never crashes a report on Windows."""
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except AttributeError:
            pass


# --- Reading transcripts ----------------------------------------------------------

def load(path):
    """Return a transcript's records, skipping lines that are not valid JSON."""
    out = []
    with open(path, encoding="utf-8", errors="replace") as f:
        for line in f:
            try:
                out.append(json.loads(line))
            except ValueError:
                pass
    return out


def text_len(content):
    """Characters in a tool result's content, which is a string or a list of blocks."""
    if isinstance(content, str):
        return len(content)
    n = 0
    for c in content or []:
        if isinstance(c, dict):
            if c.get("type") == "text":
                n += len(c.get("text", ""))
            elif c.get("type") != "image":
                n += len(json.dumps(c))
    return n


def context(u):
    return sum(u.get(k) or 0 for k in USAGE_KEYS[:3])


def cache_split(usage):
    written = usage.get("cache_creation_input_tokens") or 0
    split = usage.get("cache_creation") or {}
    split_keys = ("ephemeral_5m_input_tokens", "ephemeral_1h_input_tokens")
    if not any(key in split for key in split_keys):
        return 0, 0, written
    hour = min(written, split.get("ephemeral_1h_input_tokens") or 0)
    return written - hour, hour, 0


def timestamp(value):
    time = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if time.utcoffset() is None:
        raise ValueError("timestamp must include a time zone")
    return time


def cutoff_for(entries):
    """Timestamp of the first message a person typed after the opening one, or None."""
    seen_first = False
    for d in entries:
        # Injected records (a command caveat, a reminder) are not the opening message.
        if d.get("type") != "user" or d.get("isSidechain") or d.get("isMeta"):
            continue
        c = (d.get("message") or {}).get("content")
        if isinstance(c, list) and all(isinstance(x, dict) and x.get("type") == "tool_result"
                                       for x in c):
            continue
        if not seen_first:
            seen_first = True
            continue
        origin = (d.get("origin") or {}).get("kind") or d.get("turnOrigin")
        if origin == "human" and d.get("timestamp"):
            return timestamp(d["timestamp"])
    return None


def describe_input(name, inp):
    """The part of a tool's input that says what it read: a path, command, or URL."""
    for key in ("file_path", "command", "url", "query", "path"):
        val = inp.get(key)
        if isinstance(val, str) and val.strip():
            return " ".join(val.split())[:110]
    return json.dumps(inp)[:110] if inp else ""


def tally(entries, cutoff=None, start=None):
    """Sum one transcript's usage per model, and collect its tool-result sizes."""
    calls = {}                   # message id -> (model, usage, timestamp)
    tools = {}                   # tool_use id -> (name, what it read)
    by_tool = defaultdict(lambda: [0, 0])   # tool name -> [chars, count]
    results = []                 # (chars, tool name, what it read)
    opening = defaultdict(int)   # attachment kind -> chars, before the first call
    errors = []                  # (timestamp, tool name, what it ran): failed tool calls
    recorded = None              # Claude Code's own cost for the session, if logged
    first_ts = last_ts = None
    for d in entries:
        ts = d.get("timestamp")
        if cutoff and ts and timestamp(ts) >= cutoff:
            continue
        if start and ts and timestamp(ts) < start:
            continue
        if ts:
            first_ts = first_ts or ts
        if d.get("type") == "cost-state" and d.get("totalCostUSD") is not None:
            recorded = d["totalCostUSD"]
        if d.get("type") == "attachment" and not calls:
            a = d.get("attachment")
            kind = a.get("type", "?") if isinstance(a, dict) else "?"
            opening[kind] += len(json.dumps(a))
        m = d.get("message") or {}
        # The run ends at its last reply or tool result, not at a late bookkeeping record.
        if ts and d.get("type") in ("assistant", "user"):
            last_ts = ts
        if d.get("type") == "assistant" and m.get("usage"):
            mid = m.get("id") or d.get("uuid")
            used = [c["name"].split("__")[-1] for c in m.get("content") or []
                    if isinstance(c, dict) and c.get("type") == "tool_use"]
            prev = calls.get(mid)
            calls[mid] = (m.get("model"), m["usage"], ts, (prev[3] if prev else []) + used)
            for c in m.get("content") or []:
                if isinstance(c, dict) and c.get("type") == "tool_use":
                    name = c["name"].split("__")[-1]
                    tools[c["id"]] = (name, describe_input(name, c.get("input") or {}))
        if d.get("type") == "user" and isinstance(m.get("content"), list):
            for c in m["content"]:
                if isinstance(c, dict) and c.get("type") == "tool_result":
                    name, what = tools.get(c.get("tool_use_id"), ("?", ""))
                    n = text_len(c.get("content"))
                    by_tool[name][0] += n
                    by_tool[name][1] += 1
                    results.append((n, name, what))
                    if c.get("is_error"):
                        errors.append((ts, name, what))

    models = defaultdict(lambda: defaultdict(int))
    peak = first = 0
    timeline = []
    for model, u, ts, used in sorted(calls.values(), key=lambda x: x[2] or ""):
        t = models[model]
        t["calls"] += 1
        for k in USAGE_KEYS:
            t[k] += u.get(k) or 0
        five, hour, unknown = cache_split(u)
        t["write_5m"] += five
        t["write_1h"] += hour
        t["write_unknown"] += unknown
        first = first or context(u)
        peak = max(peak, context(u))
        timeline.append((ts, context(u), u.get("cache_creation_input_tokens") or 0,
                         u.get("output_tokens") or 0, used))
    return {"models": models, "by_tool": by_tool, "results": results, "first": first,
            "peak": peak, "start": first_ts, "end": last_ts, "opening": opening,
            "recorded": recorded, "errors": errors, "timeline": timeline,
            "usages": [(model, u) for model, u, _, _ in calls.values()]}


def meta_description(transcript):
    meta = transcript[:-6] + ".meta.json"
    try:
        with open(meta, encoding="utf-8") as f:
            return json.load(f).get("description", "")
    except (OSError, ValueError):
        return ""


# --- Totals and cost --------------------------------------------------------------

def total(models):
    t = defaultdict(int)
    for v in models.values():
        for k, n in v.items():
            t[k] += n
    return t


def add(into, t):
    for k, n in t.items():
        into[k] += n


def rate_for(rates, model):
    """The rates entry whose key appears in the model id, longest key first."""
    for key in sorted(rates.get("models", {}), key=len, reverse=True):
        if key in (model or ""):
            return rates["models"][key]
    return None


def valid_price(value):
    return type(value) in (int, float) and isfinite(value) and value >= 0


def cache_price(model_rates, rates, key, shared=None):
    if key in model_rates:
        return model_rates[key]
    if shared and shared in model_rates:
        return model_rates[shared]
    multiplier = rates.get(f"{key}_multiplier", rates.get(f"{shared}_multiplier") if shared else None)
    base = model_rates.get("input")
    return base * multiplier if valid_price(base) and valid_price(multiplier) else None


def cost(usages, rates):
    """Price the categories that have a rate and identify every unpriced category."""
    if not rates:
        return None, set()
    dollars, missing = 0.0, set()
    for model, u in usages:
        r = rate_for(rates, model)
        if not r:
            missing.add(model)
            continue
        # A model's own cache prices win over the multipliers; a long-context tier
        # replaces the whole entry for calls above its threshold.
        long = r.get("long_context")
        if long and context(u) > long["above_tokens"]:
            r = long
        write_5m = cache_price(r, rates, "cache_write_5m", "cache_write")
        write_1h = cache_price(r, rates, "cache_write_1h", "cache_write")
        five, hour, unknown = cache_split(u)
        charges = [
            ("input", u.get("input_tokens"), r.get("input")),
            ("output", u.get("output_tokens"), r.get("output")),
            ("cache_read", u.get("cache_read_input_tokens"), cache_price(r, rates, "cache_read")),
            ("cache_write_5m", five, write_5m),
            ("cache_write_1h", hour, write_1h),
            ("cache_write_duration_unknown", unknown, write_5m if write_5m == write_1h else None),
        ]
        for category, tokens, price in charges:
            if tokens:
                if valid_price(price):
                    dollars += tokens * price / 1e6
                else:
                    missing.add(f"{model}/{category}")
    return dollars, missing


def fmt(t, dollars=None, missing=()):
    line = (f"calls {t['calls']:4}  in {t['input_tokens']:>9,}  "
            f"cache_write {t['cache_creation_input_tokens']:>10,}  "
            f"cache_read {t['cache_read_input_tokens']:>12,}  out {t['output_tokens']:>8,}")
    if dollars is not None:
        line += f"  ${dollars:8.2f}"
        if missing:
            line += " (partial cost)"
    return line


def models_line(models):
    return ", ".join(f"{m} x{v['calls']}" for m, v in models.items())


# --- Reports ----------------------------------------------------------------------

def report_run(path, detail, reads, timeline, rates, before, after=None):
    entries = load(path)
    scoped = [d for d in entries
              if not (after and d.get("timestamp") and timestamp(d["timestamp"]) < after)]
    cut = before if before is not None else cutoff_for(scoped)
    main = tally(entries, cut, after)
    helpers = []
    for sp in sorted(glob.glob(os.path.join(os.path.splitext(path)[0], "subagents", "*.jsonl"))):
        helper = tally(load(sp), cut, after)
        if helper["usages"]:
            helpers.append((meta_description(sp) or os.path.basename(sp), helper))

    mt = total(main["models"])
    ht = defaultdict(int)
    h_usages = []
    for _, h in helpers:
        add(ht, total(h["models"]))
        h_usages += h["usages"]
    m_cost, m_missing = cost(main["usages"], rates)
    h_cost, h_missing = cost(h_usages, rates)
    grand = defaultdict(int)
    add(grand, mt)
    add(grand, ht)

    start, end = main["start"] or "", main["end"] or ""
    print(f"{os.path.basename(path)[:8]}  {start[:16]} -> {end[11:16]} UTC  "
          f"cut={'yes' if cut else 'no'}  helpers={len(helpers)}  "
          f"main first context {main['first']:,}  peak {main['peak']:,}")
    if cut is None and after is None:
        print("  Whole transcript counted: verify the run ends there or supply --before.")
    elif cut is None:
        print("  Counted from --after to the end: verify the run ends there or supply --before.")
    missing = m_missing | h_missing
    print("  main   ", fmt(mt, m_cost, m_missing), " models:", models_line(main["models"]))
    print("  helpers", fmt(ht, h_cost, h_missing))
    print("  TOTAL  ", fmt(grand, None if m_cost is None else m_cost + h_cost, missing))
    written = grand["cache_creation_input_tokens"]
    if written:
        print(f"  cache writes: {grand['write_1h']:,} at 1 hour, {grand['write_5m']:,} at 5 minutes, "
              f"{grand['write_unknown']:,} duration unknown")
    if main["recorded"] is not None:
        print(f"  Claude Code recorded ${main['recorded']:.2f} for this session "
              "(at its own prices; compare with the computed total)")
    errors = main["errors"] + [e for _, h in helpers for e in h["errors"]]
    if errors:
        print(f"  failed tool calls: {len(errors)} (retries and lookups often follow them)")
        for ts, name, what in errors[:10]:
            print(f"    {(ts or '')[11:19]}  {name:16} {what}")
    if missing:
        print("  no rate for:", ", ".join(sorted(str(m) for m in missing)),
              "(left out of the cost)")

    if detail:
        if after is not None:
            # The window opens partway through the session, so attachments logged in it
            # are not what the session started with.
            print("  opening context: not listed with --after; run without it for the "
                  "session's starting context")
        elif main["opening"]:
            print("  opening context before the first call (chars, by kind):")
            for kind, n in sorted(main["opening"].items(), key=lambda x: -x[1]):
                print(f"    {kind:40} {n:>9,}")
        print("  main tool results by tool (chars, count):")
        for name, (n, k) in sorted(main["by_tool"].items(), key=lambda x: -x[1][0])[:15]:
            print(f"    {name:40} {n:>9,}  x{k}")
        print("  helpers:")
        for desc, h in helpers:
            t = total(h["models"])
            c, absent = cost(h["usages"], rates)
            money = f" ${c:.2f}" if c is not None else ""
            if absent:
                money += " (partial cost)"
            print(f"    {desc[:56]:56} calls {t['calls']:3} first {h['first']:>7,} "
                  f"peak {h['peak']:>7,} cache_read {t['cache_read_input_tokens']:>10,} "
                  f"out {t['output_tokens']:>7,}{money}  {models_line(h['models'])}")
            for name, (n, _) in sorted(h["by_tool"].items(), key=lambda x: -x[1][0])[:4]:
                print(f"        {name:52} {n:>9,} chars")
    if reads:
        print(f"  largest single tool results in the main session (top {reads}):")
        for n, name, what in sorted(main["results"], key=lambda x: -x[0])[:reads]:
            print(f"    {n:>9,}  {name:16} {what}")
    if timeline:
        print("  main session calls (time UTC, context, cache write, output, tools):")
        for ts, ctx, wrote, out, used in main["timeline"]:
            print(f"    {(ts or '')[11:19]}  {ctx:>9,}  {wrote:>8,}  {out:>6,}  {', '.join(used)}")


def report_helpers(folder, match, rates):
    rows, grand, usages = [], defaultdict(int), []
    for sp in sorted(glob.glob(os.path.join(folder, "*.jsonl"))):
        desc = meta_description(sp) or os.path.basename(sp)
        if match and match.lower() not in desc.lower():
            continue
        h = tally(load(sp))
        t = total(h["models"])
        add(grand, t)
        usages += h["usages"]
        c, missing = cost(h["usages"], rates)
        rows.append((desc, t, c, missing, h))
    if not rows:
        sys.exit(f"No helper transcripts in {folder}" + (f" matching {match!r}" if match else ""))
    for desc, t, c, missing, h in rows:
        print(f"  {desc[:48]:48} {fmt(t, c, missing)}  first {h['first']:,}  peak {h['peak']:,}")
    c, missing = cost(usages, rates)
    print(f"  {'TOTAL':48} {fmt(grand, c, missing)}")
    if missing:
        print("  no rate for:", ", ".join(sorted(str(m) for m in missing)))


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("run", nargs="?", help="a run's transcript (.jsonl)")
    ap.add_argument("--detail", action="store_true", help="per-tool and per-helper breakdown")
    ap.add_argument("--reads", type=int, default=0, metavar="N",
                    help="list the N largest single tool results in the main session")
    ap.add_argument("--timeline", action="store_true",
                    help="one line per main-session call: context, cache write, output, tools")
    ap.add_argument("--rates", help="JSON rates file; adds a cost column")
    ap.add_argument("--after", type=timestamp,
                    help="inclusive run start, for a run that begins partway through a session "
                         "(ISO timestamp with a time zone)")
    ap.add_argument("--before", type=timestamp, help="exclusive run cutoff (ISO timestamp with a time zone)")
    ap.add_argument("--helpers", metavar="DIR", help="total helper transcripts in DIR instead")
    ap.add_argument("--match", help="with --helpers: only descriptions containing this text")
    args = ap.parse_args()
    utf8_output()
    if (args.before is not None or args.after is not None) and args.helpers:
        ap.error("--after and --before apply to a run transcript, not --helpers")
    if args.before is not None and args.after is not None and args.after >= args.before:
        ap.error("--after must be earlier than --before")

    rates = None
    if args.rates:
        with open(args.rates, encoding="utf-8") as f:
            rates = json.load(f)
        if not isinstance(rates, dict) or not isinstance(rates.get("models"), dict) or not rates["models"]:
            ap.error("rates file must contain model prices")
        if rates.get("as_of") == "YYYY-MM-DD":
            ap.error("rates file contains the placeholder date; fill in the current prices and date")
        for model, entry in rates["models"].items():
            if not isinstance(entry, dict):
                ap.error(f"rates for {model} must be an object")
            if "long_context" in entry:
                tier = entry["long_context"]
                if not isinstance(tier, dict) or not valid_price(tier.get("above_tokens")):
                    ap.error(f"long_context for {model} needs a nonnegative above_tokens threshold")
    if args.helpers:
        report_helpers(args.helpers, args.match, rates)
    elif args.run:
        report_run(args.run, args.detail, args.reads, args.timeline, rates, args.before, args.after)
    else:
        ap.error("give a run transcript, or --helpers DIR")


if __name__ == "__main__":
    main()
