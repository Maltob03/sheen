# Codeshot

Turn code into images styled with the color themes that ship with Xcode. Runs entirely in the browser, packaged as a Docker image and as an umbrelOS community app store.

## What's in this repo

| Path | What it is |
| --- | --- |
| `src/codeshot.html` | The app source (one file, Xcode theme colors embedded) |
| `src/build.py` | Builds `app/index.html` from the source for self-hosting |
| `app/` | The files the container serves, with highlight.js bundled so it works offline |
| `Dockerfile`, `nginx.conf` | The image: nginx running as a non-root user on port 8080 |
| `umbrel-app-store.yml` | Makes this repo an umbrelOS community app store with the id `maltob` |
| `maltob-codeshot/` | The Umbrel app: manifest and compose file |

## Run it on umbrelOS (private repo)

This repo is private, so the simplest route is to build the image on the Umbrel itself. No registry is involved, and the image is built for the Umbrel's own CPU (Intel or Raspberry Pi).

1. SSH into the Umbrel (the password is your Umbrel password):

   ```bash
   ssh umbrel@umbrel.local
   ```

2. Clone the repo. When asked for a password, use a GitHub personal access token with read access to this repo:

   ```bash
   git clone https://github.com/Maltob03/codeshot.git
   cd codeshot
   ```

   If `git` isn't available on the Umbrel, download the repo as a ZIP from GitHub on your Mac, then copy it over with `scp codeshot-main.zip umbrel@umbrel.local:` and unzip it there.

3. Build and start it. It restarts automatically when the Umbrel reboots:

   ```bash
   sudo docker build -t codeshot:1.0.0 .
   sudo docker run -d --name codeshot --restart unless-stopped -p 8473:8080 codeshot:1.0.0
   ```

Open `http://umbrel.local:8473`. Unlike an App Store app, it doesn't sit behind the Umbrel login and doesn't show up on the Umbrel home screen.

To update later: `git pull`, build again, then `sudo docker rm -f codeshot` and run the `docker run` line again.

## Install from the Umbrel App Store (needs public access)

The `umbrel-app-store.yml` and `maltob-codeshot/` files let Umbrel add this repo as a community app store, so Codeshot gets a home-screen icon and the Umbrel login. That route needs Umbrel to reach both the repo and the image without credentials:

1. Make the repo public.
2. Build the image for Intel and ARM and push it to a registry, for example from a Mac with Docker installed:
   `docker buildx build --platform linux/amd64,linux/arm64 -t ghcr.io/maltob03/codeshot:1.0.0 --push .`
3. Make the package public: GitHub profile → **Packages** → **codeshot** → **Package settings** → **Change visibility**.
4. On the Umbrel: **App Store** → **⋯** → **Community App Stores**, paste `https://github.com/Maltob03/codeshot`, then install **Codeshot** from **Maltob App Store**. It opens at `http://umbrel.local:8473`.

## Release an update

1. Edit `src/codeshot.html`, then run `python3 src/build.py`.
2. Bump `version` (and `releaseNotes`) in `maltob-codeshot/umbrel-app.yml` and the image tag in `maltob-codeshot/docker-compose.yml`.
3. Commit and push, then on the Umbrel pull and rebuild as described above.

## Run it anywhere with Docker

```bash
docker build -t codeshot .
docker run --rm -p 8473:8080 codeshot
```

Then open http://localhost:8473.

## Notes

- **Copy image** needs an HTTPS address, so on `http://umbrel.local` it asks you to use Export PNG instead. Export PNG, Export SVG and Copy code work over plain HTTP.
- The code font is the system's SF Mono, so images look most like Xcode when exported from a Mac.
- Settings and imported themes are saved in your browser, per device.
