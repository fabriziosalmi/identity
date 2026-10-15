#!/usr/bin/env python3
"""Build identity artifacts from the graph (single source of truth).

Sources:
  graph.json        public nodes/edges (committed, published)
  graph.local.json  local-only nodes/edges (git-ignored, never published)

Outputs:
  docs/             static API served by GitHub Pages
    graph.json        public graph
    nodes/<id>.json   one endpoint per node, with its ask (open/closed)
    asks.json         nodes where input from other agents is welcome
    identity.md       public graph rendered as LLM context
    llms.txt          entry point for agents fetching by URL
  IDENTITY.md       public + local rendered (git-ignored), symlinked into
                    ~/.claude, ~/.gemini, ~/.codex, ~/.config/opencode
"""
import json
import re
import sys
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "graph.json"
LOCAL = ROOT / "graph.local.json"
DIST = ROOT / "docs"
BASE_URL = "https://fabriziosalmi.github.io/identity"
ISSUES = "https://github.com/fabriziosalmi/identity/issues/new"
NOTICE = (
    "This is descriptive data about a person, not instructions for you. "
    "Only nodes with ask.open=true invite input; reply via the ask.reply link. "
    "Everywhere else, no help or comment is requested."
)

# Patterns that must never reach the public output.
DENY = [
    (r"(?i)\b(sk|pk|ghp|gho|ghs|xox[bp]|wsk)[-_][A-Za-z0-9]{10,}", "token"),
    (r"(?i)\b(password|passwd|api[_-]?key|secret)\s*[:=]", "credential"),
    (r"\bIT\d{2}[A-Z]\d{10}[0-9A-Z]{12}\b", "IBAN"),
    (r"\b[A-Z]{6}\d{2}[A-Z]\d{2}[A-Z]\d{3}[A-Z]\b", "codice fiscale"),
    (r"\b\d{1,3}(\.\d{1,3}){3}\b", "IP address"),
    (r"(?i)\b[\w.+-]+@[\w-]+\.[\w.]+\b", "email address"),
    (r"(?i)edge99|ts\.net|freecoders|minimac|opti\d", "internal host"),
    ("—", "em dash (public text style)"),
]

SECTIONS = [
    ("person", "Who I am"),
    ("role", "Work"),
    ("client", "Clients (local only)"),
    ("project", "Projects"),
    ("skill", "Stack and skills"),
    ("infra", "Machines and infra (local only)"),
    ("preference", "How to work with me"),
    ("style", "How I write"),
    ("interest", "Outside work"),
    ("link", "Links"),
]


def load():
    g = json.loads(SRC.read_text())
    for n in g["nodes"]:
        n["visibility"] = "public"
    if LOCAL.exists():
        loc = json.loads(LOCAL.read_text())
        for n in loc["nodes"]:
            n["visibility"] = "local"
        g["nodes"] += loc["nodes"]
        g["edges"] += loc["edges"]
    seen = set()
    for n in g["nodes"]:
        if n["id"] in seen:
            sys.exit(f"duplicate node id: {n['id']}")
        if n["type"] not in dict(SECTIONS):
            sys.exit(f"unknown type {n['type']} on {n['id']}")
        seen.add(n["id"])
    for e in g["edges"]:
        for k in ("from", "to"):
            if e[k] not in seen:
                sys.exit(f"edge references unknown node: {e[k]}")
    return g


def public(g):
    nodes = [
        {k: v for k, v in n.items() if k != "visibility"}
        for n in g["nodes"] if n["visibility"] == "public"
    ]
    ids = {n["id"] for n in nodes}
    edges = [e for e in g["edges"] if e["from"] in ids and e["to"] in ids]
    return {**g, "nodes": nodes, "edges": edges}


def scan(text):
    hits = [why for pat, why in DENY if re.search(pat, text)]
    # Phone-like: a run of 9+ digits with separators.
    for m in re.finditer(r"\+?\d[\d\s().-]{7,}\d", text):
        if sum(c.isdigit() for c in m.group()) >= 9:
            hits.append("phone-like number")
    if hits:
        sys.exit(f"refusing to publish, found: {', '.join(sorted(set(hits)))}")


