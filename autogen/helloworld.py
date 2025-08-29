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
from autogen_core.models import ModelFamily

# Try to import env.py, otherwise use environment variables
try:
    from env import *
except ImportError:
    # Fallback to environment variables if env.py doesn't exist
    # Check for required environment variables
    required_vars = ["OPENAI_API_KEY", "OPENAI_MODEL"]
    missing_vars = [var for var in required_vars if not os.environ.get(var)]

    if missing_vars:
        print(f"Error: Missing required environment variables: {', '.join(missing_vars)}")
        print("Please either:")
        print("1. Create an env.py file with the required settings, or")
        print("2. Set environment variables using export commands:")
        print(f"   export OPENAI_API_KEY='your-api-key'")
        print(f"   export OPENAI_MODEL='your-model-name'")
        print(f"   export OPENAI_API_BASE='your-api-base-url'  # Optional")
        print(f"   export OPENAI_MODEL_FAMILY='OPENAI'  # Optional, defaults to UNKNOWN")
        exit(1)

    # Set default values for optional variables
    if not os.environ.get("OPENAI_API_BASE"):
        os.environ["OPENAI_API_BASE"] = "https://api.openai.com/v1"
    if not os.environ.get("OPENAI_MODEL_FAMILY"):
        os.environ["OPENAI_MODEL_FAMILY"] = "UNKNOWN"

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

    # Create OpenAI model client with custom model info
    model_client = OpenAIChatCompletionClient(
        model=os.environ["OPENAI_MODEL"],
        api_key=os.environ["OPENAI_API_KEY"],
        base_url=os.environ["OPENAI_API_BASE"],
        model_info={
            "vision": False,
            "function_calling": True,
            "json_output": True,
            "family": os.environ["OPENAI_MODEL_FAMILY"],
            "structured_output": False,
        },
    )

    try:
        # Create workbenches for the MCP servers
        async with McpWorkbench(filesystem_server_params) as filesystem_workbench, \
                   McpWorkbench(weather_server_params) as weather_workbench:

            # List available tools
            fs_tools = await filesystem_workbench.list_tools()
            weather_tools = await weather_workbench.list_tools()
            print(f"Filesystem tools: {[tool['name'] for tool in fs_tools]}")
            print(f"Weather tools: {[tool['name'] for tool in weather_tools]}")
            print("\n" + "="*50 + "\n")

            # Test filesystem functionality
            print("Testing Filesystem Server:")
            print("-" * 30)

            # Create filesystem agent
            fs_agent = AssistantAgent(
                name="filesystem_assistant",
                model_client=model_client,
                workbench=[filesystem_workbench],
                system_message=(
                    "You are a helpful assistant with access to filesystem tools. "
                    "When asked about files or directories, use the filesystem tools to get the actual information."
                ),
            )

            result = await fs_agent.run(
                task="List the files in the current directory and tell me what they are."
            )
            print(f"Agent response: {result.messages[-1].content}")

            print("\n" + "="*50 + "\n")

            # Test weather functionality
            print("Testing Weather Server:")
            print("-" * 25)

            # Create weather agent
            weather_agent = AssistantAgent(
                name="weather_assistant",
                model_client=model_client,
                workbench=[weather_workbench],
                system_message=(
                    "You are a helpful assistant with access to weather tools. "
                    "When asked about weather, use the weather forecast tools with the provided coordinates."
                ),
            )

            result = await weather_agent.run(
                task="What's the weather forecast for Beijing (latitude 39.9, longitude 116.4)?"
            )
            print(f"Agent response: {result.messages[-1].content}")
    except Exception as e:
        print(f"Error running with MCP servers: {e}")
        print("Make sure Node.js and @modelcontextprotocol/server-filesystem are installed")
        print("Also ensure mcp-weather.py is available in the current directory")

asyncio.run(main())
