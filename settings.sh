# Petalinux comes with its own python environmet
export PYTHON=$(which python3.6)

# Set Vitis-AI/Petalinux versions
# PETALINUX_VERSION=2021.2 # Vitis-AI 2.0
PETALINUX_VERSION=2022.2 # Vitis-AI 3.0
# Setup petalinux SDK
source ~/petalinux_sdk_$PETALINUX_VERSION/environment-setup-cortexa72-cortexa53-xilinx-linux 
echo "Using: "
printf "Petalinux "
echo $CC | awk '{print $1}' | xargs which | sed -E "s|/sysroot.+||g"


# Project intependent variables
export XMODELS_DIR=/media/sf_Xilinx_Ubuntu_18_04_shared/TSUSC/xmodels/
export BOARD_IP=192.168.1.101

echo "XMODELS_DIR $XMODELS_DIR"
echo "BOARD_IP $BOARD_IP"

