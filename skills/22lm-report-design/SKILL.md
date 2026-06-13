---
name: 22lm-report-design
description: Apply 22 Local Marketing brand design standards to any report, audit, analysis, or deliverable created for a client, lead, or internal use. Use this skill whenever generating any report, summary, audit result, proposal, competitive analysis, onboarding document, monthly performance report, SEO audit, GBP analysis, or any structured deliverable output in the context of 22 Local Marketing / 22 Local Marketing or its clients. This skill must trigger any time Connor or the team asks to "generate a report", "write up the audit", "summarize results", "create a deliverable", or "put together findings". Always apply this skill proactively — do not wait to be asked if the output is a report or document.
---

# 22 Local Marketing Report Design Standard

All reports, audits, analyses, and structured deliverables produced for 22 Local Marketing — whether for clients, leads, or internal use — must follow this design standard. This is not optional. Apply it by default.

**Brand identity:** Blaze orange primary, onyx, bone, and white. NO RED anywhere. Confident, grounded, blue-collar professional.

---

## Brand Kit

*Source: 22 Local Marketing brand tokens (`C:\22 Local Marketing\brand-deliverables\brand-tokens.css`) — the confirmed production values for the agency rebrand.*

### Colors

| Role | Hex | Usage |
|------|-----|-------|
| Blaze (Primary) | `#FB5607` | Section headers, rule lines, score callouts, CTAs, card left borders, brand identity — the dominant brand color |
| Scorch (Deep) | `#C13D0E` | Hover states, deepest emphasis, negative/decline indicators (ROI loss) |
| Onyx | `#0A0A0A` | All H1/H2/H3 heading text, dark emphasis, total bars, table header fills |
| Slate | `#525252` | Secondary text, labels, metadata, captions |
| Slate Light | `#8A8A8A` | Muted captions, footnotes, dividers |
| Border | `#E5E2DC` | Table row dividers, hairlines |
| Border Strong | `#D4D0C8` | Stronger dividers, card outlines |
| Bone | `#F8F6F2` | Section backgrounds, alternating table rows, neutral cards |
| White | `#FFFFFF` | Primary background, card surfaces |

**Color application rules:**
- `#FB5607` (Blaze) is the primary 22LM brand color. Use it for report header rule lines, section H2 underlines, card left borders, and primary CTAs. It is the brand accent and positive-emphasis color.
- `#C13D0E` (Scorch) is for hover states, deep emphasis, and negative-state indicators (e.g., a negative ROI figure). Use sparingly.
- `#0A0A0A` (Onyx) is the heading color for all H1/H2/H3 text. Also used for total bars and high-emphasis fills.
- `#525252` (Slate) is the secondary text and label color. Use for body copy and data values where a softer-than-onyx tone reads better.
- `#F8F6F2` (Bone) is the default neutral fill for cards, section backgrounds, and alternating table rows.
- **No red anywhere.** Blaze orange is the brand; do not introduce a separate red. For negative/fail/critical states, use bold Onyx (`#0A0A0A`) text with an explicit label (e.g. "FAIL", "MISSING"), or Scorch (`#C13D0E`) for a single negative figure. Severity is communicated through typography weight and labels, not red.
- Never use gradients, pastels, or off-brand colors. Dark backgrounds only for hero/cover sections or total bars (use `#0A0A0A`). All section bodies use white or `#F8F6F2`.

### Typography

*Confirmed from the 22LM brand kit. Load via Google Fonts: `Sora`.*

