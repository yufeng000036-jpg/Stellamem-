#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
config_loader.py —— 统一配置入口。

查找顺序（第一个存在的即被使用）：
  1. 环境变量 STELLAMEM_CONFIG 指向的文件（有则优先，不存在则报错）
  2. 仓库根目录 config.json（compiler/ 的上一级）
  3. 兼容回退：compiler/ 同目录 config.json（旧布局，仅当根目录没有时）

用法：
  from config_loader import load_config
  cfg = load_config()
  root = cfg["memories_root"]
"""
import json, os, sys

# compiler/ 的上一级 = 仓库根目录
_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_REPO_ROOT = os.path.dirname(_THIS_DIR)


def resolve_config_path():
    """按优先级返回 config.json 路径；找不到返回 None。"""
    env = os.environ.get("STELLAMEM_CONFIG")
    if env:
        # 环境变量显式指定 → 不静默回退，让用户知道路径写错了
        return env if os.path.isfile(env) else env
    root_cfg = os.path.join(_REPO_ROOT, "config.json")
    if os.path.isfile(root_cfg):
        return root_cfg
    legacy_cfg = os.path.join(_THIS_DIR, "config.json")
    if os.path.isfile(legacy_cfg):
        return legacy_cfg
    return root_cfg  # 报错时展示首选位置


def load_config():
    """读取 config.json，返回 dict。路径不存在或解析失败 → 明确报错、非零退出。"""
    cfg_path = resolve_config_path()
    if not os.path.exists(cfg_path):
        print(f"[错误] 配置文件不存在：{cfg_path}")
        env = os.environ.get("STELLAMEM_CONFIG")
        if env:
            print("       （来自环境变量 STELLAMEM_CONFIG，请检查该路径）")
        else:
            print("       请把 config.example.json 复制为仓库根目录的 config.json，")
            print(f"       或设置环境变量 STELLAMEM_CONFIG 指向你的配置文件。")
        sys.exit(1)
    try:
        # encoding="utf-8-sig" 兼容带 BOM 的 config.json（Windows 记事本/PowerShell 常见）
        with open(cfg_path, encoding="utf-8-sig") as fh:
            return json.load(fh)
    except json.JSONDecodeError as e:
        print(f"[错误] config.json 解析失败：{e}")
        print(f"       文件：{cfg_path}")
        sys.exit(1)


if __name__ == "__main__":
    cfg = load_config()
    print(f"config 读取成功：{resolve_config_path()}")
    print("字段：")
    for k, v in cfg.items():
        print(f"  {k} = {v}")
