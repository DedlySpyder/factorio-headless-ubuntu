FROM ubuntu:20.04

RUN apt-get update \
    && apt-get install -y \
        curl \
        python3.8 \
        python3-pip \
        xz-utils \
    && rm -rf /var/lib/apt/lists/*

ARG VERSION

RUN curl -L https://www.factorio.com/get-download/$VERSION/headless/linux64 -o /tmp/factorio.tar.xz \
    && tar -xvf /tmp/factorio.tar.xz -C / \
    && rm -f /tmp/factorio.tar.xz \
    && echo "$VERSION" > /factorio/version

COPY scripts/*.py /scripts/
