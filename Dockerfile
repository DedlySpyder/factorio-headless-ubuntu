FROM alpine:3.13

ARG VERSION

RUN apk add --no-cache curl

RUN curl -L https://www.factorio.com/get-download/$VERSION/headless/linux64 -o /tmp/factorio.tar.xz && \
    tar -xvf /tmp/factorio.tar.xz -C / && \
    rm -f /tmp/factorio.tar.xz && \
    echo "$VERSION" > /factorio/version
