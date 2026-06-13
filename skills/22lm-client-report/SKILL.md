---
name: 22lm-client-report
description: Generate branded monthly performance PDF reports for all 22 Local Marketing clients. Combines form leads and phone calls into one leads-by-source view, plus Google Ads and Google Business Profile stats, and outputs one PDF per client. Triggers on "run monthly reports", "generate reports", "monthly report time", "client reports", or any request to produce performance reports for 22 Local Marketing clients. Also triggers when Connor says "reports for all clients", "fire off reports", or "time for reports".
---

# 22 Local Marketing - Monthly Report Generator

This skill generates branded PDF reports for all 22 Local Marketing clients using live data from Google Sheets and the Windsor API.

**Read `METHODOLOGY.md` (in this skill folder) before changing any sourcing logic.** It is the single source of truth for how every lead is counted and guarantees no double counting.

## Trigger Phrases

- "run monthly reports"
- "generate reports for all clients"
- "monthly report time"
- "fire off reports"
- "reports for [client name]"
- "time for reports"

## What It Produces

One PDF per client containing:

1. **Header** with the 22 Local Marketing logo and a "(Formerly VicTree Websites LLC)" line, client name, month/year
2. **KPI hero band**: Total Leads, Website Forms, Phone Calls, Ad Spend
3. **Leads by Source**: a stacked bar chart combining form submissions and phone calls per channel (Google Ads, SEO, Google Business, AI / ChatGPT, Facebook), plus a cumulative line chart of form leads over the month
4. **Google Ads Performance** (spend, clicks, conversions, cost / conversion)
5. **Google Business Profile** (profile views, website visits, calls, direction requests)
6. **All Website Form Leads**: a full date-ordered table of every valid form lead with a color-coded source chip

## Data Sources

| Data | Source | ID |
|------|--------|----|
| Form leads | Per-client tabs in the tracking sheet, classified by landing-page URL | `1r1c_5eCY8cKVCWgBFWPKPYUOx0YPU6E_XMyogcCE3b8` |
| GBP metrics (views, website visits = `clicks` col, calls, directions) | Data Pulls sheet, "GBP Data" tab | `1xtt5tFXjmEAJSJoY5J9y4nf1uPotEA3lQa7rvy9FvG4` |
| Google Ads spend / clicks / conversions | Data Pulls sheet, "GADS Data" tab | `1xtt5tFXjmEAJSJoY5J9y4nf1uPotEA3lQa7rvy9FvG4` |
| Website (SEO) phone calls, validated | Data Pulls sheet, "Calls" tab (per-client Total column) | `1xtt5tFXjmEAJSJoY5J9y4nf1uPotEA3lQa7rvy9FvG4` |
| Google Ads phone-call LEADS | Windsor API, `PHONE_CALL_LEAD` conversions | `WINDSOR_API_KEY` in `.creds` |

Sheets are read via gviz (no auth); the "Calls" tab is read via the Sheets API (Google refresh token in `.creds`); ad call leads via the Windsor API. Calls live on separate numbers per channel, so combining them with forms does not double-count. The GADS tab's raw `phone_calls` column (call interactions) is deliberately NOT used for ad calls; the Windsor `PHONE_CALL_LEAD` conversion count is used instead.

## How to Run

### All clients, previous month (default):
```bash
python generate_reports.py --output /path/to/output
```

### Specific month:
```bash
python generate_reports.py --month 3 --year 2026 --output /path/to/output
```

### Single client:
```bash
python generate_reports.py --client "Green Bear" --month 3 --year 2026
```

## Full Monthly Run ("run reports for all clients")

This is the end-to-end flow when Connor says "run reports for all clients" (or similar). It
produces every PDF and a per-client email DRAFT with the report attached. It NEVER sends email.

1. **Confirm the period.** Default to the previous full month. State it; proceed unless corrected.
2. **Generate PDFs.** `python generate_reports.py --month M --year YYYY --output <dir>`
   One PDF per active client (Elite skipped, Trees Crossing included). PDF rendering uses
   weasyprint if available, otherwise headless Edge/Chrome automatically.
