"""Lightweight DeepSeek Code usage insights command.

This is a practical migration of the Claude-specific insights command.  It
keeps the public exports and report shape while using local JSONL scanning and
deterministic summaries instead of Claude/Anthropic model calls.
"""

from __future__ import annotations

import html
import json
import os
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


def _config_home() -> Path:
    return Path(
        os.environ.get("DEEPCODE_CONFIG_HOME")
        or os.environ.get("DEEPSEEK_CODE_HOME")
        or os.environ.get("CLAUDE_CONFIG_DIR")
        or (Path.home() / ".deepseek")
    )


def _data_dir() -> Path:
    return _config_home() / "usage-data"


def _projects_dir() -> Path:
    for candidate in (_config_home() / "projects", Path.cwd() / ".deepseek" / "projects"):
        if candidate.exists():
            return candidate
    return _config_home() / "projects"


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _safe_parse(line: str) -> dict[str, Any] | None:
    try:
        value = json.loads(line)
    except json.JSONDecodeError:
        return None
    return value if isinstance(value, dict) else None


def _iter_session_files(projects_dir: Path) -> Iterable[Path]:
    if not projects_dir.exists():
        return []
    return sorted(projects_dir.rglob("*.jsonl"), key=lambda p: p.stat().st_mtime, reverse=True)


def _message_text(message: Any) -> str:
    if isinstance(message, str):
        return message
    if not isinstance(message, dict):
        return ""
    content = message.get("content")
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        pieces: list[str] = []
        for block in content:
            if isinstance(block, dict) and block.get("type") == "text":
                pieces.append(str(block.get("text", "")))
            elif isinstance(block, str):
                pieces.append(block)
        return "\n".join(piece for piece in pieces if piece)
    return ""


def _tool_names(message: Any) -> list[str]:
    if not isinstance(message, dict):
        return []
    content = message.get("content")
    names: list[str] = []
    if isinstance(content, list):
        for block in content:
            if isinstance(block, dict):
                if block.get("type") in {"tool_use", "tool_call"} and block.get("name"):
                    names.append(str(block["name"]))
                if block.get("type") == "tool_result" and block.get("tool_use_id"):
                    names.append("tool_result")
    for call in message.get("tool_calls") or []:
        if isinstance(call, dict):
            fn = call.get("function") or {}
            names.append(str(fn.get("name") or call.get("name") or "tool_call"))
    return names


def _session_id_from_path(path: Path) -> str:
    return path.stem


def _scan_session_file(path: Path) -> dict[str, Any]:
    user_messages = 0
    assistant_messages = 0
    tool_counts: Counter[str] = Counter()
    first_prompt = ""
    timestamps: list[str] = []
    input_tokens = 0
    output_tokens = 0

    for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        event = _safe_parse(line)
        if not event:
            continue
        msg_type = event.get("type") or event.get("role")
        msg = event.get("message", event)
        ts = event.get("timestamp") or (msg.get("timestamp") if isinstance(msg, dict) else None)
        if isinstance(ts, str):
            timestamps.append(ts)
        if msg_type == "user":
            user_messages += 1
            if not first_prompt:
                first_prompt = _message_text(msg)[:300]
        elif msg_type == "assistant":
            assistant_messages += 1
            tool_counts.update(_tool_names(msg))
            usage = msg.get("usage", {}) if isinstance(msg, dict) else {}
            if isinstance(usage, dict):
                input_tokens += int(usage.get("input_tokens") or 0)
                output_tokens += int(usage.get("output_tokens") or 0)

    start_time = min(timestamps) if timestamps else datetime.fromtimestamp(path.stat().st_mtime, timezone.utc).isoformat()
    end_time = max(timestamps) if timestamps else start_time
    return {
        "session_id": _session_id_from_path(path),
        "project_path": str(path.parent),
        "start_time": start_time,
        "end_time": end_time,
        "duration_minutes": 0,
        "user_message_count": user_messages,
        "assistant_message_count": assistant_messages,
        "tool_counts": dict(tool_counts),
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "first_prompt": first_prompt,
    }