| Role | Font | Weight | Transform | Color | Usage |
|------|------|--------|-----------|-------|-------|
| Report Title / H1 | Sora | 800 | Uppercase | `#0A0A0A` | Main report title |
| Section Header / H2 | Sora | 800 | Uppercase | `#FB5607` (with `#FB5607` underline) | Section headings |
| Sub-header / H3 | Sora | 700 | None | `#0A0A0A` | Sub-sections, category labels |
| UI Labels / Accent | Sora | 700 | Uppercase (tracking `0.12em`) | `#FB5607` or `#525252` | Badges, stat labels, callout labels |
| Body / Data / Prose | Sora | 400 | None | `#0A0A0A` | All body text, table data, descriptions |
| Body Bold | Sora | 700 | None | `#0A0A0A` | Bold body callouts, key data points |
| Card Value (Stat) | Sora | 800 | None | `#0A0A0A` | Large stat numbers in score cards |

**Typography rules:**
- **Sora for everything.** Headings at 800, sub-headers and labels at 700, body at 400. No other fonts.
- Fallback stack: `'Sora', system-ui, sans-serif`.
- **Sora is never italic.** The previous 22 Local Marketing standard used italic Teko headings; that is deprecated. 22LM headings are upright Sora with tight letter-spacing (`-0.02em` on large headings, `0.12em` uppercase tracking on small labels).
- No em-dashes anywhere in report content. Use commas, periods, or parentheses.
- Data values in tables: Sora 400, normal case, color `#0A0A0A` (or `#525252` for secondary).

### Logo & Identity

- Logo: `C:\22 Local Marketing\logo-kit\all-formats-no-margin\png\22lm-primary-tight.png` (PNG for PDF embedding; webp/svg variants in the same kit). Place the primary logo top-left of the report header.
- Directly under the logo, always include: **(Formerly VicTree Websites LLC)** in small Slate text. This runs on every report during the rebrand transition.
- Agency name in text: **22 Local Marketing** (shorthand and on formal docs). Domain: `22localmarketing.com`.
- Voice: Direct, no-nonsense, blue-collar credible. No superlatives. No bravado. Data-first.

---

## Component Style (finalized 2026-06, house standard)

The monthly report (`22lm-client-report` / `generate_reports.py`) is the reference implementation. Match it:

- **Page background:** Bone `#F8F6F2`. Cards/charts sit on it as white surfaces.
- **Cards, charts, KPI/metric cards:** white, `1px solid #0A0A0A` border, `border-radius:10px`, and the signature **hard offset shadow `box-shadow: 3px 3px 0 0 #0A0A0A`**. No soft blurred shadows. No colored top/left accent borders.
- **Tables:** wrap in the same white + onyx-border + radius card, but **no shadow**. Header row: onyx `#0A0A0A` background, white Sora 800 uppercase.
- **Section headings (H2):** Sora 800 uppercase with **22LM corner brackets** (top-left + bottom-right L-shapes, 14px, `2px solid #FB5607`), NOT a solid square bullet. A thin `#D4D0C8` divider line separates sections.
- **Chips / badges:** small pill (`border-radius:4px`), a 6px color dot, tinted background of the source color, uppercase label.
- **Charts:** inline SVG line/bar (no JS lib, so it renders in PDF). Legends sit INSIDE the chart card. Cumulative charts carry a small "Cumulative" tag in the legend row.
- **Emphasis fill:** to make one stat stand out, use the pale-orange brand token `#FFE8D9` as its background (e.g., the Total Leads card).
- **PDF rendering:** always include `print-color-adjust:exact` (and `-webkit-` prefix) so background colors render in the PDF.

---

## Report Structure

Every report must follow this section order. Omit sections that don't apply — never leave a section blank. If a section has no content, skip it entirely.

### 1. Header Block (always present)
```
[22 Local Marketing logo]
(Formerly VicTree Websites LLC)
[Report Type]
[Client or Subject Name]
[Date: Month YYYY] | [Location] | Prepared by 22 Local Marketing
```
Style: Blaze rule line under the header block (`#FB5607`, 4px solid). Report type label in Blaze uppercase. Client name in Onyx bold Sora uppercase.

### 2. Executive Summary (always present)
- 2 to 4 sentences maximum
- State the purpose, the main finding, and the single most important action
- No bullet points in this section — prose only
- Use plain language. Avoid jargon unless the audience is technical.
- Background: `#F8F6F2` with `#FB5607` left border (4px solid).

