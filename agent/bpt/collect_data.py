#!/usr/bin/env python3
"""
22 Local Marketing - deterministic WQA data collector.

Pulls GA4 + GSC server-side using the Google OAuth refresh token in .creds and
writes the exact JSON files the WQA scripts (build_audit_xlsx.py / build_report.py)
consume. Returns a compact summary only - no row data is printed, so this stays
cheap to call from an agent. Each source is collected independently: if one API
is unavailable the others still write, and the summary reports what failed.

Usage:
  python collect_data.py \
    --audit-dir "C:/.../wqa/audits/<id>" \
    --slug bwlm \
    --ga4-property 520284516 \
    --gsc-site "sc-domain:betterwaylandmanagement.com" \
    --root-domain https://betterwaylandmanagement.com \
    [--as-of 2026-06-18] [--creds "C:/Agency Operations/agent/.creds"]
"""
import argparse, json, os, urllib.request, urllib.parse, urllib.error
from datetime import date, timedelta

GA4_URL = "https://analyticsdata.googleapis.com/v1beta/properties/{pid}:runReport"
GSC_URL = "https://searchconsole.googleapis.com/webmasters/v3/sites/{site}/searchAnalytics/query"
TOKEN_URL = "https://oauth2.googleapis.com/token"


def parse_creds(path):
    creds = {}
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            creds[k.strip()] = v.strip().strip('"')
    return creds


def post_json(url, body, token=None, form=False):
    if form:
        data = urllib.parse.urlencode(body).encode()
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
    else:
        data = json.dumps(body).encode()
        headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = "Bearer " + token
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        try:
            msg = json.loads(e.read().decode()).get("error", {}).get("message", "")[:200]
        except Exception:
            msg = ""
        raise RuntimeError(f"HTTP {e.code} ({url.split('/')[2]}): {msg}")


def access_token(creds):
    resp = post_json(TOKEN_URL, {
        "client_id": creds["GOOGLE_CLIENT_ID"],
        "client_secret": creds["GOOGLE_CLIENT_SECRET"],
        "refresh_token": creds["GOOGLE_REFRESH_TOKEN"],
        "grant_type": "refresh_token",
    }, form=True)
    if "access_token" not in resp:
        raise SystemExit("ERROR: token refresh failed: " + json.dumps(resp)[:300])
    return resp["access_token"]


def norm(u):
    return u.split("?")[0].split("#")[0].rstrip("/").lower() if u else ""


def ga4(token, pid, dims, metrics, start, end):
    body = {"dateRanges": [{"startDate": start, "endDate": end}],
            "dimensions": [{"name": d} for d in dims],
            "metrics": [{"name": m} for m in metrics], "limit": 100000}
    return post_json(GA4_URL.format(pid=pid), body, token=token).get("rows", [])


