import os
import sys
import time

sys.path.insert(0, r"C:\Users\KAHO\Pictures\Starwing\tools\local_launcher")
sys.path.insert(0, r"C:\Users\KAHO\Pictures\Starwing\tools")

from nesys_pipe import NesysPipeServer  # noqa: E402


def main():
    pipe = NesysPipeServer()
    pipe.set_log_callback(lambda m: print(f"[NESYS] {m}"))
    pipe.start()
    print(f"[runner] NESYS pipe started. running={pipe.running}")
    # Keep alive until killed
    try:
        while True:
            time.sleep(1)
            if not pipe.running:
                # restart if it somehow died
                pipe.start()
                print("[runner] pipe restarted")
    except KeyboardInterrupt:
        print("[runner] stopping")
        pipe.stop()


if __name__ == "__main__":
    main()