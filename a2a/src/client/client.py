# Restore single-agent interactive_chat for --interactive mode
async def interactive_chat(agent_url: str) -> None:
    await interactive_multiagent_chat({"echo": agent_url})

"""A2A Client - Implements client functionality to interact with A2A agents."""

import asyncio
import logging
from typing import Any, Dict, List, Optional
from uuid import uuid4

import click
import httpx
from a2a.client import A2AClient, A2ACardResolver, create_text_message_object
from a2a.types import (
    AgentCard,
    Message,
    MessageSendParams,
    Role,
    SendMessageRequest,
    SendStreamingMessageRequest,
    TextPart,
)

logger = logging.getLogger(__name__)


class A2AEchoClient:
    """Client for interacting with A2A Echo Agent."""

    def __init__(self, agent_url: str, timeout: float = 30.0):
        """Initialize the A2A Echo Client.

        Args:
            agent_url: Base URL of the A2A agent (e.g., 'http://localhost:8080')
            timeout: Request timeout in seconds
        """
        self.agent_url = agent_url.rstrip('/')
        self.timeout = timeout
        self.httpx_client: Optional[httpx.AsyncClient] = None
        self.a2a_client: Optional[A2AClient] = None
        self.agent_card: Optional[AgentCard] = None
        logger.info(f"Initialized A2AEchoClient for {self.agent_url}")

    async def __aenter__(self):
        """Async context manager entry."""
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.disconnect()

    async def connect(self) -> None:
        """Connect to the A2A agent and retrieve its capabilities."""
        try:
            # Create HTTP client
            self.httpx_client = httpx.AsyncClient(timeout=self.timeout)

            # Prefer JSON-RPC bootstrap to avoid issues with well-known path proxies
            logger.info(f"Connecting to A2A agent at {self.agent_url}")
            self.a2a_client = A2AClient(self.httpx_client, url=self.agent_url)
            # Try to fetch the agent card (best-effort). If it fails, continue; messaging still works.
            try:
                self.agent_card = await self.a2a_client.get_card()
            except Exception as e:
                logger.warning(
                    f"Could not fetch agent card (continuing without card): {e}"
                )

            if self.agent_card:
                logger.info(f"Successfully connected to agent: {self.agent_card.name}")
                logger.info(f"Agent description: {self.agent_card.description}")
                logger.info(f"Agent skills: {[skill.name for skill in self.agent_card.skills]}")
            else:
                logger.info("Connected to agent endpoint; agent card unavailable (will still send messages)")

        except Exception as e:
            logger.error(f"Failed to connect to A2A agent: {e}")
            await self.disconnect()
            raise

    async def disconnect(self) -> None:
        """Disconnect from the A2A agent."""
        if self.httpx_client:
            await self.httpx_client.aclose()
            self.httpx_client = None
        self.a2a_client = None
        self.agent_card = None
        logger.info("Disconnected from A2A agent")

    async def send_message(self, text: str, context_id: Optional[str] = None) -> str:
        """Send a text message to the A2A agent and get the response.

        Args:
            text: Text message to send
            context_id: Optional conversation context ID for multi-turn conversations

        Returns:
            Response text from the agent

        Raises:
            ValueError: If not connected to an agent
            Exception: If the message sending fails
        """
        if not self.a2a_client:
            raise ValueError("Not connected to an A2A agent. Call connect() first.")

        try:
            logger.info(f"Sending message: {text[:50]}...")

            # Create message with text part using helpers to match SDK schema
            message = create_text_message_object(role=Role.user, content=text)

            # Create send message request
            send_params = MessageSendParams(
                message=message,
                contextId=context_id,
            )

            request = SendMessageRequest(
                id=uuid4().hex,
                params=send_params,
            )

            # Send message and get response
            response = await self.a2a_client.send_message(request)

            # Extract text from response
            response_text = self._extract_text_from_response(response)

            logger.info(f"Received response: {response_text[:50]}...")
            return response_text

        except Exception as e:
            logger.error(f"Failed to send message: {e}")
            raise

    async def send_message_streaming(self, text: str, context_id: Optional[str] = None) -> List[str]:
        """Send a text message with streaming response.

        Args:
            text: Text message to send
            context_id: Optional conversation context ID

        Returns:
            List of response chunks
        """
        if not self.a2a_client:
            raise ValueError("Not connected to an A2A agent. Call connect() first.")

        if not self.agent_card or not self.agent_card.capabilities.streaming:
            logger.warning("Agent does not support streaming, falling back to regular message")
            response = await self.send_message(text, context_id)
            return [response]

        try:
            logger.info(f"Sending streaming message: {text[:50]}...")

            # Create message
            message = Message(
                role=Role.USER,
                parts=[TextPart(type="text", text=text)],
                messageId=uuid4().hex,
            )

            # Create streaming request
            send_params = MessageSendParams(
                message=message,
                contextId=context_id,
            )

            request = SendStreamingMessageRequest(
                id=uuid4().hex,
                params=send_params,
            )

            # Send streaming message and collect responses
            response_chunks = []
            async for chunk in self.a2a_client.send_message_streaming(request):
                chunk_text = self._extract_text_from_response(chunk)
                if chunk_text:
                    response_chunks.append(chunk_text)
                    logger.debug(f"Received chunk: {chunk_text[:30]}...")

            logger.info(f"Received {len(response_chunks)} response chunks")
            return response_chunks

        except Exception as e:
            logger.error(f"Failed to send streaming message: {e}")
            raise

    def _extract_text_from_response(self, response: Any) -> str:
        """Extract text content from an A2A response, robust to SendMessageResponse and Message objects.

        Handles Pydantic RootModel-style wrappers (objects exposing a `.root` attribute)
        at multiple levels: response -> result -> message.parts -> part.root.text.
        """
        try:
            # Helper to unwrap Pydantic RootModel-style wrappers
            def _unwrap(obj: Any) -> Any:
                try:
                    # unwrap repeatedly in case of nested roots
                    while hasattr(obj, 'root') and getattr(obj, 'root') is not None:
                        obj = getattr(obj, 'root')
                except Exception:
                    return obj
                return obj

            response_unwrapped = _unwrap(response)

            # Handle SendMessageResponse (SDK v0.3.8)
            if hasattr(response_unwrapped, 'result') and getattr(response_unwrapped, 'result'):
                result = _unwrap(getattr(response_unwrapped, 'result'))
                # If result is a Message object
                if hasattr(result, 'parts') and getattr(result, 'parts'):
                    text_parts = []
                    for idx, part in enumerate(result.parts):
                        logger.debug(f"result.parts[{idx}] type={type(part)}, repr={repr(part)}")
                        inner_part = _unwrap(part)
                        # Try part.root.text
                        if hasattr(inner_part, 'text') and getattr(inner_part, 'text'):
                            text_parts.append(getattr(inner_part, 'text'))
                        # Try part.text
                        elif hasattr(part, 'text') and getattr(part, 'text'):
                            text_parts.append(getattr(part, 'text'))
                        # Try dict access
                        elif isinstance(part, dict):
                            if 'root' in part and isinstance(part['root'], dict) and 'text' in part['root'] and part['root']['text']:
                                text_parts.append(part['root']['text'])
                            elif 'text' in part and part['text']:
                                text_parts.append(part['text'])
                        # Fallback: str(part)
                        else:
                            text_parts.append(str(part))
                    if text_parts:
                        return " ".join(text_parts)
                # If result has artifact (older SDKs)
                if hasattr(result, 'artifact') and getattr(result, 'artifact'):
                    artifact = _unwrap(getattr(result, 'artifact'))
                    if hasattr(artifact, 'parts') and getattr(artifact, 'parts'):
                        text_parts = []
                        for part in artifact.parts:
                            inner_part = _unwrap(part)
                            if hasattr(inner_part, 'text') and getattr(inner_part, 'text'):
                                text_parts.append(getattr(inner_part, 'text'))
                        if text_parts:
                            return " ".join(text_parts)
                # Fallback: check if result itself has text
                if hasattr(result, 'text') and getattr(result, 'text'):
                    return getattr(result, 'text')
            # If response itself is a Message object
            if hasattr(response_unwrapped, 'parts') and getattr(response_unwrapped, 'parts'):
                text_parts = []
                for part in response_unwrapped.parts:
                    inner_part = _unwrap(part)
                    if hasattr(inner_part, 'text') and getattr(inner_part, 'text'):
                        text_parts.append(getattr(inner_part, 'text'))
                if text_parts:
                    return " ".join(text_parts)
            # Fallback: convert response to string
            logger.warning(f"Could not extract text from response format: {type(response)}")
            return str(response)
        except Exception as e:
            logger.error(f"Error extracting text from response: {e}")
            return f"Error processing response: {e}"

    async def get_agent_info(self) -> Dict[str, Any]:
        """Get information about the connected agent.

        Returns:
            Dictionary with agent information
        """
        # If we don't have a card yet, attempt once to retrieve it
        if not self.agent_card and self.a2a_client:
            try:
                self.agent_card = await self.a2a_client.get_card()
            except Exception:
                pass
        if not self.agent_card:
            # Minimal fallback info
            return {
                "name": "Unknown A2A Agent",
                "description": "Agent card unavailable",
                "version": "",
                "url": self.agent_url,
                "skills": [],
                "capabilities": {
                    "input_modes": ["text"],
                    "output_modes": ["text"],
                    "streaming": False,
                },
            }

        # Normalize fields across schema variants
        default_input_modes = getattr(self.agent_card, "default_input_modes", None) or []
        default_output_modes = getattr(self.agent_card, "default_output_modes", None) or []
        capabilities = getattr(self.agent_card, "capabilities", None)
        streaming = getattr(capabilities, "streaming", False) if capabilities else False

        skills_list = []
        for skill in getattr(self.agent_card, "skills", []) or []:
            skills_list.append({
                "id": getattr(skill, "id", ""),
                "name": getattr(skill, "name", ""),
                "description": getattr(skill, "description", ""),
                "tags": getattr(skill, "tags", []) or [],
                "examples": getattr(skill, "examples", []) or [],
            })

        return {
            "name": getattr(self.agent_card, "name", ""),
            "description": getattr(self.agent_card, "description", ""),
            "version": getattr(self.agent_card, "version", ""),
            "url": getattr(self.agent_card, "url", ""),
            "skills": skills_list,
            "capabilities": {
                "input_modes": default_input_modes,
                "output_modes": default_output_modes,
                "streaming": streaming,
            },
        }



