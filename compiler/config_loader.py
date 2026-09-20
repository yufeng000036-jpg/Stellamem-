#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
config_loader.py —— 读取同目录 config.json，提供统一配置入口。

用法：
  from config_loader import load_config
  cfg = load_config()
  root = cfg["memories_root"]
"""
import json, os, sys

def load_config():
    """读同目录 config.json，返回 dict。路径不存在或解析失败 → 明确报错、非零退出。"""
    cfg_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")
    if not os.path.exists(cfg_path):
        print(f"[错误] 配置文件不存在：{cfg_path}")
        sys.exit(1)
    try:
        with open(cfg_path, encoding="utf-8") as fh:
            return json.load(fh)
    except json.JSONDecodeError as e:
        print(f"[错误] config.json 解析失败：{e}")
        sys.exit(1)

if __name__ == "__main__":
    cfg = load_config()
    print("config 读取成功，字段：")
    for k, v in cfg.items():
        print(f"  {k} = {v}")
