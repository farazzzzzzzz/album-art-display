"""Print active music player IDs without exposing the Plex token."""

import xml.etree.ElementTree as ET

from settings import fetch, load_config


def main():
    server, _, _, token = load_config(require_player=False)
    try:
        root = ET.fromstring(fetch(server, token, "/status/sessions"))
    except Exception as error:
        raise SystemExit("Could not read Plex sessions: " + type(error).__name__)

    found = False
    for track in root.findall("Track"):
        player = track.find("Player")
        if player is None:
            continue
        found = True
        print("Player:", player.get("title", "(unnamed)"))
        print("State:", player.get("state", "(unknown)"))
        print("ID:", player.get("machineIdentifier", "(missing)"))
        print()
    if not found:
        print("No music sessions found. Play a track on the intended player and retry.")


if __name__ == "__main__":
    main()
