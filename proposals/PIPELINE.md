# 22LM AI Proposal Pipeline — one-shot runbook

Turn a single prompt into a fully-audited, branded proposal deployed live to Cloudflare.

**Trigger:** `Proposal: <Business Name>, <City>, <State>, <website URL>`
(optionally append primary services and target cities; otherwise discover them).

**Outcome:** a live proposal at `https://proposals.22localmarketing.com/<slug>/`, fully autonomous, no checkpoint (per Connor, 2026-06).

---

## 0. Inputs to resolve first
- Business name, city, state, website URL (from the trigger).
- Trade (roofing, electrical, plumbing, HVAC, tree, etc.) — infer from the site. 22LM serves ALL contractor trades now, not just tree. See `[[project_all_contractors_pivot]]`.
- Primary services (5–8) and target cities (5–10) — from the site / GBP; these drive the architecture diagram and content.
- The prospect's logo (pull from their site) and a Google Business Profile reference.

## 1. Hard rules (apply to all visible content)
- **The narrative is BESPOKE to each prospect, never the template's sample story.** The template gives you structure and components only. Write the hero, exec summary, and every framing line fresh from THIS prospect's real audit. Let the data dictate the angle: a map-pack dominator gets a "you own your backyard, now build the web presence to grow beyond it" story, not "you're invisible." A declining site gets the decline story. A no-website site gets the foundation story. Read the data first, then decide the story. Reusing the canned narrative when it doesn't fit produces a dishonest proposal (see the Vivid Tree Service run, 2026-06).
- **No corporate/national competitors** in any comparison (no Bartlett, no franchises). Local independents only.
- **No software/tool names** in visible proposal content (no Local Falcon, Ahrefs, Screaming Frog, DataForSEO, n8n, GHL). Use "geo-grid scan", "site crawl", "domain authority", etc. (The n8n flow image is the one allowed exception Connor approved.)
- **Credentials:** "licensed (where the trade requires it), insured, bonded." The old no-licensing rule is dead.
- **No stock photos, no em-dashes/en-dashes, no superlatives/bravado, hero paragraphs ≤2 sentences.**
- Traffic numbers are Ahrefs estimates — label as "est." where shown. No GSC-only claims (we don't have the prospect's Search Console).

## 2. Data collection
Run all of these for the prospect (and the 4 chosen competitors where noted):
- **Geo-grid scan (Local Falcon):** run a scan for the primary "[service] [city]" term. Capture the grid screenshot → `geogrid.png`. Pull avg rank, share of local voice, top-3 %.
- **Rankings / authority / traffic / backlinks (Ahrefs):** domain rating + history, organic keywords + positions + history, organic traffic + 24-mo history, traffic value, referring domains + history, top pages by traffic, organic competitors, backlink stats. Estimate spam-link % from referring-domain quality.
- **Keyword detail + SERP features (DataForSEO):** volume, difficulty, position, SERP features (AI Overview, map pack, PAA) per money keyword.
- **Technical crawl (Screaming Frog, headless export):** pages crawled, 4xx/5xx, missing meta/H1, thin pages, missing alt, redirects, schema presence, indexation, Core Web Vitals.
- **GBP competitor audit (Local Falcon + GBP):** reviews, rating, photos, categories, posting cadence for the prospect + 4 competitors.
- **AI/generative presence:** query ChatGPT / AI Overview / Perplexity for "[service] [city]" and record whether the prospect is cited and who is.

## 3. Competitor selection
Pick the **4 strongest LOCAL INDEPENDENT** competitors from the map pack / Ahrefs organic competitors. Reject any regional/national chain or franchise. Mark the leader for the green "winner" coding.

## 4. Score the audit
Use the `vw-audit-rubric` skill on the collected signals to produce the 0–100 site-health score and per-category breakdown (do NOT eyeball it).

