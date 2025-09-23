"""
🤖 Agno Hello World Example with Agent and MCP Servers

This example demonstrates an AI agent with access to multiple MCP (Model Context Protocol) servers:
- Weather MCP server (mcp-weather.py) for weather information
- Filesystem MCP server for file operations

The agent runs by default with both MCP servers connected, providing:
🌤️ Weather capabilities: Get current weather and forecasts for any location
📁 Filesystem capabilities: Read/write files, list directories, navigate filesystem

Run this example:
python helloworld.py

Prerequisites:
1. Set up API keys in env.py or .env file
2. Install dependencies: pip install -r requirements.txt
3. Install filesystem MCP: npm install -g @modelcontextprotocol/server-filesystem
4. Start weather MCP server: python mcp-weather.py (in another terminal)
"""

import asyncio
import os
from textwrap import dedent
from pathlib import Path

# Load environment configuration if available
try:
    import env
except ImportError:
    try:
        from dotenv import load_dotenv
        load_dotenv()
        print("✅ Environment configuration loaded from .env file")
    except ImportError:
        print("⚠️ No environment configuration found. Make sure to set API keys.")

# Configure proxy settings for the API endpoint
def configure_proxy_settings():
    """Configure proxy settings based on environment variables."""
    # Simply use the NO_PROXY setting from env.py without modification
    no_proxy = os.getenv("NO_PROXY", "")

    if no_proxy is not None:
        # Set both uppercase and lowercase versions (some libraries use lowercase)
        os.environ["NO_PROXY"] = no_proxy
        os.environ["no_proxy"] = no_proxy

        if no_proxy:
            print(f"🌐 Using NO_PROXY from env.py: {no_proxy}")
        else:
            print(f"🌐 NO_PROXY is set to empty string (bypass all proxy)")
    else:
        print(f"🌐 NO_PROXY not configured")

# Configure proxy settings
configure_proxy_settings()

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.models.anthropic import Claude
from agno.tools.mcp import MCPTools
from agno.os import AgentOS
from agno.db.sqlite import SqliteDb


def get_configured_model():
    """Get the model configured in environment variables."""
    model_name = os.getenv("OPENAI_MODEL_NAME", "gpt-4o-mini")
    api_base = os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1")
    api_key = os.getenv("OPENAI_API_KEY", "")

    print(f"🔧 Model configuration:")
    print(f"   Model: {model_name}")
    print(f"   API Base: {api_base}")
    print(f"   API Key: {api_key[:10]}..." if api_key else "   API Key: Not set")
    print(f"   NO_PROXY: {os.environ.get('NO_PROXY', 'Not set')}")

    # Create OpenAI client with extended timeout
    print(f"🔗 Expected chat completions URL: {api_base}/chat/completions")

    # Try different client configurations
    print(f"🔧 Creating OpenAI client with custom base_url...")

    return OpenAIChat(
        id=model_name,
        api_key=api_key,
        base_url=api_base,  # Explicitly set the base_url
        timeout=60.0,  # Increase timeout to 60 seconds
        max_retries=3,  # Allow retries
    )
def test_network_connectivity():
    """Test network connectivity to the API endpoint."""
    api_base = os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1")

    try:
        import urllib.request
        import socket
        from urllib.parse import urlparse

        parsed_url = urlparse(api_base)
        host = parsed_url.hostname
        port = parsed_url.port or (443 if parsed_url.scheme == 'https' else 80)

        print(f"🔍 Testing connectivity to {host}:{port}...")

        # Test basic TCP connectivity
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        result = sock.connect_ex((host, port))
        sock.close()

        if result == 0:
            print(f"✅ TCP connection to {host}:{port} successful")
            return True
        else:
            print(f"❌ TCP connection to {host}:{port} failed")
            return False

    except Exception as e:
        print(f"❌ Network connectivity test failed: {e}")
        return False


def test_api_endpoint():
    """Test the API endpoint with a simple HTTP request."""
    api_base = os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1")
    api_key = os.getenv("OPENAI_API_KEY", "")

    try:
        import urllib.request
        import json

        # Test models endpoint (usually available on OpenAI-compatible APIs)
        models_url = f"{api_base}/models"

        print(f"🧪 Testing API endpoint: {models_url}")

        request = urllib.request.Request(models_url)
        request.add_header('Authorization', f'Bearer {api_key}')
        request.add_header('Content-Type', 'application/json')

        with urllib.request.urlopen(request, timeout=30) as response:
            if response.getcode() == 200:
                print(f"✅ API endpoint responded successfully")
                data = json.loads(response.read().decode())
                if 'data' in data and len(data['data']) > 0:
                    print(f"📋 Available models: {len(data['data'])} models found")
                    # Show first few model names
                    for i, model in enumerate(data['data'][:3]):
                        print(f"   - {model.get('id', 'unknown')}")
                    if len(data['data']) > 3:
                        print(f"   ... and {len(data['data']) - 3} more")
                return True
            else:
                print(f"⚠️ API endpoint returned status: {response.getcode()}")
                return False

    except urllib.error.HTTPError as e:
        print(f"❌ HTTP Error {e.code}: {e.reason}")
        if e.code == 401:
            print("💡 This might be an authentication issue - check your API key")
        elif e.code == 404:
            print("💡 The endpoint might not exist - check the API base URL")
        return False
    except Exception as e:
        print(f"❌ API endpoint test failed: {e}")
        return False


