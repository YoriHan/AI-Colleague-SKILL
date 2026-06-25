# gatlin.md — Growth Data & GTM-Analytics Skill

Owner: Gatlin Verifier (@gatlin) — growth data + user-scenario analysis + cross-functional GTM coordination for Helio.
Purpose: a transferable skill file. A future instance picking this up should be able to run Helio's growth analytics correctly without re-deriving the口径 corrections and pitfalls below.
Format: three buckets — **新模式 (patterns)** / **坑 (pitfalls)** / **默认模板 (default templates)**. Each entry carries a traceable source (date, and seq/commit where it applies). No secrets, no PII, no raw user quotes in this file — those stay private (DM + private repo).

---

## 1. 新模式 — Patterns

### P1. 真实日活 ≠ UV (locked 2026-06-15)
The headline DAU must be **identified active users**, not visitor count.
- 真实日活 = `uniq(person_id)` where `person.properties.email IS NOT NULL AND person.properties.email != ''` AND fired any event that UTC day.
- The old "uniq(distinct_id) over all events" was a UV/visitor metric — ~4x inflated (anonymous landing traffic was ~77% of it on 6/14). Demote UV to a separate acquisition/marketing row, never call it 日活.
- All pre-6/15 daily "DAU" numbers (380–1318) were UV; the corrected real-DAU series runs ~50–280.

### P2. 核心活跃 = message_send (send side), not ai_message_sent (recv side) (locked 2026-06-17, w/ Trace)
- `message_send` = composer send-success = a human actually composed+sent. This is the true active-sender signal.
- `ai_message_sent` = human client *received* an AI-authored message = receiving side; inflated by AI-teammate chatter (a user who only watches fires it). Runs ~1.5–2x the send count daily.
- message_send predates ai_message_sent (5/13 vs 5/21) → fully backfillable, no trend break.
- During transition, report BOTH (sent = active, recv = AI reach). 真实日活 (email-based) is unaffected.

### P3. Channel → signup → DAU is a tight same-day chain (confirmed 2026-06-18)
Correlations on the corrected series: corr(total visits, real-DAU)=0.91, corr(social visits, real-DAU)=0.74, corr(new signups, real-DAU)=0.83. New signups and real-DAU move almost in lockstep. To read a DAU move, first look at that day's X/social acquisition volume.
- Organic search has the **highest activation rate** (~13% vs social ~10% / direct ~7%) but lowest volume → most under-invested channel; argues for systematic SEO.

### P4. Stickiness = return-days, not message volume (locked 2026-06-15)
Measure user stickiness by distinct active days, not msg count (head users dominate volume). Helio's stickiest external persona = **indie developers / solo product-builders** using Helio as "an AI team that builds for me" (~42% of stickiest external), not single-shot Q&A users. Internal team is ~37–40% of top-sticky users and ~21% of all desktop messages — always exclude before reporting sticky/persona views.

### P5. Mongo interface field separates humans from AIs (locked 2026-06-15)
In `helio-prod.channel_messages`: `interface='desktop'` = real humans; `interface='cli'` = AI teammates (self-intros/@mentions); `internal`/`assistant` = non-human. Correct human filter = `interface='desktop' AND type='channel_text'`. (The older `metadata.client_msg_id` filter undercounts and only marks desktop msgs after stamping began 5/29.)

### P6. Independent GitHub identity > borrowed keys
I operate as collaborator `gatlin-helio` on Yori's repos (write access granted per-repo), commits authored under my own identity. This is the durable pattern: independent identity + clean permission boundary, not acting through a human's account. Applies to this very file — pushed under gatlin-helio, not via a borrowed YoriHan token.

---

## 2. 坑 — Pitfalls (each cost real debugging time)

### T1. HogQL silent row truncation (burned 2026-06-18)
Multi-dimension `GROUP BY` across many days, or raw-row `SELECT` with no aggregation, defaults to ~100 rows returned → later dates silently truncated (a day showing "1" was actually 62). Fix: add `LIMIT 100000` (raw rows `1000000`) + `ORDER BY` the date on every multi-group / raw-row query.

### T2. Event-name drift (locked 2026-06-15)
`login` does NOT exist — the real event is `auth_login_success`. Verify event names against the live project before trusting a funnel; a non-existent event returns 0/garbage and looks like a metric collapse.

### T3. Chart.js in a hidden tab renders at size 0 (locked 2026-06-18)
A Chart.js canvas inside `display:none` has zero dimensions. In a tabbed dashboard, lazily initialize each chart on first tab-show (registry + build()), not on page load.

### T4. Recurring-job DoD trap (locked 2026-06-11)
Never bind a recurring job's definition-of-done to a capability the running agent lacks (e.g. a "write Notion" step on a runtime with no Notion token fails by construction every round). One owner, one path. Always emit a "nothing changed" timestamp row when there's no delta — it's the only thing that lets a human distinguish "healthy, no news" from "silently broken."

### T5. Pipeline can die silently — watchdog is mandatory (caught 2026-06-22)
The 08:03 daily silently stopped delivering for 5 days (6/17–6/21); only the 09:25 watchdog caught it. Any user-facing recurring report needs a separate watchdog schedule that re-sends/alerts if the primary missed.

### T6. Deploy: never trust silence (locked 2026-05-27)
For "did the deploy land?", check the commit's check-runs/deployments via API FIRST, not the live URL. Zero check-runs + zero deployment events on the merge commit = no build was triggered (e.g. Vercel↔GitHub disconnected). Don't curl-loop the domain.

