"""
LangGraph Agent with MCP (Model Context Protocol) Integration

This implementation demonstrates how to create a LangGraph agent that can:
1. Use LangChain chat models with tool calling
2. Integrate with MCP servers for dynamic tool discovery
3. Maintain conversation state and memory
4. Support streaming responses

Based on the official LangGraph examples and documentation.
"""

import asyncio
import os
from typing import Annotated, Literal, Sequence, TypedDict

# Import environment configuration
import env

from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain_core.tools import tool
from langchain.chat_models import init_chat_model
from langchain_openai import ChatOpenAI

from langgraph.graph import StateGraph, START, END, add_messages
from langgraph.prebuilt import create_react_agent, ToolNode
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.runtime import Runtime

# MCP Integration
try:
    from langchain_mcp_adapters.client import MultiServerMCPClient
    from langchain_mcp_adapters.tools import load_mcp_tools
    MCP_AVAILABLE = True
except ImportError:
    print("MCP adapters not available. Install with: pip install langchain-mcp-adapters")
    MCP_AVAILABLE = False


class AgentState(TypedDict):
    """State schema for the agent."""
    messages: Annotated[Sequence[BaseMessage], add_messages]


class AgentContext(TypedDict):
    """Context schema for runtime configuration."""
    model: Literal["openai", "anthropic"]
    temperature: float
    use_mcp: bool


# Define basic tools (weather tool removed - now using MCP weather server)
@tool
def calculator(expression: str) -> str:
    """Safely evaluate mathematical expressions."""
    try:
        # Simple calculator - only allow basic math operations
        allowed_chars = set('0123456789+-*/(). ')
        if not all(c in allowed_chars for c in expression):
            return "Error: Only basic math operations are allowed"

        result = eval(expression)
        return f"Result: {result}"
    except Exception as e:
        return f"Error calculating '{expression}': {str(e)}"


@tool
def echo_tool(message: str) -> str:
    """Echo back the provided message."""
    return f"Echo: {message}"


# Basic tools list (weather tool now comes from MCP server)
BASIC_TOOLS = [calculator, echo_tool]


def get_model(model_type: str = "openai", temperature: float = 0.0):
    """Initialize and return a chat model using environment configuration."""
    # Use environment variables from env.py for OpenAI configuration
    model_name = os.getenv("OPENAI_MODEL_NAME", "gpt-4o-mini")
    api_base = os.getenv("OPENAI_API_BASE")
    api_key = os.getenv("OPENAI_API_KEY")

    try:
        # Configure HTTP client to avoid SSL/proxy issues
        import httpx

        # Create HTTP client
        http_client = httpx.Client(
            verify=False,  # Disable SSL verification if needed
            trust_env=False,  # Disable environment proxy settings
            timeout=10
        )

        model = ChatOpenAI(
            model=model_name,
            temperature=temperature,
            api_key=api_key,
            base_url=api_base,  # ChatOpenAI will append /v1/chat/completions
            timeout=10,
            http_client=http_client
        )
        print(f"✅ Model configured successfully!")
        print(f"📡 API Endpoint: {api_base}/v1/chat/completions")
        return model
    except Exception as e:
        print(f"⚠️  Warning: Failed to initialize model with custom endpoint: {e}")
        raise e


async def setup_mcp_tools():
    """Set up MCP tools from configured servers."""
    if not MCP_AVAILABLE:
        return []

    try:
        # Configure MCP client with multiple servers
        servers = {}

        # Weather server (local Python file)
        weather_path = os.path.join(os.path.dirname(__file__), "mcp-weather.py")
        if os.path.exists(weather_path):
            servers["weather"] = {
                "command": "python",
                "args": [weather_path],
                "transport": "stdio",
            }
            print(f"✅ Weather server configured: {weather_path}")
        else:
            print(f"⚠️ Weather server not found: {weather_path}")

        # Filesystem server (npm package) - try to configure directly
        try:
            servers["filesystem"] = {
                "command": "npx",
                "args": ["@modelcontextprotocol/server-filesystem", os.path.dirname(__file__)],
                "transport": "stdio",
            }
            print("✅ Filesystem server configured via npx (assuming npm package is installed)")
        except Exception as e:
            print(f"⚠️ Filesystem server configuration failed: {e}")

        if not servers:
            print("❌ No MCP servers available")
            return []

        client = MultiServerMCPClient(servers)

        # Load tools from MCP servers
        mcp_tools = await client.get_tools()
        print(f"Loaded {len(mcp_tools)} tools from MCP servers")
        for tool in mcp_tools:
            print(f"  - {tool.name}: {tool.description}")
        return mcp_tools
    except Exception as e:
        print(f"Failed to load MCP tools: {e}")
        return []


