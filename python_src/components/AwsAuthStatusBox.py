from __future__ import annotations

from typing import Any

from python_src.components._shared import component_payload, option


async def AwsAuthStatusBox(*args: Any, **kwargs: Any) -> Any:
    profile = str(option(args, kwargs, "profile", "default"))
    region = str(option(args, kwargs, "region", option(args, kwargs, "awsRegion", "")))
    authenticated = bool(option(args, kwargs, "authenticated", option(args, kwargs, "signedIn", False)))
    return component_payload("aws_auth_status_box", profile=profile, region=region, authenticated=authenticated)


__all__ = ["AwsAuthStatusBox"]
