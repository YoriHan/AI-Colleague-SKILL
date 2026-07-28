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

CRITERIA_VERSION = "shape-1.1.0"
ANNOTATION_REV = "r6"   # annotations only; CRITERIA_VERSION deliberately NOT bumped
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
KNOWN_FP_SOURCES = ("session", "queries")   # canonical singular forms; annotation only


def _norm_token(tok: str) -> str:
    """Normalise a matched metric token to its canonical form for FP lookup.

    SEO (see channel record, plural-form residual): METRIC_RE matches the
    inflected form, so the plural surfaced as
    "sessions" and missed the singular-only tuple -- lines whose ONLY metric
    word was the plural went unflagged. Direction was safe (under-labelling,
    not pre-down-weighting), but the flag's coverage was SILENTLY incomplete,
    and "silently" is the property this whole exercise exists to remove.
    Normalising is preferred over listing both forms: the next vocabulary
    entry with a plural inflection is then covered without a second patch.
    """
    t = tok.strip().lower()
    if t.endswith("s") and t[:-1] in KNOWN_FP_SOURCES:
        return t[:-1]
    return t


# Metric vocabulary. NOT sensitive: these are measurement nouns, not data words.
# shape-1.1.0 (Trace 5711): ASCII alternatives had INCONSISTENT word boundaries --
# `\bimps?\b` and `\bpos\b` were guarded, `positions?` / `sessions?` / `clicks?` /
# `ctr` / `queries` were not, so `position` matched inside `disposition` and
# `composition`. Half a list guarded and half not, inside one declaration.
# Every ASCII alternative is now boundary-wrapped once, centrally, so the next
# vocabulary entry cannot inherit the omission.
# This is a CRITERIA change: shape-1.0.0 counts are superseded and NOT comparable.
_ASCII_METRIC = [
    r"impressions?", r"imps?", r"clicks?", r"ctr", r"positions?", r"pos",
    r"avg\.?\s*pos", r"impr\.", r"queries", r"sessions?", r"visitors?", r"pageviews?",
]
_CJK_METRIC = [r"曝光", r"点击率", r"点击", r"均位", r"展现", r"排名", r"访客", r"浏览量"]
METRIC_RE = re.compile(
    r"(?<![A-Za-z0-9_])(?:" + "|".join(_ASCII_METRIC) + r")(?![A-Za-z0-9_])"
    + "|" + "|".join(_CJK_METRIC), re.I)

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


def candidates(text: str, artifact: str = "-", blob_sha: str = "UNPINNED"):
    """Yield ledger rows: stable candidate_id + criterion, NEVER the matched value.

    candidate_id = <artifact>#L<line>:<criterion>  -- line-anchored and content-free,
    so it can be written into the adjudication ledger (Trace 5269) without the
    ledger itself becoming a disclosure surface. NOTE the id is line-anchored, so
    it is only stable while the artifact's line numbering is; pin it with a blob
    sha / version in `expires_or_version`.
    """
    rows = []
    for variant_name, variant in (("raw", text), ("flat", flatten(text))):
        for i, line in enumerate(variant.splitlines(), 1):
            probe = PROVENANCE_RE.sub(" ", line)
            if not METRIC_RE.search(probe):
                continue
            nums = NUM_RE.findall(probe)
            if not nums:
                continue
            # scan_text() counts a line in BOTH tiers when it qualifies for both,
            # so candidates() must emit one row per qualifying tier -- otherwise the
            # rows-vs-counts invariant SEO 5384(1) verified (1109/1109) silently breaks.
            tiers = ["HARD_metric_value"]
            if len(TICK_RE.findall(line)) >= 2:
                tiers.append("SOFT_ticked_metric")
            # SEO 5384(2): using only the FIRST metric match pre-labels lines that
            # ALSO carry a real metric word as "probably noise" -- silent
            # down-weighting, one layer inside the thing I said I would not do.
            all_hits = [m.group(0).lower() for m in METRIC_RE.finditer(probe)]
            hit = ",".join(sorted(set(all_hits)))
            only_fp = all(_norm_token(h) in KNOWN_FP_SOURCES for h in all_hits)
            for tier in tiers:
              rows.append({
                  # Trace 5347: a line anchor is only valid ON A GIVEN BLOB, so the
                  # blob sha and the criteria/annotation revs are part of the id,
                  # not metadata beside it. UNPINNED is a loud default, not a blank.
                  "candidate_id": (f"{artifact}@{blob_sha}#L{i}"
                                 f":{tier}:{CRITERIA_VERSION}+{ANNOTATION_REV}"),
                  "source_artifact": artifact,
                  "blob_sha": blob_sha,
                  "expires_or_version": f"valid-only-on blob {blob_sha}; criteria {CRITERIA_VERSION}; annot {ANNOTATION_REV}",
                  "criterion": f"{tier}/{CRITERIA_VERSION}",
                  "pass": variant_name,
                  "metric_token": hit,                      # vocabulary, not data
                  "known_fp_source": only_fp,   # ALL matches on the line, not just the first
              })
    seen, out = set(), []
    for r in rows:
        if r["candidate_id"] in seen:
            continue
        seen.add(r["candidate_id"]); out.append(r)
    return out


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
    ledger = "--ledger" in argv
    blob_sha = "UNPINNED"
    if "--blob" in argv:
        i = argv.index("--blob"); blob_sha = argv[i + 1]; del argv[i:i + 2]
    argv = [a for a in argv if a != "--ledger"]
    worst = 0
    print(f"# gate19_shape {CRITERIA_VERSION} annot={ANNOTATION_REV} -- SHAPE family only")
    print("# lexicon_result: NOT MEASURED by this tool. A PASS here is not 'clean'.")
    for path in argv[1:]:
        text = sys.stdin.read() if path == "-" else open(path, encoding="utf-8", errors="replace").read()
        if ledger:
            for r in candidates(text, path, blob_sha):
                print(f"{r['candidate_id']} | pass={r['pass']} "
                      f"| metric_token={r['metric_token']} | known_fp_source={r['known_fp_source']}")
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
