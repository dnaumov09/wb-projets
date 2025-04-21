from fastapi import FastAPI, HTTPException
import json
import os

app = FastAPI()

# Define the file path for the JSON file
file_path = "./regions/ru_regions_updated.json"

@app.get("/regions", response_model=dict)
async def get_regions():
    # Check if the file exists
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")

    try:
        # Open and load the JSON file
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Error parsing JSON")
    
    return data


def run_server():
    # import uvicorn
    # uvicorn.run(app=app, host='0.0.0.0', port=8000)
    pass