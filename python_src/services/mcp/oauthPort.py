"""OAuth redirect port helpers for MCP auth flows."""

from __future__ import annotations

import socket


async def buildRedirectUri(port: int, path: str = "/callback", host: str = "127.0.0.1") -> str:
    """Build a local OAuth redirect URI."""

    normalized_path = path if path.startswith("/") else f"/{path}"
    return f"http://{host}:{int(port)}{normalized_path}"


async def findAvailablePort(start_port: int = 54545, host: str = "127.0.0.1", attempts: int = 100) -> int:
    """Find an available local TCP port for OAuth callbacks."""

    for port in range(int(start_port), int(start_port) + int(attempts)):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                sock.bind((host, port))
            except OSError:
                continue
            return port
    raise RuntimeError(f"No available port found from {start_port} after {attempts} attempts")
