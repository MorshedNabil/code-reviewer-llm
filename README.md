# code-reviewer-llm
A backend project using Django, FastAPI, Celery and Redis to review pull request codes from GitHub repository.

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
celery -A django_app worker -l info
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
