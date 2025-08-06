import pandas as pd
import json
from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from graph.flow import graph_app

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
def read_index():
    with open("static/index.html", "r") as f:
        return f.read()

@app.post("/recommend")
async def recommend(preferences: str = Form(...)):
    query = preferences.strip()
    result = graph_app.invoke({"query": query})

    # Extract sections from agent output
    seg_data = result["segment_insight"]
    perf_data = result["performance_analysis"]
    strategy_text = result["strategy_generator"]

    # Build HTML table for matched campaigns
    seg_df = pd.read_json(seg_data)
    seg_html = seg_df.to_html(index=False, border=1, classes="carbon-table")

    # Performance metrics
    avg_roi = perf_data.get("average_roi", "N/A")
    proj_roi = perf_data.get("projected_roi", "N/A")
    top_features = perf_data.get("top_features", {})
    top_feats_str = ', '.join(f"{k} ({v})" for k, v in top_features.items()) if isinstance(top_features, dict) else top_features

    high_perf = perf_data.get("high_performers", [])
    low_perf = perf_data.get("low_performers", [])
    high_perf_str = '<br>'.join(high_perf) if high_perf else "None"
    low_perf_str = '<br>'.join(low_perf) if low_perf else "None"

    # Format everything in HTML
    response_html = f'''
    <div class="recommendation-box">
        <h3>Matched Campaign Segment:</h3>
        {seg_html}

        <h3>Performance Analysis:</h3>
        <table class="carbon-table">
            <tr><th>Avg ROI</th><td>{avg_roi}</td></tr>
            <tr><th>Projected ROI</th><td>{proj_roi}</td></tr>
            <tr><th>Top Features</th><td>{top_feats_str}</td></tr>
            <tr><th>High Performers</th><td>{high_perf_str}</td></tr>
            <tr><th>Low Performers</th><td>{low_perf_str}</td></tr>
        </table>

        <h3>AI Marketing Strategy Recommendation:</h3>
        <p>{strategy_text}</p>
    </div>
    '''

    return JSONResponse(content={"recommendations": response_html})
