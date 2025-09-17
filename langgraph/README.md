# LangGraph Agent with MCP (Model Context Protocol) Integration

This project demonstrates a **production-ready** AI agent built with LangGraph and full MCP server integration. The implementation showcases multiple agent architectures, memory management, and comprehensive tool integration including weather forecasting and complete filesystem operations.

## � **Project Status: COMPLETE & WORKING**

✅ **All Features Implemented and Tested**
✅ **15 MCP Tools Successfully Integrated**
✅ **Network/Proxy Issues Resolved**
✅ **Production-Ready Configuration**

## �🌟 Features

- **Multiple Agent Architectures**: Simple ReAct agents, custom graphs, and MCP-enhanced agents
- **LangGraph Framework**: Built on LangGraph for stateful, multi-step agent workflows
- **Full MCP Protocol Support**: Dynamic tool discovery from multiple MCP servers
- **Weather Integration**: Real-time weather forecasting via custom MCP weather server
- **Complete Filesystem Operations**: 14 file tools via official MCP filesystem server
- **Memory Management**: Conversation state persistence with checkpointing
- **Corporate Network Support**: ZTE API integration with automatic proxy bypass
- **Environment Configuration**: Centralized config via `env.py` with custom API endpoints
- **Interactive CLI**: Command-line interface with demo and conversation modes
- **Streaming Support**: Real-time response streaming capabilities
- **Robust Error Handling**: Graceful fallbacks and comprehensive error management
- **Production Security**: Sandboxed filesystem access with proper validation

## 📋 Prerequisites

- Python 3.8+
- OpenAI API key (for OpenAI models) or custom API endpoint
- Node.js and npm (for filesystem MCP server)
- Optional: Custom MCP servers for additional tools

## 🚀 Quick Start

### 1. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 2. Install MCP Filesystem Server

```bash
npm install -g @modelcontextprotocol/server-filesystem
```

### 3. Configure Environment

Copy and customize the environment configuration:
```bash
cp env.py.example env.py
```

Edit `env.py` with your API credentials:
```python
import os
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

# OpenAI API Configuration
os.environ["OPENAI_API_BASE"] = os.getenv("OPENAI_API_BASE", "http://127.0.0.1:4000")
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY", "sk-1234")
os.environ["OPENAI_MODEL_NAME"] = os.getenv("OPENAI_MODEL_NAME", "gemini-2.5")

# Bypass proxy for OpenAI API domain
os.environ["NO_PROXY"] = ""
```

### 4. Run the LangGraph Agent

**Quick Demo** (shows all 15 tools working):
```bash
python helloworld.py --demo
```

**Interactive Mode** (MCP-enhanced agent with all tools):
```bash
python helloworld.py
```

**Different Agent Types**:
```bash
# Simple ReAct agent (basic tools only)
python helloworld.py --simple

# Custom agent graph
python helloworld.py --custom

# Force MCP-enhanced agent (default when MCP available)
python helloworld.py --mcp
```

## ✅ **Verified Working Examples**

### Weather Queries
```
Q: Get forecast for latitude 37.7749 and longitude -122.4194
A: The weather forecast for latitude 37.7749 and longitude -122.4194 (San Francisco, CA) is: **晴, 25℃** (Sunny, 25°C)
```

### File Operations
```
Q: List the files in the current directory
A: [Lists all files with [FILE] and [DIR] prefixes]

Q: Read the contents of README.md
A: [Returns complete file contents]

Q: Create a new file called test.txt with some content
A: [Creates file and confirms success]
```

### Mathematical Operations
```
Q: Calculate 15 * 23 + 7
A: The result of 15 * 23 + 7 is **352**.
```

## 📚 Learn More

- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [LangChain Documentation](https://python.langchain.com/)
- [Model Context Protocol (MCP)](https://modelcontextprotocol.io/)
- [MCP Filesystem Server](https://github.com/modelcontextprotocol/server-filesystem)
- [FastMCP Documentation](https://github.com/jlowin/fastmcp)
- [LangGraph Agent Examples](https://github.com/langchain-ai/langgraph/tree/main/examples)

## 🤝 Contributing

Feel free to submit issues and enhancement requests!

## 📄 License

This project is open source and available under the [MIT License](LICENSE).
