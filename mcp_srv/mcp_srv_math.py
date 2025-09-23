from fastmcp import FastMCP
from fastmcp.server.auth import BearerAuthProvider
import logging
logging.basicConfig(level=logging.INFO)

with open('../pubkey.txt', 'r') as f:
    pubkey = f.read()

auth = BearerAuthProvider(
    public_key=pubkey,
    issuer="https://dev.example.com",
    audience="my-dev-server"
)
print(auth)

mcp = FastMCP(name="Math", auth=auth)

@mcp.tool()
def add(a: int, b: int) -> int: 
    """Adds a and b."""
    logging.info(f"add(a={a}, b={b})")
    return a + b

@mcp.tool()
def multiply(a: int, b: int) -> int:
    """Multiplies a and b."""
    logging.info(f"multiply(a={a}, b={b})")
    return a * b

@mcp.tool()
def math_tool_works() -> str:
    """Confirm the math tool works."""
    logging.info("math_tool_works()")
    return 'The math tool works! 12341234'

if __name__ == "__main__": 
    mcp.run(transport='streamable-http')