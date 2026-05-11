import markdown

def md_table_to_html(md_file, html_file):
    # Read markdown file
    with open(md_file, "r", encoding="utf-8") as f:
        md_content = f.read()

    # Convert markdown to HTML (with table support)
    html_table = markdown.markdown(md_content, extensions=["tables"])

    # Inline-styled HTML5 page
    html_page = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Markdown Table Viewer</title>
</head>
<body style="font-family:Arial, sans-serif; margin:20px; background:#f9f9f9;">
  <h1 style="text-align:center;">Markdown Table Viewer</h1>
  <input type="text" id="searchBox" placeholder="Search..."
         style="display:block; margin:10px auto; padding:8px; width:90%; max-width:400px;
                border:1px solid #ccc; border-radius:4px;">
  <div style="overflow-x:auto; margin-top:20px;">
    {html_table}
  </div>
  <script>
    const searchBox = document.getElementById("searchBox");
    searchBox.addEventListener("keyup", function() {{
      const filter = searchBox.value.toLowerCase();
      const rows = document.querySelectorAll("table tbody tr");
      rows.forEach(row => {{
        const text = row.innerText.toLowerCase();
        row.style.display = text.includes(filter) ? "" : "none";
      }});
    }});
    // Apply inline styles to table elements
    document.querySelectorAll("table").forEach(tbl => {{
      tbl.style.borderCollapse = "collapse";
      tbl.style.width = "100%";
      tbl.style.background = "white";
    }});
    document.querySelectorAll("th").forEach(th => {{
      th.style.border = "1px solid #ddd";
      th.style.padding = "8px";
      th.style.textAlign = "left";
      th.style.backgroundColor = "#f2f2f2";
    }});
    document.querySelectorAll("td").forEach(td => {{
      td.style.border = "1px solid #ddd";
      td.style.padding = "8px";
      td.style.textAlign = "left";
    }});
    document.querySelectorAll("tr").forEach(tr => {{
      tr.addEventListener("mouseover", () => tr.style.backgroundColor = "#f1f1f1");
      tr.addEventListener("mouseout", () => tr.style.backgroundColor = "");
    }});
  </script>
</body>
</html>
"""

    # Write to output HTML file
    with open(html_file, "w", encoding="utf-8") as f:
        f.write(html_page)

# Example usage:
md_table_to_html("bm.md", "bm.html")
