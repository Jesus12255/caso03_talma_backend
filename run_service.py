import os
import sys

# Get the service type from environment variable
service_type = os.getenv("SERVICE_TYPE", "api")
port = os.getenv("PORT", "8000")

if service_type == "worker":
    # Command for Celery Worker
    cmd = [
        "celery",
        "-A",
        "core.celery.celery_app.celery_app",
        "worker",
        "--loglevel=info",
        "--pool=threads",
        "--concurrency=20",
        "-Q",
        "document_queue,celery",
    ]
else:
    # Default command for API (Uvicorn)
    # Cloud Run injects the PORT environment variable, usually 8080.
    # We must start uvicorn on that specific port.
    cmd = ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", port]

# Replace the current process with the new command
try:
    os.execvp(cmd[0], cmd)
except Exception as e:
    print(f"Error executing command {' '.join(cmd)}: {e}")
    sys.exit(1)
