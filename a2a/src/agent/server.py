"""A2A Agent Server - Implements an A2A compliant agent server."""

import logging
import multiprocessing
import os
from typing import Optional

import click
import uvicorn
from dotenv import load_dotenv
from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import (
    AgentCapabilities,
    AgentCard,
    AgentSkill,
)
from .executor import EchoAgentExecutor
from .langgraph_agent import LangGraphAgentExecutor
from .crewai_agent import CrewAIAgentExecutor

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)


def create_agent_card(host: str, port: int, use_llm: bool = True, agent_type: str = "echo") -> AgentCard:
    """Create an Agent Card describing our agent's capabilities.

    Args:
        host: Host address where the agent is running
        port: Port number where the agent is running
        use_llm: Whether the agent uses LLM capabilities

    Returns:
        AgentCard with agent metadata and capabilities
    """
    # Check if LLM is actually available
    llm_available = use_llm and os.getenv("OPENAI_API_KEY") is not None

    # Define the agent's skill based on capabilities
    if agent_type == "langgraph":
        skill = AgentSkill(
            id="react_tool_use",
            name="ReAct Tool Use",
            description="A LangGraph ReAct agent that can use tools such as currency conversion and answer questions",
            tags=["langgraph", "react", "tools", "llm"],
            examples=[
                "Convert 15 USD to EUR",
                "What's the exchange rate from GBP to JPY?",
                "Explain how the tool call was done",
            ],
        )
        agent_name = "LangGraph Agent"
        agent_description = (
            "An A2A-compatible agent powered by LangGraph using a ReAct workflow. "
            "It can call tools and provide concise, helpful answers."
        )
    elif agent_type == "crewai":
        skill = AgentSkill(
            id="crewai_generalist",
            name="CrewAI Generalist",
            description="A CrewAI-based assistant that produces concise, helpful answers to user questions",
            tags=["crewai", "assistant", "llm"],
            examples=[
                "Summarize the benefits of solar energy",
                "Give me a short plan for learning Python",
                "Explain Docker in simple terms",
            ],
        )
        agent_name = "CrewAI Agent"
        agent_description = (
            "An A2A-compatible agent powered by CrewAI that executes a single-turn task "
            "with a generalist assistant."
        )
    elif llm_available:
        skill = AgentSkill(
            id="intelligent_conversation",
            name="Intelligent Conversation",
            description="Engages in intelligent conversations, answers questions, and provides helpful assistance using advanced language models",
            tags=["conversation", "qa", "assistance", "llm", "ai"],
            examples=[
                "What is the capital of France?",
                "Can you help me write a Python function?",
                "Explain quantum computing in simple terms",
                "What are the benefits of renewable energy?",
                "Help me plan a trip to Japan"
            ],
        )
        agent_name = "LLM Agent"
        agent_description = (
            "An intelligent AI agent powered by large language models that can engage in "
            "natural conversations, answer questions, provide explanations, and assist with "
            "various tasks. Communicates via the Agent2Agent (A2A) protocol."
        )
    else:
        skill = AgentSkill(
            id="echo_text",
            name="Echo Text Messages",
            description="Receives text messages and returns enhanced echo responses",
            tags=["echo", "text", "conversation"],
            examples=[
                "Hello, how are you?",
                "Can you help me with something?",
                "What can you do?",
                "Echo this message back to me"
            ],
        )
        agent_name = "Echo Agent"
        agent_description = (
            "A simple A2A agent that echoes back text messages with enhancements. "
            "Perfect for testing A2A protocol communication and demonstrating basic agent functionality."
        )    # Define agent capabilities
    capabilities = AgentCapabilities(
        input_modes=["text"],
        output_modes=["text"],
        streaming=False,  # Set to True if you want to support streaming responses
    )

    # Create the agent card
    agent_card = AgentCard(
        name=agent_name,
        description=agent_description,
        url=f"http://{host}:{port}/",
        version="1.0.0",
        default_input_modes=EchoAgentExecutor.SUPPORTED_INPUT_TYPES,
        default_output_modes=EchoAgentExecutor.SUPPORTED_OUTPUT_TYPES,
        capabilities=capabilities,
        skills=[skill],
    )

    return agent_card


def create_echo_agent_server(host: str = "localhost", port: int = 8080, use_llm: bool = True, agent_type: str = "echo") -> uvicorn.Server:
    """Create and configure an A2A agent server.

    Args:
        host: Host address to bind the server to
        port: Port number to bind the server to
        use_llm: Whether to use LLM capabilities (if available)

    Returns:
        Configured Uvicorn server instance
    """
    # Create agent card
    agent_card = create_agent_card(host, port, use_llm, agent_type=agent_type)

    # Create agent executor
    if agent_type == "langgraph":
        agent_executor = LangGraphAgentExecutor()
    elif agent_type == "crewai":
        agent_executor = CrewAIAgentExecutor()
    else:
        agent_executor = EchoAgentExecutor(use_llm=use_llm)
    # Create request handler with in-memory task store
    request_handler = DefaultRequestHandler(
        agent_executor=agent_executor,
        task_store=InMemoryTaskStore(),
    )

    # Create A2A Starlette application
    server_app = A2AStarletteApplication(
        agent_card=agent_card,
        http_handler=request_handler
    )

    # Build the app
    app = server_app.build()

    # Create Uvicorn server configuration
    config = uvicorn.Config(
        app=app,
        host=host,
        port=port,
        log_level="info",
    )

    server = uvicorn.Server(config)

    # Log configuration info
    llm_available = use_llm and os.getenv("OPENAI_API_KEY") is not None
    model_name = os.getenv("OPENAI_MODEL_NAME", "gpt-3.5-turbo")
    api_base = os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1")

    logger.info(f"Created A2A Agent server at http://{host}:{port}")
    logger.info(f"Agent card available at: http://{host}:{port}/.well-known/agent.json")
    logger.info(f"Agent type: {agent_type}")

    if llm_available:
        logger.info(f"LLM enabled: {model_name} via {api_base}")
    else:
        logger.info("LLM disabled: Using echo mode (set OPENAI_API_KEY to enable LLM)")

    return server


