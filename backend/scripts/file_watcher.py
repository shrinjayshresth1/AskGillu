"""
file_watcher.py
Real-time document ingestion via filesystem event monitoring.

Uses the watchdog library to monitor the docs/ folder.
When a new or modified PDF is detected, it triggers re-ingestion
by POSTing to the /ingest internal endpoint.

Install: pip install watchdog

Usage: started automatically in FastAPI startup_event when
ENABLE_FILE_WATCHER=true is set in .env
"""
import os
import time
import threading
import requests
import logging
from datetime import datetime

try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler, FileCreatedEvent, FileModifiedEvent
    WATCHDOG_AVAILABLE = True
except ImportError:
    WATCHDOG_AVAILABLE = False
    Observer = None
    FileCreatedEvent = None
    FileModifiedEvent = None
    # Provide a dummy base class so the class definition doesn't crash
    class FileSystemEventHandler:
        pass

logger = logging.getLogger(__name__)

# Global state for watcher status
_watcher_state = {
    "active": False,
    "started_at": None,
    "last_event": None,
    "last_event_file": None,
    "events_processed": 0,
    "observer": None,
}


class PDFIngestionHandler(FileSystemEventHandler):
    """Watchdog event handler — triggers ingestion on new/modified PDFs."""

    def __init__(self, ingest_url: str, debounce_seconds: float = 3.0):
        super().__init__()
        self.ingest_url = ingest_url
        self.debounce_seconds = debounce_seconds
        self._pending: dict = {}

    def _should_process(self, path: str) -> bool:
        return path.lower().endswith(".pdf")

    def _debounced_ingest(self, path: str):
        """Wait debounce_seconds, then trigger ingest if file still exists."""
        time.sleep(self.debounce_seconds)
        if path in self._pending and os.path.exists(path):
            filename = os.path.basename(path)
            logger.info(f"[WATCHER] New file detected: {filename} — triggering ingestion…")
            try:
                resp = requests.post(
                    self.ingest_url,
                    data={"filename": filename},
                    timeout=120,
                )
                if resp.status_code == 200:
                    logger.info(f"[WATCHER] ✅ Ingested {filename} successfully.")
                else:
                    logger.warning(f"[WATCHER] ⚠️ Ingest returned {resp.status_code}: {resp.text[:200]}")
            except Exception as e:
                logger.error(f"[WATCHER] ❌ Ingest request failed: {e}")

            _watcher_state["last_event"] = datetime.now().isoformat()
            _watcher_state["last_event_file"] = filename
            _watcher_state["events_processed"] += 1
            del self._pending[path]

    def on_created(self, event):
        if not event.is_directory and self._should_process(event.src_path):
            self._pending[event.src_path] = True
            t = threading.Thread(
                target=self._debounced_ingest,
                args=(event.src_path,),
                daemon=True,
            )
            t.start()

    def on_modified(self, event):
        # Also handle overwrites of existing documents
        if not event.is_directory and self._should_process(event.src_path):
            self._pending[event.src_path] = True
            t = threading.Thread(
                target=self._debounced_ingest,
                args=(event.src_path,),
                daemon=True,
            )
            t.start()


def start_file_watcher(docs_dir: str, ingest_url: str = "http://localhost:8000/ingest") -> bool:
    """
    Start the watchdog observer as a daemon thread.
    Returns True if started successfully, False otherwise.
    """
    if not WATCHDOG_AVAILABLE:
        logger.warning("[WATCHER] watchdog not installed. File watching disabled. Run: pip install watchdog")
        return False

    if _watcher_state["active"]:
        logger.info("[WATCHER] Already running.")
        return True

    if not os.path.isdir(docs_dir):
        logger.warning(f"[WATCHER] docs dir not found: {docs_dir}")
        return False

    handler = PDFIngestionHandler(ingest_url=ingest_url)
    observer = Observer()
    observer.schedule(handler, path=docs_dir, recursive=False)
    observer.daemon = True
    observer.start()

    _watcher_state["active"] = True
    _watcher_state["started_at"] = datetime.now().isoformat()
    _watcher_state["observer"] = observer

    logger.info(f"[WATCHER] 👁 Watching for new PDFs in: {docs_dir}")
    return True


def stop_file_watcher():
    """Stop the observer if running."""
    if _watcher_state["active"] and _watcher_state["observer"]:
        _watcher_state["observer"].stop()
        _watcher_state["observer"].join(timeout=5)
        _watcher_state["active"] = False
        logger.info("[WATCHER] Stopped.")


def get_watcher_status() -> dict:
    """Return current watcher status for the /watcher-status endpoint."""
    return {
        "watcher_active": _watcher_state["active"],
        "watchdog_available": WATCHDOG_AVAILABLE,
        "started_at": _watcher_state["started_at"],
        "last_event_at": _watcher_state["last_event"],
        "last_event_file": _watcher_state["last_event_file"],
        "events_processed": _watcher_state["events_processed"],
    }
