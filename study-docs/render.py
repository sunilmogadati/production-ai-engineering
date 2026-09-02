#!/usr/bin/env python3
# Render an ML study doc (.md) to a self-contained HTML that shows Mermaid
# diagrams, LaTeX math (MathJax), and the local PNG figures in ML_Study_Figures/.
#
# Usage:
#   python3 render.py                       # renders ML_Study_01 next to this script
#   python3 render.py SomeDoc.md            # renders SomeDoc.md -> SomeDoc.html
#   python3 render.py SomeDoc.md out.html   # explicit output path
import re, html, markdown, sys, os, base64

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "ML_Study_01_Linear_Regression.md")
OUT = sys.argv[2] if len(sys.argv) > 2 else os.path.splitext(SRC)[0] + ".html"

text = open(SRC, encoding="utf-8").read()
_tm = re.search(r"^#\s+(.+)$", text, re.MULTILINE)
TITLE = _tm.group(1).strip() if _tm else os.path.basename(SRC)

mermaid_blocks, math_blocks = [], []

# 1) Protect ```mermaid ... ``` fences
def _grab_mermaid(m):
    mermaid_blocks.append(m.group(1))
    return f"\n\n@@MERMAID{len(mermaid_blocks)-1}@@\n\n"
text = re.sub(r"```mermaid\n(.*?)```", _grab_mermaid, text, flags=re.DOTALL)

# 2) Protect display math $$ ... $$
def _grab_display(m):
    math_blocks.append(("display", m.group(1).strip()))
    return f"@@MATH{len(math_blocks)-1}@@"
text = re.sub(r"\$\$(.+?)\$\$", _grab_display, text, flags=re.DOTALL)

# 3) Protect inline math $ ... $  (single line)
def _grab_inline(m):
    math_blocks.append(("inline", m.group(1).strip()))
    return f"@@MATH{len(math_blocks)-1}@@"
text = re.sub(r"\$([^\n$]+?)\$", _grab_inline, text)

# 4) Markdown -> HTML
body = markdown.markdown(text, extensions=["extra", "sane_lists", "toc"])

# 5) Restore math as MathJax delimiters
def _restore_math(m):
    kind, code = math_blocks[int(m.group(1))]
    return f"\\[{code}\\]" if kind == "display" else f"\\({code}\\)"
body = re.sub(r"@@MATH(\d+)@@", _restore_math, body)

# 6) Restore mermaid as <div class="mermaid">
def _restore_mermaid(m):
    code = html.escape(mermaid_blocks[int(m.group(1))].strip())
    return f'<div class="mermaid">{code}</div>'
body = re.sub(r"@@MERMAID(\d+)@@", _restore_mermaid, body)
body = re.sub(r"<p>(<div class=\"mermaid\">.*?</div>)</p>", r"\1", body, flags=re.DOTALL)

# 7) Inline local figures as base64 data URIs so the HTML is fully self-contained
#    (renders without file-system access — needed under macOS-protected folders, and makes it shareable)
def _inline_img(m):
    rel = m.group(1)
    path = os.path.join(os.path.dirname(os.path.abspath(SRC)), rel)
    try:
        with open(path, "rb") as f:
            data = base64.b64encode(f.read()).decode()
        return f'src="data:image/png;base64,{data}"'
    except FileNotFoundError:
        print("  !! missing figure:", rel)
        return m.group(0)
body = re.sub(r'src="(?!https?://|data:)([^"]+\.(?:png|jpe?g|gif|webp))"', _inline_img, body)

TEMPLATE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<script>
  window.MathJax = {{ tex: {{ inlineMath: [['\\\\(','\\\\)']], displayMath: [['\\\\[','\\\\]']] }},
                      svg: {{ fontCache: 'global' }} }};
</script>
<script src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-svg.js" async></script>
<script type="module">
  import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
  mermaid.initialize({{ startOnLoad: true, theme: 'default', securityLevel: 'loose' }});
</script>
<style>
  :root {{ color-scheme: light dark; }}
  body {{ max-width: 900px; margin: 2rem auto; padding: 0 1.2rem;
         font: 16px/1.65 -apple-system, Segoe UI, Roboto, Helvetica, Arial, sans-serif;
         color: #1a1a1a; background: #fff; }}
  @media (prefers-color-scheme: dark) {{ body {{ color:#e6e6e6; background:#1a1a1a; }}
     table, th, td {{ border-color:#444 !important; }} th {{ background:#2a2a2a !important; }}
     blockquote {{ background:#202830 !important; }} code {{ background:#2a2a2a !important; }} }}
  h1, h2, h3 {{ line-height: 1.25; margin-top: 1.8rem; }}
  h1 {{ border-bottom: 2px solid #d0d0d0; padding-bottom: .3rem; }}
  h2 {{ border-bottom: 1px solid #e0e0e0; padding-bottom: .2rem; }}
  img {{ max-width: 100%; height: auto; display: block; margin: 1rem auto;
        border: 1px solid #e0e0e0; border-radius: 6px; }}
  table {{ border-collapse: collapse; width: 100%; margin: 1rem 0; display:block; overflow-x:auto; }}
  th, td {{ border: 1px solid #ccc; padding: .5rem .7rem; text-align: left; vertical-align: top; }}
  th {{ background: #f2f4f7; }}
  blockquote {{ background: #f5f8fc; border-left: 4px solid #4a90d9; margin: 1rem 0;
               padding: .6rem 1rem; border-radius: 0 6px 6px 0; }}
  code {{ background: #f0f0f0; padding: .1rem .35rem; border-radius: 4px; font-size: 92%; }}
  .mermaid {{ background: #fff; border: 1px solid #e0e0e0; border-radius: 8px;
             padding: 1rem; margin: 1.2rem 0; text-align: center; }}
  em, i {{ color: inherit; }}
</style>
</head>
<body>
{body}
</body>
</html>"""

open(OUT, "w", encoding="utf-8").write(TEMPLATE.format(body=body, title=html.escape(TITLE)))
print("Wrote", OUT)
print("mermaid blocks:", len(mermaid_blocks), "| math spans:", len(math_blocks))
