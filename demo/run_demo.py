#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""run_demo.py —— 星忆 Demo（真·端到端，隔离沙箱）

真跑完整流程，全程在临时目录里操作，绝不碰你的真实记忆、绝不联网取数据：

  demo/user/ 的 7 天虚构日记
    → compiler/extract.py   日记 → Claim（调用你配置的模型服务）
    → compiler/sleep_purify.py --mode observe   Claim → memory-inbox.md
    → 展示产出

前置：
  1. 仓库根目录有 config.json（cp config.example.json config.json 后填路径）
  2. 模型服务已启动（见 docs/QUICKSTART.md）

用法：
  python demo/run_demo.py                  # 真端到端（需模型服务）
  python demo/run_demo.py --dry-run        # 只列步骤，不真跑
  python demo/run_demo.py --keep           # 跑完保留沙箱（默认保留，便于检查）
  python demo/run_demo.py --no-clean       # 同 --keep
  python demo/run_demo.py --samples 5      # 只跑前 5 篇（省时间）
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)

SUBDIRS = ["core", "long-term", "semantic", "episodic", "system", "working", "daily"]


def list_diaries():
    user_dir = os.path.join(HERE, "user")
    return sorted(f for f in os.listdir(user_dir) if f.endswith(".md"))


def make_sandbox_config(sandbox_mem):
    """在沙箱里生成专属 config.json，指向沙箱路径。"""
    tpl_path = os.path.join(REPO, "config.json")
    server_url = "http://127.0.0.1:8081"
    model_name = "<YOUR_MODEL_GGUF_PATH>"
    llama_bin = ""

    if os.path.isfile(tpl_path):
        try:
            # encoding="utf-8-sig" 兼容带 BOM 的 config.json（Windows 编辑器常见）
            with open(tpl_path, encoding="utf-8-sig") as fh:
                real = json.load(fh)
            server_url = real.get("server_url", server_url)
            model_name = real.get("model_name", model_name)
            llama_bin = real.get("llama_bin", "")
        except (json.JSONDecodeError, OSError) as e:
            print(f"  [警告] 读仓库 config.json 失败（{type(e).__name__}），"
                  f"回落到默认 {server_url}")
            print(f"         文件：{tpl_path}")

    mem = sandbox_mem.replace("\\", "/")
    cfg = {
        "memories_root": mem,
        "scripts_root": REPO.replace("\\", "/"),
        "model_name": model_name,
        "llama_bin": llama_bin,
        "server_url": server_url,
        "daily_dir": mem + "/daily",
        "system_dir": mem + "/system",
        "core_dir": mem + "/core",
        "longterm_dir": mem + "/long-term",
        "semantic_dir": mem + "/semantic",
    }
    cfg_path = os.path.join(sandbox_mem, "config.json")
    with open(cfg_path, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(cfg, fh, ensure_ascii=False, indent=2)
    return cfg_path, server_url


def run(cmd, env, timeout=600):
    """跑子进程，返回 (returncode, stdout, stderr)。"""
    try:
        r = subprocess.run(cmd, capture_output=True, text=True,
                           timeout=timeout, env=env, encoding="utf-8", errors="replace")
        return r.returncode, r.stdout or "", r.stderr or ""
    except subprocess.TimeoutExpired:
        return 124, "", f"[超时] {' '.join(cmd)}"
    except OSError as e:
        return 127, "", f"[无法执行] {e}"


def show(path, lines=25, title=None):
    if title:
        print(f"\n----- {title} -----")
    if not os.path.isfile(path):
        print(f"  （文件不存在：{path}）")
        return
    with open(path, encoding="utf-8", errors="replace") as fh:
        content = fh.readlines()
    for line in content[:lines]:
        print("  " + line.rstrip("\n"))
    if len(content) > lines:
        print(f"  ... （共 {len(content)} 行，此处只显示前 {lines} 行）")


def main():
    dry = "--dry-run" in sys.argv
    keep = ("--keep" in sys.argv) or ("--no-clean" in sys.argv)
    n_samples = None
    if "--samples" in sys.argv:
        try:
            n_samples = int(sys.argv[sys.argv.index("--samples") + 1])
        except (IndexError, ValueError):
            print("[错误] --samples 需要一个整数，如 --samples 3")
            return 1

    print("=" * 60)
    print("星忆 · Demo（虚构用户：小明）— 真·端到端演示")
    print("=" * 60)

    diaries = list_diaries()
    if n_samples:
        diaries = diaries[:n_samples]
    print(f"\n[输入] {len(diaries)} 篇虚构日记（demo/user/）")
    for f in diaries:
        print(f"  - {f}")

    print("\n[流程]")
    print("  1. 建临时沙箱，复制日记 → 沙箱 daily/（不碰真实记忆）")
    print("  2. 沙箱专属 config.json")
    print("  3. compiler/extract.py        日记 → Claim")
    print("  4. compiler/sleep_purify.py --mode observe   Claim → memory-inbox.md")
    print("  5. 展示产出")

    if dry:
        print("\n[--dry-run] 仅列步骤，未真跑。去掉 --dry-run 即执行。")
        return 0

    extract = os.path.join(REPO, "compiler", "extract.py")
    purify = os.path.join(REPO, "compiler", "sleep_purify.py")
    for p in (extract, purify):
        if not os.path.isfile(p):
            print(f"[错误] 找不到 {p}")
            return 1

    sandbox = tempfile.mkdtemp(prefix="stellamem-demo-")
    mem = os.path.join(sandbox, "memories")
    ok_count = 0
    fail_count = 0

    try:
        # 1) 骨架 + 日记
        for sub in SUBDIRS:
            os.makedirs(os.path.join(mem, sub), exist_ok=True)
        for f in diaries:
            shutil.copyfile(os.path.join(HERE, "user", f),
                            os.path.join(mem, "daily", f))
        print(f"\n[1/5] 沙箱就绪：{mem}")

        # 2) 沙箱 config
        cfg_path, server_url = make_sandbox_config(mem)
        print(f"[2/5] 沙箱 config.json：{cfg_path}")
        print(f"      模型服务：{server_url}")

        env = dict(os.environ)
        env["STELLAMEM_CONFIG"] = cfg_path
        env["PYTHONIOENCODING"] = "utf-8"

        # 3) extract 逐篇
        print(f"\n[3/5] extract.py 逐篇编译（{len(diaries)} 篇）...")
        claim_dir = os.path.join(sandbox, "claims")
        os.makedirs(claim_dir, exist_ok=True)
        for f in diaries:
            src = os.path.join(mem, "daily", f)
            out = os.path.join(claim_dir, f.replace(".md", ".claims.json"))
            code, stdout, stderr = run(
                [sys.executable, extract, src, "--out", out], env, timeout=600)
            tail = (stderr or "").strip().splitlines()
            if code == 0 and os.path.isfile(out):
                try:
                    with open(out, encoding="utf-8") as fh:
                        n = len(json.load(fh))
                except (json.JSONDecodeError, OSError):
                    n = -1
                print(f"  [OK]   {f} → {n} 条 Claim")
                ok_count += 1
            elif code == 2:
                print(f"  [跳过] {f} — 连不上模型服务（{server_url}）")
                print("         先启动模型服务再复跑，见 docs/QUICKSTART.md")
                fail_count += 1
                break
            else:
                print(f"  [失败] {f} — exit={code}")
                for line in tail[:4]:
                    print(f"         {line}")
                fail_count += 1

        # 4) sleep_purify observe
        print("\n[4/5] sleep_purify.py --mode observe ...")
        code, stdout, stderr = run(
            [sys.executable, purify, "--mode", "observe", "--force"], env, timeout=900)
        for line in (stdout or "").strip().splitlines():
            print("  " + line)
        if code != 0:
            for line in (stderr or "").strip().splitlines()[:6]:
                print("  " + line)

        # 5) 产出
        print("\n[5/5] 产出（沙箱内）")
        inbox = os.path.join(mem, "system", "memory-inbox.md")
        show(inbox, 25, "memory-inbox.md 前 25 行")
        fw = os.path.join(mem, "system", "false-write-log.md")
        if os.path.isfile(fw):
            show(fw, 10, "false-write-log.md 前 10 行")

        print("\n生成的文件树：")
        for dp, dn, fn in os.walk(mem):
            dn[:] = [d for d in dn if d != "__pycache__"]
            for f in sorted(fn):
                rel = os.path.relpath(os.path.join(dp, f), mem)
                size = os.path.getsize(os.path.join(dp, f))
                print(f"  - {rel}  ({size} B)")

        print(f"\n统计：extract 成功 {ok_count} 篇，失败/跳过 {fail_count} 篇")
        if fail_count == 0:
            print("\n完成。全流程跑通，未碰真实记忆。")
        else:
            print("\n流程跑通但有中断（多半是模型服务没起）。沙箱已保留供检查。")
        print(f"沙箱路径：{mem}")
    finally:
        if not keep and fail_count == 0:
            shutil.rmtree(sandbox, ignore_errors=True)
            print("（沙箱已清理，加 --keep 可保留检查）")
        else:
            print("（沙箱保留，检查完可手动删除该临时目录）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
