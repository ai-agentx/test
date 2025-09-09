#!/usr/bin/env python3
"""
CAMEL-AI + MCP Demo with Weather and Filesystem Integration

This demo showcases CAMEL-AI framework integration with MCP servers:
- Weather MCP server (custom Python implementation)
- Filesystem MCP server (official @modelcontextprotocol/server-filesystem)

Configuration Options:
1. env.py file (recommended for development)
2. Environment variables (recommended for production)
3. Command line arguments (for testing)

Usage:
  python helloworld.py                    # Run async demo
  python helloworld.py --sync             # Run sync demo
  python helloworld.py --create-env       # Create sample env.py
  python helloworld.py --api-key KEY      # Override API key
  python helloworld.py --model MODEL      # Override model

Environment Variables:
  OPENAI_API_KEY     - Your API key (required)
  OPENAI_MODEL       - Model name (required)
  OPENAI_BASE_URL    - API endpoint (optional)
  OPENAI_MODEL_FAMILY- Model family (optional)

Based on official CAMEL documentation patterns:
https://github.com/camel-ai/camel/tree/master/examples/toolkits/mcp/mcp_toolkit.py

Inspired by AutoGen MCP integration for comprehensive tool capabilities.
"""

import argparse
import asyncio
import json
import os
import platform
import traceback
import shutil

from camel.agents import ChatAgent
from camel.messages import BaseMessage
from camel.models import ModelFactory
from camel.toolkits import MCPToolkit
from camel.types import ModelPlatformType, ModelType, RoleType
from pathlib import Path
from rich import print as rprint
from rich.console import Console

console = Console()


def create_mcp_config():
    """Create MCP configuration file with both weather and filesystem servers."""
    current_dir = os.path.dirname(os.path.abspath(__file__))

    config = {
        "mcpServers": {
            "weather": {
                "command": "python",
                "args": ["mcp-weather.py"]
            }
        }
    }

    # On Windows, npx might need .cmd extension
    if platform.system() == "Windows":
        npx_commands = ["npx.cmd", "npx"]
        node_commands = ["node.exe", "node"]
    else:
        npx_commands = ["npx"]
        node_commands = ["node"]

    npx_path = None
    for cmd in npx_commands:
        npx_path = shutil.which(cmd)
        if npx_path:
            break

    node_path = None
    for cmd in node_commands:
        node_path = shutil.which(cmd)
        if node_path:
            break

    if npx_path:
        rprint(f"✅ Found npx at: {npx_path}")
        # Use the full path to avoid execution issues
        config["mcpServers"]["filesystem"] = {
            "command": npx_path,
            "args": ["-y", "@modelcontextprotocol/server-filesystem", current_dir]
        }
    elif node_path:
        rprint(f"⚠️ npx not found, but found node at: {node_path}")
        rprint("💡 You may need to install @modelcontextprotocol/server-filesystem globally")
        # Skip filesystem server if npx is not available
    else:
        rprint("❌ Node.js/npx not found, skipping filesystem server")
        rprint("💡 To enable filesystem capabilities:")
        rprint("   1. Install Node.js from https://nodejs.org/")
        rprint("   2. Run: npm install -g @modelcontextprotocol/server-filesystem")

    config_path = Path("mcp_config.json")
    with open(config_path, "w") as f:
        json.dump(config, f, indent=2)

    rprint(f"✅ Created MCP config: {config_path}")
    if "filesystem" in config["mcpServers"]:
        rprint(f"🔧 Filesystem server will monitor: {current_dir}")
    else:
        rprint("🔧 Running with weather-only configuration")

    return str(config_path)


def create_sample_env_file():
    """Create a sample env.py file with configuration template."""
    env_content = '''import os

# Required configuration
os.environ["OPENAI_API_KEY"] = "your-api-key-here"
os.environ["OPENAI_MODEL"] = "gpt-4"

# Optional configuration
os.environ["OPENAI_BASE_URL"] = "https://api.openai.com/v1"  # Or your custom endpoint
os.environ["OPENAI_MODEL_FAMILY"] = "OPENAI"  # OPENAI, GEMINI, CLAUDE, etc.

# Example for custom endpoints:
# os.environ["OPENAI_BASE_URL"] = "https://aiapi.zx.zte.com.cn/openai/v1"
# os.environ["OPENAI_API_KEY"] = "sk-your-custom-key"
# os.environ["OPENAI_MODEL"] = "gpt-4"
'''

    env_file = Path("env.py.example")
    with open(env_file, "w") as f:
        f.write(env_content)

    rprint(f"✅ Created sample configuration file: {env_file}")
    rprint("💡 Copy this to env.py and update with your actual values")


