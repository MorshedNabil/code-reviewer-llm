# Code Reviewer LLM (LLM + Distributed Backend)

## 📌 Overview
This project is an AI-powered code review system that uses a Large Language Model (LLM - LLaMA via Groq API) to analyze and review code like a senior software engineer.
The system is designed with a scalable, asynchronous backend architecture to ensure fast response times and efficient task handling even under heavy load.

<img width="1536" height="1024" alt="ChatGPT Image Jun 9, 2026, 10_36_07 AM" src="https://github.com/user-attachments/assets/0a53600d-98e3-47e4-8333-d3050e5e0226" />

## 📊 System Design Goals
- Non-blocking API response flow
- Efficient resource usage for LLM calls
- Modular microservice-style backend structure
- Easy horizontal scaling

## 🔐 Environment Variables
You will need the following environment variables:
```
GROQ_API_KEY=your_api_key
REDIS_URL=redis://localhost:6379
DJANGO_SECRET_KEY=your_secret_key
```

## Local setup and startup

Use PowerShell from the project root.

### 1) Activate the virtual environment

```powershell
cd "E:\My Projects\Python Projects\code-reviewer-llm"
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks script execution, run this once in the current terminal:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

Then activate again:

```powershell
.\.venv\Scripts\Activate.ps1
```

### 2) Start Redis

This project uses Docker Compose for Redis.

```powershell
docker compose up -d redis
```

If your Docker installation uses the legacy CLI:

```powershell
docker-compose up -d redis
```

To run a existing container:
```powershell
docker start project_name
```

### 3) Start Django app

Open a new terminal and activate the venv there as well, then run:

```powershell
cd "E:\My Projects\Python Projects\code-reviewer-llm\django_app"
python manage.py migrate
python manage.py runserver 0.0.0.0:8000
```

### 4) Start Celery worker

Open another terminal and activate the venv, then run:

```powershell
cd "E:\My Projects\Python Projects\code-reviewer-llm\django_app"
celery -A django_app worker -l info -P eventlet
```

### 5) Start FastAPI app

Open another terminal and activate the venv, then run:

```powershell
cd "E:\My Projects\Python Projects\code-reviewer-llm\fastapi_app"
uvicorn main:app --host 0.0.0.0 --port 8001 --reload
```

## Notes

- Run each app in a separate terminal window because Django, FastAPI, and Celery are independent processes.
- Redis must be running before the Celery worker starts.
- If you are only using the Django backend, you may not need to run the FastAPI app.
- If the venv is not active, use:

```powershell
.\.venv\Scripts\Activate.ps1
```

This project expects the environment name `.venv` at the repository root.
