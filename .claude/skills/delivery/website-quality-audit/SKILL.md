---
name: bpt-website-quality-audit
description: Strategic website quality audit with iterative checkpoints. Identifies problem areas, analyzes impact, and creates a 6-month implementation plan.
---

# Website Quality Audit (WQA) — v3.2

Comprehensive page-level website audit that pulls Ahrefs + GSC + GA4 + crawl data, classifies every URL into Technical and Content workstreams, surfaces missing on-page elements + thin content + depth gaps + striking-distance opportunities, scores link-building targets, and turns the whole thing into a strategist-approved 6-month implementation plan.

The skill produces deliverables in this exact order:

1. **Audit spreadsheet** (xlsx) — the master artifact. 7 tabs covering every URL, every recommendation, every keyword, and a scored link-building roster.
2. **Approval review** — the human-in-the-loop step where the strategist confirms, edits, rejects, or defers each recommendation AND approves the link-building roster.
3. **Visual report** (HTML) — branded client-facing report with 5 title-slide sections, generated *only after* approvals are parsed and confirmed.
4. **Implementation plan** — embedded in the report as a 6-month rolling schedule across Technical, Content, and Link-building sprints, generated from the approved items + capacity assumptions.

Each handoff requires explicit user confirmation before the next phase runs.

---

## Data Source Routing (22 Local Marketing override)

This workspace routes data through **Composio** and direct MCP integrations, NOT the extension's built-in Windsor/Ahrefs fetch (those are broken or unconnected). Use these routes for every data pull in Phase 1. Always pass EXPLICIT `YYYY-MM-DD` dates — the connectors default to a wrong system clock and silently return stale or empty data otherwise.

- **Google Search Console** → Composio tool `GOOGLE_SEARCH_CONSOLE_SEARCH_ANALYTICS_QUERY`. Args: `site_url` = `client.gsc_property` (e.g. `sc-domain:example.com`), `start_date`, `end_date`, `dimensions` (`["page"]` for per-URL, `["query"]` for keywords, `["date"]` for the time-series), `row_limit` up to 25000. Verified working.
- **Google Analytics (GA4)** → Composio tool `GOOGLE_ANALYTICS_RUN_REPORT`. Args: `property` = `properties/{client.ga4_property_id}`, `dateRanges` = `[{"startDate":...,"endDate":...}]`, `dimensions` (e.g. `[{"name":"pagePath"}]`), `metrics` (e.g. `[{"name":"sessions"},{"name":"totalUsers"},{"name":"engagementRate"},{"name":"keyEvents"}]`). Prefix the site host to `pagePath` to build the full URL used as the join key. **If it returns HTTP 403 (property not shared with the connected Composio Google account), fall back to the Pipedream tool `google_analytics-run-report-in-ga4`** — pass an explicit date range and use the GA4 tool, never the GA3 `run-report`.
- **Local Falcon** (local grid / SoLV / competitors) → Local Falcon MCP (`listLocalFalconScanReports`, `getLocalFalconReport`, etc.). NOT in Composio — keep this route.
- **Google Business Profile** (reviews / posts / profile insights) → Pipedream `google_my_business-*` and/or Local Falcon. NOT in Composio — keep this route.
- **Ahrefs** (keywords / backlinks / top pages) → currently UNAVAILABLE: the extension's `ahrefs_*` tools are bugged (`missing argument 'select'`/`'date'`) and Ahrefs is not connected in Composio. Treat keyword/backlink data as **optional** — do not block the audit on it. (`dataforseo` is connected in Composio as a possible future substitute.)
- **Screaming Frog crawl** → Screaming Frog MCP (unchanged; still the source of truth for per-page on-page data).

Write each pull to the exact output filename the Phase 2 scripts expect (see the Phase 1.2 table). The scripts don't care which tool produced the file, only that the schema matches.

---

## Phase 0: Pre-Flight Check

