"""LLM-powered Agent using OpenAI API or compatible providers (LiteLLM)."""

import logging
import os
from typing import Optional

from openai import AsyncOpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)


class LLMAgent:
    """LLM-powered Agent that can use OpenAI API or compatible providers."""

    SUPPORTED_CONTENT_TYPES = ["text"]

    def __init__(self, name: str = "LLM Agent"):
        """Initialize the LLM Agent.

        Args:
            name: Name of the agent
        """
        self.name = name
        self.client = None
        self.model_name = os.getenv("OPENAI_MODEL_NAME", "gpt-3.5-turbo")

        # Initialize OpenAI client with custom base URL if provided
        api_key = os.getenv("OPENAI_API_KEY")
        api_base = os.getenv("OPENAI_API_BASE")

        if api_key:
            client_kwargs = {"api_key": api_key}
            if api_base:
                client_kwargs["base_url"] = api_base
                logger.info(f"Using custom API base: {api_base}")

            self.client = AsyncOpenAI(**client_kwargs)
            logger.info(f"Initialized {self.name} with model: {self.model_name}")
        else:
            logger.warning("No OPENAI_API_KEY found, falling back to simple echo mode")

        # System prompt for the agent
        self.system_prompt = (
            "You are a helpful AI agent that communicates via the Agent2Agent (A2A) protocol. "
            "You should be friendly, informative, and concise in your responses. "
            "You can help with various tasks including answering questions, providing information, "
            "and having conversations. Keep your responses clear and to the point."
        )

    async def process_message(self, text: str, context: Optional[str] = None) -> str:
        """Process a text message and return a response.

        Args:
            text: Input text message
            context: Optional conversation context

        Returns:
            Processed response text
        """
        logger.info(f"Processing message: {text[:50]}...")

        if not text.strip():
            return "I received an empty message. Please send me some text to process."

        # If we have an LLM client, use it for intelligent responses
        if self.client:
            try:
                return await self._generate_llm_response(text, context)
            except Exception as e:
                logger.error(f"LLM generation failed: {e}")
                return f"I encountered an error while processing your message: {str(e)}"

        # Fallback to simple echo behavior
        return self._generate_fallback_response(text)

    async def _generate_llm_response(self, text: str, context: Optional[str] = None) -> str:
        """Generate response using LLM.

        Args:
            text: Input text
            context: Optional conversation context

        Returns:
            LLM-generated response
        """
        messages = [{"role": "system", "content": self.system_prompt}]

        # Add context if provided
        if context:
            messages.append({
                "role": "system",
                "content": f"Previous conversation context: {context}"
            })

        # Add user message
        messages.append({"role": "user", "content": text})

        try:
            response = await self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                max_tokens=500,
                temperature=0.7,
            )

            result = response.choices[0].message.content
            logger.info(f"Generated LLM response: {result[:50]}...")
            return result

        except Exception as e:
            logger.error(f"Error calling LLM API: {e}")
            raise

    def _generate_fallback_response(self, text: str) -> str:
        """Generate fallback response when LLM is not available.

        Args:
            text: Input text

        Returns:
            Simple echo response
        """
        response = f"Echo Agent received: '{text}'"

        if "hello" in text.lower():
            response += " - Hello there! Nice to meet you."
        elif "help" in text.lower():
            response += " - I'm an echo agent (LLM unavailable). I repeat back what you send me."
        elif "?" in text:
            response += " - That's an interesting question!"

        response += " (Note: LLM features unavailable - check OPENAI_API_KEY configuration)"

        logger.info(f"Generated fallback response: {response[:50]}...")
        return response

    def is_llm_available(self) -> bool:
        """Check if LLM is available for use.

        Returns:
            True if LLM client is configured, False otherwise
        """
        return self.client is not None
