from __future__ import annotations

import re


_UNSAFE_TOKENS_RE = re.compile(
    r"(\brm\s+-[^\n;|&]*[rf]|"
    r"\bmkfs\b|\bdd\b|\bchmod\s+-R\b|\bchown\s+-R\b|"
    r":\(\)\s*\{\s*:\|:&\s*\};:|"
    r">\s*/dev/(sd[a-z]|nvme\d+n\d+|disk)|"
    r"\bcurl\b.+\|\s*(sh|bash)|\bwget\b.+\|\s*(sh|bash))",
    re.IGNORECASE,
)
_WRITE_REDIRECT_RE = re.compile(r"(?<![<])(?:^|\s)(?:>|>>)\s*[^&\s]", re.IGNORECASE)
_SAFE_HEREDOC_RE = re.compile(r"<<\s*'?(PY|PYTHON|EOF|SH)'?\s*\n", re.IGNORECASE)


def hasSafeHeredocSubstitution(command: str) -> bool:
    """Return true for simple quoted heredocs that do not execute substitutions."""
    return bool(_SAFE_HEREDOC_RE.search(command)) and "$(" not in command and "`" not in command


def stripSafeHeredocSubstitutions(command: str) -> str:
    if not hasSafeHeredocSubstitution(command):
        return command
    return re.sub(r"<<\s*'?(\w+)'?.*?\n\1", "<<HEREDOC", command, flags=re.IGNORECASE | re.DOTALL)


def bashCommandIsSafe_DEPRECATED(command: str) -> bool:
    """Conservative local safety classifier for migrated bash tooling."""
    normalized = stripSafeHeredocSubstitutions(command).strip()
    if not normalized:
        return False
    if _UNSAFE_TOKENS_RE.search(normalized):
        return False
    if _WRITE_REDIRECT_RE.search(normalized):
        return False
    return True


async def bashCommandIsSafeAsync_DEPRECATED(command: str) -> bool:
    return bashCommandIsSafe_DEPRECATED(command)
