# Sleeper Fantasy Football MCP Server

A Model Context Protocol (MCP) server that provides comprehensive access to the Sleeper Fantasy Football API for leagues, rosters, matchups, drafts, players, and more.

## Purpose

This MCP server provides a secure interface for AI assistants to access Sleeper Fantasy Football data including league information, rosters, matchups, playoff brackets, transactions, draft data, and player statistics.

## Features

### Current Implementation

- **`get_user`** - Get user information by username or user ID
- **`get_user_leagues`** - Get all leagues for a user in a specific sport and season
- **`get_league`** - Get detailed information about a specific league
- **`get_league_rosters`** - Get all rosters in a league with standings and player information
- **`get_league_users`** - Get all users in a league with their team information
- **`get_league_matchups`** - Get all matchups for a specific week in a league
- **`get_winners_bracket`** - Get the winners playoff bracket for a league
- **`get_losers_bracket`** - Get the losers playoff bracket for a league
- **`get_league_transactions`** - Get all transactions for a specific week including trades, waivers, and free agent pickups
- **`get_traded_picks`** - Get all traded draft picks in a league including future picks
- **`get_nfl_state`** - Get current NFL season state including week, season type, and season dates
- **`get_user_drafts`** - Get all drafts for a user in a specific sport and season
- **`get_league_drafts`** - Get all drafts for a league
- **`get_draft`** - Get detailed information about a specific draft
- **`get_draft_picks`** - Get all picks made in a draft
- **`get_draft_traded_picks`** - Get all traded picks in a draft
- **`get_trending_players`** - Get trending players based on add or drop activity
- **`search_player_info`** - Search for detailed information about a specific player by their player ID

## Prerequisites

- Docker Desktop with MCP Toolkit enabled
- Docker MCP CLI plugin (`docker mcp` command)
- No API authentication required (Sleeper API is read-only and public)

## Installation

See the step-by-step instructions provided with the files.

## Configuration

You can optionally set a default league ID as an environment variable:
- `SLEEPER_LEAGUE_ID` - Your default league ID (e.g., "1257057278398300160")

If set, tools will use this as the default league ID when none is provided.

## Usage Examples

In Claude Desktop, you can ask:

### League Information
- "Show me the details of my Sleeper league 1257057278398300160"
- "What are the current standings in my league?"
- "Who are all the users in my fantasy league?"

### Matchups & Scores
- "Show me the matchups for week 5 in my league"
- "What's the score of this week's games?"

### Rosters & Players
- "Show me all the rosters in my league"
- "Get trending players being added in the last 24 hours"
- "Search for player information for player ID 4866"

### Playoffs
- "Show me the playoff bracket"
- "What's the losers bracket look like?"

### Transactions
- "Show me all the trades and waiver pickups from week 3"
- "What draft picks have been traded in my league?"

### Drafts
- "Show me the draft results for my league"
- "Get all the picks from draft ID 12345678"

### NFL Info
- "What week of the NFL season are we in?"
- "Get the current NFL state"

## Architecture
```
Claude Desktop → MCP Gateway → Sleeper MCP Server → Sleeper API
                                                      (api.sleeper.app)
```

## Development

### Local Testing
```bash
# Set environment variables for testing (optional)
export SLEEPER_LEAGUE_ID="1257057278398300160"

# Run directly
python sleeper_server.py

# Test MCP protocol
echo '{"jsonrpc":"2.0","method":"tools/list","id":1}' | python sleeper_server.py
```

### Adding New Tools

1. Add the function to `sleeper_server.py`
2. Decorate with `@mcp.tool()`
3. Update the catalog entry with the new tool name
4. Rebuild the Docker image

## API Rate Limits

The Sleeper API has a general rate limit of 1000 API calls per minute. This server does not implement rate limiting, so be mindful of your usage to avoid being IP-blocked.

## Troubleshooting

### Tools Not Appearing
- Verify Docker image built successfully: `docker images | grep sleeper`
- Check catalog and registry files are properly formatted
- Ensure Claude Desktop config includes custom catalog
- Restart Claude Desktop completely

### API Errors
- Verify league IDs are correct
- Check that the resource exists (some endpoints return empty arrays for missing data)
- Ensure you're using valid week numbers (1-18 for regular season)

### Player Data
- The player database is ~5MB and updated periodically
- Player IDs are used throughout the API (e.g., "4866", "2391")
- Use the `search_player_info` tool to look up player details by ID

## Security Considerations

- No authentication required (Sleeper API is read-only)
- All data is publicly accessible fantasy football information
- Running as non-root user in container
- No sensitive data stored or logged

## API Documentation

Full Sleeper API documentation: https://docs.sleeper.com

## License

MIT License
