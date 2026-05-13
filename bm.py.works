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

            # ✅ Add tick next to first field only
            tick_html = ""
            if first:
                tick_html = '<span class="status status-inline">⏳</span>'
                first = False

            fields_html += f"""
            <div class="field">
              <div class="label">{k}</div>
              <div class="value">
                {v} {tick_html}
              </div>
            </div>
            """

        # ✅ URL stored as tooltip ONLY
        cards_html += f"""
<a class="card" href="{url}" title="{url}" target="_blank" data-url="{url}">
  {fields_html}
</a>
"""

    html_template = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<link rel="icon" type="image/png" href="fav.svg">
<script src="https://cdn.jsdelivr.net/npm/xlsx/dist/xlsx.full.min.js"></script>
<title>Service Dashboard</title>

<style>
:root {
  --bg: #121212;
  --card: #1e1e1e;
  --text: #e0e0e0;
  --muted: #9e9e9e;
  --border: #2a2a2a;
  --ok: #3cb371;
  --fail: #e05555;
}

body {
  margin: 0;
  padding: 14px;
  font-family: Arial, Helvetica, Verdana, sans-serif;
  font-size: 13px;
  background: var(--bg);
  color: var(--text);
}

body.light {
  --bg: #f5f5f5;
  --card: #ffffff;
  --text: #222;
  --muted: #666;
  --border: #ddd;
}

.topbar {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 12px;
}

.search {
  flex: 1;
  max-width: 420px;
  padding: 8px 10px;
  border-radius: 6px;
  border: 1px solid var(--border);
  background: var(--card);
  color: var(--text);
}

.tools {
  display: flex;
  gap: 10px;
  cursor: pointer;
}

.container {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 12px;
}

/* ✅ Compact card */
.card {
  background: var(--card);
  border-radius: 10px;
  padding: 10px;
  text-decoration: none;
  color: var(--text);
  border: 1px solid var(--border);
  transition: transform 0.2s ease;
}

/* Hover glow */
@keyframes neonPulse {
  0%,100% { box-shadow: 0 0 10px rgba(0,255,200,0.15); }
  50% { box-shadow: 0 0 25px rgba(0,255,200,0.35); }
}

.card:hover {
  transform: translateY(-3px);
  animation: neonPulse 1.4s infinite;
}

.field { margin-bottom: 6px; }
.label { font-size: 10px; color: var(--muted); }
.value { font-weight: 600; }

/* ✅ GitHub style badge */
.status-inline {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 15px;
  height: 15px;
  margin-left: 6px;
  font-size: 10px;
  border-radius: 50%;
}

/* Tick animation */
@keyframes tickPop {
  0% { transform: scale(0.5); opacity: 0; }
  60% { transform: scale(1.2); opacity: 1; }
  100% { transform: scale(1); }
}

.ok {
  background: #2ea44f;
  color: #fff;
  animation: tickPop 0.3s ease-out;
}

.fail {
  background: #e5533d;
  color: #fff;
}

/* Footer minimal */
.footer {
  margin-top: 16px;
  text-align: center;
  font-size: 10px;
  color: var(--muted);
}

/* Auth */
#auth {
  position: fixed;
  inset: 0;
  background: #000c;
  display: flex;
  align-items: center;
  justify-content: center;
}

.auth-box {
  background: #1e1e1e;
  padding: 20px;
  border-radius: 8px;
  text-align: center;
}
</style>
</head>

<body>

<div id="auth">
  <div class="auth-box">
    Password<br>
    <input type="password" id="pwd">
  </div>
</div>

<div id="app" style="display:none;">

<div class="topbar">
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

<div class="footer">
  © Service Dashboard | Internal Use Only
</div>

</div>

<script>

const PASSWORD_HASH="__PASSWORD_HASH__";

async function sha256(t){
 const d=new TextEncoder().encode(t);
 const h=await crypto.subtle.digest("SHA-256",d);
 return Array.from(new Uint8Array(h)).map(b=>b.toString(16).padStart(2,"0")).join("");
}

document.getElementById("pwd").addEventListener("keyup",async e=>{
 if(e.key==="Enter"){
  const h=await sha256(e.target.value);
  if(h===PASSWORD_HASH){
   auth.style.display="none";
   app.style.display="block";
   checkStatuses();
   startInactivityTracking();
  }else alert("Wrong password");
 }
});

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
 document.querySelectorAll(".card").forEach(card=>{
  let s=card.querySelector(".status-inline");
  let url=card.dataset.url;

  fetch(url,{method:"HEAD",mode:"no-cors"})
   .then(()=>{s.textContent="✓";s.classList.add("ok");})
   .catch(()=>{s.textContent="✖";s.classList.add("fail");});
 });
}

/* Excel */
function exportToExcel(){
 let data=[],headers=new Set();

 document.querySelectorAll(".card").forEach(card=>{
  if(card.style.display==="none")return;

  let row={};
  card.querySelectorAll(".field").forEach(f=>{
    let k=f.querySelector(".label").innerText;
    let v=f.querySelector(".value").innerText;
    row[k]=v; headers.add(k);
  });

  row["URL"]=card.dataset.url;
  headers.add("URL");
  data.push(row);
 });

 headers=[...headers];
 let ws=XLSX.utils.aoa_to_sheet([
  headers,
  ...data.map(r=>headers.map(h=>r[h]||""))
 ]);

 let wb=XLSX.utils.book_new();
 XLSX.utils.book_append_sheet(wb,ws,"Dashboard");
 XLSX.writeFile(wb,"dashboard.xlsx");
}

/* Inactivity lock */
let t; const LIMIT=300000;

function resetTimer(){
 clearTimeout(t);
 t=setTimeout(()=>{
  app.style.display="none";
  auth.style.display="flex";
  pwd.value="";
 },LIMIT);
}

["mousemove","keydown","click","scroll"]
.forEach(e=>document.addEventListener(e,resetTimer));

function startInactivityTracking(){resetTimer();}
</script>

</body>
</html>
"""

    html_final = (
        html_template
        .replace("__CARDS__", cards_html)
        .replace("__PASSWORD_HASH__", password_hash)
    )

    with open(html_file, "w", encoding="utf-8") as f:
        f.write(html_final)

    print("✅ index.html generated successfully")


md_to_cards("bm.md", "index.html")