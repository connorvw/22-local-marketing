#!/usr/bin/env python3
# One-pass fill of the Vivid Tree Service proposal from real audit data.
# Honest narrative: owns the Logansport map, but no website/organic, toxic links, expansion open.
import sys, io
P = "site/vivid-tree-service-9k4m/index.html"
s = open(P, encoding="utf-8").read()
R = []  # (old, new)

# ---------- global tokens ----------
R += [
 ("{{CLIENT_NAME}}", "Vivid Tree Service"),
 ("{{CITY}}", "Logansport"),
 ("{{STATE}}", "Indiana"),
 ("{{CLIENT_LOGO}}", "Vivid Tree Service"),
]

# ---------- remove Loom band (Connor: leave blank) ----------
R.append(('''
  <!-- LOOM PERSONAL WALKTHROUGH (reusable across prospects) -->
  <section style="border-top:0;padding-top:0">
    <div class="container">
      <div class="loom-band">
        <div class="lt">
          <div class="eyebrow"><span class="eb-dash"></span>A quick walkthrough</div>
          <h2>Let me walk you through <span class="accent">this.</span></h2>
          <p>Two minutes from me on what we found, why it matters, and exactly how we'd fix it. Watch this first.</p>
        </div>
        <!-- Replace data-loom with your reusable Loom share ID. Same video for every prospect. -->
        <div class="loom-frame" data-loom="{{LOOM_ID}}">
          <span class="badge-loom">▶ Watch · 2 min</span>
          <div class="play"></div>
        </div>
      </div>
    </div>
  </section>
''', '\n'))

# ---------- HERO ----------
R.append(('''<h1>Summit Tree &amp; Land is invisible on the<br>map. <span class="accent">Let's fix that.</span></h1>''',
          '''<h1>You own the Logansport map. Online, you're <span class="accent">invisible.</span></h1>'''))
R.append(('''<p class="lead">You rank outside the top 3 on most of Raleigh. Here's exactly where you're losing jobs, who's taking them, and the system we'll run to put you on top.</p>''',
          '''<p class="lead">You rank #1 across all of Logansport, that's rare. But your website has almost no presence beyond the map pack, plus a link problem dragging it down, and that's exactly what we'd fix.</p>'''))

# ---------- EXEC SUMMARY ----------
R.append(("Tree removal, trimming, stump grinding, and land clearing across the Raleigh metro.",
          "Tree removal, trimming, pruning, stump grinding, land clearing, and timber milling across Northern Indiana."))
R.append(('''<div class="snap-row"><span class="k">Markets</span><span class="v">Raleigh + 2 nearby</span></div>
          <div class="snap-row"><span class="k">Avg map rank</span><span class="v">8.4</span></div>
          <div class="snap-row"><span class="k">Domain authority</span><span class="v">6 / 100</span></div>
          <div class="snap-row"><span class="k">Monthly traffic</span><span class="v">~90 visits</span></div>
          <div class="snap-row"><span class="k">Google reviews</span><span class="v">37 · 4.6★</span></div>''',
          '''<div class="snap-row"><span class="k">Markets</span><span class="v">Logansport + N. Indiana</span></div>
          <div class="snap-row"><span class="k">Avg map rank</span><span class="v">1.0 · #1 of 49</span></div>
          <div class="snap-row"><span class="k">Domain authority</span><span class="v">0.1 / 100</span></div>
          <div class="snap-row"><span class="k">Organic traffic</span><span class="v">~0 / mo</span></div>
          <div class="snap-row"><span class="k">Google reviews</span><span class="v">55 · 5.0★</span></div>'''))
R.append(('''<span class="t">Tree Removal</span><span class="t">Trimming</span><span class="t">Stump Grinding</span><span class="t">Land Clearing</span><span class="t">Emergency</span>''',
          '''<span class="t">Tree Removal</span><span class="t">Trimming</span><span class="t">Pruning</span><span class="t">Stump Grinding</span><span class="t">Land Clearing</span><span class="t">Timber Milling</span>'''))
# challenges
R.append(('''<div class="chal"><span class="cdot"></span><span>Ranking <b>outside the top 3</b> in 71% of your service area, where the call volume lives.</span></div>
          <div class="chal"><span class="cdot"></span><span><b>No pages</b> target stump grinding, emergency, or land clearing, demand you're handing to rivals.</span></div>
          <div class="chal"><span class="cdot"></span><span><b>37 reviews vs. 168</b> for the local leader, a pure review-velocity gap.</span></div>
          <div class="chal"><span class="cdot"></span><span>Domain authority of <b>6 vs. 17</b>, with thin content on every key page.</span></div>
          <div class="chal"><span class="cdot"></span><span>Slow mobile load and <b>missing local schema</b>, both rankings drags.</span></div>''',
          '''<div class="chal"><span class="cdot" style="background:var(--success)"></span><span><b>#1 across all of Logansport</b> with a 5.0 from 55 reviews. Few crews own their map like you do.</span></div>
          <div class="chal"><span class="cdot"></span><span>Your website is invisible: <b>domain authority 0.1</b>, ~0 organic traffic, just 2 ranking keywords.</span></div>
          <div class="chal"><span class="cdot"></span><span>A <b>5-page site</b> with no service or location pages, nothing for Google or AI to rank.</span></div>
          <div class="chal"><span class="cdot"></span><span>A <b>toxic-link spike</b> (34 → 176 referring domains while authority fell) that risks a penalty.</span></div>
          <div class="chal"><span class="cdot"></span><span>Bigger markets are open: <b>Kokomo, Peru, Rochester</b>, where Heartland (233 reviews) already leads.</span></div>'''))
# strategy
R.append(('''<div class="strat"><span class="n">1</span><span><b>Fix the foundation</b>, Google Business Profile, tracking, and site health in week one.</span></div>
          <div class="strat"><span class="n">2</span><span><b>Build the missing pages</b>, a real page for every service and location.</span></div>
          <div class="strat"><span class="n">3</span><span><b>Run a review engine</b> to close the 37→168 gap over the next two quarters.</span></div>
          <div class="strat"><span class="n">4</span><span><b>Earn authority</b> with content and links that move domain rating.</span></div>
          <div class="strat"><span class="n">5</span><span><b>Turn on ads</b> the day the site ships, so leads start while SEO compounds.</span></div>''',
          '''<div class="strat"><span class="n">1</span><span><b>Clean up the link profile</b>, disavow the toxic spike before it costs you rankings.</span></div>
          <div class="strat"><span class="n">2</span><span><b>Build a real website</b>, a page for every service and every nearby city.</span></div>
          <div class="strat"><span class="n">3</span><span><b>Rank organically and in AI</b>, capture the searches your map pin can't reach.</span></div>
          <div class="strat"><span class="n">4</span><span><b>Expand the map</b> into Kokomo, Peru, and Rochester, one proven city at a time.</span></div>
          <div class="strat"><span class="n">5</span><span><b>Keep your edge</b>, protect the 5.0 reviews and map dominance that already win.</span></div>'''))

# ---------- GEO-GRID ----------
R.append(("<h2>Where you actually rank.</h2>", "<h2>You own your map.</h2>"))
R.append(('''<span class="desc">We scanned a grid across your service area for "tree removal raleigh." Green is top 3. Red is page two or worse.</span>''',
          '''<span class="desc">We scanned a grid across Logansport for "tree service logansport." Every point is green, you're #1 everywhere. That's the part that's working.</span>'''))
R.append(('''<!-- Drop the actual scan export here: <img src="geogrid-scan.png" alt="Geo-grid rank scan"> -->
        <div class="lf-shot">
          <div class="ph">Geo-grid scan screenshot<br><span style="font-size:12px">{{GEOGRID_SCREENSHOT}}</span></div>
        </div>''',
          '''<div class="lf-shot"><img src="geogrid.png" alt="Geo-grid scan, ranked #1 at every point"></div>'''))
