"""
Python migration draft for `src/services/api/errors.ts`.

This file was generated from the TypeScript source to preserve the
module boundary while the runtime implementation is migrated.
Claude/Anthropic model calls should be routed through `deepseek_code`.
"""

from __future__ import annotations

from typing import Any

API_ERROR_MESSAGE_PREFIX: Any = None
API_TIMEOUT_ERROR_MESSAGE: Any = None
CCR_AUTH_ERROR_MESSAGE: Any = None
CREDIT_BALANCE_TOO_LOW_ERROR_MESSAGE: Any = None
CUSTOM_OFF_SWITCH_MESSAGE: Any = None
INVALID_API_KEY_ERROR_MESSAGE: Any = None
INVALID_API_KEY_ERROR_MESSAGE_EXTERNAL: Any = None
OAUTH_ORG_NOT_ALLOWED_ERROR_MESSAGE: Any = None
ORG_DISABLED_ERROR_MESSAGE_ENV_KEY: Any = None
ORG_DISABLED_ERROR_MESSAGE_ENV_KEY_WITH_OAUTH: Any = None
PROMPT_TOO_LONG_ERROR_MESSAGE: Any = None
REPEATED_529_ERROR_MESSAGE: Any = None
TOKEN_REVOKED_ERROR_MESSAGE: Any = None

async def categorizeRetryableAPIError(*args: Any, **kwargs: Any) -> Any:
    """Migrated placeholder for TypeScript function `categorizeRetryableAPIError`."""
    raise NotImplementedError(
        "services.api.errors.categorizeRetryableAPIError still needs business-logic migration"
    )

async def classifyAPIError(*args: Any, **kwargs: Any) -> Any:
    """Migrated placeholder for TypeScript function `classifyAPIError`."""
    raise NotImplementedError(
        "services.api.errors.classifyAPIError still needs business-logic migration"
    )

async def extractUnknownErrorFormat(*args: Any, **kwargs: Any) -> Any:
    """Migrated placeholder for TypeScript function `extractUnknownErrorFormat`."""
    raise NotImplementedError(
        "services.api.errors.extractUnknownErrorFormat still needs business-logic migration"
    )

async def getAssistantMessageFromError(*args: Any, **kwargs: Any) -> Any:
    """Migrated placeholder for TypeScript function `getAssistantMessageFromError`."""
    raise NotImplementedError(
        "services.api.errors.getAssistantMessageFromError still needs business-logic migration"
    )

async def getErrorMessageIfRefusal(*args: Any, **kwargs: Any) -> Any:
    """Migrated placeholder for TypeScript function `getErrorMessageIfRefusal`."""
    raise NotImplementedError(
        "services.api.errors.getErrorMessageIfRefusal still needs business-logic migration"
    )

async def getImageTooLargeErrorMessage(*args: Any, **kwargs: Any) -> Any:
    """Migrated placeholder for TypeScript function `getImageTooLargeErrorMessage`."""
    raise NotImplementedError(
        "services.api.errors.getImageTooLargeErrorMessage still needs business-logic migration"
    )

async def getOauthOrgNotAllowedErrorMessage(*args: Any, **kwargs: Any) -> Any:
    """Migrated placeholder for TypeScript function `getOauthOrgNotAllowedErrorMessage`."""
    raise NotImplementedError(
        "services.api.errors.getOauthOrgNotAllowedErrorMessage still needs business-logic migration"
    )

async def getPdfInvalidErrorMessage(*args: Any, **kwargs: Any) -> Any:
    """Migrated placeholder for TypeScript function `getPdfInvalidErrorMessage`."""
    raise NotImplementedError(
        "services.api.errors.getPdfInvalidErrorMessage still needs business-logic migration"
    )

async def getPdfPasswordProtectedErrorMessage(*args: Any, **kwargs: Any) -> Any:
    """Migrated placeholder for TypeScript function `getPdfPasswordProtectedErrorMessage`."""
    raise NotImplementedError(
        "services.api.errors.getPdfPasswordProtectedErrorMessage still needs business-logic migration"
    )

async def getPdfTooLargeErrorMessage(*args: Any, **kwargs: Any) -> Any:
    """Migrated placeholder for TypeScript function `getPdfTooLargeErrorMessage`."""
    raise NotImplementedError(
        "services.api.errors.getPdfTooLargeErrorMessage still needs business-logic migration"
    )

async def getPromptTooLongTokenGap(*args: Any, **kwargs: Any) -> Any:
    """Migrated placeholder for TypeScript function `getPromptTooLongTokenGap`."""
    raise NotImplementedError(
        "services.api.errors.getPromptTooLongTokenGap still needs business-logic migration"
    )

async def getRequestTooLargeErrorMessage(*args: Any, **kwargs: Any) -> Any:
    """Migrated placeholder for TypeScript function `getRequestTooLargeErrorMessage`."""
    raise NotImplementedError(
        "services.api.errors.getRequestTooLargeErrorMessage still needs business-logic migration"
    )

async def getTokenRevokedErrorMessage(*args: Any, **kwargs: Any) -> Any:
    """Migrated placeholder for TypeScript function `getTokenRevokedErrorMessage`."""
    raise NotImplementedError(
        "services.api.errors.getTokenRevokedErrorMessage still needs business-logic migration"
    )

async def isMediaSizeError(*args: Any, **kwargs: Any) -> Any:
    """Migrated placeholder for TypeScript function `isMediaSizeError`."""
    raise NotImplementedError(
        "services.api.errors.isMediaSizeError still needs business-logic migration"
    )

async def isMediaSizeErrorMessage(*args: Any, **kwargs: Any) -> Any:
    """Migrated placeholder for TypeScript function `isMediaSizeErrorMessage`."""
    raise NotImplementedError(
        "services.api.errors.isMediaSizeErrorMessage still needs business-logic migration"
    )

async def isPromptTooLongMessage(*args: Any, **kwargs: Any) -> Any:
    """Migrated placeholder for TypeScript function `isPromptTooLongMessage`."""
    raise NotImplementedError(
        "services.api.errors.isPromptTooLongMessage still needs business-logic migration"
    )

async def isValidAPIMessage(*args: Any, **kwargs: Any) -> Any:
    """Migrated placeholder for TypeScript function `isValidAPIMessage`."""
    raise NotImplementedError(
        "services.api.errors.isValidAPIMessage still needs business-logic migration"
    )

async def parsePromptTooLongTokenCounts(*args: Any, **kwargs: Any) -> Any:
    """Migrated placeholder for TypeScript function `parsePromptTooLongTokenCounts`."""
    raise NotImplementedError(
        "services.api.errors.parsePromptTooLongTokenCounts still needs business-logic migration"
    )

async def startsWithApiErrorPrefix(*args: Any, **kwargs: Any) -> Any:
    """Migrated placeholder for TypeScript function `startsWithApiErrorPrefix`."""
    raise NotImplementedError(
        "services.api.errors.startsWithApiErrorPrefix still needs business-logic migration"
    )
