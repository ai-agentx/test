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
    main()
