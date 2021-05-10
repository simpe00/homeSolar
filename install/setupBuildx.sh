#!/bin/bash
LATEST_BUILDX_VERSION=$(curl -sSL "https://api.github.com/repos/docker/buildx/releases/latest" | grep -o -P '(?<="tag_name": ").+(?=")')
DOCKER="${HOME}/.docker/"
DOCKER_CLI="${DOCKER}cli-plugins/"

if ! test -d "${DOCKER}"; then
    mkdir "${DOCKER}"
fi

if ! test -d "${DOCKER_CLI}"; then
    mkdir "${DOCKER_CLI}"
fi

sudo curl \
    -L "https://github.com/docker/buildx/releases/download/${LATEST_BUILDX_VERSION}/buildx-${LATEST_BUILDX_VERSION}.linux-arm64" \
    -o ~/.docker/cli-plugins/docker-buildx
    
sudo chmod a+x ~/.docker/cli-plugins/docker-buildx
docker buildx install