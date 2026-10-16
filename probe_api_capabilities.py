"""探测模型是否支持 function calling（tools）—— 换模型 / 换 API 供应商时先跑这个。

背景：2026-09-28 原默认模型 agnes-1.5-flash 下架（503 model_not_found），
本脚本用于给 agentic 执行器选型，逐项验证：
  1. 基础连通性
  2. tools 参数是否被接受、是否产生 tool_calls
  3. tool 结果回灌后能否继续（loop 闭环）
  4. tool_choice=required（强制调用，兜底手段）

运行：python probe_api_capabilities.py
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, str(Path(__file__).parent))

from run_agentic_eval import load_credentials  # noqa: E402  凭据加载与评估脚本同源

load_credentials()

from openai import OpenAI  # noqa: E402

api_key = os.environ.get("AGNES_API_KEY", "")
base_url = os.environ.get("AGNES_BASE_URL", "https://apihub.agnes-ai.com/v1")

# 候选：环境变量指定 + 当前可用模型（agnes-1.5-flash 已于 2026-09 下架）
CANDIDATES = [m for m in [os.environ.get("AGNES_MODEL"), "agnes-3.0-flash", "agnes-2.5-flash"] if m]

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

print(f"key_set={bool(api_key)}  candidates={CANDIDATES}\n")


def chat(model: str, messages, **kwargs):
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
    last_message = None
    try:
        msgs = [
            {"role": "system", "content": "你有 load_skill 工具，可用技能：weather / github / summarize。"},
            {"role": "user", "content": "帮我查一下北京今天的天气。"},
        ]
        r = chat(model, msgs, tools=TOOLS, tool_choice="auto")
        last_message = r.choices[0].message
        print("  [tools] content:", repr((last_message.content or "")[:80]))
        print("  [tools] finish_reason:", r.choices[0].finish_reason)
        print("  [tools] tool_calls:", last_message.tool_calls)
        if last_message.tool_calls:
            tc = last_message.tool_calls[0]
            print("  >>> tool_call:", tc.function.name, tc.function.arguments)
            ok = True
    except Exception as e:
        print("  [tools] FAIL:", type(e).__name__, str(e)[:200])

    # 3. tool 结果回灌 -> 能否继续（loop 闭环）
    if tc is not None and last_message is not None:
        try:
            msgs.append(last_message)
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
for model, ok in results.items():
    print(f"{model}: {'支持 function calling' if ok else '不可用 / 未产生 tool_calls'}")
