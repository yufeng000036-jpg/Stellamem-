# INSTALL.md —给 AI 读的安装指令（AI-Executable Install Guide）

> **这份文档是写给「AI 助手」读的，不是写给人读的。**
> 如果你是 AI，请按顺序执行下面的步骤，把这个记忆框架装到你自己的运行环境上。
> 如果你是人，把这份文件 + 整个仓库丢给你的 AI，然后说：「照 INSTALL.md 把它装到我身上」。

---

## 0. 你（AI）要先做的三件事

1. **确认你的宿主环境**。本框架的第一公民宿主是 **OpenClaw**（有 hooks / plugins / agent workspace 的环境）。
   - 如果是 OpenClaw → 继续执行全部步骤。
   - 如果是其他框架（Claude Code / Cursor / 自研 agent）→ 执行第 6 节「非 OpenClaw 适配」。
2. **盘点本机已有资源，不要先下载**。检查是否已有：Python 3.10+、Node 18+、llama.cpp（或 ollama / LM Studio）、任意 4B 级本地模型。
3. **不要修改用户已有文件内容**。本安装只做「新建 / 生成 / 追加」，绝不覆盖用户已有记忆。

---

## 1. 环境自检（先跑这个）

```bash
python setup.py check
```

`setup.py` 会输出一份环境报告：Python 版本、Node 版本、探测到的 OpenClaw 目录、探测到的模型服务、已存在的记忆目录。
**看它的「修复建议」段落，逐条照做后再继续。**

---

## 2. 两条安装路径（先选一条）

| 路径 | 适合谁 | 装什么 | 能得到什么 |
|------|--------|--------|-----------|
| **A. 只装 Compiler** | 非 OpenClaw 用户（Claude Code / Cursor / 自研 Agent） | `compiler/` + `templates/` + `config.json` | 日记 → Claim → markdown 记忆，完整的编译侧能力 |
| **B. Compiler + Adapter** | OpenClaw 用户 | 上者 + `hooks/`（自动日记）+ `adapters/openclaw/`（自动注入） | 全自动闭环：对话自动落盘、编译、注入回上下文 |

> Compiler（核心）**完全不依赖 OpenClaw**，两条路径都能跑 `extract.py` → `sleep_purify.py` → 生成 markdown。
> 区别只在「日记怎么来」和「记忆怎么回注」——这两个恰好是 OpenClaw 专用的，见第 6 节自己实现。

---

## 2b. 路径 B：一键安装（OpenClaw 用户，推荐）

```bash
python setup.py install --yes --ai-name <AI名字> --mem-root <记忆根目录> --merge-openclaw
```

参数说明：
- `--ai-name`：AI 名字（日记以谁的第一人称写），如 `小助手`
- `--mem-root`：记忆根目录（绝对路径），如 `D:/my-memory`；不填则用默认 `~/.stellamem`
- `--model-url`：OpenAI 兼容模型服务地址，如 `http://127.0.0.1:11434`（不填则自动探测 8081/1234/11434）
- `--merge-openclaw`：自动备份并合并 `openclaw.json`（**只追加 keys，不覆盖已有字段**；冲突字段保留你的原值并写入 `setup-out/openclaw.merge-conflicts.md`）
- `--yes`：跳过交互确认

### 路径 A：只装 Compiler（非 OpenClaw 用户）

不需要跑 `setup.py install`（它主要为 OpenClaw 铺 hook/adapter）。手工三步：

```bash
# 1. 配好 config.json（放在仓库根目录，或由 STELLAMEM_CONFIG 环境变量指定）
cp config.example.json config.json   # 然后编辑：memories_root / server_url

# 2. 建记忆目录骨架
mkdir -p <memories_root>/{core,long-term,semantic,system,daily}
cp -r templates/* <memories_root>/    # 空模板

# 3. 启动模型服务后，直接跑编译
python compiler/extract.py <日记文件>            # 单篇 → Claim JSON
python compiler/sleep_purify.py --mode observe   # 全量 → inbox（安全，不写正式记忆）
```

写入侧（日记怎么来）和注入侧（记忆怎么回注）需自己实现，参考第 6 节。

