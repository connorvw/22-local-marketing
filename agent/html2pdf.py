#!/usr/bin/env python3
"""
html2pdf.py - Render HTML (a file or a URL) to a polished PDF via Cloudflare
Browser Rendering (real headless Chrome). No npm, no local install.

Usage:
    python html2pdf.py --html report.html --out report.pdf
    python html2pdf.py --url https://example.com --out page.pdf

Requirements:
    - CLOUDFLARE_API_TOKEN in the environment, with the "Browser Run" (Browser
      Rendering) permission. Everything else is stdlib.

Notes:
    - Page size, orientation, and margins come from the HTML's own CSS
      @page rule, e.g.  @page { size: Letter; margin: 24px; }
      For landscape:    @page { size: Letter landscape; }
    - Background colors/images are OFF by default when Chrome prints. This
      script injects `print-color-adjust: exact` so brand backgrounds render.
    - A URL behind Cloudflare Access (e.g. reports.victreewebsites.com) will
      render the login page, not the report. Use --html for those.
"""
import argparse
import json
import os
import sys
import urllib.request
import urllib.error

ACCOUNT_ID = "ff4bcfdaf56c61c138988bc01d894d84"
ENDPOINT = f"https://api.cloudflare.com/client/v4/accounts/{ACCOUNT_ID}/browser-rendering/pdf"
# Forces Chrome to print background colors/images (suppressed by default in print).
COLOR_FIX = "html{-webkit-print-color-adjust:exact;print-color-adjust:exact}"


def main():
    ap = argparse.ArgumentParser(description="HTML/URL to PDF via Cloudflare Browser Rendering")
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--html", help="path to an HTML file")
    src.add_argument("--url", help="a URL to render")
    ap.add_argument("--out", required=True, help="output .pdf path")
    args = ap.parse_args()

    token = os.environ.get("CLOUDFLARE_API_TOKEN")
    if not token:
        sys.exit("CLOUDFLARE_API_TOKEN is not set in the environment.")

    body = {"addStyleTag": [{"content": COLOR_FIX}]}
    if args.html:
        with open(args.html, encoding="utf-8") as f:
            body["html"] = f.read()
    else:
        body["url"] = args.url

    req = urllib.request.Request(
        ENDPOINT,
        data=json.dumps(body).encode("utf-8"),
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        method="POST",
    )
    try:
        data = urllib.request.urlopen(req, timeout=90).read()
    except urllib.error.HTTPError as e:
        sys.exit(f"Cloudflare error {e.code}: {e.read().decode('utf-8', 'replace')[:400]}")

    if data[:4] != b"%PDF":
        sys.exit(f"Response was not a PDF: {data[:400]!r}")

    with open(args.out, "wb") as f:
        f.write(data)
    print(f"Wrote {args.out} ({len(data):,} bytes)")


if __name__ == "__main__":
    main()
