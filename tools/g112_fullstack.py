"""g112_fullstack.py - single entry point: boot every mock-server component and
then run the g79 keepalive (launch game + patch everything + drive-rewire).

Components (identical to local_launcher):
  1. Python HTTP   :4001  uvicorn app.main:app
  2. HTTP Proxy    :80    tools/g30_proxy.py
  3. TCP Matching  :6666  server -m app.tcp_server
  4. NESYS pipe           local_launcher/run_nesys_pipe_cli.py (if pipe is free)

Usage:
  python g112_fullstack.py            full stack + g79 keepalive (game launches)
  python g112_fullstack.py --server-only  start the servers only, block until
                                       Ctrl+C; never launches the game (used by
                                       server\\start_server.bat)

Ctrl+C terminates the server children and exits.
"""
from __future__ import annotations

import contextlib
import os
import socket
import subprocess
import sys
import time

PROJECT_ROOT = r"C:\Users\KAHO\Pictures\Starwing"
TOOLS = os.path.join(PROJECT_ROOT, "tools")
VENV_PY = os.path.join(PROJECT_ROOT, "server", ".venv", "Scripts", "python.exe")
SYS_PY = r"C:\Users\KAHO\AppData\Local\Programs\Python\Python310\python.exe"
PIPE_NAME = r"\\.\pipe\nesys_games"

COMPONENTS = [
    (4001, "http-uvicorn",
     [VENV_PY, "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "4001"],
     os.path.join(PROJECT_ROOT, "server")),
    (80   , "http-proxy",
     [VENV_PY, os.path.join(TOOLS, "g30_proxy.py")],
     PROJECT_ROOT),
    (6666 , "tcp-matching",
     [VENV_PY, "-m", "app.tcp_server"],
     os.path.join(PROJECT_ROOT, "server")),
]


def port_free(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.5)
        return s.connect_ex(("127.0.0.1", port)) != 0


def main():
    children = []
    server_only = "--server-only" in sys.argv
    try:
        for port, name, cmd, cwd in COMPONENTS:
            if not port_free(port):
                print("[%s] port %d already in use - skipped" % (name, port))
                continue
            proc = subprocess.Popen(cmd, cwd=cwd, stdout=subprocess.DEVNULL,
                                    stderr=subprocess.STDOUT,
                                    creationflags=getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0))
            children.append(proc)
            print("[%s] started PID %d" % (name, proc.pid))

        if not os.path.exists(PIPE_NAME):
            proc = subprocess.Popen(
                [SYS_PY, os.path.join(TOOLS, "local_launcher", "run_nesys_pipe_cli.py")],
                stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT, cwd=TOOLS,
                creationflags=getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0))
            children.append(proc)
            print("[nesys-pipe] started PID %d" % proc.pid)
        else:
            print("[nesys-pipe] already running - skipped")

        if server_only:
            print("==> server-only mode: blocking (Ctrl+C to stop all %d child(ren))" % len(children))
            try:
                for proc in children:
                    proc.wait()
            except KeyboardInterrupt:
                pass
            finally:
                pass
        else:
            print("==> running g79 keepalive (Ctrl+C to stop everything)")
            sys.path.insert(0, TOOLS)
            import g79_allfix_keepalive as g79
            g79.main()
    except KeyboardInterrupt:
        print("==> stopping %d server child(ren)..." % len(children))
    finally:
        for proc in children:
            with contextlib.suppress(Exception):
                proc.terminate()
        time.sleep(1)
        for proc in children:
            with contextlib.suppress(Exception):
                if proc.poll() is None:
                    proc.kill()
    print("done.")


if __name__ == "__main__":
    main()