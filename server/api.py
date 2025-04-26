import os
import json
import threading

from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from html import escape

app = FastAPI()

# @app.get("/regions", response_model=dict)
# async def get_regions():
#     file_path = "./regions/ru_regions_updated.json"
#     # Check if the file exists
#     if not os.path.exists(file_path):
#         raise HTTPException(status_code=404, detail="File not found")

#     try:
#         # Open and load the JSON file
#         with open(file_path, "r", encoding="utf-8") as f:
#             data = json.load(f)
#     except json.JSONDecodeError:
#         raise HTTPException(status_code=500, detail="Error parsing JSON")
    
#     return data


@app.get('/supplies', response_class=HTMLResponse)
async def get_supplies():
    from services import supplies_service
    supplies =  supplies_service.get_supplies_offices_status()

    # ───── simple HTML builder ────────────────────────────────
    html_parts: list[str] = [
        "<!DOCTYPE html>",
        "<html><head>",
        "<meta charset='utf-8'>",
        "<title>Supplies</title>",
        "<style>",
        "body{font-family:system-ui,Arial,sans-serif;margin:2rem;line-height:1.45}",
        ".card{border:1px solid #ccc;border-radius:8px;padding:1rem;margin-bottom:1.5rem;"
        "box-shadow:0 2px 4px rgba(0,0,0,.05)}",
        ".header{font-size:1.1rem;font-weight:600;margin-bottom:.3rem}",

        # ↓↓↓ smaller table styling ↓↓↓
        "table{width:100%;max-width:600px;border-collapse:collapse;margin-top:.5rem;"
        "font-size:0.85rem}",
        "th,td{border:1px solid #ddd;padding:.25rem .4rem;text-align:left}",
        "th{background:#f5f5f5}",

        "</style></head><body>",
    ]

    for item in supplies:
        s = item["supply"]
        dt = datetime.fromisoformat(s['createDate'])
        dt_str = dt.strftime("%d %b, %Y")
        html_parts.extend(
            [
                "<div class='card'>",
                f"<div class='header'>Поставка #{s['preorderId']} от {dt_str} - {s['detailsQuantity']} шт. - {escape(s['boxTypeName'])}</div>",
                f"<strong>Склад:</strong> {escape(s['warehouseName'])} ({escape(s['warehouseAddress'])})"
                "<table><thead><tr><th>Дата</th><th>Коэффициент</th><th>Стоимость</th></tr></thead><tbody>",
            ]
        )

        for row in item["acceptance_costs"]:
            dt = datetime.strptime(row['date'], "%Y-%m-%dT%H:%M:%SZ")
            dt_str = dt.strftime("%A - %d %b, %Y")
            dt_str = dt_str[0].upper() + dt_str[1:]
            html_parts.append(
                f"<tr><td>{dt_str}</td>"
                f"<td>{row['coefficient']}</td>"
                f"<td>{row['cost']}</td></tr>"
            )

        html_parts.extend(["</tbody></table>", "</div>"])  # close .card

    html_parts.append("</body></html>")

    # ───── return the page ────────────────────────────────────
    return HTMLResponse("".join(html_parts))

def _run_api():
    import uvicorn
    uvicorn.run(app=app, host='0.0.0.0', port=8000)

def start_api():
    api_thread = threading.Thread(target=_run_api, daemon=True)
    api_thread.start()