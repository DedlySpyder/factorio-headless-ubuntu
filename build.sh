#!/usr/bin/env bash
set -eou pipefail

# Automatically build and publish the stable and experimental headless Factorio to Docker Hub

REPO_USERNAME="dedlyspyder"
IMAGE_REPO_NAME="factorio-headless-slim"
HERE="$(readlink -f "$(dirname "$)")")"

latest_release_data="$(curl -sSf https://factorio.com/api/latest-releases)"

stable_ver="$(echo "$latest_release_data" | jq -r '.stable.headless')"
experimental_ver="$(echo "$latest_release_data" | jq -r '.experimental.headless')"


echo "Building stable image for version $stable_ver"
docker build "$HERE" \
  -t "$IMAGE_REPO_NAME:$stable_ver" \
  -t "$REPO_USERNAME/$IMAGE_REPO_NAME:$stable_ver" \
  -t "$IMAGE_REPO_NAME:stable" \
  -t "$REPO_USERNAME/$IMAGE_REPO_NAME:stable" \
  --build-arg "VERSION=$stable_ver"

if [[ "$experimental_ver" == null ]]; then
  echo "Tagging $stable_ver to experimental (same version for both)"
  docker tag "$IMAGE_REPO_NAME:stable" "$IMAGE_REPO_NAME:experimental"
  docker tag "$IMAGE_REPO_NAME:experimental" "$REPO_USERNAME/$IMAGE_REPO_NAME:experimental"
else
  echo "Building experimental image for version $experimental_ver"
  docker build "$HERE" \
    -t "$IMAGE_REPO_NAME:$experimental_ver" \
    -t "$REPO_USERNAME/$IMAGE_REPO_NAME:$experimental_ver" \
    -t "$IMAGE_REPO_NAME:experimental" \
    -t "$REPO_USERNAME/$IMAGE_REPO_NAME:experimental" \
    --build-arg "VERSION=$experimental_ver"
fi

docker push -a "$REPO_USERNAME/$IMAGE_REPO_NAME"

mapfile -t images_to_cleanup < <(docker images "$REPO_USERNAME/$IMAGE_REPO_NAME" | grep "$REPO_USERNAME" | awk '{print $1":"$2}')
for image in "${images_to_cleanup[@]}"; do
  docker rmi "$image"
done