### 3. Score or Status Overview (when applicable)
Use for: competitive audits, SEO audits, GBP analyses, monthly performance reports.
- Display as a summary table or score cards
- Pass/positive states: `#FB5607` (Blaze) or bold Onyx
- Fail/negative states: `#0A0A0A` bold text with explicit "FAIL" or "MISSING" label, or `#C13D0E` for a single negative figure — no red
- Neutral states: `#525252` regular text
- Always show metric name, value, and a brief interpretation
- If scoring out of 100: show subsection scores broken out (e.g., Website: 38/45, GBP: 31/40)

### 4. Main Data Sections (always present)
Organize by category. Each section must have:
- A bold H2 header in Blaze (`#FB5607`) with Blaze underline rule
- A brief 1-sentence context statement before any table or data
- The data itself (table, list, or prose — see Data Format Rules below)
- A "Key Takeaway" line in Slate (`#525252`) at the bottom of each section

**Section header format in Markdown:**
```markdown
## Website Performance
```
In HTML: `<h2 style="color:#FB5607; border-bottom: 2px solid #FB5607; padding-bottom: 4px; font-family:'Sora',sans-serif; font-weight:800; text-transform:uppercase;">`

### 5. Gap Analysis (for competitive / audit reports)
- Always broken out by category
- Format: **[Gap]** — what it means and why it matters
- Ordered by impact (highest ROI first)
- Never vague ("needs improvement") — always specific ("0 location pages vs competitor's 12")

### 6. Action Items / Recommendations (always present)
- Numbered list, ordered by priority
- Each item: **Bold action statement** then a 1 sentence explanation. Difficulty: Easy / Medium / Hard.
- Maximum 10 items. Minimum 3.
- Lead with quick wins first (Easy difficulty).

### 7. Footer (always present)
```
22 Local Marketing | 22localmarketing.com | (336) 296-4800
Confidential — prepared for [Client Name]
```
Top border: 2px solid `#FB5607`. Text color: `#525252`. Centered. Small (10 to 11px).

---

## Data Format Rules

### Tables
- Use for: comparison data, scored metrics, multi-column data, side-by-side audits
- Header row: white text on `#0A0A0A` background, Sora 800 uppercase
- Alternating rows: white / `#F8F6F2`
- Bold the winner or best value in each row (for competitive tables) — `#FB5607` for the winner
- Never exceed 6 columns without splitting into two tables
- Always include units in column headers (e.g., "Reviews (#)" not just "Reviews")
- Row dividers: `1px solid #E5E2DC`

### Score Cards / Callout Boxes
- Use for: single key metrics, highlight stats, exec-level numbers
- Style: `#F8F6F2` background, left border `#FB5607` (4px solid), padding 12 to 14px
- Metric value: large Sora 800 in `#0A0A0A`
- Label: small Sora 700 uppercase below the number, in `#525252`, letter-spacing `0.12em`
- Do not crowd more than 4 score cards in a single row

### Lists
- Use for: action items, feature lists, quick facts
- Bullet points for unordered lists; numbers for ordered/priority lists
- No nested bullets more than 1 level deep
- Keep bullets to 1 or 2 sentences each

### Badges / Status Indicators
- Yes / Pass / Complete — Blaze `#FB5607` text or pill
- No / Fail / Missing — bold Onyx `#0A0A0A` text or pill (NOT red)
- Warning / Caution — Scorch `#C13D0E` (sparingly)
- Unknown / N/A — Slate Light `#8A8A8A`
- Render as inline colored text labels or small pill badges

---

## Output Format by Report Type

### Markdown Reports (default for Drive storage)
- Use `##` for section headers
- Use `---` as horizontal rules between major sections
- Bold all metric labels: `**Total Reviews:**` 142
- Use tables for all comparison data
- Begin with a top-level `# Title` in the format: `# [Report Type]: [Subject] — [Month YYYY]`

