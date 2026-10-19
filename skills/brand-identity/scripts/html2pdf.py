#!/usr/bin/env python3
"""HTML -> A4 PDF via headless Chrome; prints page count. Usage: html2pdf.py in.html out.pdf"""
import os, re, subprocess, sys, shutil, tempfile
CANDS = ["/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
         "/Applications/Chromium.app/Contents/MacOS/Chromium",
         shutil.which("google-chrome") or "", shutil.which("chromium") or ""]
chrome = next((c for c in CANDS if c and os.path.exists(c)), None)
if not chrome: sys.exit("No Chrome/Chromium found. Open the HTML and print to PDF (A4, margins none, background graphics on).")
src, out = os.path.abspath(sys.argv[1]), os.path.abspath(sys.argv[2])
prof = tempfile.mkdtemp(prefix="bb-chrome-")
subprocess.run([chrome, "--headless=new", f"--user-data-dir={prof}", "--no-first-run", "--disable-gpu", "--no-pdf-header-footer",
                f"--print-to-pdf={out}", "file://" + src], check=True, capture_output=True, timeout=120)
data = open(out, "rb").read()
pages = len(re.findall(rb"/Type\s*/Page[^s]", data))
html = open(src, encoding="utf-8").read()
want = html.count("class='page")
print(f"{out}: {pages} pages (html pages: {want})" + ("" if pages == want else "  MISMATCH: a section overflowed, shorten it"))
sys.exit(0 if pages == want else 2)
