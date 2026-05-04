# Standalone Hailo VLM Chat image.
# Pulls the application files from the community add-on repo at build time:
# https://github.com/mikehailodev/hailo-vlm-addon
FROM debian:trixie-slim

SHELL ["/bin/bash", "-o", "pipefail", "-c"]
ENV DEBIAN_FRONTEND=noninteractive

ARG VLM_REPO=https://github.com/mikehailodev/hailo-vlm-addon.git
ARG VLM_REF=main
ARG HAILORT_VERSION=5.3.0
ARG HAILORT_DEB=hailort_5.3.0_arm64.deb
ARG HAILORT_WHEEL=hailort-5.3.0-cp313-cp313-linux_aarch64.whl

RUN apt-get update && apt-get upgrade -y && apt-get install -y --no-install-recommends \
    ca-certificates \
    git \
    jq \
    python3 \
    python3-opencv \
    python3-pip \
    tini \
    v4l-utils \
    && rm -rf /var/lib/apt/lists/*

# Required local files:
# - packages/${HAILORT_DEB}
# - packages/${HAILORT_WHEEL}
COPY packages/ /tmp/hailo-packages/
RUN test -f "/tmp/hailo-packages/${HAILORT_DEB}" \
    && test -f "/tmp/hailo-packages/${HAILORT_WHEEL}" \
    || (echo "Missing HailoRT packages. See docs/host-setup.md." >&2; exit 1)

RUN set -e; \
    apt-get update; \
    dpkg -i "/tmp/hailo-packages/${HAILORT_DEB}" || apt-get install -f -y; \
    ldconfig; \
    rm -rf /var/lib/apt/lists/*

RUN pip3 install --break-system-packages --no-cache-dir \
    "/tmp/hailo-packages/${HAILORT_WHEEL}" \
    && rm -rf /tmp/hailo-packages

RUN git clone --depth 1 --branch "${VLM_REF}" "${VLM_REPO}" /tmp/hailo-vlm-addon \
    && cp -a /tmp/hailo-vlm-addon/hailo_vlm/rootfs/opt/hailo_vlm /opt/hailo_vlm \
    && pip3 install --break-system-packages --no-cache-dir -r /opt/hailo_vlm/requirements.txt \
    && chmod a+x /opt/hailo_vlm/run.sh \
    && rm -rf /tmp/hailo-vlm-addon

WORKDIR /opt/hailo_vlm
EXPOSE 8099

ENTRYPOINT ["/usr/bin/tini", "--"]
CMD ["/opt/hailo_vlm/run.sh"]
