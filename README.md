# GTM Friends — AI 同事技能索引

`#gtm_friends` 频道里各 AI 同事的 skill 汇总。每个 skill 文件记录该同事的角色、能力、自动化任务与首次配置引导。

> 口径：本索引按仓库实际文件如实标注；**未成文/未成可安装格式的会明确标出**，不假装齐全。

## 技能一览

| AI 同事 | 角色（一句话） | Skill 文件 | 可直接安装 |
|---|---|---|---|
| **Gatlin Verifier** (@gatlin) | 增长数据 & GTM 分析：真实 DAU/活跃口径、用户场景、渠道归因、异动检测、发布前核验 | [gatlin/SKILL.md](./gatlin/SKILL.md) · [gatlin.md](./gatlin.md) | ✅ 是 |
| **SEO Genius** (@seogenius-2) | SEO/GEO：关键词策略、页面 SEO、内容缺口、自然增长、SEO 发布把关 | [seo-genius.md](./seo-genius.md) | ⚠️ 待转格式 |
| **Day Planner** (@dayplanner-2) | 日程规划：把优先级/会议/跟进变成能过的一天，保护注意力、让时间可见 | [day-planner.md](./day-planner.md) | ⚠️ 待转格式 |
| **Email Genius** (@emailgenius-2) | 邮件自动化：巡检 Gmail、分诊、起草英文回复、批量触达、发票跟踪、导入 Notion | ⏳ 未入库 | ❌ 缺 |
| **User Guardian** (@userguardian) | 会议纪要 / 用户访谈整理 / 产品反馈录入 + 首次配置引导（meeting-notes） | [userguardian.md](./userguardian.md) | ⚠️ 待转格式 |
| **Official Account Assistant** (@officialaccountassistant) | 写作 / 公众号 / 社媒文案 | ⏳ 未入库 | ❌ 缺 |
| **Trace** (@trace) | 工程 / 产品把关 | ⏳ 未入库 | ❌ 缺 |

## 安装说明

Helio 安装 skill 需要仓库里有名为 **`SKILL.md`** 的文件（带 YAML frontmatter：`name` + `description`）。

- **可直接安装**（已是 `SKILL.md` 格式）：
  - Gatlin：`heliox skill install https://github.com/YoriHan/AI-Colleague-SKILL/tree/main/gatlin`
- **⚠️ 待转格式**：`seo-genius.md` / `day-planner.md` / `userguardian.md` 内容已成文，但还不是可安装的 `SKILL.md` 格式（`userguardian.md` 已有 frontmatter，只差改成 `<名字>/SKILL.md` 的目录结构）。转好即可安装。
- **❌ 缺**：Email Genius / OAA / Trace 尚未把 skill 写入本仓库。

## 现状小结（2026-07-07）

- 7 个 GTM AI 同事中，**4 个已有 skill 文件**（Gatlin / SEO Genius / Day Planner / User Guardian），**3 个未入库**（Email Genius / OAA / Trace）。
- **仅 Gatlin 一个是可直接安装的格式**；其余 3 个成文的待转成 `<名字>/SKILL.md`。
- 下一步：补齐未入库的 3 个 + 把成文的 3 个转成可安装格式，让每个都能一键装。
