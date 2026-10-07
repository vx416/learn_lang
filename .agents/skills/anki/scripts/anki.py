#!/usr/bin/env python3
"""CLI for the AnkiConnect API (Anki desktop + AnkiConnect add-on, code 2055492159).

Stdlib only. Run from anywhere:

    python3 .agents/skills/anki/scripts/anki.py decks
    python3 .agents/skills/anki/scripts/anki.py models
    python3 .agents/skills/anki/scripts/anki.py fields --model Basic
    python3 .agents/skills/anki/scripts/anki.py list --deck Japanese --added 7
    python3 .agents/skills/anki/scripts/anki.py add --deck Japanese --field Front=犬 --field Back=dog --tags vocab,n5
    python3 .agents/skills/anki/scripts/anki.py add --deck Japanese --json notes.json
    python3 .agents/skills/anki/scripts/anki.py batch                  # current vocab batch deck and fill level
    python3 .agents/skills/anki/scripts/anki.py add --batch --model "Vocab Cloze" --json words.json
    python3 .agents/skills/anki/scripts/anki.py flush                  # import queued cards from queue/*.json into Anki
    python3 .agents/skills/anki/scripts/anki.py update --id 1234 --field "Back=dog (animal)" --add-tags animal
    python3 .agents/skills/anki/scripts/anki.py reset --deck English::Vocab::001
    python3 .agents/skills/anki/scripts/anki.py raw findNotes '{"query":"is:due"}'

When Anki is unreachable (e.g. on a machine without Anki installed), `list`, `batch`, and `add`
automatically fall back to the Git-tracked `queue/` directory (`queue/vocab.json`,
`queue/grammar.json`, and `queue/existing_index.json`).

Exit codes: 0 ok, 1 Anki unreachable, 2 AnkiConnect returned an error, 3 bad input.
"""

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.request

URL = os.environ.get("ANKICONNECT_URL", "http://127.0.0.1:8765")
SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(SKILL_DIR)))
QUEUE_DIR = os.path.join(REPO_ROOT, "queue")
MODEL_FILES = {
    "Vocab Cloze": os.path.join(SKILL_DIR, "vocab_cloze_model.json"),
    "Grammar Practice": os.path.join(SKILL_DIR, "grammar_practice_model.json"),
}
QUEUE_FILES = {
    "Vocab Cloze": os.path.join(QUEUE_DIR, "vocab.json"),
    "Grammar Practice": os.path.join(QUEUE_DIR, "grammar.json"),
}
INDEX_FILE = os.path.join(QUEUE_DIR, "existing_index.json")


class AnkiError(Exception):
    pass


class AnkiUnreachable(Exception):
    pass


