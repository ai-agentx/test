#!/usr/bin/env python3
"""Basic tests for the A2A implementation."""

import asyncio
import unittest
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from agent.executor import EchoAgent, EchoAgentExecutor
from agent.server import create_agent_card
from agent.langgraph_agent import LangGraphAgent, LangGraphAgentExecutor
from agent.crewai_agent import CrewAIAgent, CrewAIAgentExecutor


class TestEchoAgent(unittest.TestCase):
    """Test cases for the EchoAgent."""

    def setUp(self):
        """Set up test fixtures."""
        self.agent = EchoAgent()

    def test_basic_message_processing(self):
        """Test basic message processing."""
        response = self.agent.process_message("Hello")
        self.assertIn("Hello", response)
        self.assertIn("Echo Agent received", response)

    def test_empty_message(self):
        """Test handling of empty messages."""
        response = self.agent.process_message("")
        self.assertIn("empty message", response)

    def test_hello_message(self):
        """Test special handling of hello messages."""
        response = self.agent.process_message("hello there")
        self.assertIn("Hello there! Nice to meet you", response)

    def test_help_message(self):
        """Test special handling of help messages."""
        response = self.agent.process_message("Can you help me?")
        self.assertIn("echo agent", response)

    def test_question_message(self):
        """Test special handling of questions."""
        response = self.agent.process_message("What is this?")
        self.assertIn("interesting question", response)


class TestAgentCard(unittest.TestCase):
    """Test cases for agent card creation."""

    def test_agent_card_creation(self):
        """Test agent card creation."""
        card = create_agent_card("localhost", 8080)

        self.assertEqual(card.name, "Echo Agent")
        self.assertEqual(card.version, "1.0.0")
        self.assertEqual(card.url, "http://localhost:8080/")
        self.assertIn("text", card.capabilities.input_modes)
        self.assertIn("text", card.capabilities.output_modes)
        self.assertTrue(len(card.skills) > 0)

        # Check skill details
        skill = card.skills[0]
        self.assertEqual(skill.id, "echo_text")
        self.assertTrue(len(skill.examples) > 0)


class TestLangGraphAgent(unittest.TestCase):
    """Basic tests for LangGraph agent presence and behavior without API key."""

    def test_instantiation_without_api_key(self):
        # Ensure that creating the agent without credentials doesn't crash
        agent = LangGraphAgent()
        # Without OPENAI_API_KEY, agent is not ready
        self.assertFalse(agent.is_ready())

    def test_executor_instantiation(self):
        # Ensure executor can be created
        executor = LangGraphAgentExecutor()
        self.assertIsNotNone(executor)


class TestCrewAIAgent(unittest.TestCase):
    """Basic tests for CrewAI agent presence and behavior without API key."""

    def test_instantiation_without_api_key(self):
        agent = CrewAIAgent()
        self.assertFalse(agent.is_ready())

    def test_executor_instantiation(self):
        executor = CrewAIAgentExecutor()
        self.assertIsNotNone(executor)


async def run_async_tests():
    """Run asynchronous tests."""
    print("Running async tests...")

    # Test that we can create an executor
    executor = EchoAgentExecutor()
    assert executor is not None
    assert executor.agent is not None

    print("✅ Async tests passed!")


def main():
    """Run all tests."""
    print("🧪 Running A2A Tests")
    print("=" * 30)

    # Run synchronous tests
    print("Running synchronous tests...")
    unittest.main(argv=[''], exit=False, verbosity=2)

    # Run asynchronous tests
    asyncio.run(run_async_tests())

    print("\n✅ All tests completed!")


if __name__ == "__main__":
    main()
