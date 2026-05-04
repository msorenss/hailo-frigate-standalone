#!/usr/bin/env bash
set -euo pipefail

ok() { printf 'OK: %s\n' "$*"; }
warn() { printf 'WARN: %s\n' "$*" >&2; }
fail() { printf 'FAIL: %s\n' "$*" >&2; exit 1; }

arch="$(uname -m)"
if [[ "$arch" == "aarch64" || "$arch" == "arm64" ]]; then
  ok "64-bit ARM host detected ($arch)"
else
  warn "Expected aarch64/arm64 for Raspberry Pi 5; got $arch"
fi

if [[ -r /etc/os-release ]]; then
  . /etc/os-release
  ok "OS: ${PRETTY_NAME:-unknown}"
  if [[ "${VERSION_CODENAME:-}" != "trixie" ]]; then
    warn "Target baseline is Raspberry Pi OS/Debian Trixie; detected codename '${VERSION_CODENAME:-unknown}'"
  fi
fi

if command -v docker >/dev/null 2>&1; then
  ok "docker found: $(docker --version)"
else
  fail "docker is not installed"
fi

if docker compose version >/dev/null 2>&1; then
  ok "docker compose found: $(docker compose version --short)"
else
  fail "docker compose plugin is not available"
fi

if lsmod | grep -qi hailo; then
  ok "Hailo kernel module appears loaded"
else
  warn "No Hailo kernel module found in lsmod"
fi

hailo_device="${HAILO_DEVICE:-/dev/h1x-0}"
if [[ -e "$hailo_device" ]]; then
  ok "$hailo_device exists"
  if [[ -r "$hailo_device" || -w "$hailo_device" ]]; then
    ok "$hailo_device has user-visible permissions"
  else
    warn "$hailo_device exists but current user may not have access"
  fi
else
  fail "$hailo_device not found; install/verify Hailo-10H driver and firmware first"
fi

if [[ -e /dev/hailo_control ]]; then
  ok "/dev/hailo_control exists; consider mapping it in compose.yaml if required"
fi

if command -v hailortcli >/dev/null 2>&1; then
  ok "hailortcli found"
  hailortcli fw-control identify || warn "hailortcli identify failed"
else
  warn "hailortcli not found on host; this can be okay if runtime is only inside containers"
fi

if compgen -G '/dev/video*' >/dev/null; then
  ok "Video devices: $(ls /dev/video* | tr '\n' ' ')"
else
  warn "No /dev/video* devices found; RTSP cameras do not need this"
fi