R.append(('''<div class="lf-kw">Keyword: <b>tree removal raleigh nc</b> · scanned April 2026</div>''',
          '''<div class="lf-kw">Keyword: <b>tree service logansport</b> · scanned June 2026</div>'''))
R.append(('''<div class="lf-metric"><span class="m-lab">Average map rank</span><span class="m-val">8.4</span></div>
            <div class="lf-metric"><span class="m-lab">Share of local voice</span><span class="m-val">11%</span></div>
            <div class="lf-metric"><span class="m-lab">Top-3 visibility</span><span class="m-val">29%</span></div>''',
          '''<div class="lf-metric"><span class="m-lab">Average map rank</span><span class="m-val">1.0</span></div>
            <div class="lf-metric"><span class="m-lab">Share of local voice</span><span class="m-val">100%</span></div>
            <div class="lf-metric"><span class="m-lab">Top-3 visibility</span><span class="m-val">100%</span></div>'''))
R.append(("You're strong right next to your address and disappear two miles out. That's where the volume is, and where we go to work first.",
          "This is rare, and it's your foundation. The catch: it stops at the edge of town, and it's all you have. In organic search, in AI answers, and in the next town over, you don't exist yet."))

# ---------- VISIBILITY GAPS ----------
R.append(("<h2>Where you're losing visibility.</h2>", "<h2>Where your website goes missing.</h2>"))
R.append(('''<span class="desc">The money keywords, where you rank today, and the exact problem holding each one back.</span>''',
          '''<span class="desc">The searches that book jobs, whether your website ranks, and why a map pin alone can't catch them.</span>'''))
R.append(('''<tr><td>tree removal raleigh</td><td class="num">1,300</td><td class="pos-cell" style="color:var(--danger)">#12</td><td><span class="tag b-danger"><span class="bd"></span>Stuck on page 2, effectively invisible</span></td></tr>
            <tr><td>emergency tree service raleigh</td><td class="num">880</td><td class="pos-cell" style="color:var(--danger)">#19</td><td><span class="tag b-danger"><span class="bd"></span>Losing every emergency call to rivals</span></td></tr>
            <tr><td>land clearing raleigh nc</td><td class="num">410</td><td class="pos-cell" style="color:var(--danger)">—</td><td><span class="tag b-danger"><span class="bd"></span>No page on your site targets this</span></td></tr>
            <tr><td>stump grinding raleigh</td><td class="num">590</td><td class="pos-cell" style="color:var(--warning)">#8</td><td><span class="tag b-warn"><span class="bd"></span>Just below the map pack cutoff</span></td></tr>
            <tr><td>tree trimming near me</td><td class="num">720</td><td class="pos-cell" style="color:var(--warning)">#5</td><td><span class="tag b-warn"><span class="bd"></span>Striking distance, one push from top 3</span></td></tr>''',
          '''<tr><td>tree service logansport</td><td class="num">10</td><td class="pos-cell" style="color:var(--warning)">Map pin</td><td><span class="tag b-warn"><span class="bd"></span>Your GBP ranks; your website doesn't</span></td></tr>
            <tr><td>emergency tree service logansport</td><td class="num">~10</td><td class="pos-cell" style="color:var(--danger)">—</td><td><span class="tag b-danger"><span class="bd"></span>An AI Overview answers it, you're not cited</span></td></tr>
            <tr><td>stump grinding logansport</td><td class="num">low</td><td class="pos-cell" style="color:var(--danger)">—</td><td><span class="tag b-danger"><span class="bd"></span>No page on your site targets this service</span></td></tr>
            <tr><td>tree removal cost</td><td class="num">12,100</td><td class="pos-cell" style="color:var(--danger)">—</td><td><span class="tag b-danger"><span class="bd"></span>Big research demand, no content to capture it</span></td></tr>
            <tr><td>tree removal near me</td><td class="num">60,500</td><td class="pos-cell" style="color:var(--danger)">—</td><td><span class="tag b-danger"><span class="bd"></span>Where the volume is, a map pin can't reach it</span></td></tr>'''))
# authority gauges
R.append(('''<div class="gauge" style="--val:6;--gc:var(--danger);margin:0 auto 14px"><div class="inner"><div><div class="g-val">6</div><div class="g-lab">Domain authority</div></div></div></div>
          <div style="font-size:13px;color:var(--slate)">Out of 100. Top rival sits at 19.</div>''',
          '''<div class="gauge" style="--val:1;--gc:var(--danger);margin:0 auto 14px"><div class="inner"><div><div class="g-val">0.1</div><div class="g-lab">Domain authority</div></div></div></div>
          <div style="font-size:13px;color:var(--slate)">Out of 100. Effectively zero.</div>'''))
R.append(('''<div class="gauge" style="--val:31;--gc:var(--blaze);margin:0 auto 14px"><div class="inner"><div><div class="g-val">42</div><div class="g-lab">Linking sites</div></div></div></div>
          <div style="font-size:13px;color:var(--slate)">Other sites linking to yours.</div>''',
          '''<div class="gauge" style="--val:70;--gc:var(--danger);margin:0 auto 14px"><div class="inner"><div><div class="g-val">176</div><div class="g-lab">Linking sites</div></div></div></div>
          <div style="font-size:13px;color:var(--slate)">Mostly low-quality. A cleanup target.</div>'''))

# ---------- COMPETITORS ----------
R.append(("<h2>Who's eating your lunch.</h2>", "<h2>Who you're up against as you grow.</h2>"))
R.append(('''<span class="desc">The four crews beating you in the map pack, side by side.</span>''',
          '''<span class="desc">The local independents you'll face the moment you expand beyond Logansport.</span>'''))
R.append(('''<tr><td class="you">Summit Tree &amp; Land (you)</td><td class="you num">6</td><td class="you num">37</td><td class="you num">4.6</td><td class="you num">88</td></tr>
            <tr><td>Oak City Tree Service</td><td class="num">17</td><td class="num">168</td><td class="num">4.9</td><td class="num">312</td></tr>
            <tr><td>Triangle Tree Service</td><td class="num">14</td><td class="num">156</td><td class="num">4.8</td><td class="num">290</td></tr>
            <tr><td>Carolina Tree Care</td><td class="num">11</td><td class="num">98</td><td class="num">4.7</td><td class="num">177</td></tr>
            <tr><td>Raleigh Tree Pros</td><td class="num">9</td><td class="num">76</td><td class="num">4.7</td><td class="num">142</td></tr>''',
          '''<tr><td class="you">Vivid Tree Service (you)</td><td class="you num">0.1</td><td class="you num">55</td><td class="you num">5.0</td><td class="you num">2</td></tr>
            <tr><td>Heartland Tree Service</td><td class="num">1.6</td><td class="num">233</td><td class="num">5.0</td><td class="num">8</td></tr>
            <tr><td>Straight Cut Tree Service</td><td class="num">0.0</td><td class="num">120</td><td class="num">5.0</td><td class="num">4</td></tr>
            <tr><td>Beachy Tree Service</td><td class="num">0.0</td><td class="num">73</td><td class="num">5.0</td><td class="num">7</td></tr>
            <tr><td>HillTop Tree Service</td><td class="num">0.7</td><td class="num">41</td><td class="num">4.7</td><td class="num">0</td></tr>'''))

# ---------- ARCHITECTURE DIAGRAM ----------
R.append(('<button class="node" data-pop="service"><span class="dotp"></span>Lot Clearing</button>',
          '<button class="node" data-pop="service"><span class="dotp"></span>Land Clearing</button>'))
