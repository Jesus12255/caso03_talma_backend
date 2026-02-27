import os
import subprocess
import sys

def run_api():
    print("🚀 Starting FastAPI Server...")
    # Using uvicorn to run the app
    # host 0.0.0.0 is necessary for Docker/Cloud Run
    # port 8080 matches Dockerfile and Cloud Run default
    cmd = [
        "uvicorn", 
        "main:app", 
        "--host", "0.0.0.0", 
        "--port", "8080", 
        "--workers", "1"  # Keep it simple for start
    ]
    subprocess.run(cmd)

def run_worker():
    print("📦 Starting Celery Worker (Pool: SOLO)...")
    # Exact command requested by user:
    # celery -A core.celery.celery_app worker --loglevel=info --pool=solo
    cmd = [
        "celery", 
        "-A", "core.celery.celery_app", 
        "worker", 
        "--loglevel=info", 
        "--pool=solo"
    ]
    subprocess.run(cmd)

if __name__ == "__main__":
    service_type = os.getenv("SERVICE_TYPE", "api").lower()
    
    if service_type == "api":
        run_api()
    elif service_type == "worker":
        run_worker()
    else:
        print(f"❌ Unknown SERVICE_TYPE: {service_type}")
        sys.exit(1)
