# ---------------------------------------------------------------------------
# Test storage functions
# ---------------------------------------------------------------------------
#
# This software is a part of MTDA.
# Copyright (C) 2023 Siemens Digital Industries Software
#
# ---------------------------------------------------------------------------
# SPDX-License-Identifier: MIT
# ---------------------------------------------------------------------------

import time

from common import Consts
from common import Utils

from mtda.pytest import Console
from mtda.pytest import Storage
from mtda.pytest import Target


def test_write_raw(powered_off):
    assert Storage.to_host() is True
    Storage.write("alpine.tar")
    assert Storage.to_target() is True

    assert Target.on() is True
    Console.send("cat /etc/os-release\r")
    assert Console.wait_for("Alpine") is not None


def test_write_bmap(powered_off):
    assert Storage.to_host() is True
    Storage.write("rockylinux.tar")
    assert Storage.to_target() is True

    assert Target.on() is True
    Console.send("cat /etc/os-release\r")
    assert Console.wait_for("Rocky Linux") is not None


def test_write_bz2(powered_off):
    assert Storage.to_host() is True
    Storage.write("archlinux.tar.bz2")
    assert Storage.to_target() is True

    assert Target.on() is True
    Console.send("cat /etc/os-release\r")
    assert Console.wait_for("Arch Linux") is not None


def test_write_gz(powered_off):
    assert Storage.to_host() is True
    Storage.write("debian.tar.gz")
    assert Storage.to_target() is True

    assert Target.on() is True
    Console.send("cat /etc/os-release\r")
    assert Console.wait_for("Debian") is not None


def test_write_xz(powered_off):
    assert Storage.to_host() is True
    Storage.write("almalinux.tar.xz")
    assert Storage.to_target() is True

    assert Target.on() is True
    Console.send("cat /etc/os-release\r")
    assert Console.wait_for("AlmaLinux") is not None


def test_write_zst(powered_off):
    assert Storage.to_host() is True
    Storage.write("ubuntu.tar.zst")
    assert Storage.to_target() is True

    assert Target.on() is True
    Console.send("cat /etc/os-release\r")
    assert Console.wait_for("Ubuntu") is not None
