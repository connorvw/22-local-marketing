# 22 Local Marketing — Monthly Report Lead-Sourcing Methodology

Finalized 2026-06. This is the single source of truth for how every number on a monthly
report is sourced. `generate_reports.py` implements exactly this. The reports.victreewebsites.com
tool must implement the same rules.

## Core principle
Every lead is counted exactly once. Form submissions and phone calls are distinct lead events.
Phone calls are tracked on separate phone numbers per channel, so no call belongs to two channels.

## Five lead sources
`Google Ads`, `SEO`, `Google Business`, `AI / ChatGPT`, `Facebook`.

## Form leads — tracking sheet `1r1c_5eCY8cKVCWgBFWPKPYUOx0YPU6E_XMyogcCE3b8`
Per-client tab. Only rows with `Class == "Valid"` count; `Class == "Spam"` is excluded and
reported as a filtered count. Source is determined by parsing the landing-page URL query
params (NOT substring matching — "ai"/"fb" appear inside gclid strings and cause false hits).
First match wins, in this order:

1. **AI / ChatGPT** — `utm_source` contains chatgpt, openai, perplexity, gemini, claude, or copilot
2. **Facebook** — `fbclid` param present, or `utm_source` is facebook / fb
3. **Google Business** — `utm_campaign` or `utm_source` contains `gmb`
4. **Google Ads** — `gclid` / `gbraid` / `wbraid` / `gad_source` / `gad_campaignid` present, or `utm_medium` is cpc / ppc / paid
5. **SEO** — none of the above (catch-all)

Each form row lands in exactly one bucket. No form is counted twice. **Same-week duplicate
submissions** from the same person (matched by email, else name; same ISO week) are collapsed to a
single lead — conservative, so a repeat inquiry in one week is not over-claimed.

## Phone-call leads — three independent systems, zero overlap
The CallRail tracking number is on the **website only**; it does NOT capture GBP or Ads calls.
Each channel's calls live on a different number, so they never collide:

- **Google Ads calls** — Windsor API (`connectors.windsor.ai/google_ads`), sum of `conversions`
  where `conversion_action_category == "PHONE_CALL_LEAD"` **AND the conversion action name does NOT
  contain "website"** (i.e. ad-asset calls only), matched to the client by account name. Website-
  attributed ad calls are excluded on purpose — they ring the website number and are already counted
  in SEO answered website calls, so counting them here would double-claim. Do NOT use the GADS-tab
  `phone_calls` column — that is `metrics.phone_calls` (raw call interactions, inflated). Key:
  `WINDSOR_API_KEY` in `.creds`.
- **Google Business calls** — Data Pulls "GBP Data" tab, `call_clicks` (calls from the GBP listing).
- **SEO / website calls** — Data Pulls "Calls" tab, the client's **Answered** column only. Only
  answered website calls count as valid SEO calls. The **Missed** count is NOT added to leads; it
  is surfaced as a note in the Leads-by-Source bar-chart card ("N calls went unanswered this month,
  each a potential lead"). (CallRail website calls; answering-machine pickups are already counted
  as missed by the team.)
- **AI / ChatGPT** and **Facebook** have no dedicated call tracking. Any calls they drove came
  through the website and are already inside the SEO/website bucket. They show 0 calls.

## No-double-count guarantees
- Forms: one row → one source.
- Calls: three separate phone numbers (Ads call-asset/Google forwarding, GBP listing, website
  CallRail) → a given call exists in at most one system.
- Forms vs calls: distinct events. One person who both calls and submits a form is 2 leads (intended).

## Ad call attribution — resolved conservatively (no overlap)
Windsor `PHONE_CALL_LEAD` for a client is the sum of two conversion actions:
"Calls from Ads" (call-asset, Google's forwarding number, never touches the website) +
"Calls from Website" (clicks on the site's phone link, attributed to an ad). The
"Calls from Website" portion are website calls that ALSO ring the website number and are already
inside the validated SEO answered-calls total. Example (Green Bear, May 2026):
14 "Calls from Ads" + 4 "Calls from Website".

**Resolved (2026-06, conservative — "rather miss than over-claim"):** count **ad-asset calls only**.
Exclude any PHONE_CALL_LEAD conversion whose action name contains "website". So Green Bear Ads = 14,
not 18, and the 4 website-attributed calls are counted once (under SEO). This guarantees no call is
double-claimed across Ads and SEO. (Earlier Option A — count all PHONE_CALL_LEAD — was reversed in
favor of this conservative rule.)

## Platform metrics — shown, never added to lead totals
- Google Ads: spend, clicks, conversions, cost/conversion (Data Pulls "GADS Data" tab).
- GBP: profile views (`impressions`), website visits (`clicks` column — NOT "website_clicks",
  which does not exist in the tab), calls (`call_clicks`), direction requests.
These are context only and are never summed into the lead counts.

## Report scope
All active clients. Elite is skipped by default (`SKIP_CLIENTS`); Trees Crossing is included.
