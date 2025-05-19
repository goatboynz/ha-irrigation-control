ARG BUILD_FROM
FROM ${BUILD_FROM}

# Set shell
SHELL ["/bin/bash", "-o", "pipefail", "-c"]

# Set workdir
WORKDIR /usr/src/app

# Copy requirements first for better cache
COPY requirements.txt .

# Install required packages and Python deps
RUN \
    apk add --no-cache \
        py3-pip \
        gcc \
        musl-dev \
        python3-dev \
        libffi-dev \
    && pip3 install --no-cache-dir -r requirements.txt \
    && apk del \
        gcc \
        musl-dev \
        python3-dev \
        libffi-dev

# Copy local code to image
COPY irrigation_control/ .
COPY rootfs/ /
COPY run.sh /

# Set permissions
RUN chmod a+x /run.sh

# Labels
LABEL \
    io.hass.name="Irrigation Control" \
    io.hass.description="Advanced irrigation scheduling and control for 6 zones" \
    io.hass.type="addon" \
    io.hass.version="${BUILD_VERSION}" \
    io.hass.arch="${BUILD_ARCH}" \
    maintainer="YOUR_NAME <your_email@example.com>"

# Start addon
CMD [ "/run.sh" ]
