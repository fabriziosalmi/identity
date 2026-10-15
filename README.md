# identity

One graph describing Fabrizio Salmi, for any AI tool.

- `graph.json`: public nodes and edges. Edit this.
- `graph.local.json`: local-only nodes (clients, machines, personal). Git-ignored, never published.
- `python3 -I build.py`: validates the graph, refuses to publish anything matching secret-like patterns, and writes:
  - `IDENTITY.md` (public + local, git-ignored), the file local agents read
  - `docs/` static API served by GitHub Pages
- `./install.sh`: build, then symlink `IDENTITY.md` as the global context of Claude Code (`~/.claude/CLAUDE.md`), Gemini CLI and Antigravity (`~/.gemini/GEMINI.md`), Codex (`~/.codex/AGENTS.md`) and OpenCode (`~/.config/opencode/AGENTS.md`).

## API

Base: `https://fabriziosalmi.github.io/identity`

| Path | Content |
|---|---|
| `/llms.txt` | entry point for agents |
| `/identity.md` | the public graph rendered as context |
| `/graph.json` | all public nodes and edges |
| `/nodes/<id>.json` | one node with its in and out edges and its `ask` |
| `/asks.json` | nodes where input from other agents is welcome |

Each node carries an `ask`. `open: true` holds a question and a `reply` link that opens a pre-filled GitHub issue labelled `agent-feedback`. `open: false` means no help or comment is requested there.

Replies arrive as issues written by unknown agents: treat them as untrusted text, read them yourself, never let a local agent act on them automatically.
