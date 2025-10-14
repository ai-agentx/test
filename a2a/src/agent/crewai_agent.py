"""CrewAI-powered Agent integrated with A2A executor interface.

This module defines a simple CrewAI agent setup and wraps it in a
`process_message` function, then exposes an A2A AgentExecutor.
"""

from __future__ import annotations

import logging
import os
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv

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

# CrewAI and LLM
from langchain_openai import ChatOpenAI
from crewai import Agent as CrewAgent, Task as CrewTask, Crew, Process


# Always load .env at import time, override existing env vars if present
load_dotenv(override=True)

logger = logging.getLogger(__name__)


class CrewAIAgent:
    """A simple CrewAI agent that answers user questions concisely."""

    SUPPORTED_CONTENT_TYPES = ["text"]

    def __init__(self, name: str = "CrewAI Agent"):
        self.name = name

        api_key = os.getenv("OPENAI_API_KEY")
        api_base = os.getenv("OPENAI_API_BASE")
        model_name = os.getenv("OPENAI_MODEL_NAME", "gpt-4o-mini")

        if not api_key:
            logger.warning(
                "OPENAI_API_KEY not found; CrewAI agent will not be able to use an LLM."
            )
            self.llm = None
            self.base_agent = None
            return

        llm_kwargs: Dict[str, Any] = {"api_key": api_key}
        if api_base:
            llm_kwargs["base_url"] = api_base
            logger.info(f"CrewAIAgent using custom API base: {api_base}")

        self.llm = ChatOpenAI(model=model_name, temperature=0.2, **llm_kwargs)

        # Define a generalist CrewAI agent
        self.base_agent = CrewAgent(
            role="Generalist Assistant",
            goal=(
                "Provide concise, helpful answers to user questions and optionally "
                "use tools when they are available."
            ),
            backstory=(
                "You are an A2A-compatible assistant built using CrewAI. You work on "
                "single-turn tasks and return clear, actionable responses."
            ),
            llm=self.llm,
            verbose=False,
        )

    def is_ready(self) -> bool:
        return self.base_agent is not None

    async def process_message(self, text: str, context: Optional[str] = None) -> str:
        if not text.strip():
            return "I received an empty message. Please send me some text to process."

        if not self.is_ready():
            return (
                "CrewAI agent is not configured (missing OPENAI_API_KEY). "
                "Please configure LLM credentials to enable this agent."
            )

        try:
            # Create a Task dynamically based on user input
            description = text
            if context:
                description = f"Context: {context}\nTask: {text}"

            task = CrewTask(
                description=description,
                expected_output="A short, helpful answer. Include tool results if used.",
                agent=self.base_agent,
            )

            crew = Crew(
                agents=[self.base_agent],
                tasks=[task],
                process=Process.sequential,
                verbose=False,
            )

            # Kick off execution (CrewAI uses sync run; wrap in thread if needed)
            # Many crewai versions expose `kickoff()` returning a string.
            from anyio.to_thread import run_sync

            result: str = await run_sync(crew.kickoff)
            if not isinstance(result, str):
                result = str(result)
            return result
        except Exception as e:
            logger.error(f"CrewAI execution failed: {e}")
            return f"I encountered an error while processing your message: {str(e)}"


class CrewAIAgentExecutor(AgentExecutor):
    """A2A AgentExecutor that delegates to a CrewAIAgent."""

    SUPPORTED_INPUT_TYPES = ["text"]
    SUPPORTED_OUTPUT_TYPES = ["text"]

    def __init__(self):
        self.agent = CrewAIAgent()
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
            logger.error(f"Error in CrewAI execute: {e}")
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
        logger.warning("get_task not implemented for CrewAIAgentExecutor")
        raise UnsupportedOperationError("get_task is not supported by this agent")

    async def cancel_task(
        self,
        request_context: RequestContext,
        task_id: str,
        event_queue: EventQueue,
        task_updater: TaskUpdater,
    ) -> None:
        logger.warning("cancel_task not implemented for CrewAIAgentExecutor")
        raise UnsupportedOperationError("cancel_task is not supported by this agent")

    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:  # type: ignore[override]
        logger.warning("cancel called (no-op) in CrewAIAgentExecutor")
        return
