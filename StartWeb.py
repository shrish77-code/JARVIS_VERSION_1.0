import threading
import time
from pathlib import Path

from WebServer import run_server
from Main import FirstThread

print("=" * 60)
print("     J.A.R.V.I.S. - AI Assistant Web Interface")
print("=" * 60)
print("\n Starting Web Server and Backend...")

backend_thread = threading.Thread(target=FirstThread, daemon=True)
backend_thread.start()

time.sleep(1)

print("\n Backend started successfully!")
print("\n Web Interface: http://localhost:5000")
print(" Press Ctrl+C to stop\n")
print("=" * 60)

try:
    run_server()
except KeyboardInterrupt:
    print("\n\n Shutting down J.A.R.V.I.S...")
    print(" Goodbye!\n")
