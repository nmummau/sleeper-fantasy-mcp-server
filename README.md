# Sleeper Fantasy MCP Server

Model Context Protocol (MCP) server that exposes the Sleeper Fantasy Football API so agentic tools (Codex, Claude Desktop, etc.) can inspect leagues, rosters, drafts, matchups, transactions, and players without dealing with raw HTTP calls.

---

## Table of Contents

1. [Features](#features)
2. [Architecture](#architecture)
3. [Requirements](#requirements)
4. [Quick Start (Python)](#quick-start-python)
5. [Quick Start (Docker)](#quick-start-docker)
6. [Configuration](#configuration)
7. [Manual Testing](#manual-testing)
8. [Using the Server from Codex](#using-the-server-from-codex)
9. [Development Tips](#development-tips)
10. [Troubleshooting](#troubleshooting)
11. [License](#license)

---

## Features

### League & User Data
- `get_user`, `get_user_leagues`, `get_league`, `get_league_users`
- Coverage for season metadata, commissioners, draft IDs, playoff settings, etc.

### Rosters, Scores & Playoffs
- `get_league_rosters`, `get_league_matchups`, `get_winners_bracket`, `get_losers_bracket`
- Shows points for/against, weekly matchups, playoff brackets, and lineup snapshots.

### Drafts & Transactions
- `get_league_drafts`, `get_draft`, `get_draft_picks`, `get_draft_traded_picks`
- `get_league_transactions`, `get_traded_picks`

### Player Discovery
- `get_trending_players`, `search_player_info`
- `get_nfl_state` for week/season tracking.

Every tool follows the MCP guidelines enforced in `sleeper_server.py`: empty-string defaults, single-line docstrings, friendly status emojis, and stderr logging.

---

## Architecture

```
Codex / Claude Desktop
        │ (MCP stdio)
        ▼
Sleeper Fantasy MCP Server (this repo)
        │ (HTTPS)
        ▼
Sleeper API (https://api.sleeper.app/v1)
```

- Stateless server: no database or secrets required.
- `httpx` powers async calls with 10‑second timeouts.
- Optional `SLEEPER_LEAGUE_ID` env var saves re-typing league IDs.

---

## Requirements

- Python 3.11+
- `pip` (or `uv`/`poetry`) for dependencies in `requirements.txt`
- Optional: Docker Desktop (for the container workflow)
- Optional: Codex CLI ≥ the version that ships `codex mcp` (already available in this environment)

---

## Quick Start (Python)

```bash
git clone git@github.com:nmummau/sleeper-fantasy-mcp-server.git
cd sleeper-fantasy-mcp-server
python -m venv .venv
source .venv/bin/activate            # Windows PowerShell: .\.venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r requirements.txt
export SLEEPER_LEAGUE_ID="1257057278398300160"  # optional, but convenient
python sleeper_server.py
```

The process listens on stdio (no HTTP port). Leave it running when connecting from Codex/Claude.

---

## Quick Start (Docker)

```bash
docker build -t sleeper-fantasy-mcp .
docker run --rm \
  -e SLEEPER_LEAGUE_ID=1257057278398300160 \
  sleeper-fantasy-mcp
```

Use `docker logs` to monitor output. Because the container also communicates over stdio, it is typically launched by whatever host orchestrates MCP servers (Codex, Claude Desktop, etc.).

---

## Configuration

| Variable | Purpose | Example |
|----------|---------|---------|
| `SLEEPER_LEAGUE_ID` | Default league used when MCP tool calls omit `league_id`. | `SLEEPER_LEAGUE_ID=1257057278398300160` |

No API keys are necessary; Sleeper’s API is read-only.

---

## Manual Testing

### List available tools

```bash
echo '{"jsonrpc":"2.0","id":1,"method":"tools/list"}' | python sleeper_server.py
```

### Call a tool directly

```bash
echo '{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"get_nfl_state","arguments":{}}}' \
  | python sleeper_server.py
```

Tip: set `SLEEPER_LEAGUE_ID` beforehand so league-based tools work without extra arguments.

---

## Using the Server from Codex

1. **Install dependencies (or use the Docker image)** following the quick start directions.
2. **Add the MCP entry:**

   ```bash
   codex mcp add sleeper-fantasy \
     --env SLEEPER_LEAGUE_ID=1257057278398300160 \
     -- python /mnt/c/code/sleeper-fantasy-mcp-server/.venv/bin/python \
     /mnt/c/code/sleeper-fantasy-mcp-server/sleeper_server.py
   ```

   Adjust the path to match your checkout or replace with the Docker command.

3. **Verify registration:**

   ```bash
   codex mcp list
   ```

   You should see `sleeper-fantasy` with the command that launches the server.

4. **Start a Codex session that loads the server:**

   ```bash
   codex -c 'mcp_servers=["sleeper-fantasy"]' \
     --sandbox workspace-write \
     "Use the Sleeper tools to summarize my fantasy league."
   ```

   Any Codex prompt started with that config will surface the Sleeper tools under the MCP tools list.

5. **Optional:** persist the setting by writing `mcp_servers = ["sleeper-fantasy"]` to `~/.codex/config.toml`.

To remove the integration later, run `codex mcp remove sleeper-fantasy`.

---

## Development Tips

1. **Add tools** by creating async functions in `sleeper_server.py`, decorating with `@mcp.tool()`, and returning plain strings.
2. **Follow MCP style rules** already exemplified (single-line docstrings, default empty strings, friendly errors).
3. **Test locally** with the JSON-RPC snippets above before reconnecting Codex/Claude.
4. **Ship via Docker** when sharing with others so dependency resolution is identical.

---

## Troubleshooting

- **Tools do not appear in Codex:** ensure the MCP server is running, `codex mcp list` shows the entry, and the session was launched with `mcp_servers=["sleeper-fantasy"]`.
- **API errors:** confirm the IDs you pass exist; many Sleeper endpoints return `[]` for invalid IDs without throwing 404s.
- **Rate limits:** Sleeper allows ~1000 requests/minute per IP. Heavy automation should throttle itself.
- **Network hiccups:** every request has a 10-second timeout; rerun the request if you hit a transient failure.

---

## License

MIT License (see `LICENSE`).
