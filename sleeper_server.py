#!/usr/bin/env python3
"""
Sleeper Fantasy Football MCP Server - Access Sleeper API for fantasy football leagues, rosters, matchups, drafts, and player data
"""

import os
import sys
import logging
import json
import httpx
from mcp.server.fastmcp import FastMCP

# Configure logging to stderr
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stderr,
)
logger = logging.getLogger("sleeper-server")

# Initialize MCP server
mcp = FastMCP("sleeper")

# Configuration
BASE_URL = "https://api.sleeper.app/v1"
LEAGUE_ID = os.environ.get("SLEEPER_LEAGUE_ID", "")

# === UTILITY FUNCTIONS ===


async def fetch_json(url: str):
    """Fetch JSON data from Sleeper API."""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            raise Exception(f"API Error {e.response.status_code}: {e.response.text}")
        except Exception as e:
            raise Exception(f"Request failed: {str(e)}")


def format_user(user):
    """Format user object for display."""
    if not user:
        return "No user data"
    return f"""👤 User: {user.get("display_name", "N/A")} (@{user.get("username", "N/A")})
- User ID: {user.get("user_id", "N/A")}
- Avatar: {user.get("avatar", "N/A")}"""


def format_league(league):
    """Format league object for display."""
    if not league:
        return "No league data"
    return f"""🏈 League: {league.get("name", "N/A")}
- League ID: {league.get("league_id", "N/A")}
- Season: {league.get("season", "N/A")}
- Status: {league.get("status", "N/A")}
- Sport: {league.get("sport", "N/A")}
- Total Rosters: {league.get("total_rosters", "N/A")}
- Draft ID: {league.get("draft_id", "N/A")}"""


def format_roster(roster, index):
    """Format roster object for display."""
    settings = roster.get("settings", {})
    return f"""📊 Roster {index + 1} (ID: {roster.get("roster_id", "N/A")})
- Owner: {roster.get("owner_id", "N/A")}
- Record: {settings.get("wins", 0)}W - {settings.get("losses", 0)}L - {settings.get("ties", 0)}T
- Points For: {settings.get("fpts", 0)}.{settings.get("fpts_decimal", 0)}
- Points Against: {settings.get("fpts_against", 0)}.{settings.get("fpts_against_decimal", 0)}
- Players: {len(roster.get("players", []))} total
- Starters: {", ".join(roster.get("starters", [])[:5])}{"..." if len(roster.get("starters", [])) > 5 else ""}"""


# === MCP TOOLS ===


@mcp.tool()
async def get_user(username: str = "") -> str:
    """Get Sleeper user information by username or user ID."""
    logger.info(f"Fetching user: {username}")

    if not username.strip():
        return "❌ Error: Username or user ID is required"

    try:
        url = f"{BASE_URL}/user/{username}"
        user = await fetch_json(url)
        return f"✅ User Found:\n{format_user(user)}"
    except Exception as e:
        logger.error(f"Error: {e}")
        return f"❌ Error: {str(e)}"


@mcp.tool()
async def get_user_leagues(
    user_id: str = "", sport: str = "nfl", season: str = "2024"
) -> str:
    """Get all leagues for a user in a specific sport and season."""
    logger.info(f"Fetching leagues for user {user_id}")

    if not user_id.strip():
        return "❌ Error: User ID is required"

    try:
        url = f"{BASE_URL}/user/{user_id}/leagues/{sport}/{season}"
        leagues = await fetch_json(url)

        if not leagues:
            return f"📭 No leagues found for user {user_id} in {sport} {season}"

        result = f"🏈 Found {len(leagues)} league(s):\n\n"
        for i, league in enumerate(leagues, 1):
            result += f"{i}. {format_league(league)}\n\n"

        return result
    except Exception as e:
        logger.error(f"Error: {e}")
        return f"❌ Error: {str(e)}"


