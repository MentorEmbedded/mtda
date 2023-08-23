# ---------------------------------------------------------------------------
# This yocto layer is part of MTDA
# Copyright (C) 2023 Siemens Digital Industrial Software
# ---------------------------------------------------------------------------
# SPDX-License-Identifier: MIT
# ---------------------------------------------------------------------------

SUMMARY = "MJPG-streamer takes JPGs from Linux-UVC compatible webcams,\
	filesystem or other input plugins and streams them as M-JPEG \
	via HTTP to webbrowsers, VLC and other software. It is the \
	successor of uvc-streamer, a Linux-UVC streaming application \
	with Pan/Tilt"

LICENSE = "GPL-2.0-only"
LIC_FILES_CHKSUM = "file://LICENSE;md5=751419260aa954499f7abaabaa882bbe"

SRCREV = "310b29f4a94c46652b20c4b7b6e5cf24e532af39"

SRC_URI = "git://github.com/jacksonliam/mjpg-streamer.git;protocol=https;branch=master"

# Workaround multiple defined symbols
TARGET_CFLAGS += "-fcommon"

DEPENDS = "libgphoto2 v4l-utils"

S = "${WORKDIR}/git/mjpg-streamer-experimental"

inherit cmake

OECMAKE_GENERATOR="Unix Makefiles"
EXTRA_OECMAKE = "-DENABLE_HTTP_MANAGEMENT=ON"

do_install() {
    oe_runmake install DESTDIR=${D}
}