def request(action, **params):
    payload = json.dumps({"action": action, "version": 6, "params": params}).encode()
    req = urllib.request.Request(URL, data=payload, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            body = json.load(resp)
    except (urllib.error.URLError, OSError) as e:
        raise AnkiUnreachable(
            f"Cannot reach AnkiConnect at {URL} ({e.reason if hasattr(e, 'reason') else e}).\n"
            "Is Anki open with the AnkiConnect add-on installed? Restart Anki after installing it."
        )
    if body.get("error"):
        raise AnkiError(body["error"])
    return body["result"]


def load_json_file(path, default):
    if not os.path.exists(path):
        return default
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save_json_file(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")


def refresh_existing_index():
    """Export all existing Vocab Cloze and Grammar Practice first-field keys to queue/existing_index.json."""
    index = load_json_file(INDEX_FILE, {"Vocab Cloze": [], "Grammar Practice": []})
    for model, first_field in [("Vocab Cloze", "Word"), ("Grammar Practice", "Target")]:
        ids = request("findNotes", query=f'model:"{model}"')
        notes = request("notesInfo", notes=ids) if ids else []
        vals = sorted({
            n["fields"][first_field]["value"].strip()
            for n in notes
            if first_field in n.get("fields", {}) and n["fields"][first_field]["value"].strip()
        })
        index[model] = vals
    save_json_file(INDEX_FILE, index)
    return index


def parse_fields(pairs):
    fields = {}
    for pair in pairs or []:
        if "=" not in pair:
            die(f"--field must be Name=Value, got: {pair!r}")
        name, value = pair.split("=", 1)
        fields[name] = value
    return fields


def parse_tags(s):
    return [t.strip() for t in (s or "").split(",") if t.strip()]


def die(msg, code=3):
    print(msg, file=sys.stderr)
    sys.exit(code)


def validate_fields(model, fields, cache):
    """Check field names against the note type. Returns error string or None."""
    if model not in cache:
        if model in MODEL_FILES and os.path.exists(MODEL_FILES[model]):
            cache[model] = load_json_file(MODEL_FILES[model], {})["inOrderFields"]
        else:
            cache[model] = request("modelFieldNames", modelName=model)
    expected = cache[model]
    unknown = [f for f in fields if f not in expected]
    if unknown:
        return f"unknown field(s) {unknown} for model {model!r}; it has {expected}"
    if not fields.get(expected[0], "").strip():
        return f"first field {expected[0]!r} of model {model!r} must not be empty"
    return None


# ---------- commands ----------

def cmd_decks(_):
    print("\n".join(request("deckNames")))


def cmd_models(_):
    print("\n".join(request("modelNames")))


def cmd_fields(args):
    print("\n".join(request("modelFieldNames", modelName=args.model)))


def build_query(args):
    if args.query:
        return args.query
    parts = []
    if args.deck:
        parts.append(f'deck:"{args.deck}"')
    if args.tag:
        parts.append(f"tag:{args.tag}")
    if args.added:
        parts.append(f"added:{args.added}")
    if args.rated:
        parts.append(f"rated:{args.rated}")
    if args.due:
        parts.append("is:due")
    if args.new:
        parts.append("is:new")
    return " ".join(parts) or "*"


def offline_list(query, args):
    index = load_json_file(INDEX_FILE, {})
    rows = []
    for model, first_field in [("Vocab Cloze", "Word"), ("Grammar Practice", "Target")]:
        for val in index.get(model, []):
            rows.append({
                "noteId": "existing-index",
                "modelName": model,
                "tags": ["indexed"],
                "fields": {first_field: val},
            })
        for item in load_json_file(QUEUE_FILES[model], []):
            rows.append({
                "noteId": "queued",
                "modelName": model,
                "tags": item.get("tags", []),
                "fields": item.get("fields", {}),
            })

    terms = [m[0] or m[1] for m in re.findall(r'(?:Word|Target):(?:"([^"]+)"|([^\s)]+))', query, re.I)]
    if terms:
        lower_terms = {t.lower() for t in terms}
        rows = [
            r for r in rows
            if next(iter(r["fields"].values()), "").strip().lower() in lower_terms
        ]
    elif query != "*":
        q_lower = query.lower()
        rows = [r for r in rows if q_lower in json.dumps(r, ensure_ascii=False).lower()]

    total = len(rows)
    rows = rows[: args.limit]
    if args.json:
        json.dump({"query": query, "offline": True, "total": total, "notes": rows}, sys.stdout, ensure_ascii=False, indent=2)
        print()
        return
    print(f"Query: {query} (offline mode: checked queue/ & existing_index.json)\n")
    for i, n in enumerate(rows, 1):
        print(f"--- {i}. note {n['noteId']} [{n['modelName']}] ---")
        for k, v in n["fields"].items():
            if v.strip():
                print(f"  {k}: {v}")
        if n["tags"]:
            print(f"  Tags: {', '.join(n['tags'])}")
        print()
    print(f"Showing {len(rows)} of {total} notes.")


def cmd_list(args):
    query = build_query(args)
    try:
        ids = request("findNotes", query=query)
        total = len(ids)
        notes = request("notesInfo", notes=ids[: args.limit]) if ids else []
    except AnkiUnreachable:
        offline_list(query, args)
        return
    rows = [
        {"noteId": n["noteId"], "modelName": n["modelName"], "tags": n["tags"],
         "fields": {k: v["value"] for k, v in n["fields"].items()}}
        for n in notes
    ]
    if args.json:
        json.dump({"query": query, "total": total, "notes": rows}, sys.stdout, ensure_ascii=False, indent=2)
        print()
        return
    print(f"Query: {query}\n")
    for i, n in enumerate(rows, 1):
        print(f"--- {i}. note {n['noteId']} [{n['modelName']}] ---")
        for k, v in n["fields"].items():
            if v.strip():
                print(f"  {k}: {v}")
        if n["tags"]:
            print(f"  Tags: {', '.join(n['tags'])}")
        print()
    print(f"Showing {len(rows)} of {total} notes.")


# ---------- vocab batches: parent::001, parent::002, ... each holding at most N notes ----------

def batch_state(parent, size):
    """Return (number, count) of the batch that should receive the next note.

    Creates parent::001 if no batch exists yet, and the next batch when the
    latest one is full.
    """
    prefix = parent + "::"
    nums = [int(d[len(prefix):]) for d in request("deckNames")
            if d.startswith(prefix) and d[len(prefix):].isdigit()]
    if not nums:
        create_batch_deck(parent, 1)
        return 1, 0
    num = max(nums)
    count = len(request("findNotes", query=f'deck:"{batch_deck_name(parent, num)}"'))
    if count >= size:
        num += 1
        create_batch_deck(parent, num)
        count = 0
    return num, count


def batch_deck_name(parent, num):
    return f"{parent}::{num:03d}"


def create_batch_deck(parent, num):
    """Create parent::NNN and give it the same deck options preset as the parent."""
    deck = batch_deck_name(parent, num)
    request("createDeck", deck=deck)
    config_id = request("getDeckConfig", deck=parent)["id"]
    request("setDeckConfigId", decks=[deck], configId=config_id)
    return deck


def cmd_batch(args):
    try:
        num, count = batch_state(args.batch_parent, args.batch_size)
        print(f"{batch_deck_name(args.batch_parent, num)} ({count}/{args.batch_size})")
    except AnkiUnreachable:
        model = "Grammar Practice" if "Grammar" in args.batch_parent else "Vocab Cloze"
        qpath = QUEUE_FILES[model]
        queued = load_json_file(qpath, [])
        known = load_json_file(INDEX_FILE, {}).get(model, [])
        rel_q = os.path.relpath(qpath, REPO_ROOT)
        print(f"offline (Anki unreachable) — {rel_q}: {len(queued)} pending | existing_index.json: {len(known)} known")


def queue_notes_offline(validated_items, args):
    """Append validated notes to queue/vocab.json or queue/grammar.json when Anki is offline."""
    index = load_json_file(INDEX_FILE, {})
    blocked = []
    to_queue = []

    # Track existing keys per model across existing_index.json and queue/*.json
    existing_keys = {}
    queues = {}
    for model, qpath in QUEUE_FILES.items():
        queues[model] = load_json_file(qpath, [])
        keys = {k.strip().lower() for k in index.get(model, [])}
        for item in queues[model]:
            first_val = next(iter(item.get("fields", {}).values()), "").strip().lower()
            if first_val:
                keys.add(first_val)
        existing_keys[model] = keys

    for i, item in enumerate(validated_items):
        model = item["modelName"]
        if model not in QUEUE_FILES:
            die(f"offline queue only supports {list(QUEUE_FILES)}, got {model!r}", 1)
        first = next(iter(item["fields"].values())).strip()
        key = first.lower()
        if not args.allow_duplicate and key in existing_keys[model]:
            blocked.append((i, first, "cannot create note because it is a duplicate (in offline index/queue)"))
        else:
            existing_keys[model].add(key)
            to_queue.append(item)

    if blocked:
        for i, first, reason in blocked:
            print(f"skip note {i} ({first!r}): {reason}", file=sys.stderr)
        if not args.partial:
            die("nothing queued. Use --partial to queue the others, or --allow-duplicate.", 2)

    touched_models = set()
    for item in to_queue:
        model = item["modelName"]
        queues[model].append({"fields": item["fields"], "tags": item["tags"]})
        touched_models.add(model)
        rel_q = os.path.relpath(QUEUE_FILES[model], REPO_ROOT)
        first = next(iter(item["fields"].values())).strip()
        print(f"queued note to {rel_q!r} (total {len(queues[model])} in queue): {first}")

    for model in touched_models:
        save_json_file(QUEUE_FILES[model], queues[model])


def add_items_online(validated_items, batch_mode, batch_parent, batch_size, allow_duplicate, partial):
    if batch_mode:
        batch_num, batch_count = batch_state(batch_parent, batch_size)

    notes = []
    for item in validated_items:
        if batch_mode:
            if batch_count >= batch_size:
                batch_num, batch_count = batch_num + 1, 0
                create_batch_deck(batch_parent, batch_num)
            deck = batch_deck_name(batch_parent, batch_num)
            batch_count += 1
        else:
            deck = item["deckName"]
        notes.append({
            "deckName": deck,
            "modelName": item["modelName"],
            "fields": item["fields"],
            "tags": item["tags"],
            "options": {"allowDuplicate": allow_duplicate},
        })

    checks = request("canAddNotesWithErrorDetail", notes=notes)
    blocked = [(i, c["error"]) for i, c in enumerate(checks) if not c["canAdd"]]
    if blocked:
        for i, reason in blocked:
            first = next(iter(notes[i]["fields"].values()))
            print(f"skip note {i} ({first!r}): {reason}", file=sys.stderr)
        if not partial:
            die("nothing added. Use --partial to add the others, or --allow-duplicate.", 2)
        notes = [n for i, n in enumerate(notes) if i not in {b[0] for b in blocked}]
        if not notes:
            return

    ids = request("addNotes", notes=notes)
    for n, nid in zip(notes, ids):
        first = next(iter(n["fields"].values()))
        print(f"added note {nid} to {n['deckName']!r}: {first}")


def cmd_add(args):
    if args.json:
        src = sys.stdin if args.json == "-" else open(args.json, encoding="utf-8")
        with src:
            items = json.load(src)
        if not isinstance(items, list):
            die("--json must contain a list of {deck?, model?, fields, tags?} objects")
    else:
        if not args.field:
            die("give at least one --field Name=Value, or --json")
        items = [{"fields": parse_fields(args.field), "tags": parse_tags(args.tags)}]

    if args.batch and args.deck:
        die("use either --deck or --batch, not both")

    validated_items, cache = [], {}
    for i, it in enumerate(items):
        deck = None if args.batch else (it.get("deck") or args.deck)
        model = it.get("model") or args.model
        if not args.batch and not deck:
            die(f"note {i}: no deck (set --deck or a 'deck' key)")
        fields = it.get("fields") or {}
        err = validate_fields(model, fields, cache)
        if err:
            die(f"note {i}: {err}")
        validated_items.append({
            "deckName": deck,
            "modelName": model,
            "fields": fields,
            "tags": it.get("tags") or parse_tags(args.tags),
        })

    if args.queue:
        queue_notes_offline(validated_items, args)
        return

    try:
        add_items_online(
            validated_items,
            batch_mode=args.batch,
            batch_parent=args.batch_parent,
            batch_size=args.batch_size,
            allow_duplicate=args.allow_duplicate,
            partial=args.partial,
        )
        try:
            refresh_existing_index()
        except Exception:
            pass
    except AnkiUnreachable:
        queue_notes_offline(validated_items, args)


def cmd_flush(args):
    """Import queued notes from queue/vocab.json and queue/grammar.json into Anki, then refresh existing_index.json."""
    existing_models = set(request("modelNames"))
    for model, mpath in MODEL_FILES.items():
        if model not in existing_models and os.path.exists(mpath):
            request("createModel", **load_json_file(mpath, {}))
            print(f"created missing model {model!r}")

    targets = [
        ("Vocab Cloze", "English::Vocab", QUEUE_FILES["Vocab Cloze"]),
        ("Grammar Practice", "English::Grammar", QUEUE_FILES["Grammar Practice"]),
    ]
    for model, parent, qpath in targets:
        rel_q = os.path.relpath(qpath, REPO_ROOT)
        items = load_json_file(qpath, [])
        if not items:
            print(f"{rel_q}: 0 pending")
            continue
        request("createDeck", deck=parent)
        cache = {}
        validated = []
        for i, it in enumerate(items):
            fields = it.get("fields") or {}
            err = validate_fields(model, fields, cache)
            if err:
                die(f"{rel_q} note {i}: {err}")
            validated.append({
                "deckName": None,
                "modelName": model,
                "fields": fields,
                "tags": it.get("tags") or (["vocab"] if model == "Vocab Cloze" else ["grammar"]),
            })
        add_items_online(
            validated,
            batch_mode=True,
            batch_parent=parent,
            batch_size=args.batch_size,
            allow_duplicate=False,
            partial=True,
        )
        save_json_file(qpath, [])
        num, count = batch_state(parent, args.batch_size)
        print(f"cleared {rel_q} -> {batch_deck_name(parent, num)} ({count}/{args.batch_size})")

    idx = refresh_existing_index()
    print(f"synced queue/existing_index.json ({len(idx.get('Vocab Cloze', []))} vocab, {len(idx.get('Grammar Practice', []))} grammar)")


def cmd_update(args):
    fields = parse_fields(args.field)
    if fields:
        request("updateNoteFields", note={"id": args.id, "fields": fields})
        print(f"updated fields {list(fields)} on note {args.id}")
    if args.add_tags:
        request("addTags", notes=[args.id], tags=" ".join(parse_tags(args.add_tags)))
        print(f"added tags {parse_tags(args.add_tags)} to note {args.id}")
    if args.remove_tags:
        request("removeTags", notes=[args.id], tags=" ".join(parse_tags(args.remove_tags)))
        print(f"removed tags {parse_tags(args.remove_tags)} from note {args.id}")
    if not (fields or args.add_tags or args.remove_tags):
        die("nothing to do: give --field, --add-tags, or --remove-tags")


def cmd_reset(args):
    cards = request("findCards", query=f'deck:"{args.deck}"')
    if not cards:
        print(f"0 cards in {args.deck!r}")
        return
    request("forgetCards", cards=cards)
    print(f"reset {len(cards)} cards in {args.deck!r}")


def cmd_raw(args):
    try:
        params = json.loads(args.params) if args.params else {}
    except json.JSONDecodeError as e:
        die(f"params is not valid JSON: {e}")
    json.dump(request(args.action, **params), sys.stdout, ensure_ascii=False, indent=2)
    print()


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("decks", help="list deck names").set_defaults(fn=cmd_decks)
    sub.add_parser("models", help="list note types").set_defaults(fn=cmd_models)
    s = sub.add_parser("fields", help="list field names of a note type")
    s.add_argument("--model", required=True)
    s.set_defaults(fn=cmd_fields)

    s = sub.add_parser("list", help="find notes (Anki search syntax; falls back to queue/ when offline)")
    s.add_argument("--deck")
    s.add_argument("--tag")
    s.add_argument("--added", type=int, metavar="DAYS", help="added in the last N days")
    s.add_argument("--rated", type=int, metavar="DAYS", help="reviewed in the last N days")
    s.add_argument("--due", action="store_true")
    s.add_argument("--new", action="store_true")
    s.add_argument("--query", help="raw Anki search; overrides the other filters")
    s.add_argument("--limit", type=int, default=20)
    s.add_argument("--json", action="store_true", help="machine-readable output")
    s.set_defaults(fn=cmd_list)

    s = sub.add_parser("batch", help="show the vocab batch deck the next note would go to (or queue status if offline)")
    s.add_argument("--batch-parent", default="English::Vocab")
    s.add_argument("--batch-size", type=int, default=200)
    s.set_defaults(fn=cmd_batch)

    s = sub.add_parser("add", help="add one note (--field) or many (--json); auto-queues to queue/ when offline")
    s.add_argument("--deck", help="target deck (default for --json items without 'deck')")
    s.add_argument("--batch", action="store_true",
                   help="put notes into the current batch deck (parent::NNN, max --batch-size notes each)")
    s.add_argument("--batch-parent", default="English::Vocab")
    s.add_argument("--batch-size", type=int, default=200)
    s.add_argument("--model", default="Basic", help="note type (default: Basic)")
    s.add_argument("--field", action="append", metavar="NAME=VALUE")
    s.add_argument("--tags", default="", help="comma-separated")
    s.add_argument("--json", metavar="FILE", help="list of {deck?, model?, fields, tags?}; '-' for stdin")
    s.add_argument("--allow-duplicate", action="store_true")
    s.add_argument("--partial", action="store_true", help="add the notes that pass even if some are rejected")
    s.add_argument("--queue", action="store_true", help="force writing to queue/*.json even if Anki is open")
    s.set_defaults(fn=cmd_add)

    s = sub.add_parser("flush", help="import queued cards from queue/*.json into Anki and sync existing_index.json")
    s.add_argument("--batch-size", type=int, default=200)
    s.set_defaults(fn=cmd_flush)

    s = sub.add_parser("update", help="change fields or tags of an existing note")
    s.add_argument("--id", type=int, required=True)
    s.add_argument("--field", action="append", metavar="NAME=VALUE")
    s.add_argument("--add-tags", default="", help="comma-separated")
    s.add_argument("--remove-tags", default="", help="comma-separated")
    s.set_defaults(fn=cmd_update)

    s = sub.add_parser("reset", help="forget all cards in a deck so they become New again")
    s.add_argument("--deck", required=True, help="deck name (includes sub-decks)")
    s.set_defaults(fn=cmd_reset)

    s = sub.add_parser("raw", help="call any AnkiConnect action")
    s.add_argument("action")
    s.add_argument("params", nargs="?", help="JSON object")
    s.set_defaults(fn=cmd_raw)

    args = p.parse_args()
    try:
        args.fn(args)
    except AnkiUnreachable as e:
        die(str(e), 1)
    except AnkiError as e:
        die(f"AnkiConnect error: {e}", 2)


if __name__ == "__main__":
    main()