Verify two things before doing anything else. If either is missing, halt with a clear message and do NOT proceed.

### 0.1 Client record + agency profile

| Property | Location | Used for |
|----------|----------|----------|
| `vertical` | `client.vertical` | Page-type classifier |
| `ga4_property_id` | `client.ga4_property_id` | Per-URL traffic |
| `gsc_property` | `client.gsc_property` | Impressions, clicks, position, CTR |
| Ahrefs target | `client.custom_fields.ahrefs_target` | Keywords + backlinks (NOT a crawl substitute) |
| Competitor list | `client.custom_fields.competitors` (array) | Competitor data pulls (Phase 1.5) |
| Windsor accounts | `client.custom_fields.windsor_accounts.{ga4,gsc}` | Monthly time-series + period comparison |
| `agency.branding` | `agency.branding.*` | Report styling (falls back to defaults) |

Branding is optional. Everything else blocks.

### 0.2 Screaming Frog crawl — HARD PREREQUISITE

**An SF crawl is the source of truth for all per-page on-page data:** title, meta description, H1, word count, inlinks, outlinks, crawl depth, indexability, canonical, status codes. **Ahrefs does NOT substitute for this.** The site-audit endpoint requires a separately-run Ahrefs Site Audit crawl that often isn't current, and `site-explorer-crawled-pages` returns only URL/status/title with no on-page content fields.

**Before any data pulls, verify** that the file exists at:

```
clients/{client-folder-slug}/crawls/latest-crawl.json
```

with at least 10 pages of data.

**If missing, halt immediately** with this message to the user:

> WQA cannot run without a Screaming Frog crawl. SF is the source of truth for per-page title, meta, H1, word count, inlinks, outlinks, and crawl depth. Ahrefs is used for keywords and backlinks only — not as a substitute.
>
> To proceed:
> 1. Run Screaming Frog SEO Spider against the client's domain.
> 2. Export the Internal HTML report (Internal > HTML).
> 3. Run `wqa_upload_crawl` OR drop the CSV into `clients/{slug}/crawls/`.
> 4. Re-run this skill.

Do NOT proceed with partial-data fallbacks. Surface the requirement clearly and wait.

---

## Phase 1: Data Collection

**Goal:** Pull every data source into the audit folder so the xlsx builder has what it needs.

### 1.1 Create the audit workspace

```
wqa_create_audit { client_id, notes }
```

Returns `audit_id` and creates the folder:

```
clients/{client-folder-slug}/wqa/audits/{audit_id}/
```

Note: the **client folder slug** (e.g. `the-blueprint-training`) may differ from the **file-prefix slug** used in output filenames (e.g. `tbt`). Scripts accept both via `--client-slug` (file prefix) and `--audit-dir` (full path to the audit folder).

### 1.2 Pull data from connected sources

Run these in parallel where possible. All save to the audit folder.

| Source | Tool (22LM routing — see Data Source Routing above) | Output file |
|--------|------|-------------|
| Screaming Frog crawl | Screaming Frog MCP — Internal:All export (Address, Title, Meta Description, H1, Word Count, Status Code, Indexability, Canonical, Crawl Depth, Inlinks, Outlinks, Redirect URL) | `clients/{slug}/crawls/latest-crawl.json` |
| GSC per-URL (current 90d) | Composio `GOOGLE_SEARCH_CONSOLE_SEARCH_ANALYTICS_QUERY` — `site_url`=client.gsc_property, `dimensions`=`["page"]`, explicit dates | `{slug}-gsc.json` — list of `{page,clicks,impressions,position}` |
| GSC per-URL (prior 90d, for Δ) | same, prior-90d range | `{slug}-gsc-90d-prior.json` — `{by_page:{url:{clicks,impressions,position,ctr}}}` |
| GSC monthly time-series (16 mo) | same, `dimensions`=`["date"]` | `{slug}-gsc-monthly.json` |
| GA4 per-URL (current 90d) | Composio `GOOGLE_ANALYTICS_RUN_REPORT` — `property`=properties/{ga4_property_id}, `dimensions`=`[{"name":"pagePath"}]`, `metrics`=sessions/totalUsers/engagementRate/keyEvents; prefix host to pagePath. **403 → Pipedream `google_analytics-run-report-in-ga4` fallback** | `{slug}-ga4.json` — list of `{page_location,sessions,users,engagement_rate,conversions}` |
| GA4 per-URL (prior 90d, optional) | same, prior-90d range | `{slug}-ga4-90d-prior.json` |
| GA4 monthly (organic + total) | same, `dimensions`=`[{"name":"yearMonth"},{"name":"sessionDefaultChannelGroup"}]`, metric sessions | `{slug}-ga4-monthly.json` |
| Ahrefs (keywords / backlinks / top pages) | OPTIONAL — `ahrefs_*` bugged + not in Composio; skip until fixed. Files may be absent. | `{slug}-ahrefs*.json` |

