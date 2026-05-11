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

        fields = ""
        for k, v in data.items():
            if k.lower() == "url":
                continue
            fields += f"""
            <div class="field">
              <div class="label">{k}</div>
              <div class="value">{v}</div>
            </div>
            """

        cards_html += f"""
<a class="card" href="{url}" target="_blank" data-url="{url}">
  {fields}
  <div class="status">⏳</div>
</a>
"""

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Service Dashboard</title>

<!-- Favicon -->
<link rel="icon" type="image/png" href="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAMAAAAoLQ9TAAAAMFBMVEUAAAD///8AAABfX1+fn5+Pj4+YmJipqanJycm4uLiLi4vCwsLx8fF79kkpAAAADXRSTlMAEBAgIDAwQEBAUF9w4ZQAAABPSURBVBjTY2CAAUYGBgaGhgZGJmYmRiZWNi4eHiE5OTkFhYWKijYGRk5uDl4+fg4ODR0TEoKKiooKCnqGhoYmJiYGADAD9fAs+n4RS3AAAAAElFTkSuQmCC">

<style>
:root {{
  --bg: #121212;
  --card: #1e1e1e;
  --text: #e6e6e6;
  --muted: #9e9e9e;
  --border: #2a2a2a;
}}

body.light {{
  --bg: #f7f7f7;
  --card: #ffffff;
  --text: #202020;
  --muted: #6a6a6a;
  --border: #dcdcdc;
}}

body {{
  margin: 0;
  padding: 14px;
  font-family: Arial, Helvetica, Verdana, sans-serif;
  font-size: 12.5px;
  background: var(--bg);
  color: var(--text);
}}

.top-bar {{
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
  justify-content: center;
  margin-bottom: 14px;
}}

.search {{
  flex: 1;
  min-width: 200px;
  max-width: 420px;
  padding: 7px 9px;
  border-radius: 6px;
  border: 1px solid var(--border);
  background: var(--card);
  color: var(--text);
  font-size: 12px;
}}

.icon-btn {{
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 7px;
  cursor: pointer;
  font-size: 16px;
  padding: 6px 9px;
}}

.container {{
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(255px, 1fr));
  gap: 13px;
}}

.card {{
  background: var(--card);
  border-radius: 10px;
  padding: 12px;
  border: 1px solid var(--border);
  box-shadow: 0 2px 6px rgba(0,0,0,0.25);
  text-decoration: none;
  color: var(--text);
  position: relative;
}}

.card:hover {{
  transform: translateY(-2px);
}}

.field {{ margin-bottom: 6px; }}

.label {{
  font-size: 10.5px;
  color: var(--muted);
}}

.value {{
  font-weight: 600;
  word-break: break-word;
}}

.status {{
  position: absolute;
  top: 8px;
  right: 10px;
  font-size: 15px;
}}

.ok {{ color: #48c774; }}
.fail {{ color: #f14668; }}

.footer {{
  margin-top: 18px;
  text-align: center;
  font-size: 10.5px;
  color: var(--muted);
}}

@media print {{
  .top-bar, .status {{ display: none; }}
  body {{ background: white; color: black; }}
}}
</style>
</head>

<body>

<div class="top-bar">
  <input class="search" id="searchBox" placeholder="Search..." />
  <button class="icon-btn" id="modeBtn">☀️</button>
  <button class="icon-btn" onclick="window.print()">📄</button>
</div>

<div class="container" id="cards">
  {cards_html}
</div>

<div class="footer" id="footer"></div>

<script>
// Search
document.getElementById("searchBox").addEventListener("keyup", e => {{
  const q = e.target.value.toLowerCase();
  document.querySelectorAll(".card").forEach(c => {{
    c.style.display = c.innerText.toLowerCase().includes(q) ? "" : "none";
  }});
}});

// Footer timestamp + copyright
document.getElementById("footer").textContent =
  new Date().toLocaleString() + " © Monitoring Dashboard";

// Dark / Light toggle
const body = document.body;
const btn = document.getElementById("modeBtn");

btn.onclick = () => {{
  body.classList.toggle("light");
  btn.textContent = body.classList.contains("light") ? "🌙" : "☀️";
}};

// URL status check
document.querySelectorAll(".card").forEach(card => {{
  const status = card.querySelector(".status");
  const url = card.dataset.url;

  fetch(url, {{ method: "HEAD", mode: "no-cors" }})
    .then(() => {{
      status.textContent = "✔";
      status.classList.add("ok");
    }})
    .catch(() => {{
      status.textContent = "✖";
      status.classList.add("fail");
    }});
}});
</script>

</body>
</html>
"""

    with open(html_file, "w", encoding="utf-8") as f:
        f.write(html)

    print("✅ index.html generated successfully")


# Usage
md_to_cards("bm.md", "index.html")
