#!/usr/bin/env python3
"""
CrewAI Hello World Example with MCP Weather and Filesystem Tools

This example demonstrates a simplified crew with one agent that uses
multiple MCP (Model Context Protocol) tools:
- Weather tool for getting weather forecasts
- Filesystem tools for reading, writing, and listing files

The agent will get weather information and save it to a file using MCP services.
"""

import env
import os

# Disable CrewAI telemetry before importing CrewAI modules
os.environ["OTEL_SDK_DISABLED"] = "true"
os.environ["CREWAI_TELEMETRY_DISABLED"] = "true"

from crewai import Agent, Crew, Task, Process, LLM
from crewai.tools import BaseTool
from typing import Type, Optional
from pydantic import BaseModel, Field
import json
import subprocess


class WeatherInput(BaseModel):
    """Input schema for weather tool"""
    lat: float = Field(description="Latitude coordinate")
    lon: float = Field(description="Longitude coordinate")


class FilesystemReadInput(BaseModel):
    """Input schema for filesystem read tool"""
    path: str = Field(description="File path to read")


class FilesystemWriteInput(BaseModel):
    """Input schema for filesystem write tool"""
    path: str = Field(description="File path to write")
    content: str = Field(description="Content to write to file")


class FilesystemListInput(BaseModel):
    """Input schema for filesystem list tool"""
    path: str = Field(description="Directory path to list", default=".")


class MCPFilesystemTool(BaseTool):
    """Filesystem tool using MCP filesystem service"""
    name: str = "filesystem_operations"
    description: str = "Read, write, and list files and directories using MCP filesystem service"

    def _run(self, operation: str, path: str, content: str = None) -> str:
        """Perform filesystem operations"""
        try:
            if operation == "read":
                return self._read_file(path)
            elif operation == "write":
                return self._write_file(path, content)
            elif operation == "list":
                return self._list_directory(path)
            else:
                return f"Unknown operation: {operation}"
        except Exception as e:
            return f"Filesystem operation error: {str(e)}"

    def _read_file(self, path: str) -> str:
        """Read file content using MCP filesystem service"""
        try:
            # In a real MCP implementation, this would call the MCP filesystem server
            # For now, we'll use direct file operations
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            return f"File content from {path}:\n{content}"
        except Exception as e:
            return f"Error reading file {path}: {str(e)}"

    def _write_file(self, path: str, content: str) -> str:
        """Write content to file using MCP filesystem service"""
        try:
            # In a real MCP implementation, this would call the MCP filesystem server
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
            return f"Successfully wrote content to {path}"
        except Exception as e:
            return f"Error writing file {path}: {str(e)}"

    def _list_directory(self, path: str) -> str:
        """List directory contents using MCP filesystem service"""
        try:
            import os
            items = os.listdir(path)
            items_info = []
            for item in items:
                item_path = os.path.join(path, item)
                item_type = "directory" if os.path.isdir(item_path) else "file"
                items_info.append(f"{item} ({item_type})")

            return f"Contents of {path}:\n" + "\n".join(items_info)
        except Exception as e:
            return f"Error listing directory {path}: {str(e)}"


class MCPFilesystemReadTool(BaseTool):
    """Read files using MCP filesystem service"""
    name: str = "read_file"
    description: str = "Read content from a file using MCP filesystem service"
    args_schema: Type[BaseModel] = FilesystemReadInput

    def _run(self, path: str) -> str:
        """Read file content"""
        fs_tool = MCPFilesystemTool()
        return fs_tool._read_file(path)


class MCPFilesystemWriteTool(BaseTool):
    """Write files using MCP filesystem service"""
    name: str = "write_file"
    description: str = "Write content to a file using MCP filesystem service"
    args_schema: Type[BaseModel] = FilesystemWriteInput

    def _run(self, path: str, content: str) -> str:
        """Write content to file"""
        fs_tool = MCPFilesystemTool()
        return fs_tool._write_file(path, content)


class MCPFilesystemListTool(BaseTool):
    """List directory contents using MCP filesystem service"""
    name: str = "list_directory"
    description: str = "List contents of a directory using MCP filesystem service"
    args_schema: Type[BaseModel] = FilesystemListInput

    def _run(self, path: str = ".") -> str:
        """List directory contents"""
        fs_tool = MCPFilesystemTool()
        return fs_tool._list_directory(path)


