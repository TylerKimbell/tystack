#!/usr/bin/env python3
r"""Compare which items two helper reports cover, by the item keys they cite.

Usage:
  report_keys.py --pattern REGEX A.md [B.md]
  report_keys.py --pattern REGEX --pair DIR SUFFIX_A SUFFIX_B

With one file, prints its sorted unique keys. With two, prints how many each has and
which keys only one side cites. --pair checks both sides for unmatched reports, prints
their keys, and exits with status 2 when reports are missing. Its subtotal covers only
matched reports (the files helper_reports.py writes).

A key is whatever identifies one source item in the reports: a message, thread, ticket,
or document id. There is no default pattern, because a loose one silently miscounts:
write one alternative per key shape the reports actually use, for example
'(mail:[0-9a-f]{12,20}|case:\d{6,9})', and check one report's count by eye before
trusting a comparison.
"""

import argparse
import glob
import os
import re
import sys


def utf8_output():
    """Print UTF-8 on every console, so non-ASCII text never crashes a report on Windows."""
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except AttributeError:
            pass


def keys(path, pat):
    """The unique whole matches in a file (whole match, so groups in the pattern don't matter)."""
    with open(path, encoding="utf-8", errors="replace") as f:
        return {m.group(0) for m in pat.finditer(f.read())}


def compare(a, b, pat, label_a, label_b, show=True):
    ka, kb = keys(a, pat), keys(b, pat)
    only_a, only_b = sorted(ka - kb), sorted(kb - ka)
    print(f"{os.path.basename(a)}: {label_a} {len(ka)}, {label_b} {len(kb)}, "
          f"both {len(ka & kb)}, only {label_a} {len(only_a)}, only {label_b} {len(only_b)}")
    if show:
        for k in only_a:
            print(f"    only {label_a}: {k}")
        for k in only_b:
            print(f"    only {label_b}: {k}")
    return len(ka), len(kb), len(only_a), len(only_b)


def reports(folder, suffix):
    ending = f".{suffix}.md"
    return {os.path.basename(path)[:-len(ending)]: path
            for path in glob.glob(os.path.join(glob.escape(folder), "*" + glob.escape(ending)))}


def compare_pairs(folder, sa, sb, pat):
    first, second = reports(folder, sa), reports(folder, sb)
    if not (first or second):
        print("INCOMPLETE: no reports found for either suffix")
        return 2
    totals = [0, 0, 0, 0]
    for name in sorted(first.keys() & second.keys()):
        for i, count in enumerate(compare(first[name], second[name], pat, sa, sb)):
            totals[i] += count
    for present, other, label, missing_label in ((first, second, sa, sb), (second, first, sb, sa)):
        for name in sorted(present.keys() - other.keys()):
            found = sorted(keys(present[name], pat))
            print(f"{name}: no {missing_label} report; {len(found)} keys in {label}:")
            for key in found:
                print(f"    {key}")
    print(f"PAIRED SUBTOTAL: {sa} {totals[0]}, {sb} {totals[1]}, only {sa} {totals[2]}, "
          f"only {sb} {totals[3]}")
    if first.keys() != second.keys():
        print("INCOMPLETE: the subtotal excludes unmatched reports")
        return 2
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("files", nargs="*", help="one or two report files")
    ap.add_argument("--pair", nargs=3, metavar=("DIR", "SUFFIX_A", "SUFFIX_B"),
                    help="compare every <name>.SUFFIX_A.md with <name>.SUFFIX_B.md in DIR")
    ap.add_argument("--pattern", required=True,
                    help="regex for one item key, one alternative per key shape")
    args = ap.parse_args()
    utf8_output()
    pat = re.compile(args.pattern)

    if args.pair:
        folder, sa, sb = args.pair
        if sa == sb:
            ap.error("--pair requires two distinct suffixes")
        return compare_pairs(folder, sa, sb, pat)
    elif len(args.files) == 1:
        found = sorted(keys(args.files[0], pat))
        print(f"{len(found)} keys")
        for k in found:
            print(f"  {k}")
    elif len(args.files) == 2:
        compare(args.files[0], args.files[1], pat, "A", "B")
    else:
        sys.exit("Give one or two report files, or --pair DIR SUFFIX_A SUFFIX_B.")


if __name__ == "__main__":
    sys.exit(main())
