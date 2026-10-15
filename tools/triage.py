#!/usr/bin/env python3
"""Deterministic triage for agent-feedback issues.

Usage: triage.py <github-event.json> [asks.json]
Prints a JSON decision: {"pass": bool, "reasons": [...]}.
Never executes or fetches anything from the issue: it only reads text.
"""
import json
import re
import sys
from pathlib import Path

ASKS = Path(__file__).resolve().parent.parent / "docs" / "asks.json"
FIELDS = {
    "node": "Node",
    "proposal": "Proposal",
    "evidence": "Evidence",
    "verified": "How you verified it",
    "agent": "Agent and model",
}
SLOP = [
    r"as an ai( language model)?", r"i hope this helps", r"great question",
    r"\bdelve\b", r"\btapestry\b", r"in today's fast-paced", r"game[- ]changer",
    r"\bseamless(ly)?\b", r"\bleverag(e|ing)\b", r"\brobust\b", r"\bunlock\b",
    r"cutting[- ]edge", r"\bsynerg", r"it is important to note", r"let me know if",
]
HARD_SLOP = SLOP[:3]
EVIDENCE = [
    r"```", r"\b[\w./-]+\.\w+:\d+", r"https?://\S+", r"/api\d?/|/nodes/|/v\d/",
    r"\b\d+(\.\d+)?\s?(ms|s|%|MB|GB|KB|tokens|req/s|rps|x)\b",
]
FORBIDDEN = [
    (r"\b(curl|wget)\b[^\n|]*\|\s*(sudo\s+)?(ba|z)?sh\b", "pipes a download into a shell"),
    (r"https?://(bit\.ly|tinyurl\.com|t\.co|goo\.gl|is\.gd|cutt\.ly|rb\.gy)/", "uses a URL shortener"),
    (r"(?i)\b(give|send|share|provide|grant)\b.{0,20}\b(api key|token|password|credentials|ssh|access|email|phone)\b",
     "asks for access or personal data"),
    (r"(?i)\b(subscribe|sign up|discount|promo code|our (product|platform|service))\b", "promotes something"),
]


def sections(body):
    out, cur = {}, None
    for line in (body or "").splitlines():
        m = re.match(r"^###\s+(.+?)\s*$", line)
        if m:
            cur = m.group(1)
            out[cur] = []
        elif cur:
            out[cur].append(line)
    return {k: "\n".join(v).strip() for k, v in out.items()}


def decide(issue, asks):
    body = issue.get("body") or ""
    s = sections(body)
    reasons = []
    get = lambda f: "" if s.get(FIELDS[f], "") in ("", "_No response_") else s[FIELDS[f]]

    for f, label in FIELDS.items():
        if not get(f):
            reasons.append(f"missing field: {label}")
    open_nodes = {a["node"] for a in asks["open"]}
    node = get("node").strip().strip("`").lower()
    if node and node not in open_nodes:
        reasons.append(f"node '{node}' has no open ask (open: {', '.join(sorted(open_nodes))})")

    proposal, evidence = get("proposal"), get("evidence")
    if proposal and not 80 <= len(proposal) <= 4000:
        reasons.append("proposal must be 80 to 4000 characters")
    if len(body) > 12000:
        reasons.append("issue is longer than 12000 characters")
    if evidence and not any(re.search(p, evidence) for p in EVIDENCE):
        reasons.append("evidence has no file:line, code block, URL, endpoint or measurement")

    text = f"{issue.get('title', '')}\n{body}"
    low = text.lower()
    hits = [p for p in SLOP if re.search(p, low)]
    if any(re.search(p, low) for p in HARD_SLOP) or len(hits) >= 3:
        reasons.append("reads as generic generated text; state the concrete change and its evidence")
    for pat, why in FORBIDDEN:
        if re.search(pat, text):
            reasons.append(f"not allowed: {why}")
    return {"pass": not reasons, "node": node, "reasons": reasons}


def main():
    event = json.loads(Path(sys.argv[1]).read_text())
    asks = json.loads(Path(sys.argv[2] if len(sys.argv) > 2 else ASKS).read_text())
    print(json.dumps(decide(event["issue"], asks)))


if __name__ == "__main__":
    main()
