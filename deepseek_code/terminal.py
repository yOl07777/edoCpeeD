from __future__ import annotations

import argparse
import asyncio
import difflib
import json
import os
import re
import shlex
import subprocess
import sys
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from deepseek_code.config import DeepSeekConfig
from deepseek_code.core.code_processor import ToolRoundLimitExceeded
from deepseek_code.core.types import InternalMessage, InternalStreamDelta, InternalToolCall


DEFAULT_TERMINAL_SYSTEM_PROMPT = (
    "You are DeepSeek Code, a concise coding assistant. "
    "Help with code generation, analysis, refactoring, and debugging. "
    "Use tools when available and return clear, actionable answers. "
    "When the user asks you to create, update, inspect, or refactor files, use the available file tools. "
    "Prefer read_file before editing existing files, write_file for new files, and edit_file for exact replacements. "
    "Keep file paths workspace-relative unless the user gives an absolute path."
)

WELCOME = """DeepSeek Code
Type /help for commands, @file to attach context, !cmd to run PowerShell, /exit to quit.
Tips: /context shows memory size, /undo removes the last turn, /retry reruns it.
"""


HELP_TEXT = """Ask
  Type normally        Send a prompt to DeepSeek Code
  @README.md ...       Attach a file as context
  /paste               Enter multiline prompt, finish with .end
  End with \\          Continue input on the next line

Workspace
  /pwd                 Show current workspace
  /cd <path>           Change current workspace
  /ls [path]           List files
  /tree [path]         Show a shallow directory tree
  /read <path>         Print a text file
  /open <path|last>    Jump to a file in the terminal
  /open file.py:42     Jump to a specific line with context
  /jump [path|last]    Alias for /open, defaults to last changed file
  /write <path> <text> Write text to a file
  /append <path> <text> Append text to a file
  !git status          Run a PowerShell command

Session
  /status              Show model, workspace, context, and tools
  /context             Show context/message summary
  /history [n]         Show recent user prompts and assistant replies
  /again [n]           Rerun recent user prompt n from /history, default 1
  /last                Print the most recent assistant response
  /find <text>         Search current conversation messages
  /save [path]         Save transcript to markdown
  /compact [n]         Keep system prompt and last n messages
  /undo                Remove the most recent user turn
  /retry               Rerun the last user turn
  /clear               Clear conversation context

Settings
  /model [name]        Show or switch model
  /stream [on|off]     Show or toggle streaming output
  /tools               Show tool status and a short tool list
  /branch              Show current git branch
  /diff [path|last]    Show git diff summary, or a file diff
  /changes             Show files changed in this terminal session
  /shell [--timeout N] <cmd>
                       Run a PowerShell command
  !!                   Rerun the previous shell shortcut
  /doctor              Show local diagnostics
  /login               Show API key setup help
  /exit, /quit         Exit
"""

LOGIN_HELP = """No DeepSeek API key is configured yet.

Set one in this PowerShell session:
  $env:DEEPSEEK_API_KEYS="sk-..."

Or start once with:
  python -m deepseek_code.cli --api-key sk-...

You can keep using local slash commands in this terminal before configuring a key.
"""

COMMAND_NAMES = {
    "/append",
    "/again",
    "/?",
    "/cd",
    "/clear",
    "/compact",
    "/context",
    "/cwd",
    "/branch",
    "/changes",
    "/diff",
    "/doctor",
    "/exit",
    "/find",
    "/help",
    "/history",
    "/jump",
    "/last",
    "/login",
    "/ls",
    "/model",
    "/open",
    "/paste",
    "/pwd",
    "/q",
    "/quit",
    "/read",
    "/retry",
    "/save",
    "/shell",
    "/status",
    "/stream",
    "/tools",
    "/tree",
    "/undo",
    "/write",
}


class OfflineProcessor:
    def __init__(self, *, model: str, system_prompt: str, reason: str | None = None) -> None:
        self.model = model
        self.messages = [InternalMessage(role="system", content=system_prompt)]
        self.reason = reason or "No DeepSeek API key configured. Type /login for setup instructions."

    async def stream_text(self, prompt: str, **_: Any):
        self.messages.append(InternalMessage(role="user", content=prompt))
        raise RuntimeError(self.reason)
        yield ""  # pragma: no cover

    async def run(self, prompt: str, **_: Any) -> Any:
        self.messages.append(InternalMessage(role="user", content=prompt))
        raise RuntimeError(self.reason)


@dataclass
class TerminalOptions:
    model: str | None = None
    api_key: str | None = None
    endpoint: str | None = None
    stream: bool = True
    enable_tools: bool = True
    max_tokens: int | None = None
    temperature: float | None = None
    system_prompt: str = DEFAULT_TERMINAL_SYSTEM_PROMPT


