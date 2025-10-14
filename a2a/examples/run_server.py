#!/usr/bin/env python3
"""Run the A2A Echo Agent Server.

This script starts an A2A compliant agent server that implements
a simple echo functionality with message enhancements.
"""

import sys
import os

# Add src to path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from agent.server import main

if __name__ == "__main__":
    import sys
    # If no CLI args (other than script name), force agent_type=None for multi-agent mode
    if len(sys.argv) == 1:
        import inspect
        main_args = inspect.getfullargspec(main).args
        kwargs = {}
        if "agent_type" in main_args:
            kwargs["agent_type"] = None
        main(**kwargs)
    else:
        # Let Click handle CLI args (including --agent-type)
        main()
