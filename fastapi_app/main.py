from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional
from dotenv import load_dotenv
import os
import httpx

app = FastAPI()

# ====== pydantic model ========
class AnalyzePRrequest(BaseModel):
    repo_url : str
    pr_number : int
    github_token : Optional[str] = None

# Django api base url
DJANGO_API_BASE_URL = os.getenv("DJANGO_API__BASE_URL", "http://127.0.0.1:8000")

# ============== api endpoints ==============
@app.get("/health/")
async def health_check():
    return {"status": "ok"}

@app.post("/start-task/")
async def start_task_endpoint(task_request : AnalyzePRrequest):
    data = {
        "repo_url" : task_request.repo_url,
        "pr_number" : task_request.pr_number,
        "github_token" : task_request.github_token
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{DJANGO_API_BASE_URL}/start_task/",
                json = data # DRF can usually handle both JSON and form data, so data=data may still work. But since this is API-to-API communication, json=data is cleaner and more standard.
            )

            if response.status_code != 200:
                try:
                    error_body = response.json()
                except ValueError:
                    error_body = {"detail": response.text}

                return JSONResponse(
                    status_code=response.status_code,
                    content=error_body
                )
        return response.json() # converts the json response into python dictionary and sends the response back to the client 
    
    except httpx.RequestError:
        raise HTTPException(
            status_code = 503,
            detail = "Django server did not respond"
        )


@app.get("/task-status-view/{task_id}/")
async def task_status_endpoint(task_id: str):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{DJANGO_API_BASE_URL}/task_status_view/{task_id}/",
            )

            if response.status_code != 200:
                try:
                    error_body = response.json()
                except ValueError:
                    error_body = {"detail": response.text}

                return JSONResponse(
                    status_code=response.status_code,
                    content=error_body
                )
        return response.json()
    
    except httpx.RequestError:
        raise HTTPException(
            status_code = 503,
            detail = "Django server did not respond"
        )