# 22 Local Marketing — Agency OS (customized)

> **Do not restore the stock heading.** This file is intentionally customized. The extension only overwrites a workspace `CLAUDE.md` whose first heading is exactly `# Agency OS Workspace`; because this one differs, extension updates will leave it alone. If you ever reinstall/rebuild the extension and it regenerates a stock file, re-apply the Data Source Routing block below.

Local-first agency management system. Visual dashboard at http://localhost:3001.

## Data Source Routing (CANONICAL — overrides any skill instructions)

When any Agency OS skill (WQA, proposal generator, project plan, onboarding, etc.) needs external data, use these routes. The extension's built-in Windsor/Ahrefs fetch is broken or unconnected in v1.4 — do NOT use it. **Always pass EXPLICIT `YYYY-MM-DD` dates** — the connectors default to a wrong system clock and silently return stale/empty data.

| Data | Route | Notes |
|------|-------|-------|
| **Google Search Console** | Composio `GOOGLE_SEARCH_CONSOLE_SEARCH_ANALYTICS_QUERY` | `site_url`=client.gsc_property; `dimensions` `["page"]` / `["query"]` / `["date"]`. Verified. |
| **Google Analytics (GA4)** | Composio `GOOGLE_ANALYTICS_RUN_REPORT` | `property`=`properties/{ga4_property_id}`; `dateRanges`; `dimensions` e.g. `[{"name":"pagePath"}]`; `metrics` sessions/totalUsers/engagementRate/keyEvents. The `connor@22localmarketing.com` Composio Google account is **admin on all 6 client GA4 properties**. Verified roster-wide. Any 403 → Pipedream `google_analytics-run-report-in-ga4` fallback. |
| **Local Falcon** (grid / SoLV / competitors) | Local Falcon MCP (`listLocalFalconScanReports` → `getLocalFalconReport`) | Not in Composio. |
| **Google Business Profile** (reviews / posts / insights) | Pipedream `google_my_business-*` and/or Local Falcon | Not in Composio. |
| **Ahrefs** (keywords / backlinks / DR) | UNAVAILABLE — extension `ahrefs_*` bugged + not in Composio | Treat as optional; `dataforseo` (in Composio) is a future substitute. |
| **Screaming Frog crawl** | Screaming Frog MCP | Source of truth for per-page on-page data. |

The WQA + proposal skill files carry the same routing block, but **this file is the durable source of truth** — skill files get overwritten on extension update; this one does not.

### GA4 property IDs (active roster)
Better Way `520284516` · TN Tree Preservation `479613721` · Fonville `487606539` · McQuillin `494312681` · Ranger `502336589` · Green Bear `510151433`.

## WQA Pipeline (owned, deterministic)

Data collection is owned by `C:\22 Local Marketing\agent\bpt\collect_data.py` — it pulls GA4 + GSC server-side with the Google refresh token and writes the exact files the WQA scripts read, so data never round-trips through the agent's context. Run order for a WQA:

1. **Crawl** (Screaming Frog MCP) → `clients/{slug}/crawls/latest-crawl.json`.
2. **Collect** GA4 + GSC (one call, returns a summary only):
   `python "C:\22 Local Marketing\agent\bpt\collect_data.py" --audit-dir <audit-dir> --slug <slug> --ga4-property <id> --gsc-site "sc-domain:<domain>" --root-domain https://<domain> --as-of <YYYY-MM-DD>`
   Writes `{slug}-gsc.json`, `-gsc-90d-prior.json`, `-gsc-monthly.json`, `-ga4.json`, `-ga4-monthly.json`.
3. **Build** with the stock scripts, always prefixed `PYTHONUTF8=1` (fixes the Windows cp1252 crash in build_report/parse_approvals/build_project_plan):
   `build_audit_xlsx.py` → approvals → `build_report.py` → `build_project_plan.py`.

