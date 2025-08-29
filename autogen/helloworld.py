"""
This is a simple example of using AutoGen with MCP servers for enhanced capabilities.
Includes filesystem and weather MCP server integration.
"""
import asyncio
import os
from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_ext.tools.mcp import McpWorkbench, StdioServerParams
from autogen_agentchat.ui import Console
from env import *

async def main() -> None:
    # Setup MCP servers parameters
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # Filesystem MCP Server parameters
    filesystem_server_params = StdioServerParams(
        command="npx",
        args=["-y", "@modelcontextprotocol/server-filesystem", current_dir],
        read_timeout_seconds=30,
    )

    # Weather MCP Server parameters
    weather_server_params = StdioServerParams(
        command="python",
        args=["mcp-weather.py"],
        cwd=".",
        read_timeout_seconds=30,
    )

    # Create OpenAI model client
    model_client = OpenAIChatCompletionClient(
        model=os.environ["OPENAI_MODEL"],
        api_key=os.environ["OPENAI_API_KEY"],
        base_url=os.environ["OPENAI_API_BASE"]
    )

    try:
        # Create workbenches for the MCP servers
        async with McpWorkbench(filesystem_server_params) as filesystem_workbench, \
                   McpWorkbench(weather_server_params) as weather_workbench:

            # Create agent with MCP capabilities using AutoGen AssistantAgent
            agent = AssistantAgent(
                name="mcp_assistant",
                model_client=model_client,
                workbench=[filesystem_workbench, weather_workbench],
                system_message=(
                    "You are a helpful assistant with access to filesystem and weather tools. "
                    "ALWAYS use the available tools when users ask about files, directories, or weather. "
                    "When asked to list files, use the filesystem tools to get the actual file listing. "
                    "When asked about weather, use the weather forecast tools with the provided coordinates. "
                    "Be specific about using tools rather than providing general information."
                ),
            )

            # List available tools
            fs_tools = await filesystem_workbench.list_tools()
            weather_tools = await weather_workbench.list_tools()
            print(f"Filesystem tools: {[tool['name'] for tool in fs_tools]}")
            print(f"Weather tools: {[tool['name'] for tool in weather_tools]}")
            print("\n" + "="*50 + "\n")

            # Test filesystem functionality
            print("Testing Filesystem Server:")
            print("-" * 30)
            result = await agent.run(
                task="List the files in the current directory and tell me what they are."
            )
            print(f"Agent response: {result.messages[-1].content}")

            print("\n" + "="*50 + "\n")

            # Test weather functionality
            print("Testing Weather Server:")
            print("-" * 25)
            result = await agent.run(
                task="What's the weather forecast for Beijing (latitude 39.9, longitude 116.4)?"
            )
            print(f"Agent response: {result.messages[-1].content}")
    except Exception as e:
        print(f"Error running with MCP servers: {e}")
        print("Make sure Node.js and @modelcontextprotocol/server-filesystem are installed")
        print("Also ensure mcp-weather.py is available in the current directory")

asyncio.run(main())