3. **Sanity-check before emailing.** The script prints per-client forms/calls/ads/GBP. Scan it:
   any client showing all zeros, or calls/forms that look impossible vs the sheets, is a
   matching failure — fix it (check the client's `windsor_hints` / `calls_label` / lead tab)
   before drafting that client's email. This is the "no mistakes" gate.
4. **Draft one email per client (DRAFT ONLY, never send).** Using the Gmail MCP `create_draft`
   with the client's PDF attached:
   - **To:** the client's primary contact (see Client Emails below).
   - **From / Reply-To:** connor@victreewebsites.com. (Report delivery is agency to client, so
     it comes from Connor, NOT the client-brand sender used for the client's own lead/confirmation
     emails. Do not apply the lead-form email rules here.)
   - **Subject:** `Your {Month} Performance Report — {Client name}`
   - **Body:** short, plain, on-brand 22LM voice. Lead with the month and total leads, one or two
     sentences of plain-English context, a thank-you, and that the full report is attached. No
     superlatives, no em-dashes, no hype.
   - **Attachment:** that client's PDF only. Double-check the attached file matches the recipient.
   - Leave it as a **draft**. Do not send. Connor reviews and sends each one.
5. **Report back.** Tell Connor how many drafts are ready, the per-client lead totals, and flag
   any anomalies from step 3.

### Client Emails (report-delivery recipients)
Drafts go To the client's primary, CC the office manager where listed, From/Reply-To connor@victreewebsites.com.

| Client | To | CC |
|--------|----|----|
| Better Way LM | brennonmersing0@gmail.com | — |
| Fonville Tree Service | jbftreeandbobcat@gmail.com | — |
| Green Bear Tree Service | greenbeartreeservice@gmail.com | — |
| McQuillin Tree | mcquillintree@gmail.com | — |
| Ranger Tree Care | rangertreecare@gmail.com | melanie@rangertreecare.com (office manager) |
| TN Tree Pres | tntreepres@yahoo.com | — |
| Trees Crossing | treescrossingllc@gmail.com | mjimenez9622@gmail.com (office manager) |
| Elite Tree Service (skipped) | info@elitetreeservicellc.com | — |

Notes:
- **Trees Crossing's two addresses were given "for this iteration only" — re-confirm them before each run.**
- Elite is skipped by default; its address is recorded only for completeness.
- Never guess or substitute an address. If a client is missing here, ask before drafting.

### Single client / specific month (CLI)
`python generate_reports.py --client "Green Bear" --month 5 --year 2026 --output <dir>`

## Client Configuration

Each client has these defaults baked into the script:

| Client | Avg Job Price | Mgmt Fee | Lead Tab Name |
|--------|--------------|----------|---------------|
| Better Way LM | $2,500 | $1,500 | Better Way LM |
| Elite Tree Service | $2,000 | $1,250 | Elite Tree Service |
| Fonville Tree Service | $2,000 | $1,000 | Fonville Tree Service |
| Green Bear Tree Service | $2,500 | $1,500 | Green Bear Tree Service |
| McQuillin Tree | $2,200 | $1,500 | McQuillin Tree |
| Ranger Tree Care | $3,500 | $1,500 | Ranger Tree Care |
| TN Tree Pres | $2,846 | $1,250 | TN Tree Pres |
| Trees Crossing | $2,500 | $1,500 | Trees Crossing |

## Lead Classification Logic

Form leads (Class = "Valid"; "Spam" excluded) are classified by parsing the **landing-page URL query parameters** (not substring matching, which misfires on gclid noise):
- **AI / ChatGPT**: `utm_source` contains chatgpt / openai / perplexity / gemini / claude / copilot
- **Facebook**: `fbclid` present, or `utm_source` = facebook / fb
- **Google Business**: `utm_campaign` or `utm_source` contains `gmb`
- **Google Ads**: `gclid` / `gbraid` / `wbraid` / `gad_source` / `gad_campaignid` present, or `utm_medium` = cpc/ppc/paid
- **SEO**: none of the above (catch-all)

Phone calls are bucketed by channel from their own sources: Google Ads (Windsor `PHONE_CALL_LEAD`), Google Business (GBP `call_clicks`), and SEO (validated website calls from the Calls tab). AI / ChatGPT and Facebook have no separate call tracking, so their calls fall under the SEO/website bucket.

## Dependencies

```
pip install requests
```
PDF rendering order (automatic fallback):
1. **Cloudflare Browser Rendering** via `C:\22 Local Marketing\agent\html2pdf.py` (real headless Chrome; needs `CLOUDFLARE_API_TOKEN` in env; auto-injects `print-color-adjust:exact` so brand backgrounds render). This is the primary path — see [[reference_html_to_pdf]].
2. `weasyprint` (if its native libs are present).
3. Headless Microsoft Edge / Chrome `--print-to-pdf` (no install needed).

The report CSS already sets `@page{size:letter;margin:0}` and `print-color-adjust:exact`; do not pass `printBackground` to the Cloudflare endpoint (it 400s).

## Design Standard

Reports follow `22lm-report-design` brand standards: Sora headings (800, uppercase, never italic), Sora body text, #FB5607 (Blaze orange) primary accents, #0A0A0A (Onyx) headings, #F8F6F2 (Bone) card backgrounds. The header embeds the 22LM logo with a "(Formerly VicTree Websites LLC)" line beneath it. No red anywhere.

## Updating Client Defaults

If a client's avg job price or management fee changes, update the `CLIENTS` dict at the top of `generate_reports.py`.

## Adding a New Client

Add a new entry to the `CLIENTS` dict with:
- `full_name`: Legal/display name
- `lead_tab`: Exact tab name in the tracking sheet
- `windsor_hints`: Lowercase substrings to match the account name in the GBP/GADS tabs and Windsor API
- `calls_label`: Lowercase substring to match the client's column header in the "Calls" tab
- `location`: City, State
- `jobPrice` / `mgmtFee`: retained but no longer used in the report (ROI section was removed)

To skip a client from the default all-clients run, add its key to `SKIP_CLIENTS` (Elite is skipped there now). Pass `--include-elite` to override.