@mcp.tool()
async def get_league(league_id: str = "") -> str:
    """Get detailed information about a specific league."""
    logger.info(f"Fetching league: {league_id}")

    lid = league_id.strip() or LEAGUE_ID.strip()
    if not lid:
        return "❌ Error: League ID is required (provide league_id or set SLEEPER_LEAGUE_ID environment variable)"

    try:
        url = f"{BASE_URL}/league/{lid}"
        league = await fetch_json(url)

        result = f"✅ League Details:\n{format_league(league)}\n\n"

        if league.get("settings"):
            settings = league["settings"]
            result += f"⚙️ Settings:\n"
            result += f"- Playoff Teams: {settings.get('playoff_teams', 'N/A')}\n"
            result += f"- Waiver Type: {settings.get('waiver_type', 'N/A')}\n"
            result += (
                f"- Trade Deadline: Week {settings.get('trade_deadline', 'N/A')}\n"
            )

        return result
    except Exception as e:
        logger.error(f"Error: {e}")
        return f"❌ Error: {str(e)}"


@mcp.tool()
async def get_league_rosters(league_id: str = "") -> str:
    """Get all rosters in a league with standings and player information."""
    logger.info(f"Fetching rosters for league: {league_id}")

    lid = league_id.strip() or LEAGUE_ID.strip()
    if not lid:
        return "❌ Error: League ID is required (provide league_id or set SLEEPER_LEAGUE_ID environment variable)"

    try:
        url = f"{BASE_URL}/league/{lid}/rosters"
        rosters = await fetch_json(url)

        if not rosters:
            return f"📭 No rosters found for league {lid}"

        result = f"📊 Found {len(rosters)} roster(s):\n\n"
        for i, roster in enumerate(rosters):
            result += f"{format_roster(roster, i)}\n\n"

        return result
    except Exception as e:
        logger.error(f"Error: {e}")
        return f"❌ Error: {str(e)}"


@mcp.tool()
async def get_league_users(league_id: str = "") -> str:
    """Get all users in a league with their team information."""
    logger.info(f"Fetching users for league: {league_id}")

    lid = league_id.strip() or LEAGUE_ID.strip()
    if not lid:
        return "❌ Error: League ID is required (provide league_id or set SLEEPER_LEAGUE_ID environment variable)"

    try:
        url = f"{BASE_URL}/league/{lid}/users"
        users = await fetch_json(url)

        if not users:
            return f"📭 No users found for league {lid}"

        result = f"👥 Found {len(users)} user(s):\n\n"
        for i, user in enumerate(users, 1):
            metadata = user.get("metadata", {})
            team_name = metadata.get("team_name", "No team name")
            is_owner = "👑 Commissioner" if user.get("is_owner") else ""
            result += f"{i}. {user.get('display_name', 'N/A')} (@{user.get('username', 'N/A')}) {is_owner}\n"
            result += f"   Team: {team_name}\n"
            result += f"   User ID: {user.get('user_id', 'N/A')}\n\n"

        return result
    except Exception as e:
        logger.error(f"Error: {e}")
        return f"❌ Error: {str(e)}"


@mcp.tool()
async def get_league_matchups(league_id: str = "", week: str = "1") -> str:
    """Get all matchups for a specific week in a league."""
    logger.info(f"Fetching matchups for league {league_id}, week {week}")

    lid = league_id.strip() or LEAGUE_ID.strip()
    if not lid:
        return "❌ Error: League ID is required (provide league_id or set SLEEPER_LEAGUE_ID environment variable)"

    if not week.strip():
        return "❌ Error: Week number is required"

    try:
        url = f"{BASE_URL}/league/{lid}/matchups/{week}"
        matchups = await fetch_json(url)

        if not matchups:
            return f"📭 No matchups found for league {lid}, week {week}"

        matchup_dict = {}
        for matchup in matchups:
            mid = matchup.get("matchup_id")
            if mid not in matchup_dict:
                matchup_dict[mid] = []
            matchup_dict[mid].append(matchup)

        result = f"🏈 Week {week} Matchups:\n\n"
        for mid, teams in matchup_dict.items():
            result += f"⚔️ Matchup {mid}:\n"
            for team in teams:
                points = team.get("points", 0)
                custom = team.get("custom_points")
                points_str = (
                    f"{custom} (override)" if custom is not None else f"{points}"
                )
                result += f"  Roster {team.get('roster_id', 'N/A')}: {points_str} pts\n"
                result += f"    Starters: {', '.join(team.get('starters', [])[:5])}{'...' if len(team.get('starters', [])) > 5 else ''}\n"
            result += "\n"

        return result
    except Exception as e:
        logger.error(f"Error: {e}")
        return f"❌ Error: {str(e)}"


