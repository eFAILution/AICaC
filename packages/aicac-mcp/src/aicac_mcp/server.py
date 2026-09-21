#!/usr/bin/env python3
"""
AICaC MCP Server

Model Context Protocol server providing AICaC v2.0 validation,
bootstrap, migration, and sync capabilities as MCP tools and resources.
"""

import asyncio
import json
import logging
from pathlib import Path
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp import types

from . import tools
from . import assets

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("aicac-mcp")


async def handle_list_resources(ctx, params) -> types.ListResourcesResult:
    """List available AICaC resources (schemas and skills)."""
    resources = []
    
    schema_files = [
        "context.schema.json",
        "architecture.schema.json",
        "workflows.schema.json",
        "decisions.schema.json",
        "errors.schema.json",
        "index.schema.json",
    ]
    
    for schema_file in schema_files:
        name = schema_file.replace(".schema.json", "")
        resources.append(types.Resource(
            uri=f"aicac://spec/v2/{schema_file}",
            name=f"AICaC v2.0 schema: {name}",
            mimeType="application/json",
            description=f"JSON Schema for .ai/{name}.yaml",
        ))
    
    skill_files = {
        "router.md": "Route query intents to the correct .ai/ file",
        "bootstrap.md": "Populate a fresh .ai/ directory",
        "validate.md": "Interpret validator output",
        "sync.md": "Update .ai/ after code changes",
        "migrate.md": "Migrate from v1.x to v2.0",
    }
    
    for skill_file, description in skill_files.items():
        skill_name = skill_file.replace(".md", "")
        resources.append(types.Resource(
            uri=f"aicac://skill/{skill_name}",
            name=f"AICaC skill: {skill_name}",
            mimeType="text/markdown",
            description=description,
        ))
    
    return types.ListResourcesResult(resources=resources)


async def handle_read_resource(ctx, params: types.ReadResourceRequestParams) -> types.ReadResourceResult:
    """Read a specific AICaC resource."""
    uri = params.uri
    
    try:
        if uri.startswith("aicac://spec/v2/"):
            schema_file = uri.replace("aicac://spec/v2/", "")
            schema_dir = assets.get_schemas_dir()
            schema_path = schema_dir / schema_file
            
            if not schema_path.exists():
                raise ValueError(f"Schema not found: {schema_file}")
            
            content = schema_path.read_text()
            return types.ReadResourceResult(
                contents=[types.TextResourceContents(
                    uri=uri,
                    mimeType="application/json",
                    text=content,
                )]
            )
        
        elif uri.startswith("aicac://skill/"):
            skill_name = uri.replace("aicac://skill/", "")
            skills_dir = assets.get_skills_dir()
            skill_path = skills_dir / f"{skill_name}.md"
            
            if not skill_path.exists():
                raise ValueError(f"Skill not found: {skill_name}")
            
            content = skill_path.read_text()
            return types.ReadResourceResult(
                contents=[types.TextResourceContents(
                    uri=uri,
                    mimeType="text/markdown",
                    text=content,
                )]
            )
        
        else:
            raise ValueError(f"Unknown resource URI: {uri}")
    
    except FileNotFoundError as e:
        # Return error as resource content
        return types.ReadResourceResult(
            contents=[types.TextResourceContents(
                uri=uri,
                mimeType="text/plain",
                text=f"Resource unavailable: {e}",
            )]
        )