## 5. Build the proposal
1. **Slug:** `<business-kebab>-<4char-hash>` (unguessable, e.g. `summit-tree-land-x7k2`).
2. **Folder:** copy `template/index.html` and ALL shared images into `site/<slug>/`:
   - shared/reusable, copy as-is: `example-build-trust.png`, `conversion-automation.png`, `work-ranger.png`, `work-fonville.png`, `work-mcquillin.png`, `work-greenbear.png`, `work-tntp.png`
   - add per-prospect: prospect logo (`logo.png`/`.webp`), `geogrid.png`
     - **Scrape the logo from the prospect's site** (don't use a text wordmark): grab the header logo `<img>` (class often `logo`/`header-title-logo`) or the og:image / `logoImageUrl`. Squarespace → `images.squarespace-cdn.com/...`, Wix → `static.wixstatic.com/...`. Save with the correct extension (Squarespace often serves WebP even at a `.png` URL, name it `.webp`). Put it as an `<img>` in BOTH the nav (`.client-logo`) and the hero (`.hero-logo`), replacing the `{{CLIENT_LOGO}}` `.cl-ph` placeholder. **Always show the business name (`<span class="cl-name">{{CLIENT_NAME}}</span>`) next to the logo in both spots** (the template already includes these spans, just fill `{{CLIENT_NAME}}`).
3. **Fill** `site/<slug>/index.html` — replace every placeholder and all SAMPLE data:
   - Tokens: `{{CLIENT_NAME}} {{CITY}} {{STATE}} {{CLIENT_LOGO}} {{GEOGRID_SCREENSHOT}} {{LOOM_ID}}`
     (`{{CLIENT_LOGO}}` → `<img src="logo.png">`, `{{GEOGRID_SCREENSHOT}}` → `<img src="geogrid.png">`, `{{LOOM_ID}}` → Connor's reusable Loom share ID).
   - **Pitch tab:** hero headline + lead (≤2 sentences); exec-summary snapshot/challenges/strategy; geo-grid keyword + metrics; visibility-gaps table + authority gauges; competitor table + the 3 competitor chart data arrays; the architecture diagram (service-hub names = prospect's services, area-hub names = prospect's real cities/suburbs, commercial verticals relevant to the trade, the spoke examples, and the keyword in the geo-grid section).
   - **Analysis tab:** organic scorecards + deltas; 24-mo trend; decline drivers + cannibalization table; keyword funnel; keyword-detail table; AI-presence matrix; top-pages table; topical-authority table (green=winner); thin-content table; content-gap table; site-health gauge + categories (from rubric); crawl summary + issues; Core Web Vitals; technical checklist; GBP competitor audit (green=winner); backlink table incl. spam % (>20% = red); projection.
   - **Chart JS data arrays** (update the numbers in the `<script>`): `trafficChart`, `compReviews`, `compDR`, `compKw`, `organicTrend`, `projectionChart`, `backlinkChart`. Keep `CMP_LABELS` = the 4 competitors + "You".
   - **Pricing (static):** website $5,000 one-time; tiers $1,000 / $1,500 / $2,000. Adjust ROI calculator's default avg-job-value to the trade if useful.
4. **DO NOT change** these reusable sections: testimonials/Google reviews carousel (real 22LM reviews + Mitch Crowell video), recent-work carousel (5 client sites), winning-formula popups (page-type do/don'ts are trade-agnostic), pricing tiers table, the invoice form.

## 6. Validate
`python validate.py site/<slug>/index.html` — must print **PASS** with **zero** remaining `{{TOKEN}}` placeholders. A JS syntax error (e.g. an apostrophe in a single-quoted string) breaks the entire page; when writing JS string data, use double quotes for any string containing an apostrophe.

## 7. Deploy
`bash deploy.sh` (validates every proposal in `site/`, then `wrangler pages deploy site`). `site/` is the persistent local source of every proposal; each deploy ships the whole folder.

## 8. Output
Return the live URL `https://proposals.22localmarketing.com/<slug>/` and a one-line summary of the headline findings.

---
**Infra (already set up):** Cloudflare Pages project `22lm-proposals`, account `ff4bcfdaf56c61c138988bc01d894d84`, custom domain `proposals.22localmarketing.com` (zone `c17eae29b9a97a7bb5edb020c8a78ca6`). Token in agent env. Stripe invoice Worker for the form CTA is still TODO. See `[[project_ai_proposal_system]]`.