@mcp.tool()
async def get_winners_bracket(league_id: str = "") -> str:
    """Get the winners playoff bracket for a league."""
    logger.info(f"Fetching winners bracket for league: {league_id}")

    lid = league_id.strip() or LEAGUE_ID.strip()
    if not lid:
        return "❌ Error: League ID is required (provide league_id or set SLEEPER_LEAGUE_ID environment variable)"

    try:
        url = f"{BASE_URL}/league/{lid}/winners_bracket"
        bracket = await fetch_json(url)

        if not bracket:
            return f"📭 No playoff bracket found for league {lid}"

        result = f"🏆 Winners Bracket:\n\n"
        for match in bracket:
            round_num = match.get("r", "N/A")
            match_id = match.get("m", "N/A")
            t1 = match.get("t1", "TBD")
            t2 = match.get("t2", "TBD")
            winner = match.get("w", "TBD")

            result += f"Round {round_num}, Match {match_id}:\n"
            result += f"  Team 1: Roster {t1}\n"
            result += f"  Team 2: Roster {t2}\n"
            if winner != "TBD" and winner is not None:
                result += f"  Winner: Roster {winner}\n"
            result += "\n"

        return result
    except Exception as e:
        logger.error(f"Error: {e}")
        return f"❌ Error: {str(e)}"


@mcp.tool()
async def get_losers_bracket(league_id: str = "") -> str:
    """Get the losers playoff bracket for a league."""
    logger.info(f"Fetching losers bracket for league: {league_id}")

    lid = league_id.strip() or LEAGUE_ID.strip()
    if not lid:
        return "❌ Error: League ID is required (provide league_id or set SLEEPER_LEAGUE_ID environment variable)"

    try:
        url = f"{BASE_URL}/league/{lid}/losers_bracket"
        bracket = await fetch_json(url)

        if not bracket:
            return f"📭 No losers bracket found for league {lid}"

        result = f"🎯 Losers Bracket:\n\n"
        for match in bracket:
            round_num = match.get("r", "N/A")
            match_id = match.get("m", "N/A")
            t1 = match.get("t1", "TBD")
            t2 = match.get("t2", "TBD")
            winner = match.get("w", "TBD")
            placement = match.get("p", "")

            result += f"Round {round_num}, Match {match_id}"
            if placement:
                result += f" (for place {placement})"
            result += ":\n"
            result += f"  Team 1: Roster {t1}\n"
            result += f"  Team 2: Roster {t2}\n"
            if winner != "TBD" and winner is not None:
                result += f"  Winner: Roster {winner}\n"
            result += "\n"

        return result
    except Exception as e:
        logger.error(f"Error: {e}")
        return f"❌ Error: {str(e)}"


@mcp.tool()
async def get_league_transactions(league_id: str = "", week: str = "1") -> str:
    """Get all transactions for a specific week in a league including trades, waivers, and free agent pickups."""
    logger.info(f"Fetching transactions for league {league_id}, week {week}")

    lid = league_id.strip() or LEAGUE_ID.strip()
    if not lid:
        return "❌ Error: League ID is required (provide league_id or set SLEEPER_LEAGUE_ID environment variable)"

    if not week.strip():
        return "❌ Error: Week number is required"

    try:
        url = f"{BASE_URL}/league/{lid}/transactions/{week}"
        transactions = await fetch_json(url)

        if not transactions:
            return f"📭 No transactions found for league {lid}, week {week}"

        result = f"💼 Week {week} Transactions ({len(transactions)} total):\n\n"

        for i, txn in enumerate(transactions, 1):
            txn_type = txn.get("type", "unknown")
            status = txn.get("status", "unknown")

            result += f"{i}. Type: {txn_type.upper()} - Status: {status}\n"

            if txn.get("adds"):
                result += f"   Adds: {', '.join([f'Player {pid} to Roster {rid}' for pid, rid in txn['adds'].items()])}\n"

            if txn.get("drops"):
                result += f"   Drops: {', '.join([f'Player {pid} from Roster {rid}' for pid, rid in txn['drops'].items()])}\n"

            if txn.get("draft_picks"):
                result += (
                    f"   Draft Picks: {len(txn['draft_picks'])} pick(s) involved\n"
                )

            result += "\n"

        return result
    except Exception as e:
        logger.error(f"Error: {e}")
        return f"❌ Error: {str(e)}"


