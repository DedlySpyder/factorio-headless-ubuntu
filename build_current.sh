#!/usr/bin/env bash
set -eou pipefail

# Automatically build and publish the stable and experimental headless Factorio to Docker Hub

HERE="$(readlink -f "$(dirname "$)")")"

latest_release_data="$(curl -sSf https://factorio.com/api/latest-releases)"

stable_ver="$(echo "$latest_release_data" | jq -r '.stable.headless')"
experimental_ver="$(echo "$latest_release_data" | jq -r '.experimental.headless')"

if [[ "$experimental_ver" == null ]]; then
  "$HERE/build_version.sh" "$stable_ver" "stable" "experimental"
else
  "$HERE/build_version.sh" "$stable_ver" "stable"
  "$HERE/build_version.sh" "$experimental_ver" "experimental"
fi
