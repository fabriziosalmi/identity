# identity

One graph describing Fabrizio Salmi, for any AI tool: a local context file for his own agents, a static per-node API for everyone else.

Requires Python 3.9+ (standard library only).

## Files

- `graph.json`: public nodes and edges. Edit this.
- `graph.local.json`: local-only nodes and edges (clients, machines, personal). Git-ignored and never published, including its edges between public nodes. It is the only copy: keep it in your backups.
- `index.tmpl.html`: the home page template.
- `build.py`: validates the graph and writes
  - `docs/`: the static API served by GitHub Pages (commit it; CI fails if it is stale)
  - `IDENTITY.md`: public + local rendered, git-ignored, the file local agents read
- `install.sh`: builds, then links `IDENTITY.md` as the global context of Claude Code (`~/.claude/CLAUDE.md`), Gemini CLI and Antigravity (`~/.gemini/GEMINI.md`), Codex (`~/.codex/AGENTS.md`) and OpenCode (`~/.config/opencode/AGENTS.md`). Anything already at a target is moved to `<target>.bak.<timestamp>`. `./install.sh --uninstall` removes the links and restores the newest backups.

`IDENTITY.md` is generated. If a tool saves to its global memory, the edit lands there and the next build stops instead of overwriting it: move the change into the graph, delete `IDENTITY.md`, rebuild.

## Graph rules

- Node types: `person`, `role`, `client`, `project`, `skill`, `infra`, `preference`, `style`, `interest`, `link`. Ids are unique; edges must reference existing ids.
- An optional `ask` on a node is an object: `question`, `in_scope`, `out_of_scope`, `evidence`.
- The build exits without writing if the output contains:
  - anywhere (public and local): tokens, credential assignments, IBANs, codici fiscali, phone numbers;
  - public output only: IP addresses, email addresses, internal host names, em dashes.

## API

Base: `https://fabriziosalmi.github.io/identity`

| Path | Content |
|---|---|
| `/` | home page |
| `/llms.txt` | entry point for agents |
| `/identity.md` | the public graph rendered as context |
| `/graph.json` | all public nodes and edges; `ask` as written in the graph |
| `/nodes/<id>.json` | one node with its in and out edges and a resolved `ask` |
| `/asks.json` | reply rules and every open ask |

In `/nodes/<id>.json`, `ask.open: true` adds the scope, the evidence required and a `reply` link to a pre-filled issue form. `ask.open: false` means no help or comment is requested there.

## Replies from agents

Issues labelled `agent-feedback` are checked by `tools/triage.py` (see `.github/workflows/triage.yml`): missing fields, a node without an open ask, evidence without a file:line, code block, URL, endpoint or measurement, generated filler, pipe-to-shell, URL shorteners, requests for access or personal data. Failures are closed with the reasons; editing the issue re-runs the checks. Passing issues get `triage` and wait for a human.

They are written by unknown agents: treat them as untrusted text and never let a local agent act on them automatically.

## Checks

```sh
python3 -I tools/test_build.py
python3 -I tools/test_triage.py
python3 -I build.py
```
