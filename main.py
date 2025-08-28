#!/usr/bin/env python3
"""
PII Detection Plugin Entry Point

This is the main entry point for the PII detection plugin.
The plugin provides tools for detecting, analyzing, and masking
personally identifiable information (PII) in text using AI-powered analysis.
"""

import sys
import os

# Add the current directory to Python path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

try:
    from dify_plugin import DifyPluginEnv
except ImportError:
    print("Error: dify_plugin module not found. Please ensure the plugin is running in a proper Dify environment.")
    sys.exit(1)

if __name__ == "__main__":
    # Initialize and run the plugin
    env = DifyPluginEnv()
    env.run()