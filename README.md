MatchMarket Logistics Engine: Workspace Configuration
=====================================================
This repository houses the core codebase, tool execution layers, and integration suites for the MatchMarket Logistics Engine —
an autonomous inventory assistant powered by the Google Agent Development Kit (ADK), Gemini 3.5 Flash, and MongoDB Atlas.

Repository Structure
====================
The workspace is structured into specialized modules to isolate the agent logic, backend server drivers, and verification assets:

Google_Rapid_Agent_Hackathon
├── agent/                  # Core ADK Agent files
├── mcp_server/             # Model Context Protocol (MCP) server drivers 
├── client/                 # Seeding scripts, local MCP automated tests, and verification test cases
└── info.txt                # Production deployment variables, connection strings, and Docker build manifests