`setup.py install` 会**自动完成以下全部动作**（幂等，重复跑安全）：

| # | 动作 | 产出 |
|---|------|------|
| 1 | 探测 OpenClaw 状态目录 | 定位 `~/.openclaw/` |
| 2 | 探测 sessions 目录 | 定位 `agents/main/sessions`（优先默认 agent） |
| 3 | 生成记忆根目录 + `config.json` | 记忆路径、模型名、llama_bin |
| 4 | 创建记忆目录骨架 | `core/ long-term/ semantic/ episodic/ system/ working/ daily/` |
| 5 | 拷贝模板 | 从 `templates/` 生成空记忆文件（不覆盖已有） |
| 6 | 安装 hook | 拷贝 `hooks/daily-autolog/` 到 `~/.openclaw/hooks/`，并改**副本**的 `AI_NAME`/`SESSIONS_DIR`/`DAILY_DIR` |
| 7 | 安装 adapter | 拷贝 `adapters/openclaw/` 到 OpenClaw extensions 目录，并改**副本**的 `ROOT` |
| 8 | 合并配置 | `--merge-openclaw` 时自动备份 + 合并 `openclaw.json`；否则生成 `setup-out/openclaw.snippet.json` |
| 9 | 自检 | 跑一遍 `python compiler/memory.py doctor` |

> ⚠️ **重要**：安装器**只改拷贝到目标位置的副本，绝不改写仓库源文件**。源文件始终保持模板状态（占位符），可重复分发、重复安装。
> ⚠️ **config.json 位置**：统一放在**仓库根目录**（`STELLAMEM_CONFIG` 环境变量可覆盖）。`compiler/config_loader.py` 按此顺序查找：环境变量 → 仓库根 → compiler/ 旧位置（兼容）。

---

## 3. 需要人（用户）确认的两处

装完 setup 后，**只需用户确认两件事**再重启：

1. **模型服务**：`python compiler/start_server.py` 需要 llama.cpp + 一个 gguf 模型。见第 4 节。
   > 如果你用的是 Ollama / LM Studio（不走 start_server.py），则这一步也不用额外配置。
2. **重启 OpenClaw**，使 hook 和 plugin 生效。

> 💡 `openclaw.json` 的合并已由 `--merge-openclaw` 自动完成（自动备份 + 只追加 keys）。
> 如果没加这个参数，install 会在 `setup-out/openclaw.snippet.json` 生成片段，由你（AI）在用户确认后合并——合并前先备份，逐条确认，不要整文件覆盖。

---

## 4. 模型服务（编译侧必需）

编译（把日记变成结构化记忆）需要**一个本地模型**。三选一：

### 方案 A：llama.cpp（本框架默认）
```bash
# 1. 拿到 llama.cpp 的 llama-server 可执行文件
# 2. 下载一个 4B 级模型（推荐 Qwen3-4B 的 GGUF 量化版，Q4_K_M 约 2.5GB）
# 3. 编辑 config.json：
#    - model_name 指向 gguf 路径
#    - llama_bin 指向 llama-server 可执行文件（留空则自动从 PATH 探测）
python compiler/start_server.py
```

### 方案 B：Ollama（最省事，推荐给新手）
```bash
ollama pull qwen3:4b
ollama serve        # 默认监听 127.0.0.1:11434
```
然后把 `config.json` 的 `server_url` 改成 `http://127.0.0.1:11434`。
> ⚠️ Ollama 的 OpenAI 兼容层路径是 `/v1/chat/completions`，本框架默认已按此拼接，通常无需改代码。

### 方案 C：LM Studio
启动 LM Studio 的 Local Server（默认 `http://127.0.0.1:1234/v1`），改 `server_url` 即可。

**模型选择建议**：
- 首选 **Qwen3-4B**（中文强、结构化输出稳）
- 备选 Qwen2.5-7B / Gemma-3-4B
- 不要用低于 3B 的模型，结构化 JSON 输出会崩

---

## 5. 验证安装（必须全绿才算成功）

