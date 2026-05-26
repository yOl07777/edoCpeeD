from __future__ import annotations

from python_src.components.mcp.CapabilitiesSection import CapabilitiesSection
from python_src.components.mcp.ElicitationDialog import ElicitationDialog
from python_src.components.mcp.MCPAgentServerMenu import MCPAgentServerMenu
from python_src.components.mcp.MCPListPanel import MCPListPanel
from python_src.components.mcp.MCPReconnect import MCPReconnect
from python_src.components.mcp.MCPRemoteServerMenu import MCPRemoteServerMenu
from python_src.components.mcp.MCPSettings import MCPSettings
from python_src.components.mcp.MCPStdioServerMenu import MCPStdioServerMenu
from python_src.components.mcp.MCPToolDetailView import MCPToolDetailView
from python_src.components.mcp.MCPToolListView import MCPToolListView
from python_src.components.mcp.McpParsingWarnings import McpParsingWarnings


default = {
    "provider": "deepseek",
    "components": [
        "CapabilitiesSection",
        "ElicitationDialog",
        "MCPListPanel",
        "MCPSettings",
        "MCPToolListView",
        "MCPToolDetailView",
    ],
}


__all__ = [
    "CapabilitiesSection",
    "ElicitationDialog",
    "MCPAgentServerMenu",
    "MCPListPanel",
    "MCPReconnect",
    "MCPRemoteServerMenu",
    "MCPSettings",
    "MCPStdioServerMenu",
    "MCPToolDetailView",
    "MCPToolListView",
    "McpParsingWarnings",
    "default",
]
