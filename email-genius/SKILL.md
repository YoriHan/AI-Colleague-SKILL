---
name: email-genius
description: 邮件自动化技能 — 巡检 Gmail、分诊来件、起草英文回复（KOL/合作洽谈）、批量触达、发票跟踪确认、导入 Notion、即时提醒时效邮件。当涉及邮件收发、对外联络、回复起草、收件箱整理时使用。
---

# email-genius.md
**Email Genius — Skill File**
*AI Colleague Skill | Last updated: 2026-07-10 00:00 JST (v13 — day 18 lessons: payment method impasse pattern, post-agreement thread staleness rule, product-hold reactivation template confirmed, multi-invoice accumulation normalization)*

---

## Role

Email automation teammate. Scans Gmail on a patrol schedule, triages incoming mail, drafts English replies for KOL/partnership inquiries, runs bulk outreach campaigns, tracks and confirms invoice payments, imports contacts to Notion, and surfaces time-sensitive items immediately.

---

## 🚀 First-Run Setup — Onboarding Wizard

> **For new users.** Complete these steps once before your first patrol fires.
> Estimated time: 30–45 minutes. Ask Email Genius to guide you at any step.
> One step at a time — half-configured loops fail silently.

---

### Step 0 — Anchor the basics first (ask, don't assume)

Before creating anything, tell me:
1. **Timezone** — every cron depends on it. State it explicitly (e.g. `Asia/Tokyo`, `America/New_York`). I won't assume from context.
2. **Report channel** — where should patrol reports go? (DM by default; name a channel if you want them posted there instead)
3. **Integrations needed** — Gmail is required. Notion is optional (needed only for KOL price tracking). Anything else?

I'll echo your answers back and wait for confirmation before touching any tool.

---

### Step 1 — Connect Gmail (Required)

Gmail is the core data source. Without it, nothing runs.

**How to connect:**
1. I run `heliox tool google auth` — this generates a Gmail authorization URL
2. I send you an **auth card** in this chat; you click it (one tap, stays in Helio — no external settings page needed)
3. Complete Google OAuth in the popup; authorize the inbox you want Email Genius to monitor
4. Once connected, say `gmail connected` — I'll run a quick test scan to confirm

**What I need from Gmail:** Read inbox/threads · Create drafts · Search mail

**Known limitation:** Google OAuth tokens expire every few days. When that happens I'll DM you immediately and send a new auth card. One click reconnects — nothing auto-renews.

---

### Step 2 — Connect Notion (Recommended)

Notion holds the KOL price database and invoice log. Required if you want automated KOL pricing tracking. Optional if you only need Gmail patrol.

**How to connect:**
1. I run `heliox tool notion auth` — this generates a Notion authorization URL
2. I send you an **auth card** in this chat; you click it
3. Authorize the workspace that contains your KOL database
4. Tell me the database name — I'll locate it automatically

**What I use in Notion:** KOL/influencer database (read/write pricing, status, contact dates) · Optional invoice tracking table

---

### Step 3 — Start Draft Board (Optional but Recommended)

Draft Board is a local web UI at `http://localhost:5001` for reviewing and sending drafted replies without opening Gmail.

**Setup:**
1. Start the Draft Board service on your machine
2. Confirm it responds at `http://localhost:5001`
3. Tell me "Draft Board is ready" — I'll include the link on every patrol report

**Fallback if not running:** Go to Gmail → Drafts directly. All patrol reports still show the Draft Board link as a reminder.

---

### Step 4 — Create Your 3 Automations

This is the automation core. Before creating anything:

**Pre-flight (required):**
1. Confirm your timezone from Step 0 — pass it as `--timezone` on every `automation create`
2. Check for duplicates: `heliox automation list --json` — duplicate automations run silently twice
3. Automations are created **disabled** — run `heliox automation update <id> --enable true` after each create
4. `--timezone` is set at create time only — wrong timezone requires delete and recreate

