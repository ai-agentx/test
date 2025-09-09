
# CAMEL-AI + MCP Demo (Weather + Filesystem)

This project demonstrates how to use the [CAMEL-AI framework](https://github.com/camel-ai/camel) integrated with [Model Context Protocol (MCP)](https://spec.modelcontextprotocol.io/) servers, enabling agents to access both weather and filesystem capabilities.

## 🌟 Features

- Access weather and filesystem tools via MCP servers
- Compatible with OpenAI API, customizable model/API key/base URL
- Supports both async and sync run modes
- Multiple configuration options: environment variables, `env.py`, or command line
- Auto-detects npx/node and enables filesystem tools if available

## 🚀 Quick Start

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure environment

Recommended: copy the example config and fill in your OpenAI key and model name:

```bash
cp env.py.example env.py
# Edit env.py and set OPENAI_API_KEY and OPENAI_MODEL
```

Or set environment variables directly:

```bash
export OPENAI_API_KEY=your-key
export OPENAI_MODEL=gpt-4
```

### 3. Run the demo

```bash
python helloworld.py           # Async demo (recommended)
python helloworld.py --sync    # Sync demo
```

## 🛠️ Command Line Arguments

| Argument           | Description                          |
|--------------------|--------------------------------------|
| --sync             | Run synchronous version              |
| --create-env       | Generate env.py.example sample file  |
| --api-key KEY      | Specify OpenAI API Key               |
| --model MODEL      | Specify model name                   |
| --base-url URL     | Specify API Base URL                 |
| --model-family     | Specify model family (OPENAI, etc.)  |

## ⚙️ Environment Variables

- `OPENAI_API_KEY`      Required, your OpenAI API Key
- `OPENAI_MODEL`        Required, model name (e.g. gpt-4)
- `OPENAI_BASE_URL`     Optional, API endpoint, default https://api.openai.com/v1
- `OPENAI_MODEL_FAMILY` Optional, model family, default OPENAI

Three configuration options supported:
1. `env.py` file (recommended for development)
2. Environment variables (recommended for production)
3. Command line arguments (for temporary override)

## 🧩 MCP Server Integration

- Weather service: built-in Python implementation (`mcp-weather.py`)
- Filesystem service: auto-detects npx/node, prefers npx to launch official @modelcontextprotocol/server-filesystem
- Auto-generates `mcp_config.json` config file
- If node/npx not detected, only weather service is enabled

## 📝 Example Interactions

1. List files in the current directory and analyze their types
2. Read and summarize Python files in the directory
3. Query weather for specific coordinates (e.g. New York/Beijing)
4. Combined query: list files then get weather

## 🐍 Python Version Compatibility

- Recommended: Python 3.10-3.12
- 3.13 and above: not yet supported

## References

- [CAMEL-AI Documentation](https://docs.camel-ai.org/)
- [MCP Specification](https://spec.modelcontextprotocol.io/)
- [CAMEL Cookbook](https://docs.camel-ai.org/cookbooks/)
- [MCP Servers Registry](https://github.com/punkpeye/awesome-mcp-servers)

---

This project is for learning and research purposes only. Please refer to the respective open source licenses for CAMEL/MCP components.

## 📚 Additional Resources

- [CAMEL Documentation](https://docs.camel-ai.org/)
- [MCP Specification](https://spec.modelcontextprotocol.io/)
- [CAMEL Cookbook](https://docs.camel-ai.org/cookbooks/)
- [MCP Servers Registry](https://github.com/punkpeye/awesome-mcp-servers)

## 📄 License

This project is for educational purposes. Please refer to the respective licenses of CAMEL and MCP components.