def create_simple_agent(model_type: str = "openai", temperature: float = 0.0, use_mcp: bool = False):
    """Create a simple ReAct agent using LangGraph prebuilt components."""
    model = get_model(model_type, temperature)

    # For simple agent, use basic tools
    tools = BASIC_TOOLS

    # Create agent with memory
    checkpointer = InMemorySaver()

    # Create system prompt
    system_prompt = "You are a helpful AI assistant. Use the available tools to help answer questions and solve problems."

    agent = create_react_agent(
        model=model,
        tools=tools,
        checkpointer=checkpointer,
        prompt=system_prompt
    )

    return agent
def create_custom_agent_graph(model_type: str = "openai", temperature: float = 0.0):
    """Create a custom agent graph with more control over the workflow."""

    model = get_model(model_type, temperature)
    tools = BASIC_TOOLS

    # Bind tools to model
    model_with_tools = model.bind_tools(tools)

    def should_continue(state: AgentState):
        """Determine whether to continue or end the conversation."""
        messages = state["messages"]
        last_message = messages[-1]

        # If the last message has tool calls, continue to tools
        if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
            return "tools"
        # Otherwise, end
        return END

    def call_model(state: AgentState):
        """Call the model with the current state."""
        messages = state["messages"]

        # Add system message if not present
        if not messages or not isinstance(messages[0], SystemMessage):
            system_msg = SystemMessage(content="You are a helpful AI assistant. Use the available tools when needed to provide accurate and helpful responses.")
            messages = [system_msg] + list(messages)

        response = model_with_tools.invoke(messages)
        return {"messages": [response]}

    # Create tool node
    tool_node = ToolNode(tools)

    # Build the graph
    workflow = StateGraph(AgentState)

    # Add nodes
    workflow.add_node("agent", call_model)
    workflow.add_node("tools", tool_node)

    # Set entry point
    workflow.add_edge(START, "agent")

    # Add conditional edges
    workflow.add_conditional_edges(
        "agent",
        should_continue,
        {
            "tools": "tools",
            END: END,
        }
    )

    # Add edge from tools back to agent
    workflow.add_edge("tools", "agent")

    # Compile with memory
    checkpointer = InMemorySaver()
    return workflow.compile(checkpointer=checkpointer)


async def create_mcp_enhanced_agent():
    """Create an agent enhanced with MCP tools."""
    if not MCP_AVAILABLE:
        print("⚠️  MCP adapters not available. Install with: pip install langchain-mcp-adapters")
        print("🔄 Falling back to basic agent (no weather tools available)")
        return create_simple_agent()

    try:
        # Load MCP tools
        mcp_tools = await setup_mcp_tools()

        # Combine basic tools with MCP tools
        all_tools = BASIC_TOOLS + mcp_tools

        model = get_model("openai", 0.0)
        checkpointer = InMemorySaver()

        # Create system prompt
        system_prompt = "You are a helpful AI assistant with access to various tools including MCP-provided capabilities."

        # Create agent with all tools
        agent = create_react_agent(
            model=model,
            tools=all_tools,
            checkpointer=checkpointer,
            prompt=system_prompt
        )

        print(f"✅ MCP-enhanced agent created with {len(mcp_tools)} additional tools")
        return agent
    except Exception as e:
        print(f"Failed to create MCP-enhanced agent: {e}")
        return create_simple_agent()


