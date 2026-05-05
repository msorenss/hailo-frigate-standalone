# Standalone Hailo-10H Frigate + VLM on Raspberry Pi 5

This repo is a standalone Docker Compose scaffold for running these workloads on a Raspberry Pi 5 with a Hailo-10H AI accelerator:

- Frigate 0.17.1 with the community Hailo-10H detector patch.
- Hailo VLM Chat as a separate web/API service.
- MQTT integration back to Home Assistant running on another machine.

It is based on research from:

- https://community.hailo.ai/t/hailo-10h-on-home-assistant-edge-ai-home-automation/19082
- https://github.com/mikehailodev/frigate-hass-addons-h10
- https://github.com/mikehailodev/hailo-vlm-addon

## Credits

This standalone project builds on community work by [mikehailodev/frigate-hass-addons-h10](https://github.com/mikehailodev/frigate-hass-addons-h10), [mikehailodev/hailo-vlm-addon](https://github.com/mikehailodev/hailo-vlm-addon), and the upstream [Frigate](https://github.com/blakeblackshear/frigate) project.

See [LICENSES.md](LICENSES.md) for attribution and licensing notes.

## Target Architecture

```text
Cameras -> Raspberry Pi 5 + Hailo-10H
             |-- Frigate H10 container -> MQTT -> Home Assistant host
             |-- Hailo VLM Chat container -> http://<pi>:8099
```

The Frigate detector type remains `hailo8l`. That is intentional: the patched Frigate plugin auto-detects Hailo-10H hardware while keeping the existing Frigate config key.

## Current Tested State

This scaffold has been built and smoke-tested on a Raspberry Pi 5 running Debian/Raspberry Pi OS Trixie with HailoRT 5.3.0 and a Hailo-10H device exposed as `/dev/h1x-0`.

Verified locally:

- Frigate image builds from `ghcr.io/blakeblackshear/frigate:0.17.1`.
- Frigate reports `0.17.1-416a9b7` on `/api/version`.
- Frigate sees the Hailo-10H with `hailortcli fw-control identify`.
- VLM starts on port `8099` and reports `hailo_available=true` and `hailo_device=true`.

The VLM service still needs a real camera source and a VLM HEF model before it can do useful image-language inference.

## Quick Start

1. Prepare the Pi host with Raspberry Pi OS Trixie 64-bit and a working Hailo-10H driver/runtime. See [docs/host-setup.md](docs/host-setup.md).
2. Copy the editable local configuration files:

```bash
cp .env.example .env
cp config/frigate/config.yml.example config/frigate/config.yml
cp config/vlm/options.json.example config/vlm/options.json
```

3. Place the required HailoRT package files in the service package directories:
   - `services/frigate-h10/packages/`: `hailort_5.3.0_arm64.deb` and `hailort-5.3.0-cp311-cp311-linux_aarch64.whl`
   - `services/hailo-vlm/packages/`: `hailort_5.3.0_arm64.deb` and `hailort-5.3.0-cp313-cp313-linux_aarch64.whl`
4. Adjust `.env`, `config/frigate/config.yml`, and `config/vlm/options.json`. These local files are ignored by git. Put camera credentials only in `.env`.
5. Place a Hailo-10H VLM HEF model, for example `Qwen2-VL-2B-Instruct.hef`, in `models/vlm/`. See [docs/vlm.md](docs/vlm.md).
6. Run the checks:

```bash
make check-host
make check-packages
```

7. Build and start:

```bash
make build
make up
make logs
```

Frigate will be available on `http://<pi>:5000` by default. Hailo VLM Chat will be available on `http://<pi>:8099`.

## Camera Configuration

Copy [config/frigate/config.yml.example](config/frigate/config.yml.example) to `config/frigate/config.yml` and adjust it for your camera. The generated `config/frigate/config.yml` is ignored by git. The RTSP URL is read from the `FRIGATE_CAMERA_RTSP_URL` environment variable so credentials stay in `.env`.

```yaml
cameras:
   camera_1:
      enabled: true
      ffmpeg:
         inputs:
            - path: "{FRIGATE_CAMERA_RTSP_URL}"
               roles:
                  - detect
                  - record
      detect:
         enabled: true
         width: 1280
         height: 720
         fps: 5
```

Set the actual URL in `.env`:

```dotenv
FRIGATE_CAMERA_RTSP_URL=rtsp://<url-encoded-user>:<url-encoded-password>@<camera-ip>:554/<stream>
```

If your username or password contains special URL characters, URL-encode them before putting them in the RTSP URL. For example, `@` becomes `%40`. Set `detect.width` and `detect.height` to match the stream you use.

Useful common RTSP paths to try if the current one fails:

```text
/stream1
/stream2
/live/ch0
/live/ch1
/h264Preview_01_main
/h264Preview_01_sub
```

Example retention for a one-camera setup:

```yaml
record:
   enabled: true
   detections:
      pre_capture: 5
      post_capture: 5
      retain:
         days: 1
         mode: active_objects

snapshots:
   enabled: true
   timestamp: true
   bounding_box: true
   crop: false
   retain:
      default: 1
      objects:
         person: 1
         car: 1
```

After changing `.env`, recreate Frigate so Compose injects the new environment variable:

```bash
sudo docker compose --env-file .env -f compose.yaml up -d --force-recreate frigate-h10
```

Then check:

```bash
curl http://127.0.0.1:5000/api/version
sudo docker compose --env-file .env -f compose.yaml ps frigate-h10
```

## Hailo-10H Frigate Details

The Frigate detector type remains `hailo8l` by design:

```yaml
detectors:
   hailo8l:
      type: hailo8l
      device: PCIe
```

The patched plugin auto-detects `HAILO10H`, selects Hailo-10H-compatible defaults, and sets the shared VDevice group so Frigate and VLM can use the accelerator at the same time.

The Frigate image also removes the old `/usr/local/bin/hailortcli` from the upstream base image and links it to the HailoRT 5.3.0 CLI installed from the local `.deb`. Verify with:

```bash
sudo docker exec frigate-h10 sh -c 'hailortcli --version && hailortcli fw-control identify'
```

Expected output includes `HailoRT-CLI version 5.3.0` and `Device Architecture: HAILO10H`.

## Required HailoRT Packages

The Dockerfiles expect these files across the two service package directories:

```text
hailort_5.3.0_arm64.deb
hailort-5.3.0-cp311-cp311-linux_aarch64.whl
hailort-5.3.0-cp313-cp313-linux_aarch64.whl
```

They are not committed here. Copy the `.deb` into both service package folders, the `cp311` wheel into the Frigate package folder, and the `cp313` wheel into the VLM package folder. This keeps the repo small and avoids bundling licensed binary artifacts.

## Important Files

- [compose.yaml](compose.yaml) - Docker Compose deployment for both services.
- [services/frigate-h10/Dockerfile](services/frigate-h10/Dockerfile) - Frigate image with HailoRT 5.3.0 package replacement.
- [services/frigate-h10/hailo10h_patch.py](services/frigate-h10/hailo10h_patch.py) - Hailo-10H detector patch and shared VDevice group.
- [services/hailo-vlm/Dockerfile](services/hailo-vlm/Dockerfile) - VLM image that pulls the upstream app files at build time.
- [config/frigate/config.yml.example](config/frigate/config.yml.example) - Frigate config template.
- [config/vlm/options.json.example](config/vlm/options.json.example) - VLM options template.

## Notes

The first milestone is to reproduce the community add-on runtime outside Home Assistant Supervisor. After that works, upgrading Frigate or HailoRT should be handled separately and tested carefully.
