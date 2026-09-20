---
name: daily-autolog
description: "Automatically summarize the day's conversations into daily diaries when /new or /reset is issued, and backfill yesterday's diary on gateway startup"
homepage: https://docs.openclaw.ai/automation/hooks
metadata:
  {
    "openclaw":
      {
        "emoji": "📓",
        "events": ["command:new", "command:reset", "gateway:startup"],
        "install": [{ "id": "local", "kind": "managed", "label": "Local managed hook" }],
      },
  }
---

# Daily Autolog Hook（自动日记）

自动把会话总结成 `daily/YYYY-MM-DD.md` 日记。**这是「写入侧」——没有它，AI 的对话不会自动进入记忆系统。**

## What It Does

- **A（写今天）**：`/new` 或 `/reset` 时，把今天所有会话消息总结成第一人称日记，写入 `daily/YYYY-MM-DD.md`。
- **C（补昨天）**：网关启动（`gateway:startup`）时，检查昨天日记是否缺失，缺失则补写。
- **幂等**：每条日记带 `[HH:MM]` 时间戳，只写时间晚于文件已覆盖最后时间的新会话，已覆盖则跳过。
- **降级**：本地模型总结失败时，降级为原始转录，保证不漏写。

## 安装（3 个地方要改）

编辑 `handler.js` 顶部的常量：

1. `AI_NAME` —— 改成你自己的 AI 名字（日记以谁的第一人称写）
2. `SESSIONS_DIR` —— 改成你 OpenClaw 的会话目录（如 `C:/Users/你/.openclaw/agents/main/sessions`）
3. `DAILY_DIR` —— 改成你记忆根目录下的 daily 子目录（如 `C:/Users/你/<你的记忆根>/daily`）

然后把整个 `daily-autolog/` 目录复制到 OpenClaw 的 hooks 目录（`~/.openclaw/hooks/`），并在 `openclaw.json` 里启用：

```json
{
  "hooks": {
    "internal": {
      "enabled": true,
      "entries": {
        "daily-autolog": { "enabled": true }
      }
    }
  }
}
```

重启 OpenClaw 即可生效。

## Output Format

```markdown
# 2026-09-20 日记

[14:32] 我和用户讨论了星忆的配置化收口……
```

每条以 `[HH:MM]` 开头（不加日期），时间按升序。

## Requirements

- 本地模型服务需运行在 `http://127.0.0.1:8081/v1/chat/completions`（llama.cpp 等），否则降级为原始转录。
- 会话数据目录即 `SESSIONS_DIR`。

## 注意

- **事件名用冒号格式**：`command:new` / `command:reset` / `gateway:startup`（不是下划线 `gateway_start`）。
- **归档文件**：`/new` 或 `/reset` 后 OpenClaw 会把旧 session 重命名为 `xxx.jsonl.reset.<时间戳>`，历史消息都在归档里，读取时必须用 `includes(".jsonl")` 而非 `endsWith(".jsonl")`，否则漏读。
