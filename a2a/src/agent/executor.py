"""Agent Executor for A2A Protocol - Handles message processing logic."""

import logging
from typing import Any, Dict, List, Optional

from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.server.tasks import TaskUpdater
from a2a.types import (
    DataPart,
    Message,
    Part,
    Task,
    TaskState,
    TextPart,
    UnsupportedOperationError,
)
from a2a.utils import (
    new_agent_text_message,
    new_task,
)
from .llm_agent import LLMAgent

logger = logging.getLogger(__name__)


class EchoAgent:
    """Simple Echo Agent that processes and responds to text messages."""

    SUPPORTED_CONTENT_TYPES = ["text"]

    def __init__(self, name: str = "Echo Agent"):
        """Initialize the Echo Agent.

        Args:
            name: Name of the agent
        """
        self.name = name
        logger.info(f"Initialized {self.name}")

    def process_message(self, text: str) -> str:
        """Process a text message and return a response.

        Args:
            text: Input text message

        Returns:
            Processed response text
        """
        logger.info(f"Processing message: {text[:50]}...")

        # Simple echo processing with some enhancements
        if not text.strip():
            return "I received an empty message. Please send me some text to process."

        # Add some basic processing logic
        response = f"Echo Agent received: '{text}'"

        if "hello" in text.lower():
            response += " - Hello there! Nice to meet you."
        elif "help" in text.lower():
            response += " - I'm an echo agent. I repeat back what you send me with some enhancements."
        elif "?" in text:
            response += " - That's an interesting question!"

        logger.info(f"Generated response: {response[:50]}...")
        return response


class EchoAgentExecutor(AgentExecutor):
    """A2A Agent Executor that handles A2A protocol messages using EchoAgent."""

    SUPPORTED_INPUT_TYPES = ["text"]
    SUPPORTED_OUTPUT_TYPES = ["text"]

    def __init__(self, use_llm: bool = True):
        """Initialize the Echo Agent Executor.

        Args:
            use_llm: Whether to use LLM agent (if available) or simple echo agent
        """
        if use_llm:
            self.agent = LLMAgent()
            agent_type = "LLM Agent" if self.agent.is_llm_available() else "Echo Agent (LLM fallback)"
        else:
            self.agent = EchoAgent()
            agent_type = "Echo Agent"

        logger.info(f"Initialized EchoAgentExecutor with {agent_type}")

        # Store conversation contexts for multi-turn conversations
        self.conversation_contexts: Dict[str, List[str]] = {}    async def send_message(
        self,
        request_context: RequestContext,
        task: Task,
        event_queue: EventQueue,
        task_updater: TaskUpdater,
    ) -> None:
        """Handle incoming A2A messages and generate responses.

        Args:
            request_context: Context information for the request
            task: The task containing the message to process
            event_queue: Queue for publishing events
            task_updater: Interface for updating task status
        """
        try:
            logger.info(f"Processing task: {task.id}")

            # Extract the message from the task
            message = task.message
            if not message:
                raise ValueError("No message found in task")

            # Get conversation context if available
            context_id = getattr(task, 'context_id', None)
            context = None
            if context_id and context_id in self.conversation_contexts:
                # Use last few messages as context
                context = " | ".join(self.conversation_contexts[context_id][-3:])

            # Process text parts from the message
            response_texts = []
            for part in message.parts:
                if isinstance(part, TextPart):
                    # Process the text using our agent (LLM or Echo)
                    if hasattr(self.agent, 'process_message') and callable(getattr(self.agent, 'process_message')):
                        # Check if it's an async method (LLM agent)
                        import inspect
                        if inspect.iscoroutinefunction(self.agent.process_message):
                            response_text = await self.agent.process_message(part.text, context)
                        else:
                            response_text = self.agent.process_message(part.text)
                    else:
                        response_text = f"Agent error: No process_message method available"

                    response_texts.append(response_text)

                    # Store conversation context
                    if context_id:
                        if context_id not in self.conversation_contexts:
                            self.conversation_contexts[context_id] = []
                        self.conversation_contexts[context_id].append(f"User: {part.text}")
                        self.conversation_contexts[context_id].append(f"Agent: {response_text}")

                        # Keep only last 10 exchanges to manage memory
                        if len(self.conversation_contexts[context_id]) > 20:
                            self.conversation_contexts[context_id] = self.conversation_contexts[context_id][-20:]

                elif isinstance(part, DataPart):
                    # Handle data parts (for future extension)
                    response_texts.append("I received some data, but I can only process text messages.")
                else:
                    logger.warning(f"Unsupported part type: {type(part)}")
                    response_texts.append(f"I received an unsupported message type: {type(part).__name__}")

            if not response_texts:
                response_texts = ["I didn't find any text to process in your message."]

            # Combine all responses
            combined_response = " ".join(response_texts)            # Create response message
            response_message = new_agent_text_message(combined_response)

            # Update task with the response
            await task_updater.update_task(
                task.id,
                task_state=TaskState.COMPLETED,
                artifact=response_message,
            )

            logger.info(f"Successfully completed task: {task.id}")

        except Exception as e:
            logger.error(f"Error processing task {task.id}: {e}")

            # Update task with error status
            error_message = new_agent_text_message(
                f"I encountered an error while processing your message: {str(e)}"
            )

            await task_updater.update_task(
                task.id,
                task_state=TaskState.FAILED,
                artifact=error_message,
            )

    async def get_task(
        self,
        request_context: RequestContext,
        task_id: str,
        event_queue: EventQueue,
    ) -> Task:
        """Retrieve a task by ID.

        Args:
            request_context: Context information for the request
            task_id: ID of the task to retrieve
            event_queue: Queue for publishing events

        Returns:
            The requested task

        Raises:
            UnsupportedOperationError: This operation is not supported in this example
        """
        logger.warning(f"get_task called for task_id: {task_id} (not implemented)")
        raise UnsupportedOperationError("get_task is not supported by this agent")

    async def cancel_task(
        self,
        request_context: RequestContext,
        task_id: str,
        event_queue: EventQueue,
        task_updater: TaskUpdater,
    ) -> None:
        """Cancel a task.

        Args:
            request_context: Context information for the request
            task_id: ID of the task to cancel
            event_queue: Queue for publishing events
            task_updater: Interface for updating task status

        Raises:
            UnsupportedOperationError: This operation is not supported in this example
        """
        logger.warning(f"cancel_task called for task_id: {task_id} (not implemented)")
        raise UnsupportedOperationError("cancel_task is not supported by this agent")