def test_chat_completions_endpoint():
    """Test the chat completions endpoint specifically."""
    api_base = os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1")
    api_key = os.getenv("OPENAI_API_KEY", "")
    model_name = os.getenv("OPENAI_MODEL_NAME", "gpt-4o-mini")

    try:
        import urllib.request
        import json

        # Test chat completions endpoint
        chat_url = f"{api_base}/chat/completions"

        print(f"🧪 Testing chat completions endpoint: {chat_url}")

        # Simple test request
        test_data = {
            "model": model_name,
            "messages": [{"role": "user", "content": "Hello"}],
            "max_tokens": 10,
            "stream": False
        }

        request = urllib.request.Request(chat_url, method='POST')
        request.add_header('Authorization', f'Bearer {api_key}')
        request.add_header('Content-Type', 'application/json')

        data = json.dumps(test_data).encode('utf-8')

        with urllib.request.urlopen(request, data, timeout=30) as response:
            if response.getcode() == 200:
                print(f"✅ Chat completions endpoint working!")
                response_data = json.loads(response.read().decode())
                if 'choices' in response_data:
                    print(f"📝 Test response received successfully")
                return True
            else:
                print(f"⚠️ Chat completions endpoint returned status: {response.getcode()}")
                return False

    except urllib.error.HTTPError as e:
        print(f"❌ HTTP Error {e.code}: {e.reason}")
        if e.code == 404:
            print("💡 Chat completions endpoint not found - the API path might be different")
            print(f"💡 Try checking if the endpoint should be: {api_base.replace('/openai', '/v1')}/chat/completions")
        elif e.code == 422:
            print("💡 Request format error - the API might expect different parameters")
        return False
    except Exception as e:
        print(f"❌ Chat completions test failed: {e}")
        return False


def test_streaming_vs_nonstreaming():
    """Test both streaming and non-streaming requests to identify the issue."""
    api_base = os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1")
    api_key = os.getenv("OPENAI_API_KEY", "")
    model_name = os.getenv("OPENAI_MODEL_NAME", "gpt-4o-mini")

    try:
        import urllib.request
        import json

        chat_url = f"{api_base}/chat/completions"

        # Test non-streaming request
        print(f"🧪 Testing non-streaming request...")
        test_data = {
            "model": model_name,
            "messages": [{"role": "user", "content": "Hello"}],
            "max_tokens": 10,
            "stream": False
        }

        request = urllib.request.Request(chat_url, method='POST')
        request.add_header('Authorization', f'Bearer {api_key}')
        request.add_header('Content-Type', 'application/json')

        data = json.dumps(test_data).encode('utf-8')

        with urllib.request.urlopen(request, data, timeout=30) as response:
            if response.getcode() == 200:
                print(f"✅ Non-streaming request successful")
            else:
                print(f"❌ Non-streaming request failed: {response.getcode()}")

        # Test streaming request
        print(f"🧪 Testing streaming request...")
        test_data["stream"] = True

        request = urllib.request.Request(chat_url, method='POST')
        request.add_header('Authorization', f'Bearer {api_key}')
        request.add_header('Content-Type', 'application/json')

        data = json.dumps(test_data).encode('utf-8')

        with urllib.request.urlopen(request, data, timeout=30) as response:
            if response.getcode() == 200:
                print(f"✅ Streaming request successful")
                # Read a bit of the streaming response
                chunk = response.read(100)
                print(f"📡 Streaming response sample: {chunk[:50]}...")
                return True
            else:
                print(f"❌ Streaming request failed: {response.getcode()}")
                return False

    except Exception as e:
        print(f"❌ Streaming test failed: {e}")
        return False


