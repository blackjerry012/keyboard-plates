import os, urllib.parse

# ← 改成你的本機 repo 路徑（就是這個資料夾）
SITE_FOLDER = r"C:\Users\USER\Desktop\mydcbot\keyboard-plates"

# 我們現在把檔案放在根目錄 → 留空字串
SUBDIR = ""

folder = os.path.join(SITE_FOLDER, SUBDIR) if SUBDIR else SITE_FOLDER

def list_files(exts):
    return sorted([f for f in os.listdir(folder) if f.lower().endswith(exts)])

def make_links(files):
    lines = []
    prefix = (SUBDIR + "/") if SUBDIR else ""
    for f in files:
        safe = urllib.parse.quote(f)  # 這行會把中文/空白/括號做 URL encode
        lines.append(f'    <li><a href="{prefix}{safe}" download>{f}</a></li>')
    return "\n".join(lines)

dwg = list_files(('.dwg',))
dxf = list_files(('.dxf',))

html = f"""<!DOCTYPE html>
<html lang="zh">
<head>
  <meta charset="UTF-8">
  <title>鍵盤定位板下載區</title>
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <style>
    body {{ font-family: "Microsoft JhengHei", sans-serif; background:#f5f5f5; padding:40px; }}
    h1 {{ color:#222; text-align:center; }}
    .section {{ max-width:820px; margin:24px auto; background:#fff; border-radius:12px; padding:20px 24px; box-shadow:0 2px 10px rgba(0,0,0,.05); }}
    h2 {{ margin:0 0 12px; color:#333; }}
    ul {{ list-style:none; padding:0; margin:0; }}
    li {{ margin:8px 0; }}
    a {{ display:block; padding:10px 12px; border-radius:8px; background:#007acc; color:#fff; text-decoration:none; }}
    a:hover {{ background:#005fa3; }}
    footer {{ margin-top:24px; text-align:center; color:#888; font-size:13px; }}
  </style>
</head>
<body>
  <h1>鍵盤定位板下載區</h1>

  <div class="section">
    <h2>DXF</h2>
    <ul>
{make_links(dxf)}
    </ul>
  </div>

  <div class="section">
    <h2>DWG</h2>
    <ul>
{make_links(dwg)}
    </ul>
  </div>

  <footer>© 2025 我的鍵盤定位板分享網站</footer>
</body>
</html>
"""

with open(os.path.join(SITE_FOLDER, "index.html"), "w", encoding="utf-8") as f:
    f.write(html)

print("✅ 已生成 index.html")
