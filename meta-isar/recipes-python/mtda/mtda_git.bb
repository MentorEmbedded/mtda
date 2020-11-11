# This Isar layer is part of MTDA
# Copyright (C) 2017-2020 Mentor Graphics, a Siemens business

inherit dpkg

SRC_URI += "git://github.com/MentorEmbedded/mtda.git;protocol=https;branch=master"
SRCREV   = "ce18b700e153f88e65d2b44322a4171aa9852968"
S        = "${WORKDIR}/git"

DEPENDS += "zerorpc-python"
