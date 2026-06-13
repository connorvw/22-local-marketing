#!/usr/bin/env python3
"""
Pre-publish validator for 22LM proposals.

Catches the class of bug that silently kills the whole page: a JS syntax error
(e.g. an apostrophe inside a single-quoted string) takes down EVERY interactive
feature at once, not just the broken section.

What it does:
  1. Extracts every inline <script> block from the proposal HTML.
  2. Runs `node --check` on each (parse only, never executes), so any syntax
     error is reported with its line, column, and the offending source line.
  3. Warns about unfilled {{TOKEN}} placeholders left in the file.

Exit code 0 = safe to publish. Non-zero = do not publish.

Usage:  python validate.py path/to/proposal.html
        python validate.py            # defaults to template/index.html
"""
import re
import subprocess
import sys
import tempfile
import os

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT = os.path.join(HERE, "template", "index.html")

# inline <script> blocks only (skip <script src="...">)
SCRIPT_RE = re.compile(r"<script(?![^>]*\bsrc=)[^>]*>(.*?)</script>", re.DOTALL | re.IGNORECASE)
TOKEN_RE = re.compile(r"\{\{[A-Z0-9_]+\}\}")


def check_js(html_path):
    with open(html_path, "r", encoding="utf-8") as f:
        html = f.read()

    errors = []
    # line offset of each script so node's line numbers can map back to the HTML
    for idx, m in enumerate(SCRIPT_RE.finditer(html), start=1):
        body = m.group(1)
        html_start_line = html[: m.start(1)].count("\n") + 1
        with tempfile.NamedTemporaryFile(
            "w", suffix=".js", delete=False, encoding="utf-8"
        ) as tf:
            tf.write(body)
            tmp = tf.name
        try:
            res = subprocess.run(
                ["node", "--check", tmp], capture_output=True, text=True
            )
        finally:
            os.unlink(tmp)
        if res.returncode != 0:
            # node reports line numbers relative to the extracted script;
            # add the HTML offset so the message points at the real file line.
            stderr = res.stderr
            ln = re.search(r":(\d+)\b", stderr.splitlines()[0]) if stderr else None
            html_line = (html_start_line + int(ln.group(1)) - 1) if ln else "?"
            errors.append((idx, html_line, stderr.strip()))

    tokens = sorted(set(TOKEN_RE.findall(html)))
    return errors, tokens


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT
    if not os.path.exists(path):
        print(f"FAIL  file not found: {path}")
        sys.exit(2)

    errors, tokens = check_js(path)

    if errors:
        print(f"FAIL  {len(errors)} JavaScript syntax error(s) in {path}\n")
        for idx, html_line, msg in errors:
            print(f"  <script> #{idx}  (around HTML line {html_line}):")
            for line in msg.splitlines():
                print(f"    {line}")
            print()
        print("Do NOT publish. A JS syntax error disables every interactive feature.")
        sys.exit(1)

    print(f"PASS  JavaScript parses cleanly: {path}")
    if tokens:
        print(f"\nWARN  {len(tokens)} unfilled placeholder(s) still in the file:")
        for t in tokens:
            print(f"    {t}")
        print("  These are expected in the template; fill them per prospect before publishing.")
    sys.exit(0)


if __name__ == "__main__":
    main()