class DeepSeekTerminal:
    def __init__(
        self,
        *,
        client: Any,
        processor: Any,
        model: str,
        tools: list[dict[str, Any]] | None = None,
        stream: bool = True,
        max_tokens: int | None = None,
        temperature: float | None = None,
        max_tool_rounds: int = 10,
    ) -> None:
        self.client = client
        self.processor = processor
        self.model = model
        self.tools = tools
        self.stream = stream
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.max_tool_rounds = max_tool_rounds
        self._last_context_hint_at = 0
        self._last_turn_tokens: dict[str, int] | None = None
        self._active_tool_labels: dict[str, str] = {}
        self._stream_tool_block_open = False
        self._last_changed_files: list[str] = []
        self._last_shell_command: str | None = None
        self._last_shell_timeout: int = 30
        self._last_error_summary: str | None = None
        self._last_error_suggestions: list[str] = []

    async def run(self) -> int:
        self._print_welcome()
        try:
            while True:
                try:
                    prompt = await self._read_user_prompt()
                except (EOFError, KeyboardInterrupt):
                    print()
                    return 0
                prompt = prompt.strip()
                if not prompt:
                    continue
                if prompt == "!!":
                    await self._rerun_last_shell_shortcut()
                    continue
                if prompt.startswith("!"):
                    await self._run_shell_shortcut(prompt[1:].strip())
                    continue
                if prompt.startswith("/"):
                    should_continue = await self._handle_command(prompt)
                    if not should_continue:
                        return 0
                    continue
                prompt = self._expand_file_mentions(prompt)
                await self._send_prompt(prompt)
        finally:
            self._set_cursor("block")

    async def _read_user_prompt(self) -> str:
        self._set_cursor("beam")
        line = await asyncio.to_thread(input, self._prompt_label())
        if line.rstrip().endswith("\\"):
            lines = [line.rstrip()[:-1]]
            while True:
                self._set_cursor("beam")
                next_line = await asyncio.to_thread(input, self._continuation_label())
                if next_line.rstrip().endswith("\\"):
                    lines.append(next_line.rstrip()[:-1])
                    continue
                lines.append(next_line)
                return "\n".join(lines)
        return line

    def _prompt_label(self) -> str:
        cwd = Path.cwd()
        cwd_name = cwd.name or self._display_path(cwd)
        tool_mark = "+" if self.tools else "-"
        git = self._git_summary()
        git_mark = f" {git['branch']}{'*' if git['dirty'] else ''}" if git else ""
        # Avoid the awkward "DeepCode DeepCode" prompt when the workspace is
        # the project itself; the directory name already carries the brand.
        prefix = "DeepCode" if cwd_name.lower() == "deepcode" else f"DeepCode {cwd_name}"
        change_mark = f" chg:{len(self._last_changed_files)}" if self._last_changed_files else ""
        label = f"{prefix}{git_mark} {self.model} tools:{tool_mark}{change_mark}> "
        if not self._color_enabled():
            return label
        parts = [
            self._style(prefix, "36;1"),
            self._style(git_mark, "32;1") if git_mark else "",
            " ",
            self._style(self.model, "38;5;111"),
            " ",
            self._style(f"tools:{tool_mark}", "38;5;85" if self.tools else "90"),
            self._style(change_mark, "38;5;221;1") if change_mark else "",
            self._style("> ", "38;5;45;1"),
        ]
        return "".join(parts)

    def _continuation_label(self) -> str:
        label = "    ... "
        if not self._color_enabled():
            return label
        return self._style("    ... ", "38;5;244")

    def _print_welcome(self) -> None:
        git = self._git_summary()
        rows = [
            ("Workspace", self._display_path(Path.cwd())),
            ("Model", self.model),
            ("Tools", f"{'enabled' if self.tools else 'disabled'} ({len(self.tools or [])})"),
            ("Streaming", "on" if self.stream else "off"),
            ("Context", self._format_tokens(self._estimate_context_tokens())),
        ]
        if git:
            rows.insert(1, ("Git", f"{git['branch']} ({'dirty' if git['dirty'] else 'clean'})"))
        self._panel(
            "DeepSeek Code",
            rows,
            subtitle="Local coding terminal powered by DeepSeek/OpenAI-compatible chat completions.",
        )
        print(self._muted("Quick actions: /status  /context  /diff  /changes  /doctor  /help"))
        print(self._muted("Shortcuts:     @file for context   !cmd for PowerShell   /exit to quit"))
        print()

    @staticmethod
    def _color_enabled() -> bool:
        if os.environ.get("NO_COLOR"):
            return False
        return bool(getattr(sys.stdout, "isatty", lambda: False)())

    def _style(self, text: str, code: str) -> str:
        if not self._color_enabled():
            return text
        return f"\x1b[{code}m{text}\x1b[0m"

    def _muted(self, text: str) -> str:
        return self._style(text, "2")

    def _ok(self, text: str) -> str:
        return self._style(text, "32;1")

    def _warn(self, text: str) -> str:
        return self._style(text, "33;1")

    def _danger(self, text: str) -> str:
        return self._style(text, "31;1")

    def _accent(self, text: str) -> str:
        return self._style(text, "36;1")

    def _assistant_accent(self, text: str) -> str:
        return self._style(text, "38;5;183")

    def _assistant_heading(self, text: str) -> str:
        return self._style(text, "38;5;219;1")

    def _rule(self) -> str:
        return self._muted("-" * 72)

    def _section(self, title: str) -> None:
        print(self._accent(f"== {title} =="))
        print(self._rule())

    def _kv(self, key: str, value: Any) -> None:
        label = key + ":"
        if self._color_enabled():
            label = self._muted(label.ljust(12))
        print(f"{label} {value}")

    def _success(self, text: str) -> None:
        print(self._ok(f"[OK] {text}"))

    def _notice(self, text: str) -> None:
        print(self._muted(f"  {text}"))

    def _warning(self, text: str) -> None:
        print(self._warn(f"[warn] {text}"))

    def _error(self, text: str) -> None:
        print(self._danger(f"[error] {text}"), file=sys.stderr)

    def _set_cursor(self, shape: str) -> None:
        if not self._color_enabled():
            return
        shapes = {
            "beam": "\x1b[5 q",
            "block": "\x1b[2 q",
            "underline": "\x1b[3 q",
        }
        sequence = shapes.get(shape)
        if sequence:
            print(sequence, end="", flush=True)

    def _assistant_chunk(self, text: str) -> str:
        return self._assistant_accent(text)

    def _assistant_block(self, text: str) -> str:
        if not self._color_enabled() or not text:
            return text
        lines: list[str] = []
        in_code = False
        for line in text.splitlines(keepends=True):
            stripped = line.lstrip()
            if stripped.startswith("```"):
                in_code = not in_code
                lines.append(self._style(line, "90"))
            elif in_code:
                lines.append(self._style(line, "92"))
            elif stripped.startswith(("#", "-", "*", "1.", "2.", "3.")):
                lines.append(self._assistant_line(line, "38;5;219;1"))
            else:
                lines.append(self._assistant_line(line, "38;5;183"))
        return "".join(lines)

    def _assistant_line(self, text: str, base_code: str) -> str:
        if not self._color_enabled() or not text:
            return text
        pattern = re.compile(r"(`[^`\n]+`|\*\*[^*\n]+\*\*)")
        parts: list[str] = []
        last = 0
        for match in pattern.finditer(text):
            if match.start() > last:
                parts.append(self._style(text[last : match.start()], base_code))
            token = match.group(0)
            if token.startswith("`"):
                parts.append(self._style(token[1:-1], "38;5;229;1"))
            else:
                parts.append(self._style(token[2:-2], "38;5;225;1"))
            last = match.end()
        if last < len(text):
            parts.append(self._style(text[last:], base_code))
        return "".join(parts)

    def _render_inline_markup(self, text: str) -> str:
        if not self._color_enabled() or not text:
            return text

        def code_repl(match: re.Match[str]) -> str:
            return self._style(match.group(1), "38;5;229;1")

        def bold_repl(match: re.Match[str]) -> str:
            return self._style(match.group(1), "38;5;225;1")

        rendered = re.sub(r"`([^`\n]+)`", code_repl, text)
        rendered = re.sub(r"\*\*([^*\n]+)\*\*", bold_repl, rendered)
        return rendered

    def _panel(
        self,
        title: str,
        rows: list[tuple[str, Any]],
        *,
        subtitle: str | None = None,
        width: int = 78,
    ) -> None:
        width = max(48, min(width, 100))
        border = "+" + "-" * (width - 2) + "+"
        print(self._accent(border))
        print(self._accent("| " + title[: width - 4].ljust(width - 4) + " |"))
        if subtitle:
            subtitle_text = self._truncate_display(subtitle, limit=width - 4)
            print(self._muted("| " + subtitle_text.ljust(width - 4) + " |"))
        print(self._accent("|" + "-" * (width - 2) + "|"))
        key_width = min(14, max((len(key) for key, _ in rows), default=8))
        for key, value in rows:
            text = f"{key + ':':<{key_width + 1}} {value}"
            print("| " + self._truncate_display(text, limit=width - 4).ljust(width - 4) + " |")
        print(self._accent(border))

    def _display_path(self, path: Path) -> str:
        try:
            home = Path.home()
            resolved = path.resolve()
            try:
                relative = resolved.relative_to(home)
                text = "~" if not relative.parts else "~" + os.sep + str(relative)
            except ValueError:
                text = str(resolved)
        except OSError:
            text = str(path)
        if len(text) <= 72:
            return text
        return "..." + text[-69:]

    def _tty_notice(self, text: str) -> None:
        if self._color_enabled():
            self._set_cursor("block")
            print(self._muted(text))

    def _elapsed_note(self, started_at: float) -> None:
        if self._color_enabled():
            elapsed = time.perf_counter() - started_at
            print(self._muted(f"done in {elapsed:.1f}s"))

    def _estimate_tokens(self, value: Any) -> int:
        if value is None:
            return 0
        text = value if isinstance(value, str) else json.dumps(value, ensure_ascii=False, default=str)
        if not text:
            return 0
        cjk = sum(1 for char in text if "\u4e00" <= char <= "\u9fff")
        non_cjk = len(text) - cjk
        return max(1, int(cjk * 0.9 + non_cjk / 4 + 0.999))

    def _estimate_message_tokens(self, message: Any) -> int:
        content = getattr(message, "content", "")
        overhead = 4
        if isinstance(content, list):
            total = overhead
            for item in content:
                if isinstance(item, dict) and item.get("type") in {"image", "image_url"}:
                    total += 85
                else:
                    total += self._estimate_tokens(item)
            return total
        return overhead + self._estimate_tokens(content)

    def _estimate_context_tokens(self, messages: list[Any] | None = None) -> int:
        values = messages if messages is not None else list(getattr(self.processor, "messages", []) or [])
        if not values:
            return 0
        return sum(self._estimate_message_tokens(message) for message in values) + 3

    @staticmethod
    def _format_tokens(tokens: int | float) -> str:
        value = int(tokens)
        if value >= 1_000_000:
            return f"~{value / 1_000_000:.2f}M tokens"
        if value >= 10_000:
            return f"~{value / 1000:.1f}k tokens"
        if value >= 1000:
            return f"~{value / 1000:.2f}k tokens"
        return f"~{value} tokens"

    def _usage_tokens(self, response: Any) -> dict[str, int] | None:
        usage = getattr(response, "usage", None)
        if not isinstance(usage, dict):
            return None
        input_tokens = int(usage.get("prompt_tokens") or usage.get("input_tokens") or 0)
        output_tokens = int(usage.get("completion_tokens") or usage.get("output_tokens") or 0)
        total_tokens = int(usage.get("total_tokens") or input_tokens + output_tokens)
        if not any((input_tokens, output_tokens, total_tokens)):
            return None
        return {"input": input_tokens, "output": output_tokens, "total": total_tokens}

    def _turn_token_note(self, *, started_at: float, input_tokens: int, output_text: str, response: Any | None = None) -> None:
        output_tokens = self._estimate_tokens(output_text)
        usage = self._usage_tokens(response)
        if usage:
            turn_tokens = usage
        else:
            turn_tokens = {"input": input_tokens, "output": output_tokens, "total": input_tokens + output_tokens}
        self._last_turn_tokens = turn_tokens
        if self._color_enabled():
            elapsed = time.perf_counter() - started_at
            print(
                self._muted(
                    "tokens "
                    f"in {self._format_tokens(turn_tokens['input'])}, "
                    f"out {self._format_tokens(turn_tokens['output'])}, "
                    f"turn {self._format_tokens(turn_tokens['total'])} "
                    f"/ context {self._format_tokens(self._estimate_context_tokens())} "
                    f"/ {elapsed:.1f}s"
                )
            )

    @staticmethod
    def _truncate_display(text: Any, *, limit: int = 88) -> str:
        value = str(text).replace("\r", " ").replace("\n", " ").strip()
        value = re.sub(r"\s+", " ", value)
        if len(value) <= limit:
            return value
        return value[: max(0, limit - 3)].rstrip() + "..."

    @staticmethod
    def _normalize_shell_command(command: str) -> tuple[str, str]:
        value = command.strip()
        lowered = value.lower()
        for prefix in ("powershell -command ", "powershell.exe -command ", "pwsh -command ", "pwsh.exe -command "):
            if lowered.startswith(prefix):
                body = value[len(prefix) :].strip()
                if len(body) >= 2 and body[0] == body[-1] and body[0] in {"'", '"'}:
                    body = body[1:-1]
                return "PowerShell", body
        return "Shell", value

    def _tool_call_label(self, call: InternalToolCall) -> str:
        args = call.arguments
        if not isinstance(args, dict):
            return call.name

        command = args.get("command")
        if command:
            shell_name, shell_command = self._normalize_shell_command(str(command))
            return f"{shell_name}({self._truncate_display(shell_command, limit=72)})"

        path = args.get("path")
        if path:
            action = {
                "read_file": "Read",
                "write_file": "Write",
                "edit_file": "Edit",
                "notebook_edit": "Edit notebook",
            }.get(call.name, call.name)
            return f"{action}({self._truncate_display(path, limit=72)})"

        pattern = args.get("pattern")
        if pattern:
            return f"Search({self._truncate_display(pattern, limit=72)})"

        query = args.get("query")
        if query:
            return f"Search web({self._truncate_display(query, limit=72)})"

        url = args.get("url")
        if url:
            return f"Fetch({self._truncate_display(url, limit=72)})"

        return call.name

    def _print_stream_event(self, delta: InternalStreamDelta, *, output_started: bool) -> None:
        if not delta.tool_calls:
            return
        if output_started and not self._stream_tool_block_open:
            print()
        self._stream_tool_block_open = True
        labels = [self._tool_call_label(call) for call in delta.tool_calls]
        if delta.finish_reason == "tool_call_started":
            for call, label in zip(delta.tool_calls, labels):
                self._active_tool_labels[call.id] = label
                print(self._muted(f"  [tool] -> {label}"))
        elif delta.finish_reason == "tool_call_finished":
            for call, label in zip(delta.tool_calls, labels):
                label = self._active_tool_labels.pop(call.id, label)
                print(self._ok(f"  [tool] <- {label} done"))
        else:
            for label in labels:
                print(self._muted(f"  [tool] -- {label}"))

    async def _send_prompt(self, prompt: str) -> None:
        started_at = time.perf_counter()
        input_tokens = self._estimate_context_tokens() + self._estimate_tokens(prompt)
        try:
            if self.tools:
                before_count = len(getattr(self.processor, "messages", []))
                response: Any | None = None
                output_text = ""
                if self.stream:
                    try:
                        self._tty_notice("DeepSeek is thinking...")
                        output_parts: list[str] = []
                        self._stream_tool_block_open = False
                        async for delta in self.processor.stream_text(
                            prompt,
                            tools=self.tools,
                            max_tool_rounds=self.max_tool_rounds,
                            max_tokens=self.max_tokens,
                            temperature=self.temperature,
                            tool_events=True,
                        ):
                            if isinstance(delta, str):
                                if self._stream_tool_block_open:
                                    print()
                                    self._stream_tool_block_open = False
                                output_parts.append(delta)
                                self._set_cursor("underline")
                                print(self._assistant_chunk(delta), end="", flush=True)
                            elif isinstance(delta, InternalStreamDelta):
                                self._print_stream_event(delta, output_started=bool(output_parts))
                        print()
                        output_text = "".join(output_parts)
                    except ToolRoundLimitExceeded as stream_exc:
                        self._error(self._format_tool_round_limit(stream_exc))
                    except Exception as stream_exc:
                        self._error(
                            f"[stream] failed, retrying once without streaming: {self._format_error(stream_exc)}\n"
                            "Next: if this keeps happening, use /stream off"
                        )
                        response = await self.processor.run(
                            prompt,
                            tools=self.tools,
                            max_tool_rounds=self.max_tool_rounds,
                            max_tokens=self.max_tokens,
                            temperature=self.temperature,
                        )
                        output_text = response.message.content or ""
                        print(self._assistant_block(output_text))
                        self._notice("Stream fallback succeeded. Use /stream off if streaming keeps failing.")
                else:
                    response = await self.processor.run(
                        prompt,
                        tools=self.tools,
                        max_tool_rounds=self.max_tool_rounds,
                        max_tokens=self.max_tokens,
                        temperature=self.temperature,
                    )
                    output_text = response.message.content or ""
                    print(self._assistant_block(output_text))
                self._print_tool_activity(before_count)
                self._maybe_print_context_hint()
                self._turn_token_note(started_at=started_at, input_tokens=input_tokens, output_text=output_text, response=response)
            elif self.stream:
                response = None
                output_text = ""
                try:
                    self._tty_notice("DeepSeek is thinking...")
                    output_parts: list[str] = []
                    self._stream_tool_block_open = False
                    async for delta in self.processor.stream_text(
                        prompt,
                        tools=self.tools,
                        max_tool_rounds=self.max_tool_rounds,
                        max_tokens=self.max_tokens,
                        temperature=self.temperature,
                        tool_events=True,
                    ):
                        if isinstance(delta, str):
                            if self._stream_tool_block_open:
                                print()
                                self._stream_tool_block_open = False
                            output_parts.append(delta)
                            self._set_cursor("underline")
                            print(self._assistant_chunk(delta), end="", flush=True)
                        elif isinstance(delta, InternalStreamDelta):
                            self._print_stream_event(delta, output_started=bool(output_parts))
                    print()
                    output_text = "".join(output_parts)
                except ToolRoundLimitExceeded as stream_exc:
                    self._error(self._format_tool_round_limit(stream_exc))
                except Exception as stream_exc:
                    self._error(
                        f"[stream] failed, retrying once without streaming: {self._format_error(stream_exc)}\n"
                        "Next: if this keeps happening, use /stream off"
                    )
                    response = await self.processor.run(
                        prompt,
                        tools=self.tools,
                        max_tool_rounds=self.max_tool_rounds,
                        max_tokens=self.max_tokens,
                        temperature=self.temperature,
                    )
                    output_text = response.message.content or ""
                    print(self._assistant_block(output_text))
                    self._notice("Stream fallback succeeded. Use /stream off if streaming keeps failing.")
                self._maybe_print_context_hint()
                self._turn_token_note(started_at=started_at, input_tokens=input_tokens, output_text=output_text, response=response)
            else:
                self._tty_notice("DeepSeek is thinking...")
                response = await self.processor.run(
                    prompt,
                    tools=self.tools,
                    max_tool_rounds=self.max_tool_rounds,
                    max_tokens=self.max_tokens,
                    temperature=self.temperature,
                )
                output_text = response.message.content or ""
                print(self._assistant_block(output_text))
                self._maybe_print_context_hint()
                self._turn_token_note(started_at=started_at, input_tokens=input_tokens, output_text=output_text, response=response)
        except Exception as exc:
            self._error(self._format_error(exc))

    def _format_error(self, exc: Exception) -> str:
        detail = str(exc).strip()
        text = detail or exc.__class__.__name__
        suggestions = self._error_suggestions(text)
        self._last_error_summary = self._truncate_display(text, limit=140)
        self._last_error_suggestions = suggestions
        if not suggestions:
            return text
        return f"{text}\nNext: " + " | ".join(suggestions)

    def _error_suggestions(self, text: str) -> list[str]:
        lowered = text.lower()
        status = self._http_status_from_error(text)
        if status in {401, 403} or "unauthorized" in lowered or "forbidden" in lowered or "invalid api key" in lowered:
            return ["/login", "check DEEPSEEK_API_KEYS", "/doctor"]
        if status == 429 or "rate limit" in lowered or "too many requests" in lowered:
            return ["wait a minute and /retry", "try a smaller prompt", "/doctor"]
        if status is not None and 500 <= status <= 599:
            return ["/retry", "check DEEPSEEK_ENDPOINTS", "try https://api.deepseek.com", "/doctor"]
        if any(marker in lowered for marker in ("connecterror", "connecttimeout", "readtimeout", "networkerror", "temporary failure", "enotfound", "name resolution", "dns")):
            return ["check DEEPSEEK_ENDPOINTS", "try https://api.deepseek.com", "/stream off", "/doctor"]
        if any(marker in lowered for marker in ("certificate", "ssl", "tls", "proxy")):
            return ["check proxy/certificate settings", "try https://api.deepseek.com", "/doctor"]
        if "no deepseek api key" in lowered or "api key" in lowered and "missing" in lowered:
            return ["/login", 'set $env:DEEPSEEK_API_KEYS="sk-..."', "/doctor"]
        return []

    @staticmethod
    def _http_status_from_error(text: str) -> int | None:
        match = re.search(r"\bHTTP\s+([1-5]\d\d)\b|\bstatus(?:_code)?[=: ]+([1-5]\d\d)\b", text, re.IGNORECASE)
        if not match:
            return None
        return int(next(group for group in match.groups() if group))

    def _format_tool_round_limit(self, exc: Exception) -> str:
        text = self._format_error(exc)
        suggestions = [
            "ask a narrower request",
            "/last",
            "ask: continue from the last visible tool result",
        ]
        self._last_error_summary = self._truncate_display(str(exc) or exc.__class__.__name__, limit=140)
        self._last_error_suggestions = suggestions
        return f"{text}\nNext: " + " | ".join(suggestions)

    def _print_tool_activity(self, start_index: int) -> None:
        messages = getattr(self.processor, "messages", [])[start_index:]
        changed: list[str] = []
        for message in messages:
            if getattr(message, "role", None) != "tool":
                continue
            content = getattr(message, "content", "")
            payload = self._tool_result_payload(content)
            if payload:
                path = self._changed_file_from_payload(payload)
                if path:
                    display = self._remember_changed_file(path)
                    if display not in changed:
                        changed.append(display)
            summary = self._summarize_tool_payload(payload) if payload else self._summarize_tool_result(content)
            if summary:
                print(self._muted(summary))
        if changed:
            self._print_changed_file_followup(changed)

    def _tool_result_payload(self, content: Any) -> dict[str, Any] | None:
        if not isinstance(content, str):
            return None
        try:
            payload = json.loads(content)
        except json.JSONDecodeError:
            return None
        if not isinstance(payload, dict):
            return None
        return payload

    def _summarize_tool_result(self, content: Any) -> str:
        payload = self._tool_result_payload(content)
        return self._summarize_tool_payload(payload) if payload else ""

    def _summarize_tool_payload(self, payload: dict[str, Any]) -> str:
        if not isinstance(payload, dict):
            return ""
        if "error" in payload:
            return f"  ! tool error: {self._truncate_display(payload['error'], limit=96)}"
        path = payload.get("path")
        if payload.get("written") and path:
            return f"     Wrote {self._truncate_display(path, limit=72)} ({payload.get('bytes', 0)} bytes)"
        if "replacements" in payload and path:
            return f"     Edited {self._truncate_display(path, limit=72)} ({payload['replacements']} replacement(s))"
        if "content" in payload and path:
            line_count = payload.get("line_count", "?")
            return f"     Read {self._truncate_display(path, limit=72)} ({line_count} line(s))"
        if "exit_code" in payload:
            exit_code = payload.get("exit_code")
            stdout = payload.get("stdout") or ""
            stderr = payload.get("stderr") or ""
            parts = [f"exit {exit_code}"]
            if stdout:
                parts.append(f"stdout {len(str(stdout).splitlines())} line(s)")
            if stderr:
                parts.append(f"stderr {len(str(stderr).splitlines())} line(s)")
            return "     Shell " + ", ".join(parts)
        if "matches" in payload:
            return f"     Found {len(payload.get('matches') or [])} match(es)"
        if "files" in payload:
            return f"     Found {len(payload.get('files') or [])} file(s)"
        return ""

    def _changed_file_from_payload(self, payload: dict[str, Any]) -> str | None:
        path = payload.get("path")
        if not path:
            return None
        if payload.get("written") or "replacements" in payload:
            return str(path)
        return None

    def _remember_changed_file(self, path: str | Path) -> str:
        target = self._resolve_workspace_path(str(path))
        display = self._workspace_relative_path(target)
        self._last_changed_files = [item for item in self._last_changed_files if item != display]
        self._last_changed_files.append(display)
        return display

    def _last_changed_file(self) -> str | None:
        return self._last_changed_files[-1] if self._last_changed_files else None

    def _print_changed_file_followup(self, changed: list[str]) -> None:
        if len(changed) == 1:
            path = changed[0]
            print(self._muted(f"     Next: /open {path}  |  /diff {path}  |  /changes"))
        else:
            print(self._muted(f"     Changed {len(changed)} files. Next: /open last  |  /diff last  |  /changes"))

    def _tool_names(self, limit: int = 12) -> list[str]:
        names: list[str] = []
        for tool in self.tools or []:
            if not isinstance(tool, dict):
                continue
            fn = tool.get("function") if isinstance(tool.get("function"), dict) else {}
            name = fn.get("name") or tool.get("name")
            if name:
                names.append(str(name))
        return names[:limit]

    def _expand_file_mentions(self, prompt: str) -> str:
        pattern = re.compile(r"(?<!\S)@([^\s]+)")
        attachments: list[str] = []

        def replace(match: re.Match[str]) -> str:
            raw_path = match.group(1).strip('"').strip("'")
            target = self._resolve_workspace_path(raw_path)
            if not target.is_file():
                return match.group(0)
            try:
                text = target.read_text(encoding="utf-8", errors="replace")
            except OSError:
                return match.group(0)
            if len(text) > 20_000:
                text = text[:20_000] + "\n... [truncated]"
            attachments.append(f"\n\n--- Attached file: {raw_path} ---\n{text}\n--- End file: {raw_path} ---")
            return raw_path

        expanded = pattern.sub(replace, prompt)
        if attachments:
            return expanded + "".join(attachments)
        return expanded

    async def _handle_command(self, raw: str) -> bool:
        command, _, arg = raw.partition(" ")
        command = command.lower()
        arg = arg.strip()
        if command in {"/exit", "/quit", "/q"}:
            return False
        if command in {"/help", "/?"}:
            self._section("Help")
            print(HELP_TEXT.strip())
            return True
        if command == "/login":
            self._section("Login")
            print(LOGIN_HELP.strip())
            return True
        if command == "/paste":
            prompt = self._read_multiline_input(append=False, purpose="prompt")
            if prompt.strip():
                await self._send_prompt(self._expand_file_mentions(prompt.strip()))
            return True
        if command == "/clear":
            system = self.processor.messages[0] if self.processor.messages else InternalMessage(role="system", content=DEFAULT_TERMINAL_SYSTEM_PROMPT)
            self.processor.messages = [system]
            self._success("Context cleared.")
            return True
        if command == "/compact":
            self._compact_context(arg)
            return True
        if command == "/model":
            if arg:
                self.model = arg
                self.processor.model = arg
                self._success(f"Model set to {arg}.")
            else:
                self._kv("Current model", self.model)
            return True
        if command == "/stream":
            if arg:
                value = arg.lower()
                if value not in {"on", "off", "true", "false", "1", "0"}:
                    self._warning("Usage: /stream [on|off]")
                    return True
                self.stream = value in {"on", "true", "1"}
            self._success(f"Streaming: {'on' if self.stream else 'off'}")
            return True
        if command == "/status":
            self._status()
            return True
        if command == "/branch":
            self._branch_status()
            return True
        if command == "/diff":
            self._diff_status(arg)
            return True
        if command == "/changes":
            self._changes_status()
            return True
        if command == "/tools":
            self._tools_status()
            return True
        if command == "/history":
            self._history_status(arg)
            return True
        if command == "/again":
            await self._again_from_history(arg)
            return True
        if command == "/context":
            self._context_status()
            return True
        if command == "/last":
            self._print_last_assistant()
            return True
        if command == "/find":
            self._find_in_context(arg)
            return True
        if command == "/save":
            self._save_transcript(arg)
            return True
        if command == "/undo":
            self._undo_last_turn()
            return True
        if command == "/retry":
            await self._retry_last_turn()
            return True
        if command in {"/pwd", "/cwd"}:
            self._kv("Workspace", Path.cwd())
            return True
        if command == "/cd":
            self._change_directory(arg)
            return True
        if command == "/ls":
            self._list_files(arg or ".")
            return True
        if command == "/tree":
            self._tree(arg or ".")
            return True
        if command in {"/read", "/open", "/jump"}:
            self._read_file(arg or ("last" if command == "/jump" else ""))
            return True
        if command == "/write":
            self._write_file(arg, append=False)
            return True
        if command == "/append":
            self._write_file(arg, append=True)
            return True
        if command == "/shell":
            await self._run_shell_shortcut(arg)
            return True
        if command == "/doctor":
            self._doctor()
            return True
        suggestions = difflib.get_close_matches(command, sorted(COMMAND_NAMES), n=3, cutoff=0.45)
        if suggestions:
            self._warning(f"Unknown command: {command}. Did you mean {' or '.join(suggestions)}?")
        else:
            self._warning(f"Unknown command: {command}. Type /help.")
        return True

    def _compact_context(self, arg: str) -> None:
        try:
            keep = int(arg) if arg else 12
        except ValueError:
            keep = 12
        keep = max(2, keep)
        messages = getattr(self.processor, "messages", [])
        if len(messages) <= keep + 1:
            self._notice(f"Context already compact ({len(messages)} messages).")
            return
        system = messages[0]
        removed = len(messages) - keep - 1
        summary = InternalMessage(
            role="system",
            content=f"Earlier conversation was compacted locally. {removed} messages were removed from active context.",
        )
        self.processor.messages = [system, summary] + messages[-keep:]
        self._success(f"Compacted context: kept {keep} recent messages, removed {removed}.")

    def _status(self) -> None:
        messages = getattr(self.processor, "messages", [])
        context_tokens = self._estimate_context_tokens(messages)
        rows: list[tuple[str, Any]] = [("Workspace", self._display_path(Path.cwd()))]
        git = self._git_summary()
        if git:
            dirty = "dirty" if git["dirty"] else "clean"
            rows.append(("Git", f"{git['branch']} ({dirty})"))
        rows.extend(
            [
                ("Model", self.model),
                ("Streaming", "on" if self.stream else "off"),
                ("Tools", f"{'enabled' if self.tools else 'disabled'} ({len(self.tools or [])})"),
                ("Messages", len(messages)),
                ("Context", self._format_tokens(context_tokens)),
            ]
        )
        if self._last_turn_tokens:
            rows.append(
                (
                    "Last turn",
                    f"in {self._format_tokens(self._last_turn_tokens['input'])}, "
                    f"out {self._format_tokens(self._last_turn_tokens['output'])}, "
                    f"total {self._format_tokens(self._last_turn_tokens['total'])}",
                )
            )
        self._panel("Status", rows)

    def _branch_status(self) -> None:
        git = self._git_summary()
        if not git:
            self._warning("Git: not a repository")
            return
        dirty = "dirty" if git["dirty"] else "clean"
        self._section("Branch")
        self._kv("Branch", f"{git['branch']} ({dirty})")

    def _diff_status(self, arg: str) -> None:
        try:
            parts = shlex.split(arg, posix=False) if arg else []
        except ValueError:
            parts = arg.split()
        full = "--full" in parts
        stat = "--stat" in parts
        paths = [part.strip('"').strip("'") for part in parts if not part.startswith("--")]
        path_arg = paths[0] if paths else ""
        if path_arg.lower() == "last":
            path_arg = self._last_changed_file() or ""
        if path_arg:
            self._file_diff_status(path_arg, stat_only=stat and not full)
            return
        if not self._git_summary():
            self._warning("Git: not a repository")
            return
        command = ["git", "diff"] if full else ["git", "diff", "--stat"]
        result = self._run_git(command, timeout=10)
        if result is None:
            self._warning("Could not read git diff.")
            return
        output = result.strip()
        self._section("Diff")
        print(output or "No unstaged diff.")

    def _file_diff_status(self, path_arg: str, *, stat_only: bool = False) -> None:
        target = self._resolve_workspace_path(path_arg)
        if not target.exists():
            self._warning(f"File not found: {target}")
            return
        relative = self._workspace_relative_path(target)
        self._section(f"Diff: {relative}")
        if stat_only:
            stat = self._run_git(["git", "diff", "--stat", "--", relative], timeout=10) if self._git_summary() else None
            print((stat or "").strip() or f"{relative} | {target.stat().st_size} bytes")
            return
        output = self._run_git(["git", "diff", "--", relative], timeout=10) if self._git_summary() else None
        if output and output.strip():
            print(output.strip())
            return
        if self._is_git_tracked(relative):
            print("No unstaged diff for this file.")
            return
        print(self._added_file_diff(relative, target))

    def _is_git_tracked(self, relative: str) -> bool:
        result = self._run_git(["git", "ls-files", "--error-unmatch", "--", relative], timeout=5)
        return result is not None

    def _added_file_diff(self, relative: str, target: Path) -> str:
        try:
            text = target.read_text(encoding="utf-8", errors="replace")
        except OSError as exc:
            return f"Could not read file for diff: {exc}"
        lines = text.splitlines()
        diff = difflib.unified_diff(
            [],
            lines,
            fromfile="/dev/null",
            tofile=relative,
            lineterm="",
        )
        rendered = "\n".join(diff)
        return rendered[:20_000] + ("\n... [diff truncated]" if len(rendered) > 20_000 else "")

    def _changes_status(self) -> None:
        if not self._last_changed_files:
            self._panel("Changed files", [("Files", "none in this terminal session yet")])
            return
        rows: list[tuple[str, Any]] = []
        for index, path in enumerate(reversed(self._last_changed_files[-20:]), start=1):
            suffix = " (last)" if index == 1 else ""
            rows.append((f"{index:>2}", f"{path}{suffix}"))
        self._panel("Changed files", rows, subtitle="Recently changed in this terminal session.")
        print(self._muted("Next: /open last  |  /diff last  |  /open <path>"))

    def _tools_status(self) -> None:
        count = len(self.tools or [])
        names = self._tool_names()
        rows = [
            ("Status", f"{'enabled' if count else 'disabled'} ({count})"),
            ("Shown", ", ".join(names) + (" ..." if count > len(names) else "") if names else "none"),
        ]
        self._panel("Tools", rows, subtitle="Workspace tools exposed to DeepSeek as function calls.")
        if names:
            print("Available: " + ", ".join(names) + (" ..." if count > len(names) else ""))
            self._notice("Ask naturally to read, write, edit, search, or run shell commands.")
        else:
            self._notice("Restart without --no-tools to enable workspace file tools.")

    def _user_prompt_history(self) -> list[tuple[int, str]]:
        history: list[tuple[int, str]] = []
        for index, message in enumerate(getattr(self.processor, "messages", [])):
            if getattr(message, "role", None) != "user":
                continue
            content = getattr(message, "content", "")
            if isinstance(content, str) and content.strip():
                history.append((index, content))
        return history

    def _history_status(self, arg: str) -> None:
        try:
            limit = int(arg) if arg else 10
        except ValueError:
            limit = 10
        limit = max(1, min(50, limit))
        messages = getattr(self.processor, "messages", [])
        history = list(reversed(self._user_prompt_history()))[:limit]
        rows: list[tuple[str, Any]] = [
            ("Messages", len(messages)),
            ("User prompts", len(self._user_prompt_history())),
        ]
        self._panel("History", rows, subtitle=f"Recent prompts. Rerun with /again <n>; newest is 1.")
        if not history:
            self._notice("No user prompts yet.")
            return
        for number, (_, prompt) in enumerate(history, start=1):
            print(f"{number:>2}. {self._truncate_display(prompt, limit=110)}")

    async def _again_from_history(self, arg: str) -> None:
        history = list(reversed(self._user_prompt_history()))
        if not history:
            self._notice("No user prompt to rerun.")
            return
        try:
            number = int(arg) if arg else 1
        except ValueError:
            self._warning("Usage: /again [history-number]")
            return
        if number < 1 or number > len(history):
            self._warning(f"History item not found: {number}. Use /history to see recent prompts.")
            return
        prompt = history[number - 1][1]
        self._notice(f"Rerunning history item {number}: {self._truncate_display(prompt, limit=88)}")
        await self._send_prompt(prompt)

    def _context_status(self) -> None:
        messages = getattr(self.processor, "messages", [])
        by_role: dict[str, int] = {}
        chars = 0
        for message in messages:
            role = getattr(message, "role", "unknown")
            by_role[role] = by_role.get(role, 0) + 1
            content = getattr(message, "content", "")
            if isinstance(content, str):
                chars += len(content)
            elif content is not None:
                chars += len(str(content))
        role_text = ", ".join(f"{role}:{count}" for role, count in sorted(by_role.items()))
        rough_tokens = self._estimate_context_tokens(messages)
        rows: list[tuple[str, Any]] = [
            ("Messages", f"{len(messages)} ({role_text or 'empty'})"),
            ("Approx context", f"{chars} chars / ~{rough_tokens} tokens"),
            ("Token estimate", self._format_tokens(rough_tokens)),
        ]
        if messages:
            last_role = getattr(messages[-1], "role", "unknown")
            rows.append(("Last turn", last_role))
        if self._last_turn_tokens:
            rows.append(("Last usage", f"~{self._last_turn_tokens['total']} tokens"))
        self._panel("Context", rows)
        if len(messages) > 40:
            self._notice("Tip: use /compact 16 if responses start getting slower or less focused.")

    def _print_last_assistant(self) -> None:
        for message in reversed(getattr(self.processor, "messages", [])):
            if getattr(message, "role", None) == "assistant":
                content = getattr(message, "content", "")
                self._section("Last assistant")
                print(content if content else "(last assistant message has no text)")
                return
        self._notice("No assistant response yet.")

    def _find_in_context(self, query: str) -> None:
        needle = query.strip().lower()
        if not needle:
            self._warning("Usage: /find <text>")
            return
        matches: list[str] = []
        for index, message in enumerate(getattr(self.processor, "messages", [])):
            content = getattr(message, "content", "")
            text = content if isinstance(content, str) else str(content)
            pos = text.lower().find(needle)
            if pos < 0:
                continue
            snippet = text[max(0, pos - 40) : pos + len(needle) + 80].replace("\n", " ")
            matches.append(f"{index}: {getattr(message, 'role', 'unknown')} - {snippet}")
        if not matches:
            self._notice(f"No matches for: {query}")
            return
        self._section("Search results")
        for line in matches[:20]:
            print(line)
        if len(matches) > 20:
            self._notice(f"... {len(matches) - 20} more")

    def _save_transcript(self, arg: str) -> None:
        raw_path = arg.strip().strip('"').strip("'")
        if raw_path:
            target = self._resolve_workspace_path(raw_path)
        else:
            target = Path.cwd() / ".deepseek" / "transcripts" / "last-session.md"
        target.parent.mkdir(parents=True, exist_ok=True)
        try:
            target.write_text(self._render_transcript(), encoding="utf-8")
        except OSError as exc:
            self._error(f"Could not save transcript: {exc}")
            return
        self._success(f"Saved transcript: {target}")

    def _render_transcript(self) -> str:
        lines = [f"# DeepSeek Code Transcript", "", f"Workspace: {Path.cwd()}", f"Model: {self.model}", ""]
        for message in getattr(self.processor, "messages", []):
            role = getattr(message, "role", "unknown")
            content = getattr(message, "content", "")
            if content is None:
                content = ""
            if not isinstance(content, str):
                content = json.dumps(content, ensure_ascii=False, indent=2)
            lines.extend([f"## {role}", "", content, ""])
        return "\n".join(lines).rstrip() + "\n"

    def _undo_last_turn(self) -> None:
        removed = self._remove_last_response(include_user=True)
        if removed:
            self._success(f"Removed {removed} message(s) from the last turn.")
        else:
            self._notice("Nothing to undo.")

    async def _retry_last_turn(self) -> None:
        messages = getattr(self.processor, "messages", [])
        last_user = None
        for message in reversed(messages):
            if getattr(message, "role", None) == "user":
                last_user = message
                break
        if last_user is None or not isinstance(last_user.content, str):
            self._notice("No user turn to retry.")
            return
        prompt = last_user.content
        removed = self._remove_last_response(include_user=True)
        if removed:
            self._notice(f"Retrying last turn ({removed} message(s) removed).")
        await self._send_prompt(prompt)

    def _remove_last_response(self, *, include_user: bool) -> int:
        messages = getattr(self.processor, "messages", [])
        if len(messages) <= 1:
            return 0
        index = len(messages) - 1
        while index > 0 and getattr(messages[index], "role", None) != "user":
            index -= 1
        if index <= 0:
            return 0
        remove_from = index if include_user else index + 1
        removed = len(messages) - remove_from
        if removed <= 0:
            return 0
        del messages[remove_from:]
        return removed

    def _maybe_print_context_hint(self) -> None:
        count = len(getattr(self.processor, "messages", []))
        if count >= 40 and count - self._last_context_hint_at >= 20:
            self._last_context_hint_at = count
            self._notice(f"[context] {count} messages in memory. Use /context or /compact 16 if the session feels heavy.")

    def _split_path_and_text(self, arg: str) -> tuple[str, str]:
        try:
            parts = shlex.split(arg, posix=False)
        except ValueError:
            parts = arg.split(maxsplit=1)
        if not parts:
            return "", ""
        path = parts[0].strip('"').strip("'")
        if len(parts) == 1:
            return path, ""
        marker = arg.find(parts[1])
        text = arg[marker:] if marker >= 0 else " ".join(parts[1:])
        return path, text

    def _resolve_workspace_path(self, raw: str) -> Path:
        path = Path(raw).expanduser()
        if not path.is_absolute():
            path = Path.cwd() / path
        return path.resolve()

    def _workspace_relative_path(self, path: Path) -> str:
        try:
            return str(path.resolve().relative_to(Path.cwd().resolve())).replace("\\", "/")
        except ValueError:
            return str(path)

    def _change_directory(self, arg: str) -> None:
        if not arg:
            self._warning("Usage: /cd <path>")
            return
        target = self._resolve_workspace_path(arg.strip('"').strip("'"))
        if not target.exists():
            self._warning(f"Directory not found: {target}")
            return
        if not target.is_dir():
            self._warning(f"Not a directory: {target}")
            return
        os.chdir(target)
        self._refresh_workspace_prompt()
        self._success(f"Workspace: {target}")

    def _list_files(self, arg: str) -> None:
        target = self._resolve_workspace_path(arg.strip('"').strip("'") or ".")
        if not target.exists():
            self._warning(f"Path not found: {target}")
            return
        if target.is_file():
            print(target.name)
            return
        self._section(f"Files: {target.name or target}")
        entries = sorted(target.iterdir(), key=lambda p: (not p.is_dir(), p.name.lower()))
        for entry in entries[:100]:
            suffix = "/" if entry.is_dir() else ""
            print(f"{entry.name}{suffix}")
        if len(entries) > 100:
            self._notice(f"... {len(entries) - 100} more")

    def _tree(self, arg: str) -> None:
        path_arg, depth = self._parse_tree_args(arg)
        target = self._resolve_workspace_path(path_arg)
        if not target.exists():
            self._warning(f"Path not found: {target}")
            return
        if target.is_file():
            print(target.name)
            return
        self._section(f"Tree: {target.name or target}")
        print(f"{target.name}/")
        self._print_tree(target, prefix="", depth=0, max_depth=depth)

    def _parse_tree_args(self, arg: str) -> tuple[str, int]:
        try:
            parts = shlex.split(arg, posix=False)
        except ValueError:
            parts = arg.split()
        path = "."
        depth = 2
        index = 0
        while index < len(parts):
            part = parts[index]
            if part in {"--depth", "-d"} and index + 1 < len(parts):
                try:
                    depth = max(1, min(5, int(parts[index + 1])))
                except ValueError:
                    depth = 2
                index += 2
                continue
            path = part.strip('"').strip("'")
            index += 1
        return path or ".", depth

    def _print_tree(self, root: Path, *, prefix: str, depth: int, max_depth: int) -> None:
        if depth >= max_depth:
            return
        ignored = {".git", "__pycache__", ".pytest_cache", ".mypy_cache", "node_modules", ".venv"}
        try:
            entries = [entry for entry in sorted(root.iterdir(), key=lambda p: (not p.is_dir(), p.name.lower())) if entry.name not in ignored]
        except OSError as exc:
            print(f"{prefix}{self._danger(f'[error: {exc}]')}")
            return
        shown = entries[:40]
        for index, entry in enumerate(shown):
            connector = "`-- " if index == len(shown) - 1 else "|-- "
            print(f"{prefix}{connector}{entry.name}{'/' if entry.is_dir() else ''}")
            if entry.is_dir():
                next_prefix = prefix + ("    " if index == len(shown) - 1 else "|   ")
                self._print_tree(entry, prefix=next_prefix, depth=depth + 1, max_depth=max_depth)
        if len(entries) > len(shown):
            print(f"{prefix}`-- ... {len(entries) - len(shown)} more")

    def _read_file(self, arg: str) -> None:
        if not arg:
            self._warning("Usage: /read <path>")
            return
        cleaned, line_number = self._parse_open_target(arg)
        if not cleaned:
            self._notice("No changed file yet. Use /changes after a file write or edit.")
            return
        target = self._resolve_workspace_path(cleaned)
        if not target.is_file():
            self._warning(f"File not found: {target}")
            return
        try:
            text = target.read_text(encoding="utf-8", errors="replace")
        except OSError as exc:
            self._error(f"Could not read file: {exc}")
            return
        lines = text.splitlines()
        relative = self._workspace_relative_path(target)
        title = f"Open: {relative}:{line_number}" if line_number else f"Open: {relative}"
        self._section(title)
        if line_number:
            self._print_file_window(lines, center=line_number, radius=20)
        else:
            self._print_file_window(lines, center=None, radius=0, max_lines=200)
        print(self._muted(f"Next: /diff {relative}  |  /open {relative}:<line>"))

    def _parse_open_target(self, arg: str) -> tuple[str, int | None]:
        cleaned = arg.strip().strip('"').strip("'")
        line_number: int | None = None
        match = re.match(r"^(?P<path>.+):(?P<line>[1-9]\d*)$", cleaned)
        if match:
            cleaned = match.group("path").strip('"').strip("'")
            line_number = int(match.group("line"))
        if cleaned.lower() == "last":
            cleaned = self._last_changed_file() or ""
        return cleaned, line_number

    def _print_file_window(
        self,
        lines: list[str],
        *,
        center: int | None,
        radius: int,
        max_lines: int | None = None,
    ) -> None:
        total = len(lines)
        if total == 0:
            print(self._muted("(empty file)"))
            return
        if center is None:
            start = 1
            end = min(total, max_lines or total)
            current = None
        else:
            current = max(1, min(total, center))
            start = max(1, current - radius)
            end = min(total, current + radius)
            if center > total:
                self._notice(f"Line {center} is past EOF; showing line {total}.")
        width = len(str(end))
        for line_no in range(start, end + 1):
            marker = ">" if current == line_no else " "
            print(f"{marker} {line_no:>{width}} | {lines[line_no - 1]}")
        if end < total:
            self._notice(f"... {total - end} more lines")

    def _write_file(self, arg: str, *, append: bool) -> None:
        path_text, content = self._split_path_and_text(arg)
        if not path_text:
            self._warning(f"Usage: {'/append' if append else '/write'} <path> <text>")
            return
        if not content:
            content = self._read_multiline_input(append=append)
        target = self._resolve_workspace_path(path_text)
        target.parent.mkdir(parents=True, exist_ok=True)
        try:
            if append:
                with target.open("a", encoding="utf-8") as handle:
                    handle.write(content)
                    if content and not content.endswith("\n"):
                        handle.write("\n")
            else:
                target.write_text(content, encoding="utf-8")
        except OSError as exc:
            self._error(f"Could not write file: {exc}")
            return
        action = "Appended" if append else "Wrote"
        display = self._remember_changed_file(target)
        self._success(f"{action}: {display}")
        self._print_changed_file_followup([display])

    def _read_multiline_input(self, *, append: bool, purpose: str | None = None) -> str:
        action = purpose or ("append" if append else "write")
        self._notice(f"Enter text to {action}. Finish with a single line containing .end")
        lines: list[str] = []
        while True:
            try:
                line = input()
            except (EOFError, KeyboardInterrupt):
                print()
                break
            if line == ".end":
                break
            lines.append(line)
        return "\n".join(lines)

    def _parse_shell_shortcut(self, raw: str) -> tuple[str, int, str | None]:
        value = raw.strip()
        timeout = 30
        if not value:
            return "", timeout, "Usage: !<powershell command> or /shell [--timeout N] <command>"
        match = re.match(r"^--timeout\s+(\S+)(?:\s+([\s\S]+))?$", value)
        if match:
            raw_timeout, rest = match.group(1), (match.group(2) or "").strip()
            try:
                timeout = int(raw_timeout)
            except ValueError:
                return "", timeout, "Usage: --timeout must be an integer number of seconds."
            if timeout < 1 or timeout > 600:
                return "", timeout, "Usage: --timeout must be between 1 and 600 seconds."
            if not rest:
                return "", timeout, "Usage: /shell [--timeout N] <command>"
            value = rest
        return value, timeout, None

    async def _rerun_last_shell_shortcut(self) -> None:
        if not self._last_shell_command:
            self._notice("No shell command to rerun yet.")
            return
        self._notice(f"Rerunning shell: {self._truncate_display(self._last_shell_command, limit=88)}")
        await self._run_shell_shortcut(self._last_shell_command, timeout=self._last_shell_timeout, remember=False)

    async def _run_shell_shortcut(self, command: str, *, timeout: int | None = None, remember: bool = True) -> None:
        parsed_command, parsed_timeout, error = self._parse_shell_shortcut(command)
        if timeout is not None:
            parsed_timeout = timeout
        if error:
            self._warning(error)
            return
        if not parsed_command:
            self._warning("Usage: !<powershell command>")
            return
        if remember:
            self._last_shell_command = parsed_command
            self._last_shell_timeout = parsed_timeout
        self._section(f"Shell: {parsed_command}")
        proc = await asyncio.create_subprocess_exec(
            "powershell",
            "-NoProfile",
            "-NonInteractive",
            "-Command",
            parsed_command,
            cwd=str(Path.cwd()),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        try:
            stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=parsed_timeout)
        except asyncio.TimeoutError:
            proc.kill()
            stdout, stderr = await proc.communicate()
            self._warning(f"[shell] timed out after {parsed_timeout}s")
            self._notice("Next: use !! to rerun, or ! --timeout N <cmd> / /shell --timeout N <cmd> for a longer run.")
        out_text = stdout.decode(errors="replace").strip()
        err_text = stderr.decode(errors="replace").strip()
        if out_text:
            print(out_text[:20_000])
        if err_text:
            print(err_text[:20_000], file=sys.stderr)
        status = "OK" if proc.returncode == 0 else "Error"
        print(self._ok(f"[shell] exit {proc.returncode}") if status == "OK" else self._danger(f"[shell] exit {proc.returncode}"))
        if status != "OK":
            self._notice("Next: check stderr, use !! to rerun, or try a narrower command to isolate the failure.")

    def _doctor(self) -> None:
        has_key = bool(os.environ.get("DEEPSEEK_API_KEY") or os.environ.get("DEEPSEEK_API_KEYS"))
        endpoint = os.environ.get("DEEPSEEK_ENDPOINTS") or os.environ.get("DEEPSEEK_ENDPOINT") or "default"
        rows: list[tuple[str, Any]] = [("Workspace", self._display_path(Path.cwd()))]
        git = self._git_summary()
        if git:
            rows.append(("Git", f"{git['branch']} ({'dirty' if git['dirty'] else 'clean'})"))
        rows.extend(
            [
                ("Model", self.model),
                ("API key", "configured" if has_key else "missing"),
                ("Stream", "on" if self.stream else "off"),
                ("Tools", f"{'enabled' if self.tools else 'disabled'} ({len(self.tools or [])})"),
                ("Endpoint", endpoint),
                ("Env file", os.environ.get("DEEPSEEK_ENV_FILE") or ".env auto"),
                ("Last shell", self._truncate_display(self._last_shell_command, limit=56) if self._last_shell_command else "none"),
            ]
        )
        if self._last_error_summary:
            rows.append(("Last error", self._last_error_summary))
        if not has_key:
            rows.append(("Suggestion", "/login"))
        if endpoint not in {"default", "https://api.deepseek.com"}:
            rows.append(("Suggestion", "If requests fail, try the default endpoint"))
            rows.append(("Endpoint fix", "DEEPSEEK_ENDPOINTS=https://api.deepseek.com"))
        if self.stream:
            rows.append(("Suggestion", "If stream fails repeatedly, use /stream off"))
        for suggestion in self._last_error_suggestions[:3]:
            rows.append(("Recovery", suggestion))
        try:
            import certifi  # noqa: F401

            rows.append(("certifi", "installed"))
        except Exception as exc:
            rows.append(("certifi", f"missing ({exc})"))
        self._panel("Doctor", rows, subtitle="Local runtime diagnostics.")

    def _git_summary(self) -> dict[str, Any] | None:
        branch = self._run_git(["git", "branch", "--show-current"], timeout=3)
        if branch is None:
            return None
        branch = branch.strip() or "detached"
        status = self._run_git(["git", "status", "--porcelain"], timeout=3)
        return {"branch": branch, "dirty": bool((status or "").strip())}

    def _run_git(self, command: list[str], *, timeout: int) -> str | None:
        try:
            result = subprocess.run(
                command,
                cwd=str(Path.cwd()),
                capture_output=True,
                text=True,
                timeout=timeout,
                check=False,
            )
        except (OSError, subprocess.SubprocessError):
            return None
        if result.returncode != 0:
            return None
        return result.stdout

    def _refresh_workspace_prompt(self) -> None:
        if not getattr(self.processor, "messages", None):
            return
        first = self.processor.messages[0]
        if first.role != "system" or not isinstance(first.content, str):
            return
        marker = "\n\nCurrent workspace:"
        base = first.content.split(marker, 1)[0]
        first.content = _terminal_system_prompt(base, tools_enabled=bool(self.tools))


