"""Every tool's input schema must be self-contained.

Some MCP clients and relays forward a tool's ``inputSchema`` without its
top-level ``$defs`` block. A schema that still contains ``$ref`` pointers
then references nothing, and the client rejects the tool (this is what
disabled ``generate_preset`` and ``edit_preset`` in the Claude desktop app).
"""

import asyncio
import json

from serum_mcp.server import mcp


def _tool_schemas() -> dict[str, dict]:
    tools = asyncio.run(mcp.list_tools())
    return {tool.name: tool.inputSchema for tool in tools}


def test_no_tool_schema_uses_defs_or_refs() -> None:
    for name, schema in _tool_schemas().items():
        text = json.dumps(schema)
        assert "$defs" not in text, f"{name} schema still has $defs"
        assert "$ref" not in text, f"{name} schema still has $ref"


def test_preset_tools_still_expose_spec_fields() -> None:
    schemas = _tool_schemas()
    for name in ("generate_preset", "edit_preset"):
        spec = schemas[name]["properties"]["spec"]
        assert "properties" in spec, f"{name} spec was not expanded"
        assert "oscillators" in spec["properties"]
