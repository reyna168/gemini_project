from mcp.server.fastmcp import FastMCP
import time
import signal
import sys
import json

# Handle SIGINT (Ctrl+C) gracefully
def signal_handler(sig, frame):
    print("Shutting down server gracefully...")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)


# Create an MCP server with increased timeout
mcp = FastMCP(
    name="count-r",
    host="127.0.0.1",
    port=8080,
    # Add this to make the server more resilient
    timeout=30  # Increase timeout to 30 seconds
)

# Define our tool
@mcp.tool()
def count_r(words: list[str]) -> json:
    """Count the number of 'r' letters in a given word."""
    result = {}
    try:
        for word in words:
            # Add robust error handling
            if not isinstance(word, str):
                result[word] = 0
            else:
                result[word] = word.lower().count("r")
        return result
    except Exception as e:
        # Return 0 on any error
        return result

# Define our tool
@mcp.tool()
def count_l(words: list[str]) -> json:
    """Count the number of 'l' letters in a given word."""
    result = {}
    try:
        for word in words:
            if not isinstance(word, str):
                result[word] = 0
            else:
                result[word] = word.lower().count("l")
        return result
    except Exception:
        return result

# Define our tool
@mcp.tool()
def count_e(words: list[str]) -> json:
    """Count the number of 'e' letters in a given word."""
    result = {}
    try:
        for word in words:
            if not isinstance(word, str):
                result[word] = 0
            else:
                result[word] = word.lower().count("e")
        return result
    except Exception:
        return result

if __name__ == "__main__":
    try:
        print("Starting MCP server on 127.0.0.1:8080")
        # Use this approach to keep the server running
        mcp.run()
    except Exception as e:
        print(f"Error: {e}")
        # Sleep before exiting to give time for error logs
        time.sleep(1)
