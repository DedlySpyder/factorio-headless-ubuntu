#!/usr/bin/env bash
set -eou pipefail

# Build and publish the specified version of headless Factorio to Docker Hub (extra args will be different tags of the
# same build)

REPO_USERNAME="dedlyspyder"
IMAGE_REPO_NAME="factorio-headless-slim"


if [[ -z "$1" ]]; then
  echo "Missing base version to build"
  echo "Usage: $0 [version] (extra tags...)"
  exit 1
fi

VERSION="$1"
shift
IFS=" " read -r -a EXTRA_TAGS <<< "$@"

HERE="$(readlink -f "$(dirname "$)")")"

echo "Building $VERSION tag for $IMAGE_REPO_NAME"
docker build "$HERE" \
  -t "$IMAGE_REPO_NAME:$VERSION" \
  -t "$REPO_USERNAME/$IMAGE_REPO_NAME:$VERSION" \
  --build-arg "VERSION=$VERSION"

for tag in "${EXTRA_TAGS[@]}"; do
  echo "Tagging $VERSION tag to $tag for $IMAGE_REPO_NAME"
  docker tag "$IMAGE_REPO_NAME:$VERSION" "$IMAGE_REPO_NAME:$tag"
  docker tag "$IMAGE_REPO_NAME:$VERSION" "$REPO_USERNAME/$IMAGE_REPO_NAME:$tag"
done

echo "Pushing $REPO_USERNAME/$IMAGE_REPO_NAME"
docker push -a "$REPO_USERNAME/$IMAGE_REPO_NAME"

mapfile -t images_to_cleanup < <(docker images "$REPO_USERNAME/$IMAGE_REPO_NAME" | grep "$REPO_USERNAME" | awk '{print $1":"$2}')
for image in "${images_to_cleanup[@]}"; do
  docker rmi "$image"
done
