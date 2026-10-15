#!/usr/bin/env python3
"""Tests for the privacy guards in build.py. Run: python3 -I tools/test_build.py"""
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("build", REPO / "build.py")
build = importlib.util.module_from_spec(spec)
spec.loader.exec_module(build)


def blocked(text, public=True):
    try:
        build.scan(text, public=public)
    except build.BuildError:
        return True
    return False


GRAPH = {
    "meta": {"title": "T", "intro": "I", "updated": "2026-01-01"},
    "nodes": [
        {"id": "a", "type": "person", "label": "A"},
        {"id": "b", "type": "project", "label": "B",
         "ask": {"question": "Q?", "in_scope": "x", "out_of_scope": "y", "evidence": "z"}},
    ],
    "edges": [{"from": "a", "rel": "maintains", "to": "b"}],
}
LOCAL = {
    "nodes": [{"id": "c", "type": "client", "label": "C", "text": "client detail"}],
    "edges": [{"from": "a", "rel": "serves", "to": "c"},
              {"from": "a", "rel": "private_link", "to": "b"}],
}


class Sandbox(unittest.TestCase):
    """A throwaway copy of the build paths, so main() can run end to end."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        d = Path(self.tmp.name)
        self.saved = {k: getattr(build, k) for k in ("ROOT", "SRC", "LOCAL", "DIST", "IDENTITY")}
        build.SRC, build.LOCAL = d / "graph.json", d / "graph.local.json"
        build.DIST, build.IDENTITY = d / "docs", d / "IDENTITY.md"
        build.SRC.write_text(json.dumps(GRAPH))
        build.LOCAL.write_text(json.dumps(LOCAL))

    def tearDown(self):
        for k, v in self.saved.items():
            setattr(build, k, v)
        self.tmp.cleanup()

    def run_main(self):
        build.main()
        return {p.relative_to(build.DIST).as_posix(): p.read_text()
                for p in build.DIST.rglob("*") if p.is_file()}


class Scan(unittest.TestCase):
    def test_blocks_secrets_everywhere(self):
        for t in ["token gho_" + "a" * 20, "github_pat_" + "A" * 30, "AKIA" + "B" * 16,
                  "AIza" + "c" * 35, "glpat-" + "d" * 20, "-----BEGIN OPENSSH PRIVATE KEY-----",
                  "api_key: x", "password = y", "IT60X0542811101000000123456",
                  "RSSMRA80A01H501U", "call +39 333 123 4567"]:
            self.assertTrue(blocked(t), t)
            self.assertTrue(blocked(t, public=False), t)

    def test_blocks_public_only_rules_in_public(self):
        for t in ["host 10.0.0.12", "me@example.com", "gitlab.edge99.net", "a — b"]:
            self.assertTrue(blocked(t), t)
            self.assertFalse(blocked(t, public=False), t)

    def test_allows_ordinary_text(self):
        for t in ["Borsa Italiana (2019 to 2025)", "v2.48.6", "1993-1999", "~1.4k stars, 16 GB RAM"]:
            self.assertFalse(blocked(t), t)

    def test_error_names_category_not_value(self):
        with self.assertRaises(build.BuildError) as cm:
            build.scan("password = hunter2")
        self.assertNotIn("hunter2", str(cm.exception))


class Load(unittest.TestCase):
    def test_tags_local_nodes_and_edges(self):
        with tempfile.TemporaryDirectory() as d:
            src, loc = Path(d, "g.json"), Path(d, "l.json")
            src.write_text(json.dumps(GRAPH))
            loc.write_text(json.dumps(LOCAL))
            g = build.load(src, loc)
        p = build.public(g)
        self.assertEqual([n["id"] for n in p["nodes"]], ["a", "b"])
        self.assertEqual([e["rel"] for e in p["edges"]], ["maintains"])
        self.assertTrue(all("visibility" not in n for n in p["nodes"]))
        self.assertEqual(p["meta"]["schema_version"], build.SCHEMA_VERSION)

    def test_rejects_bad_ids_and_dangling_edges(self):
        for bad in [{"id": "Bad Id", "type": "person", "label": "x"},
                    {"id": "../x", "type": "person", "label": "x"}]:
            g = {**GRAPH, "nodes": GRAPH["nodes"] + [bad]}
            with tempfile.TemporaryDirectory() as d:
                Path(d, "g.json").write_text(json.dumps(g))
                with self.assertRaises(build.BuildError):
                    build.load(Path(d, "g.json"), Path(d, "none.json"))
        g = {**GRAPH, "edges": [{"from": "a", "rel": "x", "to": "missing"}]}
        with tempfile.TemporaryDirectory() as d:
            Path(d, "g.json").write_text(json.dumps(g))
            with self.assertRaises(build.BuildError):
                build.load(Path(d, "g.json"), Path(d, "none.json"))


class EndToEnd(Sandbox):
    def test_local_data_never_reaches_docs(self):
        out = self.run_main()
        blob = "".join(out.values())
        self.assertNotIn("client detail", blob)
        self.assertNotIn("private_link", blob)
        self.assertIn("client detail", build.IDENTITY.read_text())
        self.assertIn("nodes/b.json", out)
        self.assertTrue(json.loads(out["nodes/b.json"])["ask"]["open"])

    def test_secret_in_local_graph_writes_nothing(self):
        bad = {**LOCAL, "nodes": [{**LOCAL["nodes"][0], "text": "api_key: x"}]}
        build.LOCAL.write_text(json.dumps(bad))
        with self.assertRaises(build.BuildError):
            build.main()
        self.assertFalse(build.DIST.exists())
        self.assertFalse(build.IDENTITY.exists())

    def test_tool_edit_to_identity_blocks_rebuild(self):
        self.run_main()
        with build.IDENTITY.open("a") as f:
            f.write("- remembered by a tool\n")
        with self.assertRaises(build.BuildError):
            build.main()
        self.assertIn("remembered by a tool", build.IDENTITY.read_text())

    def test_rebuild_is_idempotent_and_prunes_removed_nodes(self):
        first = self.run_main()
        self.assertEqual(self.run_main(), first)
        g = {**GRAPH, "nodes": GRAPH["nodes"][:1], "edges": []}
        build.SRC.write_text(json.dumps(g))
        build.LOCAL.write_text(json.dumps({**LOCAL, "edges": LOCAL["edges"][:1]}))
        self.assertNotIn("nodes/b.json", self.run_main())


if __name__ == "__main__":
    unittest.main(verbosity=1)
