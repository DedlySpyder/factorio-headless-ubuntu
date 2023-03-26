[Factorio](https://www.factorio.com/) headless server image. This image was made to be used as a base for other images.

**Do not use this image if you are looking for a quick multiplayer server**, there are likely better options for that.

## Tags
* `stable` - Latest stable release
* `experimental` - Latest experimental release, may be same as stable if there is only a stable release currently
* `[FACTORIO_VERSION]-[SCRIPTS_VERSION]` - All other tags are in this format. The first version is the Factorio version.
The second version is the version of the helper scripts for tooling.

## Image Composition
This contains Factorio, python 3.8, and some [helper scripts](https://github.com/DedlySpyder/factorio-headless-ubuntu/tree/main/scripts) in `/script` for running/parsing Factorio output.

The version of Factorio that was originally downloaded for the image can be found in `/factorio/version`

[Dockerfile Source](https://github.com/DedlySpyder/factorio-headless-ubuntu/blob/main/Dockerfile)

