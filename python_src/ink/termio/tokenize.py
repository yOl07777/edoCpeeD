from __future__ import annotations

from typing import Any


def _is_csi_final(code: int) -> bool:
    return 0x40 <= code <= 0x7E


def _is_csi_param(code: int) -> bool:
    return 0x30 <= code <= 0x3F


def _is_csi_intermediate(code: int) -> bool:
    return 0x20 <= code <= 0x2F


def _is_esc_final(code: int) -> bool:
    return 0x30 <= code <= 0x7E


class Tokenizer:
    def __init__(self, *, x10Mouse: bool = False) -> None:
        self.state = "ground"
        self._buffer = ""
        self.x10Mouse = x10Mouse

    def feed(self, input: str) -> list[dict[str, str]]:
        tokens, self.state, self._buffer = _tokenize(input, self.state, self._buffer, False, self.x10Mouse)
        return tokens

    def flush(self) -> list[dict[str, str]]:
        tokens, self.state, self._buffer = _tokenize("", self.state, self._buffer, True, self.x10Mouse)
        return tokens

    def reset(self) -> None:
        self.state = "ground"
        self._buffer = ""

    def buffer(self) -> str:
        return self._buffer


def _tokenize(input: str, state: str, initial_buffer: str, flush: bool, x10_mouse: bool) -> tuple[list[dict[str, str]], str, str]:
    data = initial_buffer + input
    tokens: list[dict[str, str]] = []
    i = 0
    text_start = 0
    seq_start = 0
    current_state = state

    def flush_text() -> None:
        nonlocal text_start
        if i > text_start:
            text = data[text_start:i]
            if text:
                tokens.append({"type": "text", "value": text})
        text_start = i

    def emit_sequence(seq: str) -> None:
        nonlocal current_state, text_start
        if seq:
            tokens.append({"type": "sequence", "value": seq})
        current_state = "ground"
        text_start = i

    while i < len(data):
        code = ord(data[i])
        if current_state == "ground":
            if code == 0x1B:
                flush_text()
                seq_start = i
                current_state = "escape"
            i += 1
        elif current_state == "escape":
            if code == 0x5B:
                current_state = "csi"
                i += 1
            elif code == 0x5D:
                current_state = "osc"
                i += 1
            elif code in (0x50, 0x5F):
                current_state = "string"
                i += 1
            elif code == 0x4F:
                current_state = "ss3"
                i += 1
            elif _is_csi_intermediate(code):
                current_state = "escapeIntermediate"
                i += 1
            elif _is_esc_final(code):
                i += 1
                emit_sequence(data[seq_start:i])
            elif code == 0x1B:
                emit_sequence(data[seq_start:i])
                seq_start = i
                current_state = "escape"
                i += 1
            else:
                current_state = "ground"
                text_start = seq_start
        elif current_state == "escapeIntermediate":
            if _is_csi_intermediate(code):
                i += 1
            elif _is_esc_final(code):
                i += 1
                emit_sequence(data[seq_start:i])
            else:
                current_state = "ground"
                text_start = seq_start
        elif current_state == "csi":
            if x10_mouse and code == 0x4D and i - seq_start == 2:
                if i + 4 <= len(data):
                    i += 4
                    emit_sequence(data[seq_start:i])
                else:
                    i = len(data)
            elif _is_csi_final(code):
                i += 1
                emit_sequence(data[seq_start:i])
            elif _is_csi_param(code) or _is_csi_intermediate(code):
                i += 1
            else:
                current_state = "ground"
                text_start = seq_start
        elif current_state == "ss3":
            if 0x40 <= code <= 0x7E:
                i += 1
                emit_sequence(data[seq_start:i])
            else:
                current_state = "ground"
                text_start = seq_start
        elif current_state in ("osc", "string"):
            if code == 0x07:
                i += 1
                emit_sequence(data[seq_start:i])
            elif code == 0x1B and i + 1 < len(data) and ord(data[i + 1]) == 0x5C:
                i += 2
                emit_sequence(data[seq_start:i])
            else:
                i += 1

    if current_state == "ground":
        flush_text()
        return tokens, current_state, ""
    if flush:
        remaining = data[seq_start:]
        if remaining:
            tokens.append({"type": "sequence", "value": remaining})
        return tokens, "ground", ""
    return tokens, current_state, data[seq_start:]


async def createTokenizer(*args: Any, **kwargs: Any) -> Any:
    options = args[0] if args else kwargs
    if not isinstance(options, dict):
        options = {}
    return Tokenizer(x10Mouse=bool(options.get("x10Mouse", False)))
