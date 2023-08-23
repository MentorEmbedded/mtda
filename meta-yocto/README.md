# MTDA Yocto layer

mtda-image is based on core-image-base

### Building for imx boards
1. Following bsp build instructions from https://source.codeaurora.org/external/imx/imx-manifest/tree/README?h=imx-linux-honister (Tested with `DISTRO=fsl-imx-xwayland`)
2. Once build setup is created, add this layer in `conf/bblayer.conf`.
3. Build the image
    > bitbake mtda-image

### Building for Beaglebone black
The image for the Beaglebone black may be built with `kas/yocto/mtda-beaglebone-yocto.yml`.

1. Clone this repo.
2. Execute the following command.
```
./kas-container build kas/yocto/mtda-beaglebone-yocto.yml
```
3. The build artifacts will be present under `build/tmp/deploy/images/beaglebone-yocto`
