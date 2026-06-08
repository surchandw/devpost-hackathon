import os
import sys
import json
from typing import Optional
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import uvicorn
from pymongo import MongoClient, ReturnDocument

app = FastAPI(title="MatchMarket-Logistics-Webhook")
db_client = None

def get_database():
    global db_client
    connection_string = os.environ.get("MDB_MCP_CONNECTION_STRING")
    if not connection_string:
        print("CRITICAL ERROR: MDB_MCP_CONNECTION_STRING is missing.", file=sys.stderr)
        sys.exit(1)
    if db_client is None:
        db_client = MongoClient(connection_string)
    return db_client["MatchMarket"]

# =====================================================================
# UNIFIED NATIVE MCP OVER HTTP POST ROUTER
# =====================================================================

@app.post("/")
async def handle_mcp_http_request(request: Request) -> JSONResponse:
    try:
        body = await request.json()
        method = body.get("method")
        request_id = body.get("id", 0)
        
        if method == "initialize":
            return JSONResponse({
                "jsonrpc": "2.0", "id": request_id,
                "result": {
                    "protocolVersion": "2025-11-25",
                    "capabilities": {"tools": {}},
                    "serverInfo": {"name": "MatchMarket-Logistics-Engine", "version": "2.0.0"}
                }
            })

        elif method == "tools/list":
            return JSONResponse({
                "jsonrpc": "2.0", "id": request_id,
                "result": {
                    "tools": [
                        {
                            "name": "lookup_logistics_data",
                            "description": "Audits database logs across stock_inventory, promotions, match_events, staff_schedule, or supplier_orders.",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "collection": {"type": "string", "enum": ["stock_inventory", "promotions", "match_events", "staff_schedule", "supplier_orders"]},
                                    "filter_key": {"type": "string", "description": "Field to filter by (e.g., 'category', 'status', 'event_name')"},
                                    "filter_value": {"type": "string", "description": "The exact value to search for"}
                                },
                                "required": ["collection"]
                            }
                        },
                        {
                            "name": "modify_logistics_record",
                            "description": "Applies number adjustments, shifts quantities, or updates status fields across all operational collections.",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "collection": {"type": "string", "enum": ["stock_inventory", "promotions", "match_events", "staff_schedule", "supplier_orders"]},
                                    "search_key": {"type": "string", "description": "Field to identify the document (e.g., 'name', 'event_id', 'order_number')"},
                                    "search_value": {"type": "string", "description": "Value identifying the document row"},
                                    "update_field": {"type": "string", "description": "The field being modified (e.g., 'quantity', 'status')"},
                                    "adjustment_value": {"type": "string", "description": "The new text status or numeric value to change/increment"}
                                },
                                "required": ["collection", "search_key", "search_value", "update_field", "adjustment_value"]
                            }
                        }
                    ]
                }
            })

        elif method == "tools/call":
            params = body.get("params", {})
            tool_name = params.get("name")
            args = params.get("arguments", {})
            db = get_database()
            target_coll = args.get("collection")
            
            output_text = ""

            # 1. READ CHANNELS: HUMAN READABLE MAPPING
            if tool_name == "lookup_logistics_data":
                query = {}
                fk = args.get("filter_key")
                fv = args.get("filter_value")
                if fk and fv and fk.strip() and fv.strip():
                    query[fk] = fv
    
                cursor = db[target_coll].find(query).limit(50)
                lines = []
    
                for doc in cursor:
                    if target_coll == "stock_inventory":
                        lines.append(f"• Item: {doc.get('name', doc.get('item_name'))} | Stock: {doc.get('quantity', doc.get('shelf_stock', 0))} units | Price: ${doc.get('price', 0)}")
                    elif target_coll == "match_events":
                        lines.append(f"• Event: {doc.get('title', doc.get('event_name', 'Unassigned'))} | Date: {doc.get('date_time', doc.get('date', 'TBD'))} | Venue: {doc.get('location', doc.get('venue', 'TBD'))} | Status: {doc.get('status', 'Scheduled')}")
                    elif target_coll == "promotions":
                        lines.append(f"• Campaign: {doc.get('campaign_name', 'Clearance')} | Target: {doc.get('target_item', 'All')} | Status: {doc.get('status', 'Active')}")
                    elif target_coll == "staff_schedule":
                        lines.append(f"• Staff: {doc.get('staff_name', 'Vacant')} | Role: {doc.get('role', 'Floor Lead')} | Shift: {doc.get('shift', 'Match Day')} | Status: {doc.get('status', 'Assigned')}")
                    elif target_coll == "supplier_orders":
                        lines.append(f"• Order: {doc.get('order_number', 'MM-01')} | Item: {doc.get('item_name')} | Status: {doc.get('status', 'Pending')}")
                
                if lines:
                    output_text = f"Successfully synchronized database records for '{target_coll}':\n\n" + "\n".join(lines)
                else:
                    output_text = f"Logistics check complete: No matching records found inside '{target_coll}'."

            # 2. WRITE CHANNELS: TRANSACTION HANDLING
            elif tool_name == "modify_logistics_record":
                search_query = {args.get("search_key"): args.get("search_value")}
                field = args.get("update_field")
                val = args.get("adjustment_value")
                
                try:
                    update_op = {"$inc": {field: int(val)}}
                except ValueError:
                    update_op = {"$set": {field: val}}
                    
                updated_doc = db[target_coll].find_one_and_update(
                    search_query, update_op, return_document=ReturnDocument.AFTER
                )
                
                if updated_doc:
                    output_text = f"Transaction Confirmed: Record '{args.get('search_value')}' inside '{target_coll}' has been successfully updated. Field '{field}' is now set to '{updated_doc.get(field)}'."
                else:
                    output_text = f"Transaction Declined: Target record '{args.get('search_value')}' was not found inside '{target_coll}'."

            # WRAP COMPLIANTLY IN THE CHOSEN INTERFACE LAYER
            sanitized_text = output_text.replace("\n", "  ").replace("•", "-")
            return JSONResponse({
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "content": [{"type": "text", "text": sanitized_text}]
                }
            })

        return JSONResponse({"jsonrpc": "2.0", "id": request_id, "result": {}})
    except Exception as e:
        return JSONResponse({
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {"code": -32603, "message": str(e)}
        })

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))