def deduplicateSessionBranches(sessions: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    best: dict[str, dict[str, Any]] = {}
    for session in sessions:
        sid = str(session.get("session_id") or session.get("id") or "")
        if not sid:
            continue
        current = best.get(sid)
        if current is None or int(session.get("user_message_count", 0)) > int(current.get("user_message_count", 0)):
            best[sid] = dict(session)
    return sorted(best.values(), key=lambda item: str(item.get("start_time", "")), reverse=True)


def detectMultiClauding(sessions: Iterable[dict[str, Any]]) -> dict[str, int]:
    """Approximate overlapping local sessions from start/end timestamps."""

    intervals: list[tuple[str, str, str]] = []
    for session in sessions:
        start = str(session.get("start_time") or "")
        end = str(session.get("end_time") or start)
        sid = str(session.get("session_id") or "")
        if start and sid:
            intervals.append((start, end, sid))
    overlap_events = 0
    involved: set[str] = set()
    for idx, (start, end, sid) in enumerate(intervals):
        for other_start, other_end, other_sid in intervals[idx + 1 :]:
            if start <= other_end and other_start <= end:
                overlap_events += 1
                involved.update({sid, other_sid})
    return {"overlap_events": overlap_events, "sessions_involved": len(involved), "user_messages_during": 0}


def _aggregate(sessions: list[dict[str, Any]]) -> dict[str, Any]:
    tool_counts: Counter[str] = Counter()
    projects: Counter[str] = Counter()
    for session in sessions:
        tool_counts.update(session.get("tool_counts") or {})
        projects[str(session.get("project_path") or "unknown")] += 1
    start_values = [str(s.get("start_time")) for s in sessions if s.get("start_time")]
    total_user = sum(int(s.get("user_message_count", 0)) for s in sessions)
    total_assistant = sum(int(s.get("assistant_message_count", 0)) for s in sessions)
    return {
        "total_sessions": len(sessions),
        "total_sessions_scanned": len(sessions),
        "sessions_with_facets": 0,
        "date_range": {
            "start": min(start_values)[:10] if start_values else "unknown",
            "end": max(start_values)[:10] if start_values else "unknown",
        },
        "total_messages": total_user + total_assistant,
        "total_duration_hours": 0,
        "total_input_tokens": sum(int(s.get("input_tokens", 0)) for s in sessions),
        "total_output_tokens": sum(int(s.get("output_tokens", 0)) for s in sessions),
        "tool_counts": dict(tool_counts),
        "languages": {},
        "git_commits": int(tool_counts.get("git_commit", 0)),
        "git_pushes": int(tool_counts.get("git_push", 0)),
        "projects": dict(projects),
        "goal_categories": {},
        "outcomes": {},
        "satisfaction": {},
        "helpfulness": {},
        "session_types": {},
        "friction": {},
        "success": {},
        "session_summaries": [
            {
                "id": str(s.get("session_id")),
                "date": str(s.get("start_time", ""))[:10],
                "summary": str(s.get("first_prompt") or "No user prompt captured")[:180],
            }
            for s in sessions[:20]
        ],
        "total_interruptions": 0,
        "total_tool_errors": 0,
        "tool_error_categories": {},
        "user_response_times": [],
        "median_response_time": 0,
        "avg_response_time": 0,
        "sessions_using_task_agent": sum(1 for s in sessions if "Task" in (s.get("tool_counts") or {})),
        "sessions_using_mcp": sum(1 for s in sessions if any(str(k).startswith("mcp__") for k in (s.get("tool_counts") or {}))),
        "sessions_using_web_search": sum(1 for s in sessions if "WebSearch" in (s.get("tool_counts") or {})),
        "sessions_using_web_fetch": sum(1 for s in sessions if "WebFetch" in (s.get("tool_counts") or {})),
        "total_lines_added": 0,
        "total_lines_removed": 0,
        "total_files_modified": 0,
        "days_active": len({v[:10] for v in start_values}),
        "messages_per_day": total_user,
        "message_hours": [],
        "multi_clauding": detectMultiClauding(sessions),
    }


def _make_insights(data: dict[str, Any]) -> dict[str, Any]:
    top_tools = sorted(data.get("tool_counts", {}).items(), key=lambda item: item[1], reverse=True)[:5]
    tool_text = ", ".join(f"{name} ({count})" for name, count in top_tools) or "no tool usage captured"
    return {
        "at_a_glance": {
            "whats_working": f"DeepSeek Code found {data['total_sessions']} local session(s) and {tool_text}.",
            "whats_hindering": "This lightweight migration does not call a remote model for qualitative facets yet.",
            "quick_wins": "Run more substantive local sessions, then regenerate insights for richer summaries.",
            "ambitious_workflows": "Facet extraction can later be wired to DeepSeek chat completions.",
        },
        "top_tools": top_tools,
    }


def _html_report(data: dict[str, Any], insights: dict[str, Any]) -> str:
    glance = insights.get("at_a_glance", {})
    rows = "\n".join(
        f"<li><strong>{html.escape(item['date'])}</strong>: {html.escape(item['summary'])}</li>"
        for item in data.get("session_summaries", [])
    )
    return f"""<!doctype html>
<html lang="zh-CN">
<head><meta charset="utf-8"><title>DeepSeek Code Insights</title></head>
<body>
<h1>DeepSeek Code Insights</h1>
<p>{data['total_sessions']} sessions · {data['total_messages']} messages</p>
<h2>At a Glance</h2>
<p>{html.escape(str(glance.get('whats_working', '')))}</p>
<p>{html.escape(str(glance.get('quick_wins', '')))}</p>
<h2>Recent Sessions</h2>
<ul>{rows}</ul>
</body>
</html>"""


async def generateUsageReport(options: dict[str, Any] | None = None) -> dict[str, Any]:
    sessions = [_scan_session_file(path) for path in _iter_session_files(_projects_dir())]
    sessions = deduplicateSessionBranches(sessions)
    data = _aggregate(sessions)
    insights = _make_insights(data)
    report_dir = _data_dir()
    report_dir.mkdir(parents=True, exist_ok=True)
    html_path = report_dir / "report.html"
    html_path.write_text(_html_report(data, insights), encoding="utf-8")
    return {"insights": insights, "htmlPath": str(html_path), "data": data, "facets": {}, "remoteStats": None}


def buildExportData(
    data: dict[str, Any],
    insights: dict[str, Any],
    facets: dict[str, Any] | Iterable[tuple[str, Any]] | None,
    remoteStats: dict[str, Any] | None = None,
) -> dict[str, Any]:
    facet_values = dict(facets or {}).values() if not isinstance(facets, dict) else facets.values()
    facets_summary = {
        "total": 0,
        "goal_categories": {},
        "outcomes": {},
        "satisfaction": {},
        "friction": {},
    }
    for facet in facet_values:
        if not isinstance(facet, dict):
            continue
        facets_summary["total"] += 1
        for source, target in (
            ("goal_categories", "goal_categories"),
            ("user_satisfaction_counts", "satisfaction"),
            ("friction_counts", "friction"),
        ):
            for key, count in (facet.get(source) or {}).items():
                facets_summary[target][key] = facets_summary[target].get(key, 0) + int(count or 0)
        outcome = facet.get("outcome")
        if outcome:
            facets_summary["outcomes"][outcome] = facets_summary["outcomes"].get(outcome, 0) + 1
    return {
        "metadata": {
            "username": os.environ.get("SAFEUSER") or os.environ.get("USER") or os.environ.get("USERNAME") or "unknown",
            "generated_at": _now_iso(),
            "deepseek_code_version": os.environ.get("DEEPCODE_VERSION", "unknown"),
            "date_range": data.get("date_range", {"start": "unknown", "end": "unknown"}),
            "session_count": data.get("total_sessions", 0),
            "remote_hosts_collected": [
                host.get("name") for host in (remoteStats or {}).get("hosts", []) if host.get("sessionCount", 0) > 0
            ],
        },
        "aggregated_data": data,
        "insights": insights,
        "facets_summary": facets_summary,
    }


async def _get_prompt_for_command(args: str = "", context: dict[str, Any] | None = None) -> list[dict[str, str]]:
    report = await generateUsageReport({"collectRemote": "--homespaces" in (args or "")})
    report_url = f"file://{report['htmlPath']}"
    text = f"""The user just ran /insights for DeepSeek Code.

Report URL: {report_url}
HTML file: {report['htmlPath']}
Sessions analyzed: {report['data']['total_sessions']}
Messages: {report['data']['total_messages']}

Output this message exactly:

<message>
Your shareable DeepSeek Code insights report is ready:
{report_url}

Want to dig into any section or try one of the suggestions?
</message>"""
    return [{"type": "text", "text": text}]


usageReport: dict[str, Any] = {
    "type": "prompt",
    "name": "insights",
    "description": "Generate a report analyzing your DeepSeek Code sessions",
    "contentLength": 0,
    "progressMessage": "analyzing your sessions",
    "source": "builtin",
    "getPromptForCommand": _get_prompt_for_command,
}

default = usageReport

__all__ = [
    "buildExportData",
    "deduplicateSessionBranches",
    "default",
    "detectMultiClauding",
    "generateUsageReport",
    "usageReport",
]
