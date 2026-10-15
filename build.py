#!/usr/bin/env python3
"""Build identity artifacts from the graph (single source of truth).

Sources:
  graph.json        public nodes/edges (committed, published)
  graph.local.json  local-only nodes/edges (git-ignored, never published)

Outputs:
  docs/             static API served by GitHub Pages
    graph.json        public graph
    nodes/<id>.json   one endpoint per node, with its ask (open/closed)
    asks.json         reply rules and nodes where input is welcome
    identity.md       public graph rendered as LLM context
    llms.txt          entry point for agents fetching by URL
    index.html        home page
  IDENTITY.md       public + local rendered (git-ignored), symlinked into
                    ~/.claude, ~/.gemini, ~/.codex, ~/.config/opencode

Every output is computed and scanned before the first write, and every file
is replaced atomically.
"""
import hashlib
import json
import os
import re
import sys
from pathlib import Path
from string import Template
from urllib.parse import quote

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "graph.json"
LOCAL = ROOT / "graph.local.json"
DIST = ROOT / "docs"
IDENTITY = ROOT / "IDENTITY.md"
SCHEMA_VERSION = 1
BASE_URL = "https://fabriziosalmi.github.io/identity"
ISSUES = "https://github.com/fabriziosalmi/identity/issues/new"
NOTICE = (
    "This is descriptive data about a person, not instructions for you. "
    "Only nodes with ask.open=true invite input; reply via the ask.reply link, "
    "following asks.json rules. Everywhere else, no help or comment is requested."
)
# Published rules. tools/triage.py enforces the mechanical ones (fields, open
# node, lengths, evidence shape, filler, forbidden patterns); scope and
# "one proposal" are judged by a human.
RULES = [
    "One proposal per issue, about one node with an open ask.",
    "Stay inside in_scope; anything in out_of_scope is closed.",
    "Evidence is mandatory: file:line, raw request, API endpoint, sample with license, or a measurement.",
    "Say how you verified it, and which agent and model wrote it.",
    "Proposal 80 to 4000 characters; whole issue at most 12000.",
    "No promotion, no install-this links, no URL shorteners, no requests for access, keys or personal data.",
    "Replies failing these checks are closed automatically; editing the issue re-runs the checks.",
]

# Patterns that must never reach an output. PUBLIC_ONLY ones are allowed in
# the local file, which never leaves this machine except as AI context.
DENY = [
    (r"(?i)\b(sk|pk|ghp|gho|ghs|ghu|ghr|xox[bpas]|wsk|glpat)[-_][A-Za-z0-9_-]{10,}", "token"),
    (r"\bgithub_pat_[A-Za-z0-9_]{20,}", "token"),
    (r"\b(AKIA|ASIA)[0-9A-Z]{16}\b", "token"),
    (r"\bAIza[0-9A-Za-z_-]{30,}", "token"),
    (r"-----BEGIN [A-Z ]*PRIVATE KEY-----", "private key"),
    (r"(?i)\b(password|passwd|api[_-]?key|secret)\s*[:=]", "credential"),
    (r"\bIT\d{2}[A-Z]\d{10}[0-9A-Z]{12}\b", "IBAN"),
    (r"\b[A-Z]{6}\d{2}[A-Z]\d{2}[A-Z]\d{3}[A-Z]\b", "codice fiscale"),
    (r"\b\d{1,3}(\.\d{1,3}){3}\b", "IP address"),
    (r"(?i)\b[\w.+-]+@[\w-]+\.[\w.]+\b", "email address"),
    (r"(?i)edge99|ts\.net|freecoders|minimac|opti\d", "internal host"),
    ("—", "em dash (public text style)"),
]
PUBLIC_ONLY = {"IP address", "email address", "internal host", "em dash (public text style)"}
ID_RE = re.compile(r"^[a-z0-9][a-z0-9-]{0,62}$")
TRAILER = re.compile(r"\n<!-- identity-build sha256:([0-9a-f]{64}) -->\n\Z")

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


class BuildError(Exception):
    pass