async def basic_agent_example():
    """Basic Agno agent example."""
    print("🚀 Running Basic Agent Example")

    # Test network connectivity first
    if not test_network_connectivity():
        print("⚠️ Network connectivity issue detected. Continuing anyway...")

    # Test API endpoint
    if not test_api_endpoint():
        print("⚠️ API endpoint test failed. Continuing anyway...")

    # Test chat completions endpoint specifically
    if not test_chat_completions_endpoint():
        print("⚠️ Chat completions endpoint test failed. This might explain the connection error...")

    # Test streaming vs non-streaming to identify the root cause
    print("\n🔍 Testing streaming vs non-streaming requests...")
    test_streaming_vs_nonstreaming()

    # Use model configuration from environment variables
    model_name = os.getenv("OPENAI_MODEL_NAME", "gpt-4o-mini")
    api_base = os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1")

    print(f"🤖 Using model: {model_name}")
    print(f"🌐 API Base: {api_base}")

    try:
        agent = Agent(
            name="Hello World Agent",
            model=get_configured_model(),  # Use configured model with timeout
            instructions=dedent("""\
                You are a friendly AI assistant created with Agno.
                - Be helpful and informative
                - Use emojis to make responses engaging
                - Keep responses concise but complete
            """),
            markdown=True,
        )

        # Simple interaction - try without streaming first
        print("🔄 Testing without streaming...")
        await agent.aprint_response(
            "Hello! Can you tell me what Agno is and what you can do?",
            stream=False  # Disable streaming to test
        )

    except Exception as e:
        print(f"❌ Error with custom LLM provider: {e}")
        print("\n💡 Troubleshooting suggestions:")
        print(f"1. Verify API endpoint is accessible: {api_base}")
        print(f"2. Check model name is correct: {model_name}")
        print("3. Confirm API key is valid in env.py")
        print("4. Test network connectivity to your LLM provider")
        print("5. Check if the provider supports the OpenAI-compatible API format")
        print("6. Verify proxy settings and NO_PROXY configuration")
        print("7. Try running: curl -v " + api_base + "/models" + " -H 'Authorization: Bearer YOUR_KEY'")
        print("9. Verify the API server is running and not overloaded")
        print("\n🔧 Current proxy settings:")
        print(f"   NO_PROXY: {os.environ.get('NO_PROXY', 'Not set')}")
        print(f"   HTTP_PROXY: {os.environ.get('HTTP_PROXY', 'Not set')}")
        print(f"   HTTPS_PROXY: {os.environ.get('HTTPS_PROXY', 'Not set')}")


async def mcp_agent_example():
    """MCP agent with filesystem tools example."""
    print("🔧 Running MCP Agent Example")

    try:
        # Initialize MCP tools with filesystem server
        async with MCPTools(
            "npx -y @modelcontextprotocol/server-filesystem",
            args=[str(Path(__file__).parent)],
            timeout_seconds=30
        ) as mcp_tools:

            agent = Agent(
                name="MCP Filesystem Agent",
                model=get_configured_model(),
                tools=[mcp_tools],
                instructions=dedent("""\
                    You are an AI assistant with filesystem access via MCP.
                    - Help users explore and analyze files and directories
                    - Be careful with file operations
                    - Explain what you're doing before performing actions
                    - Use appropriate tools for the task
                """),
                markdown=True,
            )

            await agent.aprint_response(
                "Can you list the files in the current directory and tell me about this project?",
                stream=True
            )

    except Exception as e:
        print(f"❌ Error with MCP agent: {e}")
        print("💡 Make sure you have Node.js installed and the MCP server package available")


