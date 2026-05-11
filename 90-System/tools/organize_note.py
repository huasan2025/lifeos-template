#!/usr/bin/env python3
"""Organize a local text file with a local Ollama model."""

from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path


DEFAULT_MODEL = "qwen3.6"
DEFAULT_HOST = "http://127.0.0.1:11434"
SYSTEM_PROMPT = """你是一个谨慎的中文文本整理助手。

你的任务是整理用户给出的原始文本，使其更清晰、更适合阅读。

必须遵守：
1. 保留原意，不补充原文没有的新事实。
2. 可以去掉重复、口头禅和明显无意义的噪音。
3. 可以重组结构、加标题、加列表、提炼待办。
4. 直接输出最终结果，不要解释你的处理过程。
5. 默认输出 Markdown。"""


def build_prompt(user_instruction: str, source_text: str) -> str:
    return (
        f"请按下面要求整理文本。\n\n"
        f"要求：\n{user_instruction.strip()}\n\n"
        f"原始文本如下：\n\n{source_text}"
    )


def call_ollama(host: str, model: str, prompt: str) -> str:
    payload = {
        "model": model,
        "prompt": prompt,
        "system": SYSTEM_PROMPT,
        "stream": False,
    }
    data = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        f"{host.rstrip('/')}/api/generate",
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=600) as response:
            body = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Ollama API 返回错误：{exc.code} {detail}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(
            "无法连接到 Ollama。请先确认 `brew services start ollama` 已启动，"
            "并且模型已下载。"
        ) from exc

    result = body.get("response", "").strip()
    if not result:
        raise RuntimeError("模型没有返回内容。")
    return result


def default_output_path(source_path: Path) -> Path:
    return source_path.with_name(f"{source_path.stem}.organized.md")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Read a local file, send it to Ollama, and save an organized Markdown version."
    )
    parser.add_argument("source", help="Path to the source text/markdown file")
    parser.add_argument("instruction", help="Natural-language instruction for how to organize it")
    parser.add_argument(
        "-o",
        "--output",
        help="Output file path. Defaults to <source>.organized.md in the same folder.",
    )
    parser.add_argument(
        "-m",
        "--model",
        default=DEFAULT_MODEL,
        help=f"Ollama model name. Default: {DEFAULT_MODEL}",
    )
    parser.add_argument(
        "--host",
        default=DEFAULT_HOST,
        help=f"Ollama host URL. Default: {DEFAULT_HOST}",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    source_path = Path(args.source).expanduser().resolve()
    if not source_path.exists():
        print(f"找不到文件：{source_path}", file=sys.stderr)
        return 1
    if not source_path.is_file():
        print(f"不是文件：{source_path}", file=sys.stderr)
        return 1

    source_text = source_path.read_text(encoding="utf-8")
    if not source_text.strip():
        print(f"文件内容为空：{source_path}", file=sys.stderr)
        return 1

    output_path = (
        Path(args.output).expanduser().resolve()
        if args.output
        else default_output_path(source_path)
    )

    prompt = build_prompt(args.instruction, source_text)
    try:
        result = call_ollama(args.host, args.model, prompt)
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    output_path.write_text(result + "\n", encoding="utf-8")
    print(f"已生成：{output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
