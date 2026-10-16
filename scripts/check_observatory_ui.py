"""Run the actual interface control code against a temporary HTTP server.

Node 18+ is needed for this developer check, not for using the Observatory.
The DOM is mocked; visual browser rendering is a separate check.
"""
from pathlib import Path
import shutil
import subprocess
import sys
import threading

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from perfectjet.observatory.workbench import make_server


def main():
    node = shutil.which("node")
    if not node:
        raise SystemExit("Node 18+ is required for the interface developer check")
    server = make_server(0)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        result = subprocess.run([node, str(ROOT / "scripts/check_observatory_ui.js"),
                                 f"http://127.0.0.1:{server.server_port}"], check=False)
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
