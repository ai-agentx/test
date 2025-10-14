"""LangGraph-powered Agent integrated with A2A executor interface.

This module defines a simple ReAct-style LangGraph agent that can call tools
and generate responses via an LLM (OpenAI-compatible).

It exposes:
- LangGraphAgent: wraps a LangGraph graph with a simple `process_message` API
- LangGraphAgentExecutor: A2A AgentExecutor that uses LangGraphAgent
"""

from __future__ import annotations

import logging
import os
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv

# Always load .env at import time, override existing env vars if present
load_dotenv(override=True)

# A2A imports
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.server.tasks import TaskUpdater
from a2a.types import (
    DataPart,
    Task,
    TaskState,
    TextPart,
    UnsupportedOperationError,
)
from a2a.utils import new_agent_text_message

# LangChain / LangGraph imports
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent

# Local tools
from .tools import get_exchange_rate


logger = logging.getLogger(__name__)


class LangGraphAgent:
    """Simple LangGraph agent using a ReAct-style prebuilt graph.

    The agent supports calling the `get_exchange_rate` tool and can be extended
    by registering additional tools.
    """

    SUPPORTED_CONTENT_TYPES = ["text"]

    def __init__(self, name: str = "LangGraph Agent"):
        self.name = name

        # Configure LLM from environment
        api_key = os.getenv("OPENAI_API_KEY")
        api_base = os.getenv("OPENAI_API_BASE")
        model_name = os.getenv("OPENAI_MODEL_NAME", "gpt-4o-mini")

        if not api_key:
            logger.warning(
                "OPENAI_API_KEY not found; LangGraph agent will not be able to use an LLM."
            )
            self.llm = None
            self.graph = None
            return

        llm_kwargs: Dict[str, Any] = {"api_key": api_key}
        if api_base:
            llm_kwargs["base_url"] = api_base
            logger.info(f"LangGraphAgent using custom API base: {api_base}")

        # Initialize LLM and graph
        self.llm = ChatOpenAI(model=model_name, temperature=0.2, **llm_kwargs)
        tools = [get_exchange_rate]
        self.graph = create_react_agent(self.llm, tools=tools)

        # Simple system prompt guiding the agent to be concise and helpful
        self.system_prompt = (
            "You are an A2A-compatible assistant built with LangGraph. Be concise, "
            "helpful, and use tools when beneficial."
        )

    def is_ready(self) -> bool:
        """Return True if the agent graph is initialized and ready."""
        return self.graph is not None

    async def process_message(self, text: str, context: Optional[str] = None) -> str:
        """Process a user message by invoking the LangGraph agent.

        Args:
            text: The user input text
            context: Optional conversation context string (will be provided as a system message)

        Returns:
            Assistant response text
        """
        if not text.strip():
            return "I received an empty message. Please send me some text to process."

        if not self.is_ready():
            return (
                "LangGraph agent is not configured (missing OPENAI_API_KEY). "
                "Please configure LLM credentials to enable this agent."
            )

        # Build message list for the graph state
        messages: List[Any] = []
        messages.append(SystemMessage(content=self.system_prompt))
        if context:
            messages.append(SystemMessage(content=f"Conversation context: {context}"))
        messages.append(HumanMessage(content=text))

        try:
            # The prebuilt ReAct agent expects state with a `messages` list
            result = await self.graph.ainvoke({"messages": messages})
            # Result is a state dict with updated `messages`
            result_messages = result.get("messages", [])
            # Return the last assistant message content
            for msg in reversed(result_messages):
                try:
                    if getattr(msg, "type", None) == "ai" or msg.__class__.__name__ == "AIMessage":
                        content = getattr(msg, "content", None)
                        if content:
                            return content if isinstance(content, str) else str(content)
                except Exception:
                    continue
            # Fallback: stringify entire result
            logger.warning("Could not find AI message in graph result; returning stringified result")
            return str(result)
        except Exception as e:
            logger.error(f"LangGraph invocation failed: {e}")
            return f"I encountered an error while processing your message: {str(e)}"


class LangGraphAgentExecutor(AgentExecutor):
    """A2A AgentExecutor that delegates to a LangGraphAgent."""

    SUPPORTED_INPUT_TYPES = ["text"]
    SUPPORTED_OUTPUT_TYPES = ["text"]

    def __init__(self):
        self.agent = LangGraphAgent()
        self.conversation_contexts: Dict[str, List[str]] = {}

    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        try:
            message = context.message
            response_texts: List[str] = []

            for part in message.parts:
                text_value = None
                if hasattr(part, "root") and hasattr(part.root, "text"):
                    text_value = part.root.text
                elif hasattr(part, "text"):
                    text_value = part.text

                if text_value is None:
                    response_texts.append("I can only process text messages.")
                    continue

                response_texts.append(await self.agent.process_message(text_value))

            combined = " ".join(response_texts) or "I didn't find any text to process."
            await event_queue.enqueue_event(new_agent_text_message(combined))
            return None
        except Exception as e:
            logger.error(f"Error in LangGraph execute: {e}")
            await event_queue.enqueue_event(
                new_agent_text_message(f"Error while processing your message: {e}")
            )
            return None

    async def send_message(
        self,
        request_context: RequestContext,
        task: Task,
        event_queue: EventQueue,
        task_updater: TaskUpdater,
    ) -> None:
        try:
            message = task.message
            if not message:
                raise ValueError("No message found in task")

            context_id = getattr(task, "context_id", None)
            context_str = None
            if context_id and context_id in self.conversation_contexts:
                context_str = " | ".join(self.conversation_contexts[context_id][-3:])

            response_texts: List[str] = []
            for part in message.parts:
                inner = part.root if hasattr(part, "root") else part
                if isinstance(inner, TextPart) or hasattr(inner, "text"):
                    text_value = getattr(inner, "text", None)
                    if text_value is not None:
                        result = await self.agent.process_message(text_value, context=context_str)
                        response_texts.append(result)

                        if context_id:
                            self.conversation_contexts.setdefault(context_id, [])
                            self.conversation_contexts[context_id].append(f"User: {text_value}")
                            self.conversation_contexts[context_id].append(f"Agent: {result}")
                            if len(self.conversation_contexts[context_id]) > 20:
                                self.conversation_contexts[context_id] = self.conversation_contexts[context_id][-20:]
                elif isinstance(inner, DataPart):
                    response_texts.append("I received some data, but I can only process text messages.")
                else:
                    response_texts.append("Unsupported message part type.")

            combined = " ".join(response_texts) or "I didn't find any text to process."
            await task_updater.update_task(
                task.id,
                task_state=TaskState.COMPLETED,
                artifact=new_agent_text_message(combined),
            )
        except Exception as e:
            logger.error(f"Error processing task {task.id}: {e}")
            await task_updater.update_task(
                task.id,
                task_state=TaskState.FAILED,
                artifact=new_agent_text_message(f"I encountered an error: {e}"),
            )

    async def get_task(
        self,
        request_context: RequestContext,
        task_id: str,
        event_queue: EventQueue,
    ) -> Task:
        logger.warning("get_task not implemented for LangGraphAgentExecutor")
        raise UnsupportedOperationError("get_task is not supported by this agent")

    async def cancel_task(
        self,
        request_context: RequestContext,
        task_id: str,
        event_queue: EventQueue,
        task_updater: TaskUpdater,
    ) -> None:
        logger.warning("cancel_task not implemented for LangGraphAgentExecutor")
        raise UnsupportedOperationError("cancel_task is not supported by this agent")

    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:  # type: ignore[override]
        logger.warning("cancel called (no-op) in LangGraphAgentExecutor")
        return
