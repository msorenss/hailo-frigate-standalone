#!/usr/bin/env bash
set -euo pipefail

if [[ -z "${HAILORT_VERSION:-}" ]]; then
  if [[ -f .env ]]; then
    set -a
    . ./.env
    set +a
  elif [[ -f .env.example ]]; then
    set -a
    . ./.env.example
    set +a
  fi
fi

HAILORT_VERSION="${HAILORT_VERSION:-5.3.0}"
HAILORT_DEB="${HAILORT_DEB:-hailort_${HAILORT_VERSION}_arm64.deb}"
FRIGATE_HAILORT_WHEEL="${FRIGATE_HAILORT_WHEEL:-hailort-${HAILORT_VERSION}-cp311-cp311-linux_aarch64.whl}"
VLM_HAILORT_WHEEL="${VLM_HAILORT_WHEEL:-hailort-${HAILORT_VERSION}-cp313-cp313-linux_aarch64.whl}"

contexts=(
  "services/frigate-h10/packages:${HAILORT_DEB}:${FRIGATE_HAILORT_WHEEL}"
  "services/hailo-vlm/packages:${HAILORT_DEB}:${VLM_HAILORT_WHEEL}"
)

missing=0
for item in "${contexts[@]}"; do
  IFS=: read -r context deb wheel <<<"$item"
  required=("$deb" "$wheel")
  echo "Checking ${context}"
  for file in "${required[@]}"; do
    if [[ -f "${context}/${file}" ]]; then
      echo "  OK ${file}"
    else
      echo "  MISSING ${file}" >&2
      missing=1
    fi
  done
done

if [[ "$missing" -ne 0 ]]; then
  cat >&2 <<'MSG'

Copy the HailoRT package files into both package directories before building.
They are intentionally ignored by git because they may be large or licensed.
MSG
  exit 1
fi
