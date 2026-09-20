# 快速开始（Quickstart）

## 1. 环境准备

- Python 3.10+
- 本地模型服务（llama.cpp 等，用于编译日记的 Claim）
- 记忆根目录（如 `~/memories`）

## 2. 配置

```bash
cp config.example.json config.json
# 编辑 config.json，填你的路径和模型名
```

## 3. 建记忆结构

参考 `templates/`，建：

```
<你的记忆根>/
├── core/          identity.md / user-core.md / preferences.md
├── long-term/     projects.md / decisions.md / lessons.md
├── semantic/      profile.md 等
└── daily/         YYYY-MM-DD.md 日记
```

## 4. 启动模型服务

```bash
# 例：llama.cpp
llama-server -m <你的模型> --port 8081
```

## 5. 编译日记

```bash
python compiler/extract.py   # 日记 → Claim
python compiler/sleep_purify.py --mode review  # Claim → 记忆文件
```

## 6. 接 AI 框架（adapter）

以 OpenClaw 为例，见 `adapters/openclaw/`：
- 把 adapter 复制到 OpenClaw 的 extensions 目录
- 改 `index.js` 里的 `<YOUR_MEMORIES_PATH>` 为你的记忆根
- 重启 OpenClaw

## 7. 验证

问 AI：「你记得我之前说过什么偏好吗？」——它应该能答出你写进 core/preferences.md 的内容。
