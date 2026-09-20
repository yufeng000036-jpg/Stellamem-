#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
judge.py —— 星忆第二步：判断新 Claim 与已有记忆的关系

通过 HTTP 调用本地 llama server，判断一个新 Claim 与若干候选旧记忆的关系，
输出 8 种关系之一：NEW / DUPLICATE / REINFORCES / REFINES /
COMPATIBLE / SUPERSEDES / CONTRADICTS / UNCERTAIN。

用法：
  python judge.py '<新Claim JSON>' '<候选旧记忆 JSON数组>'

依赖：仅 Python 标准库 + 一个已启动的 llama server。
"""
import urllib.request, json, sys, re, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config_loader import load_config

SERVER = load_config()["server_url"]

SYSTEM = (
    "你是记忆关系判断器。判断一条新记忆与若干条已有记忆的关系。\n"
    "关系类型（8 选 1）：\n"
    "  NEW：全新，与所有已有都无关\n"
    "  DUPLICATE：与某条已有完全重复\n"
    "  REINFORCES：强化某条已有（同一事实再次确认）\n"
    "  REFINES：细化某条已有（更具体，是子集）\n"
    "  COMPATIBLE：与某条兼容并存，不冲突\n"
    "  SUPERSEDES：取代某条已有（新的覆盖旧的）\n"
    "  CONTRADICTS：与某条矛盾\n"
    "  UNCERTAIN：无法判断\n"
    "只输出 JSON，不要解释、不要 markdown。\n"
    '输出格式：[{"against": <索引号或null>, "relation": "<关系>", "confidence": 0.0~1.0, "reason": "<一句话>"}]\n'
)

def call_llm(system, user, max_tokens=256, temp=0.0):
    body = json.dumps({
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "temperature": temp,
        "max_tokens": max_tokens,
        "stream": False,
    }).encode("utf-8")
    req = urllib.request.Request(
        SERVER + "/v1/chat/completions",
        data=body,
        headers={"Content-Type": "application/json"},
    )
    resp = urllib.request.urlopen(req, timeout=300)
    return json.loads(resp.read().decode("utf-8"))["choices"][0]["message"]["content"]

def parse_json(text):
    # 从后往前找 [ ... ]，返回最后一个能解析成 list 的
    results = []
    depth = 0
    start = -1
    for i, ch in enumerate(text):
        if ch == '[':
            if depth == 0:
                start = i
            depth += 1
        elif ch == ']':
            if depth > 0:
                depth -= 1
                if depth == 0 and start != -1:
                    try:
                        obj = json.loads(text[start:i+1])
                        if isinstance(obj, list):
                            results.append(obj)
                    except (json.JSONDecodeError, ValueError):
                        pass
    return results[-1] if results else None

def main():
    if len(sys.argv) < 3:
        print("用法：python judge.py '<新Claim JSON>' '<候选旧记忆 JSON数组>'")
        sys.exit(1)
    try:
        new_claim = json.loads(sys.argv[1])
        candidates = json.loads(sys.argv[2])
    except json.JSONDecodeError as e:
        print(f"[错误] JSON 解析失败：{e}")
        sys.exit(1)

    user = (
        "新记忆：\n" + json.dumps(new_claim, ensure_ascii=False, indent=2)
        + "\n已有记忆（数组，索引从 0 开始）：\n" + json.dumps(candidates, ensure_ascii=False, indent=2)
        + "\n判断关系，输出 JSON："
    )
    print("[运行] 判断关系...")
    try:
        out = call_llm(SYSTEM, user)
    except urllib.error.URLError as e:
        print(f"[错误] 无法连接 llama server：{e}")
        print("请先运行 start_server.py 启动本地模型服务。")
        sys.exit(2)

    result = parse_json(out)
    if result is None:
        print("[警告] 未能解析输出，模型原始输出：")
        print(out[:800])
        sys.exit(3)
    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