R.append(('''<button class="node" data-pop="areahub"><span class="dotp"></span>Raleigh <span class="more">primary</span></button>
              <button class="node" data-pop="areahub"><span class="dotp"></span>Cary</button>
              <button class="node" data-pop="areahub"><span class="dotp"></span>Durham</button>
              <button class="node" data-pop="areahub"><span class="dotp"></span>Apex</button>
              <button class="node" data-pop="areahub"><span class="dotp"></span>Wake Forest</button>
              <button class="node" data-pop="areahub"><span class="dotp"></span>Garner</button>''',
          '''<button class="node" data-pop="areahub"><span class="dotp"></span>Logansport <span class="more">primary</span></button>
              <button class="node" data-pop="areahub"><span class="dotp"></span>Peru</button>
              <button class="node" data-pop="areahub"><span class="dotp"></span>Kokomo</button>
              <button class="node" data-pop="areahub"><span class="dotp"></span>Rochester</button>
              <button class="node" data-pop="areahub"><span class="dotp"></span>Wabash</button>
              <button class="node" data-pop="areahub"><span class="dotp"></span>Royal Center</button>'''))
R.append(('''City-service spokes from <span style="color:var(--blaze)">Raleigh</span> · /areas/raleigh/&hellip;''',
          '''City-service spokes from <span style="color:var(--blaze)">Logansport</span> · /areas/logansport/&hellip;'''))
R.append(('''<button class="node" data-pop="spoke"><span class="dotp"></span>Tree Removal in Raleigh</button>
                <button class="node" data-pop="spoke"><span class="dotp"></span>Stump Grinding in Raleigh</button>
                <button class="node" data-pop="spoke"><span class="dotp"></span>Tree Trimming in Raleigh</button>''',
          '''<button class="node" data-pop="spoke"><span class="dotp"></span>Tree Removal in Logansport</button>
                <button class="node" data-pop="spoke"><span class="dotp"></span>Stump Grinding in Logansport</button>
                <button class="node" data-pop="spoke"><span class="dotp"></span>Tree Trimming in Logansport</button>'''))

# ---------- GAME PLAN phase 1 ----------
R.append(('''<li>Google Business Profile audit, verification, and categories</li><li>Call tracking and analytics live</li><li>Site health fixes: broken links, local schema, crawl errors</li>''',
          '''<li>Disavow the toxic backlink spike before it costs rankings</li><li>Call tracking and analytics live</li><li>Lock in the Google Business Profile that's already winning</li>'''))

# ---------- PRICING form + CTA ----------
R.append(('placeholder="Summit Tree &amp; Land Co. LLC"', 'placeholder="Vivid Tree Service LLC"'))
R.append(('''<h2>Ready to own <span class="accent">Raleigh?</span></h2>
        <p>The crews above aren't slowing down. Every month you wait is jobs going to them.</p>''',
          '''<h2>Ready to grow beyond <span class="accent">Logansport?</span></h2>
        <p>You already own your town. Let's turn that into a website and a market that grow with you.</p>'''))

# ================= ANALYSIS TAB =================
# scorecards
R.append(('''<div class="scard"><div class="sl">Domain authority</div><div class="sv">6</div><div class="sd up">▲ 1 <span class="agone">vs 6 mo ago</span></div></div>
        <div class="scard"><div class="sl">Organic keywords</div><div class="sv">88</div><div class="sd down">▼ 32 <span class="agone">vs 6 mo ago</span></div></div>
        <div class="scard"><div class="sl">Organic traffic</div><div class="sv">~90</div><div class="sd down">▼ 41% <span class="agone">vs 6 mo ago</span></div></div>
        <div class="scard hl"><div class="sl">Traffic value</div><div class="sv">$310</div><div class="sd down">▼ 38% <span class="agone">/mo est.</span></div></div>
        <div class="scard"><div class="sl">Referring domains</div><div class="sv">42</div><div class="sd down">▼ 3 <span class="agone">vs 6 mo ago</span></div></div>''',
          '''<div class="scard"><div class="sl">Domain authority</div><div class="sv">0.1</div><div class="sd down">▼ 1.6 <span class="agone">vs 6 mo ago</span></div></div>
        <div class="scard"><div class="sl">Organic keywords</div><div class="sv">2</div><div class="sd down">▼ 1 <span class="agone">vs 6 mo ago</span></div></div>
        <div class="scard"><div class="sl">Organic traffic</div><div class="sv">~0</div><div class="sd neutral">— none in 24 mo</div></div>
        <div class="scard hl"><div class="sl">Traffic value</div><div class="sv">$0</div><div class="sd neutral"><span class="agone">/mo est.</span></div></div>
        <div class="scard"><div class="sl">Referring domains</div><div class="sv">176</div><div class="sd down">▲ 119 <span class="agone">likely spam</span></div></div>'''))
R.append(('''<div class="callout"><div><div class="cl-t">Traffic decline from peak</div><div class="cl-s">Peak ~150/mo → ~90/mo today</div></div><div class="cl-v">−41%</div></div>
        <div class="callout"><div><div class="cl-t">Value decline from peak</div><div class="cl-s">Estimated monthly traffic value</div></div><div class="cl-v">−38%</div></div>''',
          '''<div class="callout"><div><div class="cl-t">Organic traffic, 24 months</div><div class="cl-s">Effectively zero the entire time</div></div><div class="cl-v">~0</div></div>
        <div class="callout"><div><div class="cl-t">Ranking keywords</div><div class="cl-s">Both zero-volume; your GBP does the work</div></div><div class="cl-v">2</div></div>'''))

# what's driving it
R.append(("<h2>So why is it falling?</h2>", "<h2>So why is your website invisible?</h2>"))
R.append(('''<span class="desc">Two forces are compounding: algorithm shifts and AI answers eating your clicks.</span>''',
          '''<span class="desc">Two reasons: there's almost nothing on the site to rank, and the links you do have are hurting you.</span>'''))
R.append(('''<div style="font-size:12px;font-weight:600;letter-spacing:.06em;text-transform:uppercase;color:var(--slate);margin-bottom:14px">Google algorithm updates over the window</div>
          <div class="checklist">
            <div class="ci"><div><div class="ct">Aug 2024 core update</div><div class="cd">First leg down in rankings</div></div><span class="st badge b-warn"><span class="bd"></span>Impact</span></div>
            <div class="ci"><div><div class="ct">Nov 2024 core update</div><div class="cd">Further erosion on service terms</div></div><span class="st badge b-warn"><span class="bd"></span>Impact</span></div>
            <div class="ci"><div><div class="ct">Mar 2025 core update</div><div class="cd">Thin pages lost ground</div></div><span class="st badge b-danger"><span class="bd"></span>High</span></div>
            <div class="ci"><div><div class="ct">AI Overviews expansion</div><div class="cd">Answers shown above your listings</div></div><span class="st badge b-danger"><span class="bd"></span>High</span></div>
          </div>''',
          '''<div style="font-size:12px;font-weight:600;letter-spacing:.06em;text-transform:uppercase;color:var(--slate);margin-bottom:14px">Why there's nothing to rank</div>
          <div class="checklist">
            <div class="ci"><div><div class="ct">5 pages total</div><div class="cd">home, services, about, contact, estimate</div></div><span class="st badge b-danger"><span class="bd"></span>Thin</span></div>
            <div class="ci"><div><div class="ct">No service pages</div><div class="cd">8 services live on one shared page</div></div><span class="st badge b-danger"><span class="bd"></span>Missing</span></div>
            <div class="ci"><div><div class="ct">No location pages</div><div class="cd">nothing for nearby towns</div></div><span class="st badge b-danger"><span class="bd"></span>Missing</span></div>
            <div class="ci"><div><div class="ct">No blog or content</div><div class="cd">no topical authority being built</div></div><span class="st badge b-warn"><span class="bd"></span>Gap</span></div>
          </div>'''))
