import os
from pathlib import Path


def load_env_files(start_file):
    for parent in reversed(Path(start_file).resolve().parents):
        env_path = parent / ".env"
        if not env_path.is_file():
            continue

        for line in env_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue

            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip().strip("\"'")
            if key:
                os.environ.setdefault(key, value)