### HTML Reports (for client-facing deliverables, PDF export, Cloudflare Pages)
- Inline all CSS (no external stylesheets)
- Load fonts: `https://fonts.googleapis.com/css2?family=Sora:wght@400;600;700;800&display=swap`
- Heading font stack: `'Sora', system-ui, sans-serif` — H1/H2 always weight 800 uppercase, never italic
- H3 font stack: `'Sora', system-ui, sans-serif` — weight 700, normal case
- Body font stack: `'Sora', system-ui, sans-serif` — weight 400, color `#0A0A0A`
- Blaze accent lines on all H2 headers via `border-bottom: 2px solid #FB5607`
- Cards use `border-left: 4px solid #FB5607`
- Section fills: `background: #F8F6F2`
- Header: embed the 22LM logo (base64 data URI for reliable PDF rendering), with "(Formerly VicTree Websites LLC)" beneath it
- Max content width: `860px`, centered with `margin: 0 auto`
- Mobile-responsive: single column on screens under 600px

### In-Chat Reports (conversational delivery)
- Use Markdown formatting
- Lead with the Executive Summary directly
- Keep tables tight — max 4 columns for readability
- End with a clear "Next Steps" call to action

---

## Tone & Voice Rules

These apply to all written content in every report:

- **Direct and clear.** Say what it is. Skip throat-clearing phrases like "it's worth noting that" or "it's important to consider."
- **No superlatives.** Never say "best," "top-rated," "world-class," "industry-leading."
- **No licensing claims.** Never call any client "licensed." Only "insured and bonded."
- **No em-dashes.** Use commas, periods, or parentheses instead.
- **No AI-sounding language.** Avoid: "delve," "leverage," "utilize," "it's worth noting," "in conclusion," "comprehensive."
- **Data before opinion.** State the fact, then the implication. Not the implication first.
- **Humble but confident.** The tone is professional blue-collar, not corporate consultant.

---

## Report Type Quick Reference

| Report Type | Required Sections | Primary Data Format |
|-------------|-------------------|---------------------|
| Competitive Audit | Header, Summary, Score Overview, Per-Category Tables, Gap Analysis, Actions | Side-by-side comparison tables |
| Monthly Performance | Header, Summary, KPI Scorecard, Traffic, Leads, GBP, Actions | Score cards + trend tables |
| SEO / Website Audit | Header, Summary, Score Overview, Website Table, Off-Page Table, Actions | Scored metric tables |
| Client Onboarding Summary | Header, Summary, Client Info, Services, Priority Areas, Content Rules | Clean info tables |
| Lead Proposal | Header, Summary, Opportunity Overview, Recommended Services, Pricing | Prose + services table |
| Internal Analysis | Header, Summary, Findings, Actions | Prose + data tables |

---

## What This Skill Does NOT Cover

- Writing client-facing content (website copy, GBP posts) — those follow separate content rules
- Code output (HTML landing pages, scripts) — those follow separate development standards
- Social media content — separate social voice guidelines apply

When in doubt: if the output is a structured deliverable that someone will read to understand data or make a decision, apply this skill.

---

## Migration Note (22 Local Marketing rebrand)

The agency rebranded from **22 Local Marketing** to **22 Local Marketing**. Two prior styles are now deprecated:
- The original red (`#CC1A1A`) and Teko 800 italic style.
- The May 2026 22 Local Marketing green (`#008614`) and Teko/Bai Jamjuree style.

Any report or deliverable produced from this point forward must use:
- Blaze orange (`#FB5607`) as the primary brand color
- Onyx (`#0A0A0A`) for all headings
- Sora 800 uppercase (never italic) for H1/H2, Sora 700 for H3
- The 22LM logo in the header with "(Formerly VicTree Websites LLC)" beneath it
- No red anywhere, including for negative/fail states

If you encounter an older report styled in red or green, regenerate it under the 22LM standard if it's still in active use.
