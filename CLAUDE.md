# Sleeper Fantasy Football MCP Server - Implementation Guide

## Overview

This MCP server provides comprehensive access to the Sleeper Fantasy Football API, enabling AI assistants to retrieve league data, matchups, rosters, draft information, player stats, and more.

## Key Features

### User & League Management
- Fetch user profiles by username or ID
- Get all leagues for a user by season
- View detailed league settings and configuration
- List all users/managers in a league

### Rosters & Standings
- View all rosters with win/loss records
- See current points for and against
- Check player lineups and bench players
- Track waiver positions and moves

### Matchups & Scoring
- Get weekly matchups with scores
- View starting lineups for each team
- See custom commissioner overrides
- Track head-to-head results

### Playoffs
- Winners bracket (championship path)
- Losers bracket (consolation games)
- Track playoff progression
- View placement games

### Transactions
- Weekly transactions (trades, waivers, free agents)
- Traded draft picks (current and future)
- FAAB spending tracking
- Add/drop history

### Drafts
- Draft results and picks
- Draft settings and configuration
- Keeper designations
- Traded picks within drafts

### Players & Trends
- Trending adds/drops
- Player search by ID
- Detailed player information
- Injury status tracking

## Default League ID

Users can set a `SLEEPER_LEAGUE_ID` environment variable to avoid typing their league ID repeatedly. If set, all league-related tools will use this as the default when no league_id parameter is provided.

Example: `SLEEPER_LEAGUE_ID=1257057278398300160`

## Tool Categories

### Essential Tools (Most Common)
1. `get_league` - League overview
2. `get_league_rosters` - Current standings
3. `get_league_matchups` - Weekly scores
4. `get_league_users` - Team managers

### Analysis Tools
1. `get_winners_bracket` - Playoff tracking
2. `get_league_transactions` - Trade/waiver analysis
3. `get_traded_picks` - Dynasty league management
4. `get_trending_players` - Waiver wire targets

### Draft Tools
1. `get_draft` - Draft recap
2. `get_draft_picks` - Pick-by-pick results
3. `get_league_drafts` - All league drafts

### Reference Tools
1. `get_nfl_state` - Current week/season info
2. `search_player_info` - Player lookup
3. `get_user` - User profile

## Response Formatting

All tools return formatted strings with emojis for visual clarity:
- 🏈 League/NFL information
- 👤 User profiles
- 📊 Rosters and standings
- ⚔️ Matchups
- 🏆 Winners bracket
- 🎯 Losers bracket
- 💼 Transactions
- 🔄 Trades
- 📝 Drafts
- 📈 Trending adds
- 📉 Trending drops
- ✅ Success messages
- ❌ Error messages

## Error Handling

All tools include comprehensive error handling:
- Missing required parameters
- Invalid league/user/draft IDs
- API rate limit errors (429)
- Network timeouts
- Invalid data formats

## Common Use Cases

### League Commissioner
"Show me this week's matchups, recent transactions, and current standings"

### Dynasty Manager
"Get all traded picks and show me trending adds for RB"

### Draft Analysis
"Show me the draft results and tell me who got the best value"

### Playoff Tracking
"Display the playoff bracket and tell me who's playing for the championship"

## API Limitations

1. **Read-Only**: Cannot modify leagues, make trades, or submit waivers
2. **Rate Limits**: Stay under 1000 calls per minute
3. **No Authentication**: All data is publicly accessible
4. **Player Database**: ~5MB file, updated periodically by Sleeper

## Best Practices

1. **Set Default League ID**: Reduces repetitive parameter passing
2. **Cache Player Data**: The player database changes infrequently
3. **Batch Queries**: Combine related information requests
4. **Use Correct Week**: Verify current week with `get_nfl_state` first

## Development Notes

- Uses `httpx` for async HTTP requests
- All parameters default to empty strings (not None)
- Single-line docstrings only (per MCP requirements)
- Comprehensive logging to stderr
- 10-second timeout on all API calls

## Future Enhancements

Potential additions (if Sleeper API expands):
- League creation/modification (if API becomes writable)
- Real-time draft monitoring
- Player projections integration
- Historical season data analysis
- Advanced statistics calculations

## Support

For API questions: https://docs.sleeper.com
For Sleeper support: https://support.sleeper.com
