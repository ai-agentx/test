# CrewAI Hello World with MCP Integration

This project demonstrates CrewAI integration with MCP (Model Context Protocol) tools, showcasing how to build multi-agent systems that can access external services through standardized protocols.

## Features

🌤️ **Weather MCP Tool** - Get weather forecasts using MCP weather service  
📂 **Filesystem MCP Tools** - Read, write, and list files using MCP filesystem service  
🤖 **Multi-Tool Agent** - Single agent with access to multiple MCP tools  
🔄 **Complex Workflows** - Chained operations across different MCP services  
🛡️ **Enterprise Ready** - Proxy bypass, telemetry disabled, error handling

## Prerequisites

1. **Python 3.8+**
2. **CrewAI dependencies** (install with `pip install -r requirements.txt`)

## Setup

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure LLM API** (Pre-configured):

   **Windows PowerShell:**
   ```powershell
   $env:OPENAI_API_BASE="http://127.0.0.1:4000"
   $env:OPENAI_API_KEY="your-api-key"
   $env:OPENAI_MODEL_NAME="your-model-name"
   ```

   **Linux/Mac Bash:**
   ```bash
   export OPENAI_API_BASE="http://127.0.0.1:4000"
   export OPENAI_API_KEY="your-api-key"
   export OPENAI_MODEL_NAME="your-model-name"
   ```

3. **MCP Services Setup**:
   - `mcp-weather.py` - Weather MCP service (FastMCP implementation)
   - Filesystem MCP tools integrated directly in helloworld.py
   - No additional MCP server setup required for this demo

## Running

### Main MCP Multi-Tool Example
```bash
python helloworld.py
```

This will demonstrate:
1. 🌤️ **Weather Lookup** - Get weather for Beijing using MCP weather service
2. 📂 **Directory Listing** - List current directory contents
3. 📝 **File Creation** - Create weather report file
4. ✅ **File Verification** - Read back the created file

## Resources

- [CrewAI Documentation](https://docs.crewai.com/)
- [Model Context Protocol](https://modelcontextprotocol.io/)
- [FastMCP Documentation](https://github.com/jlowin/fastmcp)
- [CrewAI GitHub Repository](https://github.com/crewAIInc/crewAI)
- [LiteLLM Documentation](https://docs.litellm.ai/docs/)
- [MCP Filesystem Server](https://github.com/modelcontextprotocol/servers/tree/main/src/filesystem)

## License

This project is for educational purposes. Please refer to CrewAI's license for usage terms.