@mcp.tool()
async def get_traded_picks(league_id: str = "") -> str:
    """Get all traded draft picks in a league including future picks."""
    logger.info(f"Fetching traded picks for league: {league_id}")

    lid = league_id.strip() or LEAGUE_ID.strip()
    if not lid:
        return "❌ Error: League ID is required (provide league_id or set SLEEPER_LEAGUE_ID environment variable)"

    try:
        url = f"{BASE_URL}/league/{lid}/traded_picks"
        picks = await fetch_json(url)

        if not picks:
            return f"📭 No traded picks found for league {lid}"

        result = f"🔄 Traded Draft Picks ({len(picks)} total):\n\n"

        for i, pick in enumerate(picks, 1):
            season = pick.get("season", "N/A")
            round_num = pick.get("round", "N/A")
            original = pick.get("roster_id", "N/A")
            previous = pick.get("previous_owner_id", "N/A")
            current = pick.get("owner_id", "N/A")

            result += f"{i}. {season} Round {round_num}\n"
            result += f"   Original Owner: Roster {original}\n"
            result += f"   Previous Owner: Roster {previous}\n"
            result += f"   Current Owner: Roster {current}\n\n"

        return result
    except Exception as e:
        logger.error(f"Error: {e}")
        return f"❌ Error: {str(e)}"


@mcp.tool()
async def get_nfl_state() -> str:
    """Get current NFL season state including week, season type, and season dates."""
    logger.info("Fetching NFL state")

    try:
        url = f"{BASE_URL}/state/nfl"
        state = await fetch_json(url)

        result = f"""🏈 NFL State:
- Current Week: {state.get("week", "N/A")}
- Display Week: {state.get("display_week", "N/A")}
- Season: {state.get("season", "N/A")}
- Season Type: {state.get("season_type", "N/A")}
- Season Start: {state.get("season_start_date", "N/A")}
- League Season: {state.get("league_season", "N/A")}
- League Create Season: {state.get("league_create_season", "N/A")}
- Previous Season: {state.get("previous_season", "N/A")}"""

        return result
    except Exception as e:
        logger.error(f"Error: {e}")
        return f"❌ Error: {str(e)}"


@mcp.tool()
async def get_user_drafts(
    user_id: str = "", sport: str = "nfl", season: str = "2024"
) -> str:
    """Get all drafts for a user in a specific sport and season."""
    logger.info(f"Fetching drafts for user {user_id}")

    if not user_id.strip():
        return "❌ Error: User ID is required"

    try:
        url = f"{BASE_URL}/user/{user_id}/drafts/{sport}/{season}"
        drafts = await fetch_json(url)

        if not drafts:
            return f"📭 No drafts found for user {user_id} in {sport} {season}"

        result = f"📝 Found {len(drafts)} draft(s):\n\n"
        for i, draft in enumerate(drafts, 1):
            result += f"{i}. Draft ID: {draft.get('draft_id', 'N/A')}\n"
            result += f"   Type: {draft.get('type', 'N/A')}\n"
            result += f"   Status: {draft.get('status', 'N/A')}\n"
            result += f"   League ID: {draft.get('league_id', 'N/A')}\n"
            result += f"   Season: {draft.get('season', 'N/A')}\n\n"

        return result
    except Exception as e:
        logger.error(f"Error: {e}")
        return f"❌ Error: {str(e)}"


