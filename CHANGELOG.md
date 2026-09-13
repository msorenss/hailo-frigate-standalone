# Changelog

## 2026-09-13

- Updated Frigate Hailo-10H build defaults to the stable `0.18.0-standard-arm64` release, keeping HailoRT 5.3.0.
- Updated upgrade documentation and Docker Hub release references to `0.18.0` and `latest` for `msorenss79/hailo-frigate-h10`.
- Corrected the image source label to this repository and added the `0.18.0` version label.

## 2026-09-07

- Updated Frigate Hailo-10H build defaults and upgrade documentation to `0.18.0-rc2-standard-arm64`.
- Prepared the Docker Hub release tag `0.18.0-rc2` and `latest` for `msorenss79/hailo-frigate-h10`.

## 2026-09-05

- Updated Frigate Hailo-10H build defaults and upgrade documentation to `0.18.0-rc1-standard-arm64`.
- Docker Hub release tags: `0.18.0-rc1` and `latest` for `msorenss79/hailo-frigate-h10`.

## 2026-08-11

- Updated the Frigate Hailo-10H build defaults to `ghcr.io/blakeblackshear/frigate:0.18.0-beta3-standard-arm64`.
- Published Docker Hub tags `0.18.0-beta3` and `latest` for `msorenss79/hailo-frigate-h10`.

## 2026-08-06

- Updated the Frigate Hailo-10H build defaults to `ghcr.io/blakeblackshear/frigate:0.18.0-beta2-standard-arm64`.
- Published Docker Hub tags `0.18.0-beta2` and `latest` for `msorenss79/hailo-frigate-h10`.

## 2026-07-13

- Switched the Frigate Hailo-10H build defaults to `ghcr.io/blakeblackshear/frigate:0.18.0-beta1-standard-arm64` for beta testing.
- Published Docker Hub tags `0.18.0-beta1` and `latest` for `msorenss79/hailo-frigate-h10`; both point at the same beta image digest.
- Removed the 0.17-era `ui.time_format` example because Frigate 0.18 removes `ui.date_format` and `ui.time_format`.
- Documented backing up Frigate config and database files before running the 0.18 beta migration.

## 2026-07-05

- Updated the Frigate base image defaults and documentation from `0.17.1` to `0.17.2`.
- Published and documented the Docker Hub image tags `0.17.2`, `latest`, and `local` for `msorenss79/hailo-frigate-h10`.
- Documented using the versioned Docker Hub tag with `pull_policy: always` and `platform: linux/arm64`.
- Fixed `.env.example` so the RTSP placeholder can be sourced by shell-based checks without Bash interpreting angle brackets as redirection.
- Added a Frigate UI `time_format: 24hour` default/workaround for Swedish locale `Invalid time` rendering.
