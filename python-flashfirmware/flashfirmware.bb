DESCRIPTION = "Simple Python flashfirmware hdmi application"
SECTION = "examples"
LICENSE = "MIT"
LIC_FILES_CHKSUM = "file://${COREBASE}/meta/COPYING.MIT;md5=3da9cfbcb788c80a0384361b4de20420"

SRC_URI = "file://setup.py \
           file://python-flashfirmware.py \
           file://flashfirmware/__init__.py \
           file://flashfirmware/main.py"

S = "${WORKDIR}"
RDEPENDS_${PN} += "python-smbus python-math"
inherit setuptools

do_install_append () {
    install -d ${D}${bindir}
    install -m 0755 python-flashfirmware.py ${D}${bindir}
}
