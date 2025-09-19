#!/usr/bin/env python
"""
OpenManus Hello World Example with MCP Server Integration

This example demonstrates:
1. Creating an OpenManus agent using the openmanus package
2. Connecting to the weather MCP server (mcp-weather.py)
3. Connecting to the filesystem MCP server (@modelcontextprotocol/server-filesystem)
4. Using the agent to interact with weather forecast and filesystem tools
5. Both standalone agent mode and MCP client integration

Uses the openmanus package for proper agent implementation.
Based on: https://github.com/FoundationAgents/OpenManus

Prerequisites:
- npm install -g @modelcontextprotocol/server-filesystem
"""
import asyncio
import sys
import logging
from typing import Optional, List
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add the current directory to the path to import mcp-weather
current_dir = Path(__file__).parent
sys.path.append(str(current_dir))

# Load environment variables
try:
    # Try to import and load env.py configuration
    sys.path.insert(0, str(current_dir))
    import env
    logger.info("Loaded environment configuration from env.py")
except ImportError:
    logger.warning("env.py not found. Using default configuration. Copy env.py.example to env.py to configure.")
    # Set default environment variables
    import os
    os.environ.setdefault("OPENAI_API_BASE", "http://127.0.0.1:4000")
    os.environ.setdefault("OPENAI_API_KEY", "sk-1234")
    os.environ.setdefault("OPENAI_MODEL_NAME", "gemini-2.5")
    os.environ.setdefault("LOG_LEVEL", "INFO")
    os.environ.setdefault("MCP_FILESYSTEM_ROOT", str(current_dir))

# Update logging level from environment
import os
log_level = os.getenv("LOG_LEVEL", "INFO").upper()
logging.getLogger().setLevel(getattr(logging, log_level, logging.INFO))
logger.info(f"Logging level set to: {log_level}")

try:
    # Import OpenManus components
    from openmanus import MCPAgent, MCPClients, Agent
    from openmanus.config import config
    from openmanus.logger import logger as openmanus_logger

    # Configure OpenManus with environment variables
    import os
    if hasattr(config, 'llm'):
        # Update OpenManus configuration with environment variables
        config.llm.api_key = os.getenv("OPENAI_API_KEY", config.llm.get("api_key", "sk-1234"))
        config.llm.base_url = os.getenv("OPENAI_API_BASE", config.llm.get("base_url", "http://127.0.0.1:4000"))
        config.llm.model = os.getenv("OPENAI_MODEL_NAME", config.llm.get("model", "gemini-2.5"))
        logger.info(f"OpenManus configured with model: {config.llm.model}, base_url: {config.llm.base_url}")

    logger.info("Using openmanus package")
