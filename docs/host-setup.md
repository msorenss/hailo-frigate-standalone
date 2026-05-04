# Host Setup: Raspberry Pi OS Trixie

Target host:

- Raspberry Pi 5
- Hailo-10H AI HAT+/AI HAT+ 2 class device
- Raspberry Pi OS Trixie 64-bit
- Docker Engine with the Docker Compose plugin

## Install OS Packages

Start from a fresh 64-bit Trixie image, then update it:

```bash
sudo apt update
sudo apt full-upgrade
sudo apt install dkms
```

If Hailo packages are available from your configured apt sources for Trixie:

```bash
sudo apt install hailo-all
```

The community forum notes that newer Hailo Raspberry Pi support is Trixie-focused. If `hailo-all` is unavailable, use the Hailo/Raspberry Pi installation instructions that match your Hailo-10H hardware and OS image.

## Verify Hailo Device

Before starting containers, verify the host sees the accelerator:

```bash
lsmod | grep -i hailo
ls -l /dev/h1x-0 /dev/hailo* 2>/dev/null
hailortcli fw-control identify
```

This repo also includes a helper:

```bash
make check-host
```

On this Raspberry Pi OS Trixie / HailoRT 5.3.0 setup, the host device node is `/dev/h1x-0`. [compose.yaml](../compose.yaml) maps it into containers both as `/dev/h1x-0` and as `/dev/hailo0` because the upstream add-on code still checks `/dev/hailo0`.

## HailoRT Package Files

The images expect these package files in their local `packages` directories:

```text
hailort_5.3.0_arm64.deb
hailort-5.3.0-cp311-cp311-linux_aarch64.whl
hailort-5.3.0-cp313-cp313-linux_aarch64.whl
```

Copy them to:

```text
services/frigate-h10/packages/hailort_5.3.0_arm64.deb
services/frigate-h10/packages/hailort-5.3.0-cp311-cp311-linux_aarch64.whl
services/hailo-vlm/packages/hailort_5.3.0_arm64.deb
services/hailo-vlm/packages/hailort-5.3.0-cp313-cp313-linux_aarch64.whl
```

Then run:

```bash
make check-packages
```

The default scaffold version is controlled by `HAILORT_VERSION=5.3.0` in `.env.example` and `.env`.

## Docker Permissions

The compose file maps the host `HAILO_DEVICE` into both containers and aliases it to `/dev/hailo0`. It also adds the capabilities that the Home Assistant add-ons requested through full-access mode.

If a container logs `EPERM` or cannot open `/dev/hailo0`:

1. Confirm the device exists on the host.
2. Confirm the host user can run Docker.
3. Confirm `.env` has `HAILO_DEVICE=/dev/h1x-0` for HailoRT 5.3.0 on Trixie.
4. Add `/dev/hailo_control` mapping if your driver exposes it.
5. As a temporary diagnostic only, test with `privileged: true` on the failing service.

Keep `privileged: true` as a fallback, not the first choice.
