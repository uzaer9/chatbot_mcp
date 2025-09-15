# test_mcp.py
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def test_connection():
    server_params = StdioServerParameters(
        command="python",
        args=["-u", r"E:\Football_CB\mcp_server\soccer_server.py"],
    )
    
    async with stdio_client(server_params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            tools = await session.list_tools()
            print(f"Connected! Found {len(tools.tools)} tools")
            for tool in tools.tools:
                print(f"  - {tool.name}")

if __name__ == "__main__":
    asyncio.run(test_connection())