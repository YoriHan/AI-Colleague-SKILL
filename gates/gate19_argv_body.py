#!/usr/bin/env python3
"""gate19_argv_body.py -- enumerate ALL scannable fields in an --args-file argv.

WHY THIS EXISTS
  Four lanes independently wrote the same extractor: "take the longest string
  in the array". It is wrong twice over, and neither failure announces itself.

  (1) It crosses surfaces. The longest string is not always delivered content:
        message send  -> longest string IS the body          (accidentally right)
        message cede  -> longest string is --reason, which is action metadata
                         with no delivered-content face at all
        task/document -> body lives on the task/document surface, recovered by
                         show/get with no seq and no version history

  (2) It returns ONE field, and several verbs carry MORE THAN ONE body-shaped
      field. Observed tonight, all four caught by sample luck rather than method:
        document edit -> --old AND --new      (UG 6012: --old had never been scanned)
        task create   -> title AND description (Gatlin 6035: title never scanned)
        message cede  -> reason mislabelled as body (SEO 6007)
        message send  -> right only because the corpus happened to be all sends (EG 6008)

  So this module (a) dispatches on the verb, never on length, (b) returns EVERY
  body-shaped field for that verb, and (c) REFUSES unknown verbs instead of
  guessing.

CONTRACT
  extract(argv) -> (surface, [Field, ...])
    Field = {field, face, text}
      face 'delivered'  -- real delivered content, channel-seq recoverable
           'metadata'   -- action metadata, NO delivered-content face
           'surface'    -- lives on task/document surface; recovery via
                           show/get only, no seq, no version history
  Unknown verb -> (surface='unknown', fields=[]). Callers MUST treat that as
  UNMEASURED, never as clean -- same rule the shape gate prints about its own
  blind half.

  COVERAGE, per field, because "0 chars" has three different meanings
  (Gatlin 6358, Trace 6363 -- a payload face that reached zero must not read
  like a face that was scanned and found clean):
      OK             text is present and non-empty
      PAYLOAD-EMPTY  the field exists in the argv but carries no characters
      ABSENT         the field is not in the argv at all
  PAYLOAD-EMPTY and ABSENT are both UNMEASURED. The exit code says so: any
  field not OK makes the run exit non-zero. An earlier version printed
  "absent fields: 1" and still exited 0 -- the rule was in the docstring and
  not in the code, which is the failure this whole file exists to prevent.

CLI output is content-free: path, surface, field, face, char count.
"""
import json, sys

# verb -> [(selector, field_label, face)]
#   selector "--flag"  -> value of that flag
#   selector int N     -> Nth POSITIONAL after the verb (0-based)
#
# Positional index, never a prefix test. An earlier draft of this file skipped
# any positional starting with "@" or "#" as "a target" -- which silently
# dropped every message body that opens with a mention (27 of 66 artifacts in
# the corpus it was written against). Guessing a field's role from its content
# is the same sin as guessing it from its length.
_DISPATCH = {
    # verified against `heliox <verb> --help` on 2026-07-28, not inferred.
    ("message", "send"):            [(3,                     "body",        "delivered")],
    ("message", "cede"):            [(("--reason",),         "reason",      "metadata")],
    ("task", "create"):             [(2,                     "title",       "surface"),
                                     (("-d", "--description"), "description", "surface")],
    ("task", "update"):             [(("-d", "--description"), "description", "surface"),
                                     (("--title",),          "title",       "surface")],
    ("task", "comments", "add"):    [(4,                     "comment",     "surface")],
    ("task", "comments", "update"): [(5,                     "comment",     "surface")],
    ("task", "done"):               [(("--comment", "-c"),   "evidence",    "surface")],
    ("document", "edit"):           [(("--old",),            "old",         "surface"),
                                     (("--new",),            "new",         "surface")],
    ("document", "create"):         [(("--content",),        "content",     "surface")],
    ("document", "seed"):           [(("--content",),        "content",     "surface")],
}


_VALUE_FLAGS = {"--reason", "--description", "-d", "--title", "--old", "--new",
                "--content", "--comment", "-c", "--thread", "--seen",
                "--in-reply-to", "-a", "--attachment", "--channel", "--assignee",
                "--deadline", "--labels", "--priority", "--status", "--collab-url"}


def _flag_value(argv, flags):
    """flags is a tuple of aliases -- `-d` and `--description` are the same field."""
    for i, a in enumerate(argv[:-1]):
        if a in flags:
            return argv[i + 1]
    return None


def _positionals(argv):
    """Positional elements, in order, from argv[0]. Flags and their values removed.

    Indices in _DISPATCH are absolute over positionals INCLUDING the verb tokens,
    so `message send #chan BODY` puts BODY at 3 and `task comments add REF BODY`
    puts BODY at 4. One origin, no per-arity offset -- but it means every index
    in the table must be counted from argv[0]. Changing this origin once already
    shifted every row by one; the synthetic controls below are what caught it,
    which is why rows the local corpus never exercises still need controls.
    """
    out, skip = [], False
    for a in argv:
        if skip:
            skip = False
            continue
        if isinstance(a, str) and a.startswith("-"):
            if a in _VALUE_FLAGS:
                skip = True
            continue
        out.append(a)
    return out


