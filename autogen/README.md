# AutoGen Examples

Welcome to the AutoGen examples! This directory contains ready-to-run examples demonstrating how to use Microsoft AutoGen for building powerful multi-agent systems.

## ⚡ Quick Start (5-Minute Setup)

Let's create your first AutoGen multi-agent system! We'll start with a simple example and then explore more advanced scenarios.

1. Install dependencies:
```bash
cd autogen
pip install -r requirements.txt
```

2. Install Node.js MCP filesystem server:
```bash
npm install -g @modelcontextprotocol/server-filesystem
```

3. Set up environment:
```bash
cp env.py.example env.py
```

Edit `env.py` with your settings:
```python
import os

os.environ["OPENAI_API_BASE"] = "https://api.openai.com/v1"
os.environ["OPENAI_API_KEY"] = "your-api-key-here"
os.environ["OPENAI_MODEL"] = "gpt-4o"
os.environ["OPENAI_MODEL_FAMILY"] = "openai"
```

4. Run the MCP-enabled agent:
```bash
python helloworld.py
```

## 🚀 Available Example

`helloworld.py` - MCP-enabled agent with filesystem and weather tools
- Demonstrates proper MCP server integration using openai-agents framework
- Tests filesystem tools (list files, read directories) and weather forecasting
- Shows clean output without SSL tracing noise
- Runs specific demo tasks and exits (non-interactive)
- Perfectexample of connecting external tools to AI agents via MCP

## 💡 Key Features

- **MCP Server Integration**: Connect external tools via Model Context Protocol
- **Filesystem Access**: Read files, list directories, and analyze file contents
- **Weather Information**: Get weather forecasts for any location
- **Clean Agent Framework**: Uses openai-agents for proper MCP integration
- **Flexible Configuration**: Environment-based model and API configuration
- **Multi-Model Support**: Works with OpenAI, Claude, and other model families
- **Error Recovery**: Built-in error handling and clean output

## 🤝 Next Steps
- Run `helloworld.py` to see MCP integration in action
- Modify the `env.py` file to test different models and APIs
- Read the comments in the example for detailed explanations
- Explore the [openai-agents documentation](https://github.com/openai/openai-agents-python) for advanced MCP usage
- Check out the [AutoGen documentation](https://microsoft.github.io/autogen/stable/reference/index.html) for more details
- Try creating your own MCP servers for custom tool integration

## 📚 Additional Resources

- [AutoGen GitHub Repository](https://github.com/microsoft/autogen)
- [AutoGen Official Documentation](https://microsoft.github.io/autogen/stable/reference/index.html)

## 🛠️ Troubleshooting

1. If you see API key errors:
   - Check if your API key is correctly set in `env.py`
   - Verify your API key has sufficient credits

2. If MCP server connection fails:
   - Ensure Node.js is installed: `node --version`
   - Verify filesystem server is installed: `npm list -g @modelcontextprotocol/server-filesystem`
   - Check that the weather MCP server is available in `../openai-agents/mcp-weather.py`

3. For model-specific errors:
   - Try using a different model from your config list
   - Check if your API key has access to the requested model
   - Ensure `OPENAI_MODEL_FAMILY` matches your model type (e.g., "openai" for GPT models, "claude" for Claude models)

4. If you're using custom API endpoints or non-OpenAI models:
   - Set the correct `OPENAI_MODEL_FAMILY` value ("claude", "anthropic", "openai", etc.)
   - Verify your API base URL is correct
   - Ensure the model name matches what your API endpoint expects

4. If filesystem tools don't work:
   - Verify the current directory permissions
   - Check if the filesystem MCP server has proper access to the directory

5. If weather tools fail:
   - Ensure Python can execute the weather MCP server script
   - Verify the relative path to `mcp-weather.py` is correct
