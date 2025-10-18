#!/usr/bin/env python3
"""Run the A2A Echo Agent Server.

This script starts an A2A compliant agent server that implements
a simple echo functionality with message enhancements.
"""

import sys
import os

# Add src to path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from agent.server import main as cli

if __name__ == "__main__":
    import sys
    # If no CLI args, bypass Click parsing and call the underlying callback
    # with agent_type=None to start all agents on consecutive ports.
    if len(sys.argv) == 1:
        # Pull defaults from env (matching README/env vars) with sensible fallbacks
        host = os.getenv("A2A_HOST", "localhost")
        try:
            port = int(os.getenv("A2A_PORT", "8080"))
        except ValueError:
            port = 8080
        log_level = os.getenv("LOG_LEVEL", "info")
        no_llm = os.getenv("NO_LLM", "0") in ("1", "true", "True")

        # Click commands expose the original function as `.callback`
        # Call it directly so we can pass agent_type=None
        try:
            cli.callback(host=host, port=port, log_level=log_level, no_llm=no_llm, agent_type=None)
        except AttributeError:
            # Fallback: if for some reason `.callback` isn't available, invoke like a normal function
            cli(host=host, port=port, log_level=log_level, no_llm=no_llm, agent_type=None)
    else:
        # Let Click handle CLI args (including --agent-type)
        cli()