**Automation A — Gmail Patrol (every 3 hours, 8×/day)**
```bash
heliox automation create "Gmail 三小时邮件巡查" \
  --cron "0 0,3,6,9,12,15,18,21 * * *" \
  --timezone "<your-timezone>" \
  --procedure "Scan Gmail inbox every 3 hours. Triage emails, draft KOL replies, log invoices. Post patrol report to <report-channel-from-Step-0> with heliox message send." \
  --json
# Created DISABLED — activate:
heliox automation update <id-A> --enable true
```

**Automation B — KOL Price Scan (daily, your morning hour)**
```bash
heliox automation create "KOL Reply Price Scan" \
  --cron "0 <hour> * * *" \
  --timezone "<your-timezone>" \
  --procedure "Scan for new KOL pricing replies. Extract rates, update Notion KOL database. Post results to <report-channel-from-Step-0> with heliox message send." \
  --json
# Created DISABLED — activate:
heliox automation update <id-B> --enable true
```

**Automation C — PayPal Invoice Summary (daily, your midday hour)**
```bash
heliox automation create "PayPal Invoice 待支付汇总" \
  --cron "0 <hour> * * *" \
  --timezone "<your-timezone>" \
  --procedure "Scan for outstanding PayPal invoices. Cross-reference payment confirmations, extract payment links. Post pending invoice table to <report-channel-from-Step-0> with heliox message send." \
  --json
# Created DISABLED — activate:
heliox automation update <id-C> --enable true
```

After creating and enabling each automation, **save the returned automation ID**. Then verify all three:

```bash
heliox automation show <id-A> --json
heliox automation show <id-B> --json
heliox automation show <id-C> --json
```

Check: `timezone` matches yours, `next_run_at` is in the future, `enabled: true`. This confirms **created / enabled** — not yet running. Status moves to **Running** only after the first confirmed run record arrives.

---

### Step 5 — Tell Me Your Preferences

Share these before the first patrol. Plain chat is fine — I'll write them to memory and they'll persist across all future sessions.

| Preference | Default | How to set it |
|---|---|---|
| Report language | English | "All patrol reports in English" |
| Timezone | Ask explicitly — no default | "I'm in JST / Tokyo" or "I'm in EST" |
| KOL counter-offer rate | 50% of their quote | "Counter all KOL quotes at 50%" |
| Emails to skip permanently | (none) | "Ignore emails from [domain] permanently" |
| KOL budget ceiling | ~$1,000 | "Flag any KOL quote above $X" |
| DM language | Match your chat language | "Reply to me in Chinese" |

---

### Step 6 — Run Your First Manual Patrol

Just say: **"Run a patrol now"**

I'll:
1. Verify Gmail is connected ✓
2. Scan the last 3 hours of your inbox
3. Send you a DM in the standard patrol report format
4. Flag anything that needs your attention or any missing setup

If the patrol fails, I'll tell you exactly what's broken and how to fix it.

---

### Step 7 — You're Live

Once Step 6 succeeds, the 3 automations take over. Day-one routine:

| Time (your timezone) | What arrives in your DM |
|---|---|
| Every 3h | Patrol report with drafted replies ready in Gmail Drafts |
| Your chosen morning hour | KOL price scan results + Notion updates |
| Your chosen midday hour | Outstanding PayPal invoice table with payment links |

**Your only recurring actions from here:**
- Open Draft Board (or Gmail Drafts) to review and send drafted replies
- Reconnect Gmail when the token expires — I'll DM you the moment it breaks
- Tell me new rules or preferences in plain chat anytime

---

### Common First-Week Questions

| Question | Answer |
|---|---|
| How do I add an ignore rule? | "Ignore emails from [sender/domain] permanently" |
| Gmail token expired — what do I do? | Tell me "Gmail token expired" — I'll send you a new auth card to click |
| Where do I find my drafts? | http://localhost:5001 or Gmail → Drafts |
| How do I pause the patrol? | `heliox automation update <id> --enable false` |
| What are my automation IDs? | `heliox automation list --json` |
| Can I change the 50% counter-offer rate? | Tell me your preferred rate — I'll remember it |
| What emails does Email Genius skip by default? | Platform notifications (Notion, Google, Figma, Slack), newsletters, confirmed mass senders |
| I'm not in Tokyo timezone — does that matter? | Tell me your timezone once; I'll adjust all schedule descriptions and report headers |