@mcp.tool()
async def get_league_drafts(league_id: str = "") -> str:
    """Get all drafts for a league."""
    logger.info(f"Fetching drafts for league: {league_id}")

    lid = league_id.strip() or LEAGUE_ID.strip()
    if not lid:
        return "❌ Error: League ID is required (provide league_id or set SLEEPER_LEAGUE_ID environment variable)"

    try:
        url = f"{BASE_URL}/league/{lid}/drafts"
        drafts = await fetch_json(url)

        if not drafts:
            return f"📭 No drafts found for league {lid}"

        result = f"📝 Found {len(drafts)} draft(s):\n\n"
        for i, draft in enumerate(drafts, 1):
            settings = draft.get("settings", {})
            metadata = draft.get("metadata", {})

            result += f"{i}. Draft ID: {draft.get('draft_id', 'N/A')}\n"
            result += f"   Type: {draft.get('type', 'N/A')}\n"
            result += f"   Status: {draft.get('status', 'N/A')}\n"
            result += f"   Season: {draft.get('season', 'N/A')}\n"
            result += f"   Teams: {settings.get('teams', 'N/A')}\n"
            result += f"   Rounds: {settings.get('rounds', 'N/A')}\n"
            result += f"   Scoring: {metadata.get('scoring_type', 'N/A')}\n\n"

        return result
    except Exception as e:
        logger.error(f"Error: {e}")
        return f"❌ Error: {str(e)}"


@mcp.tool()
async def get_draft(draft_id: str = "") -> str:
    """Get detailed information about a specific draft."""
    logger.info(f"Fetching draft: {draft_id}")

    if not draft_id.strip():
        return "❌ Error: Draft ID is required"

    try:
        url = f"{BASE_URL}/draft/{draft_id}"
        draft = await fetch_json(url)

        settings = draft.get("settings", {})
        metadata = draft.get("metadata", {})

        result = f"""📝 Draft Details:
- Draft ID: {draft.get("draft_id", "N/A")}
- Type: {draft.get("type", "N/A")}
- Status: {draft.get("status", "N/A")}
- League ID: {draft.get("league_id", "N/A")}
- Season: {draft.get("season", "N/A")}
- Sport: {draft.get("sport", "N/A")}

⚙️ Settings:
- Teams: {settings.get("teams", "N/A")}
- Rounds: {settings.get("rounds", "N/A")}
- Pick Timer: {settings.get("pick_timer", "N/A")} seconds
- Scoring: {metadata.get("scoring_type", "N/A")}

📊 Roster Slots:
- QB: {settings.get("slots_qb", 0)}
- RB: {settings.get("slots_rb", 0)}
- WR: {settings.get("slots_wr", 0)}
- TE: {settings.get("slots_te", 0)}
- FLEX: {settings.get("slots_flex", 0)}
- K: {settings.get("slots_k", 0)}
- DEF: {settings.get("slots_def", 0)}
- BN: {settings.get("slots_bn", 0)}"""

        return result
    except Exception as e:
        logger.error(f"Error: {e}")
        return f"❌ Error: {str(e)}"


@mcp.tool()
async def get_draft_picks(draft_id: str = "") -> str:
    """Get all picks made in a draft."""
    logger.info(f"Fetching draft picks for: {draft_id}")

    if not draft_id.strip():
        return "❌ Error: Draft ID is required"

    try:
        url = f"{BASE_URL}/draft/{draft_id}/picks"
        picks = await fetch_json(url)

        if not picks:
            return f"📭 No picks found for draft {draft_id}"

        result = f"🎯 Draft Picks ({len(picks)} total):\n\n"

        for pick in picks[:50]:
            metadata = pick.get("metadata", {})
            player_name = f"{metadata.get('first_name', '')} {metadata.get('last_name', '')}".strip()
            position = metadata.get("position", "N/A")
            team = metadata.get("team", "N/A")

            result += f"Pick {pick.get('pick_no', 'N/A')} (Round {pick.get('round', 'N/A')}):\n"
            result += f"  Player: {player_name or 'Unknown'} - {position} ({team})\n"
            result += f"  Roster ID: {pick.get('roster_id', 'N/A')}\n"
            if pick.get("is_keeper"):
                result += f"  ⭐ Keeper\n"
            result += "\n"

        if len(picks) > 50:
            result += f"... and {len(picks) - 50} more picks\n"

        return result
    except Exception as e:
        logger.error(f"Error: {e}")
        return f"❌ Error: {str(e)}"


