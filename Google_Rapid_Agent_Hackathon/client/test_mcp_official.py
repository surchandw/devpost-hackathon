import asyncio
from mcp import ClientSession
from mcp.client.sse import sse_client

# Cloud Run Endpoint URL (Do not include a trailing slash)
SERVER_URL = "https://matchmarket-mcp-server-124170541983.us-central1.run.app/sse"

async def main():
    print(f"Initializing secure channel to FastMCP at: {SERVER_URL}")
    
    try:
        # The official sse_client natively establishes the stream and tracks the /messages URI redirection
        async with sse_client(SERVER_URL) as streams:
            async with ClientSession(streams[0], streams[1]) as session:
                
                # Step 1: Execute official protocol handshake
                print("Executing official protocol handshake...")
                await session.initialize()
                print("Handshake successful! Connection verified.")
                print("-" * 60)

                # Step 2: List Registered Operations
                print("Requesting complete Registered Tools directory...")
                tools_response = await session.list_tools()
                for tool in tools_response.tools:
                    print(f" - Found Tool: {tool.name} -> {tool.description}")
                print("-" * 60)

                # Step 3: Trigger a live tool call directly into MongoDB Atlas
                print("Simulating Agent tool execution call: find_items...")
                result = await session.call_tool(
                    name="find_items",
                    arguments={"category": "Merchandise"}
                )
                
                print("Live Database Result Returned to Client:")
                # Access the content block directly from the formal MCP structure
                for content_item in result.content:
                    print(content_item.text)
                print("-" * 60)

    except Exception as e:
        print(f"An error occurred during lifecycle tracking: {e}")

if __name__ == "__main__":
    # Run the asynchronous loop seamlessly
    asyncio.run(main())