def extract(argv):
    if not isinstance(argv, list) or len(argv) < 2:
        return ("unknown", [])
    # longest verb prefix wins: `task comments add` before `task comments`.
    key = None
    for n in (3, 2):
        cand = tuple(str(x) for x in argv[:n])
        if cand in _DISPATCH:
            key = cand
            break
    if key is None:
        return ("unknown", [])
    surface = "_".join(key)
    pos = _positionals(argv)
    fields = []
    for sel, label, face in _DISPATCH[key]:
        if isinstance(sel, int):
            text = pos[sel] if sel < len(pos) and isinstance(pos[sel], str) else None
        else:
            text = _flag_value(argv, sel)
        if text is None:
            cov = "ABSENT"
        elif not str(text).strip():
            cov = "PAYLOAD-EMPTY"
        else:
            cov = "OK"
        fields.append({"field": label, "face": face, "text": text, "coverage": cov})
    return (surface, fields)


_CONTROLS = [
    # (argv, surface, field, expected_text) -- EVERY dispatch row has one.
    # Three rows shipped without a control at first (task comments update,
    # task done, document create). All three turned out correct when read off
    # `--help`, but "correct and unmeasured" is not a state this file is allowed
    # to ship: an untested row reads exactly like a tested one from the outside.
    # (argv, surface, field, expected_text) -- every dispatch row has one,
    # including the rows no local corpus exercises. Reindexing the positional
    # origin once shifted every int row by one and only these caught it.
    (["message", "send", "#c", "BODY", "--seen", "1"], "message_send", "body", "BODY"),
    (["message", "cede", "#c", "--reason", "R", "--seen", "1"], "message_cede", "reason", "R"),
    (["task", "create", "T", "-d", "D"], "task_create", "title", "T"),
    (["task", "create", "T", "-d", "D"], "task_create", "description", "D"),
    (["task", "update", "U3-1", "--title", "T", "-d", "D"], "task_update", "description", "D"),
    (["task", "update", "U3-1", "--title", "T", "-d", "D"], "task_update", "title", "T"),
    (["task", "comments", "add", "U3-1", "C"], "task_comments_add", "comment", "C"),
    (["task", "comments", "update", "U3-1", "cid", "C2"], "task_comments_update", "comment", "C2"),
    (["task", "done", "U3-1", "--comment", "EV"], "task_done", "evidence", "EV"),
    (["document", "create", "--content", "B", "--channel", "#c"], "document_create", "content", "B"),
    (["document", "edit", "x", "--old", "O", "--new", "N"], "document_edit", "old", "O"),
    (["document", "edit", "x", "--old", "O", "--new", "N"], "document_edit", "new", "N"),
    (["document", "seed", "x", "--content", "B"], "document_seed", "content", "B"),
    # coverage controls: "0 chars" must not be able to look like "scanned, clean"
    (["message", "send", "#c", "", "--seen", "1"], "message_send", "body", ""),
    (["message", "cede", "#c", "--seen", "1"], "message_cede", "reason", None),
    (["task", "list"], "unknown", None, None),
    (["totally", "madeup"], "unknown", None, None),
]


def selftest():
    bad = 0
    for argv, exp_surface, exp_field, exp_text in _CONTROLS:
        surface, fields = extract(argv)
        fld = next((f for f in fields if f["field"] == exp_field), None) if exp_field else None
        got = fld["text"] if fld else None
        ok = surface == exp_surface and got == exp_text
        # coverage must agree with the text: empty -> PAYLOAD-EMPTY, missing -> ABSENT
        if fld is not None:
            want = "ABSENT" if got is None else ("PAYLOAD-EMPTY" if not str(got).strip() else "OK")
            ok = ok and fld["coverage"] == want
        if not ok:
            bad += 1
            print(f"FAIL  {' '.join(argv[:3])}  surface={surface} {exp_field}={got!r}")
    print(f"# selftest: {len(_CONTROLS) - bad} pass / {bad} fail")
    return 1 if bad else 0


def main(argv):
    if "--selftest" in argv:
        return selftest()
    if len(argv) < 2:
        print(__doc__)
        return 64
    print(f"{'artifact':32s} {'surface':15s} {'field':11s} {'face':10s} "
          f"{'chars':>6s}  coverage")
    unknown = unmeasured = 0
    for p in argv[1:]:
        try:
            a = json.load(open(p, encoding="utf-8"))
        except Exception:
            print(f"{p:32s} {'unparsed':15s} {'-':11s} {'-':10s} {'-':>6s}  UNPARSED")
            unknown += 1
            continue
        surface, fields = extract(a)
        if surface == "unknown":
            unknown += 1
            print(f"{p:32s} {surface:15s} {'-':11s} {'-':10s} {'-':>6s}  UNKNOWN-VERB")
            continue
        for f in fields:
            if f["coverage"] != "OK":
                unmeasured += 1
            print(f"{p:32s} {surface:15s} {f['field']:11s} {f['face']:10s} "
                  f"{len(f['text']) if f['text'] else 0:>6d}  {f['coverage']}")
    print(f"# unknown verb / unparsed: {unknown}   "
          f"fields not OK (UNMEASURED, not clean): {unmeasured}")
    if unmeasured:
        print("# a PAYLOAD-EMPTY / ABSENT field was NOT scanned-and-clean; do not "
              "record it as clean", file=sys.stderr)
    return 1 if (unknown or unmeasured) else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
