#!/usr/bin/env python3
"""Tests for the privacy guards in build.py. Run: python3 -I tools/test_build.py"""
import importlib.util
import unittest
from pathlib import Path

spec = importlib.util.spec_from_file_location("build", Path(__file__).resolve().parent.parent / "build.py")
build = importlib.util.module_from_spec(spec)
spec.loader.exec_module(build)


def blocked(text, public=True):
    try:
        build.scan(text, public=public)
    except SystemExit:
        return True
    return False


class Scan(unittest.TestCase):
    def test_blocks_secrets_everywhere(self):
        for t in ["token gho_" + "a" * 20, "api_key: x", "password = y",
                  "IT60X0542811101000000123456", "RSSMRA80A01H501U", "call +39 333 123 4567"]:
            self.assertTrue(blocked(t), t)
            self.assertTrue(blocked(t, public=False), t)

    def test_blocks_public_only_rules_in_public(self):
        for t in ["host 10.0.0.12", "me@example.com", "gitlab.edge99.net", "a — b"]:
            self.assertTrue(blocked(t), t)
            self.assertFalse(blocked(t, public=False), t)

    def test_allows_ordinary_text(self):
        for t in ["Borsa Italiana (2019 to 2025)", "v2.48.6", "1993-1999", "~1.4k stars, 16 GB RAM"]:
            self.assertFalse(blocked(t), t)


class Public(unittest.TestCase):
    def graph(self):
        return {"meta": {}, "nodes": [
            {"id": "a", "type": "person", "label": "A", "visibility": "public"},
            {"id": "b", "type": "project", "label": "B", "visibility": "public"},
            {"id": "c", "type": "client", "label": "C", "visibility": "local"},
        ], "edges": [
            {"from": "a", "rel": "maintains", "to": "b"},
            {"from": "a", "rel": "serves", "to": "c"},
            {"from": "a", "rel": "secret_link", "to": "b", "local": True},
        ]}

    def test_drops_local_nodes_and_their_edges(self):
        p = build.public(self.graph())
        self.assertEqual([n["id"] for n in p["nodes"]], ["a", "b"])
        self.assertNotIn("serves", [e["rel"] for e in p["edges"]])

    def test_local_edge_between_public_nodes_stays_local(self):
        p = build.public(self.graph())
        self.assertEqual([e["rel"] for e in p["edges"]], ["maintains"])

    def test_visibility_field_not_published(self):
        p = build.public(self.graph())
        self.assertTrue(all("visibility" not in n for n in p["nodes"]))


if __name__ == "__main__":
    unittest.main(verbosity=1)
