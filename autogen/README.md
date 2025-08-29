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

3. Set up environment (choose one method):

**Method 1: Using env.py file (recommended for development)**
```bash
cp env.py.example env.py
```

Edit `env.py` with your settings:
```python
import os

os.environ["OPENAI_API_BASE"] = "http://127.0.0.1:4000"
os.environ["OPENAI_API_KEY"] = "sk-1234"
os.environ["OPENAI_MODEL"] = "gemini-2.5"
os.environ["OPENAI_MODEL_FAMILY"] = "GEMINI"
```

**Method 2: Using export commands (recommended for production/Ubuntu)**
```bash
export OPENAI_API_KEY="sk-1234"
export OPENAI_MODEL="gemini-2.5"
export OPENAI_API_BASE="http://127.0.0.1:4000"  # Optional, defaults to OpenAI API
export OPENAI_MODEL_FAMILY="GEMINI"  # Optional, defaults to UNKNOWN
```

### Model Family Configuration

The `OPENAI_MODEL_FAMILY` environment variable specifies the model family for proper handling of different AI models. Supported values include:

- `"OPENAI"` - For OpenAI models (GPT-3.5, GPT-4, GPT-4o, etc.)
- `"GEMINI"` - For Google Gemini models
- `"CLAUDE"` - For Anthropic Claude models
- `"R1"` - For DeepSeek R1 reasoning models
- `"UNKNOWN"` - For unrecognized or custom models (default fallback)

This setting ensures proper token counting, cost estimation, and model-specific behavior handling.

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
   - Ensure `OPENAI_MODEL_FAMILY` matches your model type:
     - `"OPENAI"` for GPT models (gpt-3.5-turbo, gpt-4, gpt-4o, etc.)
     - `"GEMINI"` for Google Gemini models (gemini-1.5-pro, gemini-2.0-flash, etc.)
     - `"CLAUDE"` for Anthropic Claude models (claude-3-5-sonnet, claude-3-haiku, etc.)
     - `"R1"` for DeepSeek R1 reasoning models
     - `"UNKNOWN"` for custom or unrecognized models

4. If you're using custom API endpoints or non-OpenAI models:
   - Set the correct `OPENAI_MODEL_FAMILY` value as listed above
   - Verify your API base URL is correct
   - Ensure the model name matches what your API endpoint expects
   - For proxy services like litellm, use the base model family (e.g., "GEMINI" for "vercel-gemini-2.5-pro")

4. If filesystem tools don't work:
   - Verify the current directory permissions
   - Check if the filesystem MCP server has proper access to the directory

5. If weather tools fail:
   - Ensure Python can execute the weather MCP server script
   - Verify the relative path to `mcp-weather.py` is correct
