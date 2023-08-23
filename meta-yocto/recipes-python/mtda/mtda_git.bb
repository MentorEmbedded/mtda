# ---------------------------------------------------------------------------
# This yocto layer is part of MTDA
# Copyright (C) 2023 Siemens Digital Industrial Software
# ---------------------------------------------------------------------------
# SPDX-License-Identifier: MIT
# ---------------------------------------------------------------------------

SUMMARY = "Multi-Tenant Device Access"
DESCRIPTION = "Multi-Tenant Device Access (or MTDA for short) is a \
	relatively small Python application acting as an interface \
	to a test device"
HOMEPAGE = "https://github.com/siemens/mtda "

LICENSE = "MIT"
LIC_FILES_CHKSUM = "file://COPYING;md5=9ed3c91908f8cbdb153f02d73272aa17"

MTDA_FILES = " \
    CONTRIBUTING.md \
    COPYING \
    LICENSES/ \
    MAINTAINERS.md \
    MANIFEST.in \
    README.md \
    configs/ \
    debian/ \
    docs/ \
    Kconfig \
    mtda-cli \
    mtda-config \
    mtda-service \
    mtda-systemd-helper \
    mtda-ui \
    mtda.ini \
    mtda/ \
    scripts/ \
    setup.py \
    tests/ \
    tox.ini \
    "

SRC_URI += "${@' '.join(['file://' + d.getVar('LAYERDIR_mtda') + '/../' + file for file in d.getVar('MTDA_FILES').split()])}"

S = "${WORKDIR}/working-repo"

do_gen_working_repo() {
    # when fetching the source from within the layer, after do_unpack
    # the source files are placed based on the absolute location for
    # the files/directories in the working directory eg: 
    # tmp/work/.../mtda/git/home/machine/buids/mtda/ or while building
    # with kas it is in tmp/work/.../mtda/git/repo , so we need to
    # determine the location of the sources before copying those to the
    # working directory
    MTDA_DIR=$(find ${WORKDIR}/ -type f -iname mtda-cli -exec dirname "{}" \;)
    for file in ${MTDA_FILES}; do
        cp -r ${MTDA_DIR}/${file} ${S}/
    done
}

do_gen_working_repo[cleandirs] += "${S}"

addtask gen_working_repo after do_unpack before do_patch

inherit setuptools3 systemd

RDEPENDS:${PN} = " \
    ${PYTHON_PN}-pyserial \
    ${PYTHON_PN}-pyusb \
    ${PYTHON_PN}-pyzmq \
    ${PYTHON_PN}-psutil \
    ${PYTHON_PN}-requests \
    ${PYTHON_PN}-terminal \
    ${PYTHON_PN}-kconfiglib \
"

do_install:append () {
    install -d ${D}${systemd_system_unitdir}
    install -m 0644 ${S}/debian/mtda.service ${D}${systemd_system_unitdir}
    install -m 0644 ${S}/debian/mtda-config.service ${D}${systemd_system_unitdir}
    install -m 0644 ${S}/debian/mtda-config.path ${D}${systemd_system_unitdir}

    # move mtda-systemd-helper from /usr/bin/ to /usr/sbin
    install -d ${D}${sbindir}
    mv ${D}/${bindir}/mtda-systemd-helper ${D}${sbindir}

    # move mtda-service from /usr/bin/ to /usr/sbin
    install -d ${D}${sbindir}
    mv ${D}/${bindir}/mtda-service ${D}${sbindir}
}

SYSTEMD_SERVICE:${PN} = "	\
	mtda.service 		\
	mtda-config.service 	\
	mtda-config.path 	\
"
