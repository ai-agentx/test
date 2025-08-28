"""
This is a simple example of using AutoGen with MCP servers for enhanced capabilities.
Includes filesystem and weather MCP server integration.
"""
import asyncio
import os
from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_ext.models.openai._model_info import ModelInfo
from agents import Agent, Runner, set_tracing_disabled
from agents.mcp import MCPServerStdio
from agents.models.openai_chatcompletions import OpenAIChatCompletionsModel
from openai import AsyncOpenAI
from env import *

# Disable tracing to avoid SSL timeout errors in logs
set_tracing_disabled(True)

async def main() -> None:
    # Setup MCP servers
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # Filesystem MCP Server
    filesystem_server = MCPServerStdio(
        params={
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-filesystem", current_dir],
        },
        name="Filesystem MCP Server",
        cache_tools_list=True,
        client_session_timeout_seconds=30,
    )

    # Weather MCP Server
    weather_server = MCPServerStdio(
        params={
            "command": "python",
            "args": ["mcp-weather.py"],
            "cwd": ".",
            "encoding": "utf-8"
        },
        name="Weather MCP Server",
        cache_tools_list=False,
        client_session_timeout_seconds=30,
    )

    # Create OpenAI client using openai-agents pattern
    openai_client = AsyncOpenAI(
        base_url=os.environ["OPENAI_API_BASE"],
        api_key=os.environ["OPENAI_API_KEY"]
    )
    model = OpenAIChatCompletionsModel(
        model=os.environ["OPENAI_MODEL"],
        openai_client=openai_client
    )

    # Create agent with MCP capabilities using openai-agents
    agent = Agent(
        name="MCP Assistant",
        instructions=(
            "You are a helpful assistant with access to filesystem and weather tools. "
            "ALWAYS use the available tools when users ask about files, directories, or weather. "
            "When asked to list files, use the filesystem tools to get the actual file listing. "
            "When asked about weather, use the weather forecast tools with the provided coordinates. "
            "Be specific about using tools rather than providing general information."
        ),
        model=model,
        mcp_servers=[filesystem_server, weather_server]
    )

    try:
        async with filesystem_server, weather_server:
            # List available tools
            fs_tools = await filesystem_server.list_tools()
            weather_tools = await weather_server.list_tools()
            print(f"Filesystem tools: {[tool.name for tool in fs_tools]}")
            print(f"Weather tools: {[tool.name for tool in weather_tools]}")
            print("\n" + "="*50 + "\n")

            # Test filesystem functionality
            print("Testing Filesystem Server:")
            print("-" * 30)
            result = await Runner.run(
                agent,
                "List the files in the current directory and tell me what they are."
            )
            print(f"Agent response: {result.final_output}")

            print("\n" + "="*50 + "\n")

            # Test weather functionality
            print("Testing Weather Server:")
            print("-" * 25)
            result = await Runner.run(
                agent,
                "What's the weather forecast for Beijing (latitude 39.9, longitude 116.4)?"
            )
            print(f"Agent response: {result.final_output}")
    except Exception as e:
        print(f"Error running with MCP servers: {e}")
        print("Make sure Node.js and @modelcontextprotocol/server-filesystem are installed")
        print("Also ensure mcp-weather.py is available in the openai-agents directory")
    except Exception as e:
        print(f"Error running with MCP servers: {e}")
        print("Make sure Node.js and @modelcontextprotocol/server-filesystem are installed")
        print("Also ensure mcp-weather.py is available in the openai-agents directory")

asyncio.run(main())
