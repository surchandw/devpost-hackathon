# MatchMarket Logistics Engine: Workspace Configuration

This repository houses the core codebase, tool execution layers, and integration suites for the **MatchMarket Logistics Engine**—an autonomous inventory assistant powered by the Google Agent Development Kit (ADK), Gemini 3.5 Flash, and MongoDB Atlas.

---

## Architectural Data Separation
* **Primary Cloud Datastore (Partner Track):** MongoDB Atlas (Hosting the core production `inventory` and `events` collections via the Model Context Protocol server).
* **Stateful Session Memory:** Local, non-networked SQLite (`aiosqlite`) acting strictly as an ephemeral conversational history cache inside the application instances.

---

## Repository Structure

The workspace is structured into specialized modules to isolate the agent logic, backend server drivers, and verification assets:

Google_Rapid_Agent_Hackathon
├── agent/                  # Core Google ADK Agent source files & system prompts
├── mcp_server/             # Model Context Protocol (MCP) server source code & tool mappings
├── client/                 # Seeding scripts, local MCP test harnesses, and validation test cases
└── info.txt                # Production deployment variables, metrics, and Docker build manifests


Prerequisites & Infrastructure Setup:
Docker must be installed before compiling container artifacts. Please refer to the Official Docker Installation Guide for details. 
Google ADK and the gcloud CLI toolchain are required for local workspace testing.

Initialize your Artifact Registry Repository:
Run the following command to establish your target Docker image host repository in Google Cloud Platform:
gcloud artifacts repositories create matchmarket-repo \
    --repository-format=docker \
    --location=us-central1 \
    --description="MatchMarket Hackathon Container Repository"



Directory Breakdown & Component Specifications:
1. mcp_server/
This directory contains the source code for the MongoDB Atlas Model Context Protocol (MCP) server layer.

Build the MCP Server Image:
gcloud builds submit --tag us-central1-docker.pkg.dev/gen-lang-client-0729100476/matchmarket-repo/mcp-server:latest .

Deploy the MCP Server to Google Cloud Run:
gcloud run deploy matchmarket-mcp-server \
  --image us-central1-docker.pkg.dev/gen-lang-client-0729100476/matchmarket-repo/mcp-server:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars MDB_MCP_CONNECTION_STRING="mongodb+srv://<USER>:<PASSWORD>@<YOUR_CLUSTER>.mongodb.net/MatchMarket"
  

2. agent/
Contains the core Google ADK agent logic. Update your environment flags within the .env file located inside this target folder before compiling the container layer.
Build the Google ADK Agent Image:
gcloud builds submit --tag us-central1-docker.pkg.dev/gen-lang-client-0729100476/matchmarket-repo/adk-agent:latest .

Deploy the Agent Container to Google Cloud Run:
gcloud run deploy matchmarket-logistics-agent \
  --image us-central1-docker.pkg.dev/gen-lang-client-0729100476/matchmarket-repo/adk-agent:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
  
3. client/
Houses workspace utility assets designed to validate system stability and hydrate data models:

seed_data.py: Automates target collection creation and structures initial documents within MongoDB Atlas.

test_mcp_official.py: A lightweight client module used to verify error-free MCP server connectivity.

test_case.txt: A comprehensive manifest of baseline project verification scenarios.

4. info.txt
A secure workspace file documenting database connection paths, deployment environmental logs, and secondary setup parameters.































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


Docker must be install before building the image. Please refer to https://docs.docker.com/engine/install/ on how to install docker.
Google ADK, and gcloud softwares are require to test locally. 
Create a Docker repository in Artifact Registry:

gcloud artifacts repositories create matchmarket-repo \
    --repository-format=docker \
    --location=us-central1 \
    --description="MatchMarket Hackathon MCP Server Repository"


Directory Breakdown & Component Specifications
==============================================
1. mcp_server -
---------------
This directory contains the MongoDB Atlas MCP server source code. 

Build the mcp server image:

gcloud builds submit --tag us-central1-docker.pkg.dev/gen-lang-client-0729100476/matchmarket-repo/mcp-server:py-v1 .

Deploy MongoDB MCP server to cloud Run:

gcloud run deploy matchmarket-mcp-server \
  --image us-central1-docker.pkg.dev/gen-lang-client-0729100476/matchmarket-repo/mcp-server:py-v9 \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars MDB_MCP_CONNECTION_STRING="mongodb+srv://admin:MyPassword123@cluster0.pvpecbn.mongodb.net/MatchMarket"

2. agent -
----------
It contains Google ADK agent source code. Update correct project details in .env located inside this folder.

Build Google ADK agent docker image:

gcloud builds submit --tag us-central1-docker.pkg.dev/gen-lang-client-0729100476/matchmarket-repo/adk-agent:v1 .

Deploy the Google ADK agent docker image to the Cloud Run:

gcloud run deploy matchmarket-logistics-agent \
  --image us-central1-docker.pkg.dev/gen-lang-client-0729100476/matchmarket-repo/adk-agent:v1 \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated

3. client -
-----------
This directory contains three files - 
seed_data.py - MonoDB collection creation file
test_mcp_official.py - MongoDB MCP server test client
test_case.txt - Project test cases.


4. info.txt -
-------------
Contains database connection string details and commands to build and deploy docker images.
