"""Release notes command."""

from __future__ import annotations

from typing import Any

from python_src.utils.releaseNotes import CHANGELOG_URL, getAllReleaseNotes, getStoredChangelog


def formatReleaseNotes(notes: list[tuple[str, list[str]]]) -> str:
    return "\n\n".join(f"Version {version}:\n" + "\n".join(f"- {note}" for note in items) for version, items in notes)


async def call(*_args: Any, **_kwargs: Any) -> dict[str, str]:
    cached = getAllReleaseNotes(await getStoredChangelog())
    if cached:
        return {"type": "text", "value": formatReleaseNotes(cached)}
    return {"type": "text", "value": f"See the full changelog at: {CHANGELOG_URL}"}