class MCPWeatherTool(BaseTool):
    """Weather tool using MCP weather service from mcp-weather.py"""
    name: str = "get_weather"
    description: str = "Get weather forecast for given coordinates (latitude, longitude) using MCP weather service"
    args_schema: Type[BaseModel] = WeatherInput

    def _call_mcp_weather(self, lat: float, lon: float) -> str:
        """Call the MCP weather service from mcp-weather.py"""
        try:
            # Import the weather function from mcp-weather.py
            # Since mcp-weather.py uses FastMCP, we'll extract the core logic
            import sys
            import os

            # Add current directory to path to import mcp-weather
            current_dir = os.path.dirname(os.path.abspath(__file__))
            if current_dir not in sys.path:
                sys.path.insert(0, current_dir)

            # For now, we'll use the same logic as the MCP service
            # In a real implementation, you'd use MCP client-server communication
            result = "晴, 25℃"  # This matches the mcp-weather.py get_forecast function

            return result

        except Exception as e:
            return f"Error calling MCP weather service: {str(e)}"

    def _run(self, lat: float, lon: float) -> str:
        """Get weather forecast from MCP weather service"""
        try:
            # Call the MCP weather service
            weather_result = self._call_mcp_weather(lat, lon)

            return f"MCP Weather Service Report for coordinates ({lat}, {lon}): {weather_result}"

        except Exception as e:
            return f"Error getting weather data: {str(e)}"


def setup_environment():
    """Setup environment variables for API connection"""
    # Disable proxy settings
    os.environ["HTTP_PROXY"] = ""
    os.environ["HTTPS_PROXY"] = ""
    os.environ["http_proxy"] = ""
    os.environ["https_proxy"] = ""
    os.environ["NO_PROXY"] = "*"

    # Get the configuration from environment (set by env.py)
    base_url = os.environ.get("OPENAI_API_BASE")
    api_key = os.environ.get("OPENAI_API_KEY")
    model = os.environ.get("OPENAI_MODEL_NAME")

    # Create a custom LLM instance
    custom_llm = LLM(
        model=f"openai/{model}",  # Add openai/ prefix for LiteLLM
        api_key=api_key,
        base_url=base_url,
        temperature=0.7
    )

    return custom_llm


def create_multi_tool_agent(llm):
    """Create an agent with both weather and filesystem MCP tools"""
    weather_tool = MCPWeatherTool()
    fs_read_tool = MCPFilesystemReadTool()
    fs_write_tool = MCPFilesystemWriteTool()
    fs_list_tool = MCPFilesystemListTool()

    return Agent(
        role='Multi-Tool Assistant',
        goal='Provide weather information and perform filesystem operations using MCP services',
        backstory="""You are a helpful assistant with access to both weather data and filesystem operations
        through MCP (Model Context Protocol) services. You can:
        - Get weather forecasts for any location given coordinates
        - Read, write, and list files and directories
        Always be friendly and provide useful information with clear explanations.""",
        verbose=True,
        allow_delegation=False,
        llm=llm,
        tools=[weather_tool, fs_read_tool, fs_write_tool, fs_list_tool]
    )


def create_multi_tool_task(agent):
    """Create a task that uses both weather and filesystem tools"""
    return Task(
        description="""Complete the following multi-step task:

        1. Get the weather forecast for Beijing, China (coordinates: 39.9042° N, 116.4074° E)
        2. List the contents of the current directory to see what files are available
        3. Create a weather report file called 'beijing_weather_report.txt' with the weather information
        4. Read the file back to confirm it was created successfully

        Provide a comprehensive summary of all operations performed.""",
        expected_output="""A detailed report including:
        - Weather forecast for Beijing
        - List of files in current directory
        - Confirmation of weather report file creation
        - Content verification of the created file""",
        agent=agent
    )


def main():
    """
    Main function to run the multi-tool MCP crew
    """
    print("🚀 Starting CrewAI Multi-Tool MCP Example")
    print("=" * 50)

    try:
        # Setup environment and LLM
        print("🔧 Setting up environment...")
        custom_llm = setup_environment()

        # Create agent and task
        print("👤 Creating multi-tool agent...")
        multi_agent = create_multi_tool_agent(custom_llm)

        print("📋 Creating multi-tool task...")
        multi_task = create_multi_tool_task(multi_agent)

        # Create and run the crew
        print("🚀 Creating crew...")
        crew = Crew(
            agents=[multi_agent],
            tasks=[multi_task],
            process=Process.sequential,
            verbose=True,
        )

        print("\n🛠️  Executing multi-tool operations...")
        print("=" * 50)

        result = crew.kickoff()

        print("\n" + "=" * 50)
        print("✅ Multi-tool crew execution completed successfully!")
        print("=" * 50)
        print("\n📝 Final Report:")
        print("-" * 30)
        print(result)

    except Exception as e:
        error_str = str(e)
        print(f"\n❌ Error occurred: {error_str}")
        print(f"\n🐛 Full Error Details:")
        print("-" * 20)
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
