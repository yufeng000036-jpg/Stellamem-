# Roadmap（规划）

> 本文件只列**尚未实现**的能力。README 只写已经跑通的能力，这里列规划，避免混淆「已支持」和「计划支持」。
>
> 优先级：`P0` 近期核心 · `P1` 重要增强 · `P2` 远期 / 待评估。

---

## 安全与治理（优先）

| 项 | 优先级 | 说明 |
|---|---|---|
| 自动关系裁决接入主流程 | P0 | 把 `judge.py`（8 种关系判断）接入 `sleep_purify.py`，让 REFINES / SUPERSEDES / CONTRADICTS 自动落冲突日志与版本链 |
| 密钥自动识别与脱敏 | P0 | 确定性识别 API Key / Token / 密码等，拦截写入或替换为 `secret_ref` 引用 |
| 敏感数据分级 | P1 | `public / private / sensitive / secret` 四级，并区分 storage policy 与 injection policy（`always / recall / confirm / never`） |
| Context Projection | P1 | Adapter 按任务做更严格的读取隔离，只注入相关记忆 |
| 第三方 Adapter 签名校验 | P2 | 安装前校验 Adapter 来源可信度 |

---

## 框架适配

| 项 | 优先级 | 说明 |
|---|---|---|
| Claude Code Adapter | P1 | 计划支持 |
| Cursor Adapter | P2 | 计划支持 |
| 其他框架 Adapter | P2 | 欢迎社区贡献 |

---

## 体验与分发

| 项 | 优先级 | 说明 |
|---|---|---|
| 可复现 Benchmark 发布 | P1 | 公开 samples / golden / 结果与跑分脚本 |
| GUI | P2 | 图形界面（查看 / 确认 inbox / 回滚） |
| 多设备同步 | P2 | 待评估（当前本地优先，不强依赖） |
| 云端加密同步 | P2 | 待评估 |
| 自动 JSON-LD 导出 | P2 | 结构化互操作导出 |
| 自动 SBOM | P2 | 软件物料清单 |
| 自动签名发布 | P2 | 签名校验发布物 |

---

## 团队与企业（远期）

| 项 | 优先级 | 说明 |
|---|---|---|
| 团队记忆 | P2 | 多人共享记忆空间 |
| 企业权限 | P2 | 角色与访问控制 |

---

## 说明

- 本 Roadmap 会随开发进度更新；已完成的项会移入 [CHANGELOG.md](CHANGELOG.md)。
- 优先级可能调整，不构成承诺或发布保证。
