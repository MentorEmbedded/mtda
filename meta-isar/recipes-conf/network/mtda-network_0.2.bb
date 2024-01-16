# This Isar layer is part of MTDA
# Copyright (C) 2024 Siemens AG
# SPDX-License-Identifier: MIT

DESCRIPTION = "MTDA network configuration using network-manager"
MAINTAINER = "Cedric Hombourger <chombourger@gmail.com>"
DEBIAN_DEPENDS = "nbd-server, network-manager"
DPKG_ARCH = "all"

SRC_URI = "file://postinst \
           file://90-systemd-networkd-disabled.preset"

inherit dpkg-raw

do_install() {
    # disable systemd-networkd service
    install -d -m 755 ${D}/etc/systemd/system-preset
    install -m 755 ${WORKDIR}/90-systemd-networkd-disabled.preset ${D}/etc/systemd/system-preset/
}
