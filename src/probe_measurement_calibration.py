"""Loopback-only calibration of upstream curl flags, not a CNI experiment."""
import json
import platform
import shutil
import socket
import subprocess
import threading
import time
from pathlib import Path


def trial(curl, case, delay):
    record = {"case": case, "body_delay_seconds": delay}
    listener = socket.socket()
    listener.bind(("127.0.0.1", 0))
    listener.listen(1)
    listener.settimeout(4)
    port = listener.getsockname()[1]
    stop = threading.Event()
    start = time.monotonic()

    def serve():
        try:
            conn, _ = listener.accept()
            with conn:
                record["accept_seconds"] = time.monotonic() - start
                conn.settimeout(3)
                conn.recv(4096)
                conn.sendall(b"HTTP/1.1 200 OK\r\nContent-Length: 2\r\nConnection: close\r\n\r\n")
                if delay is None:
                    stop.wait(3)
                else:
                    stop.wait(delay)
                    conn.sendall(b"OK")
                    record["body_sent_seconds"] = time.monotonic() - start
        except (OSError, TimeoutError) as exc:
            record["server_error"] = type(exc).__name__
        finally:
            listener.close()

    worker = threading.Thread(target=serve)
    worker.start()
    command = [curl, "--connect-timeout", "1", f"http://127.0.0.1:{port}"]
    # Ignore proxy configuration for this loopback-only calibration.
    import os
    env = dict(os.environ, NO_PROXY="127.0.0.1", no_proxy="127.0.0.1")
    try:
        result = subprocess.run(command, capture_output=True, timeout=2, env=env)
        record.update(returncode=result.returncode, watchdog=False,
                      response=result.stdout.decode("utf-8", errors="replace"))
    except subprocess.TimeoutExpired:
        record.update(returncode=None, watchdog=True)
    finally:
        record["elapsed_seconds"] = time.monotonic() - start
        stop.set()
        worker.join(5)
    assert not worker.is_alive()
    return record


def main():
    curl = shutil.which("curl.exe") or shutil.which("curl")
    if not curl:
        raise SystemExit("curl unavailable")
    rows = [trial(curl, case, delay) for case, delay, count in
            [("immediate", 0, 5), ("delayed_body_0.25s", .25, 5),
             ("withheld_body", None, 2)] for _ in range(count)]
    checks = {
        "all_connections_accepted": all("accept_seconds" in r for r in rows),
        "ten_completed_responses": sum(r["returncode"] == 0 and r.get("response") == "OK" for r in rows) == 10,
        "delayed_completion_after_accept": all(r["elapsed_seconds"] - r["accept_seconds"] >= .24 for r in rows if r["case"] == "delayed_body_0.25s"),
        "withheld_body_exceeds_connect_timeout": all(r["watchdog"] and r["elapsed_seconds"] > 1 for r in rows if r["case"] == "withheld_body"),
        "no_server_errors": all("server_error" not in r for r in rows)
    }
    output = {"status": "command-level calibration, no novelty claim", "platform": platform.platform(),
              "curl": subprocess.check_output([curl, "--version"], text=True).splitlines()[0],
              "checks": checks, "trials": rows}
    path = Path(__file__).resolve().parents[1] / "analysis" / "probe-measurement-calibration.json"
    path.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"trials": len(rows), "checks": checks}))
    if not all(checks.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
