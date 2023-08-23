# ---------------------------------------------------------------------------
# This yocto layer is part of MTDA
# Copyright (C) 2023 Siemens Digital Industrial Software
# ---------------------------------------------------------------------------
# SPDX-License-Identifier: MIT
# ---------------------------------------------------------------------------

SUMMARY = "Yocto image for mtda"
DESCRIPTION = "Yocto image for mtda."

# based on core image base
include recipes-core/images/core-image-base.bb

DISTRO_FEATURES:append = " systemd"
VIRTUAL-RUNTIME_init_manager += "systemd"

IMAGE_INSTALL:append = " \
        git \
        zstandard \
        zerorpc-python \
        mtda \
        python3-daemon \ 
        python3-zopeinterface \
        openssh \
        sd-mux-ctrl \
        pduclient \
        python3-zeroconf \
        python3-py3qterm \
        mjpg-streamer \
"
