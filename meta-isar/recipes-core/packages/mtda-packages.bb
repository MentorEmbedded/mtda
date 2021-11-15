# This Isar layer is part of MTDA
# Copyright (C) 2017-2021 Mentor Graphics, a Siemens business

# Here's our list of custom packages
DEPENDS = "                              \
    hap-python                           \
    mjpg-streamer                        \
    mtda                                 \
    mtda-usb-functions                   \
    sd-mux-ctrl                          \
    zstandard                            \
"

# Make sure packages we built were added to the isar-apt repository
do_build[deptask] += "do_deploy_deb"

# This is a meta-package, nothing to build per se
do_build() {
    true
}

do_deploy_deb() {
    true
}
addtask deploy_deb after do_build