def build_terminal_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="deepseek-terminal")
    parser.add_argument("--model", default=None)
    parser.add_argument("--api-key", default=None)
    parser.add_argument("--endpoint", default=None)
    parser.add_argument("--no-stream", action="store_true", help="Disable streaming output.")
    parser.add_argument("--no-tools", action="store_true", help="Disable local file/tool access.")
    parser.add_argument("--max-tokens", type=int, default=None)
    parser.add_argument("--temperature", type=float, default=None)
    return parser


def _load_tools(enable_tools: bool) -> tuple[list[dict[str, Any]] | None, Any | None]:
    if not enable_tools:
        return None, None
    try:
        from python_src.tools import build_default_tool_registry, get_deepseek_tools

        return get_deepseek_tools(), build_default_tool_registry()
    except Exception as exc:
        print(f"Warning: full toolset could not be loaded: {exc}", file=sys.stderr)
        print("Falling back to core file tools: read_file, write_file, edit_file, glob_files, grep_files.", file=sys.stderr)
        try:
            from deepseek_code.core.tool_adapter import ToolRegistry
            from python_src.tools.FileEditTool.FileEditTool import FileEditTool
            from python_src.tools.FileReadTool.FileReadTool import FileReadTool
            from python_src.tools.FileWriteTool.FileWriteTool import FileWriteTool
            from python_src.tools.GlobTool.GlobTool import GlobTool
            from python_src.tools.GrepTool.GrepTool import GrepTool

            fallback_tools = [FileReadTool, FileWriteTool, FileEditTool, GlobTool, GrepTool]
            registry = ToolRegistry()
            for tool in fallback_tools:
                registry.register(tool.name, tool.handler)
            return [tool.to_deepseek_schema() for tool in fallback_tools], registry
        except Exception as fallback_exc:
            print(f"Warning: file tools disabled because fallback loading failed: {fallback_exc}", file=sys.stderr)
            return None, None