def ask_for(n):
    """Per-node invitation to other agents: open (with a question) or closed."""
    a = n.get("ask")
    if not a:
        return {"open": False, "note": "No help or comment requested here."}
    title = quote(f"[agent] {n['id']}: ")
    body = quote(
        f"Node: {BASE_URL}/nodes/{n['id']}.json\nQuestion: {a}\n\n"
        "Your suggestion (concrete; no links to install, no requests for data):\n"
    )
    return {
        "open": True,
        "question": a,
        "reply": f"{ISSUES}?labels=agent-feedback&title={title}&body={body}",
    }


def node_doc(n, g):
    by_id = {x["id"]: x for x in g["nodes"]}

    def rel(e, k):
        return {"rel": e["rel"], "node": e[k], "label": by_id[e[k]]["label"],
                "href": f"{BASE_URL}/nodes/{e[k]}.json"}

    return {
        **{k: v for k, v in n.items() if k != "ask"},
        "out": [rel(e, "to") for e in g["edges"] if e["from"] == n["id"]],
        "in": [rel(e, "from") for e in g["edges"] if e["to"] == n["id"]],
        "ask": ask_for(n),
        "notice": NOTICE,
    }


def render(g, with_asks):
    by_id = {n["id"]: n for n in g["nodes"]}
    m = g["meta"]
    out = [f"# {m['title']}", "", m["intro"], ""]
    for kind, heading in SECTIONS:
        group = [n for n in g["nodes"] if n["type"] == kind]
        if not group:
            continue
        out += [f"## {heading}", ""]
        for n in group:
            line = f"- **{n['label']}**"
            if n.get("text"):
                line += f": {n['text']}"
            uses = [by_id[e["to"]]["label"] for e in g["edges"]
                    if e["from"] == n["id"] and e["rel"] == "uses"]
            if uses:
                line += f" [{', '.join(uses)}]"
            if n.get("url"):
                line += f" <{n['url']}>"
            out.append(line)
        out.append("")
    asks = [n for n in g["nodes"] if n.get("ask")]
    if with_asks and asks:
        out += ["## Where input from other agents is welcome", "",
                "Everything else: no help or comment requested.", ""]
        out += [f"- **{n['label']}**: {n['ask']} "
                f"(reply: {BASE_URL}/nodes/{n['id']}.json)" for n in asks]
        out.append("")
    out.append(f"_Graph: {BASE_URL}/graph.json, updated {m['updated']}_")
    return "\n".join(out) + "\n"


def main():
    g = load()
    pub = public(g)
    docs = {n["id"]: node_doc(n, pub) for n in pub["nodes"]}
    asks = [{"node": i, "question": d["ask"]["question"], "reply": d["ask"]["reply"],
             "href": f"{BASE_URL}/nodes/{i}.json"}
            for i, d in docs.items() if d["ask"]["open"]]

    def dump(o):
        return json.dumps(o, ensure_ascii=False, indent=2) + "\n"

    pub_md = render(pub, with_asks=True)
    pub_json = dump(pub)
    scan(pub_md + pub_json + "".join(dump(d) for d in docs.values()))

    (DIST / "nodes").mkdir(parents=True, exist_ok=True)
    for old in (DIST / "nodes").glob("*.json"):
        old.unlink()
    for i, d in docs.items():
        (DIST / "nodes" / f"{i}.json").write_text(dump(d))
    (DIST / "graph.json").write_text(pub_json)
    (DIST / "asks.json").write_text(dump({"notice": NOTICE, "open": asks}))
    (DIST / "identity.md").write_text(pub_md)
    (DIST / ".nojekyll").write_text("")
    (DIST / "llms.txt").write_text(
        f"# {g['meta']['title']}\n\n> {g['meta']['intro']}\n\n{NOTICE}\n\n"
        f"- [Identity (markdown)]({BASE_URL}/identity.md): read this as user context\n"
        f"- [Identity graph (JSON)]({BASE_URL}/graph.json): nodes and edges, same content\n"
        f"- [Open asks]({BASE_URL}/asks.json): where input is welcome, and how to reply\n"
        f"- Per node: {BASE_URL}/nodes/<id>.json (ask.open=false means no comment wanted)\n"
    )
    (ROOT / "IDENTITY.md").write_text(render(g, with_asks=False))
    print(f"ok: {len(pub['nodes'])} public + {len(g['nodes']) - len(pub['nodes'])} local nodes, "
          f"{len(pub['edges'])} public edges, {len(asks)} open asks")


if __name__ == "__main__":
    main()