R.append(('''<div style="font-size:12px;font-weight:600;letter-spacing:.06em;text-transform:uppercase;color:var(--slate);margin-bottom:14px">AI Overview exposure on your core keywords</div>
          <div class="gauge" style="--val:60;--gc:var(--danger);margin:6px auto 16px"><div class="inner"><div><div class="g-val">3/5</div><div class="g-lab">show AI Overview</div></div></div></div>
          <p style="font-size:13px;color:var(--slate)">An AI answer now sits above the organic results on most of your money keywords. Even when you rank, the click is intercepted by the AI box before it reaches your listing.</p>''',
          '''<div style="font-size:12px;font-weight:600;letter-spacing:.06em;text-transform:uppercase;color:var(--slate);margin-bottom:14px">A toxic backlink spike</div>
          <div class="gauge" style="--val:80;--gc:var(--danger);margin:6px auto 16px"><div class="inner"><div><div class="g-val">176</div><div class="g-lab">ref domains</div></div></div></div>
          <p style="font-size:13px;color:var(--slate)">Your referring domains jumped from 34 to 176 in two months while your authority fell. That's the signature of a spam/PBN link blast, and it risks a Google penalty. Cleanup is step one.</p>'''))
# cannibalization table -> AI overview opportunity
R.append(('''<div style="font-size:13px;font-weight:700;letter-spacing:.04em;text-transform:uppercase;color:var(--onyx);margin-bottom:4px">The fingerprint: rankings held, traffic still fell</div>
        <div style="font-size:14px;color:var(--slate);margin-bottom:14px">When position is flat or up but estimated traffic drops, an AI Overview is taking the click.</div>
        <div class="tbl-wrap">
          <table>
            <thead><tr><th>Keyword</th><th>Rank: 12 mo ago → now</th><th>AI Overview</th><th>Est. traffic</th></tr></thead>
            <tbody>
              <tr><td>oak tree disease (blog)</td><td class="num">#6 → #5</td><td><span class="tag b-danger"><span class="bd"></span>Yes</span></td><td><span class="tag b-danger"><span class="bd"></span>▼ 60%</span></td></tr>
              <tr><td>tree removal cost</td><td class="num">#8 → #7</td><td><span class="tag b-danger"><span class="bd"></span>Yes</span></td><td><span class="tag b-danger"><span class="bd"></span>▼ 44%</span></td></tr>
              <tr><td>stump grinding raleigh</td><td class="num">#9 → #8</td><td><span class="tag b-danger"><span class="bd"></span>Yes</span></td><td><span class="tag b-warn"><span class="bd"></span>▼ 22%</span></td></tr>
              <tr><td>tree trimming near me</td><td class="num">#7 → #5</td><td><span class="tag b-success"><span class="bd"></span>No</span></td><td><span class="tag b-success"><span class="bd"></span>▲ 12%</span></td></tr>
            </tbody>
          </table>
        </div>''',
          '''<div style="font-size:13px;font-weight:700;letter-spacing:.04em;text-transform:uppercase;color:var(--onyx);margin-bottom:4px">AI Overviews answering for you</div>
        <div style="font-size:14px;color:var(--slate);margin-bottom:14px">Google now shows an AI answer on these searches. You're not cited in any of them, your competitors are.</div>
        <div class="tbl-wrap">
          <table>
            <thead><tr><th>Search</th><th>AI Overview</th><th>You cited?</th><th>Who shows instead</th></tr></thead>
            <tbody>
              <tr><td>emergency tree service logansport</td><td><span class="tag b-danger"><span class="bd"></span>Yes</span></td><td><span class="tag b-danger"><span class="bd"></span>No</span></td><td>Heartland, Straight Cut</td></tr>
              <tr><td>tree removal cost</td><td><span class="tag b-danger"><span class="bd"></span>Yes</span></td><td><span class="tag b-danger"><span class="bd"></span>No</span></td><td>National sites</td></tr>
              <tr><td>tree removal near me</td><td><span class="tag b-warn"><span class="bd"></span>Map pack</span></td><td><span class="tag b-warn"><span class="bd"></span>Pin only</span></td><td>You, plus local rivals</td></tr>
            </tbody>
          </table>
        </div>'''))

# keyword funnel
R.append(('''<span class="desc">Most of your visibility is informational. The keywords that book jobs are where you're thinnest.</span>''',
          '''<span class="desc">You rank for almost nothing. Two keywords total, both zero-volume. There's no funnel yet, we build it.</span>'''))
R.append(('''<div class="frow"><div class="fl">Awareness <small>"types of tree disease"</small></div><div class="fbar"><i style="width:78%"></i></div><div class="fv">61 kw<small>info intent</small></div></div>
        <div class="frow"><div class="fl">Consideration <small>"tree removal cost"</small></div><div class="fbar"><i style="width:34%"></i></div><div class="fv">19 kw<small>research</small></div></div>
        <div class="frow"><div class="fl">Decision <small>"tree removal raleigh"</small></div><div class="fbar"><i style="width:12%"></i></div><div class="fv">8 kw<small>ready to hire</small></div></div>''',
          '''<div class="frow"><div class="fl">Awareness <small>"how to save a tree"</small></div><div class="fbar"><i style="width:3%"></i></div><div class="fv">0 kw<small>info intent</small></div></div>
        <div class="frow"><div class="fl">Consideration <small>"tree removal cost"</small></div><div class="fbar"><i style="width:3%"></i></div><div class="fv">0 kw<small>research</small></div></div>
        <div class="frow"><div class="fl">Decision <small>"tree service logansport"</small></div><div class="fbar"><i style="width:14%"></i></div><div class="fv">2 kw<small>both zero-volume</small></div></div>'''))
R.append(('''<p style="font-size:13px;color:var(--slate);margin-top:14px">Only <strong>8 of 88 keywords</strong> are bottom-of-funnel, the ones tied to revenue. That's the gap we close first.</p>''',
          '''<p style="font-size:13px;color:var(--slate);margin-top:14px">You rank for just <strong>2 keywords</strong> total, both zero-volume local terms your GBP already covers. There's no organic funnel yet. That's what we build.</p>'''))

# keyword detail
R.append(('''<span class="desc">Volume, difficulty, your position, and what's on the results page for each.</span>''',
          '''<span class="desc">Volume, difficulty, whether your website ranks, and what's on the results page.</span>'''))
R.append(('''<tr><td>tree removal raleigh</td><td>1,300</td><td>28</td><td>12</td><td>Map pack, AI Overview</td></tr>
            <tr><td>emergency tree service raleigh</td><td>880</td><td>22</td><td>19</td><td>Map pack</td></tr>
            <tr><td>stump grinding raleigh</td><td>590</td><td>18</td><td>8</td><td>Map pack, PAA</td></tr>
            <tr><td>land clearing raleigh nc</td><td>410</td><td>31</td><td>24</td><td>AI Overview</td></tr>
            <tr><td>tree trimming near me</td><td>720</td><td>25</td><td>5</td><td>Map pack</td></tr>''',
          '''<tr><td>tree service logansport</td><td>10</td><td>n/a</td><td>Map pin</td><td>Map pack</td></tr>
            <tr><td>emergency tree service logansport</td><td>~10</td><td>n/a</td><td>—</td><td>AI Overview, Map pack</td></tr>
            <tr><td>stump grinding logansport</td><td>low</td><td>n/a</td><td>—</td><td>Map pack, PAA</td></tr>
            <tr><td>tree removal cost</td><td>12,100</td><td>10</td><td>—</td><td>AI Overview, PAA</td></tr>
            <tr><td>tree removal near me</td><td>60,500</td><td>30</td><td>—</td><td>Map pack</td></tr>'''))