@click.command()
@click.option("--host", default="localhost", help="Host address to bind the server to")
@click.option("--port", default=8080, type=int, help="Port number to bind the server to")
@click.option("--log-level", default="info", help="Logging level")
@click.option("--no-llm", is_flag=True, help="Disable LLM and use simple echo mode")
@click.option("--agent-type", type=click.Choice(["echo", "langgraph", "crewai"], case_sensitive=False), default="echo", help="Select which agent implementation to run")
def main(host: str, port: int, log_level: str, no_llm: bool, agent_type: str = None) -> None:
    """Start the A2A Agent server.

    This starts an A2A compliant agent server that can receive and respond to text messages.
    The agent can use LLM capabilities (if configured) or fall back to simple echo functionality.

    Environment Variables:
        OPENAI_API_KEY: Your OpenAI API key
        OPENAI_API_BASE: Custom API base URL (e.g., for LiteLLM)
        OPENAI_MODEL_NAME: Model name to use (default: gpt-3.5-turbo)
    """
    # Configure logging
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    use_llm = not no_llm

    logger.info("Starting A2A Agent Server...")
    logger.info(f"Host: {host}")
    logger.info(f"Port: {port}")
    logger.info(f"LLM Mode: {'Enabled' if use_llm else 'Disabled'}")
    logger.info(f"Agent Type: {agent_type}")

    # Show configuration
    if use_llm:
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key:
            logger.info(f"API Key: {'*' * 10}{api_key[-4:] if len(api_key) > 4 else '****'}")
        else:
            logger.warning("OPENAI_API_KEY not found - will use echo mode")

        api_base = os.getenv("OPENAI_API_BASE")
        if api_base:
            logger.info(f"API Base: {api_base}")

        model_name = os.getenv("OPENAI_MODEL_NAME", "gpt-3.5-turbo")
        logger.info(f"Model: {model_name}")

    # If agent_type is not set or empty, run all agents on different ports
    if not agent_type:
        logger.info("No agent_type set; running all agents (echo, langgraph, crewai) on different ports.")
        base_port = port
        agent_types = ["echo", "langgraph", "crewai"]
        servers = []
        for idx, atype in enumerate(agent_types):
            agent_port = base_port + idx
            logger.info(f"\n{'='*40}\nStarting {atype.upper()} agent on port {agent_port}")
            # Log LLM and model info for each agent type
            if atype == "langgraph":
                logger.info(f"LangGraph agent will use LLM: {os.getenv('OPENAI_MODEL_NAME', 'gpt-4o-mini')} via {os.getenv('OPENAI_API_BASE', 'https://api.openai.com/v1')}")
            elif atype == "crewai":
                logger.info(f"CrewAI agent will use LLM: {os.getenv('OPENAI_MODEL_NAME', 'gpt-4o-mini')} via {os.getenv('OPENAI_API_BASE', 'https://api.openai.com/v1')}")
            else:
                logger.info(f"Echo agent will use LLM: {os.getenv('OPENAI_MODEL_NAME', 'gpt-3.5-turbo')} via {os.getenv('OPENAI_API_BASE', 'https://api.openai.com/v1')}")
            server = create_echo_agent_server(host, agent_port, use_llm, agent_type=atype)
            servers.append(server)
        def run_server_instance(server, atype, port):
            logger.info(f"{'='*40}\nRunning {atype.upper()} agent at http://{host}:{port}\n{'='*40}")
            server.run()

        processes = []
        for server, atype in zip(servers, agent_types):
            agent_port = base_port + agent_types.index(atype)
            p = multiprocessing.Process(target=run_server_instance, args=(server, atype, agent_port))
            p.start()
            processes.append(p)
        try:
            for p in processes:
                p.join()
        except KeyboardInterrupt:
            logger.info("Server shutdown requested")
            for p in processes:
                p.terminate()
        except Exception as e:
            logger.error(f"Server error: {e}")
            for p in processes:
                p.terminate()
            raise
        return

    try:
        # Create and run the server
        server = create_echo_agent_server(host, port, use_llm, agent_type=agent_type)
        server.run()
    except KeyboardInterrupt:
        logger.info("Server shutdown requested")
    except Exception as e:
        logger.error(f"Server error: {e}")
        raise


if __name__ == "__main__":
    main()
