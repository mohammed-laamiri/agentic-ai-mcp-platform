"""
Echo Tool

Simple example tool used to validate full execution pipeline.

Purpose:
- Demonstrate real callable execution
- Demonstrate schema validation
- Provide safe test tool
"""

from typing import Dict, Any


def echo_tool(message: str) -> Dict[str, Any]:
    """
    Echoes the provided message.

    Args:
        message: string to echo

    Returns:
        dict response
    """

    return {
        "echo": message,
        "length": len(message),
    }