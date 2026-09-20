#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""run_demo.py —— 星忆一键演示

流程：demo/user/ 的 7 天虚构日记 → 编译成 Claim → 路由到记忆文件。

前置：
  1. 配置 config.example.json → config.json（填你的路径）
  2. 启动模型服务（见 docs/ 快速开始）

用法：
  python run_demo.py          # 演示模式：打印流程 + 预期产出
"""
import os

ROOT = os.path.dirname(os.path.abspath(__file__))

def main():
    print("=" * 50)
    print("星忆 · Demo（虚构用户：小明）")
    print("=" * 50)
    user_dir = os.path.join(ROOT, "user")
    diaries = sorted(f for f in os.listdir(user_dir) if f.endswith(".md"))
    print(f"\n输入：{len(diaries)} 篇虚构日记")
    for f in diaries:
        print(f"  - {f}")
    print("\n流程：")
    print("  1. extract.py 编译日记 -> Claim（kind/subject/predicate/value）")
    print("  2. sleep_purify.py 路由 Claim -> core/long-term/semantic")
    print("  3. adapter 注入 core/ 到 AI 上下文")
    print("\n预期产出（模拟）：")
    print("  core/preferences.md   <- 偏好（喜欢猫、路径用引号）")
    print("  long-term/projects.md <- 项目（bookmarks-cleaner）")
    print("  long-term/lessons.md  <- 教训（先写测试再重构）")
    print("\n真实运行：请先配置好模型服务，再手动跑 compiler/ 下的脚本。")
    print("（本 demo 是说明性脚本，不依赖模型。）")

if __name__ == "__main__":
    main()