**GA4 note:** `collect_data.py` GA4 needs the **GA4 Data API enabled** in Google Cloud project `846574421747` (the refresh-token project; GSC is already enabled there). Enabled + verified 2026-06-18. If a future client 403s, enable at console.cloud.google.com → APIs & Services, or fall back to Composio `GOOGLE_ANALYTICS_RUN_REPORT`.

## Proposal (owned, local-contractor)

`C:\22 Local Marketing\agent\bpt\build_proposal.py` renders a self-contained HTML proposal (Sora + Blaze) for local contractors. It ONLY includes data-backed sections (snapshot, organic trend, local map visibility, top pages, findings, 6-month plan, projection, team) — no Ahrefs / AI-screenshot / backlink / pricing slides, because Ahrefs is effectively blind to small local sites (2 keywords / 5 visits for these clients), so those slides can never fill. Use this, NOT the stock `proposal_*` extension tools, for client proposals.

Run after a WQA (reuses the collector's `{slug}-gsc.json`/`-ga4.json`/`-ga4-monthly.json`/`-gsc-monthly.json`):
```
python "C:\22 Local Marketing\agent\bpt\build_proposal.py" --audit-dir <audit-dir> --slug <slug> --client-name "<Name>" --location "<City, ST>" --root-domain https://<domain> --crawl clients/<slug>/crawls/latest-crawl.json --localfalcon <audit-dir>/<slug>-localfalcon.json
```
The `--localfalcon` JSON (grid + per-keyword SoLV + competitors) is produced from the Local Falcon MCP (`listLocalFalconScanReports` → `getLocalFalconReport`, extract `data_points` ranks + top competitors); omit the flag to skip the local section.

The `--ahrefs-audit` JSON adds an Ahrefs Site Audit section (health score + errors/warnings/notices + every present issue: oversized images, slow pages, schema validation errors, Open Graph gaps, mixed content, broken outbound links, etc. — complementary to the Screaming Frog crawl). Build it from the Ahrefs MCP: `site-audit-projects` (health_score + urls_with_errors/warnings/notices) → `site-audit-issues {project_id}` (keep issues where `crawled>0`: name, importance, category, crawled). **Ahrefs Site Audit project IDs:** Better Way `9764715` · Fonville `9764716` · Ranger `9764721` · McQuillin `9764722` · Green Bear `9764723` · TN Tree Preservation `9764724`.

---

## On Conversation Start

1. **Check setup status**: Read `data/agency.json` and `data/team.json`. If the agency profile is empty or has no owner, suggest `/agency-os-meta-workspace-setup`.
2. **Dashboard**: available at http://localhost:3001.
3. **If set up**: greet by agency name and give a brief status snapshot (active leads, clients, follow-ups due).

## Skills

| Skill | Description |
|-------|-------------|
| `/agency-os-meta-workspace-setup` | First-time setup wizard |
| `/agency-os-meta-doctor` | Diagnose connection issues |
| `/agency-os-sales-proposal-generator` | Generate proposals with competitive analysis |
| `/agency-os-delivery-client-onboarding` | Client onboarding workflow |
| `/agency-os-delivery-website-quality-audit` | Strategic website quality audit (xlsx → approvals → report → plan) |
| `/agency-os-productization-project-plan` | 12-month project plan from a completed WQA (or a template) |

## Quick Commands

**Sales:** "Show my pipeline summary" · "Create a lead for [company], contact [name] at [email]" · "List follow-ups due today"
**Clients & Projects:** "List my active clients" · "Create a client for [company]" · "Show active sprints"
**Agency:** "Show my agency profile" · "List team members"

## Data Storage

```
data/        agency.json · team.json · leads.json · clients.json · projects.json · sprints.json · deliverables.json
clients/     {client-slug}/ per-client files
```

## Troubleshooting

- Tools not working → `/agency-os-meta-doctor`
- Dashboard not loading → check MCP server connected (Settings → MCP Servers); try http://localhost:3001
- Docs: https://github.com/The-Blueprint-Training/bpt-agency-os

---
*22 Local Marketing customization of Agency OS v1.4.0 — data routing maintained locally.*