# generative / AI presence
R.append(('''<span class="desc">When someone asks an AI assistant for a tree service in Raleigh, you don't come up.</span>''',
          '''<span class="desc">Ask an AI assistant for a tree service near Logansport and you don't come up. The local leaders do.</span>'''))
R.append(('''<tr><td>Google AI Overview</td><td>"tree removal raleigh"</td><td><span class="tag b-danger"><span class="bd"></span>No</span></td><td>Oak City, Triangle</td></tr>
            <tr><td>ChatGPT</td><td>"best tree service in raleigh"</td><td><span class="tag b-danger"><span class="bd"></span>No</span></td><td>Oak City, Carolina</td></tr>
            <tr><td>Perplexity</td><td>"emergency tree service raleigh"</td><td><span class="tag b-danger"><span class="bd"></span>No</span></td><td>Triangle, Oak City</td></tr>''',
          '''<tr><td>Google AI Overview</td><td>"emergency tree service logansport"</td><td><span class="tag b-danger"><span class="bd"></span>No</span></td><td>Heartland, Straight Cut</td></tr>
            <tr><td>ChatGPT</td><td>"best tree service near logansport"</td><td><span class="tag b-danger"><span class="bd"></span>No</span></td><td>Heartland, Beachy</td></tr>
            <tr><td>Perplexity</td><td>"tree removal logansport in"</td><td><span class="tag b-danger"><span class="bd"></span>No</span></td><td>Straight Cut, Heartland</td></tr>'''))

# top pages
R.append(('''<span class="desc">A handful of pages carry the site, and almost none of them target a service that pays.</span>''',
          '''<span class="desc">Your whole site is 5 pages, and none of them pull measurable organic traffic.</span>'''))
R.append(('''<tr><td>/blog/when-to-remove-a-tree</td><td class="num">38</td><td>when to remove a tree</td><td><span class="tag b-warn"><span class="bd"></span>Informational</span></td></tr>
            <tr><td>/ (home)</td><td class="num">22</td><td>summit tree raleigh</td><td><span class="tag b-success"><span class="bd"></span>Branded</span></td></tr>
            <tr><td>/tree-removal</td><td class="num">14</td><td>tree removal raleigh</td><td><span class="tag b-success"><span class="bd"></span>Service</span></td></tr>
            <tr><td>/blog/tree-disease-guide</td><td class="num">11</td><td>oak tree disease</td><td><span class="tag b-warn"><span class="bd"></span>Informational</span></td></tr>
            <tr><td>/about</td><td class="num">5</td><td>summit tree about</td><td><span class="tag b-success"><span class="bd"></span>Branded</span></td></tr>''',
          '''<tr><td>/ (home)</td><td class="num">~0</td><td>tree trimming logansport</td><td><span class="tag b-success"><span class="bd"></span>Branded</span></td></tr>
            <tr><td>/services</td><td class="num">0</td><td>—</td><td><span class="tag b-warn"><span class="bd"></span>One shared page</span></td></tr>
            <tr><td>/about</td><td class="num">0</td><td>—</td><td><span class="tag b-success"><span class="bd"></span>Branded</span></td></tr>
            <tr><td>/contact</td><td class="num">0</td><td>—</td><td><span class="tag b-success"><span class="bd"></span>Utility</span></td></tr>
            <tr><td>/free-estimate</td><td class="num">0</td><td>—</td><td><span class="tag b-success"><span class="bd"></span>Conversion</span></td></tr>'''))
R.append(('''<p style="font-size:13px;color:var(--slate);margin-top:12px"><strong>~50% of your traffic is blog content with no service intent.</strong> It reads well but doesn't book jobs.</p>''',
          '''<p style="font-size:13px;color:var(--slate);margin-top:12px"><strong>No page pulls measurable organic traffic.</strong> No blog, no service pages, the homepage is carrying everything, which is almost nothing.</p>'''))

# topical authority -> content footprint (real keyword counts)
R.append(("<h2>Content coverage vs. competitors.</h2>", "<h2>Nobody here has built real content.</h2>"))
R.append(('''<span class="desc">Google ranks the site that covers a topic most completely. Pages per topic cluster, you against the field.</span>''',
          '''<span class="desc">The whole market is thin. Ranking keywords per site, you're last, but a real content build leapfrogs everyone.</span>'''))
R.append(('''<thead><tr><th>Topic cluster</th><th>You</th><th>Oak City</th><th>Triangle</th><th>Carolina</th><th>Raleigh Pros</th></tr></thead>
          <tbody>
            <tr><td>Tree removal</td><td class="lose">1</td><td class="win">8</td><td class="lose">5</td><td class="lose">4</td><td class="lose">3</td></tr>
            <tr><td>Tree trimming &amp; pruning</td><td class="lose">1</td><td class="win">6</td><td class="lose">4</td><td class="lose">3</td><td class="lose">2</td></tr>
            <tr><td>Stump grinding</td><td class="lose">0</td><td class="win">4</td><td class="lose">3</td><td class="lose">2</td><td class="lose">2</td></tr>
            <tr><td>Emergency &amp; storm</td><td class="lose">0</td><td class="win">5</td><td class="lose">3</td><td class="lose">2</td><td class="lose">1</td></tr>
            <tr><td>Land clearing</td><td class="lose">0</td><td class="win">3</td><td class="lose">2</td><td class="lose">1</td><td class="lose">1</td></tr>
            <tr><td>Tree health &amp; disease</td><td class="lose">0</td><td class="win">4</td><td class="lose">2</td><td class="lose">1</td><td class="lose">0</td></tr>
            <tr><td>Commercial / municipal</td><td class="lose">0</td><td class="win">3</td><td class="lose">1</td><td class="lose">1</td><td class="lose">0</td></tr>
            <tr><td><strong>Locations covered</strong></td><td class="lose">2</td><td class="win">14</td><td class="lose">9</td><td class="lose">6</td><td class="lose">5</td></tr>
          </tbody>''',
          '''<thead><tr><th>Content signal</th><th>You</th><th>Heartland</th><th>Straight Cut</th><th>Beachy</th><th>HillTop</th></tr></thead>
          <tbody>
            <tr><td>Keywords ranked</td><td class="lose">2</td><td class="win">8</td><td class="lose">4</td><td class="lose">7</td><td class="lose">0</td></tr>
            <tr><td>Domain authority</td><td class="lose">0.1</td><td class="win">1.6</td><td class="lose">0.0</td><td class="lose">0.0</td><td class="lose">0.7</td></tr>
            <tr><td>Dedicated service pages</td><td class="lose">0</td><td class="win">3</td><td class="lose">1</td><td class="lose">2</td><td class="lose">0</td></tr>
            <tr><td><strong>Location pages</strong></td><td class="lose">0</td><td class="win">2</td><td class="lose">1</td><td class="lose">1</td><td class="lose">0</td></tr>
          </tbody>'''))
R.append(('''<p style="font-size:13px;color:var(--slate);margin-top:12px">You hold <strong>2 of 7</strong> topic clusters with even minimal coverage. The market leader holds all 7 with depth. That gap is why they own the map pack.</p>''',
          '''<p style="font-size:13px;color:var(--slate);margin-top:12px">Even the leader, Heartland, ranks for only 8 keywords. No one here has built real service or location content. The first to do it wins the region.</p>'''))

