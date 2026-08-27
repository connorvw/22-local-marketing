#!/usr/bin/env python3
"""
22 Local Marketing - local-contractor proposal generator (owned).

Deterministic, self-contained HTML deck for local contractors. Renders ONLY
sections backed by data we actually have (GA4 + GSC from collect_data.py, the
Screaming Frog crawl, and Local Falcon) but renders them in DEPTH: full on-page
SEO audit, content + crawl-depth distributions, indexability/status breakdown,
and search-position distribution. No Ahrefs / AI / backlink / pricing slides.
Sora type, Blaze accent, 22LM brand.
"""
import argparse, json, os, statistics
from collections import Counter
from datetime import date

MONTHS = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
ASSET = (".jpg",".jpeg",".png",".webp",".gif",".svg",".css",".js",".pdf",".ico",".woff",".woff2",".xml")


def load(p, d=None):
    try:
        with open(p, encoding="utf-8") as f: return json.load(f)
    except Exception: return d if d is not None else None

def norm(u): return (u or "").split("?")[0].split("#")[0].rstrip("/").lower()
def mlabel(ym): y,m = ym.split("-"); return f"{MONTHS[int(m)-1]} '{y[2:]}"
def pct(n, t): return round(n/t*100) if t else 0


def main():
    ap = argparse.ArgumentParser()
    for x in ["audit-dir","slug","client-name","location","root-domain","crawl"]:
        ap.add_argument("--"+x, required=True)
    ap.add_argument("--localfalcon", default=None)
    ap.add_argument("--ahrefs-audit", default=None)
    ap.add_argument("--brand-color", default="#FB5607")
    ap.add_argument("--as-of", default=date.today().isoformat())
    a = ap.parse_args()
    A, S, ROOT = a.audit_dir, a.slug, a.root_domain.rstrip("/")
    P = lambda n: os.path.join(A, f"{S}-{n}")
    pathof = lambda u: (u or "").replace(ROOT, "") or "/"

    gsc = load(P("gsc.json"), [])
    ga4m = load(P("ga4-monthly.json"), {"organic": [], "total": []})
    cr = load(a.crawl, []); pages = cr.get("pages", cr) if isinstance(cr, dict) else cr
    lf = load(a.localfalcon, {}) if a.localfalcon else {}
    aa = load(a.ahrefs_audit, {}) if a.ahrefs_audit else {}

    # ---- organic trend ----
    org = sorted(ga4m.get("organic", []), key=lambda r: r["month"])
    peak = max(org, key=lambda r: r["sessions"]) if org else {"month":"","sessions":0}
    cm = org[-1] if org else {"month":"","sessions":0}
    org90 = sum(r["sessions"] for r in org[-3:])
    declined = peak["sessions"] > 0 and cm["sessions"] < 0.7*peak["sessions"]
    dpct = pct(peak["sessions"]-cm["sessions"], peak["sessions"]) if peak["sessions"] else 0

    # ---- GSC ----
    gclicks = sum(p["clicks"] for p in gsc); gimpr = sum(p["impressions"] for p in gsc)
    avg_pos = round(sum(p["position"]*p["impressions"] for p in gsc)/gimpr, 1) if gimpr else 0
    gsc_by = {norm(p["page"]): p for p in gsc}
    top_pages = sorted([p for p in gsc if p["clicks"] or p["impressions"]>50], key=lambda p:-p["clicks"])[:12]
    posdist = [("Top 3", sum(1 for p in gsc if p["position"]<=3)),
               ("4-10", sum(1 for p in gsc if 3<p["position"]<=10)),
               ("11-20", sum(1 for p in gsc if 10<p["position"]<=20)),
               ("21+", sum(1 for p in gsc if p["position"]>20))]
    striking = sorted([p for p in gsc if 5<=p["position"]<=15 and p["impressions"]>=300], key=lambda p:-p["impressions"])[:10]
    lowctr = sorted([p for p in gsc if p["impressions"]>=800 and p["clicks"]/p["impressions"]<0.02], key=lambda p:-p["impressions"])[:10]

    # ---- crawl: content pages ----
    html200 = [p for p in pages if str(p.get("status_code"))=="200"
               and (p.get("title") or p.get("word_count") is not None)
               and not pathof(p.get("url","")).lower().endswith(ASSET)]
    content = [p for p in html200 if (p.get("indexability") or "Indexable")=="Indexable"]
    nC = len(content)
    titles = Counter(norm(p.get("title") or "") for p in content if p.get("title"))
    metas = Counter((p.get("meta_description") or "").strip().lower() for p in content if p.get("meta_description"))
    def ln(x): return len(x or "")
    miss_title = [p for p in content if not p.get("title")]
    miss_meta = [p for p in content if not p.get("meta_description")]
    miss_h1 = [p for p in content if not p.get("h1")]
    dup_title = sum(c for t,c in titles.items() if t and c>1)
    dup_meta = sum(c for t,c in metas.items() if t and c>1)
    title_len = [p for p in content if p.get("title") and not (30<=ln(p["title"])<=60)]
    meta_len = [p for p in content if p.get("meta_description") and not (70<=ln(p["meta_description"])<=160)]
    thin = sorted([p for p in content if isinstance(p.get("word_count"),(int,float)) and p["word_count"]<300], key=lambda p: p["word_count"])
    noindex = [p for p in html200 if p.get("indexability") and p["indexability"]!="Indexable"]
    orphans = [p for p in content if isinstance(p.get("inlinks"),(int,float)) and p["inlinks"]<=1]
    wc = [p["word_count"] for p in content if isinstance(p.get("word_count"),(int,float)) and p["word_count"]>0]
    avg_wc = round(statistics.mean(wc)) if wc else 0
    med_wc = round(statistics.median(wc)) if wc else 0

    # status across ALL crawled urls
    sc = Counter(str(p.get("status_code")) for p in pages)
    n200 = sum(v for k,v in sc.items() if k.startswith("2"))
    n3 = sum(v for k,v in sc.items() if k.startswith("3"))
    n4 = sum(v for k,v in sc.items() if k.startswith("4"))
    p404 = [p for p in pages if str(p.get("status_code"))=="404"]
    p404s = sorted([(p.get("url",""), (gsc_by.get(norm(p.get("url",""))) or {}).get("impressions",0)) for p in p404], key=lambda x:-x[1])
    redirects = [p for p in pages if str(p.get("status_code")).startswith("3")]

    wc_buckets = [("Under 300", sum(1 for w in wc if w<300)), ("300-599", sum(1 for w in wc if 300<=w<600)),
                  ("600-999", sum(1 for w in wc if 600<=w<1000)), ("1000-1999", sum(1 for w in wc if 1000<=w<2000)),
                  ("2000+", sum(1 for w in wc if w>=2000))]
    depths = [p.get("crawl_depth") for p in content if isinstance(p.get("crawl_depth"),(int,float))]
    depth_buckets = [(str(d), sum(1 for x in depths if x==d)) for d in range(0,4)] + [("4+", sum(1 for x in depths if x>=4))]

    def sev(c, warn=1, fail=None):
        if c==0: return ("pass","Pass")
        fail = fail if fail is not None else max(8, nC//8)
        return ("fail","Fix" if c>=fail else "warn","Improve")[0:2] if c>=fail else ("warn","Improve")
    # simpler severity
    def status3(c, fail_at):
        if c==0: return ("#16a34a","Pass")
        if c>=fail_at: return ("#ef4444","Action needed")
        return ("#eab308","Improve")
    audit = [
        ("Missing title tags", len(miss_title), 1),
        ("Duplicate title tags", dup_title, 2),
        ("Title length outside 30-60 chars", len(title_len), max(10,nC//4)),
        ("Missing meta descriptions", len(miss_meta), max(5,nC//5)),
        ("Duplicate meta descriptions", dup_meta, 2),
        ("Meta length outside 70-160 chars", len(meta_len), max(10,nC//4)),
        ("Missing H1", len(miss_h1), 1),
        ("Thin content (under 300 words)", len(thin), 5),
        ("Non-indexable content pages", len(noindex), 3),
        ("Broken pages (404)", len(p404), 1),
        ("Redirects (3xx)", len(redirects), max(8,nC//6)),
        ("Orphan pages (<=1 internal link)", len(orphans), 5),
    ]

    rep = f"a {lf.get('rating')}-star reputation on {lf.get('reviews')} reviews" if lf.get("rating") else "a strong local reputation"
    if declined:
        story = (f"{a.client_name} has {rep}, but organic traffic peaked at {peak['sessions']:,} sessions in {mlabel(peak['month'])} "
                 f"and has fallen to {cm['sessions']:,}, about {dpct}% off the peak. We crawled all {len(pages)} URLs on the site and "
                 f"pulled 90 days of Search Console and Analytics data. The audit below shows exactly where the traffic is leaking and "
                 f"what to fix first.")
    else:
        story = (f"{a.client_name} has {rep} and is gaining traction. We crawled all {len(pages)} URLs and pulled 90 days of Search "
                 f"Console and Analytics data. The audit below shows the highest-leverage technical and content fixes to accelerate it.")

    gscm = {r["month"]: r for r in load(P("gsc-monthly.json"), [])}
    months = sorted(set([r["month"] for r in org] + list(gscm.keys())))
    orgm = {r["month"]: r["sessions"] for r in org}
    cur = cm["sessions"] or org90//3 or 50; tgt = max(peak["sessions"], int(cur*3))
    chart = {"labels":[mlabel(m) for m in months], "organic":[orgm.get(m) for m in months],
             "clicks":[gscm.get(m,{}).get("clicks") for m in months], "impr":[gscm.get(m,{}).get("impressions") for m in months],
             "proj":{"labels":["Now","Month 3","Month 6","Month 9","Month 12"],
                     "current":[cur,round(cur*1.05),round(cur*1.1),round(cur*1.15),round(cur*1.2)],
                     "target":[cur,round(cur+(tgt-cur)*.25),round(cur+(tgt-cur)*.5),round(cur+(tgt-cur)*.78),tgt]}}

    ctx = dict(a=a, story=story, declined=declined, peak=peak, cm=cm, dpct=dpct,
               gclicks=gclicks, gimpr=gimpr, avg_pos=avg_pos, top_pages=top_pages, posdist=posdist,
               striking=striking, lowctr=lowctr, lf=lf, chart=chart, pathof=pathof,
               nC=nC, avg_wc=avg_wc, med_wc=med_wc, audit=audit, status3=status3,
               n200=n200, n3=n3, n4=n4, p404s=p404s, thin=thin, orphans=orphans, noindex=noindex,
               wc_buckets=wc_buckets, depth_buckets=depth_buckets, total_urls=len(pages), aa=aa)
    html = render(ctx)
    out = P("proposal.html")
    open(out,"w",encoding="utf-8").write(html)
    print(f"Saved: {out} ({len(html):,} bytes)")
    print(f"  {len(pages)} URLs crawled · {nC} content pages · audit checks: {len(audit)}")
    print(f"  404s {len(p404s)} · thin {len(thin)} · noindex {len(noindex)} · orphans {len(orphans)} · striking {len(striking)} · low-CTR {len(lowctr)}")


CSS = """
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:'Sora',system-ui,sans-serif;color:#14161c;background:#eceef2;line-height:1.55;font-size:13.5px}
.wrap{max-width:1000px;margin:0 auto;background:#fff;box-shadow:0 1px 40px rgba(10,14,26,.12)}
.hero{background:#0a0e1a;color:#fff;padding:60px 56px;border-left:10px solid var(--accent)}
.hero .agency{font-size:13px;letter-spacing:.3em;text-transform:uppercase;color:var(--accent);font-weight:700;margin-bottom:24px}
.hero h1{font-size:46px;font-weight:800;line-height:1.02;margin-bottom:10px;letter-spacing:-.5px}
.hero .sub{font-size:17px;color:#aeb4c2;font-weight:500}
.hero .meta{font-size:13px;color:#6f7892;margin-top:20px}
.sec{padding:38px 56px;border-bottom:1px solid #eef0f4}
.sechead{display:flex;align-items:baseline;gap:14px;margin-bottom:4px}
.secnum{font-size:13px;font-weight:800;color:var(--accent)}
.sec h2{font-size:13px;letter-spacing:.16em;text-transform:uppercase;color:#8a8f9c;font-weight:700}
.lead{font-size:23px;font-weight:800;letter-spacing:-.3px;margin:2px 0 16px;line-height:1.2}
.story{font-size:15.5px;color:#3a3a44;line-height:1.65;max-width:780px}
.kpis{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin-top:20px}
.kpi{background:#f7f8fb;border:1px solid #e8ebf1;border-radius:13px;padding:16px 18px;border-top:3px solid var(--accent)}
.kpi .v{font-size:31px;font-weight:800;color:#0a0e1a;line-height:1;letter-spacing:-1px}
.kpi .l{font-size:11px;font-weight:700;color:#5a5e6b;margin-top:9px;text-transform:uppercase;letter-spacing:.05em}
.kpi .s{font-size:11.5px;color:#9298a6;margin-top:3px}
table{width:100%;border-collapse:collapse;font-size:13px;margin-top:8px}
th{text-align:left;font-size:10.5px;letter-spacing:.07em;text-transform:uppercase;color:#9298a6;font-weight:700;padding:8px 11px;border-bottom:2px solid #eef0f4}
td{padding:9px 11px;border-bottom:1px solid #f3f4f7}
td.r,th.r{text-align:right;font-variant-numeric:tabular-nums}
tr:hover td{background:#fafbfc}
code{font-family:ui-monospace,Menlo,monospace;font-size:12px;color:#374151}
.chartbox{position:relative;height:300px;margin-top:12px}
.grid2{display:grid;grid-template-columns:1fr 1fr;gap:28px;margin-top:4px}
.pill{font-size:11px;font-weight:800;color:#fff;border-radius:999px;padding:3px 11px;white-space:nowrap}
.bars{margin-top:8px}
.bar{display:grid;grid-template-columns:120px 1fr 46px;align-items:center;gap:10px;margin:7px 0;font-size:12.5px}
.bar .track{height:18px;background:#f0f2f6;border-radius:5px;overflow:hidden}
.bar .fill{height:100%;background:var(--accent);border-radius:5px}
.bar .n{text-align:right;font-weight:700;font-variant-numeric:tabular-nums}
.statrow{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-top:6px}
.stat{background:#f7f8fb;border:1px solid #e8ebf1;border-radius:12px;padding:14px 16px;text-align:center}
.stat .sv{font-size:26px;font-weight:800;color:#0a0e1a}
.stat .sl{font-size:11px;color:#7c818d;margin-top:4px;text-transform:uppercase;letter-spacing:.04em;font-weight:700}
.heat{display:grid;grid-template-columns:repeat(7,1fr);gap:6px;width:330px}
.cell{aspect-ratio:1;border-radius:7px;display:flex;align-items:center;justify-content:center;font-size:13px;font-weight:800;color:#fff;text-shadow:0 1px 2px rgba(0,0,0,.25)}
.legend{display:flex;gap:14px;margin-top:12px;font-size:12px;color:#7c818d}
.legend span{display:inline-flex;align-items:center;gap:6px}.legend i{width:12px;height:12px;border-radius:3px}
.lf-wrap{display:grid;grid-template-columns:360px 1fr;gap:28px;align-items:start;margin-top:8px}
details.acc{border:1px solid #e8ebf1;border-radius:14px;margin-bottom:12px;overflow:hidden}
details.acc summary{list-style:none;cursor:pointer;padding:17px 22px;display:flex;align-items:center;gap:16px;background:#0a0e1a;color:#fff}
details.acc summary::-webkit-details-marker{display:none}
.acc .per{font-size:11px;font-weight:800;letter-spacing:.08em;text-transform:uppercase;color:var(--accent);min-width:150px}
.acc .ph{font-size:16px;font-weight:800;flex:1}.acc .chev{color:#7c84a0;transition:transform .2s}
details.acc[open] .chev{transform:rotate(90deg)}
.acc .body{padding:16px 22px 18px}.acc .body ul{margin-left:20px;font-size:13.5px;color:#3a3a44}.acc .body li{padding:3px 0}
.why{display:grid;grid-template-columns:repeat(2,1fr);gap:14px;margin-top:6px}
.wcard{border:1px solid #e8ebf1;border-radius:14px;padding:18px 20px;background:#fbfcfe}
.wcard .wn{font-size:13px;font-weight:800;color:var(--accent)}.wcard .wt{font-size:15px;font-weight:800;margin:5px 0}.wcard .wd{font-size:13px;color:#4a4b55}
.cta{background:#0a0e1a;color:#fff;padding:28px 56px;display:flex;align-items:center;justify-content:space-between;gap:20px}
.cta .ct{font-size:19px;font-weight:800}.cta .cs{font-size:13px;color:#aeb4c2;margin-top:4px}
.cta .go{background:var(--accent);color:#fff;font-weight:800;font-size:14px;padding:11px 22px;border-radius:999px}
.subh{font-size:13px;font-weight:800;color:#0a0e1a;margin:18px 0 4px}
"""

CHART_JS = """
window.addEventListener('load',function(){
 if(typeof Chart==='undefined')return;
 var D=window.PD.chart, A=getComputedStyle(document.documentElement).getPropertyValue('--accent').trim();
 var t=document.getElementById('trend');
 if(t)new Chart(t,{type:'line',data:{labels:D.labels,datasets:[
   {label:'Organic sessions (GA4)',data:D.organic,borderColor:A,backgroundColor:A+'22',yAxisID:'y',tension:.35,fill:true,spanGaps:true,borderWidth:2.5,pointRadius:2},
   {label:'Search clicks (GSC)',data:D.clicks,borderColor:'#16a34a',yAxisID:'y',tension:.35,spanGaps:true,borderWidth:2,pointRadius:0},
   {label:'Search impressions (GSC)',data:D.impr,borderColor:'#94a3b8',borderDash:[4,4],yAxisID:'y2',tension:.35,spanGaps:true,borderWidth:1.5,pointRadius:0}]},
   options:{responsive:true,maintainAspectRatio:false,interaction:{mode:'index',intersect:false},plugins:{legend:{position:'top',labels:{font:{size:11},usePointStyle:true,boxWidth:8}}},
     scales:{y:{position:'left',beginAtZero:true,title:{display:true,text:'Sessions / Clicks'}},y2:{position:'right',beginAtZero:true,grid:{drawOnChartArea:false},title:{display:true,text:'Impressions'}}}}});
 var pr=document.getElementById('proj');
 if(pr)new Chart(pr,{type:'line',data:{labels:D.proj.labels,datasets:[
   {label:'Current pace',data:D.proj.current,borderColor:'#94a3b8',borderDash:[6,5],tension:.35,borderWidth:2,pointRadius:0},
   {label:'With this plan',data:D.proj.target,borderColor:A,backgroundColor:A+'22',fill:true,tension:.35,borderWidth:2.5,pointRadius:3}]},
   options:{responsive:true,maintainAspectRatio:false,plugins:{legend:{position:'top',labels:{font:{size:11},usePointStyle:true,boxWidth:8}}},scales:{y:{beginAtZero:true,title:{display:true,text:'Organic sessions / mo'}}}}});
});
"""

def cellcolor(r):
    return "#b91c1c" if r==0 else "#16a34a" if r<=3 else "#84cc16" if r<=6 else "#eab308" if r<=10 else "#f97316" if r<=15 else "#ef4444"

def bars(items, accent="var(--accent)"):
    mx = max((v for _,v in items), default=1) or 1
    return '<div class="bars">'+"".join(
        f'<div class="bar"><div>{l}</div><div class="track"><div class="fill" style="width:{pct(v,mx)}%;background:{accent}"></div></div><div class="n">{v:,}</div></div>'
        for l,v in items)+'</div>'


def render(c):
    a=c["a"]; A=a.brand_color; po=c["pathof"]; n=[0]
    def head(label, lead):
        n[0]+=1; return f'<div class="sechead"><span class="secnum">{n[0]:02d}</span><h2>{label}</h2></div><div class="lead">{lead}</div>'
    H=[f"""<!DOCTYPE html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{a.client_name} — Local SEO Audit & Plan</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Sora:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>
<style>:root{{--accent:{A}}}{CSS}</style></head><body><div class="wrap">
<div class="hero"><div class="agency">22 Local Marketing</div><h1>{a.client_name}</h1>
<div class="sub">Local SEO Audit &amp; Growth Plan — {a.location}</div>
<div class="meta">Prepared {a.as_of} · {a.root_domain.replace('https://','')} · {c['total_urls']} URLs crawled</div></div>"""]

    # 1 snapshot
    kp = [("Organic sessions / mo", f"{c['cm']['sessions']:,}", "GA4, latest month"),
          ("Search clicks (90d)", f"{c['gclicks']:,}", "Search Console"),
          ("Search impressions (90d)", f"{c['gimpr']:,}", "Visibility in results"),
          ("Avg. position", f"{c['avg_pos']}", "Most pages on page 2"),
          ("Pages crawled", f"{c['total_urls']:,}", f"{c['nC']} content pages"),
          ("Avg. words / page", f"{c['avg_wc']:,}", f"median {c['med_wc']:,}")]
    if c["lf"].get("rating"): kp.append(("Google rating", f"{c['lf']['rating']}", f"{c['lf']['reviews']} reviews"))
    if c["lf"].get("grid_solv") is not None: kp.append(("Local Share of Voice", f"{c['lf']['grid_solv']:.0f}%", "Map grid coverage"))
    kph = "".join(f'<div class="kpi"><div class="v">{v}</div><div class="l">{l}</div><div class="s">{s}</div></div>' for l,v,s in kp)
    H.append(f'<div class="sec">{head("Where You Stand Today","A snapshot from your live data")}<div class="story">{c["story"]}</div><div class="kpis">{kph}</div></div>')

    # 2 trend
    H.append(f'<div class="sec">{head("Search Visibility Over Time","Organic sessions, clicks, and impressions")}<div class="chartbox"><canvas id="trend"></canvas></div></div>')

    # 3 search performance
    pd = c["posdist"]; mxp=max(v for _,v in pd) or 1
    posrow="".join(f'<div class="stat"><div class="sv">{v}</div><div class="sl">{l}</div></div>' for l,v in pd)
    strk="".join(f'<tr><td>{po(p["page"])}</td><td class="r">{p["position"]:.0f}</td><td class="r">{p["impressions"]:,}</td><td class="r">{p["clicks"]}</td></tr>' for p in c["striking"]) or '<tr><td colspan=4>None yet.</td></tr>'
    low="".join(f'<tr><td>{po(p["page"])}</td><td class="r">{p["impressions"]:,}</td><td class="r">{p["clicks"]}</td><td class="r">{p["clicks"]/p["impressions"]*100:.1f}%</td></tr>' for p in c["lowctr"]) or '<tr><td colspan=4>None.</td></tr>'
    H.append(f'''<div class="sec">{head("Search Performance","Where you rank and where the quick wins are")}
<div class="statrow">{posrow}</div>
<div class="subh">Striking distance — pages on page 2 that can reach page 1</div>
<table><tr><th>Page</th><th class="r">Pos</th><th class="r">Impr (90d)</th><th class="r">Clicks</th></tr>{strk}</table>
<div class="subh">High impressions, low clicks — title &amp; meta rewrites</div>
<table><tr><th>Page</th><th class="r">Impr</th><th class="r">Clicks</th><th class="r">CTR</th></tr>{low}</table></div>''')

    # 4 local
    if c["lf"].get("grid"):
        lf=c["lf"]; cells="".join(f'<div class="cell" style="background:{cellcolor(r)}">{r if r else "·"}</div>' for row in lf["grid"] for r in row)
        kr="".join(f'<tr><td>{k["keyword"]}</td><td class="r">{k["solv"]:.0f}%</td><td class="r">{k["arp"]:.1f}</td></tr>' for k in lf.get("keywords",[]))
        cr_="".join(f'<tr><td>{x["name"]}</td><td class="r">{x["avg_rank"]}</td><td class="r">{x.get("rating","")}</td></tr>' for x in lf.get("competitors",[]))
        H.append(f'''<div class="sec">{head("Local Map Visibility",f'"{lf.get("grid_keyword","")}" across the area · {lf.get("grid_solv",0):.0f}% Share of Local Voice')}
<div class="lf-wrap"><div><div class="heat">{cells}</div>
<div class="legend"><span><i style="background:#16a34a"></i>Top 3</span><span><i style="background:#eab308"></i>4-10</span><span><i style="background:#f97316"></i>11-20</span><span><i style="background:#b91c1c"></i>Not ranked</span></div></div>
<div><table><tr><th>Keyword</th><th class="r">SoLV</th><th class="r">Avg rank</th></tr>{kr}</table>
<table style="margin-top:14px"><tr><th>Top competitors in grid</th><th class="r">Avg rank</th><th class="r">Rating</th></tr>{cr_}</table></div></div></div>''')

    # 5 technical audit
    arows="".join(f'<tr><td>{nm}</td><td class="r">{cnt:,}</td><td class="r"><span class="pill" style="background:{c["status3"](cnt,fa)[0]}">{c["status3"](cnt,fa)[1]}</span></td></tr>' for nm,cnt,fa in c["audit"])
    H.append(f'''<div class="sec">{head("Technical SEO Audit",f'On-page health across {c["nC"]} content pages')}
<div class="statrow"><div class="stat"><div class="sv">{c["n200"]:,}</div><div class="sl">200 OK</div></div>
<div class="stat"><div class="sv">{c["n3"]:,}</div><div class="sl">Redirects</div></div>
<div class="stat"><div class="sv">{c["n4"]:,}</div><div class="sl">Errors (4xx)</div></div>
<div class="stat"><div class="sv">{len(c["noindex"]):,}</div><div class="sl">Non-indexable</div></div></div>
<table><tr><th>Check</th><th class="r">Pages</th><th class="r">Status</th></tr>{arows}</table></div>''')

    # 5b Ahrefs site audit
    if c["aa"].get("issues"):
        aa=c["aa"]; sc={"Error":"#ef4444","Warning":"#eab308","Notice":"#94a3b8"}
        ir="".join(f'<tr><td>{i["name"]}</td><td>{i["category"]}</td><td class="r">{i["crawled"]:,}</td><td class="r"><span class="pill" style="background:{sc.get(i["importance"],"#94a3b8")}">{i["importance"]}</span></td></tr>' for i in aa["issues"])
        H.append(f'''<div class="sec">{head("Ahrefs Site Audit",f'Independent crawl · health score {aa.get("health_score","")}/100 across {aa.get("crawled","")} URLs')}
<div class="statrow"><div class="stat"><div class="sv" style="color:var(--accent)">{aa.get("health_score","")}</div><div class="sl">Health score</div></div>
<div class="stat"><div class="sv">{aa.get("errors",0)}</div><div class="sl">Errors</div></div>
<div class="stat"><div class="sv">{aa.get("warnings",0)}</div><div class="sl">Warnings</div></div>
<div class="stat"><div class="sv">{aa.get("notices",0)}</div><div class="sl">Notices</div></div></div>
<div class="subh">Every issue found, by severity</div>
<table><tr><th>Issue</th><th>Category</th><th class="r">URLs</th><th class="r">Severity</th></tr>{ir}</table></div>''')

    # 6 content + crawl depth
    p404="".join(f'<tr><td>{po(u)}</td><td class="r">{imp:,}</td></tr>' for u,imp in c["p404s"][:8]) or '<tr><td colspan=2>None.</td></tr>'
    thinl="".join(f'<tr><td>{po(p.get("url",""))}</td><td class="r">{int(p["word_count"])}</td></tr>' for p in c["thin"][:8]) or '<tr><td colspan=2>None.</td></tr>'
    H.append(f'''<div class="sec">{head("Content &amp; Crawl Depth","How deep and how thorough the site is")}
<div class="grid2"><div><div class="subh">Word count distribution</div>{bars(c["wc_buckets"])}</div>
<div><div class="subh">Click depth from homepage</div>{bars(c["depth_buckets"], "#16a34a")}</div></div>
<div class="grid2" style="margin-top:18px"><div><div class="subh">Broken pages losing impressions</div>
<table><tr><th>404 URL</th><th class="r">Impr/mo lost</th></tr>{p404}</table></div>
<div><div class="subh">Thinnest content pages</div><table><tr><th>Page</th><th class="r">Words</th></tr>{thinl}</table></div></div></div>''')

    # 7 top pages
    tp="".join(f'<tr><td>{po(p["page"])}</td><td class="r">{p["clicks"]}</td><td class="r">{p["impressions"]:,}</td><td class="r">{p["position"]:.0f}</td></tr>' for p in c["top_pages"])
    H.append(f'<div class="sec">{head("Top Pages","What is driving search traffic now")}<table><tr><th>Page</th><th class="r">Clicks (90d)</th><th class="r">Impressions</th><th class="r">Avg pos</th></tr>{tp}</table></div>')

    # 8 plan accordion
    phases=[("Month 1 · Foundation","Diagnose and stabilize",
             ["Investigate the traffic drop and recover lost rankings" if c["declined"] else "Lock in analytics and conversion tracking",
              f"Fix the {len(c['p404s'])} broken pages and clear the redirect chains","Resolve missing titles, metas, and H1s flagged above","Set up clean conversion tracking and a baseline"]),
            ("Months 2-3 · Local + Content","Widen coverage and depth",
             ["Google Business Profile optimization and a steady review pace","Content for the map-grid gap areas",
              f"Expand the {len(c['thin'])} thin pages and rewrite low-CTR titles and metas","Strengthen internal links to the orphan pages"]),
            ("Months 4-6 · Authority + Growth","Build and compound",
             [f"Push the {len(c['striking'])} striking-distance pages into the top 5","Targeted link building across service and service-area pages","Monthly reporting tied to calls and leads"])]
    accs="".join(f'<details class="acc"{" open" if i==0 else ""}><summary><span class="per">{per}</span><span class="ph">{ph}</span><span class="chev">&#9656;</span></summary><div class="body"><ul>{"".join(f"<li>{x}</li>" for x in it)}</ul></div></details>' for i,(per,ph,it) in enumerate(phases))
    H.append(f'<div class="sec">{head("The Plan","A focused 6-month build, tied to the findings above")}{accs}</div>')

    # 9 projection
    H.append(f'<div class="sec">{head("12-Month Projection","Where this plan can take organic traffic")}<div class="chartbox"><canvas id="proj"></canvas></div><div class="s" style="font-size:12px;color:#9298a6;margin-top:10px">Directional estimate based on your current trend and planned work, not a guarantee.</div></div>')

    # 10 why us
    why=[("Contractor specialists","We work only with contractors and home-service businesses, so the playbook is tuned to how local buyers search and hire."),
         ("Omnipresence, not just rankings","Maps, organic, Local Services Ads, and paid working together so you show up wherever the customer looks."),
         ("Honest, measurable reporting","Clear monthly reporting tied to calls and leads, not vanity metrics."),
         ("Built on real data","Every recommendation here came from a full crawl plus your Search Console, Analytics, and map-grid data. No guesswork.")]
    wh="".join(f'<div class="wcard"><div class="wn">{i+1:02d}</div><div class="wt">{t}</div><div class="wd">{d}</div></div>' for i,(t,d) in enumerate(why))
    H.append(f'<div class="sec">{head("Why 22 Local Marketing","How we work and what makes us different")}<div class="why">{wh}</div></div>')

    H.append(f'<div class="cta"><div><div class="ct">Ready to get found across {a.location.split(",")[0]}?</div><div class="cs">22 Local Marketing · The dominant local presence for contractors</div></div><div class="go">Let\'s talk</div></div>')
    H.append(f'</div><script>window.PD={{"chart":{json.dumps(c["chart"])}}};</script><script>{CHART_JS}</script></body></html>')
    return "".join(H)


if __name__ == "__main__":
    main()
