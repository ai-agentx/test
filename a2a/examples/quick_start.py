#!/usr/bin/env python3
"""Quick Start Example - Simple A2A interaction demo.

This is a minimal example showing how to:
1. Start an A2A agent server
2. Connect a client
3. Send a message
4. Get a response
"""

import asyncio
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from agent.server import create_echo_agent_server
from client.client import A2AEchoClient


async def quick_demo():
    """Run a quick A2A demonstration."""
    print("🚀 A2A Quick Start Demo")
    print("-" * 30)

    # Configuration
    host = "localhost"
    port = 8081  # Use different port to avoid conflicts
    agent_url = f"http://{host}:{port}"

    # Start server
    print(f"Starting server at {agent_url}...")
    server = create_echo_agent_server(host, port)
    server_task = asyncio.create_task(server.serve())

    try:
        # Wait for server to start
        await asyncio.sleep(2)
        print("✅ Server started!")

        # Connect client and send message
        print("\nConnecting client...")
        async with A2AEchoClient(agent_url) as client:
            print("✅ Client connected!")

            # Send a test message
            message = "Hello from the quick demo!"
            print(f"\n📤 Sending: {message}")

            response = await client.send_message(message)
            print(f"📥 Received: {response}")

            print("\n✅ Demo completed successfully!")

    finally:
        # Stop server
        print("\nStopping server...")
        server.should_exit = True
        try:
            await asyncio.wait_for(server_task, timeout=3.0)
        except asyncio.TimeoutError:
            server_task.cancel()
        print("✅ Server stopped!")


if __name__ == "__main__":
    try:
        asyncio.run(quick_demo())
    except KeyboardInterrupt:
        print("\n👋 Demo interrupted")
    except Exception as e:
        print(f"\n❌ Error: {e}")