```bash
# 5.1 记忆系统体检
python compiler/memory.py doctor

# 5.2 注入侧验证：重启 OpenClaw 后，问你的 AI：
#     「你记得我的偏好吗？」
#     它应该能说出 core/preferences.md 里的内容

# 5.3 写入侧验证：在 OpenClaw 里发一次 /new，然后检查：
#     <记忆根>/daily/<今天日期>.md 是否被自动写出

# 5.4 编译侧验证：跑一次
python compiler/sleep_purify.py --mode observe
#     observe 模式只提取 + 写 inbox，绝不写正式记忆，安全
```

四项全过 = 安装成功。

---

## 6. 非 OpenClaw 适配（Claude Code / Cursor / 自研 Agent）

本框架的核心（`compiler/` 和记忆 schema）是**框架无关的**，只有两个组件依赖 OpenClaw：
- `hooks/daily-autolog/handler.js`（写入侧）
- `adapters/openclaw/index.js`（注入侧）

**替换方案**：

| 组件 | 你要做的 |
|------|---------|
| 写入侧 | 自己写一个「对话结束 → 落盘 daily」的钩子。核心是把对话按 `[HH:MM] role: content` 格式写成 `daily/YYYY-MM-DD.md`。 |
| 注入侧 | 在你的 system prompt 构建处，读 `core/identity.md` + `core/user-core.md` + `core/preferences.md` 拼进去；再按关键词命中读 `long-term/` 和 `semantic/`。可参考 `adapters/openclaw/index.js` 的逻辑，只有 30 行。 |
| 编译侧 | 完全不用改，改 `config.json` 的路径即可。 |

---

## 7. 常见坑（实测踩过的，AI 请逐条对照）

1. **hook 事件名用冒号**：`command:new` / `command:reset` / `gateway:startup`。写成下划线 `gateway_start` 永远不触发。
2. **hook 放 `~/.openclaw/hooks/`，不是 `extensions/`**。放错目录静默失效。
3. **必须开总开关**：`hooks.internal.enabled = true`，没有这行连内置 hook 都不加载。
4. **归档文件读取**：`/new` 后旧 session 改名 `xxx.jsonl.reset.<时间戳>`，读会话必须用 `includes(".jsonl")` 而非 `endsWith(".jsonl")`，否则漏读历史。
5. **`config_loader` 找不到 config.json 会直接退出**：先把 `config.example.json` 拷成**仓库根目录**的 `config.json` 填好，再跑 compiler。也可用环境变量 `STELLAMEM_CONFIG` 指向任意位置的配置文件。
6. **模型端口两处配置**：`config.json` 的 `server_url` 和 `handler.js` 里的 `MODEL_URL` 是两套，改一处不够。
7. **Windows 编码**：脚本已避免 emoji（GBK 控制台会崩）。自己加输出时也注意。
8. **`memory.py rollback` 默认是干跑**：必须加 `--yes` 才真恢复。

---

## 8. 装完之后：让 AI 真正「用上」这套框架

安装只是开始。要让框架活起来，需要三步循环：

```
① 写入：AI 每天和你聊完 → daily-autolog 自动落盘日记
② 编译：定期跑 sleep_purify.py → 从日记提炼出偏好/决策/教训/项目
③ 注入：每次对话开始 → adapter 把 core/ 记忆喂回 AI 上下文
```

**建议的日常节奏**：
- **每轮对话结束**：跑 `python compiler/sleep_purify.py`（review 模式）
- **每周一次**：整理 `long-term/` 和 `semantic/`，去重合并
- **发现冲突时**：写入 `system/conflict-log.md`，等用户裁决

---

## 9. 给 AI 的最后一段话

> 这套框架的本质是：**把 AI 的记忆从「模型内部的模糊权重」变成「磁盘上的可审计 markdown 文件」**。
> 装上它之后，你的记忆会像代码一样：可 diff、可 review、可回滚、可版本化。
>
> 但请记住三条铁律：
> 1. **不删除任何原始文件**，只做「新增 + 标注」。
> 2. **不覆盖旧记忆**，冲突时两处都保留、记 conflict-log。
> 3. **不写入任何 API Key / 密码 / 密钥**到记忆文件。
>
> 拿不准就两处都放，不要丢信息。
