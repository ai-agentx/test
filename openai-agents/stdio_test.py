"""
Example demonstrating MCPServerStdio usage with openai-agents-python.

Based on patterns from:
https://github.com/openai/openai-agents-python/tree/main/examples/mcp/
"""

import asyncio
import os

from agents import Agent, Runner, set_tracing_disabled
from agents.mcp import MCPServerStdio
from agents.models.openai_chatcompletions import OpenAIChatCompletionsModel
from openai import AsyncOpenAI


# Disable tracing to avoid 403 errors from external telemetry services
set_tracing_disabled(True)


def get_openai_model() -> OpenAIChatCompletionsModel:
    api_key = os.getenv("OPENAI_API_KEY", "sk-1234")
    base_url = os.getenv("OPENAI_API_BASE_URL", "http://127.0.0.1:4000")
    model_name = os.getenv("OPENAI_MODEL", "gemini-2.5")

    openai_client = AsyncOpenAI(base_url=base_url, api_key=api_key)
    return OpenAIChatCompletionsModel(model=model_name, openai_client=openai_client)


async def filesystem_example():
    print("\n=== Filesystem MCP Server Example ===\n")

    current_dir = os.path.dirname(os.path.abspath(__file__))

    server = MCPServerStdio(
        params={
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-filesystem", current_dir],
        },
        name="Filesystem MCP Server",
        cache_tools_list=True,  # Cache tools for better performance
        client_session_timeout_seconds=30,
    )

    model = get_openai_model()

    agent = Agent(
        name="File Assistant",
        instructions=(
            "You are a helpful assistant that can read and analyze files. "
            "Use the filesystem tools to help users with file operations."
        ),
        model=model,
        mcp_servers=[server]
    )

    try:
        async with server:
            tools = await server.list_tools()
            print(f"Available tools: {[tool.name for tool in tools]}")
            print("\nRunning agent with filesystem access...\n")
            result = await Runner.run(
                agent,
                "List the files in the current directory and tell me what they are."
            )
            print(f"Agent response: {result.final_output}")
    except Exception as e:
        print(f"Error running filesystem example: {e}")
        print("Make sure Node.js and @modelcontextprotocol/server-filesystem are installed")


async def custom_mcp_server_example():
    print("\n=== Custom MCP Server Example ===\n")

    server = MCPServerStdio(
        params={
            "command": "python",
            "args": ["mcp-weather.py"],
            "env": {
                "MCP_SERVER_CONFIG": "production"
            },
            "cwd": ".",
            "encoding": "utf-8"
        },
        name="Weather MCP Server",
        cache_tools_list=False,  # Don't cache if tools change frequently
        client_session_timeout_seconds=30,  # Longer timeout for custom servers
    )

    model = get_openai_model()

    agent = Agent(
        name="Weather Assistant",
        instructions=(
            "You are a helpful weather assistant that can get weather forecasts. "
            "Use the weather tools to help users with weather information. "
            "When calling get_forecast, use reasonable latitude and longitude values."
        ),
        model=model,
        mcp_servers=[server]
    )

    try:
        async with server:
            print("Connected to custom weather MCP server")
            tools = await server.list_tools()
            print(f"Available tools: {[tool.name for tool in tools]}")
            print("\nRunning agent with weather access...\n")
            result = await Runner.run(
                agent,
                "What's the weather forecast for Beijing (latitude 39.9, longitude 116.4)?"
            )
            print(f"Agent response: {result.final_output}")
    except Exception as e:
        print(f"Error running custom server example: {e}")
        print("Make sure mcp-weather.py is in the current directory and working")


async def main():
    # Filesystem example
    # Install with: npm install -g @modelcontextprotocol/server-filesystem
    await filesystem_example()

    # Custom weather server example
    # Uses the mcp-weather.py server in the current directory
    await custom_mcp_server_example()


if __name__ == "__main__":
    asyncio.run(main())
