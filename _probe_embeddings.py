"""探测 Agnes API 是否提供 embeddings 接口 —— 技能检索对照实验的前置检查。

运行：cd agent-skill-framework && python _probe_embeddings.py
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, str(Path(__file__).parent))

from run_agentic_eval import load_credentials  # noqa: E402

load_credentials()

from openai import OpenAI  # noqa: E402

api_key = os.environ.get("AGNES_API_KEY", "")
base_url = os.environ.get("AGNES_BASE_URL", "https://apihub.agnes-ai.com/v1")
client = OpenAI(api_key=api_key, base_url=base_url)

print(f"key_set={bool(api_key)}  base_url={base_url}\n")

CANDIDATES = [
    "text-embedding-3-small",
    "text-embedding-3-large",
    "text-embedding-ada-002",
    "bge-m3",
    "bge-large-zh-v1.5",
    "doubao-embedding",
    "embedding-2",
    "embedding-3",
    "multilingual-e5-large",
    "qwen3-embedding",
]

for m in CANDIDATES:
    try:
        r = client.embeddings.create(model=m, input="测试文本 hello world", timeout=30)
        print(f"{m}  OK  dim={len(r.data[0].embedding)}")
    except Exception as e:  # noqa: BLE001
        print(f"{m}  FAIL  {type(e).__name__}: {str(e)[:130]}")

# 顺便列出网关可见的模型（部分网关支持 /models）
try:
    ms = client.models.list(timeout=30)
    names = sorted(x.id for x in ms.data)
    emb = [n for n in names if any(k in n.lower() for k in ("embed", "bge", "e5", "gte"))]
    print(f"\n/models 可见 {len(names)} 个模型；疑似 embedding：{emb[:20]}")
except Exception as e:  # noqa: BLE001
    print(f"\n/models 不可用：{type(e).__name__}: {str(e)[:130]}")
