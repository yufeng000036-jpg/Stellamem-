#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
start_server.py —— 启动本地记忆编译模型服务

启动 llama.cpp 的 HTTP server，加载 Qwen3-4B 纯文本模型，
供 extract.py / judge.py 通过 HTTP 调用。

用法：
  python start_server.py        # 前台运行（Ctrl+C 停止）
  python start_server.py --bg   # 后台运行

依赖：llama.exe（llama.cpp 0.4.0+）
"""
import subprocess, sys, os
import shutil as _sh
from urllib.parse import urlparse
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config_loader import load_config

_cfg = load_config()
# LLAMA 优先读 config.json 的 llama_bin，其次自动探测（llama-server / llama.exe / llama）
LLAMA = _cfg.get("llama_bin") or \
        _sh.which("llama-server") or _sh.which("llama-server.exe") or \
        _sh.which("llama") or _sh.which("llama.exe")
if not LLAMA:
    print("[错误] 未找到 llama.cpp 可执行文件。请在 config.json 里填 llama_bin，或把它加进 PATH。")
    sys.exit(1)
MODEL = _cfg["model_name"]
_parsed = urlparse(_cfg["server_url"])
HOST = _parsed.hostname or "127.0.0.1"
PORT = str(_parsed.port or 8081)
NGL = "99"

def build_cmd():
    return [
        LLAMA, "serve",
        "-m", MODEL,
        "--port", PORT,
        "--host", HOST,
        "-ngl", NGL,
        "--device", "CUDA0",
        "-c", "8192",
    ]

def main():
    cmd = build_cmd()
    print("[启动] llama server，模型：", os.path.basename(MODEL))
    print("[启动] 地址：http://" + HOST + ":" + PORT)
    print("[启动] 命令：", " ".join(cmd))
    print("[提示] 保持本进程运行，然后用 extract.py / judge.py 调用")

    if "--bg" in sys.argv:
        # 后台运行（Windows 用 CREATE_NEW_PROCESS_GROUP）
        subprocess.Popen(cmd, creationflags=subprocess.CREATE_NEW_PROCESS_GROUP)
        print("[已后台启动]")
    else:
        # 前台运行（阻塞）
        subprocess.run(cmd)

if __name__ == "__main__":
    main()
