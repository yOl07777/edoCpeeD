"""
Python migration draft for `src/utils/git.ts`.

This file was generated from the TypeScript source to preserve the
module boundary while the runtime implementation is migrated.
Claude/Anthropic model calls should be routed through `deepseek_code`.
"""

from __future__ import annotations

from typing import Any

dirIsInGitRepo: Any = None
findCanonicalGitRoot: Any = None
findGitRoot: Any = None
getBranch: Any = None
getChangedFiles: Any = None
getDefaultBranch: Any = None
getFileStatus: Any = None
getHead: Any = None
getIsClean: Any = None
getIsGit: Any = None
getIsHeadOnRemote: Any = None
getRemoteUrl: Any = None
getWorktreeCount: Any = None
gitExe: Any = None
hasUnpushedCommits: Any = None
stashToCleanState: Any = None

async def findRemoteBase(*args: Any, **kwargs: Any) -> Any:
    """Migrated placeholder for TypeScript function `findRemoteBase`."""
    raise NotImplementedError(
        "utils.git.findRemoteBase still needs business-logic migration"
    )

async def getGitDir(*args: Any, **kwargs: Any) -> Any:
    """Migrated placeholder for TypeScript function `getGitDir`."""
    raise NotImplementedError(
        "utils.git.getGitDir still needs business-logic migration"
    )

async def getGitState(*args: Any, **kwargs: Any) -> Any:
    """Migrated placeholder for TypeScript function `getGitState`."""
    raise NotImplementedError(
        "utils.git.getGitState still needs business-logic migration"
    )

async def getGithubRepo(*args: Any, **kwargs: Any) -> Any:
    """Migrated placeholder for TypeScript function `getGithubRepo`."""
    raise NotImplementedError(
        "utils.git.getGithubRepo still needs business-logic migration"
    )

async def getRepoRemoteHash(*args: Any, **kwargs: Any) -> Any:
    """Migrated placeholder for TypeScript function `getRepoRemoteHash`."""
    raise NotImplementedError(
        "utils.git.getRepoRemoteHash still needs business-logic migration"
    )

async def isAtGitRoot(*args: Any, **kwargs: Any) -> Any:
    """Migrated placeholder for TypeScript function `isAtGitRoot`."""
    raise NotImplementedError(
        "utils.git.isAtGitRoot still needs business-logic migration"
    )

async def isCurrentDirectoryBareGitRepo(*args: Any, **kwargs: Any) -> Any:
    """Migrated placeholder for TypeScript function `isCurrentDirectoryBareGitRepo`."""
    raise NotImplementedError(
        "utils.git.isCurrentDirectoryBareGitRepo still needs business-logic migration"
    )

async def normalizeGitRemoteUrl(*args: Any, **kwargs: Any) -> Any:
    """Migrated placeholder for TypeScript function `normalizeGitRemoteUrl`."""
    raise NotImplementedError(
        "utils.git.normalizeGitRemoteUrl still needs business-logic migration"
    )

async def preserveGitStateForIssue(*args: Any, **kwargs: Any) -> Any:
    """Migrated placeholder for TypeScript function `preserveGitStateForIssue`."""
    raise NotImplementedError(
        "utils.git.preserveGitStateForIssue still needs business-logic migration"
    )
