# ---------------------------------------------------------------------------
# This yocto layer is part of MTDA
# Copyright (C) 2023 Siemens Digital Industrial Software
# ---------------------------------------------------------------------------
# SPDX-License-Identifier: MIT
# ---------------------------------------------------------------------------

DESCRIPTION = "Unlike the older pyqonsole this console widget works with \
               PyQt5/PySide2 and let's you embed a shell into your application."
HOMEPAGE = "https://gitlab.com/mikeramsey/py3qtermwidget"

LICENSE = "GPL-3.0-only"
LIC_FILES_CHKSUM = "file://${COMMON_LICENSE_DIR}/GPL-3.0-only;md5=c79ff39f19dfec6d293b95dea7b07891"

SRC_URI[md5sum] = "3d1d9b07d1ceef712a9212a04396260f"
SRC_URI[sha256sum] = "88379580d5d155361e072520bae62e047ab3741eaeb8b07867ab4588ea7a5031"

inherit pypi setuptools3

PYPI_PACKAGE = "py3qterm"