def setup_environment():
    """Setup environment variables from env.py file or system environment."""
    env_file = Path("env.py")

    # Try to load from env.py file first
    if env_file.exists():
        try:
            rprint("✅ Loaded environment settings from env.py")
            return True
        except ImportError as e:
            rprint(f"⚠️ Failed to load env.py: {e}")

    # Fallback to system environment variables
    rprint("🔧 Loading configuration from environment variables...")

    # Check for required environment variables
    required_vars = ["OPENAI_API_KEY", "OPENAI_MODEL"]
    missing_vars = []

    for var in required_vars:
        if not os.environ.get(var):
            missing_vars.append(var)

    if missing_vars:
        rprint(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        rprint("\n💡 Configuration options:")
        rprint("   Option 1 - Environment variables (Windows):")
        rprint("     set OPENAI_API_KEY=your-api-key")
        rprint("     set OPENAI_MODEL=your-model-name")
        rprint("     set OPENAI_BASE_URL=your-api-base-url  # Optional")
        rprint("     set OPENAI_MODEL_FAMILY=OPENAI         # Optional")
        rprint("\n   Option 2 - Environment variables (Linux/Mac):")
        rprint("     export OPENAI_API_KEY=your-api-key")
        rprint("     export OPENAI_MODEL=your-model-name")
        rprint("     export OPENAI_BASE_URL=your-api-base-url  # Optional")
        rprint("     export OPENAI_MODEL_FAMILY=OPENAI         # Optional")
        rprint("\n   Option 3 - Create env.py file:")

        # Offer to create sample env file
        create_sample_env_file()

        return False

    # Set default values for optional variables
    defaults = {
        "OPENAI_BASE_URL": "https://api.openai.com/v1",
        "OPENAI_MODEL_FAMILY": "OPENAI"
    }

    for var, default_value in defaults.items():
        if not os.environ.get(var):
            os.environ[var] = default_value
            rprint(f"🔧 Using default {var}: {default_value}")

    # Display current configuration
    rprint("✅ Environment configuration loaded:")
    rprint(f"   API Key: {os.environ.get('OPENAI_API_KEY', 'Not set')[:10]}...")
    rprint(f"   Model: {os.environ.get('OPENAI_MODEL', 'Not set')}")
    rprint(f"   Base URL: {os.environ.get('OPENAI_BASE_URL', 'Not set')}")
    rprint(f"   Model Family: {os.environ.get('OPENAI_MODEL_FAMILY', 'Not set')}")

    return True


async def mcp_toolkit_async_example():
    """Async MCP example with weather and optional filesystem capabilities."""
    rprint("[bold green]CAMEL-AI + MCP Integration Demo (Weather + Filesystem)[/bold green]")

    # Setup environment
    if not setup_environment():
        rprint("[red]❌ Environment setup failed. Please configure API keys.[/red]")
        return

    # Create config
    config_path = create_mcp_config()

    # Use the async context manager pattern from official examples
    async with MCPToolkit(config_path=config_path) as mcp_toolkit:
        rprint(f"✅ Connected to MCP servers")

        tools = mcp_toolkit.get_tools()
        rprint(f"Found {len(tools)} tools:")

        # Categorize tools
        filesystem_tools = []
        weather_tools = []

        for tool in tools:
            tool_name = tool.func.__name__
            rprint(f"  • {tool_name}")
            if 'file' in tool_name.lower() or 'read' in tool_name.lower() or 'write' in tool_name.lower() or 'list' in tool_name.lower():
                filesystem_tools.append(tool)
            elif 'weather' in tool_name.lower() or 'forecast' in tool_name.lower():
                weather_tools.append(tool)

        # Create model
        model = ModelFactory.create(
            model_platform=ModelPlatformType.OPENAI,
            model_type=os.environ.get("OPENAI_MODEL", "gpt-4"),
        )

        # Test filesystem functionality if available
        if filesystem_tools or any('file' in str(tool) for tool in tools):
            rprint("\n" + "="*60)
            rprint("[bold yellow]Testing Filesystem Capabilities[/bold yellow]")
            rprint("="*60)

            # Create filesystem agent
            filesystem_agent = ChatAgent(
                system_message=(
                    "You are a helpful assistant with access to filesystem tools. "
                    "When asked about files or directories, use the filesystem tools to get the actual information. "
                    "Be thorough and provide detailed information about what you find."
                ),
                model=model,
                tools=tools,
            )

            # Test filesystem functionality
            fs_queries = [
                "List the files in the current directory and tell me what they are.",
                "What Python files are in this directory? Read the first few lines of each to understand what they do."
            ]

            for i, query in enumerate(fs_queries, 1):
                rprint(f"\n[bold blue]Filesystem Query {i}:[/bold blue] {query}")
                rprint("-" * 50)
                try:
                    response = await filesystem_agent.astep(query)
                    rprint(f"[bold green]Agent:[/bold green] {response.msgs[0].content}")

                    if response.info.get('tool_calls'):
                        rprint(f"[dim yellow]Tool calls made: {len(response.info['tool_calls'])}[/dim yellow]")
                except Exception as e:
                    rprint(f"[red]Error:[/red] {e}")
        else:
            rprint("\n[yellow]⚠️ No filesystem tools available - skipping filesystem tests[/yellow]")

        rprint("\n" + "="*60)
        rprint("[bold yellow]Testing Weather Capabilities[/bold yellow]")
        rprint("="*60)

        # Create weather agent
        weather_agent = ChatAgent(
            system_message=(
                "You are a helpful assistant with access to weather tools. "
                "When asked about weather, use the weather forecast tools with the provided coordinates. "
                "Provide detailed and informative weather reports."
            ),
            model=model,
            tools=tools,
        )

        # Test weather functionality
        weather_queries = [
            "What's the weather like at coordinates 40.7128, -74.0060? (New York)",
            "Get the weather forecast for Beijing coordinates 39.9, 116.4"
        ]

        for i, query in enumerate(weather_queries, 1):
            rprint(f"\n[bold blue]Weather Query {i}:[/bold blue] {query}")
            rprint("-" * 50)
            try:
                response = await weather_agent.astep(query)
                rprint(f"[bold green]Agent:[/bold green] {response.msgs[0].content}")

                if response.info.get('tool_calls'):
                    rprint(f"[dim yellow]Tool calls made: {len(response.info['tool_calls'])}[/dim yellow]")
            except Exception as e:
                rprint(f"[red]Error:[/red] {e}")

        # Test combined functionality only if we have both types of tools
        if len(tools) > 1:
            rprint("\n" + "="*60)
            rprint("[bold yellow]Testing Combined Capabilities[/bold yellow]")
            rprint("="*60)

            # Create combined agent
            combined_agent = ChatAgent(
                system_message=(
                    "You are a versatile assistant with access to available tools. "
                    "Use the appropriate tools based on what the user asks for. "
                    "If filesystem tools are available, use them for file operations. "
                    "Use weather tools for weather forecasts."
                ),
                model=model,
                tools=tools,
            )

            # Test combined functionality
            if filesystem_tools:
                combined_query = "First, list the Python files in this directory, then get the weather for New York (40.7128, -74.0060)"
            else:
                combined_query = "Get the weather for both New York (40.7128, -74.0060) and London (51.5074, -0.1278)"

            rprint(f"\n[bold blue]Combined Query:[/bold blue] {combined_query}")
            rprint("-" * 50)

            try:
                response = await combined_agent.astep(combined_query)
                rprint(f"[bold green]Agent:[/bold green] {response.msgs[0].content}")

                if response.info.get('tool_calls'):
                    rprint(f"[dim yellow]Tool calls made: {len(response.info['tool_calls'])}[/dim yellow]")
            except Exception as e:
                rprint(f"[red]Error:[/red] {e}")


def mcp_toolkit_sync_example():
    """Sync MCP example with both weather and filesystem capabilities."""
    rprint("[bold green]CAMEL-AI + MCP Integration Demo (Sync - Weather + Filesystem)[/bold green]")

    # Setup environment
    if not setup_environment():
        rprint("[red]❌ Environment setup failed. Please configure API keys.[/red]")
        return

    # Create config
    config_path = create_mcp_config()

    # Use the sync context manager pattern from official examples
    with MCPToolkit(config_path=config_path) as mcp_toolkit:
        rprint(f"✅ Connected to MCP servers")

        tools = mcp_toolkit.get_tools()
        rprint(f"Found {len(tools)} tools:")
        for tool in tools:
            rprint(f"  • {tool.func.__name__}")

        # Create model
        model = ModelFactory.create(
            model_platform=ModelPlatformType.OPENAI,
            model_type=os.environ.get("OPENAI_MODEL", "gpt-4"),
        )

        # Test filesystem functionality
        rprint(f"\n[bold yellow]Testing Filesystem + Weather (Sync)[/bold yellow]")
        rprint("-" * 40)

        # Create combined agent
        agent = ChatAgent(
            system_message=(
                "You are a helpful assistant with filesystem and weather capabilities. "
                "Use filesystem tools for file operations and weather tools for forecasts."
            ),
            model=model,
            tools=tools,
        )

        # Test queries
        test_queries = [
            "List the files in the current directory",
            "What's the weather like at coordinates 40.7128, -74.0060?"
        ]

        for query in test_queries:
            rprint(f"\n[bold blue]Query:[/bold blue] {query}")
            try:
                response = agent.step(query)
                rprint(f"[bold green]Agent:[/bold green] {response.msgs[0].content}")

                if response.info.get('tool_calls'):
                    rprint(f"[dim yellow]Tool calls: {len(response.info['tool_calls'])}[/dim yellow]")
            except Exception as e:
                rprint(f"[red]Error:[/red] {e}")


async def main():
    """Main function demonstrating CAMEL-AI with Weather + Filesystem MCP integration."""
    try:
        rprint("[bold magenta]🐫 CAMEL-AI + MCP Demo (Weather + Filesystem)[/bold magenta]")
        rprint("Based on official CAMEL examples with filesystem MCP integration")
        rprint("-" * 60)

        # Use async version only (since we're already in async context)
        await mcp_toolkit_async_example()

        rprint("\n" + "="*60)
        rprint("[bold green]✅ Demo completed successfully![/bold green]")
        rprint("Your CAMEL agent now has weather capabilities!")
    except Exception as e:
        rprint(f"[red]❌ Demo failed:[/red] {e}")

        # Provide specific guidance based on the error
        error_str = str(e)
        if "npx" in error_str or "Win32" in error_str:
            rprint("\n[yellow]💡 Node.js/npx Setup Instructions for Windows:[/yellow]")
            rprint("   1. Download and install Node.js from: https://nodejs.org/")
            rprint("   2. Restart your terminal/PowerShell after installation")
            rprint("   3. Verify installation: node --version && npm --version")
            rprint("   4. Install filesystem server: npm install -g @modelcontextprotocol/server-filesystem")
            rprint("   5. Re-run this demo")
            rprint("\n[dim]   Alternative: Run with weather-only mode automatically enabled[/dim]")
        else:
            rprint("[yellow]💡 Check your environment configuration and API keys[/yellow]")

        traceback.print_exc()


if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="CAMEL-AI + MCP Demo")
    parser.add_argument("--sync", action="store_true", help="Run synchronous version")
    parser.add_argument("--create-env", action="store_true", help="Create sample env.py file and exit")
    parser.add_argument("--api-key", help="OpenAI API key (overrides env)")
    parser.add_argument("--model", help="Model name (overrides env)")
    parser.add_argument("--base-url", help="API base URL (overrides env)")
    parser.add_argument("--model-family", help="Model family (overrides env)",
                       choices=["OPENAI", "GEMINI", "CLAUDE"])

    args = parser.parse_args()

    # Handle --create-env flag
    if args.create_env:
        create_sample_env_file()
        exit(0)

    # Override environment variables with command line arguments
    if args.api_key:
        os.environ["OPENAI_API_KEY"] = args.api_key
    if args.model:
        os.environ["OPENAI_MODEL"] = args.model
    if args.base_url:
        os.environ["OPENAI_BASE_URL"] = args.base_url
    if args.model_family:
        os.environ["OPENAI_MODEL_FAMILY"] = args.model_family

    # Run the appropriate version
    if args.sync:
        rprint("[bold magenta]🐫 CAMEL-AI + MCP Demo (Sync)[/bold magenta]")
        mcp_toolkit_sync_example()
    else:
        asyncio.run(main())
