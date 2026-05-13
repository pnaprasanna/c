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
        for k, v in data.items():
            if k.lower() == "url":
                continue
            fields_html += f"""
            <div class="field">
              <div class="label">{k}</div>
              <div class="value">{v}</div>
            </div>
            """

        cards_html += f"""
<a class="card" href="{url}" target="_blank" data-url="{url}">
  {fields_html}
  <div class="status">⏳</div>
</a>
"""

    html_template = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Service Dashboard</title>

<!-- ✅ XLSX Library -->
<script src="https://cdn.jsdelivr.net/npm/xlsx/dist/xlsx.full.min.js"></script>

<style>
/* (same styles as yours, unchanged for brevity) */
body { font-family: Arial; background:#121212; color:#eee; padding:14px;}
.topbar { display:flex; gap:10px;}
.search { padding:8px; flex:1;}
.tools span { cursor:pointer; margin-left:10px; font-size:16px;}
.container { display:grid; grid-template-columns:repeat(auto-fit,minmax(260px,1fr)); gap:14px;}
.card { background:#1e1e1e; padding:14px; border-radius:10px; text-decoration:none; color:#eee;}
.label { font-size:11px; color:#aaa;}
.value { font-weight:bold;}
.status { position:absolute;}
</style>
</head>

<body>

<div id="auth">
  <input type="password" id="pwd" placeholder="Password">
</div>

<div id="app" style="display:none;">

<div class="topbar">
  <input type="text" class="search" placeholder="Search..." id="searchBox">
  <div class="tools">
    <span id="themeToggle">🌙</span>
    <span onclick="window.print()">🖨</span>
    <span onclick="exportToExcel()">📊</span>
  </div>
</div>

<div class="container">
__CARDS__
</div>

</div>

<script>
const PASSWORD_HASH = "__PASSWORD_HASH__";

/* SHA */
async function sha256(text){
  const buf = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(text));
  return Array.from(new Uint8Array(buf)).map(x=>x.toString(16).padStart(2,"0")).join("");
}

/* Auth */
document.getElementById("pwd").addEventListener("keyup", async e=>{
  if(e.key==="Enter"){
    const h=await sha256(e.target.value);
    if(h===PASSWORD_HASH){
      document.getElementById("auth").style.display="none";
      document.getElementById("app").style.display="block";
    } else alert("Wrong password");
  }
});

/* Search */
document.getElementById("searchBox").addEventListener("keyup", e=>{
  const q = e.target.value.toLowerCase();
  document.querySelectorAll(".card").forEach(c=>{
    c.style.display = c.innerText.toLowerCase().includes(q) ? "" : "none";
  });
});

/* ✅ TRUE XLSX EXPORT */
function exportToExcel() {
  let data = [];
  let headersSet = new Set();

  document.querySelectorAll(".card").forEach(card => {
    if (card.style.display === "none") return;

    let row = {};

    card.querySelectorAll(".field").forEach(f => {
      let key = f.querySelector(".label").innerText.trim();
      let val = f.querySelector(".value").innerText.trim();
      row[key] = val;
      headersSet.add(key);
    });

    row["URL"] = card.dataset.url;
    headersSet.add("URL");

    data.push(row);
  });

  const headers = Array.from(headersSet);

  const sheetData = [
    headers,
    ...data.map(r => headers.map(h => r[h] || ""))
  ];

  const ws = XLSX.utils.aoa_to_sheet(sheetData);
  const wb = XLSX.utils.book_new();

  XLSX.utils.book_append_sheet(wb, ws, "Dashboard");

  XLSX.writeFile(wb, "dashboard.xlsx");
}
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

    print("✅ index.html generated with TRUE XLSX export")


# Usage
md_to_cards("bm.md", "index.html")