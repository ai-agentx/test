from fastmcp import FastMCP


mcp = FastMCP("weather")

@mcp.tool()
async def get_forecast(lat: float, lon: float) -> str:
    return f"晴, 25℃"

mcp.run()
