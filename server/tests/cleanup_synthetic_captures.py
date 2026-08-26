"""Cleanup utility for synthetic capture validation tests.

Removes any files created during SYNTHETIC_CAPTURE_TEST runs.
Safe to run multiple times.
"""

import tempfile
from pathlib import Path


def cleanup_synthetic_captures():
    """Remove synthetic capture files from temp directories."""
    # Clean up any temp directories that might contain captures
    temp_dir = Path(tempfile.gettempdir())
    cleaned = 0

    for d in temp_dir.iterdir():
        if d.is_dir() and "tmp" in d.name.lower():
            for f in d.glob("capture_*.meta.json"):
                f.unlink(missing_ok=True)
                cleaned += 1
            for f in d.glob("capture_*.req.bin"):
                f.unlink(missing_ok=True)
                cleaned += 1
            for f in d.glob("capture_*.resp.bin"):
                f.unlink(missing_ok=True)
                cleaned += 1
            # Remove empty temp dirs
            try:
                if not any(d.iterdir()):
                    d.rmdir()
            except OSError:
                pass

    return cleaned


if __name__ == "__main__":
    count = cleanup_synthetic_captures()
    print(f"Cleaned up {count} synthetic capture files")
