from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class McpResource:
    uri: str
    name: str
    content: str
    mime_type: str = "text/plain"
    server: str = "local"

    def summary(self) -> dict[str, Any]:
        return {
            "uri": self.uri,
            "name": self.name,
            "mime_type": self.mime_type,
            "server": self.server,
        }

    def to_dict(self) -> dict[str, Any]:
        return {
            **self.summary(),
            "content": self.content,
        }


RESOURCES: dict[str, McpResource] = {}


def register_resource(
    uri: str,
    content: str,
    *,
    name: str | None = None,
    mime_type: str = "text/plain",
    server: str = "local",
) -> McpResource:
    resource = McpResource(
        uri=uri,
        name=name or uri,
        content=content,
        mime_type=mime_type,
        server=server,
    )
    RESOURCES[uri] = resource
    return resource


def list_resources(server: str | None = None) -> list[McpResource]:
    resources = list(RESOURCES.values())
    if server:
        resources = [resource for resource in resources if resource.server == server]
    return resources


def read_resource(uri: str) -> McpResource:
    try:
        return RESOURCES[uri]
    except KeyError as exc:
        raise KeyError(f"Unknown MCP resource URI: {uri}") from exc
