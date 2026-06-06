import os
import sys
import json
from typing import Optional
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import uvicorn
from pymongo import MongoClient, ReturnDocument

app = FastAPI(title="MatchMarket-HTTP-MCP-Engine")

db_client = None

def get_database():
    global db_client
    connection_string = os.environ.get("MDB_MCP_CONNECTION_STRING")
    if not connection_string:
        print("CRITICAL ERROR: MDB_MCP_CONNECTION_STRING is missing.", file=sys.stderr)
        sys.exit(1)
        
    if db_client is None:
        db_client = MongoClient(connection_string)
        print("Connected to MongoDB Atlas clusters successfully.", file=sys.stderr)
    return db_client["MatchMarket"]

# =====================================================================
# NATIVE MCP NATIVE OVER HTTP POST ROUTER
# =====================================================================

@app.post("/")
async def handle_mcp_http_request(request: Request) -> JSONResponse:
    """
    Natively processes formal Model Context Protocol (MCP) JSON-RPC 2.0 payloads
    directly over synchronous HTTP POST for Agent Studio compatibility.
    """
    try:
        body = await request.json()
        method = body.get("method")
        request_id = body.get("id", 0)
        
        # 1. HANDLE HANDSHAKE INITIALIZATION
        if method == "initialize":
            mcp_init_response = {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "protocolVersion": "2025-11-25",
                    "capabilities": {
                        "tools": {} # Notifies the engine we support functions
                    },
                    "serverInfo": {
                        "name": "MatchMarket-Core-Data-Engine",
                        "version": "1.0.0"
                    }
                }
            }
            return JSONResponse(mcp_init_response)

        # 2. HANDLE COMPILATION OF THE TOOLS DIRECTORY
        elif method == "tools/list":
            mcp_tools_list = {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "tools": [
                        {
                            "name": "find_items",
                            "description": "Queries the stock_inventory collection with optional filtering constraints.",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "category": {"type": "string", "description": "The target inventory segment, e.g. Merchandise or Equipment"}
                                }
                            }
                        },
                        {
                            "name": "update_stock_quantity",
                            "description": "Updates the stock count of an item dynamically by adding or subtracting units.",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "item_name": {"type": "string", "description": "Exact text name of the product"},
                                    "quantity_change": {"type": "integer", "description": "Positive integer to add, negative to subtract"}
                                },
                                "required": ["item_name", "quantity_change"]
                            }
                        }
                    ]
                }
            }
            return JSONResponse(mcp_tools_list)

        # 3. HANDLE LIVE CALLS INTO MONGODB ATLAS
        elif method == "tools/call":
            params = body.get("params", {})
            tool_name = params.get("name")
            arguments = params.get("arguments", {})
            
            db = get_database()
            output_content = ""

            if tool_name == "find_items":
                category = arguments.get("category", "Merchandise")
                cursor = db["stock_inventory"].find({"category": category}).limit(5)
                
                results = []
                for doc in cursor:
                    results.append(f"• {doc['name']}: {doc['quantity']} units available (Price: ${doc['price']})")
                
                if results:
                    output_content = f"Live inventory data for '{category}':\n\n" + "\n".join(results)
                else:
                    output_content = f"No active items found under category '{category}'."

            elif tool_name == "update_stock_quantity":
                item_name = arguments.get("item_name")
                change = int(arguments.get("quantity_change", 0))
                
                updated_doc = db["stock_inventory"].find_one_and_update(
                    {"name": item_name},
                    {"$inc": {"quantity": change}},
                    return_document=ReturnDocument.AFTER
                )
                if updated_doc:
                    output_content = f"Success! '{item_name}' balance updated. New count: {updated_doc['quantity']} units."
                else:
                    output_content = f"Error: Item '{item_name}' was not found in records."
            
            else:
                output_content = f"Unknown tool execution request: {tool_name}"

            # Format strictly as an MCP Content Item response block
            mcp_call_response = {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": output_content
                        }
                    ]
                }
            }
            return JSONResponse(mcp_call_response)

        # Catch-all fallback for other lifecycle notifications
        return JSONResponse({"jsonrpc": "2.0", "id": request_id, "result": {}})

    except Exception as e:
        print(f"Core Error: {str(e)}", file=sys.stderr)
        return JSONResponse({
            "jsonrpc": "2.0",
            "id": body.get("id", 0) if isinstance(body, dict) else 0,
            "error": {"code": -32603, "message": str(e)}
        }, status_code=200)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)

