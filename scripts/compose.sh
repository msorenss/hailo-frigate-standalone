#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "${BASH_SOURCE[0]}")/.."
env_file=".env"
if [[ ! -f "$env_file" ]]; then
	env_file=".env.example"
fi
exec docker compose --env-file "$env_file" -f compose.yaml "$@"
