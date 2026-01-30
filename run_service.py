import os
import sys
import subprocess
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler


# Define a simple handler for health checks
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")

    def log_message(self, format, *args):
        pass  # Silence logs to avoid clutter


# Get configuration
service_type = os.getenv("SERVICE_TYPE", "api")
# Cloud Run always provides a PORT env var (default 8080)
port = int(os.getenv("PORT", "8080"))

if service_type == "worker":
    # --- WORKER MODE ---
    # Cloud Run requires the container to listen on $PORT for health checks.
    # Celery doesn't do this natively, so we run a background thread with a dummy HTTP server.

    print(f"Starting dummy health check server on port {port}...")

    def start_health_server():
        try:
            server = HTTPServer(("0.0.0.0", port), HealthCheckHandler)
            server.serve_forever()
        except Exception as e:
            print(f"Health check server failed: {e}")

    # Start the HTTP server in a daemon thread
    health_thread = threading.Thread(target=start_health_server, daemon=True)
    health_thread.start()

    # Now run the actual Celery Worker in the main process
    print("Starting Celery worker...")
    cmd = [
        "celery",
        "-A",
        "core.celery.celery_app",
        "worker",
        "--loglevel=info",
        "--pool=threads",
        "--concurrency=20",
        "-Q",
        "document_queue,celery",
    ]

    # Use subprocess instead of execvp to keep the python process (and health thread) alive
    result = subprocess.run(cmd)
    sys.exit(result.returncode)

else:
    # --- API MODE ---
    # For the API, we simply run Uvicorn on the requested port.
    print(f"Starting API on port {port}...")
    cmd = ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", str(port)]

    # Replace the current process with uvicorn
    os.execvp(cmd[0], cmd)
