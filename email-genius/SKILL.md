# email-genius.md
**Email Genius — Skill File**
*AI Colleague Skill | Last updated: 2026-07-28 JST (v24.8 — Day 36 addendum, revised after group review, mechanism/evidence corrected across four review passes, patched once more post-v24.7 for a single-observer label precision fix (no content change), the last upgrading session self-report to physical draft-timestamp evidence: duplicate-drafts pileup has **two additive causes**, not one — (1) no-existing-draft check in the write path, a code fact confirmed by direct read of `cmd_draft()`, unbounded and independent of any sample; (2) this writer can run more than one concurrent session against the same inbox state, confirmed as a single mechanism — delayed-fire lifecycle overlap, 3 independent instances joined against `thread_root_seq` and the run API — with actual Gmail draft-creation timestamps confirming duplicate drafts in 2 of 3 (same-thread pairs under a minute apart on exactly those two dates, none on the third, matching a reverse prediction that could have failed and didn't) and a content-divergence variant in the third (one session missed real new items the other found); a same-fire-fanout shape was asserted, then re-asserted as candidate, then retracted outright once the anchoring field was actually checked, and that full arc is preserved in the superseded-conclusions block rather than smoothed over; demonstrates lifecycle overlap and, where cited, actual duplicate drafting — but not interleaved write-operation collision, no engine/queue evidence exists for that; a hypothesis (not yet confirmed, independently derived twice tonight) suggests the consistent ~3h05m delay is a delayed run always picked up at the next scheduled tick, not variable queueing; run-record status/shape confirmed to have zero evidentiary value for proving either single-session execution or that a cycle executed at all; second independent inbox-writer identified as a daily 10:00 JST launchd cron, schedule confirmed from the plist itself, code layer shared with patrol (one fix covers both) but schedule/session layer genuinely independent (a patrol-only procedure fix does not reach it); Gmail drafts API behavior verified (draft id vs message id vs threadId); the automation-side concurrency defect is tracked as Helio task **U3-1190** (deliberately unassigned pending a named runtime-access owner), not claimed as fixed or self-owned by this file; none of this dedup logic currently lives in the automation's actual runtime procedure document — see §11 for the full evidence split, tiering, and the ownership-split decision content for Yori)*

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
1. I run `heliox tool google auth` — this generates a Gmail authorization link
2. I send you the link in chat; click it to open the OAuth window in your browser
3. Authorize the inbox you want Email Genius to monitor and complete the Google OAuth flow
4. The system wakes me automatically once authorization completes — I'll run a quick test scan to confirm the connection

**What I need from Gmail:** Read inbox/threads · Create drafts · Search mail

**Known limitation:** Google OAuth tokens expire every few days. When that happens I'll DM you immediately with a new connect link. Click it to reauthorize — nothing auto-renews.

---

### Step 2 — Connect Notion (Recommended)

Notion holds the KOL price database and invoice log. Required if you want automated KOL pricing tracking. Optional if you only need Gmail patrol.

**How to connect:**
1. I run `heliox tool notion auth` — this generates a Notion authorization link
2. I send you the link in chat; click it to open the OAuth window in your browser
3. Authorize the workspace that contains your KOL database and complete the Notion OAuth flow
4. The system wakes me automatically once authorization completes — tell me the database name and I'll locate it

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
| Gmail token expired — what do I do? | Tell me "Gmail token expired" — I'll send you a new connect link to open and reauthorize |
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
- `email_fetch.py`'s own body field hard-truncates at 4000 characters — a PayPal invoice's amount can fall past that cutoff and read as missing even though it isn't. If an invoice amount looks absent, pull the full message (Gmail MCP `get_message` or equivalent) before reporting "amount unknown." Distinct from the Day 34 list-view truncation rule (a different automation's summary view) — this is the patrol's own fetch script silently cutting content.

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

Team-addressed compliance/security notices
- Distinguish by recipient: sent to a shared team inbox (e.g. hello@) with multiple internal cc's (e.g. dev@/w@), not to Yori personally
- Surface once with the deadline noted, labeled as a team action item — not a personal ⚠️ decision
- Only apply daily re-escalation (Day 32 bracket-phrase rule) when the deadline is inside the same near-term urgency window; a distant deadline (60+ days out) gets a single mention, not repeated resurfacing

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
Every night at 00:00 JST: review today's patrol logs and DM history, extract reusable logic, update this file, post [skill-update] email-genius.md to #gtm_friends for Trace to review/sign off; Gatlin commits approved updates to github.com/YoriHan/AI-Colleague-SKILL. DM Yori with what changed.

### 10. Privacy discipline for public surfaces
Real names, email addresses, invoice numbers, and payment amounts belong in Notion only.
In skill files, channel posts, and demo material: use generic descriptions ("KOL vendor," "4 invoices from different vendors," "a YouTuber in the above-budget range").
Apply this before any post that could end up in a public repo.

**Pre-publish mechanical scan (nightly, before posting):**
Before posting the `[skill-update]` message to #gtm_friends, scan the draft content for:
- Email addresses: any `@` match (whitelist exceptions: `service@paypal.com`, `service@intl.paypal.com`, `service@paypal.co.uk`, `invoice+statements+acct_*@stripe.com`, `*@payoneer.com`, `GoogleImageProxy` in UA strings, `notify@gmass.co`)
- Amount patterns: `$\d`, bare currency figures (e.g. `$<amount>`, `USD <amount>`)
- Invoice number patterns: `INV-` prefix, or a 4-digit numeric token appearing **within invoice/billing context only** (e.g. directly following "invoice #", "Invoice No", "INV-", "receipt #"); whitelist: standalone years (2018–2035), port numbers in localhost context (e.g. `5001` in `localhost:5001`), and any 4-digit token not adjacent to an invoice/payment keyword
- Capitalized proper name/company strings: 2+ consecutive capitalized words not in a rule description, code block, or URL; allowlist: Email Genius, Google Image Proxy, PayPal, Stripe, Draft Board, Search Console, PandaDoc, GMass, Gmail, Notion, Helio

If any match found outside the whitelist: **abort posting**, DM @yori listing each matched item, do not post until cleared.

This scan runs mechanically before every nightly post — not as a post-hoc review. Passive Rule 10 instruction alone is insufficient; nightly context regen does not auto-execute it.

### 11. Gmail drafts API behavior & duplicate-draft mitigation (verified 2026-07-28, fix not yet implemented, split by evidence class after group review)

Verified directly against the live Gmail API (not assumed):
- A draft's `id` stays stable across `drafts.update()`.
- The draft's `message.id` changes on **every** update, including a normal patrol overwrite — this is expected Gmail behavior (an edit is a new message revision under the hood), not drift or a bug. Don't use `message.id` as a stability/idempotency key for a draft.
- `message.threadId` behavior differs by draft type: a **standalone** draft (no thread set) can get reassigned a new thread on update. A **reply-style draft with an explicit thread set** — the patrol's actual usage pattern — keeps its `threadId` pinned across updates. So carry-over overwrites via the normal reply-draft path do not detach from the real conversation.
- The inbox fetch step is confirmed **pure count-based**, not time-filtered: it pulls the top-N unread messages by list order, with no comparison against any prior run's timestamp. An old unread thread can requalify indefinitely as long as it's still unread and within the top-N — this is why a thread from weeks back can resurface. The correct mental model is "was this in the top-N unread at fetch time," not "unread since last run."

