"""Async MCP client used by the OpsPilot API to connect to the tool server."""
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client
from app.core.config import settings


async def list_remote_tools() -> list[dict]:
    async with streamablehttp_client(settings.MCP_SERVER_URL) as (read_stream, write_stream, _):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            result = await session.list_tools()
            return [tool.model_dump(mode="json") for tool in result.tools]


async def call_remote_tool(name: str, arguments: dict) -> dict:
    async with streamablehttp_client(settings.MCP_SERVER_URL) as (read_stream, write_stream, _):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            result = await session.call_tool(name, arguments)
            structured = getattr(result, "structuredContent", None)
            if structured is not None:
                return {"tool": name, "result": structured, "is_error": result.isError}
            content = []
            for item in result.content:
                if hasattr(item, "text"):
                    content.append(item.text)
            return {"tool": name, "content": content, "is_error": result.isError}
