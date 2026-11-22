"""
VIRALCUT AI - Main Desktop Application Launcher
Starts the FastAPI application backend and launches the studio desktop interface.
"""

import os
import sys
import time
import threading
import webbrowser
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

def open_browser():
    """
    Actively checks when the server is ready, then automatically launches
    the ViralCut Studio in the user's default browser.
    """
    import urllib.request
    url = "http://127.0.0.1:8000"
    ready = False
    for _ in range(40):
        time.sleep(0.3)
        try:
            with urllib.request.urlopen(f"{url}/api/system/status", timeout=0.5) as resp:
                if resp.status == 200:
                    ready = True
                    break
        except Exception:
            continue

    print(f"\n==================================================================")
    print(f" -> VIRALCUT AI STUDIO IS RUNNING AND READY!")
    print(f" -> Opening your browser: {url}")
    print(f" -> (If browser doesn't pop up, simply visit {url})")
    print(f"==================================================================\n")

    try:
        opened = webbrowser.open(url)
        if not opened:
            os.system(f'start "" "{url}"')
    except Exception:
        try:
            os.system(f'start "" "{url}"')
        except Exception:
            pass

def main():
    print("=" * 65)
    print("   VIRALCUT AI - INTELLIGENT AUTONOMOUS CLIPPING STUDIO")
    print("=" * 65)
    print("-> Initializing local server on http://127.0.0.1:8000 ...")
    print("-> Desktop Studio UI: http://127.0.0.1:8000")
    print("-> Press Ctrl+C in this terminal window to stop.")
    print("=" * 65)

    # Launch browser after server has bound to port
    threading.Thread(target=open_browser, daemon=True).start()

    import uvicorn
    # Start Uvicorn ASGI server
    uvicorn.run(
        "backend.main:app",
        host="127.0.0.1",
        port=8000,
        log_level="info",
        reload=False
    )

if __name__ == "__main__":
    main()
