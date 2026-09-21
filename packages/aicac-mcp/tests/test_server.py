"""
Tests for MCP server endpoints (resources and tool registration).

These tests verify the server correctly registers tools and resources,
without requiring a full MCP client connection.
"""

from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest

from aicac_mcp import server
from mcp import types

REPO_ROOT = Path(__file__).resolve().parents[3]


class TestServerResources:
    """Test MCP resource registration and reading."""

    @pytest.mark.asyncio
    async def test_list_resources(self):
        """Server lists all expected resources."""
        result = await server.handle_list_resources(None, None)
        
        assert len(result.resources) > 0
        
        uris = [r.uri for r in result.resources]
        
        assert "aicac://spec/v2/context.schema.json" in uris
        assert "aicac://spec/v2/architecture.schema.json" in uris
        assert "aicac://skill/router" in uris
        assert "aicac://skill/bootstrap" in uris
        assert "aicac://skill/validate" in uris

    @pytest.mark.asyncio
    async def test_read_schema_resource(self):
        """Server can read schema resources."""
        params = types.ReadResourceRequestParams(uri="aicac://spec/v2/context.schema.json")
        result = await server.handle_read_resource(None, params)
        
        assert result.contents
        assert len(result.contents) > 0
        content = result.contents[0].text
        assert content
        assert "$schema" in content or "type" in content

    @pytest.mark.asyncio
    async def test_read_skill_resource(self):
        """Server can read skill resources."""
        params = types.ReadResourceRequestParams(uri="aicac://skill/router")
        result = await server.handle_read_resource(None, params)
        
        assert result.contents
        content = result.contents[0].text
        assert content
        assert len(content) > 100

    @pytest.mark.asyncio
    async def test_read_invalid_resource(self):
        """Server rejects invalid resource URIs."""
        params = types.ReadResourceRequestParams(uri="aicac://invalid/path")
        with pytest.raises(ValueError):
            await server.handle_read_resource(None, params)


class TestServerTools:
    """Test MCP tool registration."""

    @pytest.mark.asyncio
    async def test_list_tools(self):
        """Server lists all expected tools."""
        result = await server.handle_list_tools(None, None)
        
        assert len(result.tools) == 5
        
        tool_names = [t.name for t in result.tools]
        
        assert "aicac_validate" in tool_names
        assert "aicac_bootstrap" in tool_names
        assert "aicac_generate_index" in tool_names
        assert "aicac_migrate" in tool_names
        assert "aicac_sync_suggest" in tool_names

    @pytest.mark.asyncio
    async def test_tool_schemas(self):
        """All tools have valid input schemas."""
        result = await server.handle_list_tools(None, None)
        
        for tool in result.tools:
            assert tool.name
            assert tool.description
            assert tool.input_schema
            assert tool.input_schema.get("type") == "object"
            assert "properties" in tool.input_schema

    @pytest.mark.asyncio
    async def test_validate_tool_schema(self):
        """aicac_validate has correct schema."""
        result = await server.handle_list_tools(None, None)
        validate = next(t for t in result.tools if t.name == "aicac_validate")
        
        props = validate.input_schema["properties"]
        assert "project_path" in props
        assert "strict" in props
        assert props["strict"]["type"] == "boolean"

    @pytest.mark.asyncio
    async def test_bootstrap_tool_schema(self):
        """aicac_bootstrap has correct schema."""
        result = await server.handle_list_tools(None, None)
        bootstrap = next(t for t in result.tools if t.name == "aicac_bootstrap")
        
        props = bootstrap.input_schema["properties"]
        assert "project_path" in props
        assert "compliance_level" in props
        assert "apply" in props
        assert "enum" in props["compliance_level"]
