# ---------------------------------------------------------------------------
# This yocto layer is part of MTDA
# Copyright (C) 2023 Siemens Digital Industrial Software
# ---------------------------------------------------------------------------
# SPDX-License-Identifier: MIT
# ---------------------------------------------------------------------------

SUMMARY = "recipe to install pduclient"
DESCRIPTION = "recipe to install pduclient"

LICENSE = "GPL-2.0-or-later"
LIC_FILES_CHKSUM = "file://${COMMON_LICENSE_DIR}/GPL-2.0-or-later;md5=fed54355545ffd980b814dab4a3b312c"

SRCREV   = "1508d9b109188248d8a37d21a726612b47b74001"

SRC_URI = "git://git@github.com/pdudaemon/pdudaemon.git;protocol=https;branch=main"

S = "${WORKDIR}/git"

do_install(){
    install -d ${D}${bindir}
    cp -r ${S}/pduclient ${D}${bindir}
}

FILES:${PN} = "${bindir}"

INSANE_SKIP:${PN} = "file-rdeps"
