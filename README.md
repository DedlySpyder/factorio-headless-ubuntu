[Factorio](https://www.factorio.com/) headless server image. This image was made to be used as a base for other images.

**Do not use this image if you are looking for a quick multiplayer server**, there are likely better options for that.

## Tags
* `stable` - Latest stable release
* `experimental` - Latest experimental release, may be same as stable if there is only a stable release currently

## Image Composition
This image has `curl` and Factorio installed on Ubuntu. Factorio is installed at `/factorio`

The version of Factorio that was originally downloaded for the image can be found in `/factorio/version`

[Source](https://github.com/DedlySpyder/FactorioTooling/blob/main/docker/images/headless/Dockerfile)