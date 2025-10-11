#!/usr/bin/env python3
"""Complete A2A Demo - Runs both server and client in sequence.

This script demonstrates a complete A2A protocol interaction by:
1. Starting an agent server
2. Connecting a client to the server
3. Sending test messages
4. Showing the responses
"""

import asyncio
import logging
import sys
import os
import time
from typing import List

# Add src to path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from agent.server import create_echo_agent_server
from client.client import A2AEchoClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class A2ADemo:
    """Complete A2A Protocol demonstration."""

    def __init__(self, host: str = "localhost", port: int = 8080):
        """Initialize the demo.

        Args:
            host: Host address for the server
            port: Port number for the server
        """
        self.host = host
        self.port = port
        self.agent_url = f"http://{host}:{port}"
        self.server = None
        self.server_task = None

    async def start_server(self) -> None:
        """Start the A2A agent server."""
        logger.info("Starting A2A Echo Agent server...")

        # Create server
        self.server = create_echo_agent_server(self.host, self.port)

        # Start server in background task
        self.server_task = asyncio.create_task(self.server.serve())

        # Wait a moment for server to start
        await asyncio.sleep(2)
        logger.info(f"Server started at {self.agent_url}")

    async def stop_server(self) -> None:
        """Stop the A2A agent server."""
        if self.server:
            logger.info("Stopping server...")
            self.server.should_exit = True

            if self.server_task:
                try:
                    await asyncio.wait_for(self.server_task, timeout=5.0)
                except asyncio.TimeoutError:
                    logger.warning("Server shutdown timeout")
                    self.server_task.cancel()

        logger.info("Server stopped")

    async def run_client_tests(self) -> None:
        """Run client test interactions."""
        logger.info("Starting client tests...")

        try:
            async with A2AEchoClient(self.agent_url) as client:
                # Test 1: Get agent information
                await self._test_agent_info(client)

                # Test 2: Send basic messages
                await self._test_basic_messages(client)

                # Test 3: Test conversation context
                await self._test_conversation_context(client)

                # Test 4: Test special message types
                await self._test_special_messages(client)

        except Exception as e:
            logger.error(f"Client test error: {e}")
            raise

    async def _test_agent_info(self, client: A2AEchoClient) -> None:
        """Test agent information retrieval."""
        print("\n" + "="*60)
        print("🔍 TEST 1: Agent Information")
        print("="*60)

        agent_info = await client.get_agent_info()

        print(f"📋 Agent Name: {agent_info['name']}")
        print(f"📝 Description: {agent_info['description']}")
        print(f"🔢 Version: {agent_info['version']}")
        print(f"🌐 URL: {agent_info['url']}")
        print(f"📥 Input Modes: {', '.join(agent_info['capabilities']['input_modes'])}")
        print(f"📤 Output Modes: {', '.join(agent_info['capabilities']['output_modes'])}")
        print(f"⚡ Streaming: {agent_info['capabilities']['streaming']}")

        print(f"\n🎯 Skills ({len(agent_info['skills'])}):")
        for skill in agent_info['skills']:
            print(f"   • {skill['name']}: {skill['description']}")
            if skill['examples']:
                print(f"     Examples: {', '.join(skill['examples'][:2])}")

    async def _test_basic_messages(self, client: A2AEchoClient) -> None:
        """Test basic message sending."""
        print("\n" + "="*60)
        print("💬 TEST 2: Basic Messages")
        print("="*60)

        test_messages = [
            "Hello, Echo Agent!",
            "How are you doing today?",
            "Can you help me with something?",
            "What can you do for me?",
            "This is a test message",
        ]

        for i, message in enumerate(test_messages, 1):
            print(f"\n📤 Message {i}: {message}")
            response = await client.send_message(message)
            print(f"📥 Response: {response}")

            # Small delay between messages
            await asyncio.sleep(0.5)

    async def _test_conversation_context(self, client: A2AEchoClient) -> None:
        """Test conversation context maintenance."""
        print("\n" + "="*60)
        print("🔄 TEST 3: Conversation Context")
        print("="*60)

        # Use same context ID for related messages
        context_id = "demo-conversation-1"

        conversation_messages = [
            "My name is Alex",
            "What did I just tell you my name was?",
            "Can you remember what I said earlier?",
        ]

        for i, message in enumerate(conversation_messages, 1):
            print(f"\n📤 Context Message {i}: {message}")
            response = await client.send_message(message, context_id=context_id)
            print(f"📥 Response: {response}")

            await asyncio.sleep(0.5)

    async def _test_special_messages(self, client: A2AEchoClient) -> None:
        """Test special message types and edge cases."""
        print("\n" + "="*60)
        print("⚡ TEST 4: Special Messages")
        print("="*60)

        special_messages = [
            "",  # Empty message
            "   ",  # Whitespace only
            "hello",  # Trigger special response
            "HELP!",  # Help keyword
            "What is the meaning of life?",  # Question
            "This is a very long message that contains lots of text to see how the agent handles longer inputs and whether it can process them correctly without any issues.",
        ]

        for i, message in enumerate(special_messages, 1):
            display_msg = repr(message) if not message.strip() else message
            print(f"\n📤 Special Message {i}: {display_msg}")

            try:
                response = await client.send_message(message)
                print(f"📥 Response: {response}")
            except Exception as e:
                print(f"❌ Error: {e}")

            await asyncio.sleep(0.5)

    async def run_demo(self) -> None:
        """Run the complete A2A demonstration."""
        print("🚀 A2A Protocol Complete Demo")
        print("="*60)
        print(f"Server: {self.agent_url}")
        print("="*60)

        try:
            # Start server
            await self.start_server()

            # Run client tests
            await self.run_client_tests()

            print("\n" + "="*60)
            print("✅ Demo completed successfully!")
            print("="*60)

        except Exception as e:
            print(f"\n❌ Demo failed: {e}")
            logger.error(f"Demo error: {e}", exc_info=True)
            raise

        finally:
            # Stop server
            await self.stop_server()


async def main() -> None:
    """Main demo function."""
    try:
        demo = A2ADemo()
        await demo.run_demo()

    except KeyboardInterrupt:
        print("\n👋 Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
