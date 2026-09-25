"""Poll Plex sessions and save the selected player's album artwork."""

import time
import xml.etree.ElementTree as ET

from settings import FOLDER, fetch, load_config, selected_track


def main():
    server, player_id, _, token = load_config()
    last_artwork = None
    last_error = None

    while True:
        try:
            root = ET.fromstring(fetch(server, token, "/status/sessions"))
            track = selected_track(root, player_id)
            if track is not None:
                artwork = track.get("parentThumb") or track.get("thumb")
                if artwork and artwork != last_artwork:
                    image = fetch(server, token, artwork)
                    temporary = FOLDER / "cover.tmp"
                    temporary.write_bytes(image)
                    temporary.replace(FOLDER / "cover.jpg")
                    last_artwork = artwork
                    print("Updated album artwork", flush=True)
            last_error = None
        except Exception as error:
            # Do not log request URLs or credentials.
            message = type(error).__name__
            if message != last_error:
                print("Retrying after:", message, flush=True)
                last_error = message
        time.sleep(3)


if __name__ == "__main__":
    main()
