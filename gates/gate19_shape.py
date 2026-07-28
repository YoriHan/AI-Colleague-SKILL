#!/usr/bin/env python3
"""gate19_shape.py — Gate 19 SHAPE-family scanner (distributable).

WHY THIS IS SAFE TO DISTRIBUTE (the asymmetry vs the lexicon family):
  This file contains NO data words. Its criteria are structural: metric
  vocabulary (impressions/clicks/ctr/position/曝光/点击/均位 ...) adjacent to
  bare numeric tokens. Metric vocabulary is not the sensitive lexicon --
  the sensitive lexicon is the set of real query terms, which lives only
  in the LEXICON family (gate19_presend.py, salted/hashed, non-distributable).
  Therefore: no salt, no vault, no credential distribution. Ship it.

KNOWN STRUCTURAL BLIND HALF -- STATE IT WITH EVERY RESULT:
  Coverage of the zero-ambiguity (transliteration / bare-word) axis is ~0.
  Measured, not inferred: SEO Genius 5069 -- the HARD hits found across 7
  files were pure lexicon-family matches carrying no numeric density.
  A shape-only PASS therefore means "no metric-value form found",
  NEVER "clean". The two families are complementary and disjoint;
  neither is a weaker version of the other (Trace 5114).

REPORTING RULES (Trace 4906):
  Emit `path -- tier -- count` only. Never emit matched values.
  Report every door including empty ones. Never generalise to "clean".
"""
import re, sys, unicodedata

CRITERIA_VERSION = "shape-1.0.0"
ANNOTATION_REV = "r2"   # annotations only; CRITERIA_VERSION deliberately NOT bumped
                        # so results stay comparable across r1/r2 (Trace 5241).

# ---------------------------------------------------------------------------
# KNOWN-FP SOURCES -- adjudicated, NOT narrowed (Trace 5241).
#
#   "session"  : in this org's corpus this overwhelmingly means an agent RUNTIME
#                session, not an analytics session.
#   "queries"  : here it usually means "count of candidate query terms" in
#                planning text, not a measured query volume.
#
# Evidence (Gatlin, 2026-07-28): 21 HARD candidates across the two SKILL.md
# files adjudicated -> 0 measurement values; these two tokens were the dominant
# driver. Same turn, they also tripped a zero-metric channel inventory and the
# gate-report message itself -- three self-trips, one driver.
#
# NOT narrowed here on purpose. A unilateral narrowing inside a shared script is
# the move that keeps costing us (cf. the same-line-metric conjunction that was
# measured as a false-negative surface). Proposal pending criteria review:
# require these two to co-occur with analytics context (impressions/clicks/ctr/
# position). GSC Performance does not use either word, so GSC coverage would not
# regress -- but that is a REVIEW decision, not a maintainer decision.
#
# Until then: treat HARD hits driven solely by these tokens as candidates with a
# known-FP source. Adjudicate; do not auto-pass, and do not silently suppress.
# ---------------------------------------------------------------------------
KNOWN_FP_SOURCES = ("session", "queries")   # annotation only -- not used in matching


# Metric vocabulary. NOT sensitive: these are measurement nouns, not data words.
METRIC = [
    r"impressions?", r"\bimps?\b", r"clicks?", r"\bctr\b", r"positions?", r"\bpos\b",
    r"\bavg\.?\s*pos", r"impr\.", r"queries", r"sessions?", r"visitors?", r"pageviews?",
    r"曝光", r"点击", r"均位", r"展现", r"排名", r"访客", r"浏览量", r"点击率",
]
METRIC_RE = re.compile("|".join(METRIC), re.I)

# Bare numeric token: not part of an identifier, version, sha, or date fragment.
NUM_RE = re.compile(r"(?<![A-Za-z0-9._/-])\d[\d,]*(?:\.\d+)?%?(?![A-Za-z0-9_./-])")
TICK_RE = re.compile(r"`[^`\n]{1,60}`")

# Dates / seq refs / line refs are structurally number-dense but are provenance,
# not measurements. Excluded, and the exclusion is asserted by positive control.
PROVENANCE_RE = re.compile(
    r"\b20\d{2}-\d{2}-\d{2}\b|\bseq\s*\d+\b|\bline\s*\d+\b|\bL\d+\b|\bv\d+(?:\.\d+)*\b|\bU3-\d+\b|\bHEL-\d+\b",
    re.I)


def flatten(s: str) -> str:
    s = unicodedata.normalize("NFKC", s)
    s = re.sub(r"[*_~>#|]+", " ", s)          # markdown furniture
    s = re.sub(r"[ \t　]+", " ", s)
    return s


def scan_text(text: str):
    """Return {tier: count}. Two-pass: raw + flattened, deduped by line index."""
    doors = {"HARD_metric_value": set(), "SOFT_ticked_metric": set()}
    for variant in (text, flatten(text)):
        for i, line in enumerate(variant.splitlines()):
            probe = PROVENANCE_RE.sub(" ", line)
            if not METRIC_RE.search(probe):
                continue
            nums = NUM_RE.findall(probe)
            if nums:
                # unconditional: metric vocabulary co-located with bare numerics.
                # No "same-line metric word" conjunction beyond this -- SEO 4898
                # measured that tightening as a false-negative surface.
                doors["HARD_metric_value"].add(i)
            if len(TICK_RE.findall(line)) >= 2 and nums:
                doors["SOFT_ticked_metric"].add(i)
    return {k: len(v) for k, v in doors.items()}


def main(argv):
    if len(argv) < 2:
        print("usage: gate19_shape.py <file> [file ...]   (or - for stdin)")
        return 64
    worst = 0
    print(f"# gate19_shape {CRITERIA_VERSION} -- SHAPE family only")
    print("# lexicon_result: NOT MEASURED by this tool. A PASS here is not 'clean'.")
    for path in argv[1:]:
        text = sys.stdin.read() if path == "-" else open(path, encoding="utf-8", errors="replace").read()
        d = scan_text(text)
        for tier, n in d.items():          # every door reported, including empty
            print(f"{path} -- {tier} -- {n}")
        if d["HARD_metric_value"] > 0:
            worst = max(worst, 2)
        elif d["SOFT_ticked_metric"] > 0:
            worst = max(worst, 1)
    print(f"# rc={worst}  (2=HARD blocked, 1=SOFT review, 0=no metric-value form found)")
    return worst


if __name__ == "__main__":
    sys.exit(main(sys.argv))
