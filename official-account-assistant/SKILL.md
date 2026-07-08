---
name: helio-social-card
description: Full Helio social media publishing workflow — draft LinkedIn and Twitter copy with UTM links, generate a 1600x900 card image from approved Figma templates or PIL compositing, write to Notion, notify the owner for approval, and confirm publication. Also handles card-only requests and screenshot layout inspection. Use when asked to make a social post, generate a card, run today's social media content, or onboard into the social media workflow.
---

# Helio Social Media Workflow

Handles the full social media publishing cycle: copy → card → Notion → approval → publish.
Also handles card-only and screenshot-only requests.

---

## First Run: Setup Check

**Always run this block first.**

```bash
CONFIG="$HOME/.claude/skills/helio-social-card/config.json"
[ -f "$CONFIG" ] && python3 -c "
import json, sys
c = json.load(open('$CONFIG'))
print('READY' if c.get('setup_complete') else 'INCOMPLETE')
" || echo "NOT_FOUND"
```

- `READY` → skip to [Workflow](#workflow)
- `NOT_FOUND` or `INCOMPLETE` → run [references/setup-guide.md](references/setup-guide.md) before anything else

---

## Workflow

### Mode Detection

Determine what the user is asking for:

| Request | Mode |
|---------|------|
| "做今天的社媒" / "run social media" / "帮我发帖" | **Full workflow** |
| "做一张卡片" / "make a card" / "generate image" | **Card only** |
| "检查这张截图" / "inspect screenshot" | **Screenshot preflight only** |
| "重新配置" / "reset setup" | **Re-run setup** |

---

### Full Workflow

#### 1. Gather Inputs

Collect from user or context:

- **Theme / topic**: what today's post is about
- **Screenshot**: the product screenshot for the card (ask if not provided)
- **Approver**: from config (`approver_handle`), default `@yori`

If the user provides a rough brief, refine it using [references/copy-refinement.md](references/copy-refinement.md).

#### 2. Draft Copy

Draft for both platforms using the format below. Read UTM base URLs from config.

**LinkedIn format:**

```
[Hook — 3-7 words, direct]

[One sentence: the core problem your audience has]

[Product name]'s [feature] [does what]:
→ [action 1]
→ [action 2]
→ [action 3]
→ [action 4]

[One closing sentence: the value]

→ {website_url}?utm_source=linkedin&utm_medium=social&utm_campaign={campaign}
→ Community: {discord_url}
```

**Twitter format:**

```
[Hook — same as LinkedIn]
[One sentence: what the AI does]
[One sentence: what the user does]
→ {website_url}?utm_source=x&utm_medium=social&utm_campaign={campaign}
→ Community: {discord_url}
```

`{campaign}` = topic slug in lowercase underscore format (e.g. `posts_while_you_sleep`).

Use direct full URLs. Never use URL shorteners for official account posts.

#### 3. Generate Card

Run screenshot preflight, route to layout, then generate card. See [Card Generation](#card-generation) section.

#### 4. Write to Notion

Write to the 社媒素材库 database (ID from config) with:

- `Linkedin素材内容`: LinkedIn copy
- `Twitter素材内容`: Twitter copy (if database supports it; otherwise include in 备注)
- `配图`: card image URL
- `发布日期`: today's date (YYYY-MM-DD)
- `状态`: 审核中

#### 5. Notify for Approval

Send a DM to the approver handle from config with:

```
今天的社媒内容已准备好，请审核：

[LinkedIn 文案全文]

---

[Twitter 文案全文]

---

配图：[card image URL]

审核通过请回复"可以发送"。
```

#### 6. On Approval

When the approver replies with any approval signal ("可以发送" / "approve" / "ok" / "1"):

1. Attempt to publish via connected platform integrations (`heliox tool`). Twitter and LinkedIn posting **must** go through a Vault-authorized connection or `heliox tool` OAuth integration — never via manually shared access/refresh tokens. If the connection is not set up, produce draft copy only and tell the approver what still needs to be wired before direct posting is possible.
2. Reply: "已发送！" (if actually posted) or "草稿已准备好，请手动发布：[copy]" (if posting connection is not yet configured).
3. Update Notion record: `状态` → 完成

---

### Card Only

Skip copy drafting and Notion. Go directly to [Card Generation](#card-generation).

---

### Screenshot Preflight Only

Run:

```bash
python3 <skill-directory>/scripts/inspect_screenshot.py <input>
```

Report: resolution, aspect ratio, recommended layout, crop loss estimate per layout. Stop on `FAIL`. On `WARN`, disclose before continuing.

---

## Card Generation

### Screenshot Preflight

If a screenshot is provided, run `scripts/inspect_screenshot.py`. Use `recommended_screenshot_layout`. Accept layouts with ≤ 5% crop loss. Ask the user only if every layout removes more than 5% of important UI.

### Layout Routing

Read [references/layout-routing.md](references/layout-routing.md). Default to `Image / Hero Dark` for a short one-line headline with no subtitle.

### Generation Method

Read `card_method` from config.

#### Method A: Figma Plugin

1. Inspect live source node from [references/template-registry.md](references/template-registry.md)
2. Clone source frame into `Social / Production` area
3. Rename: `Social / YYYY-MM-DD / <short-title> / <theme> / <layout>`
4. Replace `Headline` text node
5. Replace screenshot image fill
6. Export as 1600×900 PNG
7. Upload to image host

**If plugin times out or disconnects**: switch to Method B for this run. Note the fallback in the delivery message.

#### Method B: PIL Compositing (fallback / default for new users)

1. Download template PNG from Figma MCP: node `17:7340` (Image/Hero Dark)
2. Composite using PIL:
   - Paint black over old screenshot area (x:173, y:319, w:1254, h:855 visible:581)
   - Scale user screenshot fit-to-width (1254px), pin to top
   - Apply rounded corner mask (36px radius)
   - Draw gradient border: orange (248,117,0) → white (255,255,255,77), computed for full 855px height, clipped to 581px
   - Center headline: Inter SemiBold 64px, white, y:198
3. Upload to approved asset host (Notion attachments, Helio workspace attachments, or Vercel Blob). Do not use litterbox.moe or other public/temporary hosts — they may be indexed and do not expire predictably. Use litterbox only if Yori explicitly approves it for this run and only for publishable synthetic assets.

Font files: `/tmp/Inter-SemiBold.ttf`. Download if missing:

```bash
curl -L -o /tmp/Inter-SemiBold.ttf \
  "https://fonts.gstatic.com/s/inter/v13/UcCO3FwrK3iLTeHuS_fvQtMwCp50KnMw2boKoduKmMEVuLyfAZ9hiJ-Ek-_EeA.woff"
```

### QA

Run [references/qa-checklist.md](references/qa-checklist.md) before delivering.

---

## Hard Rules

- Never replace UTM links with shortened URLs for official account posts.
- Never invent product capabilities, performance claims, or release details in copy.
- Never shrink type or change template geometry to force content to fit. Route to a wider layout or ask for shorter copy.
- Never crop more than 5% of a screenshot when the brief requires showing the full UI.
- Never edit the source template frame. Always duplicate first.
- If Notion write fails, report the error and include the full copy in the chat delivery so nothing is lost.
- If Figma is inaccessible, fall back to PIL without prompting the user — just note it in the delivery.

---

## Delivery

For full workflow:

- Confirmation that copy is posted to Notion
- Card image URL (and Figma frame link if method A was used)
- Platform used for card generation (Figma or PIL)
- Approval request sent to: `{approver_handle}`

For card only:

- Card image URL
- Selected template and layout name
- Screenshot preflight verdict and warnings (if applicable)
- Any copy or screenshot issue that still needs human review
