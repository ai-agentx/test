# OpenManus Test Project

This project demonstrates the integration of OpenManus agents with MCP (Model Context Protocol) servers including weather and filesystem functionality.

## Requirements

- **Python Version**: Python 3.8 - 3.12 (required for `openmanus` package compatibility)
- **Node.js**: Required for filesystem MCP server (npm)
- **Git**: Required for installing OpenManus from GitHub

## Installation

1. Ensure you have Python 3.12 or lower installed:
   ```bash
   python --version
   ```

2. Install Node.js and npm (for filesystem server):
   ```bash
   # Install Node.js from https://nodejs.org/
   node --version
   npm --version
   ```

3. Install the filesystem MCP server:
   ```bash
   npm install -g @modelcontextprotocol/server-filesystem
   ```

4. Install the required Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

   **Note**: OpenManus is installed directly from GitHub since it's not yet available on PyPI.

## Usage

1. Copy the environment template:
   ```bash
   cp env.py.example env.py
   ```

2. Configure your environment variables in `env.py`:
   - `OPENAI_API_KEY`: Your OpenAI API key
   - `OPENAI_API_BASE`: API base URL (default: http://127.0.0.1:4000)
   - `OPENAI_MODEL_NAME`: Model name to use (default: gemini-2.5)
   - `MCP_FILESYSTEM_ROOT`: Root directory for filesystem server (default: current directory)
   - `LOG_LEVEL`: Logging level (default: INFO)

3. Run the demonstration:
   ```bash
   # Run all demos (weather + filesystem + MCP client)
   python helloworld.py

   # Run specific demos
   python helloworld.py weather        # Weather MCP server only
   python helloworld.py filesystem     # Filesystem MCP server only
   python helloworld.py basic          # Basic agent functionality
   python helloworld.py client         # Direct MCP client connection
   python helloworld.py interactive    # Interactive mode
   ```

## Demo Modes

- **all**: Runs all available demos (default)
- **basic**: Basic OpenManus agent functionality
- **weather**: Weather MCP server integration demo
- **filesystem**: Filesystem MCP server integration demo
- **client**: Direct MCP client connection demo
- **interactive**: Interactive chat mode

## Features

- OpenManus agent implementation using the `openmanus` package
- Weather MCP server integration (local Python server)
- Filesystem MCP server integration (Node.js package)
- Multiple MCP server connections from single agent
- Asynchronous communication between agent and multiple services
- File operations: read, write, list directories
- Weather forecasting capabilities
- Interactive chat mode with command recognition
- Demonstration of agent-to-server interactions

## Contributing

This is a test project for exploring OpenManus and MCP integration patterns.