async def handle_list_tools(ctx, params) -> types.ListToolsResult:
    """List available AICaC tools."""
    tool_list = [
        types.Tool(
            name="aicac_validate",
            description="Validate .ai/ against v2.0 schemas, cross-references, and content quality heuristics.",
            input_schema={
                "type": "object",
                "properties": {
                    "project_path": {
                        "type": "string",
                        "description": "Path to project root (default: current directory)",
                        "default": ".",
                    },
                    "strict": {
                        "type": "boolean",
                        "description": "Treat warnings as errors (default: false)",
                        "default": False,
                    },
                },
            },
        ),
        types.Tool(
            name="aicac_bootstrap",
            description="Create a v2.0 AICaC structure in a project. Detects project type and emits AGENTS.md + .ai/*.yaml skeletons.",
            input_schema={
                "type": "object",
                "properties": {
                    "project_path": {
                        "type": "string",
                        "description": "Path to project root (default: current directory)",
                        "default": ".",
                    },
                    "compliance_level": {
                        "type": "string",
                        "enum": ["minimal", "standard", "comprehensive"],
                        "description": "Target compliance level (default: minimal)",
                        "default": "minimal",
                    },
                    "apply": {
                        "type": "boolean",
                        "description": "Apply changes (default: false for dry-run)",
                        "default": False,
                    },
                },
            },
        ),
        types.Tool(
            name="aicac_generate_index",
            description="Regenerate .ai/index.yaml — the token-cheap routing table listing ids per file.",
            input_schema={
                "type": "object",
                "properties": {
                    "project_path": {
                        "type": "string",
                        "description": "Path to project root (default: current directory)",
                        "default": ".",
                    },
                    "apply": {
                        "type": "boolean",
                        "description": "Apply changes (default: false for dry-run)",
                        "default": False,
                    },
                },
            },
        ),
        types.Tool(
            name="aicac_migrate",
            description="Migrate a v1.x .ai/ directory to v2.0 canonical shape (list-of-items → dict-keyed-by-id, common_commands → common_tasks, etc.).",
            input_schema={
                "type": "object",
                "properties": {
                    "project_path": {
                        "type": "string",
                        "description": "Path to project root (default: current directory)",
                        "default": ".",
                    },
                    "apply": {
                        "type": "boolean",
                        "description": "Apply changes (default: false for dry-run)",
                        "default": False,
                    },
                },
            },
        ),
        types.Tool(
            name="aicac_sync_suggest",
            description="Given a set of changed source files, return the list of changed paths alongside all .ai/*.yaml files that could plausibly need updates. The model decides which actually need editing.",
            input_schema={
                "type": "object",
                "properties": {
                    "project_path": {
                        "type": "string",
                        "description": "Path to project root (default: current directory)",
                        "default": ".",
                    },
                    "changed_files": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of changed files (if omitted, uses git diff HEAD)",
                    },
                },
            },
        ),
    ]
    return types.ListToolsResult(tools=tool_list)


async def handle_call_tool(ctx, params: types.CallToolRequestParams) -> types.CallToolResult:
    """Execute an AICaC tool."""
    name = params.name
    arguments = params.arguments or {}
    
    try:
        if name == "aicac_validate":
            result = tools.validate_project(
                project_path=arguments.get("project_path", "."),
                strict=arguments.get("strict", False),
            )
            
        elif name == "aicac_bootstrap":
            result = tools.bootstrap_project(
                project_path=arguments.get("project_path", "."),
                compliance_level=arguments.get("compliance_level", "minimal"),
                apply=arguments.get("apply", False),
            )
            
        elif name == "aicac_generate_index":
            result = tools.generate_index(
                project_path=arguments.get("project_path", "."),
                apply=arguments.get("apply", False),
            )
            
        elif name == "aicac_migrate":
            result = tools.migrate_project(
                project_path=arguments.get("project_path", "."),
                apply=arguments.get("apply", False),
            )
            
        elif name == "aicac_sync_suggest":
            result = tools.sync_suggest(
                project_path=arguments.get("project_path", "."),
                changed_files=arguments.get("changed_files"),
            )
            
        else:
            raise ValueError(f"Unknown tool: {name}")
        
        return types.CallToolResult(
            content=[types.TextContent(
                type="text",
                text=json.dumps(result, indent=2),
            )]
        )
        
    except Exception as e:
        logger.error(f"Error executing {name}: {e}", exc_info=True)
        return types.CallToolResult(
            content=[types.TextContent(
                type="text",
                text=json.dumps({
                    "error": str(e),
                    "tool": name,
                }, indent=2),
            )],
            isError=True,
        )


async def main_async():
    """Run the MCP server."""
    server = Server(
        "aicac-mcp",
        version="2.0.0",
        on_list_resources=handle_list_resources,
        on_read_resource=handle_read_resource,
        on_list_tools=handle_list_tools,
        on_call_tool=handle_call_tool,
    )
    
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options(),
        )


def main():
    """Entry point for the aicac-mcp command."""
    asyncio.run(main_async())


if __name__ == "__main__":
    main()
