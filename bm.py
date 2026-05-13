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

        fields_html += f"""
        <div class="field">
          <div class="label">URL</div>
          <div class="value url-line">
            <span>{url}</span>
            <span class="status status-inline">⏳</span>
          </div>
        </div>
        """

        cards_html += f"""
<a class="card" href="{url}" target="_blank" data-url="{url}">
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
  --text: #222222;
  --muted: #666666;
  --border: #dddddd;
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
  font-size: 16px;
  cursor: pointer;
}

.container {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 14px;
}

.card {
  background: var(--card);
  border-radius: 12px;
  padding: 14px;
  text-decoration: none;
  color: var(--text);
  border: 1px solid var(--border);
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

@keyframes neonPulse {
  0%,100% {
    box-shadow:
      0 4px 16px rgba(0,0,0,0.35),
      0 0 10px rgba(0,255,200,0.15);
  }
  50% {
    box-shadow:
      0 10px 28px rgba(0,0,0,0.55),
      0 0 30px rgba(0,255,200,0.35);
  }
}

.card:hover {
  transform: translateY(-4px) scale(1.01);
  animation: neonPulse 1.6s ease-in-out infinite;
}

.field { margin-bottom: 8px; }
.label { font-size: 11px; color: var(--muted); }
.value { font-weight: 600; word-break: break-word; }

.url-line {
  display: flex;
  align-items: center;
  gap: 6px;
}

.status-inline { font-size: 14px; }

.ok { color: #3b82f6; }
.fail { color: var(--fail); }

/* AUTH */
#auth {
  position: fixed;
  inset: 0;
  background: #000000ee;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 999;
}

.auth-box {
  background: #1e1e1e;
  padding: 24px;
  border-radius: 8px;
  text-align: center;
}

.auth-box input {
  margin-top: 12px;
  padding: 8px;
  width: 200px;
}
</style>
</head>

<body>

<div id="auth">
  <div class="auth-box">
    <div>Password</div>
    <input type="password" id="pwd" autofocus />
  </div>
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

/* SHA256 */
async function sha256(text) {
  const data = new TextEncoder().encode(text);
  const hash = await crypto.subtle.digest("SHA-256", data);
  return Array.from(new Uint8Array(hash))
    .map(b => b.toString(16).padStart(2, "0"))
    .join("");
}

/* AUTH */
document.getElementById("pwd").addEventListener("keyup", async e => {
  if (e.key === "Enter") {
    const inputHash = await sha256(e.target.value);
    if (inputHash === PASSWORD_HASH) {
      document.getElementById("auth").style.display = "none";
      document.getElementById("app").style.display = "block";
      checkStatuses();
      startInactivityTracking();  // ✅ start tracking
    } else {
      alert("Incorrect password");
    }
  }
});

/* Theme */
document.getElementById("themeToggle").onclick = () => {
  document.body.classList.toggle("light");
};

/* Search */
document.getElementById("searchBox").addEventListener("keyup", e => {
  const q = e.target.value.toLowerCase();
  document.querySelectorAll(".card").forEach(card => {
    card.style.display = card.innerText.toLowerCase().includes(q) ? "" : "none";
  });
});

/* Excel */
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

/* Status */
function checkStatuses() {
  document.querySelectorAll(".card").forEach(card => {
    const status = card.querySelector(".status-inline");
    const url = card.dataset.url;

    fetch(url, { method: "HEAD", mode: "no-cors" })
      .then(() => {
        status.textContent = "✔";
        status.classList.add("ok");
      })
      .catch(() => {
        status.textContent = "✖";
        status.classList.add("fail");
      });
  });
}

/* ✅ INACTIVITY LOCK */
let inactivityTimer;
const INACTIVITY_LIMIT = 5 * 60 * 1000;

function resetInactivityTimer() {
  clearTimeout(inactivityTimer);
  inactivityTimer = setTimeout(() => {
    document.getElementById("app").style.display = "none";
    document.getElementById("auth").style.display = "flex";
    document.getElementById("pwd").value = "";
  }, INACTIVITY_LIMIT);
}

["mousemove","keydown","scroll","click"].forEach(e=>{
  document.addEventListener(e, resetInactivityTimer);
});

function startInactivityTracking() {
  resetInactivityTimer();
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

    print("✅ index.html generated successfully")


md_to_cards("bm.md", "index.html")
