#!/usr/bin/env python3
"""
Example low-level MCP server demonstrating structured output support.

This example shows how to use the low-level server API to return
structured data from tools, with automatic validation against output
schemas.
"""

import asyncio
from datetime import datetime
from typing import Any


import mcp.types as types
from mcp.server.lowlevel import NotificationOptions, Server
from mcp.server.models import InitializationOptions

# Create low-level server instance
server = Server("structured-output-lowlevel-example")


@server.list_tools()
async def list_tools() -> list[types.Tool]:
    """List available tools with their schemas."""
    return [
        types.Tool(
            name="get_weather",
            description="Get weather information (simulated)",
            inputSchema={
                "type": "object",
                "properties": {"city": {"type": "string", "description": "City name"}},
                "required": ["city"],
            },
            outputSchema={
                "type": "object",
                "properties": {
                    "temperature": {"type": "number"},
                    "conditions": {"type": "string"},
                    "humidity": {"type": "integer", "minimum": 0, "maximum": 100},
                    "wind_speed": {"type": "number"},
                    "timestamp": {"type": "string", "format": "date-time"},
                },
                "required": ["temperature", "conditions", "humidity", "wind_speed", "timestamp"],
            },
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> Any:
    """
    Handle tool call with structured output.
    """

    if name == "get_weather":
        # city = arguments["city"]  # Would be used with real weather API

        # Simulate weather data (in production, call a real weather API)
        import random

        weather_conditions = ["sunny", "cloudy", "rainy", "partly cloudy", "foggy"]

        weather_data = {
            "temperature": round(random.uniform(0, 35), 1),
            "conditions": random.choice(weather_conditions),
            "humidity": random.randint(30, 90),
            "wind_speed": round(random.uniform(0, 30), 1),
            "timestamp": datetime.now().isoformat(),
        }

        # Return structured data only
        # The low-level server will serialize this to JSON content automatically
        return weather_data

    else:
        raise ValueError(f"Unknown tool: {name}")


async def run():
    """Run the low-level server using SSE transport."""
    from mcp.server.sse import SseServerTransport
    from starlette.applications import Starlette
    from starlette.responses import Response
    from starlette.routing import Mount, Route
    import uvicorn

    sse = SseServerTransport("/messages/")

    async def handle_sse(request):
        async with sse.connect_sse(
            request.scope, request.receive, request._send
        ) as streams:
            await server.run(
                streams[0], streams[1],
                InitializationOptions(
                    server_name="structured-output-lowlevel-example",
                    server_version="0.1.0",
                    capabilities=server.get_capabilities(
                        notification_options=NotificationOptions(),
                        experimental_capabilities={},
                    ),
                ),
            )
        return Response()

    starlette_app = Starlette(
        debug=True,
        routes=[
            Route("/sse", endpoint=handle_sse, methods=["GET"]),
            Mount("/messages/", app=sse.handle_post_message),
        ],
    )

    uvicorn.run(starlette_app, host="127.0.0.1", port=8000)


if __name__ == "__main__":
    asyncio.run(run())
