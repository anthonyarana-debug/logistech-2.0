FROM node:24.19.0-bookworm-slim AS frontend
WORKDIR /build
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci
COPY frontend/ ./
ENV VITE_API_BASE_URL=/api/v1
RUN npm run build
FROM golang:1.27.3-alpine@sha256:d200d2dd76b03a99b52651fd1325aff7dcd35422c35c01bac56571b0507f3deb AS caddy-builder
RUN apk add --no-cache git ca-certificates
WORKDIR /src/caddy
# Official v2.11.7 tag object 87c43dc4f54861ec7e54302cfb2ad3e34508b6dc
# resolves to this commit. Fetch and verify the immutable commit, not a branch.
RUN git init \
    && git remote add origin https://github.com/caddyserver/caddy.git \
    && git fetch --depth 1 origin 72dd0fb067f6d7826c7f79907670ba4a713bfe37 \
    && git checkout --detach FETCH_HEAD \
    && test "$(git rev-parse HEAD)" = 72dd0fb067f6d7826c7f79907670ba4a713bfe37
ENV CGO_ENABLED=0 GOTOOLCHAIN=local GOMAXPROCS=2
# Build as a versioned dependency so binary metadata retains v2.11.7.
WORKDIR /build
RUN go mod init logistech.local/caddy-build \
    && go get github.com/caddyserver/caddy/v2/cmd/caddy@v2.11.7 \
    && go get github.com/go-jose/go-jose/v4@v4.1.6 golang.org/x/net@v0.60.0
# cmd/caddy imports modules/standard, preserving ACME, local CA, files and proxy.
RUN mkdir -p /out && go build -mod=readonly -p 2 -trimpath \
    -ldflags '-w -s -X github.com/caddyserver/caddy/v2.CustomVersion=v2.11.7' \
    -o /out/caddy github.com/caddyserver/caddy/v2/cmd/caddy
FROM caddy:2.11.7-alpine@sha256:eb4d35b7452d1ab6171fbdbe8d9275b2301dad6dad92115d91e19fb9b24d510f
RUN apk upgrade --no-cache
COPY --from=caddy-builder /out/caddy /usr/bin/caddy
COPY --from=frontend /build/dist /srv
COPY deploy/production/Caddyfile /etc/caddy/Caddyfile
COPY deploy/production/routes.caddy /etc/caddy/routes.caddy