async def run_conversation(agent, config=None):
    """Run a demonstration with predefined questions and print outputs."""
    if config is None:
        config = {"configurable": {"thread_id": "default"}}

    print("🤖 LangGraph Agent Demo - Running Test Questions\n")

    # Predefined demo questions
    demo_questions = [
        "Calculate 15 * 23 + 7",
        "Get forecast for latitude 37.7749 and longitude -122.4194",
        "Echo this message: Hello from LangGraph agent!",
        "List the files in the current directory",
    ]

    for i, question in enumerate(demo_questions, 1):
        print(f"📝 Question {i}: {question}")
        try:
            # Invoke the agent
            response = await agent.ainvoke(
                {"messages": [HumanMessage(content=question)]},
                config=config
            )

            # Get the last AI message
            last_message = response["messages"][-1]
            if isinstance(last_message, AIMessage):
                print(f"🤖 Assistant: {last_message.content}\n")
            else:
                print(f"🤖 Assistant: {last_message}\n")

        except Exception as e:
            error_type = type(e).__name__
            if "Connection" in str(e) or "timeout" in str(e).lower():
                print(f"❌ Network Error ({error_type}): Cannot reach API endpoint")
                print(f"   Endpoint: {os.getenv('OPENAI_API_BASE', 'default')}")
                print(f"   Suggestion: Check network connectivity or API configuration\n")
            elif "auth" in str(e).lower() or "401" in str(e):
                print(f"❌ Authentication Error ({error_type}): Invalid API key")
                print(f"   Suggestion: Check your API key configuration\n")
            else:
                print(f"❌ Error ({error_type}): {e}\n")

    print("✅ Demo completed!")
    print("=" * 50)


async def demo_agent_capabilities():
    """Demonstrate various agent capabilities."""
    print("🚀 Demonstrating LangGraph Agent Capabilities\n")

    # Create different types of agents
    print("1. Creating Simple Agent...")
    simple_agent = create_simple_agent("openai", 0.0)

    print("2. Creating Custom Agent Graph...")
    custom_agent = create_custom_agent_graph("openai", 0.0)

    print("3. Creating MCP-Enhanced Agent...")
    mcp_agent = await create_mcp_enhanced_agent()

    # Demo questions
    demo_questions = [
        "Get forecast for latitude 37.7749 and longitude -122.4194",  # San Francisco coordinates
        "Calculate 15 * 23 + 7",
        "Echo this message back to me",
    ]

    config = {"configurable": {"thread_id": "demo"}}

    print("\n📝 Running Demo Questions on Simple Agent:")
    for question in demo_questions:
        print(f"\nQ: {question}")
        try:
            response = await simple_agent.ainvoke(
                {"messages": [HumanMessage(content=question)]},
                config=config
            )
            last_message = response["messages"][-1]
            print(f"A: {last_message.content}")
        except Exception as e:
            print(f"Error: {e}")

    print("\n" + "="*50)
    print("Demo completed! You can now start an interactive session.")


def display_configuration():
    """Display current environment configuration."""
    print("🔧 Environment Configuration:")
    print(f"   OPENAI_API_BASE: {os.getenv('OPENAI_API_BASE', 'Not set')}")
    print(f"   OPENAI_MODEL_NAME: {os.getenv('OPENAI_MODEL_NAME', 'Not set')}")
    print(f"   OPENAI_API_KEY: {'Set' if os.getenv('OPENAI_API_KEY') else 'Not set'}")
    print()


async def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="LangGraph Agent with MCP Integration")
    parser.add_argument("--demo", action="store_true", help="Run demonstration")
    parser.add_argument("--model", choices=["openai", "anthropic"], default="openai", help="Model to use")
    parser.add_argument("--temperature", type=float, default=0.0, help="Model temperature")
    parser.add_argument("--mcp", action="store_true", help="Use MCP-enhanced agent")
    parser.add_argument("--custom", action="store_true", help="Use custom agent graph")
    parser.add_argument("--config", action="store_true", help="Show configuration and exit")

    args = parser.parse_args()

    # Display configuration if requested
    if args.config:
        display_configuration()
        return

    # Always show configuration at startup
    display_configuration()

    if args.demo:
        await demo_agent_capabilities()

    # Create agent based on arguments
    if args.mcp:
        print("🔧 Creating MCP-enhanced agent...")
        agent = await create_mcp_enhanced_agent()
    elif args.custom:
        print("🔧 Creating custom agent graph...")
        agent = create_custom_agent_graph(args.model, args.temperature)
    else:
        if MCP_AVAILABLE:
            print("🔧 Creating MCP-enhanced agent (default with MCP available)...")
            agent = await create_mcp_enhanced_agent()
        else:
            print("🔧 Creating simple agent (MCP not available)...")
            agent = create_simple_agent(args.model, args.temperature)

    # Start interactive conversation
    await run_conversation(agent)


if __name__ == "__main__":
    asyncio.run(main())
