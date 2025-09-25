"""
Pydantic AI Hello World Example with MCP Weather Server Integration

This example demonstrates:
1. A Pydantic AI agent that can use the weather MCP server
2. Integration with the mcp-weather.py server
3. Basic agent functionality with tools and structured output
"""
import asyncio
import os
from typing import Annotated

from pydantic import BaseModel, Field
from pydantic_ai import Agent, RunContext
from pydantic_ai.mcp import MCPServerStdio
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider

# Load environment variables if available
try:
    from env import *  # This will load the environment configuration
except ImportError:
    # Fallback to defaults if env.py doesn't exist
    os.environ.setdefault("OPENAI_API_BASE", "http://127.0.0.1:4000")
    os.environ.setdefault("OPENAI_API_KEY", "sk-1234")
    os.environ.setdefault("OPENAI_MODEL_NAME", "gemini-2.5")


class AssistantResponse(BaseModel):
    """Structured output for assistant responses"""
    task_type: str = Field(description="Type of task performed (weather, filesystem, combined)")
    location: str = Field(default="", description="Location for weather queries")
    forecast: str = Field(default="", description="Weather forecast if applicable")
    temperature: str = Field(default="", description="Temperature if applicable")
    file_operations: str = Field(default="", description="Description of file operations performed")
    detailed_results: str = Field(default="", description="Detailed results like file contents or file lists")
    summary: str = Field(description="A brief summary of what was accomplished")


class UserContext:
    """User context for dependency injection"""
    def __init__(self, user_id: str = "default", preferred_units: str = "celsius"):
        self.user_id = user_id
        self.preferred_units = preferred_units


# Create the custom OpenAI-compatible model
def create_model():
    """Create a custom OpenAI-compatible model using environment settings"""
    api_base = os.environ.get("OPENAI_API_BASE", "http://127.0.0.1:4000")
    api_key = os.environ.get("OPENAI_API_KEY", "sk-1234")
    model_name = os.environ.get("OPENAI_MODEL_NAME", "gemini-2.5")

    # Create custom OpenAI provider with custom base URL
    provider = OpenAIProvider(
        api_key=api_key,
        base_url=api_base
    )

    # Create the model
    return OpenAIChatModel(
        model_name=model_name,
        provider=provider
    )

# Create the MCP weather server connection
weather_server = MCPServerStdio(
    'python',
    ['mcp-weather.py'],
    tool_prefix='weather',
    timeout=10,  # Increase timeout for server startup
)

# Create the MCP filesystem server connection
# Note: Requires 'npm install -g @modelcontextprotocol/server-filesystem'
filesystem_server = MCPServerStdio(
    'npx',
    ['@modelcontextprotocol/server-filesystem', '.'],  # '.' means current directory as root
    tool_prefix='fs',
    timeout=15,  # Filesystem server might take longer to start
)

# Create the main agent with weather and filesystem capabilities
weather_agent = Agent(
    model=create_model(),
    deps_type=UserContext,
    output_type=AssistantResponse,
    system_prompt="""
    You are a helpful assistant with weather and file system capabilities.

    For weather queries:
    - Use the available weather tools to get forecast information
    - Provide clear, friendly responses about weather conditions
    - Always include the temperature and a brief summary in your response

    For file operations:
    - You can read, write, and manage files in the current directory
    - When listing files, include the actual filenames in the detailed_results field
    - When reading files, include key excerpts or summaries in detailed_results
    - When creating files, mention the filename and content summary
    - Be careful with file operations and always confirm before making changes

    IMPORTANT: Always populate the detailed_results field with specific information:
    - For file listings: include actual filenames
    - For file reading: include content snippets or key information
    - For weather: include specific temperature and forecast details
    - For combined tasks: include results from both operations
    """,
    toolsets=[weather_server, filesystem_server]
)

# Add custom instructions that use dependency injection
@weather_agent.instructions
async def add_user_context(ctx: RunContext[UserContext]) -> str:
    return f"User ID: {ctx.deps.user_id}, preferred units: {ctx.deps.preferred_units}"


# Custom tool for the agent (example of adding tools beyond MCP)
@weather_agent.tool
async def get_weather_advice(
    ctx: RunContext[UserContext],
    temperature: Annotated[str, "Temperature reading like '25℃' or '77°F'"]
) -> str:
    """Provide clothing advice based on temperature"""
    # Simple temperature advice logic
    temp_num = float(temperature.replace('℃', '').replace('°F', '').replace('°C', ''))

    if '℃' in temperature or '°C' in temperature:
        if temp_num > 25:
            return "It's warm! Light clothing recommended - t-shirt and shorts."
        elif temp_num > 15:
            return "Pleasant weather! Light jacket or sweater should be perfect."
        elif temp_num > 5:
            return "Cool weather. Wear a warm jacket and long pants."
        else:
            return "Cold weather! Bundle up with a heavy coat, hat, and gloves."
    else:  # Fahrenheit
        if temp_num > 77:
            return "It's warm! Light clothing recommended - t-shirt and shorts."
        elif temp_num > 59:
            return "Pleasant weather! Light jacket or sweater should be perfect."
        elif temp_num > 41:
            return "Cool weather. Wear a warm jacket and long pants."
        else:
            return "Cold weather! Bundle up with a heavy coat, hat, and gloves."


