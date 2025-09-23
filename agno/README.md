# Agno Test Project

A comprehensive example demonstrating an Agno AI agent with integrated MCP (Model Context Protocol) servers for weather information and filesystem operations.

## 🚀 Features

- **🤖 AI Agent**: Powered by custom LLM provider (supports OpenAI-compatible APIs)
- **🌤️ Weather MCP**: Real-time weather information and forecasts
- **📁 Filesystem MCP**: File and directory operations
- **🔧 Custom Provider**: Configured for LLM provider API endpoint with claude-sonnet-4-20250514
- **🔗 Multi-Tool Integration**: Single agent with access to multiple MCP servers

## 📋 Prerequisites

1. **Python 3.8+**
2. **Node.js** (for MCP filesystem server via npx)
3. **API Keys**: LLM provider API keys configured in env.py
4. **FastMCP**: For weather MCP server functionality

## 🛠️ Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Ensure Node.js is available:**
   ```bash
   node --version
   npm --version
   ```
   The filesystem MCP server will be automatically installed via npx when needed.

3. **Configure environment:**
   - Copy `env.py.example` to `env.py`
   - Update API keys and configuration

## 🎯 Usage

### Quick Start
```bash
python helloworld.py
```

That's it! The agent will automatically start both MCP servers and demonstrate their capabilities.

### What You'll Get
The agent will connect to:
- 🌤️ **Weather MCP Server**: Automatically started via stdio (`python mcp-weather.py`)
- 📁 **Filesystem MCP Server**: Automatically started via npx (`npx @modelcontextprotocol/server-filesystem`)

### Example Interaction
The agent will automatically demonstrate both capabilities by:
- Checking weather in New York
- Listing files in the current directory
- Explaining available tools and features

## 🔧 Configuration

### Environment Variables

Key configuration options (see `env.py.example` for full details):

- `OPENAI_API_KEY`: Your LLM provider API key
- `OPENAI_API_BASE`: Custom API endpoint
- `OPENAI_MODEL_NAME`: Model name (e.g., "claude-sonnet-4-20250514")
- `MCP_FILESYSTEM_ROOT`: Root directory for filesystem operations (default: ".")
- `NO_PROXY`: Proxy bypass domains

### Supported Models

The agent supports any OpenAI-compatible API with various models:
- **Claude**: claude-sonnet-4-20250514, claude-3-opus
- **OpenAI**: gpt-4o, gpt-4o-mini, gpt-3.5-turbo
- **Custom**: Any model from your configured endpoint

## 🔍 MCP Server Details

### 🌤️ Weather MCP Server
- **File**: `mcp-weather.py`
- **Framework**: FastMCP
- **Transport**: stdio (command execution)
- **Command**: `python mcp-weather.py`
- **Function**: `get_forecast(lat, lon)` - Returns weather for coordinates
- **Example**: "晴, 25℃" for sunny, 25°C
- **Auto-start**: Started automatically by MultiMCPTools

### 📁 Filesystem MCP Server
- **Package**: `@modelcontextprotocol/server-filesystem`
- **Transport**: stdio (npx execution)
- **Command**: `npx -y @modelcontextprotocol/server-filesystem`
- **Root**: Configurable via `MCP_FILESYSTEM_ROOT` (default: current directory)
- **Auto-install**: Automatically installed via npx if not present
- **Capabilities**: Read/write files, list directories, file operations

## 🤝 Contributing

This project demonstrates Agno's MCP capabilities. You can:
- Add new MCP server integrations
- Enhance the weather service with more data
- Integrate additional LLM providers
- Improve error handling and logging

## 📚 Resources

- [Agno Documentation](https://docs.agno.com/)
- [Model Context Protocol](https://modelcontextprotocol.io/)
- [Agno GitHub Repository](https://github.com/agno-agi/agno)
- [FastMCP Documentation](https://github.com/jlowin/fastmcp)
