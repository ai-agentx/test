# Agent2Agent (A2A) Protocol Python Example

This project demonstrates how to implement the Agent2Agent (A2A) Protocol using Python. The A2A Protocol is an open standard developed by Google and donated to the Linux Foundation that enables seamless communication and collaboration between AI agents.

## What is A2A Protocol?

The Agent2Agent (A2A) Protocol is designed to enable:
- **Interoperability**: Connect agents built on different platforms (LangGraph, CrewAI, Semantic Kernel, custom solutions)
- **Complex Workflows**: Enable agents to delegate sub-tasks, exchange information, and coordinate actions
- **Secure & Opaque**: Agents interact without sharing internal memory, tools, or proprietary logic

## Features

- **LLM-Powered Agent**: Intelligent responses using OpenAI API or LiteLLM-compatible providers
- **Fallback Echo Mode**: Simple echo functionality when LLM is not available
- **A2A Compliant**: Follows the official A2A protocol specification
- **RESTful API**: HTTP-based communication using JSON-RPC
- **Agent Discovery**: Supports agent card discovery via well-known endpoints
- **Streaming Support**: Handles both synchronous and asynchronous message processing
- **Multi-Provider Support**: Works with OpenAI, Anthropic, Google, Azure, local models via LiteLLM
- **Conversation Context**: Maintains context across multi-turn conversations

## Quick Start

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure LLM**:
   ```bash
   # Copy the example environment file
   cp .env.example .env

   # Edit .env file with your configuration:
   OPENAI_API_BASE=http://localhost:4000
   OPENAI_API_KEY=your_api_key
   OPENAI_MODEL_NAME=claude-3-sonnet
   ```

3. **Start the Agent Server**:
   ```bash
   # With LLM (if configured)
   python examples/run_server.py

   # By default, if no --agent-type is set, the server runs all agents (Echo, LangGraph, CrewAI).
   # You can select a specific agent type using --agent-type:

   # Echo mode only
   python examples/run_server.py --no-llm

   # LangGraph agent (ReAct + tools)
   python examples/run_server.py --agent-type langgraph
   # or
   python examples/run_langgraph_server.py --agent-type langgraph

   # CrewAI agent (generalist assistant)
   python examples/run_server.py --agent-type crewai
   # or
   python examples/run_crewai_server.py

   # Note: All agent types are available; use --agent-type to select. For multi-agent endpoints, see advanced usage.
   ```

4. **Test with Client** (in another terminal):
   ```bash
   python examples/run_client.py --interactive
   ```

5. **Or run the complete demo**:
   ```bash
   python examples/demo.py
   ```

## Configuration

### Environment Setup

1. **Copy the example environment file:**
   ```bash
   cp .env.example .env
   ```

2. **Edit `.env` with your settings:**
   ```bash
   # Server Configuration
   A2A_HOST=localhost
   A2A_PORT=8080
   LOG_LEVEL=INFO

   # LLM Configuration
   OPENAI_API_BASE=http://localhost:4000
   OPENAI_API_KEY=your_api_key
   OPENAI_MODEL_NAME=claude-3-sonnet
   ```

3. **Available Environment Variables:**
   - `A2A_HOST`: Server host address (default: localhost)
   - `A2A_PORT`: Server port (default: 8080)
   - `LOG_LEVEL`: Logging level (DEBUG, INFO, WARNING, ERROR)
   - `CLIENT_TIMEOUT`: Client request timeout in seconds
   - `OPENAI_API_BASE`: Custom API endpoint (for LiteLLM, Azure, local models)
   - `OPENAI_API_KEY`: Your OpenAI API key or dummy key for LiteLLM
   - `OPENAI_MODEL_NAME`: Model name to use (default: gpt-3.5-turbo)

## Usage Examples

### Starting an Agent Server

```python
from src.agent.server import create_echo_agent_server

# Create and start the server with LLM support
server = create_echo_agent_server(host="localhost", port=8080, use_llm=True)
server.run()
```

### Client Interaction

```python
from src.client.client import A2AEchoClient

# Connect to agent and send message
client = A2AEchoClient("http://localhost:8080")
response = await client.send_message("Hello, Agent!")
print(response)
```

### LangGraph Agent

To run a LangGraph-powered agent that can call tools like currency conversion:

```bash
python examples/run_server.py --agent-type langgraph
```

### CrewAI Agent

To run a CrewAI-powered agent with a generalist assistant:

```bash
python examples/run_server.py --agent-type crewai
# or
python examples/run_crewai_server.py
```

## Agent Capabilities

The example agent supports:

### LLM Mode (when configured):
- **Intelligent Conversations**: Natural language understanding and generation
- **Question Answering**: Comprehensive responses to user queries
- **Task Assistance**: Help with various tasks and explanations
- **Context Awareness**: Maintains conversation context across turns
- **Multi-Provider Support**: OpenAI, Anthropic, Google, Azure, local models

### Echo Mode (fallback):
- **Text Processing**: Handles plain text messages
- **Echo Responses**: Returns processed versions of input messages
- **Pattern Recognition**: Special responses for greetings, help requests, questions

### Universal Features:
- **Agent Card**: Provides metadata about agent capabilities
- **Health Checks**: Standard A2A protocol health endpoints
- **A2A Compliance**: Full protocol implementation

## Protocol Details

This implementation follows the A2A Protocol specification:
- **Agent Cards**: JSON metadata describing agent capabilities
- **Message Format**: Standardized message structure with roles and parts
- **Task Management**: Asynchronous task handling and status tracking
- **Discovery**: Well-known endpoints for agent discovery

## References

- [A2A Protocol Official Documentation](https://a2a-protocol.org/latest/)
- [A2A Python SDK](https://github.com/a2aproject/a2a-python)
- [A2A Sample Projects](https://github.com/a2aproject/a2a-samples/)
- [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) - Complementary standard

## License

This project is licensed under the MIT License - see the LICENSE file for details.