def setup_mcp_server():
    """Setup AgentOS with MCP server capabilities."""
    print("🏗️ Setting up MCP Server with AgentOS")

    # Setup database
    db = SqliteDb(db_file="tmp/hello_world_agents.db")

    # Create multiple agents for different purposes
    chat_agent = Agent(
        id="chat-agent",
        name="Chat Agent",
        model=OpenAIChat(id="gpt-4o-mini"),
        db=db,
        instructions=dedent("""\
            You are a friendly chat assistant.
            Help users with general questions and conversations.
        """),
        add_history_to_context=True,
        num_history_runs=3,
        markdown=True,
    )

    code_agent = Agent(
        id="code-agent",
        name="Code Assistant",
        model=Claude(id="claude-sonnet-4-0"),
        db=db,
        instructions=dedent("""\
            You are a code assistant specialized in Python development.
            Help users with coding questions, debugging, and best practices.
        """),
        add_history_to_context=True,
        num_history_runs=5,
        markdown=True,
    )

    # Weather agent with MCP tools (if weather server is available)
    try:
        weather_host = os.getenv("MCP_WEATHER_SERVER_HOST", "localhost")
        weather_port = os.getenv("MCP_WEATHER_SERVER_PORT", "8000")
        weather_url = f"http://{weather_host}:{weather_port}/sse"

        # Note: In a real setup, you'd want to handle the MCP connection lifecycle properly
        weather_agent = Agent(
            id="weather-agent",
            name="Weather Assistant",
            model=OpenAIChat(id="gpt-4o-mini"),
            db=db,
            instructions=dedent(f"""\
                You are a weather assistant with access to weather forecast data.
                You can help users get weather information for specific locations.
                Weather MCP server should be available at: {weather_url}
                Ask users for latitude and longitude if they want weather information.
            """),
            add_history_to_context=True,
            num_history_runs=3,
            markdown=True,
        )
        agents_list = [chat_agent, code_agent, weather_agent]
        print("🌤️ Weather agent added (Weather MCP server integration available)")
    except Exception as e:
        agents_list = [chat_agent, code_agent]
        print("⚠️ Weather agent not added (Weather MCP server not available)")

    # Setup AgentOS with MCP enabled
    agent_os = AgentOS(
        name="Hello World AgentOS",
        description="A simple AgentOS example with multiple agents and MCP server",
        agents=agents_list,
        enable_mcp=True,  # This enables MCP server at /mcp endpoint
    )

    app = agent_os.get_app()

    print("🌐 AgentOS Server starting...")
    print("📋 Available endpoints:")
    print("  - http://localhost:7777/docs - API documentation")
    print("  - http://localhost:7777/mcp - MCP server endpoint")
    print("  - http://localhost:7777/ - AgentOS interface")
    print("\n🤖 Available agents:")
    print("  - chat-agent: General chat assistant")
    print("  - code-agent: Python code assistant")
    if len(agents_list) > 2:
        print("  - weather-agent: Weather forecast assistant")
    print(f"\n💡 Total agents: {len(agents_list)}")
    print("\n🌤️ To use weather features:")
    print("  1. Start weather MCP server: python mcp-weather.py")
    print("  2. Use weather agent or run: python helloworld.py --weather")

    # Start the server
    agent_os.serve(app="helloworld:app", host="0.0.0.0", port=7777)


async def advanced_mcp_example():
    """Advanced example with multiple MCP servers."""
    print("⚡ Running Advanced MCP Example")

    try:
        # Multiple MCP tools example
        from agno.tools.mcp import MultiMCPTools

        multi_mcp = MultiMCPTools([
            "npx -y @modelcontextprotocol/server-filesystem " + str(Path(__file__).parent),
        ])

        await multi_mcp.connect()

        agent = Agent(
            name="Advanced MCP Agent",
            model=OpenAIChat(id="gpt-4o"),
            tools=[multi_mcp],
            instructions=dedent("""\
                You are an advanced AI assistant with multiple MCP capabilities.
                You can:
                - Access filesystem operations
                - Help with various tasks using available tools
                - Provide comprehensive assistance
            """),
            markdown=True,
        )

        await agent.aprint_response(
            "Show me the project structure and help me understand what this codebase does",
            stream=True
        )

        await multi_mcp.close()

    except Exception as e:
        print(f"❌ Error with advanced MCP: {e}")
        print("💡 Some MCP servers might not be available")


async def mcp_client_example():
    """Example of connecting to external MCP servers."""
    print("🔌 Running MCP Client Example")

    try:
        # Example: Connect to Agno's documentation MCP server
        async with MCPTools(
            transport="streamable-http",
            url="https://docs.agno.com/mcp",
            timeout_seconds=30
        ) as agno_mcp:

            agent = Agent(
                name="Agno Documentation Agent",
                model=OpenAIChat(id="gpt-4o-mini"),
                tools=[agno_mcp],
                instructions=dedent("""\
                    You are an AI assistant with access to Agno documentation.
                    Help users learn about Agno framework capabilities and usage.
                    Use the available tools to search and provide accurate information.
                """),
                markdown=True,
            )

            await agent.aprint_response(
                "What is Agno and what are its main features?",
                stream=True
            )

    except Exception as e:
        print(f"❌ Error connecting to external MCP server: {e}")
        print("💡 Check your internet connection and MCP server availability")


