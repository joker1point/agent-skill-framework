"""一次性诊断脚本：探测 Agnes AI 模型的 function calling (tools) 支持情况。

背景：原配置模型 agnes-1.5-flash 已下架（503 model_not_found，2026-09-28）。
用途：为新执行器选型 —— 哪个模型支持 tools / tool 回灌 / tool_choice=required。

运行：python _probe_tools.py
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

sys.stdout.reconfigure(encoding="utf-8")

ENV_PATH = Path(r"C:\Users\biren\Documents\trae_projects\luyan\CharacterSeed\.env")
load_dotenv(ENV_PATH)

api_key = os.environ.get("AGNES_API_KEY", "")
base_url = "https://apihub.agnes-ai.com/v1"

CANDIDATES = ["agnes-3.0-flash", "agnes-2.5-flash", "agnes-2.5-pro"]

client = OpenAI(api_key=api_key, base_url=base_url)

TOOLS = [{
    "type": "function",
    "function": {
        "name": "load_skill",
        "description": "加载指定技能的详细知识内容，在回答相关问题前调用",
        "parameters": {
            "type": "object",
            "properties": {
                "skill_name": {"type": "string", "description": "技能名称"}
            },
            "required": ["skill_name"],
        },
    },
}]

print(f"key_set={bool(api_key)}\n")


def chat(model, messages, **kwargs):
    return client.chat.completions.create(
        model=model, messages=messages, max_tokens=200, temperature=0.0, timeout=90, **kwargs
    )


def probe(model: str) -> bool:
    print(f"===== {model} =====")
    ok = False

    # 1. 基础调用
    try:
        r = chat(model, [{"role": "user", "content": "只回复两个字：正常"}])
        print("  [basic] OK:", repr(r.choices[0].message.content))
    except Exception as e:
        print("  [basic] FAIL:", type(e).__name__, str(e)[:200])
        return False

    # 2. tools 参数 + 是否产生 tool_calls
    tc = None
    try:
        msgs = [
            {"role": "system", "content": "你有 load_skill 工具，可用技能：weather / github / summarize。"},
            {"role": "user", "content": "帮我查一下北京今天的天气。"},
        ]
        r = chat(model, msgs, tools=TOOLS, tool_choice="auto")
        m = r.choices[0].message
        print("  [tools] content:", repr((m.content or "")[:80]))
        print("  [tools] finish_reason:", r.choices[0].finish_reason)
        print("  [tools] tool_calls:", m.tool_calls)
        if m.tool_calls:
            tc = m.tool_calls[0]
            print("  >>> tool_call:", tc.function.name, tc.function.arguments)
            ok = True
    except Exception as e:
        print("  [tools] FAIL:", type(e).__name__, str(e)[:200])

    # 3. tool 结果回灌 -> 能否继续（loop 闭环）
    if tc is not None:
        try:
            msgs.append(r.choices[0].message)
            msgs.append({
                "role": "tool",
                "tool_call_id": tc.id,
                "content": "weather 技能：用 curl -s 'wttr.in/Beijing?format=3' 查询。",
            })
            r2 = chat(model, msgs, tools=TOOLS, tool_choice="auto")
            m2 = r2.choices[0].message
            print("  [loop] content:", repr((m2.content or "")[:120]))
            print("  [loop] finish_reason:", r2.choices[0].finish_reason)
            print("  [loop] >>> 闭环可用" if not m2.tool_calls else "  [loop] 继续调用工具（多轮可跑）")
        except Exception as e:
            print("  [loop] FAIL:", type(e).__name__, str(e)[:200])

    # 4. tool_choice=required（兜底手段）
    try:
        r = chat(model, [{"role": "user", "content": "北京天气怎么样？"}], tools=TOOLS, tool_choice="required")
        print("  [required] tool_calls:", bool(r.choices[0].message.tool_calls))
    except Exception as e:
        print("  [required] FAIL:", type(e).__name__, str(e)[:200])

    print()
    return ok


results = {m: probe(m) for m in CANDIDATES}

print("===== 汇总 =====")
for m, ok in results.items():
    print(f"{m}: {'SUPPORT function calling' if ok else 'no tool_calls / 不可用'}")