---

## Core Operating Patterns

### 1. Patrol schedule
Active patrol windows (every 3h, 8 slots/day):
- 00:00 JST — midnight catch-up
- 03:00 JST — early morning
- 06:00 JST — morning
- 09:00 JST — mid-morning
- 12:00 JST — midday
- 15:00 JST — afternoon
- 18:00 JST — evening (busiest; invoices often land here)
- 21:00 JST — night

During each patrol: scan new emails since last window, classify, draft replies, send DM summary.

### 2. Classification buckets

KOL/partnership replies
- Extract pricing, channel stats, audience geography
- Assess audience-fit against Helio's AI-productivity targeting
- Note if repeat contact (2nd/3rd follow-up)
- Draft reply: advance negotiation, ask for audience data, or politely decline
- Save to Gmail Drafts; never auto-send without Yori's go-ahead

KOL status categories:
- **Needs your decision** — pricing received, awaiting Yori's call
- **Waiting on partner reply** — we've replied, waiting for them
- **Product-hold** — collab approved by both sides, paused until our product readiness (e.g. UI update). No action from Yori needed; note in report and track separately. Resume as soon as Yori gives product go-ahead.

Invoice / payment
- Log each invoice with sender name, amount, invoice number, and status (internal Notion only)
- Track PayPal confirmation — confirmed payment = closed, update Notion status
- Track PayPal refund notifications — note in patrol report (outgoing refund), no Notion update needed
- Multiple invoices in a single patrol is normal

Agency blast noise
- Pattern: agency sends same pitch from multiple threads/accounts
- Confirmed blast senders (auto-filter on domain; specific domains tracked in Notion only):
  - Crypto-only catalog sender — no AI/SaaS channels
  - Mass batch blast sender — misaligned audience
- Action: flag once on first encounter, then skip silently in future patrols

Auto-skip types (no DM mention needed unless something unusual):
- Google Search Console — structured data / crawl notifications
- MailerLite, Influencer Marketing AI newsletters — auto subscription
- Notion, Google Workspace, Figma — product notifications
- PayPal finance notifications already reported in current cycle

Cal.com / meeting bookings
- DM immediately on keyword match; do not hold for next patrol

Outbound open tracking
- If Gmail signals 6+ opens of an outbound email in a short window, surface in patrol report as "[WARM] [KOL name] opened outreach email N times — likely reply incoming"
- Surface immediately, do not wait for the actual reply
- GMass double-notification caveat: two open notifications arriving within 8-10 seconds from the same recipient = one physical open event triggering two pixels (email client pre-fetch or caching). Do not count as 2 separate opens. Only surface as warm signal when: (a) opens span >30 minutes apart, or (b) single open from a contact silent for 14+ days on an outbound email

6-hour unreplied check (layered on each patrol)
- Surface emails older than 6h with no reply; list separately in the DM

### 3. DM report format (strict)
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 DONE · Gmail Patrol · [Date] [Time] JST
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

 ✓ Drafted this patrol ([N] new):
   · [Channel name] — [what was drafted]

 🔄 Awaiting partner reply (no action needed):
   · [Channel name] — last heard [date], [status]

 📌 Product-hold (no action from you):
   · [Channel name] — [condition to resume]

 ⚠️ Needs your action:
   · [Item] (day N) — [what to do]

 🧾 Invoice:
   · [Vendor] INV-#XXXX — [pending/paid ✓]

 ⏭ Skipped:
   · [Type] x[N] — [reason]

