import os
import hashlib
import markdown
from bs4 import BeautifulSoup

def md_to_cards(md_file, html_file):
    password = os.environ.get("DASH_PASSWORD")
    if not password:
        raise RuntimeError("DASH_PASSWORD environment variable not set")

    password_hash = hashlib.sha256(password.encode("utf-8")).hexdigest()

    with open(md_file, "r", encoding="utf-8") as f:
        md_content = f.read()

    html_table = markdown.markdown(md_content, extensions=["tables"])
    soup = BeautifulSoup(html_table, "html.parser")

    headers = [th.get_text(strip=True) for th in soup.select("thead th")]
    rows = soup.select("tbody tr")

    cards_html = ""

    for row in rows:
        values = [td.get_text(strip=True) for td in row.select("td")]
        data = dict(zip(headers, values))
        url = data.get("URL", "").strip()

        if not url:
            continue

        fields_html = ""
        first = True

        for k, v in data.items():
            if k.lower() == "url":
                continue

            tick_html = ""
            if first:
                tick_html = '<span class="status status-inline">⏳</span>'
                first = False

            fields_html += f"""
            <div class="field">
              <div class="label">{k}</div>
              <div class="value">{v} {tick_html}</div>
            </div>
            """

        cards_html += f"""
<a class="card" href="{url}" target="_blank" data-url="{url}" title="{url}">
  {fields_html}
</a>
"""

    html_template = """<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<link rel="icon" href="fav.svg">
<script src="https://cdn.jsdelivr.net/npm/xlsx/dist/xlsx.full.min.js"></script>
<title>Service Dashboard</title>

<style>
:root {
  --bg:#121212;
  --card:#1e1e1e;
  --text:#e0e0e0;
  --muted:#9e9e9e;
  --border:#2a2a2a;
}

body {
  margin:0;
  font-family:Arial, Helvetica, sans-serif;
  font-size:12px;
  background:var(--bg);
  color:var(--text);
}

body.light {
  --bg:#f5f5f5;
  --card:#ffffff;
  --text:#222;
  --muted:#666;
  --border:#ddd;
}

/* Layout */
.layout { display:flex; }

/* ✅ Sidebar fixed */
.sidebar {
  width:0;
  overflow:hidden;
  transition:0.3s ease;
  background:var(--card);
  border-right:1px solid var(--border);
}

.sidebar.active {
  width:180px;
  padding:10px;
}

.sidebar a {
  display:block;
  padding:6px 4px;
  margin:6px 0;
  text-decoration:none;
  color:var(--text);
  border-radius:6px;
}

.sidebar a:hover {
  background:rgba(0,255,200,0.08);
}

/* Main */
.main {
  flex:1;
  padding:12px;
}

/* Topbar */
.topbar {
  display:flex;
  gap:6px;
  margin-bottom:10px;
  flex-wrap:wrap;
  align-items:center;
}

.menu {
  cursor:pointer;
  font-size:16px;
}

/* Search */
.search {
  flex:1;
  min-width:150px;
  padding:6px;
  background:var(--card);
  border:1px solid var(--border);
  color:var(--text);
}

/* Buttons */
.tools span {
  cursor:pointer;
  margin-left:6px;
}

/* ✅ AI CARDS RESTORED */
.container {
  display:grid;
  grid-template-columns:repeat(auto-fit,minmax(200px,1fr));
  gap:12px;
}

.card {
  background:var(--card);
  border-radius:12px;
  padding:10px;
  text-decoration:none;
  color:var(--text);
  border:1px solid var(--border);

  transition:all 0.2s ease;
}

/* 🔥 AI glow */
.card:hover {
  transform:translateY(-4px) scale(1.02);
  box-shadow:
    0 10px 25px rgba(0,0,0,0.6),
    0 0 20px rgba(0,255,200,0.25);
  border-color:rgba(0,255,200,0.4);
}

/* Fields */
.field { margin-bottom:4px; }
.label { font-size:9px; color:var(--muted); }
.value { font-weight:600; }

/* Status */
.status-inline {
  margin-left:6px;
  width:14px;
  height:14px;
  display:inline-flex;
  align-items:center;
  justify-content:center;
  border-radius:50%;
}

/* Tick */
.ok { background:#2ea44f; color:white; }
.fail { background:#e5533d; color:white; }
</style>
</head>

<body>

<div id="auth">
<div>
Password<br>
<input type="password" id="pwd">
</div>
</div>

<div id="app" style="display:none;">

<div class="layout">

<!-- ✅ WORKING SIDEBAR -->
<div class="sidebar" id="sidebar">
  <a href="#">🏠 Home</a>
  <a href="#">📊 Dashboard</a>
  <a href="#">⚙ Settings</a>
  <a href="#">📁 Projects</a>
</div>

<div class="main">

<div class="topbar">
  <span class="menu" onclick="toggleMenu()">☰</span>
  <input class="search" id="searchBox" placeholder="Search...">

  <div class="tools">
    <span id="themeToggle">🌙</span>
    <span onclick="window.print()">🖨</span>
    <span onclick="exportToExcel()">📊</span>
  </div>
</div>

<div class="container">
__CARDS__
</div>

<div style="text-align:center;font-size:9px;color:gray;margin-top:10px;">
© Service Dashboard
</div>

</div>
</div>
</div>

<script>

/* ✅ Sidebar toggle (fixed) */
function toggleMenu(){
 document.getElementById("sidebar").classList.toggle("active");
}

/* ✅ Theme fix */
const themeBtn = document.getElementById("themeToggle");
themeBtn.onclick = () => {
 document.body.classList.toggle("light");
 themeBtn.textContent =
  document.body.classList.contains("light") ? "☀️" : "🌙";
};

/* AUTH */
pwd.onkeyup=async e=>{
 if(e.key==="Enter"){
  let d=new TextEncoder().encode(pwd.value);
  let h=await crypto.subtle.digest("SHA-256",d);
  let hex=[...new Uint8Array(h)].map(b=>b.toString(16).padStart(2,"0")).join("");
  if(hex==="__PASSWORD_HASH__"){
    auth.style.display="none";
    app.style.display="block";
    checkStatuses();
  } else alert("Wrong password");
 }
};

/* Search */
searchBox.onkeyup=e=>{
 let q=e.target.value.toLowerCase();
 document.querySelectorAll(".card").forEach(c=>{
  c.style.display=c.innerText.toLowerCase().includes(q)?"":"none";
 });
};

/* ✅ Status */
function checkStatuses(){
 document.querySelectorAll(".card").forEach(c=>{
  let s=c.querySelector(".status-inline");
  fetch(c.dataset.url,{method:"HEAD",mode:"no-cors"})
   .then(()=>{s.textContent="✓";s.classList.add("ok")})
   .catch(()=>{s.textContent="✖";s.classList.add("fail")});
 });
}

/* Excel export unchanged */
function exportToExcel(){
 let d=[],h=new Set();
 document.querySelectorAll(".card").forEach(c=>{
  if(c.style.display==="none")return;
  let r={};
  c.querySelectorAll(".field").forEach(f=>{
   let k=f.querySelector(".label").innerText;
   let v=f.querySelector(".value").innerText;
   r[k]=v; h.add(k);
  });
  r["URL"]=c.dataset.url;
  h.add("URL");
  d.push(r);
 });

 h=[...h];
 let ws=XLSX.utils.aoa_to_sheet([
  h,...d.map(r=>h.map(x=>r[x]||""))
 ]);
 let wb=XLSX.utils.book_new();
 XLSX.utils.book_append_sheet(wb,ws,"Dashboard");
 XLSX.writeFile(wb,"dashboard.xlsx");
}
</script>

</body>
</html>
"""

    html_final = html_template.replace("__CARDS__", cards_html).replace("__PASSWORD_HASH__", password_hash)

    with open(html_file, "w", encoding="utf-8") as f:
        f.write(html_final)

    print("✅ Done")


md_to_cards("bm.md", "index.html")
