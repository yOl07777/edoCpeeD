from __future__ import annotations

from typing import Any


def getPluginErrorMessage(error: dict[str, Any]) -> str:
    kind = error.get("type")
    if kind == "generic-error":
        return str(error.get("error", "Unknown plugin error"))
    if kind == "path-not-found":
        return f"Path not found: {error.get('path')} ({error.get('component')})"
    if kind == "git-auth-failed":
        return f"Git authentication failed ({error.get('authType')}): {error.get('gitUrl')}"
    if kind == "git-timeout":
        return f"Git {error.get('operation')} timeout: {error.get('gitUrl')}"
    if kind == "network-error":
        details = f" - {error.get('details')}" if error.get("details") else ""
        return f"Network error: {error.get('url')}{details}"
    if kind == "manifest-parse-error":
        return f"Manifest parse error: {error.get('parseError')}"
    if kind == "manifest-validation-error":
        return "Manifest validation failed: " + ", ".join(map(str, error.get("validationErrors") or []))
    if kind == "plugin-not-found":
        return f"Plugin {error.get('pluginId')} not found in marketplace {error.get('marketplace')}"
    if kind == "marketplace-not-found":
        return f"Marketplace {error.get('marketplace')} not found"
    if kind == "marketplace-load-failed":
        return f"Marketplace {error.get('marketplace')} failed to load: {error.get('reason')}"
    if kind == "mcp-config-invalid":
        return f"MCP server {error.get('serverName')} invalid: {error.get('validationError')}"
    if kind == "mcp-server-suppressed-duplicate":
        duplicate = str(error.get("duplicateOf", ""))
        dup = f'server provided by plugin "{duplicate.split(":", 1)[1] if ":" in duplicate else "?"}"' if duplicate.startswith("plugin:") else f'already-configured "{duplicate}"'
        return f'MCP server "{error.get("serverName")}" skipped - same command/URL as {dup}'
    if kind == "hook-load-failed":
        return f"Hook load failed: {error.get('reason')}"
    if kind == "component-load-failed":
        return f"{error.get('component')} load failed from {error.get('path')}: {error.get('reason')}"
    if kind == "mcpb-download-failed":
        return f"Failed to download MCPB from {error.get('url')}: {error.get('reason')}"
    if kind == "mcpb-extract-failed":
        return f"Failed to extract MCPB {error.get('mcpbPath')}: {error.get('reason')}"
    if kind == "mcpb-invalid-manifest":
        return f"MCPB manifest invalid at {error.get('mcpbPath')}: {error.get('validationError')}"
    if kind == "lsp-config-invalid":
        return f'Plugin "{error.get("plugin")}" has invalid LSP server config for "{error.get("serverName")}": {error.get("validationError")}'
    if kind == "lsp-server-start-failed":
        return f'Plugin "{error.get("plugin")}" failed to start LSP server "{error.get("serverName")}": {error.get("reason")}'
    if kind == "lsp-server-crashed":
        if error.get("signal"):
            return f'Plugin "{error.get("plugin")}" LSP server "{error.get("serverName")}" crashed with signal {error.get("signal")}'
        return f'Plugin "{error.get("plugin")}" LSP server "{error.get("serverName")}" crashed with exit code {error.get("exitCode", "unknown")}'
    if kind == "lsp-request-timeout":
        return f'Plugin "{error.get("plugin")}" LSP server "{error.get("serverName")}" timed out on {error.get("method")} request after {error.get("timeoutMs")}ms'
    if kind == "lsp-request-failed":
        return f'Plugin "{error.get("plugin")}" LSP server "{error.get("serverName")}" {error.get("method")} request failed: {error.get("error")}'
    if kind == "marketplace-blocked-by-policy":
        return (
            f"Marketplace '{error.get('marketplace')}' is blocked by enterprise policy"
            if error.get("blockedByBlocklist")
            else f"Marketplace '{error.get('marketplace')}' is not in the allowed marketplace list"
        )
    if kind == "dependency-unsatisfied":
        hint = "disabled - enable it or remove the dependency" if error.get("reason") == "not-enabled" else "not found in any configured marketplace"
        return f'Dependency "{error.get("dependency")}" is {hint}'
    if kind == "plugin-cache-miss":
        return f'Plugin "{error.get("plugin")}" not cached at {error.get("installPath")} - run /plugins to refresh'
    return f"Plugin error ({kind}): {error}"


__all__ = ["getPluginErrorMessage"]