async def interactive_multiagent_chat(agent_urls: Dict[str, str]) -> None:
    """Interactive chat with multiple agents; switch between them with /switch."""
    print("\n🤖 A2A Multi-Agent Interactive Chat")
    print("Connecting to agents:")
    for name, url in agent_urls.items():
        print(f"  {name}: {url}")
    print("Type 'quit', 'exit', or 'bye' to end the session")
    print("Type 'info' to see agent information")
    print("Type '/switch <agent>' to change active agent (echo, langgraph, crewai)")
    print("-" * 50)

    # Connect to all agents
    clients = {}
    for name, url in agent_urls.items():
        try:
            client = A2AEchoClient(url)
            await client.connect()
            clients[name] = client
        except Exception as e:
            print(f"❌ Failed to connect to {name} agent: {e}")

    # Default to echo
    active_agent = "echo"
    context_ids = {name: uuid4().hex for name in clients}

    def show_agent_info(name):
        client = clients[name]
        info = asyncio.run(client.get_agent_info())
        print(f"\n📋 Agent Info for {name}:")
        print(f"   Name: {info['name']}")
        print(f"   Version: {info['version']}")
        print(f"   Skills: {', '.join([s['name'] for s in info['skills']])}")

    # Show info for active agent
    info = await clients[active_agent].get_agent_info()
    print(f"Connected to: {info['name']} ({active_agent})")
    print(f"Description: {info['description']}")
    print("-" * 50)

    while True:
        try:
            user_input = input(f"\n👤 You ({active_agent}): ").strip()
            if not user_input:
                continue
            if user_input.lower() in ['quit', 'exit', 'bye']:
                print("👋 Goodbye!")
                break
            elif user_input.lower() == 'info':
                info = await clients[active_agent].get_agent_info()
                print(f"\n📋 Agent Info for {active_agent}:")
                print(f"   Name: {info['name']}")
                print(f"   Version: {info['version']}")
                print(f"   Skills: {', '.join([s['name'] for s in info['skills']])}")
                continue
            elif user_input.lower().startswith('/switch'):
                parts = user_input.split()
                if len(parts) == 2 and parts[1] in clients:
                    active_agent = parts[1]
                    info = await clients[active_agent].get_agent_info()
                    print(f"Switched to {active_agent} agent: {info['name']}")
                    print(f"Description: {info['description']}")
                else:
                    print(f"Usage: /switch <agent> (options: {', '.join(clients.keys())})")
                continue
            print("🤖 Agent: ", end="", flush=True)
            response = await clients[active_agent].send_message(user_input, context_ids[active_agent])
            print(response)
        except KeyboardInterrupt:
            print("\n\n👋 Chat interrupted. Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            print("Try again or type 'quit' to exit.")

    # Disconnect all clients
    for client in clients.values():
        await client.disconnect()


@click.command()
@click.option("--agent-url", default="http://localhost:8080", help="URL of the A2A agent")
@click.option("--message", help="Single message to send (non-interactive mode)")
@click.option("--interactive", is_flag=True, help="Start interactive chat session")
@click.option("--multi", is_flag=True, help="Start multi-agent interactive chat (echo, langgraph, crewai)")
@click.option("--info", is_flag=True, help="Show agent information and exit")
def main(agent_url: str, message: Optional[str], interactive: bool, multi: bool, info: bool) -> None:
    """A2A Echo Client - Interact with A2A agents.

    Examples:
        python client.py --info
        python client.py --message "Hello, agent!"
        python client.py --interactive
        python client.py --multi
    """
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    async def run():
        if multi:
            # Multi-agent interactive mode
            agent_urls = {
                "echo": "http://localhost:8080",
                "langgraph": "http://localhost:8081",
                "crewai": "http://localhost:8082",
            }
            await interactive_multiagent_chat(agent_urls)
            return
        if info:
            # Show agent info
            async with A2AEchoClient(agent_url) as client:
                agent_info = await client.get_agent_info()
                print("\n📋 Agent Information:")
                print(f"   Name: {agent_info['name']}")
                print(f"   Description: {agent_info['description']}")
                print(f"   Version: {agent_info['version']}")
                print(f"   URL: {agent_info['url']}")
                print(f"   Input Modes: {', '.join(agent_info['capabilities']['input_modes'])}")
                print(f"   Output Modes: {', '.join(agent_info['capabilities']['output_modes'])}")
                print(f"   Streaming: {agent_info['capabilities']['streaming']}")
                print(f"\n🎯 Skills:")
                for skill in agent_info['skills']:
                    print(f"   • {skill['name']}: {skill['description']}")
                    if skill['examples']:
                        print(f"     Examples: {', '.join(skill['examples'][:3])}")

        elif message:
            # Send single message
            async with A2AEchoClient(agent_url) as client:
                print(f"Sending message: {message}")
                response = await client.send_message(message)
                print(f"Response: {response}")

        elif interactive:
            # Start interactive chat
            await interactive_chat(agent_url)

        else:
            # Default: show help and basic info
            print("A2A Echo Client")
            print(f"Agent URL: {agent_url}")
            print("\nUse --help to see available options")
            print("Use --interactive to start a chat session")
            print("Use --info to see agent information")

    try:
        asyncio.run(run())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        logger.error(f"Client error: {e}")
        raise


if __name__ == "__main__":
    main()