def gsc(token, site, dims, start, end, row_limit=25000):
    enc = urllib.parse.quote(site, safe="")
    body = {"startDate": start, "endDate": end, "dimensions": dims, "rowLimit": row_limit}
    return post_json(GSC_URL.format(site=enc), body, token=token).get("rows", [])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--audit-dir", required=True)
    ap.add_argument("--slug", required=True)
    ap.add_argument("--ga4-property", required=True)
    ap.add_argument("--gsc-site", required=True)
    ap.add_argument("--root-domain", required=True)
    ap.add_argument("--as-of", default=date.today().isoformat())
    ap.add_argument("--creds", default=r"C:/Agency Operations/agent/.creds")
    a = ap.parse_args()

    creds = parse_creds(a.creds)
    tok = access_token(creds)
    pid = a.ga4_property.replace("properties/", "")
    root = a.root_domain.rstrip("/")
    as_of = date.fromisoformat(a.as_of)
    cur_s, cur_e = (as_of - timedelta(days=90)).isoformat(), as_of.isoformat()
    pri_s, pri_e = (as_of - timedelta(days=180)).isoformat(), (as_of - timedelta(days=91)).isoformat()
    mon_s = (as_of - timedelta(days=485)).isoformat()

    os.makedirs(a.audit_dir, exist_ok=True)
    def out(name): return os.path.join(a.audit_dir, f"{a.slug}-{name}")
    def save(name, obj): json.dump(obj, open(out(name), "w", encoding="utf-8"))

    ok, fail = [], []

    def step(label, fn):
        try:
            fn(); ok.append(label)
        except Exception as e:
            fail.append(f"{label}: {e}")

    def ga4_pages():
        rows = ga4(tok, pid, ["pagePath"], ["sessions", "totalUsers", "engagementRate", "keyEvents"], cur_s, cur_e)
        data = [{"page_location": root + r["dimensionValues"][0]["value"],
                 "sessions": int(r["metricValues"][0]["value"]),
                 "users": int(r["metricValues"][1]["value"]),
                 "engagement_rate": round(float(r["metricValues"][2]["value"]), 4),
                 "conversions": int(r["metricValues"][3]["value"])} for r in rows]
        save("ga4.json", data)
        ga4_pages.total = sum(d["sessions"] for d in data); ga4_pages.n = len(data)

    def ga4_monthly():
        rows = ga4(tok, pid, ["yearMonth", "sessionDefaultChannelGroup"], ["sessions"], mon_s, cur_e)
        organic, total = {}, {}
        for r in rows:
            ym = r["dimensionValues"][0]["value"]          # YYYYMM
            month = ym[:4] + "-" + ym[4:6]                 # YYYY-MM
            ch = r["dimensionValues"][1]["value"]
            s = int(r["metricValues"][0]["value"])
            total[month] = total.get(month, 0) + s
            if ch == "Organic Search":
                organic[month] = organic.get(month, 0) + s
        save("ga4-monthly.json", {
            "organic": [{"month": m, "sessions": organic[m]} for m in sorted(organic)],
            "total": [{"month": m, "sessions": total[m]} for m in sorted(total)],
        })

    def gsc_pages():
        rows = gsc(tok, a.gsc_site, ["page"], cur_s, cur_e)
        data = [{"page": r["keys"][0], "clicks": r["clicks"], "impressions": r["impressions"],
                 "position": round(r["position"], 2)} for r in rows]
        save("gsc.json", data)
        gsc_pages.clicks = sum(d["clicks"] for d in data)
        gsc_pages.impr = sum(d["impressions"] for d in data); gsc_pages.n = len(data)

    def gsc_prior():
        rows = gsc(tok, a.gsc_site, ["page"], pri_s, pri_e)
        save("gsc-90d-prior.json", {"by_page": {norm(r["keys"][0]): {"clicks": r["clicks"],
             "impressions": r["impressions"], "position": round(r["position"], 2),
             "ctr": round(r["ctr"], 4)} for r in rows}})

    def gsc_monthly():
        rows = gsc(tok, a.gsc_site, ["date"], mon_s, cur_e, row_limit=5000)
        agg = {}
        for r in rows:
            month = r["keys"][0][:7]  # YYYY-MM from YYYY-MM-DD
            d = agg.setdefault(month, {"clicks": 0, "impressions": 0})
            d["clicks"] += r["clicks"]; d["impressions"] += r["impressions"]
        save("gsc-monthly.json", [{"month": m, "clicks": agg[m]["clicks"],
             "impressions": agg[m]["impressions"]} for m in sorted(agg)])

    step("ga4.json", ga4_pages)
    step("ga4-monthly.json", ga4_monthly)
    step("gsc.json", gsc_pages)
    step("gsc-90d-prior.json", gsc_prior)
    step("gsc-monthly.json", gsc_monthly)

    print(f"Collected for {a.slug}  (current {cur_s}..{cur_e})")
    if hasattr(gsc_pages, "n"):
        print(f"  GSC: {gsc_pages.n} pages, clicks(90d)={gsc_pages.clicks}, impressions(90d)={gsc_pages.impr}")
    if hasattr(ga4_pages, "n"):
        print(f"  GA4: {ga4_pages.n} pages, sessions(90d)={ga4_pages.total}")
    print(f"  OK: {', '.join(ok) if ok else 'none'}")
    if fail:
        print("  FAILED:")
        for f in fail:
            print(f"    - {f}")


if __name__ == "__main__":
    main()