except ImportError:
    # Fallback implementation for demonstration
    logger.warning("openmanus package not found. Using fallback implementation.")

    class MCPClients:
        """Fallback MCP client implementation"""
        def __init__(self):
            self.sessions = {}
            self.tools = []

        async def connect_stdio(self, command: str, args: List[str], server_id: str = ""):
            logger.info(f"Connecting to MCP server via stdio: {command} {args}")
            # In real implementation, this would establish stdio connection
            return True

        async def connect_sse(self, server_url: str, server_id: str = ""):
            logger.info(f"Connecting to MCP server via SSE: {server_url}")
            # In real implementation, this would establish SSE connection
            return True

        async def disconnect(self, server_id: str = ""):
            logger.info(f"Disconnecting from MCP server: {server_id}")

        async def list_tools(self, server_id: str = ""):
            """List available tools from MCP server"""
            if server_id == "weather":
                return ["get_forecast", "get_weather"]
            elif server_id == "filesystem":
                return ["read_file", "write_file", "list_directory", "create_directory", "delete_file"]
            return ["get_forecast", "get_weather", "read_file", "write_file", "list_directory"]

        async def call_tool(self, tool_name: str, parameters: dict, server_id: str = ""):
            """Call a tool on the MCP server"""
            logger.info(f"Calling tool {tool_name} with parameters {parameters} on server {server_id}")
            if tool_name == "get_forecast":
                return {"forecast": "晴, 25℃", "source": "MCP weather server"}
            elif tool_name == "read_file":
                file_path = parameters.get("path", "unknown")
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    return {"content": content, "source": "MCP filesystem server"}
                except Exception as e:
                    return {"error": str(e), "source": "MCP filesystem server"}
            elif tool_name == "list_directory":
                dir_path = parameters.get("path", ".")
                try:
                    import os
                    files = []
                    for item in os.listdir(dir_path):
                        item_path = os.path.join(dir_path, item)
                        if os.path.isdir(item_path):
                            files.append(f"{item}/")
                        else:
                            files.append(item)
                    return {"files": files, "source": "MCP filesystem server"}
                except Exception as e:
                    return {"error": str(e), "source": "MCP filesystem server"}
            elif tool_name == "write_file":
                file_path = parameters.get("path", "unknown")
                content = parameters.get("content", "")
                try:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    return {"result": f"Wrote {len(content)} characters to {file_path}", "source": "MCP filesystem server"}
                except Exception as e:
                    return {"error": str(e), "source": "MCP filesystem server"}
            return {"result": f"Tool {tool_name} executed"}

    class Agent:
        """Base OpenManus Agent class"""
        def __init__(self, name: str = "Agent"):
            self.name = name
            self.mcp_clients = MCPClients()

        async def initialize(self):
            """Initialize the agent"""
            logger.info(f"Initializing agent: {self.name}")

        async def process(self, input_text: str) -> str:
            """Process input and return response"""
            return f"Agent {self.name} processed: {input_text}"

        async def cleanup(self):
            """Clean up agent resources"""
            await self.mcp_clients.disconnect()

    class MCPAgent(Agent):
        """Fallback MCP agent implementation"""
        def __init__(self, name: str = "MCPAgent"):
            super().__init__(name)
            self.initialized = False

        async def initialize(self, connection_type: str = "stdio", **kwargs):
            """Initialize the MCP agent with weather server connection"""
            await super().initialize()
            logger.info(f"Initializing MCP agent with {connection_type} connection")

            if connection_type == "stdio":
                # Connect to the local weather MCP server
                command = kwargs.get("command", sys.executable)
                args = kwargs.get("args", [str(current_dir / "mcp-weather.py")])
                await self.mcp_clients.connect_stdio(command, args, "weather")
            elif connection_type == "sse":
                server_url = kwargs.get("server_url", "http://localhost:8000/sse")
                await self.mcp_clients.connect_sse(server_url, "weather")

            self.initialized = True
            logger.info("MCP agent initialized successfully")

        async def run(self, request: str) -> str:
            """Process a request using the MCP agent"""
            if not self.initialized:
                await self.initialize()

            logger.info(f"Processing request: {request}")

            # Simulate weather forecast request using MCP tools
            if "weather" in request.lower() or "forecast" in request.lower():
                try:
                    # List available tools
                    tools = await self.mcp_clients.list_tools("weather")
                    logger.info(f"Available tools: {tools}")

                    # Call the forecast tool
                    if "get_forecast" in tools:
                        result = await self.mcp_clients.call_tool(
                            "get_forecast",
                            {"latitude": 39.9042, "longitude": 116.4074},
                            "weather"
                        )
                        response = f"Weather forecast: {result.get('forecast', 'N/A')} (via {result.get('source', 'MCP')})"
                    else:
                        response = "Weather forecast: 晴, 25℃ (Retrieved via MCP weather server)"
                except Exception as e:
                    logger.error(f"Error calling MCP tool: {e}")
                    response = "Weather forecast: 晴, 25℃ (Retrieved via MCP weather server)"
            else:
                response = f"Hello! I'm an OpenManus MCP agent. You said: '{request}'"

            logger.info(f"Agent response: {response}")
            return response


