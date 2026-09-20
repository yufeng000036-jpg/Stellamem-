// Stellamem Adapter — index.js（A+B 混合注入）
// 每轮注入 core/ 三文件 + 精简索引；命中关键词时额外注入对应档案全文。
// 实测确认的 OpenClaw 格式：export default { register(api) { api.on("before_prompt_build", ...) } }

import { readFile } from "node:fs/promises";

const ROOT = "<YOUR_MEMORIES_PATH>";
const CORE = ROOT + "/core";

// 精简索引（硬编码，各档案一行，让 AI 有全局观）
const INDEX_TEXT = [
  "- 项目：进行中的项目状态",
  "- 决策：关键决策、方向选择",
  "- 教训：踩坑经验（弹窗、路径坑、编码坑等）",
  "- 画像：用户基本信息/人格/依恋",
  "- 数据画像：聊天数据规模/风格",
  "- 收藏：收藏分类",
  "- 技术档案：技术文档索引（工作流/拆解/工具链）",
].join("\n");

// 关键词映射（命中才读全文）
const KEYWORD_MAP = {
  "项目|进展|开发|在做|完成|active": ["long-term/projects.md"],
  "决策|决定|选了|版本|迁移|阈值": ["long-term/decisions.md"],
  "教训|踩坑|报错|错误|避免|以后别|经验": ["long-term/lessons.md"],
  "用户|我是谁|关于我|了解我|人格|依恋|关系|身体": ["semantic/profile.md"],
  "聊天数据|消息|画像数据": ["semantic/data-profile.md"],
  "收藏|存档": ["semantic/favorites.md"],
  "技术|工作流|拆解|工具链|插件": ["semantic/tech-index.md"],
};

const plugin = {
  id: "stellamem-adapter",
  name: "Stellamem Adapter",
  description: "把 core/ 记忆 + 索引 + 关键词命中档案 结构性注入 AI 上下文",
  register(api) {
    api.on(
      "before_prompt_build",
      async (event, ctx) => {
        try {
          // 1) core 三文件（常驻）
          const identity = await readFile(CORE + "/identity.md", "utf8");
          const userCore = await readFile(CORE + "/user-core.md", "utf8");
          const prefs = await readFile(CORE + "/preferences.md", "utf8");

          // 2) 关键词触发（读用户消息，命中才读对应档案）
          const userMsg = (event && event.prompt) || "";
          const extra = [];
          for (const [pattern, files] of Object.entries(KEYWORD_MAP)) {
            if (new RegExp(pattern).test(userMsg)) {
              for (const f of files) {
                try {
                  extra.push(await readFile(ROOT + "/" + f, "utf8"));
                } catch (e) {
                  // 单个档案读失败就跳过，不影响整体
                }
              }
            }
          }

          return {
            prependSystemContext: identity,
            prependContext: [
              userCore,
              prefs,
              "--- 记忆索引 ---",
              INDEX_TEXT,
              extra.length ? "--- 相关档案 ---\n" + extra.join("\n\n") : "",
            ]
              .filter(Boolean)
              .join("\n\n"),
          };
        } catch (e) {
          return {}; // 任何失败返回空，绝不阻塞 prompt 构建
        }
      },
      { timeoutMs: 3000 }
    );
  },
};

export default plugin;
