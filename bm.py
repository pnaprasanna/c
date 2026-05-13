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

        # ✅ URL with inline status (kept)
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
<link rel="icon" type="image/png" href="fav.svg">
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

.container {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 14px;
}

/* ✅ CARD (AI style preserved) */
.card {
  background: var(--card);
  border-radius: 12px;
  padding: 14px;
  text-decoration: none;
  color: var(--text);
  border: 1px solid var(--border);

  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

/* ✅ Neon pulse animation */
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

/* Fields */
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

/* ✅ URL + inline status */
.url-line {
  display: flex;
  align-items: center;
  gap: 6px;
}

.status-inline {
  font-size: 14px;
}

/* ✅ Blue tick style */
.ok {
  color: #3b82f6;
}

.fail {
  color: var(--fail);
}

/* Footer */
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
</div>

<div class="container">
__CARDS__
</div>

<div class="footer" id="footer"></div>

<script>
/* Search */
document.getElementById("searchBox").addEventListener("keyup", e => {
  const q = e.target.value.toLowerCase();
  document.querySelectorAll(".card").forEach(card => {
    card.style.display = card.innerText.toLowerCase().includes(q) ? "" : "none";
  });
});

/* Footer */
document.getElementById("footer").textContent =
  new Date().toLocaleString() + " © Service Dashboard";

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