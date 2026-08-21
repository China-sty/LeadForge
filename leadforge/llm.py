"""LLM 客户端（OpenAI 兼容接口，结构化输出）。"""
from __future__ import annotations

import json
import os
import re
from typing import Any, Dict, List

from openai import OpenAI


def _balanced_end(text: str, start: int, opener: str, closer: str) -> int:
    depth = 0
    in_str = False
    escape = False
    for i in range(start, len(text)):
        ch = text[i]
        if in_str:
            if escape:
                escape = False
            elif ch == "\\":
                escape = True
            elif ch == '"':
                in_str = False
        else:
            if ch == '"':
                in_str = True
            elif ch == opener:
                depth += 1
            elif ch == closer:
                depth -= 1
                if depth == 0:
                    return i
    return -1


def extract_json(text: str) -> Any:
    text = text.strip()
    if not text:
        raise ValueError("模型返回了空内容")
    fence = re.search(r"```(?:json)?\s*(.*?)```", text, re.DOTALL)
    if fence:
        text = fence.group(1).strip()
    candidates = [text]
    for opener, closer in (("{", "}"), ("[", "]")):
        start = text.find(opener)
        if start != -1:
            end = _balanced_end(text, start, opener, closer)
            if end != -1:
                candidates.append(text[start : end + 1])
    for cand in candidates:
        try:
            return json.loads(cand)
        except json.JSONDecodeError:
            fixed = re.sub(r",\s*([}\]])", r"\1", cand)
            try:
                return json.loads(fixed)
            except json.JSONDecodeError:
                continue
    raise ValueError(f"无法从模型输出解析 JSON：{text[:300]}")


class LLMClient:
    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
        model: str | None = None,
    ):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY", "")
        self.base_url = base_url or os.getenv("OPENAI_BASE_URL", "https://api.deepseek.com/v1")
        self.model = model or os.getenv("LLM_MODEL", "deepseek-chat")
        if not self.api_key:
            raise RuntimeError("未配置 OPENAI_API_KEY")
        self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)

    def chat(self, messages: List[Dict[str, str]], temperature: float = 0.3, max_tokens: int = 2000) -> str:
        resp = self.client.chat.completions.create(
            model=self.model, messages=messages, temperature=temperature, max_tokens=max_tokens
        )
        return (resp.choices[0].message.content or "").strip()

    def chat_structured(self, messages: List[Dict[str, str]], result_cls, temperature: float = 0.0):
        """结构化输出：优先 function calling，回退 JSON 模式；返回 result_cls 实例。"""
        schema = result_cls.model_json_schema()
        data = None
        try:
            resp = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                tools=[{
                    "type": "function",
                    "function": {"name": "respond", "description": "返回结构化结果", "parameters": schema},
                }],
                tool_choice={"type": "function", "function": {"name": "respond"}},
            )
            msg = resp.choices[0].message
            if msg.tool_calls:
                data = json.loads(msg.tool_calls[0].function.arguments)
            elif msg.content:
                data = extract_json(msg.content)
        except Exception:
            data = None
        if data is None:
            data = extract_json(self.chat(messages, temperature=temperature))
        return result_cls.model_validate(data)
