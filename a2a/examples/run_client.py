#!/usr/bin/env python3
"""Run the A2A Echo Client.

This script demonstrates how to interact with an A2A agent
using the client implementation.
"""

import sys
import os

# Add src to path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from client.client import main

if __name__ == "__main__":
    main()
