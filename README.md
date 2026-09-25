# Raspberry Pi Album Art Display

A simple album-art screen for my Caldera/Plexamp listening setup: a square HDMI display in a wooden frame, with the current album cover shown fullscreen.

I put this together with AI-assisted coding and a lot of trial and error. I'm not a developer; I'm sharing it because people on Reddit asked how it works. It's an early hobby project, and I'm still learning.

**Status:** adapted from the scripts running on my own Pi. This version moves personal settings into a configuration file and simplifies startup. It has not yet been tested end to end on a fresh Pi. These instructions assume an existing X11 desktop and working Plex/Caldera playback; this is not a complete SD-card image or one-click installer.

## What it does

- Reads the active music sessions from your Plex Media Server.
- Finds the chosen player by its machine identifier.
- Downloads album artwork and displays it in a local Chromium kiosk window.
- Requests screen wake when playback is reported as playing.
- Requests screen blanking after 60 seconds without playback, adjustable in configuration.
- Keeps the last artwork visible during brief errors or missing artwork.

The display code does not play or process audio. [Caldera Music](https://caldera.homes/music/) handles playback in my build, with Plexamp on my phone as the remote. Caldera, Plexamp, and Plex Media Server are separate projects and are not included here.

## My build

| Part | What I use |
| --- | --- |
| Computer | Raspberry Pi 4 |
| Display | Square HDMI screen in a wooden frame |
| Desktop | X11 with Openbox and LightDM |
| Music library | Plex Media Server on my NAS |
| Player | Caldera on the Pi, controlled from Plexamp |
| DAC | HiBy R6 III in USB DAC mode |
| Amplifier | Geshelli headphone amp |
| Headphones | HiFiMAN Edition XS, Sennheiser HD650, and Meze 99 Noir |

The DAC, amplifier, and headphones are just my audio setup; the display scripts do not depend on those particular models. Frame dimensions, a complete parts list, and construction drawings are not included in this first version.

## Requirements

- A Raspberry Pi or similar Linux computer with a working HDMI screen.
- Python 3; the Python scripts use only the standard library.
- Chromium, `xset`, `xrandr`, and `unclutter`.
- A working **X11** desktop session. These screen-control commands are not a Wayland setup.
- The example services assume the display is `:0` and the X authority file is `~/.Xauthority`.
- Network access to your Plex Media Server and a private Plex token that can read its sessions and artwork.
- A music player visible in Plex's active sessions. My setup uses Caldera; other clients are untested.

On Debian-based systems, the packages for this display layer are:

```bash
sudo apt update
sudo apt install python3 chromium x11-xserver-utils unclutter
```

This does not install or configure X11, LightDM, Openbox, automatic desktop login, Caldera, Plex Media Server, or your DAC. Get the desktop and audio playback working first. For unattended startup, the same Linux user must log into the graphical session automatically; configure that separately for your OS.

## Setup

These steps are for installing the shared version. If you already have a working album display, back up its files and service definitions before replacing them, and stop its existing display services before installation.

### 1. Copy the display files

Download this repository using **Code → Download ZIP**, extract it on the Pi, and open a terminal inside the extracted folder containing this README. Run the following as your normal desktop user, not as root:

```bash
mkdir -p "$HOME/.config/album-display"
cp index.html update.py screen-power.py settings.py list-players.py start-browser.sh config.example.json "$HOME/.config/album-display/"
```

Create your local configuration if it does not already exist:

```bash
test -e "$HOME/.config/album-display/config.json" || cp config.example.json "$HOME/.config/album-display/config.json"
nano "$HOME/.config/album-display/config.json"
```

Replace `YOUR_PLEX_SERVER_IP` with your server's address. Keep the `http://` prefix and `:32400` port unless your server uses a different connection. Leave `YOUR_PLAYER_ID` for now. Save in nano with **Ctrl+O**, **Enter**, then **Ctrl+X**.

Use a trusted local network for an HTTP connection; HTTP does not encrypt your token. For HTTPS, use a hostname and certificate your Pi can verify.

### 2. Save your Plex token privately

See Plex's official [authentication-token instructions](https://support.plex.tv/articles/204059436-finding-an-authentication-token-x-plex-token/). Plex describes that method as providing a temporary token; you may need to replace it if authentication stops working. This project does not implement an account sign-in flow.

Paste only the token value into the hidden prompt below. The token is saved locally with owner-only permissions and is not placed in the command itself:

```bash
python3 -c 'import getpass, os; from pathlib import Path; os.umask(0o077); p = Path.home() / ".config/album-display/plex-token"; token = getpass.getpass("Plex token (hidden): ").strip(); p.write_text(token); p.chmod(0o600)'
```

Never upload `plex-token`, your real `config.json`, browser profiles, or copied session XML to GitHub. The included `.gitignore` helps with Git workflows, but manually selected browser uploads must still be checked.

### 3. Find your player

Start playing music on the intended player, then run:

```bash
python3 "$HOME/.config/album-display/list-players.py"
```

Copy the ID for that player into the `player_id` field in `~/.config/album-display/config.json`. Both artwork and screen power use this exact ID. If you reinstall or replace your player, check whether its ID changed.

### 4. Check artwork retrieval

While music is playing, run:

```bash
python3 "$HOME/.config/album-display/update.py"
```

Look for `Updated album artwork` and a newly created `cover.jpg` in the display folder. Press **Ctrl+C** to stop the foreground script before starting the service.

### 5. Configure the desktop

For Openbox, merge the commands from `openbox/autostart.example` into `~/.config/openbox/autostart`, preserving unrelated commands.

The shared setup uses systemd to launch Chromium and unclutter. If an older Openbox autostart file already launches either one, remove only those duplicate launch lines. Do not run both startup methods together.

Rotation is optional. In an X11 terminal, run `xrandr` to find your connected output. The original frame uses `HDMI-1` with `--rotate inverted`; adapt or omit the commented rotation line in the example. Display names vary.

The autostart changes take effect at your next graphical login. You can run its three `xset` lines manually in an X11 terminal for the current session.

### 6. Start the services

From the extracted repository folder:

```bash
mkdir -p "$HOME/.config/systemd/user"
cp systemd/album-*.service "$HOME/.config/systemd/user/"
systemctl --user daemon-reload
systemctl --user enable --now album-display.service album-kiosk.service album-screen-power.service album-unclutter.service
```

The kiosk service waits for the X display before launching Chromium. The services run under your user account; do not use `sudo systemctl` for these units. A working graphical login is still required.

## Appearance and screen behavior

Edit `~/.config/album-display/index.html` to change the CSS variables near the top:

| Setting | Default | Purpose |
| --- | --- | --- |
| `--art-size` | `95%` | Artwork size within the screen |
| `--art-left` | `calc(51% - 11px)` | Horizontal placement from the original frame |
| `--art-top` | `calc(50% + 5px)` | Vertical placement from the original frame |
| `--art-brightness` | `0.80` | Software dimming; `1` leaves artwork undimmed |

Use `50%` for both position values to center the artwork. The brightness setting changes image rendering, not the physical backlight. Reload Chromium after changing the HTML:

```bash
systemctl --user restart album-kiosk.service
```

Edit `off_delay_seconds` in your local `config.json` to change the inactivity timeout, then restart the screen-power service. Artwork is polled every 3 seconds; screen state every 2 seconds. Wake is not guaranteed to be instantaneous because it also depends on server and display response times.

## Troubleshooting

View service state and recent logs:

```bash
systemctl --user status album-display album-kiosk album-screen-power album-unclutter --no-pager
journalctl --user -u album-display -u album-kiosk -u album-screen-power -n 80 --no-pager
```

- **No artwork:** check the server address, token, player ID, and that music is playing. Run `list-players.py` again. A black screen is expected before the first successful artwork download.
- **Wrong or old artwork:** both scripts select the exact configured player ID. Missing artwork retains the previous cover. Updated artwork at the same Plex artwork path is not fetched again until the updater restarts or a different artwork path is selected.
- **`HTTPError`:** check the token and server access. Detailed request URLs are intentionally not logged.
- **Kiosk will not start:** check that X11 is running on `:0`, the same user's X authority file is `~/.Xauthority`, and Chromium is installed at `/usr/bin/chromium`. Adjust the service environment and browser script for your system. The GPU flags came from my Pi and may need adjustment on other hardware.
- **Two browsers or repeated restarts:** check for a duplicate launch in Openbox autostart, another service, or a manually launched kiosk.
- **Screen will not blank:** `xset` DPMS support depends on the driver and screen. A black image or HDMI standby may not turn off the physical backlight, and some screens show a no-signal message.
- **Network failure:** the last image and requested screen state are retained. The inactivity timer resets after an error and starts again on successful idle polls.
- **Screen wakes by itself:** input activity or another desktop power manager can override DPMS. This simple script tracks its own last request; it does not continually verify the physical screen state.

To stop and disable the display layer:

```bash
systemctl --user disable --now album-screen-power album-unclutter album-kiosk album-display
```

## Files

| File | Purpose |
| --- | --- |
| `index.html` | Fullscreen artwork page |
| `update.py` | Retrieves current album artwork |
| `screen-power.py` | Controls X11 screen blanking/wake |
| `settings.py` | Loads private settings and makes Plex requests |
| `list-players.py` | Lists active music players for configuration |
| `config.example.json` | Settings template without personal values |
| `start-browser.sh` | Chromium kiosk launcher |
| `systemd/` | User service examples |
| `openbox/autostart.example` | Desktop rotation and screen-saver settings |
| `.gitignore` | Excludes local secrets, artwork, and browser data from normal Git adds |

Album artwork is fetched from your own Plex library; no artwork is distributed here. This project is independent of Plex and Caldera. Thanks to Elan for Caldera, which made the playback side of this build possible.
