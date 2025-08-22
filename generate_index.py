import os, re
from collections import defaultdict
from urllib.parse import quote

# === 路徑設定 ===
SITE_FOLDER    = r"C:\Users\USER\Desktop\mydcbot\keyboard-plates"  # ← 改成你的路徑
SUBDIR_PLATES  = "定位板"     # .dwg/.dxf 的子資料夾
SUBDIR_JSON    = "via檔案"    # .json 的子資料夾

PLATES_FOLDER = os.path.join(SITE_FOLDER, SUBDIR_PLATES)
JSON_FOLDER   = os.path.join(SITE_FOLDER, SUBDIR_JSON)

# === 分組規則（可自行擴充） ===
FORCE_TWO = {"singa", "gok", "tgr"}
STOP2 = {"plate","full","half","alu","fr4","pc","pom","pcpom","wk","wkl","universal","hotswap","bikini","比基尼"}
ALIAS = {
    "unikorn": "Singa-Unikorn",
    "singa-unikorn": "Singa-Unikorn",
    "neo65": "NEO65",
    "neo60": "NEO60",
    "rio65": "RIO65",
    "kbd8xiii": "KBD8XIII",
    "gok-venn": "Gok-Venn",
    "tgr": "TGR",
}

def token_split(s): return [t for t in re.split(r"[\s\-_]+", s.strip()) if t]

def series_key(fname):
    base = os.path.splitext(fname)[0]
    toks = token_split(base)
    if not toks:
        key = base
    else:
        t0 = toks[0]; key = t0
        if len(toks) >= 2:
            t1 = toks[1]
            if t0.lower() in FORCE_TWO and t1.lower() not in STOP2:
                key = f"{t0}-{t1}"
        low = base.lower()
        for k, v in ALIAS.items():
            if low.startswith(k): return v
    low_key = key.lower()
    if low_key in ALIAS: return ALIAS[low_key]
    return key.replace("_","-")

def list_files(folder, exts):
    if not os.path.isdir(folder): return []
    return sorted([f for f in os.listdir(folder) if f.lower().endswith(exts)], key=str.lower)

def href_for(subdir, fname):
    # 子資料夾與檔名都要各自做 URL 編碼（中文/空白 OK）
    return f"{quote(subdir)}/{quote(fname)}" if subdir else quote(fname)

def build_groups(files): 
    g = defaultdict(list)
    for f in files: g[series_key(f)].append(f)
    return g

plate_files = list_files(PLATES_FOLDER, (".dwg",".dxf"))
json_files  = list_files(JSON_FOLDER,   (".json",))

groups_plate = build_groups(plate_files)
groups_json  = build_groups(json_files)

def li_links(file_list, subdir):
    return "\n".join(
        f'      <li><a href="{href_for(subdir, f)}" download>{f}</a></li>'
        for f in sorted(file_list, key=str.lower)
    )

def build_sections(groups, subdir):
    parts = []
    for name in sorted(groups.keys(), key=str.lower):
        parts.append(f"""
  <details class="group" open>
    <summary><strong>{name}</strong> <span class="count">({len(groups[name])})</span></summary>
    <ul>
{li_links(groups[name], subdir)}
    </ul>
  </details>""")
    return "".join(parts) if parts else '<div class="muted">目前沒有檔案。</div>'

sections_plate = build_sections(groups_plate, SUBDIR_PLATES)
sections_json  = build_sections(groups_json,  SUBDIR_JSON)

