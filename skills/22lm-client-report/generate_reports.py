#!/usr/bin/env python3
"""
22 Local Marketing - Monthly Client Report Generator

Sources ALL data from two Google Sheets plus the Windsor API:
  - Tracking sheet (form leads), classified by landing-page URL into 5 sources
  - Client Data Pulls sheet: GBP Data tab, GADS Data tab, validated website-call "Calls" tab
  - Windsor API: ad phone-call LEADS (PHONE_CALL_LEAD conversions, not raw call interactions)

Usage:
    python generate_reports.py                    # previous month, all active clients (Elite skipped)
    python generate_reports.py --month 5 --year 2026
    python generate_reports.py --client "Green Bear" --month 5 --year 2026
"""

import argparse
import json
import re
import os
import sys
import base64
import calendar
import collections
import subprocess
import shutil
import tempfile
import time
import html as _html
from datetime import datetime, date
from urllib.request import urlopen, Request
from urllib.parse import quote, urlencode, urlparse, parse_qs

# ---------------------------------------------------------------------------
# CONFIG
# ---------------------------------------------------------------------------

CREDS_CANDIDATES = [r"C:\22 Local Marketing\agent\.creds", r"C:\VicTree Websites LLC\agent\.creds"]
CREDS_PATH = next((p for p in CREDS_CANDIDATES if os.path.exists(p)), CREDS_CANDIDATES[-1])

_LOGO_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "22lm-primary-tight.png")
try:
    with open(_LOGO_PATH, "rb") as _lf:
        LOGO_DATA_URI = "data:image/png;base64," + base64.b64encode(_lf.read()).decode("ascii")
except Exception:
    LOGO_DATA_URI = ""
LOGO_TAG = (
    '<img class="brand-logo" src="%s" alt="22 Local Marketing">' % LOGO_DATA_URI
    if LOGO_DATA_URI else '<div class="brand-fallback">22 Local Marketing</div>'
)

LEAD_SHEET_ID = "1r1c_5eCY8cKVCWgBFWPKPYUOx0YPU6E_XMyogcCE3b8"
WINDSOR_SHEET_ID = "1xtt5tFXjmEAJSJoY5J9y4nf1uPotEA3lQa7rvy9FvG4"
WINDSOR_GBP_TAB = "GBP Data"
WINDSOR_ADS_TAB = "GADS Data"

# Lead sources (order = display order). Colors are 22LM/source brand hues.
SOURCES = ["Google Ads", "SEO", "Google Business", "AI / ChatGPT", "Facebook"]
SOURCE_COLOR = {
    "Google Ads": "#008B8B", "SEO": "#0A0A0A", "Google Business": "#34A853",
    "AI / ChatGPT": "#FB5607", "Facebook": "#1877F2",
}

# Default run skips Elite (no longer active). Trees Crossing IS included.
SKIP_CLIENTS = {"Elite Tree Service"}

CLIENTS = {
    "Better Way LM": {
        "full_name": "Better Way Land Management LLC", "lead_tab": "Better Way LM",
        "windsor_hints": ["better way"], "calls_label": "better way",
        "jobPrice": 2500, "mgmtFee": 1500, "location": "Swanton, OH",
    },
    "Elite Tree Service": {
        "full_name": "Elite Tree Service LLC", "lead_tab": "Elite Tree Service",
        "windsor_hints": ["elite tree"], "calls_label": "elite",
        "jobPrice": 2000, "mgmtFee": 1250, "location": "Gurdon, AR",
    },
    "Fonville Tree Service": {
        "full_name": "Fonville Tree Service", "lead_tab": "Fonville Tree Service",
        "windsor_hints": ["fonville"], "calls_label": "fonville",
        "jobPrice": 2000, "mgmtFee": 1000, "location": "Wake Forest, NC",
    },
    "Green Bear Tree Service": {
        "full_name": "Green Bear Tree Service LLC", "lead_tab": "Green Bear Tree Service",
        "windsor_hints": ["green bear"], "calls_label": "green bear",
        "jobPrice": 2500, "mgmtFee": 1500, "location": "Kernersville, NC",
    },
    "McQuillin Tree": {
        "full_name": "McQuillin Tree Care", "lead_tab": "McQuillin Tree",
        "windsor_hints": ["mcquillin"], "calls_label": "mcquillin",
        "jobPrice": 2200, "mgmtFee": 1500, "location": "Delta, OH",
    },
    "Ranger Tree Care": {
        "full_name": "Ranger Tree Care", "lead_tab": "Ranger Tree Care",
        "windsor_hints": ["ranger"], "calls_label": "ranger",
        "jobPrice": 3500, "mgmtFee": 1500, "location": "Satellite Beach, FL",
    },
    "TN Tree Pres": {
        "full_name": "TN Tree Preservation", "lead_tab": "TN Tree Pres",
        "windsor_hints": ["tn tree", "tn preservation"], "calls_label": "tn tree",
        "jobPrice": 2846, "mgmtFee": 1250, "location": "College Grove, TN",
    },
    "Trees Crossing": {
        "full_name": "Trees Crossing LLC", "lead_tab": "Trees Crossing",
        "windsor_hints": ["trees crossing"], "calls_label": "trees crossing",
        "jobPrice": 2500, "mgmtFee": 1500, "location": "Rocky Mount, VA",
    },
}

