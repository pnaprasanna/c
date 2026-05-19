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
<a class="card" href="{url}" target="_blank" data-url="{url}">
  {fields_html}
</a>
"""

    html_template = """<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
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
  font-family: Arial, Helvetica, sans-serif;
  font-size:12px;
  background:var(--bg);
  color:var(--text);
}

/* ✅ Layout */
.layout {
  display:flex;
}

/* ✅ Sidebar */
.sidebar {
  width:0;
  overflow:hidden;
  transition:0.3s;
  background:var(--card);
  border-right:1px solid var(--border);
}

.sidebar.active {
  width:180px;
  padding:10px;
}

.sidebar a {
  display:block;
  margin:10px 0;
  color:var(--text);
  text-decoration:none;
}

/* ✅ Main */
.main {
  flex:1;
  padding:12px;
}

/* ✅ Topbar */
.topbar {
  display:flex;
  align-items:center;
  gap:6px;
  margin-bottom:10px;
  flex-wrap:wrap; /* ✅ responsive */
}

.menu {
  cursor:pointer;
  font-size:16px;
}

.search {
  flex:1;
  padding:6px;
  min-width:150px;
  background:var(--card);
  border:1px solid var(--border);
  color:var(--text);
}

.tools {
  display:flex;
  gap:6px;
}

.tools span {
  cursor:pointer;
}

/* ✅ Cards */
.container {
  display:grid;
  grid-template-columns:repeat(auto-fit,minmax(200px,1fr));
  gap:10px;
}

.card {
  background:var(--card);
  border-radius:10px;
  padding:10px;
  text-decoration:none;
  color:var(--text);
  border:1px solid var(--border);
  transition:0.2s;
}

/* ✅ AI effect */
.card:hover {
  transform:translateY(-4px);
  box-shadow:
    0 6px 20px rgba(0,0,0,0.6),
    0 0 12px rgba(0,255,200,0.25);
}

/* Fields */
.field { margin-bottom:4px; }
.label { font-size:9px; color:var(--muted); }
.value { font-weight:600; }

/* ✅ status */
.status-inline {
  width:16px;
  height:16px;
  display:inline-flex;
  align-items:center;
  justify-content:center;
  border-radius:50%;
  margin-left:6px;
  font-size:10px;
}

@keyframes tickPop {
  0% {transform:scale(.5);opacity:0}
  60% {transform:scale(1.2);opacity:1}
  100% {transform:scale(1)}
}

.ok {
  background:#2ea44f;
  color:white;
  animation:tickPop 0.3s ease-out;
}

.fail {
  background:#e5533d;
  color:white;
}

/* ✅ Mobile responsiveness */
@media (max-width: 768px) {
  .sidebar.active {
    width:140px;
  }

  .topbar {
    flex-direction:row;
    flex-wrap:wrap;
  }

  .container {
    grid-template-columns:1fr;
  }
}

/* ✅ Auth */
#auth {
  position:fixed;
  inset:0;
  background:#000c;
  display:flex;
  align-items:center;
  justify-content:center;
}
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

<div class="sidebar" id="sidebar">
  <a href="#">🏠 Home</a>
  <a href="#">📊 Dashboard</a>
  <a href="#">⚙ Settings</a>
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

/* Menu */
function toggleMenu(){
 document.getElementById("sidebar").classList.toggle("active");
}

/* Auth */
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

/* Theme */
themeToggle.onclick=()=>document.body.classList.toggle("light");

/* Search */
searchBox.onkeyup=e=>{
 let q=e.target.value.toLowerCase();
 document.querySelectorAll(".card").forEach(c=>{
  c.style.display=c.innerText.toLowerCase().includes(q)?"":"none";
 });
};

/* Status */
function checkStatuses(){
 document.querySelectorAll(".card").forEach(c=>{
  let s=c.querySelector(".status-inline");
  fetch(c.dataset.url,{method:"HEAD",mode:"no-cors"})
   .then(()=>{s.textContent="✓";s.classList.add("ok")})
   .catch(()=>{s.textContent="✖";s.classList.add("fail")});
 });
}

/* Excel */
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