html = f"""<!DOCTYPE html>
<html lang="zh">
<head>
<meta charset="UTF-8" />
<title>鍵盤定位板 & VIA JSON 下載</title>
<meta name="viewport" content="width=device-width, initial-scale=1" />
<style>
:root {{ --bg:#f5f5f5; --fg:#222; --card:#fff; --muted:#666; --btn:#007acc; --btnh:#005fa3; --bd:#ddd; }}
*{{box-sizing:border-box}} body{{margin:0;font-family:"Microsoft JhengHei",Arial,sans-serif;background:var(--bg);color:var(--fg)}}
header{{padding:28px 20px 12px;text-align:center}} h1{{margin:0 0 8px}} .hint{{color:var(--muted)}}
.wrap{{max-width:960px;margin:16px auto 40px;padding:0 16px}}
.tabs{{display:flex;justify-content:center;gap:8px;margin:12px 0 6px;flex-wrap:wrap}}
.tab-btn{{padding:10px 14px;border-radius:10px;border:1px solid var(--bd);background:#fff;cursor:pointer;min-width:120px}}
.tab-btn.active{{background:var(--btn);color:#fff;border-color:var(--btn)}}
.toolbar{{display:flex;gap:8px;justify-content:center;margin:10px auto 18px;flex-wrap:wrap}}
input[type="search"]{{width:360px;max-width:90%;padding:10px 12px;border-radius:10px;border:1px solid var(--bd)}}
button.ctrl{{padding:8px 12px;border-radius:8px;border:1px solid var(--bd);background:#fff;cursor:pointer}}
button.ctrl:hover{{background:#f0f0f0}}
.panel{{display:none}} .panel.active{{display:block}}
.group{{background:var(--card);border-radius:12px;padding:12px 16px;margin:10px 0;box-shadow:0 2px 10px rgba(0,0,0,.05)}}
summary{{cursor:pointer;font-size:18px;outline:none}} ul{{list-style:none;padding-left:0;margin:10px 0 0}} li{{margin:6px 0}}
a{{display:block;padding:10px 12px;border-radius:8px;background:var(--btn);color:#fff;text-decoration:none}} a:hover{{background:var(--btnh)}}
.muted{{color:#888;font-size:12px;text-align:center;margin-top:6px}}
</style>
</head>
<body>
<header>
  <h1>鍵盤定位板 & VIA JSON 下載</h1>
  <div class="hint">切換上方分頁；各自支援搜尋 / 展開 / 收合。連結已做 URL 編碼，中文/空白檔名可正常下載。</div>
  <div class="tabs">
    <button id="tab-plates-btn" class="tab-btn active" onclick="showTab('plates')">定位板（{len(plate_files)}）</button>
    <button id="tab-json-btn"   class="tab-btn"        onclick="showTab('json')">VIA JSON（{len(json_files)}）</button>
  </div>
</header>

<div class="wrap">
  <div id="panel-plates" class="panel active">
    <div class="toolbar">
      <input id="q-plates" type="search" placeholder="搜尋定位板…（例：Unikorn, ARC60, 910, WK）" oninput="filterList('panel-plates','q-plates')">
      <button class="ctrl" onclick="expandAll('panel-plates',true)">展開全部</button>
      <button class="ctrl" onclick="expandAll('panel-plates',false)">收合全部</button>
    </div>
{sections_plate}
    <div class="muted">定位板總數：{len(plate_files)}，系列：{len(groups_plate)}</div>
  </div>

  <div id="panel-json" class="panel">
    <div class="toolbar">
      <input id="q-json" type="search" placeholder="搜尋 VIA JSON…（例：Unikorn, 65, ANSI）" oninput="filterList('panel-json','q-json')">
      <button class="ctrl" onclick="expandAll('panel-json',true)">展開全部</button>
      <button class="ctrl" onclick="expandAll('panel-json',false)">收合全部</button>
    </div>
{sections_json}
    <div class="muted">JSON 總數：{len(json_files)}，系列：{len(groups_json)}</div>
  </div>
</div>

<script>
function showTab(which) {{
  const isPlates = (which === 'plates');
  document.getElementById('panel-plates').classList.toggle('active', isPlates);
  document.getElementById('panel-json').classList.toggle('active', !isPlates);
  document.getElementById('tab-plates-btn').classList.toggle('active', isPlates);
  document.getElementById('tab-json-btn').classList.toggle('active', !isPlates);
}}
function filterList(panelId, inputId) {{
  const q = document.getElementById(inputId).value.trim().toLowerCase();
  const panel = document.getElementById(panelId);
  panel.querySelectorAll('.group').forEach(g => {{
    const text = g.innerText.toLowerCase();
    const matched = text.includes(q);
    g.style.display = matched ? '' : 'none';
    if (matched && q) g.open = true;
  }});
}}
function expandAll(panelId, open) {{
  document.getElementById(panelId).querySelectorAll('.group').forEach(g => g.open = open);
}}
</script>
</body>
</html>
"""

with open(os.path.join(SITE_FOLDER, "index.html"), "w", encoding="utf-8") as f:
    f.write(html)

print("✅ 已生成 index.html（子資料夾版：定位板 & VIA JSON 分頁）")
