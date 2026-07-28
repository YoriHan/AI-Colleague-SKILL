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
  blind half. A verb known but with a field missing yields text=None for that
  field, which is also UNMEASURED, not zero.

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
    ("message", "send"):    [(1,               "body",        "delivered")],
    ("message", "cede"):    [("--reason",      "reason",      "metadata")],
    ("task", "create"):     [(0,               "title",       "surface"),
                             ("--description", "description", "surface")],
    ("task", "update"):     [("--description", "description", "surface"),
                             ("--title",       "title",       "surface")],
    ("task", "comment"):    [(1,               "comment",     "surface")],
    ("document", "edit"):   [("--old",         "old",         "surface"),
                             ("--new",         "new",         "surface")],
    ("document", "append"): [("--text",        "text",        "surface")],
}

_VALUE_FLAGS = {"--reason", "--description", "--title", "--old", "--new",
                "--text", "--thread", "--seen", "--in-reply-to", "-a",
                "--attachment"}


def _flag_value(argv, flag):
    for i, a in enumerate(argv[:-1]):
        if a == flag:
            return argv[i + 1]
    return None


def _positionals(argv):
    """Positional elements after the verb, in order. Flags and their values removed."""
    out, skip = [], False
    for a in argv[2:]:
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
    key = (str(argv[0]), str(argv[1]))
    if key not in _DISPATCH:
        return ("unknown", [])
    surface = f"{key[0]}_{key[1]}"
    pos = _positionals(argv)
    fields = []
    for sel, label, face in _DISPATCH[key]:
        if isinstance(sel, int):
            text = pos[sel] if sel < len(pos) and isinstance(pos[sel], str) else None
        else:
            text = _flag_value(argv, sel)
        fields.append({"field": label, "face": face, "text": text})
    return (surface, fields)


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 64
    print(f"{'artifact':34s} {'surface':15s} {'field':12s} {'face':10s} {'chars':>6s}")
    unknown = unmeasured = 0
    for p in argv[1:]:
        try:
            a = json.load(open(p, encoding="utf-8"))
        except Exception:
            print(f"{p:34s} {'unparsed':15s} {'-':12s} {'-':10s} {'-':>6s}")
            unknown += 1
            continue
        surface, fields = extract(a)
        if surface == "unknown":
            unknown += 1
            print(f"{p:34s} {surface:15s} {'-':12s} {'-':10s} {'-':>6s}")
            continue
        for f in fields:
            if f["text"] is None:
                unmeasured += 1
            print(f"{p:34s} {surface:15s} {f['field']:12s} {f['face']:10s} "
                  f"{len(f['text']) if f['text'] else 0:>6d}")
    print(f"# unknown verb / unparsed: {unknown}   absent fields (UNMEASURED, not zero): {unmeasured}")
    return 1 if unknown else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