# thin content -> page inventory
R.append(('''<span class="desc">Every key page, its word count, and what it needs to compete for its target term.</span>''',
          '''<span class="desc">Your full page inventory, and the pages that don't exist yet but need to.</span>'''))
R.append(('''<thead><tr><th>Page</th><th>Word count</th><th>Recommended</th><th>Target keyword</th><th>Status</th></tr></thead>
          <tbody>
            <tr><td>/ (home)</td><td class="num">540</td><td class="num">800+</td><td>tree service raleigh</td><td><span class="tag b-warn"><span class="bd"></span>Below target</span></td></tr>
            <tr><td>/tree-removal</td><td class="num">210</td><td class="num">1,200+</td><td>tree removal raleigh</td><td><span class="tag b-danger"><span class="bd"></span>Thin</span></td></tr>
            <tr><td>/services</td><td class="num">140</td><td class="num">800+</td><td>tree services</td><td><span class="tag b-danger"><span class="bd"></span>Thin</span></td></tr>
            <tr><td>/about</td><td class="num">320</td><td class="num">600+</td><td>about / trust</td><td><span class="tag b-warn"><span class="bd"></span>Below target</span></td></tr>
            <tr><td>/stump-grinding</td><td class="num">—</td><td class="num">1,000+</td><td>stump grinding raleigh</td><td><span class="tag b-danger"><span class="bd"></span>Missing page</span></td></tr>
            <tr><td>/emergency-tree-service</td><td class="num">—</td><td class="num">1,000+</td><td>emergency tree service</td><td><span class="tag b-danger"><span class="bd"></span>Missing page</span></td></tr>
            <tr><td>/contact</td><td class="num">90</td><td class="num">n/a</td><td>contact</td><td><span class="tag b-success"><span class="bd"></span>OK</span></td></tr>
          </tbody>''',
          '''<thead><tr><th>Page</th><th>Status</th><th>What it needs</th></tr></thead>
          <tbody>
            <tr><td>/ (home)</td><td><span class="tag b-warn"><span class="bd"></span>Live</span></td><td>Rework into a brand + region hub</td></tr>
            <tr><td>/services (one page)</td><td><span class="tag b-warn"><span class="bd"></span>Live</span></td><td>Split into a page per service</td></tr>
            <tr><td>/about</td><td><span class="tag b-success"><span class="bd"></span>Live</span></td><td>Add owner + crew for E-E-A-T</td></tr>
            <tr><td>/contact &amp; /free-estimate</td><td><span class="tag b-success"><span class="bd"></span>Live</span></td><td>Fine as-is</td></tr>
            <tr><td>Per-service pages (removal, stump, etc.)</td><td><span class="tag b-danger"><span class="bd"></span>Missing</span></td><td>Build one for each of your 8 services</td></tr>
            <tr><td>Location pages (Peru, Kokomo, &hellip;)</td><td><span class="tag b-danger"><span class="bd"></span>Missing</span></td><td>Build per nearby city</td></tr>
            <tr><td>Blog / topical content</td><td><span class="tag b-danger"><span class="bd"></span>Missing</span></td><td>Start a hub-supporting blog</td></tr>
          </tbody>'''))

# content gap
R.append(('''<tr><td>emergency tree service</td><td class="num">4 of 4</td><td class="num">0</td><td class="num">880</td><td><span class="tag b-danger"><span class="bd"></span>High</span></td></tr>
            <tr><td>commercial tree service</td><td class="num">4 of 4</td><td class="num">0</td><td class="num">210</td><td><span class="tag b-danger"><span class="bd"></span>High</span></td></tr>
            <tr><td>land clearing</td><td class="num">3 of 4</td><td class="num">0</td><td class="num">410</td><td><span class="tag b-danger"><span class="bd"></span>High</span></td></tr>
            <tr><td>tree cabling &amp; bracing</td><td class="num">3 of 4</td><td class="num">0</td><td class="num">170</td><td><span class="tag b-warn"><span class="bd"></span>Medium</span></td></tr>
            <tr><td>arborist consultation</td><td class="num">2 of 4</td><td class="num">0</td><td class="num">90</td><td><span class="tag b-warn"><span class="bd"></span>Medium</span></td></tr>''',
          '''<tr><td>tree removal near me</td><td class="num">most</td><td class="num">0</td><td class="num">60,500</td><td><span class="tag b-danger"><span class="bd"></span>High</span></td></tr>
            <tr><td>tree removal cost</td><td class="num">national</td><td class="num">0</td><td class="num">12,100</td><td><span class="tag b-danger"><span class="bd"></span>High</span></td></tr>
            <tr><td>emergency tree service logansport</td><td class="num">leaders</td><td class="num">0</td><td class="num">local</td><td><span class="tag b-danger"><span class="bd"></span>High</span></td></tr>
            <tr><td>tree service [nearby town]</td><td class="num">leaders</td><td class="num">0</td><td class="num">expansion</td><td><span class="tag b-danger"><span class="bd"></span>High</span></td></tr>
            <tr><td>timber milling / lumber</td><td class="num">0 of 4</td><td class="num">0</td><td class="num">niche</td><td><span class="tag b-warn"><span class="bd"></span>Your edge</span></td></tr>'''))

# technical / health score
R.append(("<h2>Is the foundation broken, too?</h2>", "<h2>The foundation's fine. The site is empty.</h2>"))
R.append(('''<span class="desc">Content aside, here's the health of the site itself, the part Google has to crawl and trust.</span>''',
          '''<span class="desc">The technical basics check out. What's missing is content, structure, and clean links.</span>'''))
R.append(('''<div class="gauge" style="--val:54;--gc:var(--warning);margin:0 auto 14px;width:180px;height:180px"><div class="inner" style="width:138px;height:138px"><div><div class="g-val" style="font-size:46px">54</div><div class="g-lab">Site health</div></div></div></div>
          <div class="badge b-warn"><span class="bd"></span>Needs work</div>''',
          '''<div class="gauge" style="--val:42;--gc:var(--warning);margin:0 auto 14px;width:180px;height:180px"><div class="inner" style="width:138px;height:138px"><div><div class="g-val" style="font-size:46px">42</div><div class="g-lab">Site health</div></div></div></div>
          <div class="badge b-warn"><span class="bd"></span>Needs work</div>'''))
R.append(('''<div class="cat"><span class="cn">Performance</span><div class="mini-bar"><i style="width:48%"></i></div><span class="cv">48</span></div>
          <div class="cat"><span class="cn">On-page SEO</span><div class="mini-bar"><i style="width:61%"></i></div><span class="cv">61</span></div>
          <div class="cat"><span class="cn">Technical / crawl</span><div class="mini-bar"><i style="width:57%"></i></div><span class="cv">57</span></div>
          <div class="cat"><span class="cn">Content depth</span><div class="mini-bar"><i style="width:44%"></i></div><span class="cv">44</span></div>
          <div class="cat"><span class="cn">Authority / backlinks</span><div class="mini-bar"><i style="width:33%"></i></div><span class="cv">33</span></div>
          <div class="cat"><span class="cn">Schema / structured data</span><div class="mini-bar"><i style="width:20%"></i></div><span class="cv">20</span></div>''',
          '''<div class="cat"><span class="cn">Foundation (HTTPS, mobile)</span><div class="mini-bar"><i style="width:88%"></i></div><span class="cv">88</span></div>
          <div class="cat"><span class="cn">On-page basics</span><div class="mini-bar"><i style="width:70%"></i></div><span class="cv">70</span></div>
          <div class="cat"><span class="cn">Schema</span><div class="mini-bar"><i style="width:65%"></i></div><span class="cv">65</span></div>
          <div class="cat"><span class="cn">Content depth</span><div class="mini-bar"><i style="width:12%"></i></div><span class="cv">12</span></div>
          <div class="cat"><span class="cn">Site structure (pages)</span><div class="mini-bar"><i style="width:10%"></i></div><span class="cv">10</span></div>
          <div class="cat"><span class="cn">Authority / backlinks</span><div class="mini-bar"><i style="width:8%"></i></div><span class="cv">8</span></div>'''))

