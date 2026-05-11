from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
OUT = ROOT / "python_src"
REPORT = ROOT / "PYTHON_MIGRATION_REPORT.md"

SOURCE_EXTS = {".ts", ".tsx", ".js"}


def py_path_for(path: Path) -> Path:
    rel = path.relative_to(SRC)
    return (OUT / rel).with_suffix(".py")


def module_name(path: Path) -> str:
    return ".".join(py_path_for(path).relative_to(OUT).with_suffix("").parts)


def extract_symbols(text: str) -> tuple[list[str], list[str], list[str]]:
    functions = sorted(
        set(
            re.findall(r"export\s+(?:async\s+)?function\s+([A-Za-z_][A-Za-z0-9_]*)", text)
            + re.findall(
                r"export\s+const\s+([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(?:async\s*)?\([^)]*\)\s*=>",
                text,
            )
        )
    )
    classes = sorted(set(re.findall(r"export\s+class\s+([A-Za-z_][A-Za-z0-9_]*)", text)))
    constants = sorted(
        set(
            name
            for name in re.findall(r"export\s+const\s+([A-Za-z_][A-Za-z0-9_]*)", text)
            if name not in functions
        )
    )
    return functions, classes, constants


def convert_to_python_stub(path: Path, text: str) -> str:
    functions, classes, constants = extract_symbols(text)
    src_rel = path.relative_to(ROOT).as_posix()
    lines: list[str] = [
        '"""',
        f"Python migration draft for `{src_rel}`.",
        "",
        "This file was generated from the TypeScript source to preserve the",
        "module boundary while the runtime implementation is migrated.",
        "Claude/Anthropic model calls should be routed through `deepseek_code`.",
        '"""',
        "",
        "from __future__ import annotations",
        "",
        "from typing import Any",
        "",
    ]

    if constants:
        for name in constants:
            lines.append(f"{name}: Any = None")
        lines.append("")

    for cls in classes:
        lines.extend(
            [
                f"class {cls}:",
                f'    """Migrated placeholder for TypeScript class `{cls}`."""',
                "",
                "    def __init__(self, *args: Any, **kwargs: Any) -> None:",
                "        self.args = args",
                "        self.kwargs = kwargs",
                "",
            ]
        )

    for fn in functions:
        lines.extend(
            [
                f"async def {fn}(*args: Any, **kwargs: Any) -> Any:",
                f'    """Migrated placeholder for TypeScript function `{fn}`."""',
                "    raise NotImplementedError(",
                f'        "{module_name(path)}.{fn} still needs business-logic migration"',
                "    )",
                "",
            ]
        )

    if not (functions or classes or constants):
        lines.extend(
            [
                "def _module_migration_placeholder(*args: Any, **kwargs: Any) -> Any:",
                "    raise NotImplementedError(",
                f'        "{module_name(path)} still needs business-logic migration"',
                "    )",
                "",
            ]
        )

    return "\n".join(lines)


def ensure_packages() -> None:
    for directory in [OUT, *[p for p in OUT.rglob("*") if p.is_dir()]]:
        init = directory / "__init__.py"
        if not init.exists():
            init.write_text('"""Migrated Python package."""\n', encoding="utf-8")


def main() -> None:
    OUT.mkdir(exist_ok=True)
    generated = 0
    skipped = 0

    for path in SRC.rglob("*"):
        if path.suffix.lower() not in SOURCE_EXTS:
            continue
        target = py_path_for(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists():
            skipped += 1
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        target.write_text(convert_to_python_stub(path, text), encoding="utf-8")
        generated += 1

    ensure_packages()
    REPORT.write_text(build_report(generated, skipped), encoding="utf-8-sig")
    print(f"generated={generated} skipped={skipped} out={OUT}")


def build_report(generated: int, skipped: int) -> str:
    return "\n".join(
        [
            "# Python 迁移报告",
            "",
            f"- 源目录：`{SRC}`",
            f"- 输出目录：`{OUT}`",
            f"- 新生成 Python 文件数：`{generated}`",
            f"- 已存在并跳过文件数：`{skipped}`",
            "",
            "说明：本次迁移不会覆盖原 `src` TypeScript 源码，而是在 `python_src` 中保留同构目录。",
            "自动生成文件会保留模块边界和导出符号，具体业务逻辑需要按模块逐步补全。",
            "DeepSeek API 相关核心文件已手写迁移到 `deepseek_code`，并通过 `python_src/services/api` 暴露兼容入口。",
            "",
            "## 当前完成度",
            "",
            "- 已完成：生成 Python 目录镜像、导出符号草案、DeepSeek API 客户端、消息适配、工具适配、流式解析、负载均衡。",
            "- 未完成：React/Ink UI、复杂业务逻辑、插件系统、MCP 全链路、权限 UI、所有工具的完整 Python 行为。",
            "- 原则：保留 `src` 基本不变，后续应按模块逐步把 `python_src` 中的占位函数替换成真实实现。",
            "",
        ]
    )


if __name__ == "__main__":
    main()
