"""
AgentCore Gateway target for openfda_event_counts.

The capstone requires at least one tool exposed as an MCP target through
Gateway instead of an in-process function call. We picked
openfda_event_counts because it's SafetyAgent's most-used tool and it's a
clean, single-purpose REST call, which is exactly the shape Gateway's
OpenAPI-target ingestion wants: point it at the tool's JSON schema, get an
MCP-compatible tool back, no custom Lambda needed.

This module is NOT imported by the agent at runtime. It's the one-time
setup script you run against the AgentCore Gateway control plane; after
that, SafetyAgent's tool list swaps openfda_event_counts (in-process) for
the MCP client tool Gateway hands back (see runtime.py comment on the
USE_GATEWAY_FOR_SAFETY_TOOL flag).

Usage:
    python -m agent.gateway_target --create
"""
from __future__ import annotations

import argparse
import json
import os

OPENFDA_EVENT_COUNTS_SCHEMA = {
    "openapi": "3.0.0",
    "info": {"title": "openFDA Drug Event Counts", "version": "1.0.0"},
    "paths": {
        "/drug/event.json": {
            "get": {
                "operationId": "openfda_event_counts",
                "summary": "Get grouped adverse-event report counts for a drug from FAERS.",
                "parameters": [
                    {
                        "name": "search",
                        "in": "query",
                        "required": True,
                        "schema": {"type": "string"},
                        "description": (
                            'Lucene-style query, e.g. '
                            'patient.drug.medicinalproduct:"metformin"'
                        ),
                    },
                    {
                        "name": "count",
                        "in": "query",
                        "required": True,
                        "schema": {"type": "string"},
                        "description": "Field to group/count by, e.g. patient.reaction.reactionmeddrapt.exact",
                    },
                    {
                        "name": "limit",
                        "in": "query",
                        "required": False,
                        "schema": {"type": "integer", "minimum": 1, "maximum": 50},
                    },
                ],
                "responses": {"200": {"description": "Grouped counts"}},
            }
        }
    },
    "servers": [{"url": os.environ.get("OPENFDA_BASE_URL", "https://api.fda.gov")}],
}


def create_gateway_target(gateway_id: str) -> dict:
    """
    Registers OPENFDA_EVENT_COUNTS_SCHEMA as an OpenAPI target on an
    existing AgentCore Gateway. Requires the bedrock_agentcore_starter_toolkit
    (or boto3 bedrock-agentcore-control client) and appropriate IAM perms.
    """
    from bedrock_agentcore_starter_toolkit import GatewayClient

    client = GatewayClient(region_name="ap-south-1")
    target = client.create_target(
        gateway_id=gateway_id,
        name="openfda-event-counts",
        target_type="openApiSchema",
        schema=json.dumps(OPENFDA_EVENT_COUNTS_SCHEMA),
        credential_provider="NONE",  # openFDA's basic query endpoints are public/no-auth
    )
    return target


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--create", action="store_true")
    parser.add_argument("--gateway-id", default=os.environ.get("AGENTCORE_GATEWAY_ID", ""))
    args = parser.parse_args()

    if args.create:
        if not args.gateway_id:
            raise SystemExit("Pass --gateway-id or set AGENTCORE_GATEWAY_ID (create the Gateway itself via `agentcore gateway create` first).")
        result = create_gateway_target(args.gateway_id)
        print(json.dumps(result, indent=2, default=str))
    else:
        print("Nothing to do. Pass --create --gateway-id <id>.")
        print(json.dumps(OPENFDA_EVENT_COUNTS_SCHEMA, indent=2))