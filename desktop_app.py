
import threading
import time
import webview
import logging
import sys
from pathlib import Path

# Project directory
if getattr(sys, "frozen", False):
    BASE_DIR = Path(sys.executable).resolve().parent
else:
    BASE_DIR = Path(__file__).resolve().parent

# Debug logging
logging.basicConfig(
    filename=BASE_DIR / "recruitiq_debug.log",
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
    force=True
)


# Start Flask server
def start_server():
    try:
        logging.info("Starting Flask server")

        from app import app

        app.run(
            host="127.0.0.1",
            port=5000,
            debug=False,
            use_reloader=False
        )

    except Exception:
        logging.exception("Flask server error")


# Main application
if __name__ == "__main__":

    try:
        logging.info("Application starting")

        server = threading.Thread(
            target=start_server,
            daemon=True
        )

        server.start()

        time.sleep(3)

        logging.info("Creating application window")

        webview.create_window(
            "RecruitIQ - Recruitment & Placement Management",
            "http://127.0.0.1:5000/login",
            width=1200,
            height=800,
            min_size=(900, 600)
        )

        logging.info("Starting PyWebView")

        webview.start(gui="edgechromium")

        logging.info("PyWebView closed normally")

    except Exception:
        logging.exception("Application crashed")
