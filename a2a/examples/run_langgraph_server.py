#!/usr/bin/env python3
"""Run the A2A LangGraph Agent Server.

This script starts an A2A compliant agent server backed by a LangGraph ReAct agent.
"""

import sys
import os
import logging

# Add src to path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from agent.server import create_echo_agent_server


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    host = os.getenv("A2A_HOST", "localhost")
    port = int(os.getenv("A2A_PORT", "8082"))
    use_llm = os.getenv("NO_LLM", "0") not in ("1", "true", "True")

    server = create_echo_agent_server(host=host, port=port, use_llm=use_llm, agent_type="langgraph")
    server.run()