# crawl summary
R.append(('''<div class="section-head"><h2>What the crawl found.</h2><span class="desc">28 URLs crawled, April 2026.</span></div>''',
          '''<div class="section-head"><h2>What the crawl found.</h2><span class="desc">Full site is 5 pages, June 2026.</span></div>'''))
R.append(('''<div class="stat"><div class="lab">Pages crawled</div><div class="val">28</div></div>
        <div class="stat"><div class="lab">4xx / 5xx errors</div><div class="val down">5</div><div class="sub down">broken links</div></div>
        <div class="stat"><div class="lab">Missing meta desc</div><div class="val down">14</div></div>
        <div class="stat"><div class="lab">Missing / dup H1</div><div class="val down">9</div></div>''',
          '''<div class="stat"><div class="lab">Total pages</div><div class="val">5</div></div>
        <div class="stat"><div class="lab">Service pages</div><div class="val down">0</div><div class="sub down">8 services, 1 page</div></div>
        <div class="stat"><div class="lab">Location pages</div><div class="val down">0</div></div>
        <div class="stat"><div class="lab">Blog posts</div><div class="val down">0</div></div>'''))
R.append(('''<thead><tr><th>Issue</th><th>Pages affected</th><th>Severity</th></tr></thead>
          <tbody>
            <tr><td>Broken internal links (404)</td><td>5</td><td><span class="badge b-danger"><span class="bd"></span>High</span></td></tr>
            <tr><td>Missing meta descriptions</td><td>14</td><td><span class="badge b-warn"><span class="bd"></span>Medium</span></td></tr>
            <tr><td>Thin content (&lt;300 words)</td><td>11</td><td><span class="badge b-warn"><span class="bd"></span>Medium</span></td></tr>
            <tr><td>Images missing alt text</td><td>63</td><td><span class="badge b-warn"><span class="bd"></span>Medium</span></td></tr>
            <tr><td>No HTTPS redirect on www</td><td>1</td><td><span class="badge b-danger"><span class="bd"></span>High</span></td></tr>
          </tbody>''',
          '''<thead><tr><th>Finding</th><th>Detail</th><th>Severity</th></tr></thead>
          <tbody>
            <tr><td>No per-service pages</td><td>8 services share one page</td><td><span class="badge b-danger"><span class="bd"></span>High</span></td></tr>
            <tr><td>No location pages</td><td>0 of your towns covered</td><td><span class="badge b-danger"><span class="bd"></span>High</span></td></tr>
            <tr><td>Toxic referring domains</td><td>spike to 176, DR fell</td><td><span class="badge b-danger"><span class="bd"></span>High</span></td></tr>
            <tr><td>No blog / topical content</td><td>0 posts</td><td><span class="badge b-warn"><span class="bd"></span>Medium</span></td></tr>
            <tr><td>Foundation (HTTPS, mobile, schema)</td><td>present and OK</td><td><span class="badge b-success"><span class="bd"></span>Pass</span></td></tr>
          </tbody>'''))

# remove Core Web Vitals section (no real data)
R.append(('''
  <!-- CORE WEB VITALS -->
  <section>
    <div class="container">
      <div class="eyebrow"><span class="eb-dash"></span>Technical</div>
      <div class="section-head"><h2>Performance.</h2><span class="desc">Google grades you on this. So do your visitors.</span></div>
      <div class="grid-3">
        <div class="card" style="text-align:center"><div class="gauge" style="--val:40;--gc:var(--danger);margin:0 auto 14px"><div class="inner"><div><div class="g-val">4.1s</div><div class="g-lab">LCP</div></div></div></div><div class="badge b-danger"><span class="bd"></span>Poor</div></div>
        <div class="card" style="text-align:center"><div class="gauge" style="--val:62;--gc:var(--warning);margin:0 auto 14px"><div class="inner"><div><div class="g-val">240ms</div><div class="g-lab">INP</div></div></div></div><div class="badge b-warn"><span class="bd"></span>Needs work</div></div>
        <div class="card" style="text-align:center"><div class="gauge" style="--val:85;--gc:var(--success);margin:0 auto 14px"><div class="inner"><div><div class="g-val">0.06</div><div class="g-lab">CLS</div></div></div></div><div class="badge b-success"><span class="bd"></span>Good</div></div>
      </div>
    </div>
  </section>
''', '\n'))

# technical checklist
R.append(('''<div class="ci"><div><div class="ct">HTTPS / SSL</div><div class="cd">Secure across the site</div></div><span class="st badge b-success"><span class="bd"></span>Pass</span></div>
          <div class="ci"><div><div class="ct">XML sitemap</div><div class="cd">Present and submitted</div></div><span class="st badge b-success"><span class="bd"></span>Pass</span></div>
          <div class="ci"><div><div class="ct">Robots.txt</div><div class="cd">Crawl-delay injected by CDN</div></div><span class="st badge b-warn"><span class="bd"></span>Warn</span></div>
          <div class="ci"><div><div class="ct">LocalBusiness schema</div><div class="cd">Missing on all pages</div></div><span class="st badge b-danger"><span class="bd"></span>Fail</span></div>
          <div class="ci"><div><div class="ct">Indexation</div><div class="cd">9 of 28 pages not indexed</div></div><span class="st badge b-warn"><span class="bd"></span>Warn</span></div>
          <div class="ci"><div><div class="ct">Canonical tags</div><div class="cd">Correctly set</div></div><span class="st badge b-success"><span class="bd"></span>Pass</span></div>''',
          '''<div class="ci"><div><div class="ct">HTTPS / SSL</div><div class="cd">Secure across the site</div></div><span class="st badge b-success"><span class="bd"></span>Pass</span></div>
          <div class="ci"><div><div class="ct">Mobile-friendly</div><div class="cd">Responsive viewport set</div></div><span class="st badge b-success"><span class="bd"></span>Pass</span></div>
          <div class="ci"><div><div class="ct">XML sitemap</div><div class="cd">Present</div></div><span class="st badge b-success"><span class="bd"></span>Pass</span></div>
          <div class="ci"><div><div class="ct">Local schema</div><div class="cd">JSON-LD present on homepage</div></div><span class="st badge b-success"><span class="bd"></span>Pass</span></div>
          <div class="ci"><div><div class="ct">Service &amp; location pages</div><div class="cd">None exist yet</div></div><span class="st badge b-danger"><span class="bd"></span>Fail</span></div>
          <div class="ci"><div><div class="ct">Content depth</div><div class="cd">5-page site, no blog</div></div><span class="st badge b-danger"><span class="bd"></span>Fail</span></div>'''))