def _terminal_system_prompt(base: str, *, tools_enabled: bool) -> str:
    today = datetime.now().astimezone()
    tool_note = (
        "Local file tools are enabled by default in this terminal. "
        "You may read, write, and edit files in the current workspace when the user asks."
        if tools_enabled
        else "Local file tools are disabled for this session."
    )
    return (
        f"{base}\n\n"
        f"Current date: {today:%Y-%m-%d} ({today:%A}, local timezone {today:%z}).\n"
        "For requests involving today, latest, daily problems, schedules, or other time-sensitive facts, "
        "use this date and avoid stale dates unless the user explicitly asks for them.\n"
        f"Current workspace: {os.getcwd()}\n"
        f"{tool_note}"
    )


async def run_terminal(options: TerminalOptions) -> int:
    config = DeepSeekConfig.from_env().with_overrides(
        api_key=options.api_key,
        model=options.model,
        endpoint=options.endpoint,
    )
    model = options.model or config.default_model
    if not config.api_keys:
        terminal = DeepSeekTerminal(
            client=None,
            processor=OfflineProcessor(
                model=model,
                system_prompt=_terminal_system_prompt(options.system_prompt, tools_enabled=False),
            ),
            model=model,
            tools=None,
            stream=options.stream,
            max_tokens=options.max_tokens,
            temperature=options.temperature,
        )
        print("No DeepSeek API key configured yet. Type /login for setup instructions.")
        return await terminal.run()
    try:
        from deepseek_code.client.deepseek_client import DeepSeekClient
        from deepseek_code.core.code_processor import CodeProcessor
    except Exception as exc:
        terminal = DeepSeekTerminal(
            client=None,
            processor=OfflineProcessor(
                model=model,
                system_prompt=_terminal_system_prompt(options.system_prompt, tools_enabled=False),
                reason=f"DeepSeek client dependencies are not ready: {exc}",
            ),
            model=model,
            tools=None,
            stream=options.stream,
            max_tokens=options.max_tokens,
            temperature=options.temperature,
        )
        print(f"DeepSeek client is offline: {exc}")
        print("Local slash commands are still available. Type /help.")
        return await terminal.run()

    tools, tool_registry = _load_tools(options.enable_tools)
    async with DeepSeekClient(config) as client:
        processor = CodeProcessor(
            client,
            model=model,
            tool_registry=tool_registry,
            system_prompt=_terminal_system_prompt(options.system_prompt, tools_enabled=bool(tools)),
        )
        terminal = DeepSeekTerminal(
            client=client,
            processor=processor,
            model=model,
            tools=tools,
            stream=options.stream,
            max_tokens=options.max_tokens,
            temperature=options.temperature,
        )
        return await terminal.run()


async def amain(argv: list[str] | None = None) -> int:
    args = build_terminal_parser().parse_args(argv)
    return await run_terminal(
        TerminalOptions(
            model=args.model,
            api_key=args.api_key,
            endpoint=args.endpoint,
            stream=not args.no_stream,
            enable_tools=not args.no_tools,
            max_tokens=args.max_tokens,
            temperature=args.temperature,
        )
    )


def main() -> None:
    raise SystemExit(asyncio.run(amain(sys.argv[1:])))


if __name__ == "__main__":
    main()

