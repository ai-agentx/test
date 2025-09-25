# Pydantic AI + MCP Multi-Server Integration 🌤️📁

A comprehensive example demonstrating how to build sophisticated AI agents using Pydantic AI with multiple Model Context Protocol (MCP) servers for weather forecasting and filesystem operations.

## 🌟 Key Features

### **🤖 Intelligent Multi-Capability Agent**
- **Weather Operations**: Real-time forecast queries with coordinate-based lookup
- **Filesystem Operations**: File reading, writing, directory listing with detailed metadata
- **Combined Tasks**: Weather + file operations in single unified queries
- **Smart Routing**: Automatically determines appropriate tools for each task

### **🔧 Advanced MCP Integration**
- **Dual Server Architecture**:
  - 🐍 **Weather Server**: Python FastMCP server with async weather tools
  - 📁 **Filesystem Server**: Node.js @modelcontextprotocol server with full file operations
- **Stdio Transport**: Reliable process-based communication with both servers
- **Tool Prefixing**: Automatic conflict resolution (`weather_`, `fs_` prefixes)
- **Robust Connection Management**: Auto-start/stop with proper cleanup

### **📊 Enhanced Output & Details**
- **Structured Responses**: Type-safe `AssistantResponse` with task categorization
- **Rich File Information**: Actual filenames, sizes (B/KB/MB), file types with emojis
- **Detailed Results**: Comprehensive data in structured `detailed_results` field
- **Smart Formatting**: Auto-formatted output with clear sections and visual indicators

### **🛠️ Production-Ready Architecture**
- **Dependency Injection**: User context management with preferences
- **Custom Tools**: Weather advice and detailed file listing beyond MCP servers
- **Error Handling**: Comprehensive exception handling with debug traces
- **Environment Config**: Flexible API configuration supporting multiple LLM providers
- **Interactive & Batch Modes**: Both automated demos and real-time interaction

## 📋 Requirements

- Python 3.10+
- Node.js 18+ (for filesystem server)
- Dependencies listed in `requirements.txt`

## 🚀 Setup

1. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Install Node.js MCP filesystem server**:
   ```bash
   npm install -g @modelcontextprotocol/server-filesystem
   ```

3. **Configure environment** (optional):
   - The project includes `env.py` with your custom API configuration
   - Supports OpenAI-compatible APIs, Anthropic, Google, local LLMs, etc.

## 🎯 Usage

### 🚀 Quick Start Demo
Run the comprehensive demonstration with 6 predefined queries:
```bash
python helloworld.py
```

**Demo includes:**
- 🌤️ Weather queries for NYC, London coordinates
- 📁 File operations: listing, reading, creating files
- 🔄 Combined tasks: weather + file operations

### 💬 Interactive Mode
Start real-time interactive session:
```bash
python helloworld.py --interactive
```

## 🔗 Related Links

- [Pydantic AI Documentation](https://ai.pydantic.dev/)
- [Model Context Protocol](https://modelcontextprotocol.io/)
- [FastMCP Documentation](https://github.com/modelcontextprotocol/python-sdk)
- [Pydantic AI GitHub](https://github.com/pydantic/pydantic-ai)

## 📄 License

This example is provided as-is for educational purposes. Please refer to the respective licenses of Pydantic AI and other dependencies.
