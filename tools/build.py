#!/usr/bin/env python3
"""FinSight portfolio build: MD -> styled HTML -> PDF, prototype screenshots."""
import re
import subprocess
import pathlib
import markdown

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

RESUME_CSS = """
@page { size: A4; margin: 11mm 13mm; }
* { box-sizing: border-box; }
body { font-family: "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
  color: #1a1a1a; font-size: 8.8pt; line-height: 1.38; max-width: 184mm; margin: 0 auto; }
h1 { font-size: 16pt; margin: 0 0 2px; border-bottom: 2px solid #1a1a1a; padding-bottom: 3px; }
h2 { font-size: 10.5pt; margin: .9em 0 .35em; border-left: 3.5px solid #444; padding-left: 7px; }
h3 { font-size: 9.5pt; margin: .65em 0 .2em; }
p { margin: .25em 0; }
ul { margin: .18em 0 .35em; padding-left: 1.2em; }
li { margin: .1em 0; }
hr { border: none; page-break-after: always; }
table { border-collapse: collapse; width: 100%; font-size: 7.9pt; margin: 4px 0; }
th, td { border: 1px solid #bbb; padding: 2.5px 5px; text-align: left; vertical-align: top; }
th { background: #f0f0f0; }
blockquote { border-left: 3px solid #999; margin: 3px 0; padding-left: 8px; color: #444; }
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

def replace_mermaid_with_svgs(text: str) -> str:
    diagram = 0

    def replace(match: re.Match[str]) -> str:
        nonlocal diagram
        diagram += 1
        svg = ROOT / "assets" / "diagrams" / f"diagram-{diagram}.svg"
        if not svg.exists():
            raise FileNotFoundError(f"Missing rendered diagram: {svg}")
        return (
            '<p style="text-align:center;page-break-inside:avoid">'
            f'<img src="../assets/diagrams/diagram-{diagram}.svg" '
            'style="max-width:100%;max-height:235mm" alt="架构图">'
            '</p>'
        )

    result = re.sub(r"```mermaid\n(.*?)```", replace, text, flags=re.S)
    if diagram != 8:
        raise ValueError(f"Expected 8 Mermaid diagrams, found {diagram}")
    return result


def md_to_html(md_path: pathlib.Path, use_mermaid: bool) -> pathlib.Path:
    text = md_path.read_text(encoding="utf-8")
    if use_mermaid:
        text = replace_mermaid_with_svgs(text)
    body = markdown.markdown(text, extensions=["tables", "fenced_code"])
    css = RESUME_CSS if md_path.name == "02_周子涵_参赛简历.md" else CSS
    html = f"<!DOCTYPE html><html lang='zh-CN'><head><meta charset='utf-8'><style>{css}</style></head><body>{body}</body></html>"
    out = BUILD / (md_path.stem + ".html")
    out.write_text(html, encoding="utf-8")
    return out

def chrome(args, timeout=150):
    subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--disable-background-networking", "--no-pdf-header-footer"] + args,
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
