#!/usr/bin/env bash
set -exo pipefail

REPO="dedlyspyder"
IMAGE="factorio-headless-ubuntu"

if [[ -z "$1" ]]; then
  echo "::error Usage: $0 [factorio version]"
  exit 1
fi
factorio_version="$1"

pwd
readlink -f "$(dirname "$0")"
git branch -a

script_version="$(git describe --tags --abbrev=0)"
tag="${factorio_version}-${script_version}"

if curl -sSLf "https://hub.docker.com/v2/repositories/$REPO/$IMAGE/tags/$tag" > /dev/null; then
  echo "exists=true" >> $GITHUB_OUTPUT
else
  echo "exists=false" >> $GITHUB_OUTPUT
fi
