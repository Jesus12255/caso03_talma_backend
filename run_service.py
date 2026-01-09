import os
import sys

# Get the service type from environment variable
service_type = os.getenv("SERVICE_TYPE", "api")

if service_type == "worker":
    # Command for Celery Worker
    # Note: We use the exact arguments specified in the deployment requirement
    cmd = [
        "celery",
        "-A", "core.celery.celery_app.celery_app",
        "worker",
        "--loglevel=info",
        "--pool=threads",
        "--concurrency=20",
        "-Q", "document_queue,celery"
    ]
else:
    # Default command for API (Uvicorn)
    cmd = [
        "uvicorn",
        "app.main:app",
        "--host", "0.0.0.0",
        "--port", "8000"
    ]

# Replace the current process with the new command
# This ensures the new process becomes PID 1 (or inherits it) which is correct for containers
try:
    os.execvp(cmd[0], cmd)
except Exception as e:
    print(f"Error executing command {' '.join(cmd)}: {e}")
    sys.exit(1)