@mcp.tool()
async def get_draft_traded_picks(draft_id: str = "") -> str:
    """Get all traded picks in a draft."""
    logger.info(f"Fetching traded draft picks for: {draft_id}")

    if not draft_id.strip():
        return "❌ Error: Draft ID is required"

    try:
        url = f"{BASE_URL}/draft/{draft_id}/traded_picks"
        picks = await fetch_json(url)

        if not picks:
            return f"📭 No traded picks found for draft {draft_id}"

        result = f"🔄 Traded Draft Picks ({len(picks)} total):\n\n"

        for i, pick in enumerate(picks, 1):
            result += (
                f"{i}. {pick.get('season', 'N/A')} Round {pick.get('round', 'N/A')}\n"
            )
            result += f"   Original: Roster {pick.get('roster_id', 'N/A')}\n"
            result += f"   Previous: Roster {pick.get('previous_owner_id', 'N/A')}\n"
            result += f"   Current: Roster {pick.get('owner_id', 'N/A')}\n\n"

        return result
    except Exception as e:
        logger.error(f"Error: {e}")
        return f"❌ Error: {str(e)}"


@mcp.tool()
async def get_trending_players(
    trend_type: str = "add", lookback_hours: str = "24", limit: str = "25"
) -> str:
    """Get trending players based on add or drop activity."""
    logger.info(f"Fetching trending {trend_type} players")

    if trend_type not in ["add", "drop"]:
        return "❌ Error: trend_type must be 'add' or 'drop'"

    try:
        lookback = int(lookback_hours) if lookback_hours.strip() else 24
        lim = int(limit) if limit.strip() else 25
    except ValueError:
        return "❌ Error: lookback_hours and limit must be valid numbers"

    try:
        url = f"{BASE_URL}/players/nfl/trending/{trend_type}?lookback_hours={lookback}&limit={lim}"
        players = await fetch_json(url)

        if not players:
            return f"📭 No trending {trend_type} players found"

        emoji = "📈" if trend_type == "add" else "📉"
        result = f"{emoji} Trending {trend_type.upper()} Players (Last {lookback} hours):\n\n"

        for i, player in enumerate(players, 1):
            result += f"{i}. Player ID: {player.get('player_id', 'N/A')} - {player.get('count', 0)} {trend_type}s\n"

        return result
    except Exception as e:
        logger.error(f"Error: {e}")
        return f"❌ Error: {str(e)}"


@mcp.tool()
async def search_player_info(player_id: str = "") -> str:
    """Search for detailed information about a specific player by their player ID - requires fetching all players first."""
    logger.info(f"Searching for player: {player_id}")

    if not player_id.strip():
        return "❌ Error: Player ID is required"

    try:
        url = f"{BASE_URL}/players/nfl"
        all_players = await fetch_json(url)

        player = all_players.get(player_id)
        if not player:
            return f"❌ Player ID {player_id} not found"

        result = f"""🏈 Player: {player.get("first_name", "")} {player.get("last_name", "")}
- Player ID: {player_id}
- Position: {player.get("position", "N/A")}
- Team: {player.get("team", "N/A")}
- Number: #{player.get("number", "N/A")}
- Status: {player.get("status", "N/A")}
- Age: {player.get("age", "N/A")}
- Height: {player.get("height", "N/A")}
- Weight: {player.get("weight", "N/A")}
- College: {player.get("college", "N/A")}
- Years Exp: {player.get("years_exp", "N/A")}
- Fantasy Positions: {", ".join(player.get("fantasy_positions", []))}"""

        if player.get("injury_status"):
            result += f"\n⚠️ Injury Status: {player.get('injury_status', 'N/A')}"

        return result
    except Exception as e:
        logger.error(f"Error: {e}")
        return f"❌ Error: {str(e)}"


# === SERVER STARTUP ===
if __name__ == "__main__":
    logger.info("Starting Sleeper Fantasy Football MCP server...")

    if LEAGUE_ID:
        logger.info(f"Default league ID set to: {LEAGUE_ID}")
    else:
        logger.info(
            "No default league ID set. Users must provide league_id parameter or set SLEEPER_LEAGUE_ID environment variable"
        )

    try:
        mcp.run(transport="stdio")
    except Exception as e:
        logger.error(f"Server error: {e}", exc_info=True)
        sys.exit(1)
