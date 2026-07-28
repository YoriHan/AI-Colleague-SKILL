#!/usr/bin/env python3
"""gate19_accept.py -- acceptance harness for gate19_shape.py revisions.

NOT a second criteria implementation. It imports whatever gate you point it at
and checks the three invariants Trace named in 5473, so a revision is accepted
by a run rather than by hand-written analysis each round:

  CHECK 1  criteria unchanged      scan_text(old) == scan_text(new), every file
  CHECK 2  emission == count       per tier, per file, for the new gate
  CHECK 3  flag integrity          no known_fp_source row sits on a line that
                                   also carries a real analytics token
                                   + the flagged-set delta (added / removed) is
                                     printed for the reviewer to judge

CHECK 3 deliberately does NOT assert "the flagged set only grows". r3->r4 shrank
it by 41 on purpose (the pre-down-weighting fix). Direction is a review call;
the harness reports the delta and only *asserts* the part that is unambiguously
wrong -- a row pre-labelled "known noise" while its line has analytics context.

Output is content-free: paths, line numbers, counts, tiers. Never a matched value.

Usage:
  gate19_accept.py --old <gate.py> --new <gate.py> --files <list.txt>
Exit: 0 all checks pass, 1 a check failed, 64 bad usage.
"""
import importlib.util, re, sys

# Metric vocabulary that is unambiguously analytics context. Same family as the
# gate's own METRIC list minus the two known-FP tokens -- vocabulary, not data.
ANALYTICS = re.compile(
    r"impressions?|\bimps?\b|clicks?|\bctr\b|positions?|\bpos\b"
    r"|曝光|点击|均位|展现|排名|点击率", re.I)


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def rows_of(gate, text, path):
    try:
        return gate.candidates(text, path, "ACCEPT")
    except TypeError:                      # pre-r4 signature
        return gate.candidates(text, path)


def tier_of(row):
    return row["criterion"].split("/")[0]


def key_of(row, path):
    """Normalised, revision-independent row key: path + line + tier.

    candidate_id shape changed between revisions (r4 added @<blob> and a
    :<criteria>+<annot> suffix), so keying on it directly makes every row look
    added AND removed. Found by this harness's own r3->r4 control printing
    +273/-226 -- i.e. "every row is new and every row is gone", which is the
    signature of a key that encodes the revision. True delta is +88/-41:
    88 newly-emitted SOFT rows, 41 HARD rows that r4 correctly un-flagged.
    """
    line = row["candidate_id"].split("#L")[1].split(":")[0]
    return f"{path}#L{line}:{tier_of(row)}"


def main(argv):
    if "--new" not in argv or "--files" not in argv:
        print(__doc__)
        return 64
    new_p = argv[argv.index("--new") + 1]
    files_p = argv[argv.index("--files") + 1]
    old_p = argv[argv.index("--old") + 1] if "--old" in argv else None

    new = load(new_p, "gate_new")
    old = load(old_p, "gate_old") if old_p else None
    paths = [l.strip() for l in open(files_p) if l.strip()]

    c1_bad, c2_bad, c3_bad = [], [], []
    flagged_new, flagged_old = set(), set()
    n_files = 0

    for p in paths:
        try:
            text = open(p, encoding="utf-8", errors="replace").read()
        except OSError:
            continue
        n_files += 1

        d_new = new.scan_text(text)
        if old is not None and old.scan_text(text) != d_new:
            c1_bad.append(p)

        rows = rows_of(new, text, p)
        for tier, count in d_new.items():
            emitted = sum(1 for r in rows if tier_of(r) == tier)
            if emitted != count:
                c2_bad.append((p, tier, count, emitted))

        lines = {"raw": text.splitlines(), "flat": new.flatten(text).splitlines()}
        for r in rows:
            if not r["known_fp_source"]:
                continue
            flagged_new.add(key_of(r, p))
            i = int(r["candidate_id"].split("#L")[1].split(":")[0])
            for v in ("raw", "flat"):
                seq = lines[v]
                if i - 1 < len(seq) and ANALYTICS.search(
                        new.PROVENANCE_RE.sub(" ", seq[i - 1])):
                    c3_bad.append(key_of(r, p))
                    break

        if old is not None:
            for r in rows_of(old, text, p):
                if r["known_fp_source"]:
                    flagged_old.add(key_of(r, p))

    print(f"# gate19_accept -- {n_files} file(s)")
    print(f"# new={new_p} criteria={getattr(new,'CRITERIA_VERSION','?')} "
          f"annot={getattr(new,'ANNOTATION_REV','?')}")

    if old is None:
        print("CHECK 1  criteria unchanged      SKIPPED (no --old)")
    else:
        print(f"CHECK 1  criteria unchanged      "
              f"{'PASS' if not c1_bad else 'FAIL'}  differing files: {len(c1_bad)}")
        for p in c1_bad[:10]:
            print(f"           {p}")

    print(f"CHECK 2  emission == count       "
          f"{'PASS' if not c2_bad else 'FAIL'}  mismatches: {len(c2_bad)}")
    for m in c2_bad[:10]:
        print(f"           {m[0]}  {m[1]}  count={m[2]} emitted={m[3]}")

    print(f"CHECK 3  flag integrity          "
          f"{'PASS' if not c3_bad else 'FAIL'}  "
          f"flagged rows on analytics-context lines: {len(c3_bad)}")
    for k in c3_bad[:10]:
        print(f"           {k}")

    if old is not None:
        print(f"           flagged delta: +{len(flagged_new - flagged_old)} "
              f"-{len(flagged_old - flagged_new)}  (reviewer call, not asserted)")

    failed = bool(c1_bad or c2_bad or c3_bad)
    print(f"# rc={1 if failed else 0}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