**Aggregation note:** GA4 and GSC both return multiple rows per page (one per source/medium/query/etc). The xlsx builder **sums** by normalized URL — do not use last-wins joins, you'll drop 90%+ of homepage traffic.

### 1.3 Discover legacy URLs + redirect targets

For URLs in GSC that aren't in the current crawl, HEAD-fetch to determine status (200/3xx/4xx) and redirect target. Save to `{slug}-legacy-urls.json` and `{slug}-redirect-targets.json`.

Reference implementation: `scripts/discover_redirects.py`.

---

## Phase 2: Generate Audit Spreadsheet (FIRST OUTPUT)

**Goal:** Produce a single xlsx that the strategist reviews and approves from.

Run the builder:

```bash
python3 scripts/build_audit_xlsx.py \
  --client-slug {file-prefix} \
  --audit-dir {full-audit-folder-path} \
  --root-domain https://{client-domain}
```

The xlsx is written to:

```
clients/{client-folder}/wqa/audits/{audit_id}/{slug}-wqa-data.xlsx
```

### Tabs (final order — 4 tabs total)

1. **Aggregator** — every URL with full data. **First 6 columns frozen** (Technical Action · Content Action · Priority · Sprint · Address · Page Type). Layout:
   - **Technical Action** (col A, dropdown): Fix 404 · 301 redirect · Evaluate redirect · Add canonical · Add schema · Noindex · Update robots · Indexability fix · Sitemap fix · Monitor · Leave as is
   - **Content Action** (col B, dropdown): Rewrite · Rewrite title/meta · Expand content · Refresh content · Update onpage · Consolidate · Evaluate · Leave as is
   - **Priority** (col C, dropdown P1/P2/P3)
   - **Sprint** (col D, dropdown): Sprint 1 (Planning) · Sprint 2 (Technical) · Sprint 3 (Local) · Sprint 4 (Content) · Sprint 5 (Links) · Backlog · Done
   - **Address** (col E, hyperlink to full URL)
   - **Page Type** (col F, fill-coded)
   - Then unfrozen: Status · Status Type · Redirect Target (populated from SF crawl's Redirect URL) · Funnel Stage · Indexable · Title (+ length) · Meta Description (+ length) · H1 · Word Count · Crawl Depth · Inlinks
   - **GA4 (90d) block**: Sessions · Sessions Δ · Users · Users Δ · Eng % · Conversions · Conv Δ — Δ cells get green/red conditional fills vs prior 90 days
   - **GSC (90d) block**: Clicks · Clicks Δ · Impressions · Imp Δ · CTR · CTR Δ
   - Then: Total KWs Ranking · Top Keyword · Top KW Vol · Top KW Pos · Ref Domains · URL Rating · Problem Areas · Action Notes
   - Each row can carry one or both actions; whichever is the highest-priority finding from the detector populates the cells.
   - **Strategist edits here are authoritative** — see Phase 3 below for how parse_approvals propagates them.

2. **Recommendations** — project-plan-style matrix, 8 columns. No column freeze. Auto-filter explicitly bounded to A1:H so extras don't bleed into I-Z. Columns: # · **Approval** · Priority · **Category** (Technical/Content) · Sprint · Action Type · Page Address · **Specific Next Step**.
   - **One row per (page × finding)**. A page with three issues (missing meta + missing H1 + thin content) gets three separate rows.
   - **Edit the Specific Next Step inline** for any "Edit" approval — the parser diffs against the snapshot to detect changes.

3. **Keywords** — every ranking keyword with position color-coded (green ≤3, yellow ≤10, orange ≤20, red 21+). Includes volume, est. traffic, CPC, KW difficulty, intent flags, SERP features.

4. **Target Pages** — top 20 link-building roster. Strategist reviews and approves each. Columns: # · **Approval** · Page Address · Page Type · Target Keyword · KW Volume · Current Pos · Ref Domains · Word Count · GSC Impressions · Score · Approver Notes.

### Removed tabs

- **Notes** — removed; strategists use the Approver Notes column (or a separate doc) for free-form
- **Redirects** — removed; the Aggregator's Status Type column + Redirect Target column make this a filter, not a separate tab
- **Errors** — removed; same reason (filter Aggregator by Status Type = broken)
- **Action Plan** — removed; the Project Plan section of the visual report covers this

### Issue detection — what gets surfaced

The detector returns a list of findings per URL. Each finding becomes a Recommendation row.

**Technical findings:**
- 4xx with signal (impressions, backlinks, sessions) → Fix 404 · P1 if high-signal, P2 if some-signal, P3 monitor otherwise
- 3xx redirecting to homepage with signal → Evaluate redirect · P2
- WP auto-generated archives/feeds indexed without content (`/feed`, `/tag/`, `/category/`, `/trainings_cat/`, etc.) → Noindex · P2
- 3xx working as intended → Leave as is · P3

**Content findings (only flag if SF/site-audit has confirmed page data — prevents false positives on URLs Ahrefs/GSC know about but weren't crawled):**
- Missing title → Rewrite title/meta · P1 for money/authority/homepage, P2 elsewhere
- Missing meta description → Rewrite title/meta · P2/P3
- Missing H1 → Update onpage · P2/P3
- Thin content (<618w):
  - Money page → Rewrite · P1
  - Authority page → Rewrite · P2
  - Other → Expand content · P3
- Depth gap (618-1499w, targets a ≥500-volume KW, on money/blog/content/authority page) → Expand content · P2
- Low CTR (>1000 imp, CTR <2%) → Rewrite title/meta · P2
- Striking distance (pos 4-15 with ≥500 imp) → Update onpage · P2
- Stale blog heuristic — substantial blog post (≥1000w) stuck at pos 11-30 with ≥200 imp → Refresh content · P3. (This is a proxy for content age until we wire a `last_modified` data source.)

### Target Pages scoring

Live pages on the commercial side of the site, ranked by link-building value:

```
score = keyword_volume × position_multiplier × business_value_multiplier
```

- **business_value_multiplier**: Money Page 6.0× · Authority 1.8× · Content Hub 1.3× · Blog Post 1.0×
- **position_multiplier**: Top 3 = 0.7 (marginal lift) · 4-10 = 1.5 (best ROI) · 11-30 = 1.2 (achievable with links) · 31+ = 0.4 (likely content gap, not link gap)
- Excluded: homepage, utility pages, 404s, redirects, pages with no keyword signal

Take the top 20.

### Snapshot

When the xlsx is built, the script also writes `{slug}-wqa-recommendations-original.json` next to the xlsx. This is a snapshot of the original "Specific Next Step" text for every row, used later by the approval parser to detect edits.

### Formatting

- Arial 10 body, Arial 11 bold headers. Headers: white text on `#2563EB` blue fill.
- Body cells: overflow text (no wrap), middle vertical-aligned.
- Wrap only narrative columns: Aggregator → Meta Description, Action Notes · Recommendations → Specific Next Step, Current State, Target State, Why It Matters, Approver Notes · Notes → Note · Redirects/Errors → Notes · Target Pages → Approver Notes.
- Color coding: Action columns · Priority (P1 red / P2 orange / P3 yellow) · Status Type (live green / redirect yellow / broken red) · Page Type · Approval (Approved green / Edit yellow / Rejected red / Deferred blue).

---

## Phase 2.5: Publish workbook to Google Sheets + tie to client

**Goal:** turn the generated `{slug}-wqa-data.xlsx` into a **Google Sheet** the team can
review/sync and Claude can read, and **save its URL on the client** so every downstream
deliverable can link to it.

If a Google Drive MCP is connected and the client has a Drive folder
(`custom_fields.drive_folder_id`):

1. Create the workbook as a Google Sheet from the xlsx in the client's Drive folder, e.g.:
   ```
   mcp__claude_ai_Google_Drive__create_file
     name: "{Company} — WQA Workbook"
     parent: {client drive_folder_id}
     # upload {slug}-wqa-data.xlsx converting to a Google Sheet
     # (mimeType target: application/vnd.google-apps.spreadsheet)
   ```
   Capture the resulting share/`webViewLink` URL.

   > **Capability note:** if the connected Drive MCP can't upload+convert an xlsx, fall back to
   > (a) uploading the .xlsx to the Drive folder (still yields a URL), or (b) the manual
   > "File → Import" path below — then ask the user to paste the resulting Sheet URL. Either way,
   > finish by recording it in step 2.

2. Save it on the client (idempotent — re-running updates in place):
   ```
   client_resource_set { client_id, type: "wqa_workbook", label: "WQA Workbook", url: <sheet_url>, source: "wqa" }
   ```

If Drive isn't connected, skip creation and use the manual instruction in Checkpoint 1; you can
still record a pasted URL via `client_resource_set` later. The `wqa_workbook` resource then
appears on the client's Kickoff + Content deliverables in the Projects view.

---

## CHECKPOINT 1: Approval Review

**STOP and send this message to the user:**

> The audit workbook is ready. If Drive is connected it's now a Google Sheet on the client:
> **{wqa_workbook URL}** (also saved as a client resource). Otherwise open
> `clients/{slug}/wqa/audits/{audit_id}/{slug}-wqa-data.xlsx` and upload to Google Sheets
> (File → Import) — the dropdowns and color coding carry over.
>
> **Two tabs to review:**
>
> **Recommendations** — for each row, fill in the **Approval** column (col B):
> - **Approved** — build it as-written
> - **Edit** — edit the "Specific Next Step" cell inline, then mark Edit
> - **Rejected** — don't build it
> - **Deferred** — valid but next quarter (goes to backlog)
>
> **Target Pages** — same Approval dropdown on each of the top 20 link-building targets.
>
> Skim the **Aggregator** tab too — if you disagree with a Technical Action or Content Action in col A or B, flip it via the dropdown.
>
> When done: File → Download → .xlsx → save back to the same audit folder (overwrite the original). Then come back here and say "approvals done."

Wait for the user to confirm they've finished. Do NOT proceed without confirmation.

---

## Phase 3: Parse Approvals

**Goal:** Read the returned xlsx and produce a structured approval summary.

Run:

```bash
python3 scripts/parse_approvals.py \
  --client-slug {file-prefix} \
  --audit-dir {full-audit-folder-path} \
  --root-domain https://{client-domain}
```

The parser:

1. Loads the (now edited) `{slug}-wqa-data.xlsx`.
2. Reads every row of the Recommendations tab.
3. Compares each row's current "Specific Next Step" against the snapshot to detect edits.
4. **Reads the Aggregator tab as an override layer** — strategist edits to Technical Action / Content Action / Priority / Sprint on a URL are merged into the matching Recommendation row(s). Disambiguation rules:
   - **action_type override** only applies when the URL has exactly one Recommendation row in that category (else can't safely target which rec it modifies)
   - **priority + sprint override** only applies when all of that URL's Recommendation rows had the same value originally AND the Aggregator differs (else the variance signals the strategist didn't intend a uniform change)
   - Each applied override is logged on the row as `aggregator_overrides_applied: ["action_type: Rewrite → Refresh content", ...]`
5. Buckets rows by Approval status.
6. Reads the Target Pages tab and buckets those by Approval.
7. Writes a structured summary to `{slug}-approvals.json`.
8. **Writes the final xlsx back to the same path** — single source of truth:
   - Overridden cells in Recommendations highlighted **light blue**
   - Edited Specific Next Step cells highlighted **soft yellow**
   - A pinned **Audit Summary** tab at position 1 with totals, override count, last-parsed timestamp, and a legend explaining the cell colors

### What "Edit" means

For Edit rows, the parser takes whatever text is in the "Specific Next Step" cell as the new recommendation. The strategist makes edits inline in the spreadsheet — no conversational follow-up. The `original_text` field in the summary preserves the original wording.

### Approval summary presented to user

After parsing, show this table:

| Bucket | Recommendations | Target Pages | What happens |
|--------|----------------|--------------|--------------|
| Approved | n | n | Built as written |
| Edit | n | — | Uses your edited text |
| Rejected | n | n | Dropped |
| Deferred | n | n | Backlog |
| Unmarked | n | n | Blocks next phase |

If there are Unmarked rows, list them and ask for resolution.

---

## CHECKPOINT 2: Build Visual Report

**STOP and ask:**

> "Approvals are parsed: {n} approved, {n} edited, {n} rejected, {n} deferred. Target pages: {n} approved. Ready for me to build the visual report?"

Wait for explicit yes. Then run:

```bash
python3 scripts/build_report.py \
  --client-slug {file-prefix} \
  --audit-dir {full-audit-folder-path} \
  --root-domain https://{client-domain} \
  --client-name "{Client Display Name}" \
  --primary-color "#YourHex"   # optional, defaults to #2563EB
```

### Report structure — 5 title-slide sections

**Section 1 · Performance Metrics**
- At a glance: 8 KPIs (organic sessions, conversions, GSC clicks, impressions, CTR, avg position, indexable URLs, ranking keywords) — each with ▲/▼ % change vs prior 90 days
- Organic performance over time: monthly chart showing GA4 organic sessions + GSC clicks + GSC impressions (16-month GSC limit, GA4 goes as far back as the property has data)
- Performance by page type: pie chart (GSC clicks only) + accordion for each page type listing every page in that category
- Performance by funnel stage: pie chart (GSC clicks only)
- Top 15 keywords by traffic: keyword · intent · position · volume
- Striking distance opportunities: keyword → URL with trend arrows on position/imp/clicks/CTR

**Section 2 · Technical Improvements**
- Site health snapshot (status mix donut + top broken URLs by signal)
- Indexability + critical elements: KPIs (missing title / meta / H1 / thin pages) + indexability breakdown + crawl depth distribution
- Redirects analysis (specifically calls out redirects pointing to homepage — relevance leak)
- (No PSI panel — pending API access. No "Technical work this cycle" summary — full detail is in the Project Plan.)

**Section 3 · Content**
- Content depth overview: KPIs (live pages with content / avg word count / median / thin pages)
- Word count distribution: <300 · 300-617 · 618-1500 · 1500-3000 · 3000+
- Depth by page type: avg words and thin count per page type
- (No card list — full detail is in the Project Plan.)

**Section 4 · Links**
- Target pages — link-building roster (only Approved + Edit rows): #, page, page type, target keyword, KW vol, current pos, ref domains, score
- Backlink gap analysis: pending (next iteration pulls top 5 SERP + their referring domains per target page)

**Section 5 · Project Plan — 6-Month Implementation Plan**
- KPI header: Sprint 1 Technical count · Sprint 2 Content pieces + copywriting count · Sprint 3 Links (e.g. 36 links / 6 months / N pages) · Capacity assumed (8,000w/mo, 2,000w/piece avg)
- **Six monthly accordions** (Month 1 → Month 6, Month 1 expanded by default). Each header shows the load: "23 technical · 4 content (8,000w) · 10 copywriting · 6 links". Inside each month: the exact items grouped by type, each item is its own click-to-expand accordion with full detail.

### Scheduling logic for the 6-month plan

**Month 1 is reserved for Sprint 1 (Planning / WQA, in progress) + Sprint 2 (Technical fixes + analytics setup).** Content, copywriting, and link-building never run in Month 1 — there's not enough time after the audit finishes to also produce content or run outreach.

**Sprint 2 (Technical) — Month 1, overflow Month 2:**
- All technical items → Month 1
- If > 30 items, split evenly across Month 1 and Month 2

**Sprint 4 (Content) — Months 2-6 (5 months, 40K-word capacity):**
- Body content items (Rewrite, Expand content, Refresh content, Update onpage, Consolidate) fill months by word budget (8,000w/month). Word estimates per action: Rewrite 2,000w · Expand 1,500w · Refresh 1,000w · Update onpage 500w · Consolidate 1,500w.
- Copywriting tasks (Rewrite title/meta) — round-robin 10 per month, Months 2-6 (50 total).
- If total body workload exceeds 40,000 words, overflow stacks into Month 6 — strategist should rebalance by deferring P3 items.

**Sprint 5 (Link building) — Months 2-6 (5 months, 30 link slots):**
- 6 links/month × 5 months = 30 link slots distributed across approved target pages (top-ranked pages get the extras)
- Each link slot in the report expands to show the target page, target keyword, current position, current ref domains, score, and recommended tactic options.

### Brand styling

- Headers / titles / KPI values: **Bebas Neue**, uppercase, condensed.
- Body / tables / pills / paragraphs: **Figtree** (weights 300-800).
- Hero + title slides + sprint headers: deep ink (`#0a0e1a`) with a blue left-border accent.
- Primary accent color is the client's brand blue (defaults to `#2563EB`; pass `--primary-color` to override).
- Self-contained HTML, Chart.js + Google Fonts loaded from CDN.

When the report is built, **tie it to the client** so deliverables can link to it. If Drive is
connected, upload `{slug}-wqa-report.html` to the client's Drive folder and record the URL;
otherwise record the local path:

```
client_resource_set { client_id, type: "wqa_report", label: "WQA Report", url: <drive_url_or_path>, source: "wqa" }
```

Then **stop again** and wait for confirmation before the Agency OS project is created.

---

## CHECKPOINT 3: Create Agency OS Project

**STOP and ask:**

> "Visual report is at `{path}`. Ready to generate the 12-month project plan
> (sprints + deliverables) in Agency OS?"

Wait for explicit yes, then **hand off to `/bpt-project-plan`** — that skill owns
the plan generator (`build_project_plan.py`) and the `project_plan_import` step.
Keeping a single owner means the plan is generated by exactly one code path and is
never created twice.

Invoke `/bpt-project-plan` for this client; it will:
1. Read this audit's `{slug}-approvals.json`,
2. Generate the 12-month plan, passing **`--vertical`** from the client's
   `custom_fields.vertical` (Sprint 3 Local SEO is included only for `local_service`;
   other verticals suppress it and shift content up to Month 2). Sprints 1-6: Kickoff
   (WQA + Project Plan) / Technical / Local SEO / Content / Links / Reporting (Analytics
   Audit + monthly Client Check-ins + WQA Refreshes at M6/M12) — team-routed assignees,
3. **Present the plan as a month-by-month table in chat (Checkpoint 2.5)** for the
   strategist to review/edit before committing, then
4. Import it via `project_plan_import` (idempotent — re-running replaces the prior
   plan rather than duplicating it).

Rejected recommendations are not included; Deferred are left out of the active
schedule.

---

## Phase 4: Final Recap

Send a Slack + email recap with:

- Link to the xlsx
- Link to the visual report
- Project link in Agency OS
- Counts: approved / edited / rejected / deferred / total + target pages approved / total link slots

---

## Scripts Reference

All scripts live in `scripts/`:

| Script | Purpose |
|--------|---------|
| `build_audit_xlsx.py` | Build the 7-tab audit spreadsheet from pulled data. Multi-finding detector. Snapshots originals to JSON. |
| `discover_redirects.py` | HEAD-fetch legacy URLs to determine 200/3xx/4xx and redirect targets. |
| `parse_approvals.py` | Read the returned xlsx, diff against the snapshot, write approval summary JSON. Reads both Recommendations + Target Pages tabs. |
| `build_report.py` | Generate the branded HTML report with the 6-month implementation plan. |

The detailed 12-month project plan (sprints + deliverables) is generated by the
**`/bpt-project-plan`** skill (its `scripts/build_project_plan.py` + the
`project_plan_import` MCP tool) — invoked at Checkpoint 3 above.

---

## MCP Tools Reference

| Tool | Phase | Purpose |
|------|-------|---------|
| `wqa_create_audit` | 1 | Create audit workspace |
| `wqa_upload_crawl` | 1 | Upload Screaming Frog CSV |
| `wqa_get_audit_state` | Any | Check audit progress |
| `wqa_list_audits` | Any | List client audits |
| `wqa_update_patterns` | Any | Update URL patterns |
| `windsor_query` | 1 | Pull GA4 + GSC data (monthly time-series + 90d compares) |
| `ahrefs_*` (multiple) | 1 | Ahrefs site-audit + site-explorer + keywords pulls |

---

## Decision Points

**No SF crawl yet** → **HALT.** This is a hard prerequisite — see Phase 0.2. SF is the only reliable source for title, meta, H1, word count, inlinks, outlinks, and crawl depth at the per-page level. Ahrefs is for keywords + backlinks only. Tell the user to run an SF crawl with the Internal HTML export and drop it in `clients/{slug}/crawls/`. Do not attempt partial-data fallbacks.

**GSC API limit** → 16 months max. The Section 1 time-series chart will show GSC limited to 16 months and GA4 going further back (29+ months for properties with history).

**Large site (1,000+ pages)** → Aggregator can handle it. Recommendations tab will be large; the report's Project Plan accordions remain readable because items are collapsed by default.

**No last_modified column** → The stale-blog heuristic (mid-position substantial blog posts) approximates this. For a true date-based rule, re-export SF with the Last Modified column.

**Strategist disagrees with the auto-classification** → Override in the Aggregator tab via either action dropdown. The approval parser respects whatever's in the sheet.

---

## Tips

- Always pause at each checkpoint. The whole point of the v3 flow is human-in-the-loop, not Claude-decides-everything.
- Hand-curate the top 5-10 P1 recommendations with section-by-section outlines (proposed titles, target word counts, sections to add). Auto-generated rows are fine for everything else.
- Keep the Notes tab — strategists use it during the review to flag things they want to come back to.
- The Approval dropdown values are exactly: `Approved`, `Edit`, `Rejected`, `Deferred`. Don't add new values without updating `parse_approvals.py`.
- The two action columns on the Aggregator can BOTH be populated for a single URL — Technical and Content are separate workstreams.
- We don't work in hours. The report and spreadsheet talk in capacity units (pages, pieces, words, links) and months — never billable hours.

---

*Agency OS v1.3 — Blueprint Training One-Person Agency program*
