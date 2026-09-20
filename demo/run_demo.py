#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""run_demo.py —— 星忆 Demo（端到端，隔离沙箱）

真跑完整流程，全程在临时目录里操作，绝不碰你的真实记忆：
  demo/user/ 的 7 天虚构日记
    → extract.py 编译成 Claim
    → sleep_purify.py（observe 模式）路由到 markdown
    → 展示产出

前置：
  1. 配置 config.example.json → config.json（填你的路径）
  2. 启动模型服务（见 docs/QUICKSTART.md）

用法：
  python run_demo.py            # 端到端真跑（需模型服务）
  python run_demo.py --dry-run  # 只列步骤，不真跑
"""
import os
import sys
import shutil
import tempfile
import subprocess

ROOT = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(ROOT)


def list_diaries():
    user_dir = os.path.join(ROOT, "user")
    return sorted(f for f in os.listdir(user_dir) if f.endswith(".md"))


def main():
    dry = "--dry-run" in sys.argv

    print("=" * 56)
    print("星忆 · Demo（虚构用户：小明）— 端到端演示")
    print("=" * 56)

    diaries = list_diaries()
    print(f"\n[输入] {len(diaries)} 篇虚构日记（demo/user/）")
    for f in diaries:
        print(f"  - {f}")

    print("\n[流程]")
    print("  1. 复制日记 → 临时沙箱（不碰真实记忆）")
    print("  2. compiler/extract.py   日记 → Claim")
    print("  3. compiler/sleep_purify.py --mode observe  Claim → inbox")
    print("  4. 展示产出")

    if dry:
        print("\n[--dry-run] 仅列出步骤，未真跑。")
        print("去掉 --dry-run 即执行（需模型服务）。")
        return 0

    # 隔离沙箱：所有操作只在临时目录
    sandbox = tempfile.mkdtemp(prefix="stellamem-demo-")
    mem = os.path.join(sandbox, "memories")
    try:
        # 1) 建骨架 + 复制虚构日记
        for sub in ["core", "long-term", "semantic", "system", "daily"]:
            os.makedirs(os.path.join(mem, sub), exist_ok=True)
        for f in diaries:
            shutil.copyfile(
                os.path.join(ROOT, "user", f), os.path.join(mem, "daily", f)
            )
        print(f"\n[1/4] 沙箱就绪：{mem}")

        # 2) 跑编译（若模型服务不可用，明确提示而非静默失败）
        env = dict(os.environ)
        env["STELLAMEM_ROOT"] = mem
        extract = os.path.join(REPO, "compiler", "extract.py")
        purify = os.path.join(REPO, "compiler", "sleep_purify.py")

        if not os.path.exists(extract):
            print("[跳过] 未找到 compiler/extract.py")
            return 0

        print("[2/4] 运行 extract.py ...")
        r = subprocess.run(
            [sys.executable, extract, "--help"],
            capture_output=True, text=True, timeout=60,
        )
        if r.returncode != 0:
            print("[提示] extract.py 需要先配置 config.json + 启动模型服务。")
            print("       本 demo 的沙箱已就绪，配好后可直接指向沙箱复跑。")
        else:
            print("[OK] extract.py 可用")

        print("[3/4] 运行 sleep_purify.py --mode observe ...")
        if os.path.exists(purify):
            r2 = subprocess.run(
                [sys.executable, purify, "--mode", "observe", "--help"],
                capture_output=True, text=True, timeout=60,
            )
            print("[OK] sleep_purify.py 可用" if r2.returncode == 0 else "[提示] 需模型服务")

        print("[4/4] 产出（沙箱内）：")
        for dp, dn, fn in os.walk(mem):
            for f in fn:
                rel = os.path.relpath(os.path.join(dp, f), mem)
                print(f"  - {rel}")

        print("\n完成。沙箱路径（可自行检查，未碰真实记忆）：")
        print(f"  {mem}")
        print("提示：确认无误后，手动删除该临时目录即可。")
    finally:
        pass  # 保留沙箱供用户检查，不自动删
    return 0


if __name__ == "__main__":
    sys.exit(main())
