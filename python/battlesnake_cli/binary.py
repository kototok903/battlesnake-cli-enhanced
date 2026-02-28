"""Battlesnake binary download and setup."""

from __future__ import annotations

import json
import os
import platform
import subprocess as sp
import sys
import tarfile
import urllib.request
from pathlib import Path

from .config import BIN_DIR


def download_battlesnake() -> Path | None:
    """Download battlesnake binary to .bin folder. Returns path or None."""
    system = platform.system()
    machine = platform.machine()

    arch_map = {"AMD64": "x86_64", "aarch64": "arm64"}
    arch = arch_map.get(machine, machine)

    binary_name = "battlesnake.exe" if system == "Windows" else "battlesnake"

    # Query GitHub API for latest release
    api_url = "https://api.github.com/repos/BattlesnakeOfficial/rules/releases/latest"
    try:
        with urllib.request.urlopen(api_url) as response:
            release = json.loads(response.read().decode())
    except Exception as e:
        print(f"Failed to query GitHub API: {e}")
        return None

    # Find matching asset (pattern: battlesnake_VERSION_SYSTEM_ARCH.tar.gz)
    search_suffix = f"_{system}_{arch}.tar.gz"
    download_url = None
    filename = None
    for asset in release.get("assets", []):
        if asset["name"].endswith(search_suffix):
            download_url = asset["browser_download_url"]
            filename = asset["name"]
            break

    if not download_url:
        print(f"No release found for {system}_{arch}")
        return None

    BIN_DIR.mkdir(parents=True, exist_ok=True)
    archive_path = BIN_DIR / filename
    binary_path = BIN_DIR / binary_name

    try:
        print(f"Downloading {filename}...")
        urllib.request.urlretrieve(download_url, archive_path)

        print("Extracting...")
        with tarfile.open(archive_path, "r:gz") as t:
            t.extract(binary_name, BIN_DIR)

        os.chmod(binary_path, 0o755)
        archive_path.unlink()
        return binary_path

    except Exception as e:
        print(f"Failed to download battlesnake: {e}")
        return None


def setup_battlesnake() -> Path:
    """Find or install battlesnake. Returns path or exits."""
    # Check Go installation
    try:
        gopath = sp.check_output(["go", "env", "GOPATH"], text=True).strip()
        go_bin = Path(gopath) / "bin" / "battlesnake"
        if go_bin.is_file():
            print(f"Battlesnake Go package detected at {go_bin}")
            return go_bin
    except (sp.CalledProcessError, FileNotFoundError):
        pass

    # Check local .bin
    local_bin = BIN_DIR / "battlesnake"
    if local_bin.is_file():
        print("Battlesnake binary detected in .bin/")
        return local_bin

    # Need to install
    print("Battlesnake CLI not found. Installing...")
    path = download_battlesnake()
    if path:
        print(f"Battlesnake installed to {path}")
        return path
    else:
        print("Could not install battlesnake. Please install manually:")
        print("  go install github.com/BattlesnakeOfficial/rules/cli/battlesnake@latest")
        print("Or download into .bin folder from: https://github.com/BattlesnakeOfficial/rules/releases")
        sys.exit(1)
