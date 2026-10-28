#!/bin/bash
# Reviewed operator helper; never execute automatically or from application startup.
set -euo pipefail
[[ ${EUID} == 0 ]] || { echo 'Run as root on the approved Ubuntu 24.04 VM.' >&2; exit 1; }
source /etc/os-release
[[ $ID == ubuntu && $VERSION_ID == 24.04 ]] || { echo 'Ubuntu 24.04 required.' >&2; exit 1; }
[[ $(awk '/MemTotal/{print $2}' /proc/meminfo) -ge 1900000 ]] || { echo 'Minimum 2 GB RAM; 4 GB recommended.' >&2; exit 1; }
apt-get update
apt-get install -y ca-certificates curl git python3 openssl
install -m 0755 -d /etc/apt/keyrings
curl --fail --silent --show-error --location https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
chmod a+r /etc/apt/keyrings/docker.asc
arch=$(dpkg --print-architecture)
printf 'Types: deb\nURIs: https://download.docker.com/linux/ubuntu\nSuites: noble\nComponents: stable\nArchitectures: %s\nSigned-By: /etc/apt/keyrings/docker.asc\n' "$arch" > /etc/apt/sources.list.d/docker.sources
apt-get update
apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
systemctl enable --now docker
echo 'Docker installed. Configure provider firewall for 80/443 and restricted SSH before deployment.'
