from __future__ import annotations

import argparse
import asyncio
import sys

from deepseek_code.client.deepseek_client import DeepSeekClient
from deepseek_code.config import DeepSeekConfig
from deepseek_code.core.code_processor import CodeProcessor


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="deepseek-code")
    parser.add_argument("prompt", nargs="+", help="Prompt to send to DeepSeek.")
    parser.add_argument("--provider", default="deepseek", choices=["deepseek"])
    parser.add_argument("--model", default=None, help="DeepSeek model, e.g. deepseek-chat.")
    parser.add_argument("--api-key", default=None, help="Temporarily override DEEPSEEK_API_KEYS.")
    parser.add_argument("--endpoint", default=None, help="Temporarily override DEEPSEEK_ENDPOINTS.")
    parser.add_argument("--stream", action="store_true", help="Print streamed token deltas.")
    parser.add_argument("--enable-tools", action="store_true", help="Allow the model to call migrated local tools.")
    parser.add_argument("--max-tokens", type=int, default=None)
    parser.add_argument("--temperature", type=float, default=None)
    return parser


async def amain(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    config = DeepSeekConfig.from_env().with_overrides(
        api_key=args.api_key,
        model=args.model,
        endpoint=args.endpoint,
    )
    prompt = " ".join(args.prompt)
    tools = None
    tool_registry = None
    if args.enable_tools:
        from python_src.tools import build_default_tool_registry, get_deepseek_tools

        tools = get_deepseek_tools()
        tool_registry = build_default_tool_registry()
    async with DeepSeekClient(config) as client:
        processor = CodeProcessor(
            client,
            model=args.model or config.default_model,
            tool_registry=tool_registry,
        )
        if args.stream:
            async for delta in processor.stream_text(
                prompt,
                tools=tools,
                max_tokens=args.max_tokens,
                temperature=args.temperature,
            ):
                if isinstance(delta, str):
                    print(delta, end="", flush=True)
            print()
        else:
            response = await processor.run(
                prompt,
                tools=tools,
                max_tokens=args.max_tokens,
                temperature=args.temperature,
            )
            print(response.message.content or "")
    return 0


def main() -> None:
    raise SystemExit(asyncio.run(amain(sys.argv[1:])))


if __name__ == "__main__":
    main()
