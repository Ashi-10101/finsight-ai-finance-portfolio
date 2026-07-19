#!/usr/bin/env python3
"""FinSight portfolio build: MD -> styled HTML -> PDF (Chrome headless), prototype screenshots."""
import subprocess, pathlib, markdown

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = pathlib.Path("/Users/ashi/Downloads/OpenCode/金策_FinSight_报名材料")
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
BUILD = ROOT / "build"
PDFS = ROOT / "pdfs"
SHOTS = ROOT / "assets" / "screenshots"
for d in (BUILD, PDFS, SHOTS):
    d.mkdir(parents=True, exist_ok=True)

CSS = """
@page { size: A4; margin: 18mm 16mm; }
* { box-sizing: border-box; }
body { font-family: "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
  color: #1a1a1a; font-size: 10.5pt; line-height: 1.65; max-width: 180mm; margin: 0 auto; }
h1 { font-size: 20pt; border-bottom: 2.5px solid #1a1a1a; padding-bottom: 6px; }
h2 { font-size: 14pt; margin-top: 1.4em; border-left: 4px solid #444; padding-left: 8px; }
h3 { font-size: 11.5pt; }
hr { border: none; page-break-after: always; }
table { border-collapse: collapse; width: 100%; font-size: 9pt; margin: 8px 0; }
th, td { border: 1px solid #bbb; padding: 4px 7px; text-align: left; vertical-align: top; }
th { background: #f0f0f0; }
code, pre { font-family: "SF Mono", Menlo, monospace; font-size: 8.5pt; }
pre { background: #f6f6f6; border: 1px solid #ddd; padding: 8px; white-space: pre-wrap; word-break: break-all; }
blockquote { border-left: 3px solid #999; margin-left: 0; padding-left: 10px; color: #444; }
.mermaid { text-align: center; }
strong { color: #000; }
"""

MERMAID_SNIPPET = """
<script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
<script>mermaid.initialize({startOnLoad:true, theme:"neutral", securityLevel:"loose"});</script>
"""

DOCS = [
    ("01_金策_FinSight_开题方案.md", "01_金策_FinSight_开题方案.pdf", False),
    ("02_周子涵_参赛简历.md", "02_周子涵_参赛简历.pdf", False),
    ("03_周子涵_AI与金融科技项目作品集.md", "03_周子涵_AI与金融科技项目作品集.pdf", False),
    ("04_金策_FinSight_行业与竞品研究.md", "04_金策_FinSight_行业与竞品研究.pdf", False),
    ("06_金策_FinSight_技术架构与业务流程.md", "06_金策_FinSight_技术架构与业务流程.pdf", True),
    ("H_评测方案.md", "金策_FinSight_评测方案.pdf", False),
    ("09_样本/I_数据分析与报告样本.md", "金策_FinSight_数据分析与报告样本.pdf", False),
]

def md_to_html(md_path: pathlib.Path, use_mermaid: bool) -> pathlib.Path:
    text = md_path.read_text(encoding="utf-8")
    if use_mermaid:
        # wrap ```mermaid blocks into <pre class="mermaid">
        out, in_m, buf = [], False, []
        for line in text.splitlines():
            if line.strip().startswith("```"):
                if not in_m and "mermaid" in line:
                    in_m, buf = True, []
                    continue
                elif in_m:
                    out.append('<pre class="mermaid">' + "\n".join(buf) + "</pre>")
                    in_m = False
                    continue
            if in_m:
                buf.append(line)
            else:
                out.append(line)
        text = "\n".join(out)
    body = markdown.markdown(text, extensions=["tables", "fenced_code"])
    html = f"<!DOCTYPE html><html lang='zh-CN'><head><meta charset='utf-8'><style>{CSS}</style>{MERMAID_SNIPPET if use_mermaid else ''}</head><body>{body}</body></html>"
    out = BUILD / (md_path.stem + ".html")
    out.write_text(html, encoding="utf-8")
    return out

def chrome(args, timeout=90):
    subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--no-pdf-header-footer"] + args,
                   check=True, timeout=timeout, capture_output=True)

for md_name, pdf_name, use_m in DOCS:
    md_path = SRC / md_name
    if not md_path.exists():
        print("SKIP missing:", md_name); continue
    html = md_to_html(md_path, use_m)
    chrome(["--virtual-time-budget=15000", f"--print-to-pdf={PDFS / pdf_name}", html.as_uri()])
    print("PDF:", pdf_name)

PROTO = ROOT / "prototype"
for f in sorted(PROTO.glob("*.html")):
    chrome([f"--screenshot={SHOTS / (f.stem + '.png')}", "--window-size=1600,1000",
            "--hide-scrollbars", f.as_uri()])
    print("SHOT:", f.stem)
print("BUILD DONE")