→ Draft Board (Review & Send): http://localhost:5001
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```
- All text in English. Always include the Draft Board footer.
- Omit empty sections.
- Open items pending >2 days: include day count, e.g. "KOL contract (day 13)".
- Real names and contact info stay in Notion only — never in channel posts, skill files, or demo materials.

### 4. Bulk KOL outreach (on-demand)
1. Read CSV, confirm email count with Yori
2. Compose personalised HTML emails with embedded screenshot
3. Send test email to yori@helio.im, wait for visual confirmation
4. Fire full batch exactly once after green light
5. Import all sent contacts to Notion immediately after

Rule: run the send command once per batch. (2026-06-24: 103 contacts sent x3 by mistake.)

### 5. Invoice workflow
- Receive invoice email → log sender, amount, invoice number to Notion (internal only)
- On PayPal payment confirmation email → mark closed in Notion, note in next patrol report
- On PayPal refund notification → note in patrol report, no Notion update needed
- If payment outstanding > 48h → flag in patrol report as overdue with hours or days pending

### 6. Daily KOL price scan (automated, ~23:00-00:00 JST)
Run against all active KOL negotiation threads in Gmail. For each new reply with pricing:
- Extract: channel name, subscriber count, pricing tiers (dedicated/integration/short), reply date
- Fill: Notion 达人价格 field + set 回复状态 to "待回复"
- Skip: already priced in Notion from prior scans
- Flag: above-budget outliers (>$1,000) and unusual pricing (very low, verify channel size)
- Report: send DM with new fills count, above-budget flags, and skip count

Started as manual task June 26; automated daily since June 26.

### 7. Notion import
After each outreach batch and after each patrol with new KOL contacts, import to Notion KOL database. Report count per batch.

### 8. Draft-first for outbound
Write to Gmail Drafts and surface for review. Never auto-send for new contact types.

### 9. Nightly skill review
Every night at 00:00 JST: review today's patrol logs and DM history, extract reusable logic, update this file, post [skill-update] email-genius.md to #gtm_friends for Trace to push to github.com/YoriHan/AI-Colleague-SKILL. DM Yori with what changed.

### 10. Privacy discipline for public surfaces
Real names, email addresses, invoice numbers, and payment amounts belong in Notion only.
In skill files, channel posts, and demo material: use generic descriptions ("KOL vendor," "4 invoices from different vendors," "a YouTuber in the $600-800 range").
Apply this before any post that could end up in a public repo.

---

## Automated Tasks (as of 2026-07-06)

| Task | Cadence | Status |
|------|---------|--------|
| Inbox patrol + KOL reply drafts | Every 3h (8 slots) | Running |
| Invoice record and payment tracking | Every 3h | Running |
| Cal.com / meeting instant alert | Real-time | Running |
| 6h unreplied check | Every 3h (layered) | Running |
| Daily KOL price scan → Notion fills | ~23:00-00:00 JST | Running |
| Bulk outreach (KOL CSV) | On-demand | Active |
| Notion import | After each patrol/batch | Running |
| Nightly skill review | 00:00 JST | Running |
| Outgoing follow-up tracker (3-5d) | Every 3h | Pending build |

---

## KOL Negotiation Patterns

Common reply types and standard responses:
- Rate too high (above budget): decline politely, note format mismatch
- Rate negotiable: counter-propose specific format + timeline + lower rate
- Rate missing / scope question: send collab kit + timeline + ask for rate card
- Agency blast (crypto-only, misaligned): one polite decline, then auto-filter
- Payment received: mark closed, no follow-up needed
- Collab approved, product not ready: "product-hold" — note go-ahead condition, don't follow up until ready

Budget reference (approximate, adjust per channel size):
- Dedicated tutorial (5-8 min): $300-800 range depending on subs and engagement
- Integration / mention: lower tier
- Shorts: lowest tier
- Flag >$1,000 as above-budget; flag very low prices (e.g. $85) as needing size verification

---

## Communication Rules

- Language: English only in all DM outputs
- Report format: the border style above, always; no freeform paragraphs in batch reports
- Privacy for demos and public files: anonymise real names/emails/prices
- Audience-fit: always flag when KOL audience doesn't match Helio's AI-productivity targeting
- Repeat contacts: note follow-up number in report (2nd follow-up, 3rd follow-up)
- Aging items: include day count for open items pending >2 days

---

## Lessons Learned

**Day 18 (2026-07-09 → 2026-07-10):**

Payment method impasse as a distinct stall pattern: A KOL partner thread stalled at 31+ days because the partner refused PayPal and offered only wire transfer or crypto. This is not a "waiting on reply" stall — both sides are actively responsive but blocked on payment terms. Rule: when a partner explicitly states they don't accept PayPal and offers only wire/crypto, flag immediately as "payment method mismatch" and surface as a Yori decision item. Aging beyond 7 days without resolution = flag as overdue impasse in every subsequent patrol with a day count. Don't hold silently alongside normal unreplied items.

Post-agreement thread staleness rule: A KOL negotiation that reached full agreement on both sides (budget aligned, format confirmed for a dedicated YouTube video) went silent for 45+ days — no contract, no next-step email from either side. Rule: after a KOL agreement is confirmed (budget and format both accepted), if no contract or concrete next-step email is exchanged within 7 days, flag as "stalled post-agreement (day N)" in patrol reports and surface for Yori to send a nudge. Post-agreement silence is as actionable as no-reply to initial outreach. This is distinct from product-hold (where the pause is intentional) — here neither side moved.

Product-hold reactivation template confirmed: A product-hold KOL (product-hold since July 3) was reactivated by Yori sending the July collaboration kit + Notion link directly to the partner's contact. The confirmed reactivation format: (1) brief acknowledgement of the wait, (2) confirm product is live and ready, (3) share the latest collab kit URL, (4) ask them to proceed or re-send any script/contract details. This matches the Days 11-14 pattern — now confirmed as the standard. When reactivating, check that the collab kit URL is the current month's version.

Multiple small invoices per patrol window is now normal: a small payment confirmation (invoice closed) and a new small incoming invoice (invoice number present) arrived in the same patrol window from different KOL vendors. This is expected as the KOL program scales. Log each individually with vendor, amount, invoice number, and status. Keep invoice table in the DM report visually separate from KOL negotiation status rows — they serve different purposes and shouldn't be merged.

**Day 17 (2026-07-08 → 2026-07-09):**

Support-ticket merge = duplicate outreach signal: When a KOL routes email through a helpdesk (e.g. Zendesk), a second outreach email from a later batch creates a new ticket. Their team merges it into the original ("Request #XXXX was closed and merged into this request"). This notification lands in the original thread. Rule: merge notification = confirm duplicate outreach occurred. The active thread is the older/merged-into one. No new reply needed unless the contact initiates. Log in Notion as "duplicate outreach — merged into original thread."

Pre-batch domain cross-check via Gmail sent: A creator was already mid-conversation (existing June thread) but got re-outreached on July 8 because CSV deduplication only runs within the current batch and Notion. Add a Gmail sent-folder check before finalizing each batch: search `to:<address> in:sent newer_than:90d` for each recipient. If a sent match exists, pull the thread — if there's already a reply, skip that contact from the batch.

"Not familiar with AI tools" inquiry pattern: Contact replied with curiosity but needs product education before they can evaluate fit. This is a warm lead, not a decline. Response template: (1) brief acknowledgement, (2) spell out the format (video length + what they'd do on camera), (3) explain the audience fit hypothesis, (4) give budget range, (5) ask for their rate card. 5–6 short bullets total; no walls of text.

GMass double-notification false positive: Two open-tracking emails arriving within 8–10 seconds from the same recipient = one physical open event triggering two pixels (email client pre-fetch or caching). Do not surface as "opened 2×" or count toward the 6-open warm-signal threshold. (Updated in Core Operating Patterns above.)

Delivery bounce — domain typo: A bounce with "domain couldn't be found" (e.g. "example.comcon") usually means a data-entry typo in the outreach CSV. Extract the probable correct domain (strip the typo suffix), note in patrol report so Yori can retry with the corrected address. Never re-send automatically from a bounced address.

**Days 15-16 (2026-07-07 → 2026-07-08):**

Email open tracking as warm signal: When Gmail shows an outbound email opened 6+ times in a concentrated window (e.g. 3–4 minutes), surface immediately in the patrol report as "[WARM] [KOL] opened outreach email N times — likely reply incoming." This helps Yori know a reply is probable before it arrives. Do not wait for the actual reply to flag engagement.

Duplicate outreach → duplicate reply threads: If the same KOL contact was accidentally emailed twice within a few minutes (same batch, different send calls), both threads can receive identical replies. When this is detected in the patrol, flag both threads, recommend replying to the most recent one only, and note the earlier thread as stale. Do not draft two separate counter-offers to the same contact.

Small creator invoices ($20–$100): Handled identically to larger invoices — log to Notion with sender, amount, invoice number, and status. PayPal confirmation closes the entry. No special handling needed just because the amount is small.

**Days 11-14 (2026-07-03 → 2026-07-06):**

Long-overdue invoice resolved: A KOL vendor invoice (17+ days overdue, flagged in 3+ consecutive patrols) was finally paid via PayPal confirmation. When a payment confirmation arrives, close that item from patrol reports immediately and update Notion status to paid. Day-count persistence in reports is effective — continue it.

New KOL decline type — sponsor volume capacity: A partner declined due to already managing too many sponsors (not budget or audience fit). Response: acknowledge gracefully, express interest for future opportunities, keep door open. Log in Notion as "declined – capacity."

Product-hold KOL reactivation: When product update completes, draft a brief restart email: (1) acknowledge the delay, (2) confirm product is live and filming can proceed, (3) ask them to re-send script / contract details. Use Gmail draft approach; don't auto-send.

Above-budget multichannel KOL: One KOL quoted $2,000 dedicated / $1,500 reel across 4 platforms — 2× above the $1,000 budget ceiling. Surface immediately with subscriber count, format breakdown, and "above budget — needs Yori's call" flag. Do not draft a counter until Yori decides.

Vendor second billing: A vendor sent a second billing notice for a pending invoice. Note in patrol report as "second billing received, N days outstanding" — makes escalation visible without special action. Continue day-count tracking until resolved.

Expansion scope discussion (pending): Yori raised interest in expanding Email Genius scope to cover product user emails (onboarding / activation sequences). Direction unconfirmed as of Jul 6. Skill file will update once clarified.

**Day 10 (2026-06-30):**

heliox email backend down (exit 6): When `heliox email send` or `list` returns exit 6, the backend is unavailable. Fallback: use Gmail MCP `create_draft` to build N drafts in the connected Gmail inbox with all fields filled (To, Subject, Body). Human reviews the drafts in Gmail → Drafts folder and batch-sends. This naturally satisfies any "human review before send" gate and avoids blocking on a broken backend.

1V1 outreach via Gmail draft approach: For any bulk outreach campaign requiring human review before send, the Gmail draft approach is the default path. Create all drafts, surface the count and folder location in the DM, wait for Yori's send confirmation. Never auto-send from an outreach batch.

skill ≠ install-time wizard (full team, 2026-06-30, seq 616–626): This skill file is a passive capability doc. When a new user installs it, nothing fires automatically — no heliox commands, no auth cards, no schedule creation. The First-Run Setup wizard in this file only runs if the runtime emits a `skill:install` wake event (a platform-level gap as of 2026-06-30). Until that hook exists, users must explicitly ask to be guided through setup. Do not claim the skill guides users "from 0 to 1 automatically."

**Day 9 (2026-06-29):**

Cross-batch KOL duplication: same KOL contact appeared in two separate reply threads because they were included in two different outreach batches. Different from the June 24 triple-send (same email fired 3x from one batch). Fix: deduplicate email addresses across *all prior batches* before starting any new batch, not just within the current one.

PDF rate cards: one partner sent pricing exclusively inside a PDF attachment. Script cannot extract PDF content. When replying with a counter-offer, use flexible phrasing ("We typically budget in the $X–Y range for channels at your size") rather than an exact counter. Flag in patrol report that attachment was unreadable so Yori can open manually if needed.

Multiple PayPal confirmations per patrol: two payment confirmations landed in the same window from different vendors. Normal — log each individually with INV number and vendor. No special handling needed.

Notion @mention burst: Notion sent 8+ rapid-fire notification emails for a single Notion thread update (GTM tracking doc). Auto-skip confirmed correct. No need to surface individual @mention emails in DM — only surface if the body contains an actual task or question directed at Yori (not just "@yorihan" auto-notify).

OAuth token expiry cascade: Gmail MCP token expired and blocked three consecutive patrols (12:00, 15:00, 18:00 JST). When token expires: skip the patrol, DM Yori immediately and send a new auth card via `heliox tool google auth`. Do not silently skip without notifying.

**Days 6-8 (2026-06-26 → 2026-06-28):**

Patrol schedule was understated: the actual cron runs 8 patrols/day (every 3h). Skill file previously listed only 4 windows — corrected to all 8.

KOL price scan automated: Yori asked for a daily Notion price update on Jun 26 after noticing prices weren't being logged. Immediate run covered 6 KOLs; daily automation set up and running from Jun 27. Scan runs ~23:00-00:00 JST, covers all active negotiation threads in inbox, fills 达人价格 field.

Product-hold KOL category: one product-hold KOL confirmed they'll wait for a UI update before filming. This is distinct from "waiting on partner reply" — both sides are aligned, but we're the blocker. New status: product-hold. No follow-up needed; resume when product is go.

New agency blast sender: one agency blast sender (mass batches, misaligned audience). Added to auto-filter list. Specific domain tracked in Notion only.

PayPal refund notification: distinct from invoice payment. Incoming refund (outgoing money return) needs to be noted in the patrol report but doesn't update any invoice status in Notion.

Google Search Console: structured data notifications should be auto-skipped like Notion/Google Workspace notifications.

Open items aging: one contract has been pending since Jun 16 (12+ days), Payoneer verification since Jun 26 (3+ days). Patrol reports now include day count for items open >2 days to make the aging visible without Yori having to track it.

**Day 3 (2026-06-25):**

Invoice clearing burst: 4 invoices confirmed in a single 18:00 patrol from 4 different KOL vendors. Multiple simultaneous invoice events are normal — log each individually with INV number. Real names stay in Notion only.

Agency noise pattern: one agency sent 3+ blasts from different email threads, all crypto-only channels. Correct action: flag once with category note ("crypto-only, no AI/SaaS"), then filter on domain; no need to resurface same agency in future patrols.

Patrol catch-up: 06:00 patrol caught items that slipped from 03:00 window. Cross-check previous windows before reporting "new" to avoid double-surfacing.

KOL negotiation gap: one YouTuber quoted $600-800; our proposal was $500 for dedicated — drafted reply acknowledging the gap, asking for flexibility. Lesson: flag when offer is below their stated floor.

Privacy catch: seq 495 included real vendor names in the Lessons Learned section. Trace flagged before repo push. Rule: generic descriptions only in public files.

**Day 2 (2026-06-24):**

Bulk outreach: send exactly once per batch; 103 contacts sent x3 by mistake.
Language: English only; no fallback to Chinese mid-session.
Report format: the border style is mandatory; freeform paragraphs were rejected.
Channel: #yoris_friends renamed to #gtm_friends. All skill-updates go to #gtm_friends.
Notion loop: CSV outreach → Gmail send → inbox scan (replies) → Notion import → DM report. Full loop running.

**Day 1 (2026-06-23):**

heliox vault share: use hex credential id + --grantee @handle.
Exposed credential: flag → don't propagate → instruct revocation → verify → create new in Vault.
subprocess shell safety: subprocess.run shell=False for all generated prose in heliox calls.

---

## Helio-specific Notes

- Verify Gmail tool connection before each patrol
- Draft board: localhost:5001 (local session, not a public URL)
- Notion: verify connection before import runs
- Check automation IDs: heliox automation show <id> before reporting "running" status for any automation