MONTH_NAMES = [
    "", "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
]


# ---------------------------------------------------------------------------
# CREDENTIALS
# ---------------------------------------------------------------------------

_CREDS = None
def creds():
    global _CREDS
    if _CREDS is None:
        _CREDS = {}
        try:
            for line in open(CREDS_PATH, encoding="utf-8"):
                line = line.strip()
                if "=" in line and not line.startswith("#"):
                    k, v = line.split("=", 1)
                    _CREDS[k] = v.strip().strip('"')
        except Exception as e:
            print(f"  Warning: could not read creds ({e})")
    return _CREDS


def google_access_token():
    c = creds()
    data = urlencode({
        "client_id": c.get("GOOGLE_CLIENT_ID", ""), "client_secret": c.get("GOOGLE_CLIENT_SECRET", ""),
        "refresh_token": c.get("GOOGLE_REFRESH_TOKEN", ""), "grant_type": "refresh_token",
    }).encode()
    return json.load(urlopen("https://oauth2.googleapis.com/token", data))["access_token"]


# ---------------------------------------------------------------------------
# DATA FETCHING
# ---------------------------------------------------------------------------

def fetch_gviz(sheet_id, tab_name):
    """Fetch rows from a Google Sheet tab via the gviz/tq JSON endpoint."""
    url = (f"https://docs.google.com/spreadsheets/d/{sheet_id}"
           f"/gviz/tq?tqx=out:json&sheet={quote(tab_name)}")
    req = Request(url, headers={"User-Agent": "Mozilla/5.0"})
    raw = urlopen(req, timeout=30).read().decode("utf-8")
    json_str = re.search(r"\{.*\}", raw, re.DOTALL)
    if not json_str:
        return [], []
    data = json.loads(json_str.group())
    cols = [c.get("label", c.get("id", "")) for c in data["table"]["cols"]]
    rows = []
    for r in data["table"]["rows"]:
        row = []
        for cell in r["c"]:
            if cell is None:
                row.append(None)
            else:
                v = cell.get("v")
                if isinstance(v, str) and v.startswith("Date("):
                    parts = [int(x) for x in v[5:-1].split(",")]
                    v = date(parts[0], parts[1] + 1, parts[2])
                row.append(v)
        rows.append(row)
    return cols, rows


