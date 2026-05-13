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
            copy_html = ""

            if first:
                tick_html = '<span class="status status-inline">⏳</span>'

                copy_html = f'''
                <span class="copy-btn" title="COPY" onclick="copyUrl(event,'{url}', this)">
                  <svg viewBox="0 0 24 24">
                    <rect x="9" y="9" width="10" height="10" rx="2" fill="currentColor"></rect>
                    <rect x="5" y="5" width="10" height="10" rx="2"
                      fill="none" stroke="currentColor" stroke-width="2"></rect>
                  </svg>
                </span>
                '''
                first = False

            fields_html += f"""
            <div class="field">
              <div class="label">{k}</div>
              <div class="value">
                {v} {tick_html} {copy_html}
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
  --bg:#121212;
  --card:#1e1e1e;
  --text:#e0e0e0;
  --muted:#9e9e9e;
  --border:#2a2a2a;
  --ok:#3cb371;
  --fail:#e05555;
}

body {
  margin:0;
  padding:12px;
  font-family: Arial, Helvetica, sans-serif; /* ✅ web safe */
  font-size:12px; /* ✅ smaller */
  background:var(--bg);
  color:var(--text);
}

body.light {
  --bg:#f5f5f5;
  --card:#fff;
  --text:#222;
  --muted:#666;
  --border:#ddd;
}

.topbar { display:flex; gap:8px; margin-bottom:10px; }

.search {
  flex:1;
  padding:6px;
  background:var(--card);
  border:1px solid var(--border);
  color:var(--text);
}

.tools { display:flex; gap:8px; }

.container {
  display:grid;
  grid-template-columns:repeat(auto-fit,minmax(220px,1fr));
  gap:10px;
}

/* Cards */
.card {
  background:var(--card);
  border:1px solid var(--border);
  border-radius:8px;
  padding:8px;
  text-decoration:none;
  color:var(--text);
}

/* Compact */
.field { margin-bottom:4px; }
.label { font-size:9px; color:var(--muted); }
.value { font-weight:600; }

/* Tick + Copy */
.status-inline,
.copy-btn {
  width:16px;
  height:16px;
  display:inline-flex;
  align-items:center;
  justify-content:center;
  border-radius:50%;
  margin-left:6px;
}

/* ✅ Copy icon */
.copy-btn {
  color:#888;
  opacity:0;
  transition:all .2s;
  cursor:pointer;
}
.copy-btn svg {
  width:14px; /* ✅ bigger */
  height:14px;
}

.card:hover .copy-btn { opacity:1; }

.copy-btn:hover {
  color:#fff;
  transform:scale(1.15);
}

/* ✅ Morph animation */
.copy-btn.copied svg {
  display:none;
}

.copy-btn.copied::after {
  content:"✓";
  color:#2ea44f;
  font-size:12px;
  animation:pulse .4s ease;
}

/* ✅ pulse */
@keyframes pulse {
  0% { transform:scale(.6); opacity:0; }
  50% { transform:scale(1.2); }
  100% { transform:scale(1); opacity:1; }
}

/* ✅ Tick */
@keyframes tickPop {
  0% {transform:scale(.5);opacity:0}
  60% {transform:scale(1.2);opacity:1}
  100% {transform:scale(1)}
}

.ok {
  background:#2ea44f;
  color:white;
  animation:tickPop .3s ease-out;
}

.fail {
  background:#e5533d;
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

<div style="text-align:center;font-size:9px;color:gray;margin-top:10px;">
© Service Dashboard
</div>

</div>

<script>

const PASSWORD_HASH="__PASSWORD_HASH__";

/* ✅ COPY */
function copyUrl(e,url,el){
 e.preventDefault(); e.stopPropagation();

 if(navigator.clipboard && window.isSecureContext){
  navigator.clipboard.writeText(url).then(()=>animate(el));
 } else {
  const ta=document.createElement("textarea");
  ta.value=url; document.body.appendChild(ta);
  ta.select(); document.execCommand("copy");
  ta.remove(); animate(el);
 }
}

function animate(el){
 el.classList.add("copied");
 setTimeout(()=>el.classList.remove("copied"),800);
}

/* AUTH */
pwd.onkeyup=async e=>{
 if(e.key==="Enter"){
  let d=new TextEncoder().encode(pwd.value);
  let h=await crypto.subtle.digest("SHA-256",d);
  let hex=[...new Uint8Array(h)].map(b=>b.toString(16).padStart(2,"0")).join("");
  if(hex===PASSWORD_HASH){
    auth.style.display="none";
    app.style.display="block";
    checkStatuses();
    start();
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

/* Inactivity */
let t;
function reset(){ clearTimeout(t);
 t=setTimeout(()=>{
  app.style.display="none";
  auth.style.display="flex";
  pwd.value="";
 },300000);
}
["mousemove","keydown","click","scroll"].forEach(e=>document.addEventListener(e,reset));
function start(){reset();}
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

    print("✅ Done")


md_to_cards("bm.md", "index.html")