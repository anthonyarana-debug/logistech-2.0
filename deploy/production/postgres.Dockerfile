FROM golang:1.27.3-alpine@sha256:d200d2dd76b03a99b52651fd1325aff7dcd35422c35c01bac56571b0507f3deb AS gosu-builder
RUN apk add --no-cache git
WORKDIR /src/gosu
# Official gosu 1.20, rebuilt with the patched Go standard library.
RUN git init && git remote add origin https://github.com/tianon/gosu.git \
    && git fetch --depth 1 origin 29b939aa5bd4dc588af765b8248f6e39150d2565 \
    && git checkout --detach FETCH_HEAD \
    && test "$(git rev-parse HEAD)" = 29b939aa5bd4dc588af765b8248f6e39150d2565
ENV CGO_ENABLED=0 GOTOOLCHAIN=local
RUN go build -trimpath -ldflags '-w -s' -o /out/gosu .
FROM postgres:17.11-bookworm
RUN apt-get update && apt-get upgrade -y --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*
COPY --from=gosu-builder /out/gosu /usr/local/bin/gosu
RUN gosu nobody true