def parse_lead_date(date_str):
    if not date_str:
        return None
    if isinstance(date_str, date):
        return date_str
    for fmt in ("%B %d, %Y", "%m/%d/%Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(str(date_str).strip(), fmt).date()
        except (ValueError, TypeError):
            continue
    return None


def classify_source(url):
    """Classify a form lead by its landing-page URL query params (5 sources)."""
    q = parse_qs(urlparse(url or "").query)
    src = " ".join(q.get("utm_source", [])).lower()
    med = " ".join(q.get("utm_medium", [])).lower()
    camp = " ".join(q.get("utm_campaign", [])).lower()
    if any(k in src for k in ("chatgpt", "openai", "perplexity", "gemini", "claude", "copilot")):
        return "AI / ChatGPT"
    if "fbclid" in q or "facebook" in src or src == "fb" or "facebook" in med:
        return "Facebook"
    if "gmb" in camp or "gmb" in src or "google business" in src:
        return "Google Business"
    if any(k in q for k in ("gclid", "gbraid", "wbraid", "gad_source", "gad_campaignid")) or med in ("cpc", "ppc", "paid"):
        return "Google Ads"
    return "SEO"


def fetch_leads(client_key, target_month, target_year):
    """Form leads from the tracking sheet: 5-way counts + the valid rows."""
    cfg = CLIENTS[client_key]
    result = {"forms": collections.Counter(), "spam": 0, "valid": []}
    try:
        cols, rows = fetch_gviz(LEAD_SHEET_ID, cfg["lead_tab"])
    except Exception as e:
        print(f"  Warning: could not fetch leads for {client_key}: {e}")
        return result
    cmn = {c.lower(): i for i, c in enumerate(cols)}
    di = cmn.get("date", 1)
    ci = cmn.get("class", 2)
    ui = cmn.get("page url", cmn.get("pageurl", 10))
    ni = cmn.get("name", 3)
    si = cmn.get("service needed", 8)
    ei = cmn.get("email address", cmn.get("email", 5))

    def clean(x):
        return _html.escape(str(x or "").replace("\xa0", " ").strip())

    seen = set()         # (iso_year, iso_week, identity) -> drop same-week duplicate submissions
    result["dupes"] = 0
    for row in rows:
        if len(row) <= max(di, ci):
            continue
        d = parse_lead_date(row[di])
        if d is None or d.month != target_month or d.year != target_year:
            continue
        cls = str(row[ci] or "").strip().lower()
        if cls == "spam":
            result["spam"] += 1
            continue
        if cls != "valid":
            continue
        # Conservative dedup: same person (email, else name) submitting again in the SAME week
        # counts once. Errs toward undercount rather than over-claiming repeat submissions.
        email = str(row[ei]).strip().lower() if len(row) > ei and row[ei] else ""
        nm_raw = str(row[ni]).strip().lower() if len(row) > ni and row[ni] else ""
        ident = email or nm_raw
        iso = d.isocalendar()
        wk = (iso[0], iso[1])
        if ident and (wk, ident) in seen:
            result["dupes"] += 1
            continue
        if ident:
            seen.add((wk, ident))
        url = str(row[ui]) if len(row) > ui and row[ui] else ""
        s = classify_source(url)
        result["forms"][s] += 1
        result["valid"].append((d, clean(row[ni] if len(row) > ni else ""),
                                clean(row[si] if len(row) > si else ""), s))
    result["valid"].sort(key=lambda t: t[0])
    return result


def match_windsor(account_name, hints):
    name_lower = (account_name or "").lower()
    return any(h in name_lower for h in hints)


def fetch_gbp_data(client_key, target_month, target_year):
    """GBP metrics from the Data Pulls 'GBP Data' tab. website_visits = the 'clicks' column."""
    cfg = CLIENTS[client_key]
    out = {"impressions": 0, "call_clicks": 0, "website_visits": 0, "direction_requests": 0}
    try:
        cols, rows = fetch_gviz(WINDSOR_SHEET_ID, WINDSOR_GBP_TAB)
    except Exception as e:
        print(f"  Warning: could not fetch GBP data for {client_key}: {e}")
        return out
    cmn = {c.lower(): i for i, c in enumerate(cols)}
    name_i = cmn.get("account_name", 0)
    date_i = cmn.get("date", 3)
    web_i = cmn.get("clicks", 1)          # GBP "clicks" column = website visits
    call_i = cmn.get("call_clicks", 5)
    dir_i = cmn.get("direction_requests", 6)
    imp_i = cmn.get("impressions", 7)
    kw_i = cmn.get("search_keyword", 13)

    def n(v):
        try:
            return float(v or 0)
        except (ValueError, TypeError):
            return 0.0

    for row in rows:
        if len(row) <= max(name_i, date_i):
            continue
        if not match_windsor(row[name_i], cfg["windsor_hints"]):
            continue
        d = row[date_i]
        if not (isinstance(d, date) and d.month == target_month and d.year == target_year):
            continue
        # skip keyword-only rows (they carry a search_keyword, no daily metrics)
        if len(row) > kw_i and row[kw_i] and str(row[kw_i]).strip():
            continue
        out["website_visits"] += n(row[web_i]) if len(row) > web_i else 0
        out["call_clicks"] += n(row[call_i]) if len(row) > call_i else 0
        out["direction_requests"] += n(row[dir_i]) if len(row) > dir_i else 0
        out["impressions"] += n(row[imp_i]) if len(row) > imp_i else 0
    return {k: int(round(v)) for k, v in out.items()}


def fetch_ads_data(client_key, target_month, target_year):
    """Google Ads spend/clicks/conversions from the Data Pulls 'GADS Data' tab."""
    cfg = CLIENTS[client_key]
    out = {"clicks": 0, "conversions": 0, "spend": 0.0, "days": 0}
    try:
        cols, rows = fetch_gviz(WINDSOR_SHEET_ID, WINDSOR_ADS_TAB)
    except Exception as e:
        print(f"  Warning: could not fetch Ads data for {client_key}: {e}")
        return out
    cmn = {c.lower(): i for i, c in enumerate(cols)}
    name_i = cmn.get("account_name", 0)
    date_i = cmn.get("date", 5)
    clicks_i = cmn.get("clicks", 2)
    conv_i = cmn.get("conversions", 4)
    spend_i = cmn.get("spend", 7)

    def n(v):
        try:
            return float(v or 0)
        except (ValueError, TypeError):
            return 0.0

    for row in rows:
        if len(row) <= max(name_i, date_i):
            continue
        if not match_windsor(row[name_i], cfg["windsor_hints"]):
            continue
        d = row[date_i]
        if not (isinstance(d, date) and d.month == target_month and d.year == target_year):
            continue
        out["clicks"] += int(n(row[clicks_i]) if len(row) > clicks_i else 0)
        out["conversions"] += n(row[conv_i]) if len(row) > conv_i else 0
        out["spend"] += n(row[spend_i]) if len(row) > spend_i else 0
        out["days"] += 1
    out["conversions"] = int(round(out["conversions"]))
    return out


_CALLS_CACHE = {}
def fetch_website_calls(client_key, target_month, target_year):
    """Validated website calls from the Data Pulls 'Calls' tab. Returns (answered, missed).
    Only ANSWERED count as valid SEO calls; missed are surfaced as a 'potential leads' note."""
    cfg = CLIENTS[client_key]
    key = (target_month, target_year)
    if key not in _CALLS_CACHE:
        label_map = {}
        try:
            at = google_access_token()
            req = Request(
                "https://sheets.googleapis.com/v4/spreadsheets/%s/values/Calls!A1:Z80" % WINDSOR_SHEET_ID,
                headers={"Authorization": "Bearer " + at})
            vals = json.load(urlopen(req)).get("values", [])
            header = next((r for r in vals if r and str(r[0]).strip() == "Month"), None)
            mname = f"{MONTH_NAMES[target_month]} {target_year}"
            mrow = next((r for r in vals if r and str(r[0]).strip().startswith(mname)), None)

            def _digits(cell):
                m = re.search(r"\d+", str(cell))  # first number only; avoid "4 + 3 Msgs" -> 43
                return int(m.group()) if m else 0

            if header and mrow:
                # group label sits on the client's "Answered" column; Missed = +1, Total = +2
                for i, lab in enumerate(header):
                    lab = str(lab or "").strip()
                    if lab and lab not in ("Month", "Type"):
                        answered = _digits(mrow[i]) if i < len(mrow) else 0
                        missed = _digits(mrow[i + 1]) if i + 1 < len(mrow) else 0
                        label_map[lab.lower()] = (answered, missed)
        except Exception as e:
            print(f"  Warning: could not read Calls tab: {e}")
        _CALLS_CACHE[key] = label_map
    lm = _CALLS_CACHE[key]
    want = cfg["calls_label"]
    for lab, am in lm.items():
        if want in lab or lab in want:
            return am
    return (0, 0)


def fetch_ad_call_leads(client_key, target_month, target_year):
    """Ad phone-call LEADS = ad-asset PHONE_CALL_LEAD conversions (Windsor API).
    Conservative: EXCLUDES website-attributed call conversions (e.g. 'Calls from Website') because
    those ring the website number and are already counted in SEO answered website calls. Counting
    them here too would double-claim. We would rather miss a few than over-claim."""
    cfg = CLIENTS[client_key]
    key = creds().get("WINDSOR_API_KEY", "")
    if not key:
        print("  Warning: no WINDSOR_API_KEY; ad call leads = 0")
        return 0
    last = calendar.monthrange(target_year, target_month)[1]
    url = ("https://connectors.windsor.ai/google_ads?api_key=%s&date_from=%04d-%02d-01&date_to=%04d-%02d-%02d"
           "&fields=account_name,conversion_action_name,conversion_action_category,conversions"
           % (key, target_year, target_month, target_year, target_month, last))
    try:
        data = json.load(urlopen(url, timeout=60))
        data = data.get("data", data) if isinstance(data, dict) else data
    except Exception as e:
        print(f"  Warning: Windsor ad-call-leads fetch failed: {e}")
        return 0
    tot = 0.0
    for r in data:
        if not match_windsor(r.get("account_name", ""), cfg["windsor_hints"]):
            continue
        if str(r.get("conversion_action_category", "")) == "PHONE_CALL_LEAD" \
                and "website" not in str(r.get("conversion_action_name", "")).lower():
            try:
                tot += float(r.get("conversions") or 0)
            except (ValueError, TypeError):
                pass
    return int(round(tot))


# ---------------------------------------------------------------------------
# REPORT (HTML)
# ---------------------------------------------------------------------------

CSS = """
@page{size:letter;margin:0}
*{margin:0;padding:0;box-sizing:border-box;-webkit-print-color-adjust:exact;print-color-adjust:exact}
html,body{-webkit-print-color-adjust:exact;print-color-adjust:exact}
body{font-family:'Sora',system-ui,sans-serif;font-weight:400;color:#0A0A0A;background:#F8F6F2;max-width:800px;margin:0 auto;padding:34px;font-size:13px;line-height:1.5}
h2{font-family:'Sora',sans-serif;font-weight:800;text-transform:uppercase;font-size:18px;color:#0A0A0A;letter-spacing:-.01em;margin:24px 0 12px;position:relative;display:inline-block;padding:2px 2px 0}
h2::before,h2::after{content:"";position:absolute;width:14px;height:14px;border:2px solid #FB5607}
h2::before{top:0;left:-16px;border-right:0;border-bottom:0}
h2::after{bottom:0;right:-16px;border-left:0;border-top:0}
.divider{height:1px;background:#D4D0C8;border:0;margin:24px 0}
.report-header{display:flex;justify-content:space-between;align-items:flex-end;border-bottom:4px solid #FB5607;padding-bottom:14px;margin-bottom:18px}
.report-header .brand-logo{height:26px;width:auto;display:block;margin-bottom:8px}
.report-header .brand-fallback{font-weight:800;font-size:22px;color:#0A0A0A;margin-bottom:8px}
.report-header .formerly{font-weight:400;font-size:10px;color:#8A8A8A;letter-spacing:.04em}
.report-header .meta{font-size:11px;color:#525252;text-align:right;line-height:1.5}
.report-header .meta b{color:#0A0A0A}
.report-header .agency{font-weight:700;text-transform:uppercase;font-size:11px;color:#FB5607;letter-spacing:.12em}
.client-name{font-weight:800;text-transform:uppercase;font-size:26px;color:#0A0A0A;line-height:1.05;letter-spacing:-.02em;margin-bottom:16px}
.hero{display:flex;gap:14px;margin-bottom:6px}
.hero .s{flex:1;background:#fff;border:1px solid #0A0A0A;border-radius:10px;box-shadow:3px 3px 0 0 #0A0A0A;padding:18px 14px;text-align:center}
.hero .s.lead{background:#FFE8D9}
.hero .n{font-weight:800;font-size:30px;color:#FB5607;line-height:1;letter-spacing:-.02em}
.hero .l{font-weight:600;text-transform:uppercase;font-size:9px;letter-spacing:.07em;color:#525252;margin-top:8px}
.cap{font-size:11.5px;color:#8A8A8A;margin:2px 0 10px}
.legend{display:flex;justify-content:space-between;align-items:center;gap:12px;margin-bottom:14px}
.legend .keys{display:flex;flex-wrap:wrap;gap:14px;font-size:10px;color:#525252}
.legend .keys span{display:inline-flex;align-items:center;gap:6px;text-transform:uppercase;letter-spacing:.05em;font-weight:700}
.cumtag{font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:.1em;color:#8A8A8A;white-space:nowrap}
.cardnote{margin-top:14px;padding-top:11px;border-top:1px solid #E5E2DC;font-size:11px;color:#525252;line-height:1.5}
.cardnote b{color:#FB5607}
.sw{width:11px;height:11px;border-radius:2px;display:inline-block}
.chart{background:#fff;border:1px solid #0A0A0A;border-radius:10px;box-shadow:3px 3px 0 0 #0A0A0A;padding:18px 20px}
.bar-row{display:flex;align-items:center;gap:12px;margin:9px 0}
.bar-label{width:120px;font-size:12px;font-weight:600;color:#0A0A0A;flex:0 0 auto}
.bar-track{flex:1;display:flex;background:#EDEAE3;border-radius:5px;height:22px;overflow:hidden}
.seg{height:100%}
.bar-val{width:108px;text-align:right;font-weight:800;font-size:15px;color:#0A0A0A;flex:0 0 auto;line-height:1.1}
.bar-sub{display:block;font-weight:600;font-size:9.5px;color:#8A8A8A;letter-spacing:.02em}
.kpis{display:flex;gap:14px}
.kpi{flex:1;background:#fff;border:1px solid #0A0A0A;border-radius:10px;box-shadow:3px 3px 0 0 #0A0A0A;padding:16px 12px;text-align:center}
.kpi .v{font-weight:800;font-size:25px;color:#0A0A0A;line-height:1;letter-spacing:-.02em}
.kpi .k{font-weight:600;text-transform:uppercase;font-size:9px;letter-spacing:.06em;color:#525252;margin-top:8px}
.table-wrap{background:#fff;border:1px solid #0A0A0A;border-radius:10px;overflow:hidden;margin-top:4px}
table{width:100%;border-collapse:collapse;font-size:12px}
thead tr{background:#0A0A0A;color:#fff}
th{font-weight:800;text-transform:uppercase;padding:8px 12px;text-align:left;font-size:12px;letter-spacing:.04em}
td{padding:7px 12px;border-bottom:1px solid #E5E2DC;vertical-align:top}
tbody tr:last-child td{border-bottom:none}
tbody tr:nth-child(even){background:#F8F6F2}
.chip{display:inline-flex;align-items:center;gap:6px;padding:3px 10px;border-radius:4px;font-weight:700;font-size:10px;text-transform:uppercase;letter-spacing:.05em;white-space:nowrap}
.chip i{width:6px;height:6px;border-radius:50%;display:inline-block;flex:0 0 auto}
.report-footer{border-top:2px solid #FB5607;padding-top:10px;margin-top:30px;font-size:11px;color:#525252;text-align:center}
"""

ADS_SERIES = {"Clicks": "#FB5607", "Conversions": "#0A0A0A"}
GBP_SERIES = {"Profile Views": "#34A853", "Website Visits": "#1877F2", "Calls": "#0A0A0A"}


def _line_svg(series, ndays, colordict):
    allvals = [v for arr in series.values() for v in arr]
    ymax = max(allvals + [1])
    L, R, T, Bm, VBW, VBH = 34, 14, 12, 22, 760, 200
    W = VBW - L - R; Ph = VBH - T - Bm
    def X(day): return L + (day - 1) * (W / float(max(ndays - 1, 1)))
    def Yv(v): return T + Ph - (v / float(ymax) * Ph)
    out = ['<svg viewBox="0 0 %d %d" width="100%%" preserveAspectRatio="xMidYMid meet" font-family="Sora,sans-serif">' % (VBW, VBH)]
    for v in sorted(set([0, ymax // 2, ymax])):
        yy = Yv(v)
        out.append('<line x1="%d" y1="%.1f" x2="%d" y2="%.1f" stroke="#E5E2DC" stroke-width="1"/>' % (L, yy, VBW - R, yy))
        out.append('<text x="%d" y="%.1f" font-size="9" fill="#8A8A8A" text-anchor="end">%d</text>' % (L - 6, yy + 3, v))
    for day in sorted(set([1, 5, 10, 15, 20, 25, ndays])):
        out.append('<text x="%.1f" y="%d" font-size="9" fill="#8A8A8A" text-anchor="middle">%d</text>' % (X(day), VBH - 6, day))
    for name, arr in series.items():
        col = colordict[name]
        pts = " ".join("%.1f,%.1f" % (X(d), Yv(arr[d - 1])) for d in range(1, ndays + 1))
        out.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.5" stroke-linejoin="round" stroke-linecap="round"/>' % (pts, col))
        out.append('<circle cx="%.1f" cy="%.1f" r="3" fill="%s"/>' % (X(ndays), Yv(arr[-1]), col))
    out.append('</svg>')
    return "".join(out)


def _keys_html(cd):
    return "".join('<span><i class="sw" style="background:%s"></i>%s</span>' % (c, _html.escape(n)) for n, c in cd.items())


def _daily_from_tab(tab, valuecol, hints, month, year, ndays):
    try:
        cols, rows = fetch_gviz(WINDSOR_SHEET_ID, tab)
    except Exception:
        return [0.0] * ndays
    idx = {c: i for i, c in enumerate(cols)}
    name_i = idx.get("account_name", 0); date_i = idx.get("date", 5); val_i = idx.get(valuecol)
    if val_i is None:
        return [0.0] * ndays
    arr = [0.0] * (ndays + 1)
    for r in rows:
        if len(r) <= max(name_i, date_i, val_i):
            continue
        if not match_windsor(r[name_i], hints):
            continue
        d = r[date_i]
        if not (isinstance(d, date) and d.month == month and d.year == year):
            continue
        try:
            arr[d.day] += float(r[val_i] or 0)
        except Exception:
            pass
    return [arr[day] for day in range(1, ndays + 1)]


def build_html_report(client_key, leads, gbp, ads, calls, target_month, target_year, website_missed=0):
    cfg = CLIENTS[client_key]
    full_name = cfg["full_name"]
    mname = f"{MONTH_NAMES[target_month]} {target_year}"
    forms = leads["forms"]
    valid = leads["valid"]
    spam = leads["spam"]

    form_total = sum(forms.values())
    call_total = sum(calls.values())
    grand = form_total + call_total
    spend = float(ads.get("spend", 0))
    clicks = int(ads.get("clicks", 0))
    conv = int(ads.get("conversions", 0))
    cpl = (spend / conv) if conv else 0

    # stacked bars (forms solid + calls tint)
    totals = {s: forms.get(s, 0) + calls.get(s, 0) for s in SOURCES}
    mx = max(list(totals.values()) + [1])
    bars = ""
    for s in SOURCES:
        f, c, t = forms.get(s, 0), calls.get(s, 0), totals[s]
        detail = "%d forms" % f + (" &middot; %d calls" % c if c else "")
        col = SOURCE_COLOR[s]
        bars += ('<div class="bar-row"><div class="bar-label">%s</div>'
                 '<div class="bar-track"><div class="seg" style="width:%.2f%%;background:%s"></div>'
                 '<div class="seg" style="width:%.2f%%;background:%s66"></div></div>'
                 '<div class="bar-val">%d<span class="bar-sub">%s</span></div></div>'
                 % (_html.escape(s), f / mx * 100, col, c / mx * 100, col, t, detail))

    # cumulative leads line + daily ads/gbp lines
    nd = calendar.monthrange(target_year, target_month)[1]
    daily = {s: [0] * (nd + 1) for s in SOURCES}
    for d, _n, _se, s in valid:
        daily[s][d.day] += 1
    cum = {}
    for s in SOURCES:
        run = 0; arr = []
        for day in range(1, nd + 1):
            run += daily[s][day]; arr.append(run)
        cum[s] = arr
    drawn = [s for s in SOURCES if cum[s][-1] > 0]
    leads_line = _line_svg({s: cum[s] for s in drawn}, nd, SOURCE_COLOR)
    srclegend = _keys_html({s: SOURCE_COLOR[s] for s in drawn})

    hints = cfg["windsor_hints"]
    ads_line = _line_svg({"Clicks": _daily_from_tab("GADS Data", "clicks", hints, target_month, target_year, nd),
                          "Conversions": _daily_from_tab("GADS Data", "conversions", hints, target_month, target_year, nd)}, nd, ADS_SERIES)
    gbp_line = _line_svg({"Profile Views": _daily_from_tab("GBP Data", "impressions", hints, target_month, target_year, nd),
                          "Website Visits": _daily_from_tab("GBP Data", "clicks", hints, target_month, target_year, nd),
                          "Calls": _daily_from_tab("GBP Data", "call_clicks", hints, target_month, target_year, nd)}, nd, GBP_SERIES)
    ads_keys = _keys_html(ADS_SERIES)
    gbp_keys = _keys_html(GBP_SERIES)

    unanswered_note = ("" if website_missed <= 0 else
        '<div class="cardnote"><b>%d calls</b> went unanswered this month, each a potential lead.</div>' % website_missed)

    # form table
    def chip(s):
        c = SOURCE_COLOR[s]
        return '<span class="chip" style="color:%s;background:%s14;border:1px solid %s44"><i style="background:%s"></i>%s</span>' % (c, c, c, c, _html.escape(s))
    trs = "".join('<tr><td>%s %d</td><td>%s</td><td>%s</td><td>%s</td></tr>'
                  % (d.strftime("%b"), d.day, nme, svc, chip(s)) for d, nme, svc, s in valid)

    doc = """<!DOCTYPE html><html><head><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Sora:wght@400;600;700;800&display=swap" rel="stylesheet">
<style>%s</style></head><body>
<div class="report-header">
 <div>%s<div class="formerly">(Formerly VicTree Websites LLC)</div></div>
 <div class="meta"><span class="agency">Monthly Performance Report</span><br><b>%s</b><br>%s</div>
</div>
<div class="client-name">%s</div>
<div class="hero">
 <div class="s lead"><div class="n">%d</div><div class="l">Total Leads</div></div>
 <div class="s"><div class="n">%d</div><div class="l">Website Forms</div></div>
 <div class="s"><div class="n">%d</div><div class="l">Phone Calls</div></div>
 <div class="s"><div class="n">$%s</div><div class="l">Ad Spend</div></div>
</div>
<div class="divider"></div>
<h2>Leads by Source</h2>
<p class="cap">Form submissions and phone calls combined, by channel. %d spam submissions were filtered out. Calls are tracked on separate numbers per channel, so no lead is counted twice. Website calls are attributed to SEO.</p>
<div class="chart"><div class="legend"><div class="keys"><span><i class="sw" style="background:#0A0A0A"></i>Form leads</span><span><i class="sw" style="background:#0A0A0A66"></i>Phone calls</span></div></div>%s%s</div>
<p class="cap" style="margin-top:16px">How your website form leads added up over the month, by source. Each line steps up with every lead and holds flat on days with none.</p>
<div class="chart"><div class="legend"><div class="keys">%s</div><span class="cumtag">Cumulative</span></div>%s</div>
<div class="divider"></div>
<h2>Google Ads Performance</h2>
<div class="kpis">
 <div class="kpi"><div class="v">$%s</div><div class="k">Spend</div></div>
 <div class="kpi"><div class="v">%d</div><div class="k">Clicks</div></div>
 <div class="kpi"><div class="v">%d</div><div class="k">Conversions</div></div>
 <div class="kpi"><div class="v">$%d</div><div class="k">Cost / Conversion</div></div>
</div>
<p class="cap" style="margin-top:14px">Daily ad clicks and conversions across the month.</p>
<div class="chart"><div class="legend"><div class="keys">%s</div></div>%s</div>
<div class="divider"></div>
<h2>Google Business Profile</h2>
<div class="kpis">
 <div class="kpi"><div class="v">%d</div><div class="k">Profile Views</div></div>
 <div class="kpi"><div class="v">%d</div><div class="k">Website Visits</div></div>
 <div class="kpi"><div class="v">%d</div><div class="k">Calls</div></div>
 <div class="kpi"><div class="v">%d</div><div class="k">Direction Requests</div></div>
</div>
<p class="cap" style="margin-top:14px">Daily Google Business Profile views, website visits, and calls across the month.</p>
<div class="chart"><div class="legend"><div class="keys">%s</div></div>%s</div>
<div class="divider"></div>
<h2>All Website Form Leads</h2>
<p class="cap">All %d valid form leads for %s, in date order.</p>
<div class="table-wrap"><table><thead><tr><th>Date</th><th>Name</th><th>Service Needed</th><th>Source</th></tr></thead><tbody>%s</tbody></table></div>
<div class="report-footer">22 Local Marketing &nbsp;|&nbsp; 22localmarketing.com &nbsp;|&nbsp; Confidential, prepared for %s</div>
</body></html>""" % (
        CSS, LOGO_TAG, mname, cfg["location"], _html.escape(full_name),
        grand, form_total, call_total, "{:,.0f}".format(spend),
        spam, bars, unanswered_note, srclegend, leads_line,
        "{:,.0f}".format(spend), clicks, conv, round(cpl), ads_keys, ads_line,
        gbp.get("impressions", 0), gbp.get("website_visits", 0), gbp.get("call_clicks", 0), gbp.get("direction_requests", 0), gbp_keys, gbp_line,
        form_total, mname, trs,
        _html.escape(full_name),
    )
    return doc


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------

def html_to_pdf(html_path, pdf_path):
    """Convert HTML to PDF. Primary: Cloudflare Browser Rendering via agent/html2pdf.py
    (real headless Chrome, auto-injects print-color-adjust). Fallbacks: weasyprint, headless Edge/Chrome."""
    if os.path.exists(pdf_path):
        try:
            os.remove(pdf_path)
        except Exception:
            pass
    # 1) Cloudflare Browser Rendering helper (preferred)
    helper = r"C:\22 Local Marketing\agent\html2pdf.py"
    if os.path.exists(helper):
        try:
            subprocess.run([sys.executable, helper, "--html", html_path, "--out", pdf_path],
                           timeout=240, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            if os.path.exists(pdf_path) and os.path.getsize(pdf_path) > 1000:
                return "cloudflare"
        except Exception:
            pass
    # 2) weasyprint
    try:
        from weasyprint import HTML as WeasyHTML
        WeasyHTML(filename=html_path).write_pdf(pdf_path)
        return "weasyprint"
    except Exception:
        pass
    candidates = [
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    ]
    exe = next((b for b in candidates if os.path.exists(b)), None) or shutil.which("msedge") or shutil.which("chrome")
    if not exe:
        return None
    file_url = "file:///" + os.path.abspath(html_path).replace("\\", "/")
    profile = tempfile.mkdtemp(prefix="22lm_pdf_")
    if os.path.exists(pdf_path):
        os.remove(pdf_path)
    try:
        subprocess.run([exe, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
                        "--user-data-dir=" + profile, "--print-to-pdf=" + pdf_path, file_url],
                       timeout=120, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        # headless browsers can hand off to a worker and return early; poll for the finished file
        deadline = time.time() + 60
        last = -1
        while time.time() < deadline:
            if os.path.exists(pdf_path):
                sz = os.path.getsize(pdf_path)
                if sz > 1000 and sz == last:
                    break
                last = sz
            time.sleep(0.5)
    except Exception:
        return None
    finally:
        shutil.rmtree(profile, ignore_errors=True)
    return ("edge/chrome" if (os.path.exists(pdf_path) and os.path.getsize(pdf_path) > 1000) else None)


def generate_report(client_key, target_month, target_year, output_dir):
    cfg = CLIENTS[client_key]
    print(f"\n{'='*60}\n  {cfg['full_name']}\n{'='*60}")

    leads = fetch_leads(client_key, target_month, target_year)
    gbp = fetch_gbp_data(client_key, target_month, target_year)
    ads = fetch_ads_data(client_key, target_month, target_year)
    website_answered, website_missed = fetch_website_calls(client_key, target_month, target_year)
    ad_calls = fetch_ad_call_leads(client_key, target_month, target_year)
    gbp_calls = gbp.get("call_clicks", 0)

    # Only ANSWERED website calls count as valid SEO calls; missed are noted as potential leads.
    calls = {"Google Ads": ad_calls, "SEO": website_answered, "Google Business": gbp_calls,
             "AI / ChatGPT": 0, "Facebook": 0}

    print(f"    Forms: {dict(leads['forms'])} (spam {leads['spam']})")
    print(f"    Calls: Ads {ad_calls} | Website/SEO {website_answered} answered ({website_missed} missed) | GBP {gbp_calls}")
    print(f"    Ads: ${ads.get('spend',0):,.2f} spend, {ads.get('clicks',0)} clicks, {ads.get('conversions',0)} conv")
    print(f"    GBP: {gbp.get('impressions',0)} views, {gbp.get('website_visits',0)} web visits, {gbp.get('direction_requests',0)} directions")

    html = build_html_report(client_key, leads, gbp, ads, calls, target_month, target_year, website_missed)

    month_name = MONTH_NAMES[target_month]
    safe = cfg["full_name"].replace(" ", "-").replace(",", "").replace(".", "")
    base = f"{safe}-{month_name}-{target_year}"
    html_path = os.path.join(output_dir, f"{base}.html")
    pdf_path = os.path.join(output_dir, f"{base}.pdf")
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html)
    engine = html_to_pdf(html_path, pdf_path)
    if engine:
        print(f"  PDF saved ({engine}): {pdf_path}")
    else:
        print(f"  PDF conversion unavailable; HTML saved: {html_path}")
    return pdf_path if engine else html_path


def main():
    parser = argparse.ArgumentParser(description="Generate 22 Local Marketing monthly client reports")
    parser.add_argument("--month", type=int, default=None)
    parser.add_argument("--year", type=int, default=None)
    parser.add_argument("--client", type=str, default=None)
    parser.add_argument("--output", type=str, default=".")
    parser.add_argument("--include-elite", action="store_true", help="Include Elite (skipped by default)")
    args = parser.parse_args()

    today = date.today()
    if args.month is None:
        target_month = 12 if today.month == 1 else today.month - 1
        target_year = today.year - 1 if today.month == 1 else today.year
    else:
        target_month = args.month
        target_year = args.year or today.year

    os.makedirs(args.output, exist_ok=True)
    print(f"\n22 Local Marketing - Monthly Report Generator")
    print(f"Report Period: {MONTH_NAMES[target_month]} {target_year}\nOutput: {args.output}")

    if args.client:
        matched = next((k for k in CLIENTS
                        if args.client.lower() in k.lower() or args.client.lower() in CLIENTS[k]["full_name"].lower()), None)
        if not matched:
            print(f"\nError: client '{args.client}' not found. Available: {', '.join(CLIENTS)}")
            sys.exit(1)
        generate_report(matched, target_month, target_year, args.output)
    else:
        for client_key in CLIENTS:
            if client_key in SKIP_CLIENTS and not args.include_elite:
                print(f"\n(skipping {client_key})")
                continue
            generate_report(client_key, target_month, target_year, args.output)

    print(f"\n{'='*60}\n  All reports complete.\n{'='*60}\n")


if __name__ == "__main__":
    main()
