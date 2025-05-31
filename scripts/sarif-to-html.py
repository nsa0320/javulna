# scripts/sarif-to-html.py
import json
import os

SARIF_PATH = "result.sarif"
if not os.path.exists(SARIF_PATH):
    raise FileNotFoundError("result.sarif 파일이 존재하지 않습니다.")

with open(SARIF_PATH, 'r') as f:
    sarif = json.load(f)

html = ['<html><head><meta charset="UTF-8"><title>CodeQL Report</title></head><body>']
html.append('<h1>CodeQL 분석 결과</h1>')

runs = sarif.get("runs", [])
for run in runs:
    tool = run.get("tool", {}).get("driver", {}).get("name", "Unknown Tool")
    html.append(f"<h2>도구: {tool}</h2>")
    results = run.get("results", [])
    if not results:
        html.append("<p>🔍 취약점이 발견되지 않았습니다.</p>")
        continue
    html.append(f"<p>총 {len(results)}건의 결과가 발견되었습니다.</p>")
    html.append("<ul>")
    for result in results:
        rule_id = result.get("ruleId", "unknown")
        message = result.get("message", {}).get("text", "No message")
        locations = result.get("locations", [])
        if locations:
            loc = locations[0].get("physicalLocation", {}).get("artifactLocation", {}).get("uri", "unknown")
            region = locations[0].get("physicalLocation", {}).get("region", {})
            line = region.get("startLine", "?")
            html.append(f"<li><b>{rule_id}</b> @ <code>{loc}:{line}</code><br>{message}</li>")
        else:
            html.append(f"<li><b>{rule_id}</b><br>{message}</li>")
    html.append("</ul>")

html.append("</body></html>")

with open("codeql-report.html", "w", encoding="utf-8") as f:
    f.write('\n'.join(html))

print("✅ HTML 리포트 생성 완료")
