#!/usr/bin/env python3
"""Build script for creating linux_tts_player.ankiaddon archive."""

import os
import zipfile

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_ZIP = os.path.join(SCRIPT_DIR, "linux_tts_player.ankiaddon")

INCLUDE_FILES = [
    "__init__.py",
    "manifest.json",
    "config.json",
    "config.md",
    "voices.json",
    "LICENSE",
]

INCLUDE_DIRS = [
    "vendor",
]

EXCLUDE_PATTERNS = [
    "__pycache__",
    ".git",
    ".pytest_cache",
    ".DS_Store",
    ".pyc",
    "user_files/cache",
    "user_files/debug.log",
]


def should_exclude(rel_path: str) -> bool:
    for pat in EXCLUDE_PATTERNS:
        if pat in rel_path.split(os.sep) or rel_path.endswith(pat):
            return True
    return False


def build_package():
    if os.path.exists(OUTPUT_ZIP):
        os.remove(OUTPUT_ZIP)

    print(f"Building: {OUTPUT_ZIP}")
    with zipfile.ZipFile(OUTPUT_ZIP, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        # 1. Top-level files
        for fname in INCLUDE_FILES:
            fpath = os.path.join(SCRIPT_DIR, fname)
            if os.path.exists(fpath):
                print(f"  Adding file: {fname}")
                zf.write(fpath, arcname=fname)
            else:
                print(f"  WARNING: missing {fname}")

        # 2. Directories
        for dname in INCLUDE_DIRS:
            dpath = os.path.join(SCRIPT_DIR, dname)
            for root, dirs, files in os.walk(dpath):
                for f in files:
                    full_path = os.path.join(root, f)
                    rel_path = os.path.relpath(full_path, SCRIPT_DIR)
                    if not should_exclude(rel_path):
                        zf.write(full_path, arcname=rel_path)

        # 3. Add empty user_files/.keep
        zf.writestr("user_files/.keep", "")

    size_mb = os.path.getsize(OUTPUT_ZIP) / (1024 * 1024)
    print(f"Package created successfully: {size_mb:.2f} MB -> {OUTPUT_ZIP}")


if __name__ == "__main__":
    build_package()
