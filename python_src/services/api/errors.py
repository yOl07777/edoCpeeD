"""DeepSeek/OpenAI compatible API error helpers."""

from __future__ import annotations

import json
import re
from typing import Any

API_ERROR_MESSAGE_PREFIX = "API Error:"
API_TIMEOUT_ERROR_MESSAGE = "DeepSeek API request timed out."
CCR_AUTH_ERROR_MESSAGE = "DeepSeek API authentication failed."
CREDIT_BALANCE_TOO_LOW_ERROR_MESSAGE = "DeepSeek account balance is too low."
CUSTOM_OFF_SWITCH_MESSAGE = "The API provider is currently disabled by configuration."
INVALID_API_KEY_ERROR_MESSAGE = "Invalid DeepSeek API key."
INVALID_API_KEY_ERROR_MESSAGE_EXTERNAL = "Invalid API key for the configured DeepSeek-compatible endpoint."
OAUTH_ORG_NOT_ALLOWED_ERROR_MESSAGE = "The selected organization is not allowed for this API request."
ORG_DISABLED_ERROR_MESSAGE_ENV_KEY = "Organization is disabled for API key authentication."
ORG_DISABLED_ERROR_MESSAGE_ENV_KEY_WITH_OAUTH = "Organization is disabled for OAuth authentication."
PROMPT_TOO_LONG_ERROR_MESSAGE = "Prompt is too long for the selected DeepSeek model."
REPEATED_529_ERROR_MESSAGE = "The provider is repeatedly overloaded. Please retry later or use another key/model."
TOKEN_REVOKED_ERROR_MESSAGE = "The API token was revoked."

_PROMPT_TOO_LONG_RE = re.compile(r"(prompt|context|tokens?).*(too long|maximum|exceed|overflow)", re.I)
_TOKEN_COUNTS_RE = re.compile(r"(?P<used>\d+)\D+(?:tokens?)\D+(?P<limit>\d+)", re.I)
_MEDIA_RE = re.compile(r"(image|pdf|file|media).*(too large|size|maximum|exceed)", re.I)


def _status_code(error: Any) -> int | None:
    if isinstance(error, dict):
        for key in ("status_code", "status", "code"):
            if isinstance(error.get(key), int):
                return error[key]
        response = error.get("response")
        if isinstance(response, dict) and isinstance(response.get("status_code"), int):
            return response["status_code"]
    for attr in ("status_code", "status", "code"):
        value = getattr(error, attr, None)
        if isinstance(value, int):
            return value
    response = getattr(error, "response", None)
    value = getattr(response, "status_code", None)
    return value if isinstance(value, int) else None


def _message(error: Any) -> str:
    if isinstance(error, str):
        return error
    if isinstance(error, dict):
        if isinstance(error.get("message"), str):
            return error["message"]
        nested = error.get("error")
        if isinstance(nested, dict) and isinstance(nested.get("message"), str):
            return nested["message"]
        return json.dumps(error, default=str, ensure_ascii=False)
    for attr in ("message", "detail"):
        value = getattr(error, attr, None)
        if value:
            return str(value)
    return str(error)


async def startsWithApiErrorPrefix(message: str) -> bool:
    return str(message or "").startswith(API_ERROR_MESSAGE_PREFIX)


async def isPromptTooLongMessage(message: str) -> bool:
    return bool(_PROMPT_TOO_LONG_RE.search(str(message or "")))


async def parsePromptTooLongTokenCounts(message: str) -> dict[str, int] | None:
    match = _TOKEN_COUNTS_RE.search(str(message or ""))
    if not match:
        return None
    used = int(match.group("used"))
    limit = int(match.group("limit"))
    return {"used": used, "limit": limit}


async def getPromptTooLongTokenGap(message: str) -> int | None:
    counts = await parsePromptTooLongTokenCounts(message)
    if not counts:
        return None
    return max(0, counts["used"] - counts["limit"])


async def isMediaSizeErrorMessage(message: str) -> bool:
    return bool(_MEDIA_RE.search(str(message or "")))


async def isMediaSizeError(error: Any) -> bool:
    return await isMediaSizeErrorMessage(_message(error))


async def isValidAPIMessage(message: Any) -> bool:
    return isinstance(message, str) and bool(message.strip())


async def extractUnknownErrorFormat(error: Any) -> dict[str, Any]:
    return {"status": _status_code(error), "message": _message(error), "type": type(error).__name__}


async def categorizeRetryableAPIError(error: Any) -> str:
    code = _status_code(error)
    msg = _message(error).lower()
    if code in {408, 409, 425, 429, 500, 502, 503, 504, 529}:
        return "retryable"
    if "timeout" in msg or "temporarily unavailable" in msg or "overloaded" in msg:
        return "retryable"
    if code in {401, 403}:
        return "auth"
    if code in {400, 413, 422} or await isPromptTooLongMessage(msg):
        return "request"
    return "unknown"


async def classifyAPIError(error: Any) -> dict[str, Any]:
    code = _status_code(error)
    message = _message(error)
    category = await categorizeRetryableAPIError(error)
    return {
        "status": code,
        "message": message,
        "category": category,
        "retryable": category == "retryable",
        "prompt_too_long": await isPromptTooLongMessage(message),
        "media_too_large": await isMediaSizeErrorMessage(message),
    }


async def getAssistantMessageFromError(error: Any) -> str:
    classified = await classifyAPIError(error)
    if classified["prompt_too_long"]:
        return PROMPT_TOO_LONG_ERROR_MESSAGE
    if classified["status"] == 401:
        return INVALID_API_KEY_ERROR_MESSAGE
    if classified["status"] == 429:
        return "DeepSeek API rate limit reached. Retrying with another configured key may help."
    if classified["retryable"]:
        return f"{API_ERROR_MESSAGE_PREFIX} {classified['message']}"
    return classified["message"]


async def getErrorMessageIfRefusal(response: Any) -> str | None:
    if isinstance(response, dict):
        message = response.get("refusal") or response.get("message")
        if message and str(response.get("finish_reason", "")).lower() == "content_filter":
            return str(message)
    return None


async def getImageTooLargeErrorMessage() -> str:
    return "Image is too large for the selected DeepSeek-compatible model."


async def getOauthOrgNotAllowedErrorMessage() -> str:
    return OAUTH_ORG_NOT_ALLOWED_ERROR_MESSAGE


async def getPdfInvalidErrorMessage() -> str:
    return "PDF file is invalid or cannot be parsed."


async def getPdfPasswordProtectedErrorMessage() -> str:
    return "PDF file is password protected."


async def getPdfTooLargeErrorMessage() -> str:
    return "PDF file is too large for the selected DeepSeek-compatible model."


async def getRequestTooLargeErrorMessage() -> str:
    return "Request body is too large for the selected DeepSeek-compatible endpoint."


async def getTokenRevokedErrorMessage() -> str:
    return TOKEN_REVOKED_ERROR_MESSAGE

