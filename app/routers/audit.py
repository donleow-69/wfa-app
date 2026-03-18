"""Legislation audit — uses Claude API + web search to verify penalty data is current."""

import json
import os
from datetime import datetime

import anthropic
from fastapi import APIRouter, Query, Request
from fastapi.responses import HTMLResponse, JSONResponse

from .rights_data import COUNTRY_NAMES, RIGHTS_BY_COUNTRY

router = APIRouter()

AUDIT_SECRET = os.getenv("AUDIT_SECRET", "")


def _extract_penalties(country_code: str) -> list[dict]:
    """Extract all penalty entries for a country from rights data."""
    entries = []
    categories = RIGHTS_BY_COUNTRY.get(country_code, [])
    for cat in categories:
        cat_id = cat.get("id", "")
        title = cat.get("title", "")
        penalties = cat.get("penalties", [])
        laws = [law["name"] for law in cat.get("key_laws", [])]
        details = cat.get("details", [])
        # Also grab any HKD/USD/GBP/SGD/RM/THB/IDR/PHP amounts from details
        amounts_in_details = [
            d for d in details
            if any(c in d for c in ["$", "£", "HKD", "SGD", "RM", "THB", "IDR", "PHP", "S$"])
        ]
        entries.append({
            "category": cat_id,
            "title": title,
            "penalties": penalties,
            "key_laws": laws,
            "key_amounts": amounts_in_details,
        })
    return entries


def _build_audit_prompt(country_code: str, country_name: str, entries: list[dict]) -> str:
    """Build the prompt for Claude to audit legislation."""
    data_block = json.dumps(entries, indent=2)
    return f"""You are a legal compliance auditor. Verify whether the following penalty amounts and legislation references for {country_name} are current as of {datetime.now().strftime('%B %Y')}.

For each category, check:
1. Are the penalty fine amounts correct and current?
2. Are imprisonment terms correct?
3. Are the referenced laws still the correct/current legislation?
4. Are any key monetary figures (wage rates, caps, thresholds) still accurate?

DATA TO VERIFY:
{data_block}

Respond with JSON only (no markdown fences). Use this exact structure:
{{
  "country": "{country_code}",
  "country_name": "{country_name}",
  "audit_date": "{datetime.now().strftime('%Y-%m-%d')}",
  "issues": [
    {{
      "category": "category_id",
      "severity": "high|medium|low",
      "current_value": "what the app currently says",
      "correct_value": "what it should be based on current law",
      "source": "name of the legislation or amendment",
      "note": "brief explanation"
    }}
  ],
  "verified_ok": ["list of category_ids where everything looks correct"],
  "uncertain": ["list of category_ids where you cannot confidently verify"]
}}

If everything is correct, return an empty issues array. Be conservative — only flag items you are confident are wrong. Put items you're unsure about in the uncertain array."""


async def _audit_country(country_code: str) -> dict:
    """Run the audit for a single country."""
    country_name = COUNTRY_NAMES.get(country_code, country_code)
    entries = _extract_penalties(country_code)
    if not entries:
        return {"country": country_code, "country_name": country_name, "error": "No data found"}

    prompt = _build_audit_prompt(country_code, country_name, entries)

    client = anthropic.AsyncAnthropic(api_key=os.getenv("ANTHROPIC_API_KEY", ""))
    response = await client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2000,
        messages=[{"role": "user", "content": prompt}],
    )

    text = response.content[0].text.strip()
    text = text.replace("```json", "").replace("```", "").strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return {
            "country": country_code,
            "country_name": country_name,
            "error": "Failed to parse audit response",
            "raw": text[:500],
        }


