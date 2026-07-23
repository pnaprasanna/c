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

            status_html = ""
            if first:
                status_html = '<span class="status status-inline"></span>'
                first = False

            fields_html += f"""
            <div class="field">
              <div class="label">{k}</div>
              <div class="value">
                {v} {status_html}
              </div>
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
<link rel="icon" type="image/png" href="fav.svg">
<script src="https://cdn.jsdelivr.net/npm/xlsx/dist/xlsx.full.min.js"></script>

<title>Service Dashboard</title>

<style>
:root {
  --bg:#0d1117;
  --card:#161b22;
  --text:#e6edf3;
  --muted:#9da7b3;
  --border:#30363d;
  --accent:#00ffc8;
}

body {
  margin:0;
  font-family:Arial, Helvetica, sans-serif;
  font-size:12px;
  background:var(--bg);
  color:var(--text);
}

/* ✅ cursor */
.card, .menu, .sidebar a, .tools span {
  cursor:pointer;
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

/* Sidebar */
.sidebar {
  width:0;
  overflow:hidden;
  transition:width 0.25s ease;
  background:var(--card);
  border-right:1px solid var(--border);
}

.sidebar.active {
  width:180px;
  padding:10px;
}

.sidebar a {
  display:block;
  padding:6px;
  margin:6px 0;
  text-decoration:none;
  color:var(--text);
}

.sidebar a:hover {
  background:rgba(0,255,200,0.1);
}

/* Main */
.main { flex:1; padding:12px; }

/* Topbar */
.topbar {
  display:flex;
  gap:6px;
  margin-bottom:10px;
  align-items:center;
}

.menu { cursor:pointer; }

.search {
  flex:1;
  padding:6px;
  background:var(--card);
  border:1px solid var(--border);
  color:var(--text);
}

/* Cards */
.container {
  display:grid;
  grid-template-columns:repeat(auto-fit,minmax(220px,1fr));
  gap:12px;
}

.card {
  background:var(--card);
  border:1px solid var(--border);
  border-radius:12px;
  padding:12px;
  text-decoration:none;
  color:var(--text);
  transition:0.2s;
}

.card:hover {
  transform:translateY(-3px);
  border-color:var(--accent);
  box-shadow:0 6px 20px rgba(0,255,200,0.15);
}

.field { margin-bottom:6px; }
.label { font-size:9px; color:var(--muted); }
.value { font-weight:600; }

/* Status */
.status-inline {
  width:14px;
  height:14px;
  margin-left:6px;
  border-radius:50%;
  border:2px solid #333;
  border-top:2px solid var(--accent);
  display:inline-flex;
  align-items:center;
  justify-content:center;
  animation:spin 0.8s linear infinite;
}

@keyframes spin {
  100% { transform:rotate(360deg); }
}

.ok {
  animation:none;
  background:#2ea44f;
  color:white;
}

.fail {
  animation:none;
  background:#f85149;
  color:white;
}

/* Auth */
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
  <a href="notes/contents.html">📊 Notes</a>
  <a href="#">⚙ Settings</a>
  <a href="#">📁 Projects</a>
</div>

<div class="main">

<div class="topbar">
  <span class="menu" onclick="toggleMenu()">☰</span>
  <input class="search" id="searchBox" placeholder="Search...">

  <span id="themeToggle">🌙</span>
  <span onclick="window.print()">🖨</span>
  <span onclick="exportToExcel()">📊</span>
</div>

<div class="container">
__CARDS__
</div>

</div>
</div>
</div>

<script>

/* Sidebar */
function toggleMenu(){
 document.getElementById("sidebar").classList.toggle("active");
}

/* Theme */
themeToggle.onclick=()=>{
 document.body.classList.toggle("light");
 themeToggle.textContent =
 document.body.classList.contains("light") ? "☀️" : "🌙";
};

/* ✅ Auth */
pwd.onkeyup=async e=>{
 if(e.key==="Enter"){
  let d=new TextEncoder().encode(pwd.value);
  let h=await crypto.subtle.digest("SHA-256",d);
  let hex=[...new Uint8Array(h)].map(b=>b.toString(16).padStart(2,"0")).join("");
  if(hex==="__PASSWORD_HASH__"){
    auth.style.display="none";
    app.style.display="block";
    checkStatuses();
    startTimer();  /* ✅ start inactivity */
  } else alert("Wrong password");
 }
};

/* ✅ 5 MIN INACTIVITY LOGOUT */
let timer;
function resetTimer(){
 clearTimeout(timer);
 timer=setTimeout(()=>{
   document.getElementById("app").style.display="none";
   document.getElementById("auth").style.display="flex";
   document.getElementById("pwd").value="";
 },300000); // 5 mins
}

["mousemove","keydown","scroll","click"].forEach(evt=>{
 document.addEventListener(evt, resetTimer);
});

function startTimer(){
 resetTimer();
}

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
   .then(()=>{
     s.textContent="✓";
     s.classList.add("ok");
   })
   .catch(()=>{
     s.textContent="✖";
     s.classList.add("fail");
   });
 });
}

/* Excel unchanged */
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

    html_final = html_template.replace("__CARDS__", cards_html)\
                              .replace("__PASSWORD_HASH__", password_hash)

    with open(html_file, "w", encoding="utf-8") as f:
        f.write(html_final)

    print("✅ Logout + cursor enhancements added")

md_to_cards("bm.md", "index.html")