### T7. Vercel free plan blocks non-team-member commits (locked 2026-06-23, recurred 2026-06-25)
On a free Vercel plan, only commits authored by team members auto-deploy; a collaborator outside the Vercel team gets `state=failure desc="Deployment was blocked"` (GitHub still shows a vercel[bot] deployment, but its status is failure). Diagnose via `deployments/<id>/statuses`. Fix = a Deploy Hook URL (store in Vault, never paste in chat), curl it after each push.
- **User-visible symptom**: the board *source* repo has a fresh daily commit, but the live vercel.app still shows stale data — the owner reads this as "you didn't update the board" (Yori, seq 774). Pre-empt it: when the deploy path is blocked, say so in the daily ("source pushed, live deploy pending the Deploy Hook"), don't claim the live board refreshed. Still pending Yori's Deploy Hook URL as of 6/25.

### T8. IP-based country ≠ user language/market (locked 2026-06-02)
PostHog $geoip country breakdowns mislead community/language decisions (VPN exits, diaspora). When the question is "where are our real users", cross-check with a script-class character-count over their channel text (kana/hangul/han/thai/cyrillic ranges) — no external lang-detect lib needed.

### T9. Future-dated calendar/schedule entries EXECUTE (locked 2026-06-16)
A future-dated calendar event is not an inert display prop — when its time hits it fires a real work session. Never create future-dated events for "fill my calendar for a screenshot" asks; use past-dated only.

### T10. Don't dump every user-feedback line into tasks (locked 2026-06-16)
Before logging a task from user feedback, run two gates: (1) feasibility / worth-it, (2) target-user fit (core persona = indie/solo builders assembling an AI team). Off-target or idiosyncratic asks → park in a 需求池, don't build. Merge duplicate facets of one problem into one task.

---

## 3. 默认模板 — Default templates / conventions

### D1. Daily report (Version C) — locked 2026-06-15, English since 2026-06-24
- Header line (mandatory): `👉 https://helio-growth-board.vercel.app/`
- Conclusion-first: one takeaway line + one next-step on top.
- Metric table: `Dimension | Today | Yesterday | Definition`.
- Rows: 真实日活 (headline) / 核心活跃 (show both send & recv during transition) / 新增注册 (signup_started) / 付费 (billing_plan_purchased count) / 访客UV (separate, marketing).
- Trend signal = **7-day average**, not single-day DoD/WoW (weekday DAU oscillates wildly; single days are noise).
- Delivery: DM @yori in **English** (so the convo can become social material). Numbers/口径 unchanged, only labels/diagnosis in English.
- Archive each daily to `YoriHan/DAU-Dashboard/reports/<UTC-date>.md` + `_history.md` row; then regenerate the board.

### D2. UTM / channel daily — locked 2026-06-15
- Same dashboard-link header.
- List EVERY channel with ≥1 visit (direct/X/wechat/LinkedIn/YouTube/ChatGPT), including 0-activation ones.
- Activation = wide口径: signup_started OR assistant_created OR ai_message_sent same-day.

### D3. Brand-word bucket for organic search (agreed 2026-06-23)
Brand = `helio.im`, or `helio` + {app/chat/ai/hq/workspace/teammate/assistant}. Bare "helio" alone is excluded (too generic). Everything else = non-brand organic.

### D4. PostHog access
US host `us.posthog.com`, project `421928`, Bearer auth, HogQL via `POST /api/projects/421928/query/`. Read-only key lives in Vault (`posthog-yori-readonly`), never plaintext in chat/DM.

### D5. Privacy boundary (hard rule)
Public/deployed pages (vercel.app board) get **de-identified aggregates only** — counts, distributions, scenario buckets, no handles/quotes/chat logs. Detail (handle · msg count · active days · one-line scenario · representative quote, redacted) goes ONLY to private surfaces: DM @yori + private repo `YoriHan/DAU-Dashboard/active-users/`. Redact sk-/ghp_/token/password patterns in any quoted text.

### D6. Credential discipline (locked 2026-06-14, w/ Trace)
Secrets (API tokens, PATs, Figma keys, OAuth callback URLs) go through Vault ONLY — never group channel, never DM (DM is also persistent chat history). If Vault fails, fix Vault; don't fall back to chat. Vault `credential --type token` requires data key `access_token` (not `token`). Only non-secret usage instructions may go via DM.

### D7. Dashboard generator
`gen_board.py` (self-contained: fetches PostHog series + lists DAU-Dashboard/reports via gh, data embedded, no secrets in output). Helio brand tokens (官网 light/paper theme): canvas `#fffefd`, ink `#0a0503`, accent orange `#f87500`, info `#476c90`, success `#3f754f`; fonts Playfair Display (headings) + DM Sans (body). 5 tabs: 概览 / 活跃·付费 / 获客渠道 / 用户场景 / 数据明细 / 日报归档. Deploy targets: `YoriHan/DAU-Dashboard` (archive) + `YoriHan/helio-growth-board` (Vercel source).

---

## Changelog
- 2026-06-25 (first distillation): foundational baseline established from accumulated growth/GTM-analytics knowledge. Pushed under gatlin-helio identity (YoriHan PAT not in Vault — pushing under own collaborator access instead; not a blocker, an identity choice).
- 2026-06-26 (review of 6/25): small increment. Sharpened T7 with the user-visible "source-current-but-live-stale" symptom after it recurred (Yori seq 774); the Vercel deploy-block is still pending her Deploy Hook URL. No new pattern/pitfall emerged from the day — daily DAU/UTM numbers (real-DAU 115 on 6/24, weekday stabilizing ~100-115) are data, archived in DAU-Dashboard, not skill content, so deliberately not folded in. Team-wide note: all AI colleagues now push nightly skill files to this shared repo.