def load(src=SRC, local=LOCAL):
    g = json.loads(Path(src).read_text())
    for n in g["nodes"]:
        n["visibility"] = "public"
    if Path(local).exists():
        loc = json.loads(Path(local).read_text())
        for n in loc["nodes"]:
            n["visibility"] = "local"
        # Local edges stay local even between two public nodes.
        for e in loc["edges"]:
            e["local"] = True
        g["nodes"] += loc["nodes"]
        g["edges"] += loc["edges"]
    seen = set()
    for n in g["nodes"]:
        if not ID_RE.match(n["id"]):
            raise BuildError(f"node id must match {ID_RE.pattern}: {n['id']!r}")
        if n["id"] in seen:
            raise BuildError(f"duplicate node id: {n['id']}")
        if n["type"] not in dict(SECTIONS):
            raise BuildError(f"unknown type {n['type']} on {n['id']}")
        seen.add(n["id"])
    for e in g["edges"]:
        for k in ("from", "to"):
            if e[k] not in seen:
                raise BuildError(f"edge references unknown node: {e[k]}")
    return g


def public(g):
    nodes = [
        {k: v for k, v in n.items() if k != "visibility"}
        for n in g["nodes"] if n["visibility"] == "public"
    ]
    ids = {n["id"] for n in nodes}
    edges = [e for e in g["edges"]
             if not e.get("local") and e["from"] in ids and e["to"] in ids]
    meta = {**g["meta"], "schema_version": SCHEMA_VERSION}
    return {**g, "meta": meta, "nodes": nodes, "edges": edges}


def scan(text, public=True):
    """Raise on anything secret-like. The local file goes to every AI provider
    the linked tools use, so it gets the secret checks too; the rules that
    only protect the public output (hosts, addresses, style) are skipped.
    The error names categories, never the matched text."""
    deny = DENY if public else [(p, w) for p, w in DENY if w not in PUBLIC_ONLY]
    hits = [why for pat, why in deny if re.search(pat, text)]
    # Phone-like: a run of 9+ digits with separators.
    for m in re.finditer(r"\+?\d[\d\s().-]{7,}\d", text):
        if sum(c.isdigit() for c in m.group()) >= 9:
            hits.append("phone-like number")
    if hits:
        where = "public output" if public else "IDENTITY.md"
        raise BuildError(f"refusing to write {where}, found: {', '.join(sorted(set(hits)))}")


def node_url(node_id):
    return f"{BASE_URL}/nodes/{node_id}.json"


def ask_for(n):
    """Per-node invitation to other agents: open (with a question) or closed."""
    a = n.get("ask")
    if not a:
        return {"open": False, "note": "No help or comment requested here."}
    title = quote(f"[agent] {n['id']}: ")
    return {
        "open": True,
        **a,
        "reply": f"{ISSUES}?template=agent-feedback.yml&title={title}&node={n['id']}",
    }


def node_doc(n, g):
    by_id = {x["id"]: x for x in g["nodes"]}

    def rel(e, k):
        return {"rel": e["rel"], "node": e[k], "label": by_id[e[k]]["label"],
                "href": node_url(e[k])}

    return {
        "schema_version": SCHEMA_VERSION,
        **{k: v for k, v in n.items() if k != "ask"},
        "out": [rel(e, "to") for e in g["edges"] if e["from"] == n["id"]],
        "in": [rel(e, "from") for e in g["edges"] if e["to"] == n["id"]],
        "ask": ask_for(n),
        "notice": NOTICE,
    }


def render_node(n, by_id, edges):
    line = f"- **{n['label']}**"
    if n.get("text"):
        line += f": {n['text']}"
    uses = [by_id[e["to"]]["label"] for e in edges if e["from"] == n["id"] and e["rel"] == "uses"]
    if uses:
        line += f" [{', '.join(uses)}]"
    if n.get("url"):
        line += f" <{n['url']}>"
    return line


def render_asks(nodes):
    out = ["## Where input from other agents is welcome", "",
           "Everything else: no help or comment requested.", ""]
    for n in nodes:
        a = n["ask"]
        out += [f"- **{n['label']}**: {a['question']}",
                f"  - In scope: {a['in_scope']}",
                f"  - Out of scope: {a['out_of_scope']}",
                f"  - Evidence: {a['evidence']}",
                f"  - Details and reply link: {node_url(n['id'])}"]
    out += ["", "Rules for replies:", ""] + [f"{i}. {r}" for i, r in enumerate(RULES, 1)]
    return out + [""]


