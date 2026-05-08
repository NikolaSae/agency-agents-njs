from mcp.server.fastmcp import FastMCP
from pydantic import Field
import httpx
import json
import os

mcp = FastMCP("example-mcp-server")

@mcp.tool()
async def search_issues(
    repo: str = Field(description="Repository in owner/repo format"),
    state: str = Field(default="open", description="Filter by state: open, closed, or all"),
    limit: int = Field(default=20, ge=1, le=100, description="Max results to return"),
) -> str:
    """Search GitHub issues by state. Returns issue number, title, author, and state."""
    async with httpx.AsyncClient() as client:
        params = {"state": state, "per_page": limit}
        headers = {}
        if os.environ.get('GITHUB_TOKEN'):
            headers["Authorization"] = f"token {os.environ['GITHUB_TOKEN']}"
        resp = await client.get(
            f"https://api.github.com/repos/{repo}/issues",
            params=params,
            headers=headers,
        )
        resp.raise_for_status()
        issues = [{"number": i["number"], "title": i["title"], "author": i["user"]["login"], "state": i["state"]} for i in resp.json()]
        return json.dumps(issues, indent=2)

@mcp.tool()
async def get_weather(
    location: str = Field(description="City name or location for weather lookup"),
) -> str:
    """Get current weather information for a location using wttr.in service."""
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"https://wttr.in/{location}?format=j1")
        if resp.status_code == 200:
            data = resp.json()
            current = data["current_condition"][0]
            return f"Weather in {location}: {current['weatherDesc'][0]['value']}, Temperature: {current['temp_C']}°C, Feels like: {current['FeelsLikeC']}°C"
        else:
            return f"Failed to fetch weather for {location}: {resp.status_code}"

@mcp.tool()
async def calculate_expression(
    expression: str = Field(description="Mathematical expression to evaluate, e.g., '2 + 3 * 4'"),
) -> str:
    """Safely evaluate a mathematical expression and return the result."""
    try:
        # Use eval with restricted environment for safety
        allowed_names = {
            "abs": abs, "round": round, "min": min, "max": max,
            "sum": sum, "len": len, "pow": pow, "sqrt": lambda x: x**0.5
        }
        result = eval(expression, {"__builtins__": {}}, allowed_names)
        return f"Result: {result}"
    except Exception as e:
        return f"Error evaluating expression: {e}"

if __name__ == "__main__":
    mcp.run()