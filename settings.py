"""Local configuration shared by the artwork and screen-power scripts."""

import json
import urllib.request
from pathlib import Path
from urllib.parse import urlsplit

FOLDER = Path(__file__).resolve().parent


def load_config(require_player=True):
    try:
        config = json.loads((FOLDER / "config.json").read_text())
    except FileNotFoundError:
        raise SystemExit("Copy config.example.json to config.json and edit it first.")

    server = config.get("plex_url", "").rstrip("/")
    parsed = urlsplit(server)
    if parsed.scheme not in ("http", "https") or not parsed.netloc or "YOUR_" in server:
        raise SystemExit("Set plex_url in config.json to your Plex server's base URL.")
    if parsed.username or parsed.password or parsed.query or parsed.fragment:
        raise SystemExit("Use a base URL without credentials, a query, or a fragment.")

    player_id = config.get("player_id", "").strip()
    if require_player and (not player_id or player_id == "YOUR_PLAYER_ID"):
        raise SystemExit("Run list-players.py during playback, then set player_id in config.json.")

    delay = config.get("off_delay_seconds", 60)
    if isinstance(delay, bool) or not isinstance(delay, (int, float)) or not 0 <= delay <= 86400:
        raise SystemExit("off_delay_seconds must be a number from 0 to 86400.")

    try:
        token = (FOLDER / "plex-token").read_text().strip()
    except FileNotFoundError:
        raise SystemExit("Create the private plex-token file as described in the README.")
    if not token:
        raise SystemExit("The plex-token file is empty.")

    return server, player_id, delay, token


def fetch(server, token, path):
    # Artwork must be a server-relative path, not an arbitrary external URL.
    parsed = urlsplit(path)
    if parsed.scheme or parsed.netloc or not path.startswith("/"):
        raise ValueError("Expected a Plex server-relative path")
    request = urllib.request.Request(server + path, headers={"X-Plex-Token": token})
    with urllib.request.urlopen(request, timeout=10) as response:
        return response.read()


def selected_track(root, player_id):
    for track in root.findall("Track"):
        player = track.find("Player")
        if player is not None and player.get("machineIdentifier") == player_id:
            return track
    return None
