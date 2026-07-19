# email-genius.md
**Email Genius — Skill File**
*AI Colleague Skill | Last updated: 2026-07-20 JST (v20.6 — Day 28 lessons: Google Image Proxy batch-scan cluster rule, Stripe invoice delivery path, commitment breach follow-up pattern confirmed)*

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
4. **Your Helio @handle** — used as `--owner` when creating automations, so you can pause, edit, or delete them later.

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
2. Confirm your Helio @handle (Step 0 item 4) — pass it as `--owner @<your-handle>` on every `automation create` (**required**; without it the command fails)
3. Check for duplicates: `heliox automation list --json` — duplicate automations run silently twice
4. Automations are created **disabled** — run `heliox automation update <id> --enable true` after each create
5. `--timezone` is set at create time only — wrong timezone requires delete and recreate

**Automation A — Gmail Patrol (every 3 hours, 8×/day)**
```bash
heliox automation create "Gmail 三小时邮件巡查" \
  --cron "0 0,3,6,9,12,15,18,21 * * *" \
  --timezone "<your-timezone>" \
  --owner @<your-handle-from-Step-0> \
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
  --owner @<your-handle-from-Step-0> \
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
  --owner @<your-handle-from-Step-0> \
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
| KOL budget ceiling | (confirm with user) | "Flag any KOL quote above $X" |
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
- GMass false-positive filter (three patterns — apply all before counting opens):
- (a) Two notifications within 8–10 seconds from the same recipient = one pixel fired twice (email client pre-fetch/caching). Count as 1.
- (b) User Agent contains `via ggpht.com GoogleImageProxy` or IP is in Google's 66.249.x.x range = Google spam-scanner pre-fetch. Discard entirely — not a human open.
- (c) All other notifications with timestamps >30 minutes apart = genuine human open. Count each.
Only surface as warm signal when: distinct (post-filter) opens ≥ 3 spanning >30 minutes, or a single genuine open from a contact silent for 14+ days on an outbound email

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
3. Send test email to your test inbox address, wait for visual confirmation
4. Fire full batch exactly once after green light
5. Import all sent contacts to Notion immediately after

Rule: run the send command once per batch. (2026-06-24: 103 contacts sent x3 by mistake.)

### 5. Invoice workflow
- Receive invoice email → log sender, amount, invoice number to Notion (internal only)
- On PayPal payment confirmation email → mark closed in Notion, note in next patrol report
- On PayPal refund notification → note in patrol report, no Notion update needed
- If payment outstanding > 48h → flag in patrol report as overdue with hours or days pending
- On PayPal reminder email (subject "Reminder from [Vendor]") → escalate: log as "Reminder received, first invoiced [date], now [N] days pending." Report separately in 🧾 Invoice section as reminder, not a new invoice. Do not create a duplicate Notion entry.
- Publication-gated invoice: when an invoice arrives with explicit "video will be published upon payment" or equivalent language (content already approved and ready, payment is the only trigger to go live), flag as URGENT in the 🧾 Invoice section — delay in payment = delay in live content. Label as "publish gate." Standard overdue thresholds apply starting from the invoice date, but the first mention should carry the URGENT label regardless of how recently it arrived.

### 6. Daily KOL price scan (automated, ~23:00-00:00 JST)
Run against all active KOL negotiation threads in Gmail. For each new reply with pricing:
- Extract: channel name, subscriber count, pricing tiers (dedicated/integration/short), reply date
- Fill: Notion 达人价格 field + set 回复状态 to "待回复"
- Skip: already priced in Notion from prior scans
- Flag: above-budget outliers and unusually low prices (verify channel size)
- Report: send DM with new fills count, above-budget flags, and skip count

Started as manual task June 26; automated daily since June 26.

### 7. Notion import
After each outreach batch and after each patrol with new KOL contacts, import to Notion KOL database. Report count per batch.

### 8. Draft-first for outbound
Write to Gmail Drafts and surface for review. Never auto-send for new contact types.

### 9. Nightly skill review
Every night at 00:00 JST: review today's patrol logs and DM history, extract reusable logic, update this file, post [skill-update] email-genius.md to [#gtm_friends](helio://channel/6a39f2862db71a2d0b485fea) for Trace to review/sign off; Gatlin commits approved updates to github.com/YoriHan/AI-Colleague-SKILL. DM Yori with what changed.

### 10. Privacy discipline for public surfaces
Real names, email addresses, invoice numbers, and payment amounts belong in Notion only.
In skill files, channel posts, and demo material: use generic descriptions ("KOL vendor," "4 invoices from different vendors," "a YouTuber in the above-budget range").
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
- Dedicated tutorial (5-8 min): mid-range budget, varies with subs and engagement
- Integration / mention: lower tier
- Shorts: lowest tier
- Flag above-budget outliers; flag unusually low prices as needing size verification

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

**Day 28 (2026-07-19 → 2026-07-20):**

Google Image Proxy batch scan (false positive cluster): Two GMass open notifications arrived 31 seconds apart (from two different recipients, different outbound campaigns), both with identical User Agent `Mozilla/5.0 (Windows NT 5.1; rv:11.0) Gecko Firefox/11.0 (via ggpht.com GoogleImageProxy)` and identical IP 74.125.209.166 (Google range). This is Google's image proxy scanning multiple outbound emails in a single batch pass — not two independent human opens. Both were correctly discarded as false positives per the Day 20 rule. Rule refinement: when multiple GMass open notifications arrive within a 60-second window sharing the same IP in Google's range (66.249.x.x or 74.125.x.x) AND the same `GoogleImageProxy` User Agent, treat the entire cluster as one image proxy batch scan and discard all entries in the group. None count toward warm-signal thresholds. This extends the Day 20 single-notification rule to cover batch scans that hit multiple outbound emails simultaneously.

Stripe invoice as a new trusted delivery path: A vendor invoice arrived from `invoice+statements+acct_[id]@stripe.com` — Stripe's standard system invoice notification address, analogous to PayPal's `service@paypal.com`. This is the first Stripe-routed invoice encountered. Rule: when an invoice arrives from a sender matching `invoice+statements+acct_*@stripe.com`, treat it as a Stripe-routed invoice with a trusted platform delivery path. No domain-mismatch flag (the vendor's own domain is not the sender — Stripe is the router, just as PayPal is for service@paypal.com invoices). Log with vendor name (extracted from email body/subject), invoice number, and amount, identically to PayPal invoices. Verify trust at the domain level — sender must be @stripe.com; the `acct_[id]` portion varies per vendor. This extends the invoice delivery path rules to cover Stripe alongside PayPal.

Commitment breach follow-up timing confirmed: A KOL partner with an active video collaboration (script confirmed, deposit in progress) committed "the draft will be ready within 24 hours" on July 16. Draft did not arrive. On July 19 (Day 3 from the promise), Yori sent a direct follow-up explicitly referencing the July 16 commitment. This is the Day 26 rule executed correctly. Rule confirmed and extended: after an explicit 24h promise goes unfulfilled, follow up by Day 2-3 with a message naming the specific promise and date — not a generic "checking in." After the follow-up is sent, the patrol's role shifts to response tracking: if no reply arrives within 24h of the follow-up itself, re-flag as "follow-up unanswered, Day N from original promise." Day count continues from the original promise date, not the follow-up date.

**Day 27 (2026-07-18 → 2026-07-19):**

Technical product evaluation inquiry (new email type): A developer emailed the public inbound address evaluating Helio for a specific technical use case — they run multiple AI coding agents in parallel (Codex, Cursor), use Linear as orchestration, and want a single "agent-visibility layer" on top without needing Helio to hold model keys. They asked 5 precise product questions: (1) Linear integration status (native / MCP / not at all?), (2) whether Helio functions as a coordination dashboard without any model provider connected, (3) whether multiple AI teammates can genuinely run in parallel vs. sequential handoff, (4) desktop app vs. web-only, (5) free tier vs. Basic for evaluation. This email type is distinct from: inbound unsolicited partnership pitches (Day 22 — YouTuber sending media kit), OSS/nonprofit credits requests (Day 23), and enterprise accelerator invitations (Day 26 — platform credits + investor network). Rule: classify emails with (a) a specific named use case, (b) direct product questions, and (c) explicit evaluation framing ("I'm evaluating X for Y") as qualified inbound sales leads — not partnership or KOL categories. Draft behavior: answer each question factually, flag anything product-uncertain rather than guessing (e.g., Linear roadmap status), acknowledge the specific use case directly, offer a demo or Yori's direct attention for questions beyond what email can resolve. File under ⚠️ Needs your action. Priority: same-day or next-patrol response — technical evaluators often move on quickly if they don't get a fast, direct answer. Note: if the evaluator says "no Linear = no fit" upfront and the answer is honestly "no native Linear," the correct draft says so clearly rather than hedging — a direct honest response retains more trust than a vague "roadmap" answer.

Standard PayPal invoice sender path confirmed: Received a vendor invoice delivered via service@paypal.com (the standard PayPal system-triggered invoice notification address). No domain mismatch — this is the same sender domain as all prior PayPal invoice notifications and differs from the Day 26 rule (which flags invoices arriving from a vendor's own domain that doesn't match their known primary email address). The Day 26 domain-mismatch rule applies to invoices sent directly from a vendor's billing tool or unknown domain; it does not apply to PayPal-routed invoices where service@paypal.com is the expected sender regardless of which vendor issued the invoice. Clarification to Day 26 rule: only flag domain mismatch when the invoice arrives in a non-PayPal email from a vendor billing address that differs from the vendor's known primary domain. PayPal-routed invoices (sender = service@paypal.com) are always trusted for delivery path; verification is done by cross-referencing the vendor name inside the email body against the known relationship.

**Day 26 (2026-07-17 → 2026-07-18):**

Invoice sender domain mismatch: An invoice arrived attributed to a known vendor partner but sent from a domain unrelated to that vendor's established email addresses — likely a third-party billing or payment aggregator the vendor routes through. This creates a verification gap before payment. Rule: when an invoice's from-address domain does not match the vendor's known primary email domain, flag as "VERIFY — sender domain differs from vendor domain (confirm with vendor before payment)" in the 🧾 Invoice section. Do not recommend paying until the vendor's own contact confirms out-of-band that this billing address is legitimate. Treat separately from any concurrent invoice or request from the same vendor.

Explicit time commitment → deadline tracking: A partner committed to a specific deliverable "within 24 hours" (a video draft). The deadline passed without delivery. An explicit self-imposed deadline is a named obligation — distinct from a general follow-up or an overdue invoice. Rule: when a partner gives an explicit time window ("draft in 24h", "will send by Friday"), note the deadline in the patrol report and surface as ⚠️ Needs your action in the first patrol after the deadline passes without delivery. Suggested action: a brief follow-up ("Were you able to finish the draft?"). Day count starts from when the promise was made.

Credit balance top-up as product-account email type: A vendor partner's contact expressed preference for using account credits rather than a separate payment method for product access. This is a product-side account action — not a KOL negotiation and not an invoice. It requires the owner to take a product-level action to fulfill. Rule: classify account credit top-up requests, plan access grants, or other product-side account actions under ⚠️ Needs your action. Do not conflate with outstanding invoices from the same vendor, even when both arrive in the same patrol window — handle each independently as per the Day 25 concurrent-thread rule.

Enterprise AI accelerator offer (new email type): A major tech platform company sent an enterprise partnership invitation including model credits, technical support, and investor network introductions. This is distinct from (a) KOL collab invitations, (b) agency pitches, (c) inbound creator inquiries, (d) OSS/nonprofit credits requests. Rule: classify enterprise accelerator or platform partnership invitations as business-level decisions requiring the owner's explicit call. Draft response: acknowledge interest, ask for program requirements and what is expected in return, note any enrollment deadlines. File under ⚠️ Needs your action, not under KOL categories.

Aborted patrol retry = concurrent double report: When a scheduled patrol aborts (e.g., runtime_gone), the system retries it alongside the next scheduled patrol. Both turns fire concurrently, producing two reports for the same nominal window. In today's case, the aborted 18:00 JST patrol was retried at 21:00 JST alongside the scheduled 21:00 JST patrol, producing two separate patrol DMs for the same window. Rule: when two patrol DMs arrive for the same nominal time window, both are valid — the second is a retry from the earlier abort. They may contain complementary analysis. No owner action needed; note in nightly review. The aborted-patrol's retry produces accurate coverage because each patrol re-scans the recent inbox without a strict time-window filter.

SOP document created: Yori requested a user-facing work SOP document to document how Email Genius operates, suitable for new users and reuse with real contact details stripped. The SOP was produced as a Helio document covering: patrol cadence, email classification rules, collaboration email workflow, invoice tracking, KOL price scan, draft-first outbound policy, Draft Board, proactive notification rules, and owner action checklist. Stored in Helio Docs. If needed, update the SOP whenever significant workflow changes land in this skill file.

**Day 25 (2026-07-16 → 2026-07-17):**

PDF invoice extraction confirmed (pdftotext): When an invoice arrives as a PDF attachment, the working extraction path is: (1) run `email_fetch.py attachments <thread_id>` to download the PDF to the local invoice folder; (2) run `pdftotext <path> -` to extract plain text content; (3) parse for invoice number, amount, and due date. The `pdfplumber` Python library is not available in this environment — do not attempt to import it. `pdftotext` (via Homebrew poppler) is the reliable fallback. Confirm the downloaded path from the `attachments` command output before running `pdftotext`.

Concurrent same-partner threads: A single partner (a KOL vendor) had two active threads in the same patrol window — one for a pending invoice (INV-#XXXX) and one for a new collaboration proposal (a ~200k-sub channel). These are structurally independent: the invoice thread needs payment confirmation, the proposal thread needs a negotiation reply. Rule: when the same partner appears across multiple active threads, handle each independently and report them as separate line items in the patrol DM. Do not merge their actions or assume closing one resolves the other.

Quiet-day carry-over check confirmed working: July 16 had five consecutive quiet patrol windows (09:00, 12:00, 15:00, 21:00, 00:00 JST) with zero new emails. The carry-over check (Day 21 rule) ran correctly in each window, surfacing a pending partner invoice, a credit top-up item needing a decision, and an overdue PayPal reminder with updated day counts. This confirms: quiet patrols are not a "nothing to report" — they are aging reviews. The Day 21 rule is now confirmed across multiple quiet-day cycles.

email_fetch.py positional vs flag syntax: The `fetch --count N` flag form fails; use `fetch N` (positional) instead. This is a quirk of the local script's argument parser. When the script errors on `--count`, retry with `fetch 20` (no flag).

**Day 24 (2026-07-15 → 2026-07-16):**

Post-agreement warm reactivation signal: A KOL who agreed on pricing terms in June (dedicated video, specific rate) went silent for 36+ days — no contract, no next step from either side. Today they re-opened the original outreach email 6 times (once in the morning, then a burst of 5 between 11:02–11:09 JST), while the negotiation thread itself remained untouched. This is a "post-agreement reactivation warm signal" — stronger than a routine warm open because the context is a known deal that stalled, not a cold prospect. Rule: when a post-agreement-silent KOL re-opens the outreach email after 30+ days, surface as "warm reactivation — [KOL], [N]-day post-agreement silence, re-opened outreach email [M] times today" in the ⚠️ Needs your action section. Suggested action: Yori sends a brief nudge referencing the last agreed terms and asking to confirm the next step (contract or brief). This is time-sensitive because the contact is clearly re-evaluating now.

Rapid open burst (5 opens in <7 minutes) as active-review-right-now signal: The 5-open burst between 11:02–11:09 suggests the contact is actively sharing or re-reading the email in that moment — forwarding to a team, comparing proposals, reviewing on multiple devices. This is meaningfully different from 5 opens spread across hours. Rule: when 3+ opens arrive within a 10-minute window from the same contact (all passing the false-positive filter), surface as "active-review burst — [N] opens in [M] min" as a distinct flag even if the total count is already above the standard warm-signal threshold. The burst is a timing signal: the contact is in the email right now, not just occasionally revisiting.

Cross-thread GMass open grouping: GMass sends each open notification as a new email, and Gmail sometimes assigns each a separate thread ID rather than appending to the original outbound thread. This means a contact with 6 opens shows up as 6 separate single-message threads in a patrol window. Rule: before applying the open-count filter, group all GMass notify@gmass.co emails in the patrol window by recipient address (extracted from the subject line "opened by [email]"). Count per-recipient totals across all thread IDs — do not count per-thread. A contact with 4 notifications across 4 thread IDs is one contact with 4 opens.

Publication-gated invoice: A KOL partner sent an invoice with explicit language tying video publication to payment receipt ("send payment and we can publish it today"). The video was already approved by Yori (July 12). The invoice arrived July 15 — the video has been held back for 3 days at this point. Rule: when an invoice arrives with a publication gate (content approved and ready; partner is waiting on payment to go live), flag as **URGENT** in the 🧾 Invoice section from the first mention. Every day of payment delay is a day of live content lost. Include the publish-gate note so the urgency is visible — "URGENT (publish gate) — [KOL vendor] invoice, video ready, awaiting payment."

Post-kit 30d re-open signal: A second KOL (different from the post-agreement case above) re-opened the outreach email today after 39+ days of silence following Yori's collab kit send on June 6. No rate agreement was reached — they accepted the kit but never replied. Rule: when a KOL re-opens an outreach email after 30+ days of post-kit silence with no reply, add to ⚠️ Needs your action as "re-open signal — [N]-day silence after kit send. Consider a brief check-in ('Did you get a chance to look at the kit?')." This is weaker than a post-agreement signal but still worth a lightweight nudge — the re-open indicates lingering interest.

**Day 23 (2026-07-14 → 2026-07-15):**

Draft accumulation across patrol windows: Multiple patrol windows created separate drafts for the same Gmail thread (one active KOL thread had 4 drafts; another had 3; a third had 2). This happens because each patrol run checks for new emails and creates a fresh draft without first checking whether one already exists. Rule: before creating a new draft for any thread, run `list_drafts` filtered by thread ID. If an existing draft is found, overwrite it (same thread, update body) rather than creating an additional one. Multiple live drafts for the same thread confuse the outbox and risk duplicate sends when Yori reviews Gmail Drafts.

Platform-mismatch reply (Instagram vs. YouTube outreach): A contact received a YouTube-focused collab invitation but replied 29 days later stating they only do paid collabs on short-form content on Instagram, providing three Instagram accounts and a rate far above the standard per-video budget. This is structurally different from a same-platform rate negotiation. Rule: when a contact's platform differs from the outreach intent — (a) assess whether Helio currently runs Instagram short-form (Reel) campaigns; (b) if yes, apply Instagram-appropriate budget benchmarks (not YouTube-format rates); (c) if Instagram doesn't fit current strategy, treat as graceful decline citing format/platform mismatch, not budget. The draft-first response (asking for audience stats before committing) is the correct handling for an ambiguous platform fit. Long-lag (~29 days) is still actionable; Day 19 pattern confirmed again.

OSS sponsorship/credits request (new email type): An open source standards organization leader emailed the public inbound address asking whether Helio offers sponsorships in the form of credits or plan access. This is distinct from (a) KOL content collabs, (b) inbound partnership pitch emails, and (c) invoice or payment threads. Rule: treat OSS/nonprofit credits or plan-access requests as a product-level decision, not a marketing or KOL decision. The correct draft response: acknowledge the request, ask for context on the organization (what it does, how they'd use Helio, scale of access they're seeking), and flag for Yori's explicit approval before committing to anything. Do not promise credits or plan access without Yori's green light. File under ⚠️ Needs your action in patrol reports, not under KOL categories.

**Day 22 (2026-07-13 → 2026-07-14):**

Inbound unsolicited partnership inquiry: An AI tools YouTuber proactively emailed our public inbound address with their media kit, stats link, and past sponsor list (AI SaaS brands). This is structurally different from an outreach reply — it's a cold inbound pitch. Rule: treat inbound partnership emails as warm leads — they sought us out, not the reverse. Draft reply asking for their rate card and audience data. Note their past sponsor list in patrol report as a fit-signal indicator (AI SaaS sponsors = audience likely receptive to Helio). Log in Notion as "inbound inquiry" so it's distinguishable from outreach-reply threads in future lookups.

Autoresponder redirect reply: A YouTuber contact replied to outreach with language matching a canned response: "Thank you for contacting… For faster communication and…" — redirecting to a different contact path. This is not a genuine engagement; it's a routing notification. Rule: when a reply body contains "for faster communication" or similar redirect language without any substantive engagement, treat it as an autoresponder. Flag once in patrol report as "autoresponder/routing redirect — follow up at indicated contact if relevant," then skip the thread until a real human response arrives. Do not draft a KOL reply or update Notion pricing for routing messages.

Two-part Vercel security sequence: Two emails arrived within 90 seconds from a Vercel system email address: first "No Vercel account for this email" (login attempt failed), then a signup OTP (30-min expiry). This sequence — failed login immediately followed by signup attempt — is more suspicious than a single OTP, because it shows the actor first tried to access an existing account, was told none existed, and then attempted to create one. Rule: when two Vercel system emails arrive within minutes following this login-fail → signup-attempt pattern, surface in patrol report as "two-part security sequence detected" (not just "verification code") with a note to check whether any Vercel project exists under that email and whether any linked services were accessed. The OTP expiry provides a hard 30-minute window for the threat.

Agency tiered-package graceful close: A multi-creator agency sent a final follow-up with three package tiers (all far above budget) and closing-pressure language ("if no new budget, we'll close this conversation"). The smallest tier is more than 3× the per-creator budget ceiling. Rule: when an agency's final offer contains no tier within budget and uses closing-pressure language, the right move is a graceful close — not negotiation. Draft: acknowledge the content quality and audience fit, decline the current tier structure due to budget constraints, leave the door open for individual-creator opportunities in the future. This is distinct from a high-rate single-creator counter (where negotiation makes sense) — when the entire menu is out of range, closure is cleaner than a counter.

Soft follow-up after explicit rejection: A KOL contact sent "let me know if that changes things" after a prior rejection. Rule: note once in patrol report as "residual soft follow-up, no action needed," then auto-skip the thread unless a materially different proposal arrives. A one-sentence soft follow-up after rejection is a normal sales behavior — it doesn't reopen the negotiation and doesn't require a reply.

Broken commitment vs. normal overdue: A YouTuber partner was on their third follow-up, 17–18 days past a specific commitment Yori had made (payment + brief, with an implied next-day deadline). This differs from a standard overdue invoice or an unanswered email: there was an explicit promise with a named action and implied date. Rule: distinguish "commitment breach" from "overdue item" — a commitment breach means Yori made a specific promise (payment, brief, delivery) with a date, that date passed without action, and the partner is following up on that promise. Surface as "commitment breach — Day N (promised: [action, date])" rather than just "overdue." Day count starts from the promise date, not the last email date. At Day 14+, recommend Yori take the actual action (execute payment, send the file) rather than drafting another holding reply.

**Day 21 (2026-07-12 → 2026-07-13):**

PandaDoc contract completion as milestone signal: A PandaDoc notification email arrived with subject "[Agreement Name] has been completed by all participants." This is a new email type not previously codified. Rule: when PandaDoc sends a completion notification, treat it as a contract-signed milestone — log in Notion as "contract signed" for the relevant KOL, update status from "waiting on contract" to "contract-complete, filming TBD." Flag in patrol report as "✅ [KOL vendor] contract signed." This is distinct from (a) PandaDoc invitation emails ("you've been sent a document to sign"), (b) PayPal invoice/payment emails, and (c) reminder emails.

Quiet-inbox carry-over escalation: On July 12 JST, no new emails arrived in the inbox. During quiet days, carry-over items age silently without a new-email trigger to surface them. Rule: when a patrol window finds zero new emails, explicitly list all open carry-over items with their current day-count — treat the patrol as an aging review, not a "nothing to report" skip. Example carry-overs from a quiet-inbox day: (a) a small vendor invoice overdue with a PayPal reminder already sent — Yori owes this payment; (b) a KOL partner reply marked "not familiar with AI tools" — several days unanswered, draft still needed; (c) a KOL channel awaiting Yori response on a counter-offer below their stated floor (Day 18+); (d) a partner with a payment method impasse (refused PayPal, wants wire/crypto) — Day 34+, needs Yori decision on wire/crypto vs. dropping. Invoice Day-count escalation thresholds: Day 1-2 = note in report; Day 3-4 = "overdue" flag; Day 5+ = "overdue — escalate" flag with explicit recommended action.

**Day 20 (2026-07-11 → 2026-07-12):**

Google Image Proxy false open: A GMass open notification arrived with User Agent `Mozilla/5.0 (Windows NT 5.1; rv:11.0) Gecko Firefox/11.0 (via ggpht.com GoogleImageProxy)` and IP in Google's 66.249.x.x range. This is Google's image proxy pre-loading email content during spam/safety scanning — not a human opening the email. Rule: when a GMass open notification shows `via ggpht.com GoogleImageProxy` in the User Agent or the IP resolves to the 66.249.x.x Google range, discard it as a false positive. Do not count toward the warm-signal threshold. This is a third false-positive pattern alongside the existing 8–10 second double-notification rule. The combined false-positive filter is now: (a) two notifications within 8–10 seconds = one pixel fired twice; (b) `GoogleImageProxy` in User Agent or Google IP = spam-scanner pre-fetch; (c) anything else with distinct timestamps >30 min apart = genuine human open.

PayPal reminder = escalation signal: A payment reminder from PayPal (subject "Reminder from [Vendor] (INV-XXXX)") arrived for a small invoice that had been outstanding for several days. PayPal sends automatic reminders only after an invoice remains unpaid past its due date. Rule: when a PayPal email has "Reminder" in the subject, treat it as an escalation — log as "reminder received" in the patrol report with a note that the original invoice has been pending since the first notice date. If the invoice has been flagged in prior reports, update the day-count. This is distinct from a first-notice invoice and should be reported separately in the 🧾 Invoice section as "Reminder — [Vendor] INV-XXXX, first invoiced [date], now [N] days pending."

**Day 19 (2026-07-10 → 2026-07-11):**

Dual-path reply from same KOL manager: A KOL outreached at two different contact addresses (a creator platform and a talent network) had both emails forwarded to the same manager, who replied with identical content from both accounts within 2 minutes. This is distinct from a pure duplicate outreach — it's a legitimate KOL with representation at multiple organizations all handled by one person. Rule: (a) treat both replies as one inquiry; (b) read one for the rate data — content will be identical; (c) draft the reply to whichever thread the contact identifies as their "primary email" (look for that phrase in the body); (d) mark the other thread in Notion as "secondary contact — duplicate reply, no action needed"; (e) log both email addresses in Notion under the same KOL record. Do not reply to both threads.

Far-above-budget reply: A KOL quoted rates at approximately 3.5× (integration) and 6.8× (dedicated) the standard budget ceiling. Standard rule applies — surface immediately with format breakdown and "far above budget — needs Yori's call" flag. Do not draft a counter at this range; the gap is too wide to close without explicit Yori direction on whether to negotiate, decline, or explore a different format tier.

Long-lag reply is still actionable: A KOL originally outreached in early June replied ~31 days later with a complete rate card. Treat the reply as a fresh inquiry — no special handling for the delay. Long lags are normal in high-volume outreach; the KOL is still interested.

Warm signal refinement at 4 distinct opens over 3 hours: Today confirmed that 4 distinct open events (after filtering GMass double-notifications) spread across ~3 hours reliably predicted a reply within the same patrol window. Refinement to the existing warm signal rule: surface as [WARM — reply likely] when either (a) 3+ distinct opens (post double-notification filtering) span more than 30 minutes, OR (b) 6+ raw notifications arrive within a concentrated window (as in the existing rule). Both patterns are now confirmed predictive. The "concentrated window" calibration was for raw GMass notification counts including doubles; the filtered-distinct-event threshold is lower.

**Day 18 (2026-07-09 → 2026-07-10):**

Payment method impasse as a distinct stall pattern: A KOL partner thread stalled at 31+ days because the partner refused PayPal and offered only wire transfer or crypto. This is not a "waiting on reply" stall — both sides are actively responsive but blocked on payment terms. Rule: when a partner explicitly states they don't accept PayPal and offers only wire/crypto, flag immediately as "payment method mismatch" and surface as a Yori decision item. Aging beyond 7 days without resolution = flag as overdue impasse in every subsequent patrol with a day count. Don't hold silently alongside normal unreplied items.

Post-agreement thread staleness rule: A KOL negotiation that reached full agreement on both sides (budget and format confirmed for a dedicated YouTube video) went silent for 45+ days — no contract, no next-step email from either side. Rule: after a KOL agreement is confirmed (budget and format both accepted), if no contract or concrete next-step email is exchanged within 7 days, flag as "stalled post-agreement (day N)" in patrol reports and surface for Yori to send a nudge. Post-agreement silence is as actionable as no-reply to initial outreach. This is distinct from product-hold (where the pause is intentional) — here neither side moved.

Product-hold reactivation template confirmed: A product-hold KOL was reactivated by Yori sending the current collaboration kit + Notion link directly to the partner's contact. The confirmed reactivation format: (1) brief acknowledgement of the wait, (2) confirm product is live and ready, (3) share the latest collab kit URL, (4) ask them to proceed or re-send any script/contract details. This matches the Days 11-14 pattern — now confirmed as the standard. When reactivating, check that the collab kit URL is the current month's version.

Multiple small invoices per patrol window is now normal: A payment confirmation (invoice closed) and a new incoming small invoice arrived in the same patrol window from different KOL vendors. This is expected as the KOL program scales. Log each individually with vendor, amount, invoice number, and status. Keep invoice table in the DM report visually separate from KOL negotiation status rows — they serve different purposes and shouldn't be merged.

**Day 17 (2026-07-08 → 2026-07-09):**

Support-ticket merge = duplicate outreach signal: When a KOL routes email through a helpdesk (e.g. Zendesk), a second outreach email from a later batch creates a new ticket. Their team merges it into the original ("Request #XXXX was closed and merged into this request"). This notification lands in the original thread. Rule: merge notification = confirm duplicate outreach occurred. The active thread is the older/merged-into one. No new reply needed unless the contact initiates. Log in Notion as "duplicate outreach — merged into original thread."

Pre-batch domain cross-check via Gmail sent: A KOL already mid-conversation from a prior batch got re-outreached because CSV deduplication only runs within the current batch and Notion. Add a Gmail sent-folder check before finalizing each batch: search `to:<address> in:sent newer_than:90d` for each recipient. If a sent match exists, pull the thread — if there's already a reply, skip that contact from the batch.

"Not familiar with AI tools" inquiry pattern: Contact replied with curiosity but needs product education before they can evaluate fit. This is a warm lead, not a decline. Response template: (1) brief acknowledgement, (2) spell out the format (video length + what they'd do on camera), (3) explain the audience fit hypothesis, (4) give budget range, (5) ask for their rate card. 5–6 short bullets total; no walls of text.

GMass double-notification false positive: Two open-tracking emails arriving within 8–10 seconds from the same recipient = one physical open event triggering two pixels (email client pre-fetch or caching). Do not surface as "opened 2×" or count toward the 6-open warm-signal threshold. (Updated in Core Operating Patterns above.)

Delivery bounce — domain typo: A bounce with "domain couldn't be found" usually means a data-entry typo in the outreach CSV. Extract the probable correct domain (strip the typo suffix), note in patrol report so Yori can retry with the corrected address. Never re-send automatically from a bounced address.

**Days 15-16 (2026-07-07 → 2026-07-08):**

Email open tracking as warm signal: When Gmail shows an outbound email opened 6+ times in a concentrated window (e.g. 3–4 minutes), surface immediately in the patrol report as "[WARM] [KOL] opened outreach email N times — likely reply incoming." This helps Yori know a reply is probable before it arrives. Do not wait for the actual reply to flag engagement.

Duplicate outreach → duplicate reply threads: If the same KOL contact was accidentally emailed twice within a few minutes (same batch, different send calls), both threads can receive identical replies. When this is detected in the patrol, flag both threads, recommend replying to the most recent one only, and note the earlier thread as stale. Do not draft two separate counter-offers to the same contact.

Small creator invoices (small amounts): Handled identically to larger invoices — log to Notion with sender, amount, invoice number, and status. PayPal confirmation closes the entry. No special handling needed just because the amount is small.

**Days 11-14 (2026-07-03 → 2026-07-06):**

Long-overdue invoice resolved: A KOL vendor invoice (17+ days overdue, flagged in 3+ consecutive patrols) was finally paid via PayPal confirmation. When a payment confirmation arrives, close that item from patrol reports immediately and update Notion status to paid. Day-count persistence in reports is effective — continue it.

New KOL decline type — sponsor volume capacity: A partner declined due to already managing too many sponsors (not budget or audience fit). Response: acknowledge gracefully, express interest for future opportunities, keep door open. Log in Notion as "declined – capacity."

Product-hold KOL reactivation: When product update completes, draft a brief restart email: (1) acknowledge the delay, (2) confirm product is live and filming can proceed, (3) ask them to re-send script / contract details. Use Gmail draft approach; don't auto-send.

Above-budget multichannel KOL: One KOL quoted rates well above the budget ceiling across multiple formats and 4 platforms. Surface immediately with subscriber count, format breakdown, and "above budget — needs Yori's call" flag. Do not draft a counter until Yori decides.

Vendor second billing: A vendor sent a second billing notice for a pending invoice. Note in patrol report as "second billing received, N days outstanding" — makes escalation visible without special action. Continue day-count tracking until resolved.

Expansion scope discussion (pending): Yori raised interest in expanding Email Genius scope to cover product user emails (onboarding / activation sequences). Direction unconfirmed as of Jul 6. Skill file will update once clarified.

**Day 10 (2026-06-30):**

heliox email backend down (exit 6): When `heliox email send` or `list` returns exit 6, the backend is unavailable. Fallback: use Gmail MCP `create_draft` to build N drafts in the connected Gmail inbox with all fields filled (To, Subject, Body). Human reviews the drafts in Gmail → Drafts folder and batch-sends. This naturally satisfies any "human review before send" gate and avoids blocking on a broken backend.

1V1 outreach via Gmail draft approach: For any bulk outreach campaign requiring human review before send, the Gmail draft approach is the default path. Create all drafts, surface the count and folder location in the DM, wait for Yori's send confirmation. Never auto-send from an outreach batch.

skill ≠ install-time wizard (full team, 2026-06-30, seq 616–626): This skill file is a passive capability doc. When a new user installs it, nothing fires automatically — no heliox commands, no auth cards, no schedule creation. The First-Run Setup wizard in this file only runs if the runtime emits a `skill:install` wake event (a platform-level gap as of 2026-06-30). Until that hook exists, users must explicitly ask to be guided through setup. Do not claim the skill guides users "from 0 to 1 automatically."

**Day 9 (2026-06-29):**

Cross-batch KOL duplication: same KOL contact appeared in two separate reply threads because they were included in two different outreach batches. Different from the June 24 triple-send (same email fired 3x from one batch). Fix: deduplicate email addresses across *all prior batches* before starting any new batch, not just within the current one.

PDF rate cards: one partner sent pricing exclusively inside a PDF attachment. Script cannot extract PDF content. When replying with a counter-offer, use flexible phrasing ("We typically budget in the mid-range for channels at your size") rather than an exact counter. Flag in patrol report that attachment was unreadable so Yori can open manually if needed.

Multiple PayPal confirmations per patrol: two payment confirmations landed in the same window from different vendors. Normal — log each individually with INV number and vendor. No special handling needed.

Notion @mention burst: Notion sent 8+ rapid-fire notification emails for a single Notion thread update (GTM tracking doc). Auto-skip confirmed correct. No need to surface individual @mention emails in DM — only surface if the body contains an actual task or question directed at Yori (not just "@yorihan" auto-notify).

OAuth token expiry cascade: Gmail MCP token expired and blocked three consecutive patrols. When token expires: skip the patrol, DM Yori immediately and send a new auth card via `heliox tool google auth`. Do not silently skip without notifying.

**Days 6-8 (2026-06-26 → 2026-06-28):**

Patrol schedule was understated: the actual cron runs 8 patrols/day (every 3h). Skill file previously listed only 4 windows — corrected to all 8.

KOL price scan automated: Yori asked for a daily Notion price update on Jun 26 after noticing prices weren't being logged. Immediate run covered 6 KOLs; daily automation set up and running from Jun 27. Scan runs ~23:00-00:00 JST, covers all active negotiation threads in inbox, fills 达人价格 field.

Product-hold KOL category: one product-hold KOL confirmed they'll wait for a UI update before filming. This is distinct from "waiting on partner reply" — both sides are aligned, but we're the blocker. New status: product-hold. No follow-up needed; resume when product is go.

New agency blast sender: one agency blast sender (mass batches, misaligned audience). Added to auto-filter list. Specific domain tracked in Notion only.

PayPal refund notification: distinct from invoice payment. Incoming refund (outgoing money return) needs to be noted in the patrol report but doesn't update any invoice status in Notion.

Google Search Console: structured data notifications should be auto-skipped like Notion/Google Workspace notifications.

Open items aging: carry-over items age silently; patrol reports now include day count for items open >2 days to make the aging visible without Yori having to track it.

**Day 3 (2026-06-25):**

Invoice clearing burst: 4 invoices confirmed in a single 18:00 patrol from 4 different KOL vendors. Multiple simultaneous invoice events are normal — log each individually with INV number. Real names stay in Notion only.

Agency noise pattern: one agency sent 3+ blasts from different email threads, all crypto-only channels. Correct action: flag once with category note ("crypto-only, no AI/SaaS"), then filter on domain; no need to resurface same agency in future patrols.

Patrol catch-up: 06:00 patrol caught items that slipped from 03:00 window. Cross-check previous windows before reporting "new" to avoid double-surfacing.

KOL negotiation gap: a KOL quoted above our counter rate for dedicated; our proposal was below their stated floor — drafted reply acknowledging the gap, asking for flexibility. Lesson: flag when offer is below their stated floor.

Privacy catch: seq 495 included real vendor names in the Lessons Learned section. Trace flagged before repo push. Rule: generic descriptions only in public files.

**Day 2 (2026-06-24):**

Bulk outreach: send exactly once per batch; 103 contacts sent x3 by mistake.
Language: English only; no fallback to Chinese mid-session.
Report format: the border style is mandatory; freeform paragraphs were rejected.
Channel: #yoris_friends renamed to [#gtm_friends](helio://channel/6a39f2862db71a2d0b485fea). All skill-updates go to [#gtm_friends](helio://channel/6a39f2862db71a2d0b485fea).
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
