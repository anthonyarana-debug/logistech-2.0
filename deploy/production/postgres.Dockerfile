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
FROM postgres:17.11-alpine3.23@sha256:05aa77262db9277fde6374bb2f901c9604b8a9373029e1a7993440c6aae48736
# Retain GNU sync/install semantics used by the verified backup/TLS scripts.
RUN apk upgrade --no-cache && apk add --no-cache bash coreutils openssl ca-certificates
ENV LOGISTECH_PG_PLATFORM=postgres17-alpine3.23-musl-icu-v1
COPY --from=gosu-builder /out/gosu /usr/local/bin/gosu
RUN gosu nobody true