async def weather_mcp_example():
    """Example using the local weather MCP server from mcp-weather.py."""
    print("🌤️ Running Weather MCP Example")

    try:
        # Connect to the local weather MCP server via stdio
        async with MCPTools(
            "python mcp-weather.py",
            timeout_seconds=30
        ) as weather_mcp:

            agent = Agent(
                name="Weather Assistant",
                model=OpenAIChat(id="gpt-4o-mini"),
                tools=[weather_mcp],
                instructions=dedent("""\
                    You are a weather assistant with access to weather forecast data.
                    - Help users get weather information for specific locations
                    - Use the get_forecast tool to retrieve weather data
                    - Provide helpful and accurate weather information
                    - Ask for latitude and longitude if not provided
                """),
                markdown=True,
            )

            await agent.aprint_response(
                "What's the weather forecast for Beijing (latitude: 39.9042, longitude: 116.4074)?",
                stream=True
            )

    except Exception as e:
        print(f"❌ Error connecting to weather MCP server: {e}")
        print("💡 Make sure the weather MCP server is running:")
        print(f"   python mcp-weather.py")
        print(f"   Expected server at: http://{os.getenv('MCP_WEATHER_SERVER_HOST', 'localhost')}:{os.getenv('MCP_WEATHER_SERVER_PORT', '8000')}")


async def filesystem_mcp_example():
    """Example using the globally installed filesystem MCP server."""
    print("📁 Running Filesystem MCP Example")

    try:
        # Get filesystem root from environment
        filesystem_root = os.getenv("MCP_FILESYSTEM_ROOT", ".")

        # Use the globally installed filesystem MCP server
        async with MCPTools(
            command="mcp-server-filesystem",  # Global npm package command
            args=[filesystem_root],
            timeout_seconds=30
        ) as filesystem_mcp:

            agent = Agent(
                name="Filesystem Explorer",
                model=Claude(id="claude-sonnet-4-0"),
                tools=[filesystem_mcp],
                instructions=dedent(f"""\
                    You are a filesystem explorer with access to files and directories.
                    Root directory: {filesystem_root}

                    You can:
                    - List directory contents
                    - Read file contents
                    - Search for files
                    - Analyze project structure
                    - Provide insights about codebases

                    Be careful with file operations and always explain what you're doing.
                """),
                markdown=True,
            )

            await agent.aprint_response(
                "Please explore this project directory and give me an overview of what's here. What type of project is this and what are the main files?",
                stream=True
            )

    except Exception as e:
        print(f"❌ Error connecting to filesystem MCP server: {e}")
        print("💡 Make sure the filesystem MCP server is installed globally:")
        print("   npm install -g @modelcontextprotocol/server-filesystem")
        print("💡 Alternative: Use the npx version with --mcp flag")


async def default_agent_with_mcp():
    """Default agent with both weather and filesystem MCP servers."""
    print("🚀 Running Agent with MCP Servers (Weather + Filesystem)")

    try:
        # Get server configurations from environment
        filesystem_root = os.getenv("MCP_FILESYSTEM_ROOT", ".")

        print(f"🌤️ Connecting to weather MCP server via stdio (mcp-weather.py)")
        print(f"📁 Connecting to filesystem MCP server with root: {filesystem_root}")

        # Use MultiMCPTools to handle multiple MCP servers
        from agno.tools.mcp import MultiMCPTools

        multi_mcp = MultiMCPTools([
            "python mcp-weather.py",
            f"npx -y @modelcontextprotocol/server-filesystem {filesystem_root}",
        ])

        await multi_mcp.connect()

        agent = Agent(
            name="Multi-Tool Assistant",
            model=get_configured_model(),  # Use configured model
            tools=[multi_mcp],
            instructions=dedent("""\
                You are a helpful AI assistant with access to weather information and filesystem tools.

                🌤️ Weather capabilities:
                - Get current weather for any location
                - Provide weather forecasts

                📁 Filesystem capabilities:
                - Read and write files
                - List directory contents
                - Navigate the filesystem

                Be helpful, informative, and use emojis to make responses engaging.
                Always explain what tools you're using and why.
            """),
            markdown=True,
        )

        print("\n🤖 Agent ready! Available tools:")
        print("   🌤️ Weather information")
        print("   📁 Filesystem operations")

        # Interactive examples
        await agent.aprint_response(
            "Hello! Can you tell me what tools you have available and give me a quick demo by checking the weather in New York and listing the files in the current directory?",
            stream=False
        )

        await multi_mcp.close()

    except Exception as e:
        print(f"❌ Error running agent with MCP servers: {e}")
        print("\n💡 Troubleshooting:")
        print("1. Make sure mcp-weather.py is in the current directory")
        print("2. Make sure filesystem MCP is installed: npm install -g @modelcontextprotocol/server-filesystem")
        print("3. Check your environment configuration in env.py")
        print("4. Verify Python can execute: python mcp-weather.py")


def main():
    """Main function - runs agent with MCP servers by default."""
    print("🎉 Welcome to Agno Hello World!")
    print("=" * 50)

    # Run the default agent with MCP servers
    asyncio.run(default_agent_with_mcp())


if __name__ == "__main__":
    main()