@router.get("/admin/audit", response_class=HTMLResponse)
async def audit_page(request: Request, key: str = Query("")):
    """Show the audit page (requires AUDIT_SECRET)."""
    if not AUDIT_SECRET or key != AUDIT_SECRET:
        return HTMLResponse("<h1>403 Forbidden</h1>", status_code=403)

    countries = list(COUNTRY_NAMES.items())
    html = f"""<!DOCTYPE html>
<html><head><title>Legislation Audit</title>
<style>
body {{ font-family: system-ui; max-width: 900px; margin: 2rem auto; padding: 0 1rem; background: #111; color: #eee; }}
h1 {{ color: #6cf; }}
.btn {{ background: #2563eb; color: white; border: none; padding: 10px 20px; border-radius: 6px; cursor: pointer; font-size: 1rem; }}
.btn:hover {{ background: #1d4ed8; }}
.btn:disabled {{ background: #555; cursor: wait; }}
#results {{ margin-top: 2rem; }}
.country {{ background: #1a1a2e; border-radius: 8px; padding: 1rem; margin: 1rem 0; }}
.country h3 {{ margin-top: 0; }}
.ok {{ color: #4ade80; }}
.issue {{ color: #f87171; background: #2a1a1a; padding: 0.5rem; border-radius: 4px; margin: 0.5rem 0; }}
.issue.medium {{ color: #fbbf24; background: #2a2a1a; }}
.issue.low {{ color: #93c5fd; background: #1a1a2a; }}
.uncertain {{ color: #a78bfa; }}
.spinner {{ display: none; }}
.loading .spinner {{ display: inline; }}
</style></head>
<body>
<h1>Legislation Audit</h1>
<p>Uses Claude API to verify all penalty amounts, fines, and legislation references are current.</p>
<div>
  <button class="btn" onclick="runAudit('all')" id="auditAllBtn">Audit All Countries</button>
  {''.join(f'<button class="btn" style="margin:4px" onclick="runAudit(\'{code}\')">{name}</button>' for code, name in countries)}
</div>
<div id="status"></div>
<div id="results"></div>
<script>
async function runAudit(country) {{
  const btn = document.getElementById('auditAllBtn');
  btn.disabled = true;
  const status = document.getElementById('status');
  const results = document.getElementById('results');
  results.innerHTML = '';
  status.innerHTML = '<p>Running audit... this may take a minute.</p>';

  const url = '/admin/audit/run?key={key}&country=' + country;
  try {{
    const res = await fetch(url);
    const data = await res.json();
    status.innerHTML = '<p style="color:#4ade80">Audit complete.</p>';
    renderResults(data);
  }} catch(e) {{
    status.innerHTML = '<p style="color:#f87171">Error: ' + e.message + '</p>';
  }}
  btn.disabled = false;
}}

function renderResults(data) {{
  const el = document.getElementById('results');
  let html = '';
  for (const r of (Array.isArray(data) ? data : [data])) {{
    html += '<div class="country"><h3>' + (r.country_name || r.country) + '</h3>';
    if (r.error) {{
      html += '<p style="color:#f87171">' + r.error + '</p>';
    }} else {{
      if (r.issues && r.issues.length > 0) {{
        html += '<h4 style="color:#f87171">Issues Found:</h4>';
        for (const i of r.issues) {{
          html += '<div class="issue ' + i.severity + '">';
          html += '<strong>[' + i.severity.toUpperCase() + '] ' + i.category + ':</strong> ';
          html += i.note + '<br>';
          html += '<small>Current: ' + i.current_value + ' &rarr; Should be: ' + i.correct_value + '</small><br>';
          html += '<small>Source: ' + i.source + '</small>';
          html += '</div>';
        }}
      }} else {{
        html += '<p class="ok">All penalties and legislation verified OK.</p>';
      }}
      if (r.verified_ok && r.verified_ok.length > 0) {{
        html += '<p class="ok">Verified: ' + r.verified_ok.join(', ') + '</p>';
      }}
      if (r.uncertain && r.uncertain.length > 0) {{
        html += '<p class="uncertain">Uncertain (manual check recommended): ' + r.uncertain.join(', ') + '</p>';
      }}
    }}
    html += '</div>';
  }}
  el.innerHTML = html;
}}
</script>
</body></html>"""
    return HTMLResponse(html)


@router.get("/admin/audit/run")
async def run_audit(key: str = Query(""), country: str = Query("all")):
    """Run the legislation audit (returns JSON)."""
    if not AUDIT_SECRET or key != AUDIT_SECRET:
        return JSONResponse({"error": "Forbidden"}, status_code=403)

    if country == "all":
        results = []
        for code in COUNTRY_NAMES:
            result = await _audit_country(code)
            results.append(result)
        return JSONResponse(results)
    elif country in COUNTRY_NAMES:
        result = await _audit_country(country)
        return JSONResponse(result)
    else:
        return JSONResponse({"error": f"Unknown country: {country}"}, status_code=400)
