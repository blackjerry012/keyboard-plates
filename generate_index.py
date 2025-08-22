import os, re, urllib.parse
from collections import defaultdict

# === 路徑設定：改成你的本機 repo 位置 ===
SITE_FOLDER = r"C:\Users\USER\Desktop\mydcbot\keyboard-plates"
# 如果檔案放在子資料夾，填資料夾名；否則留空字串
SUBDIR = ""  # 例: "keyboard-plates-site" 或 "files"

folder = os.path.join(SITE_FOLDER, SUBDIR) if SUBDIR else SITE_FOLDER

# === 可調的規則區 ===
# 強制用「兩個 token」當系列名的前綴（遇到像 Singa-Unikorn、Gok-Venn 這種）
FORCE_TWO = {"singa", "gok", "tgr"}  # 需要可以自行加：{"singa","gok","tgr","keycult",...}

# 別名表：把不同寫法併入同一組（key 用小寫）
ALIAS = {
    "unikorn": "Singa-Unikorn",
    "singa-unikorn": "Singa-Unikorn",
    "neo65": "NEO65",
    "neo60": "NEO60",
    "rio65": "RIO65",
    "kbd8xiii": "KBD8XIII",
    "tgr": "TGR",
    "gok-venn": "Gok-Venn",
}

# 不當作系列後綴關鍵字（遇到第二個 token 是這些，就不要湊兩個 token）
STOP2 = {"plate", "full", "half", "alu", "fr4", "pc", "pom", "pcpom", "wk", "wkl",
         "universal", "hotswap", "bikini", "比基尼"}


def list_files():
    return sorted([f for f in os.listdir(folder)
                   if f.lower().endswith((".dwg", ".dxf"))],
                  key=lambda s: s.lower())


def token_split(name_no_ext):
    # 以 - _ 空白 分詞；連續分隔符視為一個
    toks = re.split(r"[\s\-_]+", name_no_ext.strip())
    return [t for t in toks if t]


def series_key(fname):
    base = os.path.splitext(fname)[0]  # 去副檔名
    toks = token_split(base)

    if not toks:
        key = base
    else:
        t0 = toks[0]
        # 預設先用第一個 token
        key = t0

        # 若第一個 token 在 FORCE_TWO、且有第二個 token、且第二個不在 STOP2，湊成「兩個 token」
        if len(toks) >= 2:
            t1 = toks[1]
            if t0.lower() in FORCE_TWO and t1.lower() not in STOP2:
                key = f"{t0}-{t1}"

        # 針對像「Unikorn全鋼...」這種沒有分隔符，但前綴明顯的情況
        low = base.lower()
        for k, v in ALIAS.items():
            if low.startswith(k):
                return v

    # 一般情況跑到這裡：再做一次 alias 對齊（大小寫/不同寫法）
    low_key = key.lower()
    if low_key in ALIAS:
        return ALIAS[low_key]

    # 標準化顯示（把底線轉 -，首字母大寫但保留數字）
    pretty = key.replace("_", "-")
    return pretty


def href_for(fname):
    # 正確處理中文/空白/括號
    prefix = (SUBDIR + "/") if SUBDIR else ""
    return prefix + urllib.parse.quote(fname)


files = list_files()
groups = defaultdict(list)
for f in files:
    groups[series_key(f)].append(f)

# 排序群組名稱
group_names = sorted(groups.keys(), key=lambda s: s.lower())

# 產生 HTML
def li_links(file_list):
    lines = []
    for f in sorted(file_list, key=lambda s: s.lower()):
        lines.append(f'      <li><a href="{href_for(f)}" download>{f}</a></li>')
    return "\n".join(lines)

sections = []
for g in group_names:
    files_html = li_links(groups[g])
    count = len(groups[g])
    sections.append(f"""
  <details class="group" open>
    <summary><strong>{g}</strong> <span class="count">({count})</span></summary>
    <ul>
{files_html}
    </ul>
  </details>
""")

html = f"""<!DOCTYPE html>
<html lang="zh">
<head>
  <meta charset="UTF-8" />
  <title>鍵盤定位板下載區</title>
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <style>
    body {{ font-family: "Microsoft JhengHei", Arial, sans-serif; background:#f5f5f5; margin:0; }}
    header {{ padding:28px 20px 12px; text-align:center; }}
    h1 {{ margin:0 0 8px; color:#222; }}
    .hint {{ color:#666; }}
    .wrap {{ max-width:960px; margin:16px auto 40px; padding:0 16px; }}
    .toolbar {{ display:flex; gap:8px; justify-content:center; margin:10px auto 18px; flex-wrap:wrap; }}
    input[type="search"] {{ width:360px; max-width:90%; padding:10px 12px; border-radius:10px; border:1px solid #ddd; }}
    button {{ padding:8px 12px; border-radius:8px; border:1px solid #ccc; background:#fff; cursor:pointer; }}
    button:hover {{ background:#f0f0f0; }}
    .group {{ background:#fff; border-radius:12px; padding:12px 16px; margin:10px 0; box-shadow:0 2px 10px rgba(0,0,0,.05); }}
    summary {{ cursor:pointer; font-size:18px; outline:none; }}
    ul {{ list-style:none; padding-left:0; margin:10px 0 0; }}
    li {{ margin:6px 0; }}
    a {{ display:block; padding:10px 12px; border-radius:8px; background:#007acc; color:#fff; text-decoration:none; }}
    a:hover {{ background:#005fa3; }}
    .muted {{ color:#888; font-size:12px; text-align:center; margin-top:6px; }}
  </style>
</head>
<body>
  <header>
    <h1>鍵盤定位板下載區</h1>
    <div class="hint">以下提供 DXF / DWG 檔案下載；可用關鍵字快速過濾。</div>
    <div class="toolbar">
      <input id="q" type="search" placeholder="搜尋型號 / 關鍵字…（例：Unikorn, ARC60, 910, WK）" oninput="filterList()">
      <button onclick="expandAll(true)">展開全部</button>
      <button onclick="expandAll(false)">收合全部</button>
    </div>
  </header>

  <div class="wrap" id="wrap">
{''.join(sections)}
    <div class="muted">共 {len(files)} 個檔案，分為 {len(group_names)} 個系列。</div>
  </div>

<script>
function filterList() {{
  const q = document.getElementById('q').value.trim().toLowerCase();
  const groups = document.querySelectorAll('.group');
  groups.forEach(g => {{
    const text = g.innerText.toLowerCase();
    const matched = text.includes(q);
    g.style.display = matched ? '' : 'none';
    if (matched && q) g.open = true;
  }});
}}

function expandAll(open) {{
  document.querySelectorAll('.group').forEach(g => g.open = open);
}}
</script>
</body>
</html>
"""

with open(os.path.join(SITE_FOLDER, "index.html"), "w", encoding="utf-8") as f:
    f.write(html)

print("✅ 已生成 index.html（含系列分組 / 搜尋 / 展開功能）")
