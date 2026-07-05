# Changelog

## 2026-07-05

- Updated the Frigate base image defaults and documentation from `0.17.1` to `0.17.2`.
- Published and documented the Docker Hub image tags `0.17.2`, `latest`, and `local` for `msorenss79/hailo-frigate-h10`.
- Documented using the versioned Docker Hub tag with `pull_policy: always` and `platform: linux/arm64`.
- Fixed `.env.example` so the RTSP placeholder can be sourced by shell-based checks without Bash interpreting angle brackets as redirection.
- Added a Frigate UI `time_format: 24hour` default/workaround for Swedish locale `Invalid time` rendering.
