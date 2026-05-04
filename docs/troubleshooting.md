# Troubleshooting

## Hailo Device Node Is Missing

Check the host first:

```bash
lsmod | grep -i hailo
ls -l /dev/h1x-0 /dev/hailo* 2>/dev/null
hailortcli fw-control identify
```

On this Trixie/HailoRT 5.3.0 host the real device node is `/dev/h1x-0`. The compose file maps that node into containers as `/dev/hailo0` for compatibility with the upstream add-on checks. If the host node is missing, fix the Pi OS driver/firmware installation before debugging Docker.

## Container Cannot Open `/dev/hailo0`

Symptoms usually mention `EPERM`, permission denied, or HailoRT failing to create a device.

Try these in order:

1. Run `make check-host` on the Pi.
2. Confirm `.env` has `HAILO_DEVICE=/dev/h1x-0`.
3. Confirm [compose.yaml](../compose.yaml) maps that device into the failing service and aliases it to `/dev/hailo0`.
4. If the host has `/dev/hailo_control`, map it into both services.
5. Confirm `cap_add` includes `SYS_RAWIO` for VLM and `SYS_RAWIO` plus `PERFMON` for Frigate.
6. Temporarily test `privileged: true` on the failing service. If that fixes it, narrow the needed device/capability mapping afterward.

## Missing HailoRT Package Files

Run:

```bash
make check-packages
```

Both service build contexts need:

```text
hailort_5.3.0_arm64.deb
hailort-5.3.0-cp311-cp311-linux_aarch64.whl
hailort-5.3.0-cp313-cp313-linux_aarch64.whl
```

The files are ignored by git on purpose.

## Python Wheel Mismatch

The expected HailoRT wheel is `cp311`, matching Python 3.11. If the base image changes Python versions, the wheel install will fail. Keep the current base images for the first milestone.

## Frigate Uses Old HailoRT CLI

The upstream Frigate image includes `/usr/local/bin/hailortcli` from HailoRT 4.x, and `/usr/local/bin` appears before `/usr/bin` in `PATH`. The Frigate Dockerfile removes that stale binary and symlinks `/usr/local/bin/hailortcli` to the HailoRT 5.3.0 CLI installed by the `.deb` package.

Verify the rebuilt image with:

```bash
sudo docker exec frigate-h10 sh -c 'hailortcli --version && hailortcli fw-control identify'
```

Expected version is `5.3.0` and expected architecture is `HAILO10H`.

## Frigate API Returns 500 During Startup

If `/api/version` returns nginx `500` and logs show auth upstream failures for `127.0.0.1:5001`, check whether Frigate is blocked probing an unreachable RTSP URL. Test the RTSP URL from the Pi before enabling the camera in Frigate.

If logs show `KeyError: 'FRIGATE_CAMERA_RTSP_URL'`, recreate the container instead of only restarting it:

```bash
sudo docker compose --env-file .env -f compose.yaml up -d --force-recreate frigate-h10
```

`docker compose restart` does not inject newly added environment variables into an existing container.

## Frigate Patch Fails During Build

The patch is written against Frigate 0.17.0. If you change `FRIGATE_IMAGE`, the target detector plugin may have changed and the patch can fail intentionally. Re-test and update [services/frigate-h10/hailo10h_patch.py](../services/frigate-h10/hailo10h_patch.py) before upgrading Frigate.

## VLM Build Cannot Clone Upstream

The VLM Dockerfile fetches the upstream app at build time. If the Pi has no internet access, clone `mikehailodev/hailo-vlm-addon` separately and adjust the Dockerfile to copy local app files instead.

## RTSP Stream Is Blank

1. Test the RTSP URL from the Pi host with `ffprobe`, `ffmpeg`, or VLC.
2. Prefer TCP RTSP transport where possible.
3. Check camera credentials and stream path.
4. Inspect logs with `make logs`.

## Frigate and VLM Cannot Run Together

Frigate must use the patched detector code with `params.group_id = "SHARED"`. Confirm the Frigate image was rebuilt after patch changes:

```bash
docker compose --env-file .env -f compose.yaml build --no-cache frigate-h10
```

Then start both services and inspect logs:

```bash
make up
make logs
```
