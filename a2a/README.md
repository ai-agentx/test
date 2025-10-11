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

2. **Configure LLM (Optional)**:
   ```bash
   # Copy the example environment file
   cp .env.example .env

   # Edit .env file with your configuration:
   # For OpenAI
   OPENAI_API_KEY=your_api_key
   OPENAI_MODEL_NAME=gpt-3.5-turbo

   # For LiteLLM (see LITELLM_CONFIG.md for more examples)
   OPENAI_API_BASE=http://localhost:4000/v1
   OPENAI_API_KEY=dummy_key
   OPENAI_MODEL_NAME=claude-3-sonnet
   ```

3. **Start the Agent Server**:
   ```bash
   # With LLM (if configured)
   python examples/run_server.py

   # Echo mode only
   python examples/run_server.py --no-llm
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

   # LLM Configuration (Optional)
   OPENAI_API_BASE=http://localhost:4000/v1
   OPENAI_API_KEY=your_api_key
   OPENAI_MODEL_NAME=gpt-3.5-turbo
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

## LiteLLM Integration

The agent supports LiteLLM for accessing multiple LLM providers through a unified interface:

### Supported Providers:
- **OpenAI**: GPT-3.5, GPT-4, GPT-4 Turbo
- **Anthropic**: Claude 3 Sonnet, Claude 3 Haiku
- **Google**: Gemini Pro, PaLM
- **Azure OpenAI**: All Azure OpenAI models
- **Local Models**: Ollama, LocalAI, Text Generation WebUI
- **Open Source**: Hugging Face models via various endpoints

### Configuration Examples:

First, copy the example environment file:
```bash
cp .env.example .env
```

Then edit `.env` with your configuration:
```bash
# OpenAI
OPENAI_API_KEY=your_api_key
OPENAI_MODEL_NAME=gpt-3.5-turbo

# LiteLLM + Claude
OPENAI_API_BASE=http://localhost:4000/v1
OPENAI_API_KEY=your_api_key
OPENAI_MODEL_NAME=claude-3-sonnet

# Local Ollama
OPENAI_API_BASE=http://localhost:11434/v1
OPENAI_MODEL_NAME=llama2
```

See `LITELLM_CONFIG.md` for detailed setup instructions and more provider examples.

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