Duplicate-drafts pileup, investigated in depth: **two mechanisms are both confirmed real and additive — this is not a single-cause bug, and treat neither as "the" main cause**:

- **Mechanism 1 — no-existing-draft check, a code fact, unbounded by any data sample.** Confirmed by directly reading `cmd_draft()` in the write path (`~/.claude/scripts/email_fetch.py`): the function makes exactly one Gmail API call, `drafts().create()`, unconditionally — `drafts().list()` appears zero times in the file, no branch, no existing-draft check anywhere. Patrol re-drafts the same open thread every cycle with no check for an existing unsent draft. This causes accumulation **across** cycles: one extra draft per patrol run on any long-lived unreplied thread.
- **Mechanism 2 — this writer can run more than one concurrent session against the same inbox state, confirmed as a single shape (delayed-fire collision), with two separate levels of proof that must not be merged into one claim.** An earlier pass in this investigation claimed two shapes — genuine same-fire fanout ("Shape A") and delayed-fire lifecycle overlap ("Shape B") — from three candidate incidents. Adding the one field that actually settles it (`thread_root_seq`, which marker each report is anchored to) shows **all three are the same shape: delayed-fire collision. Zero confirmed same-fire-fanout instances exist in this evidence.** Retracting "Shape A" entirely rather than softening it; see the superseded-conclusions block below.
  - **Confirmed cause of duplicate drafts specifically, upgraded from session self-report to physical draft-timestamp evidence, in 2 of 3 instances.** Session reports for the 2026-07-21 and 2026-07-27 pairs each claimed both the on-time and delayed session drafted replies on the same counterpart thread(s) — but self-report has been wrong multiple times tonight, so this was checked directly against actual Gmail draft creation timestamps rather than left resting on the reports alone — physical evidence now, upgraded from narrative, but still single-observer (the same access-holder pulled it; not yet independently re-verified by a second reviewer). Method (Gatlin's proposal, run directly, not just agreed with): group real draft timestamps by thread, look for a same-thread pair under 15 minutes apart — normal single-pass operation produces one draft per thread per ~3h cycle, so a sub-15-minute pair on the same thread is only explained by two sessions writing independently. **Result, with a reverse prediction that could have failed and didn't**: on 2026-07-21, three separate threads each show a same-thread draft pair ~1 minute apart — matching the three counterparties both sessions' reports named. On 2026-07-27, the same pattern appears on the thread both sessions' reports named. On 2026-07-23 — the content-divergence instance, where the on-time session wrote zero drafts and only the delayed session wrote new ones — there is no sub-15-minute same-thread pair anywhere in that day's drafts, exactly as predicted if the mechanism is real and that day genuinely had no duplication to produce. This is now physical evidence, not self-report, for the 2026-07-21 and 2026-07-27 instances specifically.
  - **The third instance (2026-07-23) is not duplicate-draft evidence — it's the content-divergence variant**: the on-time session reported zero new emails and wrote no drafts; the delayed session reported and drafted two genuinely new replies the on-time session missed entirely. No duplicate draft here, but a different, arguably worse harm — a real action item that only one of the two sessions surfaced at all.
  - **What is not demonstrated, in any instance**: write-operation *collision* in the interleaved/race-condition sense (two Gmail API calls contending on the same operation) — there's no engine/queue log or write-level API timestamp to show that. What's demonstrated is two independent, individually-successful write operations from two sessions that shouldn't both have run. Don't conflate "two full write operations both succeeded, redundantly" with "the writes raced or corrupted each other" — this file claims only the former.
  - **Confirmed instances (3), all the same mechanism, run-leg dual-observed, channel-leg single-observer**: a fire that starts significantly late can still be actively producing its report when the *next* fire starts on time, both touching the same inbox/thread state. All three instances found tonight show the delayed fire's report landing **~3h05m** after its own `fired_at` — 3h05m05s (2026-07-21), 3h05m34s (2026-07-23), 3h05m55s (2026-07-27) — while the on-time fire in each pair reports within minutes.
  - **Hypothesis, not a conclusion, for why the ~3h05m figure is so consistent (n=3, one transcription source, independently derived twice by different methods tonight — flagged for U3-1190, not asserted here)**: the tight ~50-second consistency isn't in the delay's *duration*, it's in the *execution* duration after pickup. Measuring the delayed report against the **next** marker instead of its own gives +4m57s / +5m27s / +5m51s — the same magnitude as each pair's on-time report against its own marker (+3m53s / +2m05s / +6m14s). That suggests a stuck run isn't delayed by a variable queueing wait; it's picked up exactly at the *next* scheduled tick and then takes a normal few minutes to execute — making "~3h05m" simply "one full cycle late, plus a normal execution," not a property of the delay itself. If true, this would mean a delayed run colliding with the next on-time run isn't a probabilistic event but a structural certainty for this automation's current design. Checkable, not checked: look for more delayed instances and see if "delayed report minus next marker" keeps landing in the normal-execution-duration band, or get an engine/queue timestamp directly.
  - **Honest boundary, not overstated**: what's demonstrated is *lifecycle overlap* — two sessions from adjacent fires alive at the same wall-clock time. It does **not** demonstrate *write-operation collision* (interleaved Gmail write calls on the same thread) — there's no engine/queue log or write-level timestamp to show that, and this file does not claim it.
  - **Content-divergence is the more dangerous variant of this mechanism**: a near-duplicate is merely redundant, but a divergent pair (the 2026-07-23 instance: one session reported zero new emails, the delayed one drafted two genuinely new replies) means one session's report can silently omit real action items the other session actually found and acted on.
  - **Aggregate status, stated honestly rather than implying full coverage**: a DM-history cross-check across 153 reachable fires flagged 8 as hard-tier colliding pairs (~5.2%). Of those 8, 3 have now been individually joined against `thread_root_seq` and the run API and confirmed as delayed-fire collisions (the three above); the remaining 5 have not yet been run through the same join check. Do not treat the 8/153 figure as a verified rate for any specific mechanism until that classification is complete.
  - **One-directional caveat on this whole family of evidence**: a duplicate or divergent delivery proves concurrency; a *lack* of such deliveries elsewhere does not prove its absence, since a colliding session can draft and then withhold its own report entirely once it notices the collision. A clean delivery history on another automation sharing this runtime cannot distinguish "no concurrency happened" from "concurrency happened and left no delivery trace."
- **Durable methodology finding, applies to any epoch of this data, not just tonight, and broader than concurrency alone**: a scheduled-run record's `status` field, and the fact that a fire produces exactly one run record, have **zero** evidentiary value for proving single-session execution — not "weak," zero. This was independently re-derived twice: once by pulling the exact fire above from a second copy of the run data (result: 1 run, `status=success`, 1 thread root — a clean "negative" on a fire now known to be positive), and once by recognizing that a fire_key/fired_at grouping test is structurally blind to the phenomenon it was meant to detect, because the run-tracking unit is per-fire, not per-session — one fire is always one record no matter how many sessions worked it. **The same field also cannot be trusted for the narrower question of whether a cycle executed at all**: a sibling automation on the same runtime has a documented case of a run permanently recorded as `status=skipped` whose session nonetheless produced and published real output — so `status` can misreport execution in either direction, not just stay silent on concurrency. This has two concrete landing points in this file: the "61 of 68 pre-boundary records sit at status `fired`" reasoning above describes what the record shows, not a claim about whether those cycles executed; and the acceptance bar below ("confirmed working across multiple patrol cycles") must be checked against actual delivered output, not against run `status`, or the check inherits the exact blind spot this bullet describes. Never cite run-record shape as proof of single-session behavior, or as proof a cycle did or didn't execute, in either direction, at any point in this file's history.
- **How far back Mechanism 2 goes: run records alone can't answer pre-boundary; channel/report joins may, and two of the three confirmed instances sit before the boundary.** The run API's `source` field only starts reporting `schedule` (vs. `unknown`) at 2026-07-23T18:00:00Z; the 68 records before that boundary are overwhelmingly (61 of 68) stuck at status `fired` with no terminal state recorded at all, so run-record status cannot confirm or rule out multi-session activity before that point on its own. The 2026-07-21 and 2026-07-23 delayed-fire-collision instances sit before this boundary and were joined against the automation channel's own header/report/`thread_root_seq` fields — but that channel is visible to only one reviewer tonight, so the join itself is single-observed for the channel side even though the run-API side is dual-observed. If the channel-side join holds up under independent re-verification, it means this mechanism has direct (not extrapolated) evidence inside the largest unattributed-draft bucket's date range; keep reading that bucket as "a mechanism with single-observer evidence inside this window can explain a real share, sizing unresolved" — not as "unknowable," and not as "likely human-edited."
- A **minor compounding factor**: several of this skill's own automations share a wall-clock trigger instant, which can add to the pileup but isn't either of the two confirmed mechanisms above.

**Fix direction, refined after group review — and not fully closable in one step today**: check for an existing draft on a thread before writing a new one (upsert-by-thread rather than always-create). Among current *documented* entry points, `cmd_draft()` in the shared `~/.claude/scripts/email_fetch.py` is the best available single landing point — both known callers (the 3-hourly patrol procedure and the daily cron below) invoke it today — but a guard placed only there is **not a structural guarantee**: the cron path is a freshly-spawned agent session told to run a named skill, not bound to this function by anything that prevents it from calling something else later. It reaches `cmd_draft()` today because its skill file currently says so, not because it structurally can't do otherwise.

The layer both writers necessarily touch regardless of code path is Gmail's own draft state — check it at write time — but that's mitigation, not closure: the Gmail API has no conditional-create, and a list-then-write sequence across separate processes is a TOCTOU race, not atomic. Full closure requires **(a) exactly one effective writer, and (b) that writer never runs more than one concurrent session at once** — a write-time state-check can substitute for a missing (a) but not for a missing (b), since the non-atomicity is specifically on the concurrent-access side. **(b) is now confirmed to fail**, directly (see Mechanism 2 above) — not untested, not merely open. This means stopping the local cron (which only removes a second writer, addressing (a)) **cannot reach closure on its own regardless of that decision**, because the concurrency lives on the Helio-automation side of the patrol itself, independent of anything running on Yori's own machine. Every option below is mitigation until the automation-side concurrency/idempotency defect is itself fixed or bounded.

The detecting-"human-touched" question from the previous pass is separately still **unresolved, not just unimplemented**: the byte-diff heuristic was tried and dropped (regenerated draft text isn't byte-stable run to run even with no human involved), and the fallback signals sketched then — last-modified vs. creation-time drift, or absence from Drafts implying "sent" — were flagged in review as unsafe under two independent writers and are not the current recommendation. No replacement design has been agreed yet.

Treat the existing-draft check, the write-time Gmail-state guard, and the human-touched detector all as open implementation work. Do not report duplicate-drafts as resolved in patrol reports until a check is live, confirmed working across multiple patrol cycles, and confirmed to actually sit in the automation's real runtime procedure document (procedure doc `6a3df441…` — see below) — not merely in this skill file. Until then, expect the existing-drafts pileup to keep growing; do not "clean it up" by bulk-deleting without checking against these signals first.

**Decision pending, not yet made — split by who actually owns each half, not handed to Yori as one bundled question**:

- **Her call, and now a smaller, separate item**: the local desktop cron (`com.yorihan.email-reply-auto`) is her own machine and her own workflow choice. Stopping it removes a second writer (helps precondition (a) for the patrol's own duplicate-draft problem) but — since Mechanism 2 above is confirmed patrol-native — does **not** touch the actual concurrency defect either way. This is now cleanup/second-writer scope, not a lever on the main bug.
- **Not her call, and not a bundled "we'll handle it" either**: concurrent sessions from adjacent delayed/on-time fires is a defect in the Helio automation runtime itself, something none of the reviewing agents on this file directly own or can schedule. Scope it precisely, neither shrunk nor inflated: **proven** for this patrol automation specifically (the evidence above, delayed-fire lifecycle overlap — not "one fire spawns N sessions," that shape was retracted); **possible but unproven** for other automations sharing the same runtime, since a clean delivery history elsewhere doesn't demonstrate absence (see the one-directional caveat above) — don't write this up as either "just an email-genius bug" or "confirmed platform-wide." Writing "the engineering side will fix it" here would be exactly the recurring-task failure mode where a step is assigned to whoever-holds-a-capability without naming who that is — silently un-owned, fails every cycle. Tracked as **Helio task U3-1190** (pinned, deliberately unassigned — missing a named owner with runtime access is the task's own point, not an oversight in it): status as of this writing is "created, owner pending, not yet scheduled." This file states the defect and its evidence; do not treat "flagged in the skill file" as equivalent to "owned and scheduled" — check U3-1190's actual status for that.
- **A write-time Gmail-state check** is available as mitigation regardless of the above — not a peer option, not closure, explicitly a fallback: Gmail has no conditional-create, list-then-write across processes is a TOCTOU race, and an agent-driven caller isn't structurally bound to any particular local code path. Its ceiling travels with it wherever it's mentioned; do not let it read as "the fix" in a few weeks.
- **Leaving things as-is** means no change, not "somewhat less duplication," since none of this logic currently lives in the runtime procedure doc.

Cross-cutting all of the above: procedure doc `6a3df441…` not being rewritten means this file update is documentation only, regardless of which parts get acted on. Delivered to Yori as a single, ownership-split decision item separately (one voice, one report) rather than folded silently into "fixed."

**Superseded conclusions from earlier in this investigation — listed explicitly so a future reader doesn't cite dead text that looks current** (same date, same author, confident tone, sitting in the historical entries below — nothing in this file's prose otherwise flags that these are dead):
- ~~"Duplicate-drafts root cause: ... refuted (~100 scheduled fires, zero duplicate trigger times, clean 3h cadence). Confirmed cause: patrol re-drafts ... no existing-draft check — plain single-session logic gap"~~ (original v24.0 text, seq 2587/2732) — **superseded**: two additive mechanisms confirmed, not one; "refuted" was an unbounded claim from a bounded sample; see §11 above.
- ~~"scheduler-level double/triple-firing is refuted"~~ as an absolute, full-history claim — **superseded**: bounded to "no duplicate fire *times*" within the ~12.4-day sample; says nothing about session-level concurrency.
- ~~Run-record shape (one record per `fired_at`) can be used to argue only one session touched that fire's window, or that a cycle executed~~ — **superseded** on both counts: demonstrated false on a fire whose adjacent delayed sibling produced a colliding session (delayed-fire lifecycle overlap, not one fire with ≥2 sessions of its own — that specific framing was itself retracted, see above), and false on a run recorded `skipped` that nonetheless produced and delivered real output (cross-agent instance, see §11). Run records prove fire schedule and count; they prove nothing about session count or whether a cycle executed.
- ~~`d422`/`bc19` as evidence of "one fire spawns multiple sessions"~~ — **superseded**: re-investigated and reclassified as two distinct fires (lifecycle overlap from a delayed queue, not fan-out from one trigger); see Mechanism 2 above.
- ~~2026-07-21 15:00Z and 2026-07-23 03:00Z as "same-fire fanout" ("Shape A")~~ — **superseded, not merely disputed**: adding `thread_root_seq` (which marker each report is actually anchored to) showed each pair points to two *different*, adjacent markers, not one shared marker. Both are delayed-fire collisions, the same mechanism as `d422`/`bc19`, not a second shape. This was asserted as "candidate same-fire" for a period during this investigation before the anchoring field was checked — do not cite that intermediate framing either.

**Second, independent writer into the same inbox — schedule-verified, not just timing correlation (new disclosure, unresolved by any patrol-side fix)**: a macOS `launchd` job (`com.yorihan.email-reply-auto`, `StartCalendarInterval` = 10:00 local/JST = 01:00 UTC, confirmed by reading the plist directly, not inferred from draft timestamps) spawns a separate `claude -p` session once daily, instructed to run the `/email-reply` skill. That skill's own SKILL.md, and the 3-hourly patrol's procedure document, both call the **same shared script**, `~/.claude/scripts/email_fetch.py` — confirmed by reading both documents' invocation lines directly. A second, co-located copy of the script bundled inside the cron skill's own folder (`~/.claude/skills/email-reply/email_fetch.py`) is not called by either documented path and looks orphaned; verify and remove it separately rather than treating it as a second fix target. It carries its own copy of the same 4000-character body-truncation bug and the same no-existing-draft-check gap, for what that's worth if it's ever reactivated.

Caveat carried forward honestly, not smoothed over: this covers the two *documented* entry points only — a broader search for any third writer timed out incomplete, so "no other writer exists" is not verified, only "these two both currently trace to the same script." Any statement that "the duplicate-draft issue is fixed" must specify which writer(s) and which layer it covers — see the fix-direction discussion above for why neither a `cmd_draft()` guard nor a Gmail-state check closes this in one step. Flag this explicitly to Yori as part of the same pending decision, not folded silently into this skill's fix.

**Process rule — canonical artifact for skill-file candidates**: when multiple agents review and hand around draft versions of this file, the version posted as a channel attachment is the only copy everyone can actually read — each agent's own local workspace file lives on a different machine and isn't visible to, or persisted for, anyone else. Treat the last channel-attached version as ground truth for "what the group approved," not a locally-saved copy, and don't assume a locally-reconstructed draft matches what was actually posted — confirm by size/hash before trusting it.

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

**Day 36 (2026-07-27 → 2026-07-28):**

Hidden invoice amount traced to the patrol's own fetch truncation (new tooling gotcha, root-caused): A genuinely new PayPal invoice (never seen in any prior report, confirmed by cross-checking the full outstanding-invoice list) appeared to have no amount in the initial pass. Investigation found the cause wasn't a template or attachment issue like prior amount-truncation cases — it was `email_fetch.py`'s own body field hard-cutting at 4000 characters, with the PayPal template placing the dollar figure just past that point. Pulling the full message via Gmail MCP `get_message` recovered the amount immediately. Rule (added to Core Operating Patterns, Invoice/payment): whenever an invoice amount looks missing, treat it as a truncation candidate before treating it as genuinely absent — open the full message first. This is now the second distinct truncation source identified (Day 34: a different automation's list-view preview; today: the patrol's own fetch script), so "amount unknown" should be rare going forward — it only holds after a full-message check, not a preview-level one.

Team-inbox compliance notice vs. personal action item (new classification, added to Core Operating Patterns): A security/compliance follow-up email (a platform account-verification step with a multi-month compliance deadline) arrived addressed to the team's shared inbox and cc'ing several internal addresses, not to Yori directly. This sits between two existing categories — it's not a routine auto-skip platform notification, but it's also not a Yori-personal decision like a KOL rate or an invoice. Rule: classify by recipient scope first. Team-addressed compliance/security mail gets one mention with the deadline noted (so nothing silently expires), but doesn't earn the Day 32 bracket-phrase daily-escalation treatment unless the deadline has moved into a near-term window. Re-flagging a 3-months-out team deadline in every patrol would just be noise competing with genuine same-day decisions.

DM thread-parameter bleed between two independent send calls (small procedural fix): While reporting a completed patrol, the automation-channel note's `--thread` value was accidentally reused on the separate DM send call that followed it — the two are different conversations with independent thread state. The DM still delivered in full; the only symptom was a thread tag pointing at a seq that doesn't exist in that DM's own history. Rule: treat each `heliox message send` call as carrying its own thread context — never carry a `--thread` value across a channel note and a DM report (or between any two different target conversations) in the same reporting pass.

Cross-thread deadline claim vs. our own pending ask (new reply pattern): A KOL partner sent an urgent "this is the final deadline for script feedback, otherwise we publish with the existing cut" message — but the message crossed with an already-pending question from our side (asked two days earlier) about swapping in a different candidate video, which the partner hadn't acknowledged. Answering only the surface urgency would have let the partner's default option win by default while our real blocking question sat unanswered. Rule: when a partner's urgent deadline message lands on a thread where we already have an outstanding ask, the reply must do both — acknowledge/resolve their stated deadline AND explicitly restate our still-open question in the same message, rather than letting one crowd out the other. Two live asks on one thread need one reply that answers both, not a reply that quietly drops the older one.

Carry-over items continuing to age as expected (no new rule, tracking confirmed working): the pending decision on batch-clearing several dozen accumulated duplicate Gmail drafts, and the pending call on whether to close out one long-overdue small invoice without payment, both remain open into a second day and were correctly re-surfaced with day counts rather than silently dropped. The Day 21 aging-carryover rule continues to hold under a full quiet-ish day with only routine invoice/payment closure (no new decisions) as the other activity.

Duplicate-drafts root cause, follow-up investigation (resolves the open hypothesis above — see Core Operating Patterns §11 for the full evidence split, revised after group review): a full-team review this same night dug into the "automation may be double/triple-firing" hypothesis with actual scheduler data, a direct code read, and — critically — direct observation of a live incident, rather than inference alone. Result: **two mechanisms are both confirmed real and additive, not one root cause** — full detail and evidence tiering in §11. (1) The **no-existing-draft-check gap is a code fact**, confirmed by reading `cmd_draft()`'s write path directly, unbounded by any data sample; it accumulates drafts *across* patrol cycles. (2) **This writer can run more than one concurrent session against the same inbox state**, confirmed as a single mechanism — delayed-fire lifecycle overlap, where a late-running fire is still active when the next fire starts on time — joined against `thread_root_seq` and the run API for 3 independent instances (2026-07-21, 2026-07-23, 2026-07-27), each showing the delayed fire's report landing ~3h05m after its own fire time. For 2 of the 3 (2026-07-21, 2026-07-27), this is confirmed to actually produce duplicate drafts: real Gmail draft-creation timestamps, checked directly rather than left on session self-report, show same-thread draft pairs under a minute apart on exactly those two dates, and no such pairs anywhere on 2026-07-23 — a reverse prediction that could have failed and didn't, since 2026-07-23 is the one instance where the sessions' own reports describe zero duplication (content divergence instead). An earlier pass in this same investigation claimed a second shape ("genuine same-fire fanout") for two of these three incidents; adding the anchoring field showed both were actually the same delayed-collision mechanism, not a second one — that claim is retracted, not softened (see the superseded-conclusions block). A broader DM-history sweep flags 8 of 153 fires as candidate collisions; only the 3 above are individually confirmed so far, the rest are unclassified pending the same join check. It accumulates drafts *within* one cycle either way. Neither mechanism (1) nor (2) is "the" main driver — they stack. Separately, within the ~100-record, 2026-07-15 → 2026-07-27 (~12.4-day) run-API sample, there are zero duplicate scheduler *fire times* on a clean 3-hour cadence — that fact is real and scoped to the sample, but it does not imply "no concurrency," since a run-record's shape has zero evidentiary value either way for how many sessions worked a given fire (§11). A minor compounding factor (a few of this skill's own automations sharing a wall-clock trigger instant) can add to the pileup but isn't either confirmed mechanism above.

Verified Gmail drafts API behavior, useful beyond tonight's investigation (added to Core Operating Patterns §11): direct testing against the live API confirmed a draft's `id` is stable across updates while its `message.id` changes on every single update (expected Gmail behavior, not a bug), and that a reply-anchored draft (the patrol's real usage) keeps its `threadId` pinned across updates while a standalone draft can have its thread reassigned. Also confirmed: the inbox fetch step is purely count-based over unread mail with no date filter, so an old unread thread can resurface indefinitely as long as it stays unread and within the top-N fetched — not just "unread since last check."

Second, independent inbox writer disclosed (new, unresolved, needs Yori's call — corrected to match §11, this and that section previously disagreed): a separate scheduled job on Yori's own machine (`com.yorihan.email-reply-auto`, 10:00 JST daily) — outside this skill's automations entirely, running a different skill definition on its own schedule — writes drafts into the same Gmail inbox. It does **not** carry its own separate copy of the write logic: both this job's invoked skill and the 3-hourly patrol's procedure document call the same shared `~/.claude/scripts/email_fetch.py`, confirmed by reading both documents' invocation lines directly (see §11). A co-located bundled copy of the script inside the cron skill's own folder is not called by either documented path and is flagged as orphaned — treat it as a cleanup risk, not a second writer to patch. **Split this cleanly by layer, both halves matter and neither one alone is the full picture**: at the **code layer**, the two writers share one script, so the 4000-character truncation bug is one instance, not two — patching `email_fetch.py` once covers both callers, it is not two separate fixes. At the **schedule/session layer**, the two writers are genuinely independent — this cron has its own trigger and spawns its own fresh agent session, entirely outside the patrol's procedure document — so a rule written only into the patrol's procedure document does not reach it regardless of the shared script underneath. "The duplicate-drafts issue is fixed" therefore can't be a single claim: a code-level fix to the shared script helps both writers at once, but a procedure-level or session-behavior fix scoped only to patrol does not. Surfaced to Yori as a second, separate decision point rather than assumed covered by tonight's fix direction.

Workspace-vs-channel-attachment portability, confirmed the hard way (process lesson, added to Core Operating Patterns §11): multiple agents discovered independently tonight that a skill-file candidate saved to one agent's local workspace is invisible to, and doesn't outlive, that agent's own machine — only a version actually posted as a channel attachment is something everyone can read and verify. Several rounds of candidate edits were traded during tonight's review, but none reached final sign-off before this pass — the byte-diff "human-touched draft" heuristic that one candidate proposed was flagged and dropped as unreliable (regenerated draft text isn't byte-stable run to run even with no human edit), and a replacement detection signal wasn't finalized. Treat the existing-draft-check fix and the "human-touched" detector both as designed-but-not-yet-implemented — do not report duplicate-drafts as resolved in patrol reports until the check is actually live and confirmed working across multiple patrol cycles.

**Day 35 (2026-07-26 → 2026-07-27):**

Local skill file drift from chat-only fixes (process gap, found and closed): Last night's nightly review went through three rounds of reviewer-requested fixes (scrubbing raw internal doc/channel IDs, making the dedup rule DM-or-channel aware, making the invoice-dedup guard durable across the full log) and posted each round as a chat attachment, ending with a version confirmed clean and ready to push. But the local skill file this automation actually reads and edits every night was never updated to match — it was still sitting at the pre-fix version with the flagged internal IDs still in place. Found while preparing tonight's review, before making any further edits: synced the local file byte-for-byte to the last approved chat attachment. Rule: when a reviewer's fix is applied and reposted as a chat attachment, write that same fix back into the canonical local file in the same pass. The chat attachment is what gets pushed to GitHub, but the local file is what the next run edits from — if the two diverge, a future review edits from a stale base and can silently reintroduce an already-fixed leak. Treat "post the fix" and "save the fix" as one step, not two.

PayPal Invoice automation's first live run surfaced a 3h-patrol coverage gap: on its first real run (seeded from empty the night before), the invoice-focused automation found outstanding invoices the regular 3h Gmail patrol's classification had not been catching — including one from a partner already known through an active collab email thread, but invoiced through that vendor's own separately-branded invoicing platform rather than the collab thread's domain, plus a couple of invoices where the list-view email preview truncated the amount entirely (common for a Stripe notification preview and for a bank-transfer invoice with the amount only inside a PDF attachment). Rule: (a) a vendor already known through an active collab thread may still send invoices via a differently-branded platform/domain — cross-reference the vendor name inside the invoice body against known collab threads before treating it as a brand-new, unrelated sender; (b) when a list-view preview doesn't show the invoice amount, open the individual email or attachment to confirm the exact figure before logging or reporting it — never report an invoice as "amount unknown" when opening the source would resolve it.

Superseded-invoice pattern (new hygiene rule): two separate old, silent invoices from returning vendors turned out to have already been superseded — a newer invoice number from the same vendor, at the same or an adjacent amount, had been paid more recently, while the older invoice number was simply never followed up or cancelled. Rule: when an invoice has been silent 20+ days with no reminder and no payment trail, before escalating it as overdue, check whether a newer invoice number from the same vendor (same or close amount) was paid more recently — if so, flag it as "likely superseded by a later invoice, recommend closing rather than treating as still outstanding" instead of a fresh overdue escalation. Avoids double-counting the same underlying charge under two invoice numbers.

Unsolicited third-party signup confirmation (new email type, security-relevant): A 00:00 JST patrol (concurrent automation, running independently of this review) found a "Welcome to [freelancing platform]" account-confirmation email plus a freelancer's direct-message notification, for a platform account the owner has no record of registering. This is distinct from routine platform notifications (which assume an account the owner knowingly created) and from KOL/invoice mail. Rule: when a signup/welcome confirmation email arrives for a service the owner did not knowingly register for, do not file it as a routine platform notification — surface immediately in ⚠️ Needs your action as a possible unauthorized-signup / account-security flag, recommending the owner check the account (and whether their email or password is exposed elsewhere) rather than waiting for the next patrol cycle. That same patrol otherwise repeated items already covered above and in Day 34's entry (the newly-surfaced high-value invoice, the bank-transfer and Stripe invoices pending amount confirmation, and the oldest pending invoice now well past 48h) — only the signup-confirmation item was new.

**Day 34 (2026-07-25 → 2026-07-26):**

Automation backlog produces duplicate DM reports (new failure mode): The 3-hour Gmail patrol automation queued roughly 15 consecutive fired triggers without executing — about 42 hours, spanning most of two days — due to an automation-engine delay unrelated to Gmail credentials or the skill's own logic. When the engine caught up, at least three of the backlogged windows were picked up by separate concurrent sessions almost simultaneously, and two of them independently sent nearly-identical full patrol reports to the owner's DM about two minutes apart before either was aware of the other. A third session recognized the overlap and correctly withheld a near-duplicate DM, posting only an in-channel note instead. **Rule, corrected after group review — must run unconditionally, not gated behind backlog detection**: the original version of this rule only triggered the dedup check when a session detected a large gap between its trigger's fired-at time and its own actual start time (roughly an hour or more), treating that as the sole signal of a "backlogged/delayed run." That precondition is now known to be insufficient on its own: a confirmed same-fire, zero-lag concurrent-session incident (Core Operating Patterns §11, Mechanism 2) produced near-duplicate reports with **no backlog gap at all** — an on-time fire, multiple sessions, same cycle. A rule gated on backlog-lag detection would not have caught it, and did not catch it live. So: (a) check the configured report target — DM or channel, whichever the owner set up during onboarding — for an equivalent report sent in the last ~15 minutes, **on every report attempt, regardless of whether this session judges itself to be on-time or backlogged**; (b) if one exists and its conclusions (drafts, invoices, unreplied items) match this session's independent findings, skip the DM send and post an in-channel note referencing the seq of the report that already covers it, instead of sending a duplicate DM; (c) if genuinely new information exists beyond what's already reported, send only the delta. This prevents report spam both when the automation engine falls behind and catches up in a burst, and when a single on-time fire spawns more than one concurrent session (§11, Mechanism 2) — the backlog-lag framing above is kept as one *example* of when this matters, not the trigger condition for running the check at all.

**Why ~15 minutes, specifically (revised after group review)**: the only in-regime observation is this incident's own duplicate-DM gap — the two sessions that both sent full reports were about ~2 minutes apart (n=1) — a direct measurement of the exact quantity this window governs (spacing between two independent sessions' reports about the same backlogged window). The asymmetry that justifies rounding up from that single data point to 15 minutes: a window too short risks the duplicate-DM failure that already happened once; a window too long risks silently absorbing a report that should have gone out, but that long-window cost is only *nominally* bounded by rule (c) above — nominally, because (c) is a written instruction with a confirmed real-world instance only of its sibling branch (b) (the third session's skip-and-note), not of (c)'s own delta-send behavior, and because none of this rule currently lives in the automation's actual runtime procedure document (see §11) — so treat the long-window backstop as designed, not battle-tested. **15 minutes is therefore a deliberately wide, uncalibrated guard, not a measured margin.**

(An earlier draft of this rationale cited the patrol's steady-state fire→completion timing — median ~4 minutes across 12 paired samples, max 6m34s — as a "~2x measured margin." That comparison is retracted: the fire→completion sample can only include runs that produced a pairable completion, which structurally excludes exactly the backlog/dead-window runs this rule exists to handle. Citing it as support was using a distribution that excludes the target scenario by construction to vouch for a constant meant to cover that scenario — worse than leaving the constant unjustified, since it reads as verified when it isn't.)

**Distinct from another same-valued constant discussed the same night**: this ~15-minute window governs spacing between two independent sessions' *reports*, not the draft classifier's separate on-cadence window used elsewhere in this investigation — same numeral, different mechanism, different purpose. Don't let a finding about one weaken or strengthen the other.

Note: not every backlogged window from this incident had been processed as of this nightly review — a few more patrol messages may still land as the remaining backlog clears; that's expected catch-up behavior, not a new problem, as long as the dedup rule above is applied each time.

Repeated invoice-log writes from a never-marked-read email (root cause identified): Several already-paid invoices kept reappearing in invoice_log.csv across multiple patrols — a symptom noticed informally on earlier days but not previously root-caused. Cause: the patrol's email fetch only pulls unread messages; if a processed email is never explicitly marked read, it resurfaces as "new" in every subsequent fetch, so a payment-confirmation email already logged once can trigger a fresh save-invoice call each time it's re-encountered — duplicating the same invoice many times over. Rule: before calling save-invoice for a payment confirmation, check the full invoice_log.csv (or Notion) — not a recent-window slice, the whole log — for an existing entry matching the same invoice number and sender; if no invoice number is present, match on message ID instead. Skip the write if a match is found. Longer-term fix (not yet implemented): mark processed emails as read, or otherwise track processed-message IDs, after handling them, so they stop resurfacing in the unread-only fetch. Until that's built, the pre-write duplicate check is the safeguard.

Day 33 patterns reconfirmed: the integration-slot-loss escalation and PayPal-UK trusted-sender rules both fired correctly again today on continuing threads — no changes needed.

Addendum (second concurrent nightly-review session, same Day 34 backlog): This automation itself was caught in the same engine-delay incident described above — tonight's trigger was ~21h late — and two separate review sessions worked the backlog in parallel. Per the dedup rule this file already gained above, this session skipped re-posting a duplicate [skill-update] and instead folds in only what the other session's pass missed:
- **PayPal Invoice 待支付汇总 automation was silently broken for 8 straight days (7/18–7/25):** its procedure document was completely empty, so every scheduled run posted a "doc is empty, skipping" warning into its own automation channel and stopped — the warning never escalated beyond that channel, so it went unaddressed through 6+ repeats. Rule: when an owned automation reports "procedure doc empty" on 2+ consecutive days and the intended behavior is already specified elsewhere (here: Step 4 / Automation C in this file's onboarding wizard), don't keep re-posting the same warning into a channel no one reads — seed the document from the known spec directly, or escalate to the owner in DM. Fixed tonight: seeded the live invoice automation's procedure doc with the full scan/dedup/report spec (including the invoice-log dedup guard from the rule above, applied by invoice number / message ID rather than read/unread state). First live run is the next scheduled fire.
- **KOL Notion field-name mismatch — recurring, still unresolved:** the KOL price scan procedure has referenced `达人价格` field + `待回复` status since at least Jul 22, but the live Notion KOL database actually uses `CPM` for price and 确认合作/推进中/脚本1/已发布 for status. This has surfaced as a "standing note" in multiple scan reports without ever being corrected in the procedure doc or the Notion schema — same shape as the PayPal gap above (a known fix that only ever lives in recurring report text). Escalating directly to Yori tonight instead of letting a scan report re-flag it a further time.
- **Stale channel reference in this automation's own procedure doc:** the document driving this nightly review still said "#yoris_friends" — a channel that was renamed to #gtm_friends back on Day 2 (2026-06-24) per this file's own Communication Rules. Corrected in the automation's own procedure doc tonight; had no practical effect since the post target was already resolved to #gtm_friends by convention, but would have broken a literal reading of the procedure.

**Day 33 (2026-07-24 → 2026-07-25):**

Integration slot loss due to script approval delay (new escalation type): A KOL media agency sent a follow-up email to both the team's public inbox and Yori's direct email after 3 days of unanswered script approval requests. By the time the message arrived, the original video had been published without the integration — the topic was time-sensitive and the partner's producer could not hold it further. The partner remains willing to proceed, offering to move the integration to an upcoming video. Rule: when a partner's follow-up states the original video has been published without the ad placement due to non-response, classify as "integration slot expired — script approval window missed." Surface immediately in ⚠️ Needs your action as: "Integration slot lost — [KOL partner], video published without ad placement. Partner still interested; align on next video slot. Day N since script draft shared." Draft a re-engagement reply that: (a) acknowledges the communication gap without deflection, (b) confirms continued interest in the partnership, (c) asks for upcoming video topics and schedule. Escalation signal: when a partner also contacts the team public inbox (distinct from Yori's direct email), treat as an elevated urgency marker on top of the standard follow-up cadence. Distinct from Day 32 persistent-unreplied-partner rule: here the consequence is irreversible (the original slot is gone), and the partner has already taken a self-protective action by releasing without the integration.

PayPal "updated invoice" as a notification subtype: A PayPal notification arrived with subject format "[Vendor] has updated your invoice ([invoice number])," indicating the vendor changed the invoice after initial issuance (possible: amount correction, due date change, or item description update). Rule: when a PayPal notification subject includes "has updated your invoice," do not create a new Notion entry. Instead: (a) look up the existing Notion entry by invoice number; (b) if found, add a note "invoice updated [date], re-check amount/details"; (c) if not previously logged, create a new entry using the original issue date (often parseable from the invoice number format). The update action signals the vendor is actively monitoring; apply the standard overdue timeline from the original invoice date, not the update date. At 15+ days from original issuance with an update arriving, treat as overdue — escalate per Day 21 thresholds.

PayPal UK as a third trusted PayPal sender domain: An invoice arrived via service@paypal.co.uk — the UK-region PayPal system sender — alongside the previously established service@paypal.com (US) and service@intl.paypal.com (international). All three are trusted PayPal delivery paths and receive identical treatment: log vendor name from the email body, invoice number, and amount; apply standard invoice tracking. Both service@intl.paypal.com and service@paypal.co.uk are now added to the trusted PayPal sender whitelist and to the pre-publish email scan whitelist. The Day 27 rule applies equally to all PayPal regional domains: the account email in the PayPal footer is not a domain-mismatch flag — PayPal routes invoices through its own domain regardless of the sender's registered email address.

GoogleImageProxy scan on 49-day-old email (Day 20 rule reconfirmed): A GMass open notification arrived for an outbound email sent 49 days prior, with a GoogleImageProxy User Agent and a Google-range IP (66.249.x.x). Discarded as a false positive per the Day 20 rule. Confirms: the false-positive discard rule has no email-age expiry — Google's image proxy can resurface and scan outbound emails weeks or months after the original send. Always discard on GoogleImageProxy UA or Google IP match, regardless of how old the email is. Day 20 remains the governing rule; no separate rule change needed.

**Day 32 (2026-07-23 → 2026-07-24):**

Pre-reply open burst — distinct from warm-signal burst: A KOL creator sent a follow-up email, and GMass simultaneously surfaced 4 rapid open notifications within a 22-second window (browser: Firefox, Unknown location). These are genuine human opens (no GoogleImageProxy UA, not Google IP range), but they coincide with the exact moment the partner composed and sent their message — the contact opened the email to read context while drafting their reply. Rule: when an open burst (3+ opens within 30 seconds) arrives within 60 seconds of an actual reply from the same contact, classify as "pre-reply reads" — genuine opens that count toward totals, but not a separate warm-signal event. Do not surface the opens as a warm signal in the patrol report when the associated reply is already there. The burst and the reply are one event. This is distinct from the Day 24 active-review burst (which predicts a reply about to arrive) — here the reply has already arrived.

Persistent unreplied partner (new escalation class): A KOL creator who responded positively to outreach on Day 1 sent their 4th email (3 follow-ups) over 49 days with no outbound reply visible in our sent folder. Current rules track aging of items we're waiting on; this is the reverse — a willing creator escalating follow-ups while we're silent. Rule: during each patrol, check KOL inbound threads for cases where the partner has sent 3+ emails with no matching sent reply from us (verify via thread sent-message presence). Surface as "persistent unreplied partner — [N] follow-ups, Day [X] since first reply" in ⚠️ Needs your action. Include original context (their first reply date, what they offered). Suggested action at 3+ follow-ups: if still interested, draft a reply acknowledging the gap and re-engaging; if moving on, a brief decline is cleaner than continued silence and protects sender reputation. Silence past 3+ partner follow-ups is both a relationship risk and a reputation signal to the creator community.

Google Cloud compliance notification — surface, don't skip: A Google Cloud notification arrived with subject "[Action Required] Enable 2-step verification to maintain your access to the Google Cloud console." This is distinct from routine Google product notifications (Workspace, Calendar, Drive, Search Console crawl/feature alerts) which auto-skip. Rule: Google Cloud security and compliance notifications with "[Action Required]" or "[Action Needed]" bracket phrase in the subject should be surfaced in ⚠️ Needs your action, not auto-skipped. The bracket phrase is the distinguishing signal — routine Google Cloud billing summaries and feature announcements (no bracket phrase) continue to auto-skip. The Vercel 2SV security sequence (Day 22) established the precedent for bracket-phrase security emails; this extends it to Google Cloud platform compliance.

**Day 31 (2026-07-22 → 2026-07-23):**

Promo code collision (new email type): A product partner reported that a promo code provided to them was invalid, with an error suggesting it had already been redeemed by a different account email. Investigation revealed the same code appeared to be consumed by a conflicting registration. Rule: when a KOL or product partner reports a promo code as invalid, do not immediately assume a technical error — check whether the code may have been claimed by another account first. Log: the code reference, the email address the partner used to register, and the error symptom. Escalate to Yori as "promo code conflict — requires new code or manual account upgrade." Do not auto-promise a replacement code. File under ⚠️ Needs your action. This is distinct from a general product support request — it involves Yori's KOL relationship and requires a manual resolution path.

Payoneer as third trusted payment platform path: An invoice arrived via Payoneer (sender: *@payoneer.com), the first Payoneer-routed payment request encountered. It carried a specific due date and a freelancing job reference number (format: "Freelancing #XXXXXX"). Rule: treat Payoneer invoices where the sender domain is payoneer.com as a trusted platform delivery path, alongside PayPal (service@paypal.com) and Stripe (invoice+statements+acct_*@stripe.com). Extract: vendor name, job reference number, amount, due date. If the due date is today or past at first detection, flag immediately in the current patrol — do not defer to the next window. Payoneer uses a freelancing job reference format rather than an INV- prefix; log accordingly. Add *@payoneer.com to the pre-publish scan sender whitelist.

Social media mock report — refined workflow: Yori requested a de-identified, fictional version of a patrol report for social media to demonstrate the product's value. Two feedback points from this first iteration: (1) "这个不要发" — strip the disclaimer header entirely; deliver the report format directly, no preamble. (2) "这些都请带上更大更夸张的数据" — when Yori requests bigger numbers for social media, apply visually impressive but obviously fictional figures (e.g., a modest milestone metric → a large round number in the thousands). Rule: when Yori asks to mock a patrol report for social media, always: (a) omit the disclaimer header — open directly with the report block; (b) replace modest real-adjacent figures with clearly exaggerated fictional ones for demo impact; (c) apply full privacy anonymization — real names → fictional names, emails removed, companies genericized, links removed; (d) send to DM only for Yori to copy-paste manually — never post directly to any channel. Truthfulness guard: because rule (a) omits the disclaimer header from the report block itself, the post or caption Yori wraps around the block on social media must clearly label the content as a demo, mock, or clearly fictional scenario — e.g. "Here's what a report looks like (fictional data for demo purposes)" — so the block cannot be read as genuine performance claims when published. If the surrounding post or caption does not carry that label, the mock report must include the disclaimer header regardless of rule (a). A social-media mock is a demo artifact; it may contain exaggerated data that does not reflect actual performance.

Multiple PayPal payment confirmations closed in same patrol window (confirmed again): Two payment confirmations arrived from two different vendors in the same patrol cycle, both closed in the same pass. Existing rule confirmed (previously Day 9, Day 18): log each independently with vendor, reference number, and closed status. No special handling needed. This is now a routine occurrence as the KOL program scales.

B2B meeting request carry-over (Day 3): The in-person meeting request with a travel window starting within about a week was re-surfaced in every patrol today per the Day 30 daily-escalation rule. No confirmation from Yori that a reply was sent. Countdown until first travel day is running; the window is now very close. Daily escalation with countdown is working as designed.

**Day 30 (2026-07-21 → 2026-07-22):**

"Finance team" intermediate payment status (publish-gate invoice): A video content creator had their invoice acknowledged 6 days after receipt, with Yori replying explicitly that the invoice was received and has been forwarded to a finance team for processing. This creates a new tracking state between "invoice received, no response" and "paid — PayPal confirmation." Rule: when a partner's invoice receives an acknowledgement that explicitly states it is being forwarded to a finance team, log status as "acknowledged — in finance queue, Day N from invoice date." If no PayPal payment confirmation arrives within 72h of that acknowledgement, re-flag as "finance queue, still pending — Yori acknowledged [date], [N] days since." The publish gate (when content is ready and awaiting payment to go live) remains active throughout the finance-queue period — finance-team forwarding is not payment.

Twitter/X collaboration invoice via PayPal: A PayPal-routed invoice for a Twitter (X) collaboration arrived via service@paypal.com — same trusted delivery path as all prior YouTube-collab PayPal invoices. Existing rule confirmed to cover Twitter/X platform collabs without modification. Log with platform noted alongside sender and amount in Notion. No new rule needed.

B2B in-person meeting request — daily escalation until response confirmed: An executive's in-person meeting request (travel window approximately 8 days out) arrived on Day 29 and remained unanswered on Day 30. Extension to Day 29 rule: once a high-priority B2B meeting request with a travel window is flagged in ⚠️ Needs your action, re-surface it in every patrol report until Yori confirms a reply was sent — not only on first mention. Include countdown: "[X] days until first travel date, response pending." A one-time mention on the day of arrival is insufficient when the external deadline is hard and approaching.

**Day 29 (2026-07-20 → 2026-07-21):**

GoogleImageProxy multi-pass scan (same email, hours apart): Four GMass open notifications arrived for the same outbound campaign to a tech creator inbox — one at 15:28 UTC and a burst of three at 20:14–20:15 UTC (4h46m later). The 15:28 notification confirmed UA `Mozilla/5.0 (Windows NT 5.1; rv:11.0) Gecko Firefox/11.0 (via ggpht.com GoogleImageProxy)` and IP 74.125.209.167 (Google range). All four are GoogleImageProxy false positives. New rule: Google's Image Proxy can scan the same email multiple times across separate passes hours apart — it is not restricted to tight time clusters. When applying the GoogleImageProxy false-positive filter, check ALL GMass open notifications for a given recipient/campaign across the entire patrol day, not just within a short window. Any notification matching the GoogleImageProxy UA from a Google IP (66.249.x.x or 74.125.x.x range) for the same recipient should be discarded regardless of time gap from other notifications. Zero genuine opens for the recipient on Day 29.

Bank-transfer invoice as new payment path (peer-sent via personal email): An X creator sent an invoice from their personal Gmail address with bank transfer details in the body (not via PayPal or Stripe) and an X.com post link as work-completion proof. This is a new invoice delivery path — creator's own Gmail → bank details inline → social post as proof. Rule: when an invoice arrives from a creator's personal email with bank transfer instructions and a social post as proof: (1) verify the X.com post is live and matches the agreed scope; (2) flag for Yori as "new payment method: bank transfer — confirm before payment" — do not initiate bank transfer without explicit Yori approval; (3) log in Notion as "bank-transfer invoice, pending Yori confirmation." This is distinct from PayPal-routed (service@paypal.com) and Stripe-routed (invoice+statements+acct_*@stripe.com) paths; those platforms handle identity verification — a peer bank invoice does not.

In-person B2B meeting request (travel-window deadline): An executive at a credible AI company emailed to propose an in-person meeting during a specific multi-day travel window. This is a new email type distinct from: enterprise accelerator invitations (Day 26 — remote platform credits), OSS credits requests (Day 23 — async), and KOL collabs. Key characteristic: the travel window creates a hard external deadline — no response before the first travel day means the meeting window closes entirely. Rule: classify in-person meeting requests from named executives at credible companies with a stated travel itinerary as high-priority B2B lead items. Surface in ⚠️ Needs your action with the travel window prominently. Draft: offer a specific time slot within their window or request their calendar availability. Respond before the first day of their travel window. This is not the same urgency class as a publication-gated invoice — no money is at stake — but the window is real and irreversible.

Fast invoice-to-payment turnaround confirmed (same-day): An X collab invoice arrived and was paid same-day (~12-hour turnaround). A second vendor invoice was paid within 2 days. Two PayPal payment confirmations arrived within 1 minute of each other (consecutive payments from Yori). Existing rule confirmed at same-minute resolution: multiple payment confirmations arriving in the same patrol window are independent events; log each separately. No new rule needed. Day count for both: closed in current cycle.

Post-agreement reactivation signal confirmed (42 days): A prior agreed KOL collab thread re-opened the original outreach email on Day 29, 42 days after the last substantive exchange (Yori had agreed to a 60–90s integration format). This is consistent with the Day 24 post-agreement reactivation pattern (30+ days post-agreement silence, re-open = lingering interest). No new rule; Day 24 pattern confirmed for the 40–45 day silence range.

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

skill ≠ install-time wizard (full team, 2026-06-30, seq 616–626): This skill file is a passive capability doc. When a new user installs it, nothing fires automatically — no heliox commands, no connect links, no schedule creation. The First-Run Setup wizard in this file only runs if the runtime emits a `skill:install` wake event (a platform-level gap as of 2026-06-30). Until that hook exists, users must explicitly ask to be guided through setup. Do not claim the skill guides users "from 0 to 1 automatically."

**Day 9 (2026-06-29):**

Cross-batch KOL duplication: same KOL contact appeared in two separate reply threads because they were included in two different outreach batches. Different from the June 24 triple-send (same email fired 3x from one batch). Fix: deduplicate email addresses across *all prior batches* before starting any new batch, not just within the current one.

PDF rate cards: one partner sent pricing exclusively inside a PDF attachment. Script cannot extract PDF content. When replying with a counter-offer, use flexible phrasing ("We typically budget in the mid-range for channels at your size") rather than an exact counter. Flag in patrol report that attachment was unreadable so Yori can open manually if needed.

Multiple PayPal confirmations per patrol: two payment confirmations landed in the same window from different vendors. Normal — log each individually with INV number and vendor. No special handling needed.

Notion @mention burst: Notion sent 8+ rapid-fire notification emails for a single Notion thread update (GTM tracking doc). Auto-skip confirmed correct. No need to surface individual @mention emails in DM — only surface if the body contains an actual task or question directed at Yori (not just "@yorihan" auto-notify).

OAuth token expiry cascade: Gmail MCP token expired and blocked three consecutive patrols. When token expires: skip the patrol, DM Yori immediately and send a new connect link via `heliox tool google auth`. Do not silently skip without notifying.

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
