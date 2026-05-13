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

        # ✅ URL with inline status
        fields_html += f"""
        <div class="field">
          <div class="label">URL</div>
          <div class="value url-line">
            <span class="url-text">{url}</span>
            <span class="status-inline">⏳</span>
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

/* Sidebar */
.sidebar {
  position: fixed;
  top: 0;
  left: -220px;
  width: 220px;
  height: 100%;
  background: #1b1b1b;
  padding: 20px;
  transition: 0.3s;
  z-index: 1000;
}

.sidebar.active {
  left: 0;
}

.sidebar a {
  display: block;
  margin: 10px 0;
  color: #ccc;
  text-decoration: none;
}

.menu-btn {
  cursor: pointer;
  font-size: 20px;
}

/* Layout */
body {
  margin: 0;
  padding: 14px;
  font-family: Arial;
  background: var(--bg);
  color: var(--text);
}

.topbar {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 12px;
}

.container {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 14px;
}

/* CARD */
.card {
  background: var(--card);
  border-radius: 12px;
  padding: 14px;
  text-decoration: none;
  color: var(--text);
  border: 1px solid var(--border);

  transition: 0.2s;
}

@keyframes neonPulse {
  0%,100% {
    box-shadow: 0 0 10px rgba(0,255,200,0.2);
  }
  50% {
    box-shadow: 0 0 30px rgba(0,255,200,0.4);
  }
}

.card:hover {
  transform: translateY(-4px);
  border-color: rgba(0,255,200,0.6);
  animation: neonPulse 1.5s infinite;
}

/* Fields */
.field { margin-bottom: 8px; }
.label { font-size: 11px; color: var(--muted); }
.value { font-weight: 600; }

/* ✅ URL INLINE STATUS */
.url-line {
  display: flex;
  align-items: center;
  gap: 8px;
}

.status-inline {
  font-size: 14px;
}

.ok { color: var(--ok); }
.fail { color: var(--fail); }

.footer {
  margin-top: 18px;
  text-align: center;
  font-size: 11px;
  color: var(--muted);
}
</style>
</head>

<body>

<!-- Sidebar -->
<div class="sidebar" id="sidebar">
  <a href="#">🏠 Home</a>
  <a href="#">📊 Reports</a>
  <a href="#">⚙ Settings</a>
</div>

<div class="topbar">
  <span class="menu-btn" onclick="toggleMenu()">☰</span>
  <input type="text" class="search" placeholder="Search..." id="searchBox">
</div>

<div class="container">
__CARDS__
</div>

<div class="footer" id="footer"></div>

<script>
const PASSWORD_HASH = "__PASSWORD_HASH__";

/* Sidebar toggle */
function toggleMenu() {
  document.getElementById("sidebar").classList.toggle("active");
}

/* Search */
document.getElementById("searchBox").addEventListener("keyup", e => {
  const q = e.target.value.toLowerCase();
  document.querySelectorAll(".card").forEach(card => {
    card.style.display = card.innerText.toLowerCase().includes(q) ? "" : "none";
  });
});

/* Footer */
document.getElementById("footer").textContent =
  new Date().toLocaleString();

/* Status check */
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

checkStatuses();
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