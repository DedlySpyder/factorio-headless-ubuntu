#!/usr/bin/env bash
set -exo pipefail

REPO="dedlyspyder"
IMAGE="factorio-headless-ubuntu"

if [[ -z "$2" ]]; then
  echo "::error Usage: $0 [factorio version] [headless type: stable|experimental] "
  exit 1
fi
factorio_version="$1"
headless_type="$2"

script_version="$(git describe --tags --abbrev=0 || git pull --tags > /dev/null && git tag -l)"
version_tag="${factorio_version}-${script_version}"

docker pull "$REPO/${IMAGE}:$version_tag"
docker pull "$REPO/${IMAGE}:$headless_type"

if diff <(docker inspect "$REPO/${IMAGE}:$headless_type" | jq '.[].RootFS') <(docker inspect "$REPO/${IMAGE}:$version_tag" | jq '.[].RootFS') > /dev/null; then
  echo "equals=true" >> $GITHUB_OUTPUT
else
  echo "equals=false" >> $GITHUB_OUTPUT
fi