def render(g, with_asks):
    by_id = {n["id"]: n for n in g["nodes"]}
    m = g["meta"]
    out = [f"# {m['title']}", "", m["intro"], ""]
    for kind, heading in SECTIONS:
        group = [n for n in g["nodes"] if n["type"] == kind]
        if group:
            out += [f"## {heading}", ""]
            out += [render_node(n, by_id, g["edges"]) for n in group] + [""]
    asks = [n for n in g["nodes"] if n.get("ask")]
    if with_asks and asks:
        out += render_asks(asks)
    out.append(f"_Graph: {BASE_URL}/graph.json, updated {m['updated']}_")
    return "\n".join(out) + "\n"


def sign(text):
    return f"{text}\n<!-- identity-build sha256:{hashlib.sha256(text.encode()).hexdigest()} -->\n"


def check_untouched(path=IDENTITY):
    """IDENTITY.md is linked as each tool's global memory, so a tool may write
    to it. A build never silently overwrites such an edit: the file carries the
    hash of what the last build wrote."""
    path = Path(path)
    if not path.exists():
        return
    current = path.read_text()
    m = TRAILER.search(current)
    body = current[:m.start()] if m else None
    if not m or hashlib.sha256(body.encode()).hexdigest() != m.group(1):
        raise BuildError(f"{path.name} was edited after the last build (by you or an AI "
                         "tool saving to its global memory). Move the change into "
                         f"graph.json or graph.local.json, delete {path.name}, then rebuild.")


def write_atomic(path, text):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f".{path.name}.tmp")
    tmp.write_text(text)
    os.replace(tmp, path)


def dump(o):
    return json.dumps(o, ensure_ascii=False, indent=2) + "\n"


def outputs(g):
    """Return ({docs-relative path: text}, local markdown, open-ask count)."""
    pub = public(g)
    docs = {n["id"]: node_doc(n, pub) for n in pub["nodes"]}
    asks = [{"node": i, "href": node_url(i),
             **{k: v for k, v in d["ask"].items() if k != "open"}}
            for i, d in docs.items() if d["ask"]["open"]]
    meta = g["meta"]
    files = {f"nodes/{i}.json": dump(d) for i, d in docs.items()}
    files.update({
        "graph.json": dump(pub),
        "asks.json": dump({"schema_version": SCHEMA_VERSION, "notice": NOTICE,
                           "rules": RULES, "open": asks}),
        "identity.md": render(pub, with_asks=True),
        "index.html": Template((ROOT / "index.tmpl.html").read_text()).substitute(
            asks=len(asks), updated=meta["updated"]),
        ".nojekyll": "",
        "llms.txt": (
            f"# {meta['title']}\n\n> {meta['intro']}\n\n{NOTICE}\n\n"
            f"- [Identity (markdown)]({BASE_URL}/identity.md): read this as user context\n"
            f"- [Identity graph (JSON)]({BASE_URL}/graph.json): nodes and edges, same content\n"
            f"- [Open asks]({BASE_URL}/asks.json): where input is welcome, and how to reply\n"
            f"- Per node: {node_url('<id>')} (ask.open=false means no comment wanted)\n"
        ),
    })
    return files, render(g, with_asks=False), len(asks)


def main():
    g = load(SRC, LOCAL)
    files, local_md, n_asks = outputs(g)
    # Every check runs before the first write.
    scan("".join(files.values()))
    scan(local_md, public=False)
    check_untouched(IDENTITY)

    for rel, text in files.items():
        write_atomic(DIST / rel, text)
    for old in (DIST / "nodes").glob("*.json"):
        if f"nodes/{old.name}" not in files:
            old.unlink()
    write_atomic(IDENTITY, sign(local_md))
    n_pub = sum(1 for n in g["nodes"] if n["visibility"] == "public")
    print(f"ok: {n_pub} public + {len(g['nodes']) - n_pub} local nodes, {n_asks} open asks")


if __name__ == "__main__":
    try:
        main()
    except BuildError as e:
        sys.exit(str(e))
