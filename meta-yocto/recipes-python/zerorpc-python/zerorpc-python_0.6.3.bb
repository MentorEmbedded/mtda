# ---------------------------------------------------------------------------
# This yocto layer is part of MTDA
# Copyright (C) 2023 Siemens Digital Industrial Software
# ---------------------------------------------------------------------------
# SPDX-License-Identifier: MIT
# ---------------------------------------------------------------------------

SUMMARY = "zerorpc is a flexible RPC implementation based on zeromq \
	and messagepack"
DESCRIPTION = "zerorpc is a flexible RPC implementation based on \
	zeromq and messagepack"
HOMEPAGE = " https://github.com/0rpc/zerorpc-python "
LICENSE = "MIT"
LIC_FILES_CHKSUM = "file://${COMMON_LICENSE_DIR}/MIT;md5=0835ade698e0bcf8506ecda2f7b4f302"

SRC_URI[sha256sum] = "d2ee247a566fc703f29c277d767f6f61f1e12f76d0402faea4bd815f32cbf37f"

inherit pypi setuptools3

RDEPENDS:${PN} = " \
    ${PYTHON_PN}-msgpack \
    ${PYTHON_PN}-pyzmq \
    ${PYTHON_PN}-future \
    ${PYTHON_PN}-gevent (>=1.1) \
"

PYPI_PACKAGE = "zerorpc"
