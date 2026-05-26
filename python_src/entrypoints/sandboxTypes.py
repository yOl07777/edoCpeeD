from __future__ import annotations


SandboxFilesystemConfigSchema = {
    "type": "object",
    "properties": {"read": {"type": "array"}, "write": {"type": "array"}, "mode": {"type": "string"}},
}
SandboxNetworkConfigSchema = {
    "type": "object",
    "properties": {"enabled": {"type": "boolean"}, "allowedHosts": {"type": "array"}},
}
SandboxSettingsSchema = {
    "type": "object",
    "properties": {"filesystem": SandboxFilesystemConfigSchema, "network": SandboxNetworkConfigSchema},
}


__all__ = ["SandboxFilesystemConfigSchema", "SandboxNetworkConfigSchema", "SandboxSettingsSchema"]
