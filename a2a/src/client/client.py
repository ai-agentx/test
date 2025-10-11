"""A2A Client - Implements client functionality to interact with A2A agents."""

import asyncio
import logging
from typing import Any, Dict, List, Optional
from uuid import uuid4

import click
import httpx
from a2a.client import A2AClient
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

            # Get the A2A client using the agent card URL
            logger.info(f"Connecting to A2A agent at {self.agent_url}")
            self.a2a_client = await A2AClient.get_client_from_agent_card_url(
                self.httpx_client, self.agent_url
            )

            # Get agent card for reference
            self.agent_card = self.a2a_client.agent_card

            logger.info(f"Successfully connected to agent: {self.agent_card.name}")
            logger.info(f"Agent description: {self.agent_card.description}")
            logger.info(f"Agent skills: {[skill.name for skill in self.agent_card.skills]}")

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

            # Create message with text part
            message = Message(
                role=Role.USER,
                parts=[TextPart(type="text", text=text)],
                messageId=uuid4().hex,
            )

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
        """Extract text content from an A2A response.

        Args:
            response: Response object from A2A client

        Returns:
            Extracted text content
        """
        try:
            # Handle different response formats
            if hasattr(response, 'result') and response.result:
                result = response.result

                # Check if result has artifact
                if hasattr(result, 'artifact') and result.artifact:
                    artifact = result.artifact

                    # Extract text from parts
                    if hasattr(artifact, 'parts') and artifact.parts:
                        text_parts = []
                        for part in artifact.parts:
                            if hasattr(part, 'text') and part.text:
                                text_parts.append(part.text)

                        if text_parts:
                            return " ".join(text_parts)

                # Fallback: check if result itself has text
                if hasattr(result, 'text'):
                    return result.text

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
        if not self.agent_card:
            raise ValueError("Not connected to an A2A agent")

        return {
            "name": self.agent_card.name,
            "description": self.agent_card.description,
            "version": self.agent_card.version,
            "url": self.agent_card.url,
            "skills": [
                {
                    "id": skill.id,
                    "name": skill.name,
                    "description": skill.description,
                    "tags": skill.tags,
                    "examples": skill.examples,
                }
                for skill in self.agent_card.skills
            ],
            "capabilities": {
                "input_modes": self.agent_card.capabilities.input_modes,
                "output_modes": self.agent_card.capabilities.output_modes,
                "streaming": self.agent_card.capabilities.streaming,
            },
        }


async def interactive_chat(agent_url: str) -> None:
    """Start an interactive chat session with the A2A agent.

    Args:
        agent_url: URL of the A2A agent
    """
    print(f"\n🤖 A2A Echo Agent Interactive Chat")
    print(f"Connecting to: {agent_url}")
    print("Type 'quit', 'exit', or 'bye' to end the session")
    print("Type 'info' to see agent information")
    print("-" * 50)

    try:
        async with A2AEchoClient(agent_url) as client:
            # Show agent info
            agent_info = await client.get_agent_info()
            print(f"Connected to: {agent_info['name']}")
            print(f"Description: {agent_info['description']}")
            print("-" * 50)

            context_id = uuid4().hex  # Maintain conversation context

            while True:
                try:
                    # Get user input
                    user_input = input("\n👤 You: ").strip()

                    if not user_input:
                        continue

                    # Handle special commands
                    if user_input.lower() in ['quit', 'exit', 'bye']:
                        print("👋 Goodbye!")
                        break
                    elif user_input.lower() == 'info':
                        info = await client.get_agent_info()
                        print(f"\n📋 Agent Info:")
                        print(f"   Name: {info['name']}")
                        print(f"   Version: {info['version']}")
                        print(f"   Skills: {', '.join([s['name'] for s in info['skills']])}")
                        continue

                    # Send message to agent
                    print("🤖 Agent: ", end="", flush=True)
                    response = await client.send_message(user_input, context_id)
                    print(response)

                except KeyboardInterrupt:
                    print("\n\n👋 Chat interrupted. Goodbye!")
                    break
                except Exception as e:
                    print(f"\n❌ Error: {e}")
                    print("Try again or type 'quit' to exit.")

    except Exception as e:
        print(f"❌ Failed to connect to agent: {e}")


@click.command()
@click.option("--agent-url", default="http://localhost:8080", help="URL of the A2A agent")
@click.option("--message", help="Single message to send (non-interactive mode)")
@click.option("--interactive", is_flag=True, help="Start interactive chat session")
@click.option("--info", is_flag=True, help="Show agent information and exit")
def main(agent_url: str, message: Optional[str], interactive: bool, info: bool) -> None:
    """A2A Echo Client - Interact with A2A agents.

    Examples:
        python client.py --info
        python client.py --message "Hello, agent!"
        python client.py --interactive
    """
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    async def run():
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
