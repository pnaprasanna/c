import markdown
from bs4 import BeautifulSoup

def md_to_cards(md_file, html_file):
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

.topbar {
  display: flex;
  gap: 10px;
  align-items: center;
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
  align-items: center;
  gap: 8px;
  font-size: 11px;
  color: var(--muted);
}

.container {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 14px;
}

.card {
  background: var(--card);
  border-radius: 10px;
  padding: 14px;
  text-decoration: none;
  color: var(--text);
  box-shadow: 0 3px 8px rgba(0,0,0,0.25);
  position: relative;
  border: 1px solid var(--border);
}

.card:hover {
  transform: translateY(-2px);
}

.field {
  margin-bottom: 8px;
}

.label {
  font-size: 11px;
  color: var(--muted);
}

.value {
  font-weight: 600;
  word-break: break-word;
}

.status {
  position: absolute;
  top: 10px;
  right: 12px;
  font-size: 16px;
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

<div class="topbar">
  <input type="text" class="search" placeholder="Search..." id="searchBox">
  <div class="tools">
    <span onclick="window.print()">🖨</span>
    <span id="countdown">05:00</span>
  </div>
</div>

<div class="container" id="cards">
__CARDS__
</div>

<div class="footer" id="footer"></div>

<script>
const REFRESH_INTERVAL = 300;
let remaining = REFRESH_INTERVAL;

document.getElementById("searchBox").addEventListener("keyup", e => {
  const q = e.target.value.toLowerCase();
  document.querySelectorAll(".card").forEach(card => {
    card.style.display = card.innerText.toLowerCase().includes(q) ? "" : "none";
  });
});

function updateFooter() {
  document.getElementById("footer").textContent =
    new Date().toLocaleString() + " © Service Dashboard";
}

function checkStatuses() {
  document.querySelectorAll(".card").forEach(card => {
    const status = card.querySelector(".status");
    const url = card.dataset.url;

    status.textContent = "⏳";
    status.className = "status";

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
  updateFooter();
}

function tick() {
  remaining--;
  if (remaining <= 0) {
    remaining = REFRESH_INTERVAL;
    checkStatuses();
  }
  const m = String(Math.floor(remaining / 60)).padStart(2, "0");
  const s = String(remaining % 60).padStart(2, "0");
  document.getElementById("countdown").textContent = `${m}:${s}`;
}

checkStatuses();
setInterval(tick, 1000);
</script>

</body>
</html>
"""

    html_final = html_template.replace("__CARDS__", cards_html)

    with open(html_file, "w", encoding="utf-8") as f:
        f.write(html_final)

    print("✅ index.html generated successfully")


# Usage
md_to_cards("bm.md", "index.html")