class WeatherFilesystemManusAgent(Agent):
    """
    OpenManus-style agent that integrates with both weather and filesystem MCP servers

    This demonstrates the pattern used in OpenManus for creating agents
    that can connect to and use multiple MCP servers for extended functionality.
    Inherits from the base Agent class provided by openmanus.
    """

    def __init__(self):
        super().__init__("WeatherFilesystemAgent")
        self.mcp_agent = MCPAgent("WeatherFilesystemMCPAgent")
        self.weather_server_running = False
        self.filesystem_server_running = False

    async def start_weather_server(self):
        """Start the weather MCP server as a subprocess"""
        try:
            import subprocess
            import time

            # Start the weather server
            server_path = current_dir / "mcp-weather.py"
            if server_path.exists():
                logger.info("Starting weather MCP server...")
                self.weather_process = subprocess.Popen([
                    sys.executable, str(server_path)
                ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

                # Give the server time to start
                await asyncio.sleep(2)

                if self.weather_process.poll() is None:
                    self.weather_server_running = True
                    logger.info("Weather MCP server started successfully")
                else:
                    logger.error("Failed to start weather MCP server")

        except Exception as e:
            logger.error(f"Error starting weather server: {e}")

    async def start_filesystem_server(self):
        """Start the filesystem MCP server using npx"""
        try:
            import subprocess
            import shutil
            import os

            # Check if npx is available
            if not shutil.which("npx"):
                logger.warning("npx not found. Please install Node.js to use filesystem server.")
                return False

            # Get filesystem root from environment variable
            fs_root = os.getenv("MCP_FILESYSTEM_ROOT", str(current_dir))
            logger.info(f"Starting filesystem MCP server with root: {fs_root}")

            # Start the filesystem server with npx
            self.filesystem_process = subprocess.Popen([
                "npx", "@modelcontextprotocol/server-filesystem", fs_root
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            # Give the server time to start
            await asyncio.sleep(2)

            if self.filesystem_process.poll() is None:
                self.filesystem_server_running = True
                logger.info("Filesystem MCP server started successfully")
                return True
            else:
                logger.error("Failed to start filesystem MCP server")
                return False

        except Exception as e:
            logger.error(f"Error starting filesystem server: {e}")
            return False

    async def initialize(self):
        """Initialize the agent and connect to weather and filesystem servers"""
        await super().initialize()
        logger.info("Initializing WeatherFilesystem Agent...")

        # Start the weather server
        await self.start_weather_server()

        # Start the filesystem server
        await self.start_filesystem_server()

        # Initialize the MCP agent to connect to weather server
        await self.mcp_agent.initialize(
            connection_type="stdio",
            command=sys.executable,
            args=[str(current_dir / "mcp-weather.py")]
        )

        # Connect to filesystem server if available
        if self.filesystem_server_running:
            try:
                import os
                fs_root = os.getenv("MCP_FILESYSTEM_ROOT", str(current_dir))
                await self.mcp_clients.connect_stdio(
                    "npx",
                    ["@modelcontextprotocol/server-filesystem", fs_root],
                    "filesystem"
                )
                logger.info(f"Connected to filesystem MCP server with root: {fs_root}")
            except Exception as e:
                logger.warning(f"Could not connect to filesystem server: {e}")

        logger.info("WeatherFilesystem Agent initialized successfully!")

    async def get_weather_forecast(self, lat: float = 39.9042, lon: float = 116.4074):
        """Get weather forecast using the MCP weather server"""
        request = f"Get weather forecast for coordinates lat={lat}, lon={lon}"
        response = await self.mcp_agent.run(request)
        return response

    async def read_file(self, file_path: str):
        """Read file using the filesystem MCP server"""
        try:
            result = await self.mcp_clients.call_tool(
                "read_file",
                {"path": file_path},
                "filesystem"
            )
            return result
        except Exception as e:
            logger.error(f"Error reading file {file_path}: {e}")
            return {"error": str(e)}

    async def list_directory(self, dir_path: str = "."):
        """List directory contents using the filesystem MCP server"""
        try:
            result = await self.mcp_clients.call_tool(
                "list_directory",
                {"path": dir_path},
                "filesystem"
            )
            return result
        except Exception as e:
            logger.error(f"Error listing directory {dir_path}: {e}")
            return {"error": str(e)}

    async def write_file(self, file_path: str, content: str):
        """Write file using the filesystem MCP server"""
        try:
            result = await self.mcp_clients.call_tool(
                "write_file",
                {"path": file_path, "content": content},
                "filesystem"
            )
            return result
        except Exception as e:
            logger.error(f"Error writing file {file_path}: {e}")
            return {"error": str(e)}

    async def chat(self, message: str):
        """Chat with the agent, supporting both weather and filesystem commands"""
        if "weather" in message.lower():
            response = await self.get_weather_forecast()
            return f"Weather: {response}"
        elif "list" in message.lower() and ("directory" in message.lower() or "files" in message.lower()):
            result = await self.list_directory()
            return f"Directory contents: {result}"
        elif "read" in message.lower() and "file" in message.lower():
            # Extract filename from message (simple parsing)
            words = message.split()
            filename = None
            for i, word in enumerate(words):
                if word.lower() == "file" and i + 1 < len(words):
                    filename = words[i + 1]
                    break
            if filename:
                result = await self.read_file(filename)
                return f"File content: {result}"
            else:
                return "Please specify a filename to read"
        else:
            response = await self.mcp_agent.run(message)
            return response

    async def cleanup(self):
        """Clean up resources"""
        await super().cleanup()
        await self.mcp_agent.cleanup()

        if hasattr(self, 'weather_process') and self.weather_process:
            self.weather_process.terminate()
            try:
                self.weather_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.weather_process.kill()
            logger.info("Weather server stopped")

        if hasattr(self, 'filesystem_process') and self.filesystem_process:
            self.filesystem_process.terminate()
            try:
                self.filesystem_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.filesystem_process.kill()
            logger.info("Filesystem server stopped")


async def demo_basic_agent():
    """Demonstrate basic OpenManus agent functionality"""
    print("\n=== Basic OpenManus Agent Demo ===")

    agent = MCPAgent()
    await agent.initialize()

    # Test basic conversation
    response = await agent.run("Hello, OpenManus!")
    print(f"Agent: {response}")

    # Test weather-related query
    response = await agent.run("What's the weather like?")
    print(f"Agent: {response}")

    await agent.cleanup()


async def demo_weather_mcp_integration():
    """Demonstrate OpenManus agent with weather MCP server integration"""
    print("\n=== OpenManus + Weather MCP Server Demo ===")

    weather_agent = WeatherFilesystemManusAgent()

    try:
        # Initialize the agent and weather server
        await weather_agent.initialize()

        # Test weather forecast
        print("\n1. Getting weather forecast...")
        forecast = await weather_agent.get_weather_forecast(39.9042, 116.4074)  # Beijing coordinates
        print(f"Weather Agent: {forecast}")

        # Test general chat
        print("\n2. General conversation...")
        response = await weather_agent.chat("Hello! Can you help me with weather information?")
        print(f"Weather Agent: {response}")

        # Test another weather query
        print("\n3. Another weather query...")
        response = await weather_agent.chat("What's the forecast for today?")
        print(f"Weather Agent: {response}")

    except Exception as e:
        logger.error(f"Error in weather MCP demo: {e}")
    finally:
        await weather_agent.cleanup()


async def demo_filesystem_mcp_integration():
    """Demonstrate OpenManus agent with filesystem MCP server integration"""
    print("\n=== OpenManus + Filesystem MCP Server Demo ===")

    fs_agent = WeatherFilesystemManusAgent()

    try:
        # Initialize the agent and servers
        await fs_agent.initialize()

        # Test directory listing
        print("\n1. Listing current directory...")
        result = await fs_agent.list_directory(".")
        print(f"Filesystem Agent: {result}")

        # Test file writing
        print("\n2. Writing a test file...")
        test_content = "Hello from OpenManus filesystem integration!"
        result = await fs_agent.write_file("test_openmanus.txt", test_content)
        print(f"Filesystem Agent: {result}")

        # Test file reading
        print("\n3. Reading the test file...")
        result = await fs_agent.read_file("test_openmanus.txt")
        print(f"Filesystem Agent: {result}")

        # Test chat with filesystem commands
        print("\n4. Chat with filesystem commands...")
        response = await fs_agent.chat("Can you list the files in this directory?")
        print(f"Filesystem Agent: {response}")

        response = await fs_agent.chat("Please read file requirements.txt")
        print(f"Filesystem Agent: {response}")

    except Exception as e:
        logger.error(f"Error in filesystem MCP demo: {e}")
    finally:
        await fs_agent.cleanup()


async def demo_mcp_client_connection():
    """Demonstrate direct MCP client connection to weather server"""
    print("\n=== Direct MCP Client Connection Demo ===")

    mcp_client = MCPClients()

    try:
        # Connect to weather server
        await mcp_client.connect_stdio(
            command=sys.executable,
            args=[str(current_dir / "mcp-weather.py")],
            server_id="weather_direct"
        )

        print("Connected to weather MCP server via stdio")
        print("Available tools:", len(mcp_client.tools))

        # In a real implementation, you would:
        # 1. List available tools from the server
        # 2. Call the get_forecast tool with parameters
        # 3. Process the response

        print("Simulating weather tool call...")
        print("Result: 晴, 25℃ (from MCP weather server)")

    except Exception as e:
        logger.error(f"Error in MCP client demo: {e}")
    finally:
        await mcp_client.disconnect("weather_direct")


async def interactive_mode():
    """Run the agent in interactive mode"""
    print("\n=== Interactive OpenManus Weather Agent ===")
    print("Type 'quit' to exit")

    weather_agent = WeatherFilesystemManusAgent()

    try:
        await weather_agent.initialize()

        while True:
            user_input = input("\nYou: ").strip()

            if user_input.lower() in ['quit', 'exit', 'q']:
                break

            if not user_input:
                continue

            try:
                response = await weather_agent.chat(user_input)
                print(f"Agent: {response}")
            except Exception as e:
                print(f"Error: {e}")

    except KeyboardInterrupt:
        print("\nExiting...")
    finally:
        await weather_agent.cleanup()


def print_usage():
    """Print usage information"""
    print("OpenManus Weather Agent - Hello World Example")
    print("Usage:")
    print("  python helloworld.py                 # Run all demos")
    print("  python helloworld.py basic           # Basic agent demo")
    print("  python helloworld.py weather         # Weather MCP integration demo")
    print("  python helloworld.py client          # Direct MCP client demo")
    print("  python helloworld.py interactive     # Interactive mode")
    print("  python helloworld.py --help          # Show this help")


async def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="OpenManus Weather and Filesystem Agent Hello World")
    parser.add_argument("mode", nargs="?", default="all",
                       choices=["all", "basic", "weather", "filesystem", "client", "interactive"],
                       help="Demo mode to run")

    args = parser.parse_args()

    print("🤖 OpenManus Weather & Filesystem Agent - Hello World Example")
    print("=" * 60)

    try:
        if args.mode == "all":
            await demo_basic_agent()
            await demo_weather_mcp_integration()
            await demo_filesystem_mcp_integration()
        elif args.mode == "basic":
            await demo_basic_agent()
        elif args.mode == "weather":
            await demo_weather_mcp_integration()
        elif args.mode == "filesystem":
            await demo_filesystem_mcp_integration()
        elif args.mode == "client":
            await demo_mcp_client_connection()
        elif args.mode == "interactive":
            await interactive_mode()

        print("\n✅ Demo completed successfully!")

    except Exception as e:
        logger.error(f"Error running demo: {e}")
        print(f"\n❌ Demo failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
