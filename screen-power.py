"""Use X11 DPMS to blank the screen after confirmed playback inactivity."""

import os
import subprocess
import time
import xml.etree.ElementTree as ET
from pathlib import Path

from settings import fetch, load_config, selected_track


def xset(*args):
    env = dict(os.environ, LC_ALL="C")
    env.setdefault("DISPLAY", ":0")
    env.setdefault("XAUTHORITY", str(Path.home() / ".Xauthority"))
    result = subprocess.run(
        ["/usr/bin/xset", *args], env=env, capture_output=True, text=True, timeout=5
    )
    if result.returncode != 0:
        raise RuntimeError("Display not ready")


def main():
    server, player_id, off_delay, token = load_config()
    idle_since = None
    screen_state = None
    last_error = None

    while True:
        try:
            root = ET.fromstring(fetch(server, token, "/status/sessions"))
            track = selected_track(root, player_id)
            player = track.find("Player") if track is not None else None
            state = (player.get("state") or "").lower() if player is not None else None

            desired = None
            if state == "playing":
                idle_since = None
                desired = True
            else:
                if idle_since is None:
                    idle_since = time.monotonic()
                if time.monotonic() - idle_since >= off_delay:
                    desired = False

            if desired is not None and desired != screen_state:
                xset("+dpms")
                xset("dpms", "0", "0", "0")
                xset("dpms", "force", "on" if desired else "off")
                screen_state = desired
                print("Screen:", "ON" if desired else "OFF", flush=True)
            last_error = None
        except Exception as error:
            # Unknown playback state is not confirmed inactivity. Start a new
            # idle interval after the server/display becomes reachable again.
            idle_since = None
            message = type(error).__name__
            if message != last_error:
                print("Retrying after:", message, flush=True)
                last_error = message
        time.sleep(2)


if __name__ == "__main__":
    main()
