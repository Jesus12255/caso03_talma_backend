import os
import subprocess
import sys
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

def run_api():
    print("🚀 Starting FastAPI Server...")
    cmd = [
        "uvicorn", 
        "main:app", 
        "--host", "0.0.0.0", 
        "--port", "8080", 
        "--workers", "1"
    ]
    subprocess.run(cmd)

class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")
    def log_message(self, format, *args):
        return # Silenciar logs de health check

def start_health_server():
    server = HTTPServer(('0.0.0.0', 8080), HealthCheckHandler)
    print("🏥 Health Check Server started on port 8080")
    server.serve_forever()

def run_worker():
    print("📦 Starting Celery Worker (Pool: SOLO)...")
    
    # Iniciar servidor de salud en un hilo para satisfacer a Cloud Run
    health_thread = threading.Thread(target=start_health_server, daemon=True)
    health_thread.start()

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
