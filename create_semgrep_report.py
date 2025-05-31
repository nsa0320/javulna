import json

with open("semgrep-result.json", "r") as f:
    data = json.load(f)

html = "<html><head><title>Semgrep Report</title></head><body>"
html += "<h1>Semgrep Scan Result</h1><ul>"

for finding in data.get("results", []):
    html += f"<li><b>{finding['check_id']}</b> - {finding['path']}:{finding['start']['line']}<br>"
    html += f"<pre>{finding['extra']['message']}</pre></li>"

html += "</ul></body></html>"

with open("semgrep-report.html", "w") as f:
    f.write(html)