# GBP competitor audit -> reviews/rating only (real)
R.append(('''<thead><tr><th>Business</th><th>Reviews</th><th>Rating</th><th>Photos</th><th>Categories</th><th>Posting</th></tr></thead>
          <tbody>
            <tr><td class="cmp-you">Summit Tree &amp; Land (you)</td><td class="lose">37</td><td class="lose">4.6</td><td class="lose">24</td><td class="lose">2</td><td class="lose">None</td></tr>
            <tr><td>Oak City Tree Service</td><td class="win">168</td><td class="win">4.9</td><td class="win">210</td><td class="win">4</td><td class="win">Weekly</td></tr>
            <tr><td>Triangle Tree Service</td><td class="lose">156</td><td class="lose">4.8</td><td class="lose">180</td><td class="lose">3</td><td class="win">Weekly</td></tr>
            <tr><td>Carolina Tree Care</td><td class="lose">98</td><td class="lose">4.7</td><td class="lose">96</td><td class="lose">3</td><td class="lose">Monthly</td></tr>
            <tr><td>Raleigh Tree Pros</td><td class="lose">76</td><td class="lose">4.7</td><td class="lose">60</td><td class="lose">2</td><td class="lose">Rarely</td></tr>
          </tbody>''',
          '''<thead><tr><th>Business</th><th>Reviews</th><th>Rating</th><th>Market</th></tr></thead>
          <tbody>
            <tr><td class="cmp-you">Vivid Tree Service (you)</td><td class="lose">55</td><td class="win">5.0</td><td>Logansport</td></tr>
            <tr><td>Heartland Tree Service</td><td class="win">233</td><td class="win">5.0</td><td>Kokomo</td></tr>
            <tr><td>Straight Cut Tree Service</td><td class="lose">120</td><td class="win">5.0</td><td>Royal Center</td></tr>
            <tr><td>Beachy Tree Service</td><td class="lose">73</td><td class="win">5.0</td><td>Peru</td></tr>
            <tr><td>HillTop Tree Service</td><td class="lose">41</td><td class="lose">4.7</td><td>Akron</td></tr>
          </tbody>'''))
R.append(('''<p style="font-size:13px;color:var(--slate);margin-top:12px">You're behind on every signal Google weighs for the map pack: review volume, photos, categories, and fresh posts.</p>''',
          '''<p style="font-size:13px;color:var(--slate);margin-top:12px">You're tied for the best rating in the market and mid-pack on volume, a real strength. Heartland's review lead is what we close as you push into their backyard.</p>'''))

# backlink comparison -> real
R.append(('''<tr><td class="cmp-you">Summit Tree &amp; Land (you)</td><td class="lose">42</td><td class="lose">6</td><td class="lose">28%</td></tr>
            <tr><td>Oak City Tree Service</td><td class="win">131</td><td class="win">17</td><td class="win">9%</td></tr>
            <tr><td>Triangle Tree Service</td><td class="lose">104</td><td class="lose">14</td><td class="win">14%</td></tr>
            <tr><td>Carolina Tree Care</td><td class="lose">71</td><td class="lose">11</td><td class="lose">22%</td></tr>''',
          '''<tr><td class="cmp-you">Vivid Tree Service (you)</td><td class="lose">176</td><td class="lose">0.1</td><td class="lose">45%</td></tr>
            <tr><td>Heartland Tree Service</td><td class="win">183</td><td class="win">1.6</td><td class="win">25%</td></tr>
            <tr><td>Straight Cut Tree Service</td><td class="lose">167</td><td class="lose">0.0</td><td class="lose">35%</td></tr>
            <tr><td>Beachy Tree Service</td><td class="lose">178</td><td class="lose">0.0</td><td class="lose">30%</td></tr>'''))
R.append(('''<p style="font-size:13px;color:var(--slate);margin-top:12px">Anything over <strong>20% spam links</strong> drags your authority and risks a penalty. At 28%, yours is the highest in the market and needs a cleanup. Spam share is estimated from referring-domain quality.</p>''',
          '''<p style="font-size:13px;color:var(--slate);margin-top:12px">The whole local market runs low-quality link profiles. Yours spiked worst (34 → 176 domains while authority fell), so cleanup is first, then we rebuild with links that actually count. Spam share is estimated from referring-domain quality.</p>'''))

# projection callouts
R.append(('''<div class="callout" style="background:var(--success-bg);border-color:var(--success)"><div><div class="cl-t" style="color:var(--success)">Projected traffic · month 12</div><div class="cl-s">From ~90 today</div></div><div class="cl-v" style="color:var(--success)">~520</div></div>
        <div class="callout" style="background:var(--success-bg);border-color:var(--success)"><div><div class="cl-t" style="color:var(--success)">Bottom-funnel keywords · month 12</div><div class="cl-s">From 8 today</div></div><div class="cl-v" style="color:var(--success)">45+</div></div>''',
          '''<div class="callout" style="background:var(--success-bg);border-color:var(--success)"><div><div class="cl-t" style="color:var(--success)">Projected organic traffic · month 12</div><div class="cl-s">From ~0 today</div></div><div class="cl-v" style="color:var(--success)">~400</div></div>
        <div class="callout" style="background:var(--success-bg);border-color:var(--success)"><div><div class="cl-t" style="color:var(--success)">Ranking keywords · month 12</div><div class="cl-s">From 2 today</div></div><div class="cl-v" style="color:var(--success)">30+</div></div>'''))

# ================= JS CHART DATA =================
R.append(("const RETAINER=2500;", "const RETAINER=1500;"))
# traffic chart -> flat ~0
R.append(("data:[140,135,150,128,120,110,118,105,99,108,96,90],borderColor:ORANGE",
          "data:[0,0,0,1,0,0,1,0,0,0,0,0],borderColor:ORANGE"))
# competitor labels + bars
R.append("const CMP_LABELS=['You','Oak City','Triangle','Carolina','Raleigh Pros'];")
R[-1] = ("const CMP_LABELS=['You','Oak City','Triangle','Carolina','Raleigh Pros'];",
         "const CMP_LABELS=['You','Heartland','Straight Cut','Beachy','HillTop'];")
R.append(("cmpBars('compReviews',[37,168,156,98,76]);", "cmpBars('compReviews',[55,233,120,73,41]);"))
R.append(("cmpBars('compDR',[6,17,14,11,9]);", "cmpBars('compDR',[0.1,1.6,0,0,0.7]);"))
R.append(("cmpBars('compKw',[88,312,290,177,142]);", "cmpBars('compKw',[2,8,4,7,0]);"))
# backlink chart -> real refdomains spike
R.append(("datasets:[{data:[30,31,33,34,36,36,38,38,40,41,41,42],backgroundColor:ORANGE,borderRadius:4}]",
          "datasets:[{data:[42,44,45,47,47,57,49,40,18,34,172,176],backgroundColor:ORANGE,borderRadius:4}]"))
# organic trend -> flat zero
R.append(("data:[150,148,132,120,128,140,135,118,128,110,99,90],borderColor:ORANGE,backgroundColor:'rgba(251,86,7,.10)',fill:true,tension:.4,pointRadius:0,borderWidth:3,yAxisID:'y'",
          "data:[0,0,0,0,1,0,0,1,0,0,0,0],borderColor:ORANGE,backgroundColor:'rgba(251,86,7,.10)',fill:true,tension:.4,pointRadius:0,borderWidth:3,yAxisID:'y'"))
R.append(("data:[520,510,470,430,455,500,540,480,500,430,360,310],borderColor:INK",
          "data:[0,0,0,0,0,0,0,0,0,0,0,0],borderColor:INK"))
# projection
R.append(("data:[90,84,80,76,72,69,66],borderColor:'#C42017'", "data:[0,0,0,0,0,0,0],borderColor:'#C42017'"))
R.append(("data:[90,140,210,300,390,460,520],borderColor:'#1F7A4D'", "data:[0,40,110,200,300,380,450],borderColor:'#1F7A4D'"))

# ---------- apply ----------
missing=[]
for old,new in R:
    if old not in s:
        missing.append(old[:70])
    else:
        s = s.replace(old, new)
open(P,"w",encoding="utf-8").write(s)
print("applied", len(R)-len(missing), "of", len(R), "replacements")
if missing:
    print("MISSING (not found):")
    for m in missing: print("  -", repr(m))