# Custom tool to supplement MCP filesystem server with detailed file info
@weather_agent.tool
async def get_detailed_file_list(
    ctx: RunContext[UserContext],
    directory: Annotated[str, "Directory path to list (default: current directory)"] = "."
) -> str:
    """Get a detailed list of files and directories with sizes and types"""
    import os
    from pathlib import Path

    try:
        path = Path(directory)
        if not path.exists():
            return f"Directory '{directory}' does not exist"

        items = []
        for item in sorted(path.iterdir()):
            try:
                if item.is_file():
                    size = item.stat().st_size
                    if size < 1024:
                        size_str = f"{size}B"
                    elif size < 1024*1024:
                        size_str = f"{size//1024}KB"
                    else:
                        size_str = f"{size//(1024*1024)}MB"
                    items.append(f"📄 {item.name} ({size_str})")
                elif item.is_dir():
                    items.append(f"📁 {item.name}/")
                else:
                    items.append(f"🔗 {item.name} (link)")
            except (OSError, PermissionError):
                items.append(f"❓ {item.name} (no access)")

        if not items:
            return f"Directory '{directory}' is empty"

        return f"Contents of '{directory}':\n" + "\n".join(items)

    except Exception as e:
        return f"Error listing directory '{directory}': {e}"


async def main():
    """Main function demonstrating the weather and filesystem agent"""
    print("🌤️  Pydantic AI Weather & Filesystem Assistant")
    print("=" * 60)

    print("📋 This demo requires:")
    print("   1. Python with mcp-weather.py working")
    print("   2. Node.js with: npm install -g @modelcontextprotocol/server-filesystem")
    print("   3. Or install both servers and try the demo")

    # Create user context
    user_context = UserContext(user_id="demo_user", preferred_units="celsius")

    # Example queries to demonstrate both weather and filesystem capabilities
    queries = [
        # Weather queries
        "What's the weather forecast for coordinates 40.7128, -74.0060? Include specific temperature and conditions in detailed_results.",
        "Can you check the weather at latitude 51.5074 and longitude -0.1278?",

        # Filesystem queries
        "Can you list the files in the current directory? Show me the actual filenames and sizes in detailed_results.",
        "Read the contents of README.md if it exists and show key sections in detailed_results",
        "Create a simple text file called 'weather_log.txt' with today's date and a sample weather entry",

        # Combined queries
        "Get me the forecast for location 35.6762, 139.6503, give me clothing advice, and save this info to a file called 'tokyo_weather.txt'"
    ]

    # Use the agent within an async context manager to handle MCP server connections
    print(f"\n🚀 Starting assistant with {len(queries)} queries (weather + filesystem)...")
    async with weather_agent:
        for i, query in enumerate(queries, 1):
            print(f"\n📍 Query {i}: {query}")
            print("-" * 40)

            try:
                # Run the agent with the query and user context
                result = await weather_agent.run(query, deps=user_context)

                # Display the structured output
                print(f"🔧 Task Type: {result.output.task_type}")
                if result.output.location:
                    print(f"📍 Location: {result.output.location}")
                if result.output.temperature:
                    print(f"🌡️  Temperature: {result.output.temperature}")
                if result.output.forecast:
                    print(f"🌤️  Forecast: {result.output.forecast}")
                if result.output.file_operations:
                    print(f"📁 File Operations: {result.output.file_operations}")
                if result.output.detailed_results:
                    print(f"📋 Details:")
                    # Format detailed results nicely
                    details = result.output.detailed_results.strip()
                    if details:
                        for line in details.split('\n'):
                            if line.strip():
                                print(f"   {line}")
                print(f"📝 Summary: {result.output.summary}")

            except Exception as e:
                print(f"❌ Error: {e}")
                import traceback
                print("   Full error trace:")
                traceback.print_exc()


async def interactive_mode():
    """Interactive mode for testing the agent with weather and filesystem capabilities"""
    print("🌤️  Interactive Weather & Filesystem Assistant")
    print("=" * 60)
    print("Available capabilities:")
    print("  📍 Weather: Enter coordinates (lat, lon) - Example: 40.7128, -74.0060")
    print("  📁 Files: Ask about files - Example: 'list files' or 'read README.md'")
    print("  🔄 Combined: Mix both - Example: 'get weather for NYC and save to file'")
    print("  ⌨️  Type 'quit' to exit")
    print()

    user_context = UserContext(user_id="interactive_user", preferred_units="celsius")

    async with weather_agent:
        while True:
            try:
                user_input = input("🌍 Enter coordinates or query: ").strip()

                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("👋 Goodbye!")
                    break

                if not user_input:
                    continue

                # Try to parse as coordinates
                if ',' in user_input:
                    try:
                        parts = user_input.split(',')
                        if len(parts) == 2:
                            lat = float(parts[0].strip())
                            lon = float(parts[1].strip())
                            query = f"What's the weather forecast for coordinates {lat}, {lon}? Also provide clothing advice."
                        else:
                            query = user_input
                    except ValueError:
                        query = user_input
                else:
                    query = user_input

                print(f"\n🔍 Processing: {query}")
                print("-" * 40)

                result = await weather_agent.run(query, deps=user_context)

                print(f"🔧 Task Type: {result.output.task_type}")
                if result.output.location:
                    print(f"📍 Location: {result.output.location}")
                if result.output.temperature:
                    print(f"🌡️  Temperature: {result.output.temperature}")
                if result.output.forecast:
                    print(f"🌤️  Forecast: {result.output.forecast}")
                if result.output.file_operations:
                    print(f"📁 File Operations: {result.output.file_operations}")
                if result.output.detailed_results:
                    print(f"📋 Details:")
                    # Format detailed results nicely
                    details = result.output.detailed_results.strip()
                    if details:
                        for line in details.split('\n'):
                            if line.strip():
                                print(f"   {line}")
                print(f"📝 Summary: {result.output.summary}")
                print()

            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
                print("   Please try again or check your input format")
                print()


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--interactive":
        asyncio.run(interactive_mode())
    else:
        asyncio.run(main())
