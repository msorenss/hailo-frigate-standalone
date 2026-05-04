# Standalone Frigate image with Hailo-10H support.
# Based on the community Home Assistant add-on work from:
# https://github.com/mikehailodev/frigate-hass-addons-h10
ARG FRIGATE_IMAGE=ghcr.io/blakeblackshear/frigate:0.17.0
FROM ${FRIGATE_IMAGE}

ENV DEBIAN_FRONTEND=noninteractive
ARG HAILORT_VERSION=5.3.0
ARG HAILORT_DEB=hailort_5.3.0_arm64.deb
ARG HAILORT_WHEEL=hailort-5.3.0-cp311-cp311-linux_aarch64.whl

# Required local files:
# - packages/${HAILORT_DEB}
# - packages/${HAILORT_WHEEL}
COPY packages/ /tmp/hailo-packages/
RUN test -f "/tmp/hailo-packages/${HAILORT_DEB}" \
    && test -f "/tmp/hailo-packages/${HAILORT_WHEEL}" \
    || (echo "Missing HailoRT packages. See docs/host-setup.md." >&2; exit 1)

# Replace the HailoRT version bundled in the upstream Frigate image.
RUN set -e; \
    pip3 uninstall -y hailort 2>/dev/null || true; \
    pip3 install --break-system-packages "/tmp/hailo-packages/${HAILORT_WHEEL}"; \
    apt-get -qq update 2>/dev/null; \
    dpkg -i "/tmp/hailo-packages/${HAILORT_DEB}" 2>/dev/null || apt-get -qq install -f -y 2>/dev/null; \
    rm -f /usr/local/bin/hailortcli; \
    ln -s /usr/bin/hailortcli /usr/local/bin/hailortcli; \
    ldconfig; \
    rm -rf /tmp/hailo-packages /var/lib/apt/lists/*

COPY hailo10h_patch.py /tmp/hailo10h_patch.py
RUN python3 /tmp/hailo10h_patch.py && rm /tmp/hailo10h_patch.py

LABEL org.opencontainers.image.title="Standalone Frigate Hailo-10H" \
    org.opencontainers.image.description="Frigate 0.17.0 with HailoRT 5.3.0 and Hailo-10H detector patch" \
      org.opencontainers.image.source="https://github.com/mikehailodev/frigate-hass-addons-h10"
