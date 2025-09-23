from mcp.server.fastmcp import FastMCP
import logging
logging.basicConfig(level=logging.INFO)

mcp = FastMCP("Strings")

@mcp.tool()
def echo(s: str) -> str: 
    """Echoes a string."""
    logging.info(f"echo(s=\"{s})\"")
    return s

@mcp.tool()
def reverse(s: str) -> str:
    """Reverses a string."""
    logging.info(f"reverse(s=\"{s})\"")
    return s[::-1]

@mcp.tool()
def length(s: str) -> int:
    """Gets the length of a string."""
    logging.info(f"length(s=\"{s})\"")
    return len(s)

if __name__ == "__main__": 
    mcp.run(transport='stdio')