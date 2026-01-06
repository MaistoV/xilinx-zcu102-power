# Fixed parameters
# BIT=DPUcores_1 # Bitstream
SLEEP_SEC=2 # Between runs
SCRIPT_PATH=/home/root/TACO/scripts

# Sub-script fixed parameters
export NUM_THREADS=1
export RUN_SOFTMAX=0

# Sub-script tunable parameters
export MAX_IMAGES=1000
export POWERAPP_US=24000 # 24 ms (TIME_BIN_US)
USECONDS=24000000.0 # 24 seconds (floating point)
export NUM_SAPLES=$(bc -l <<< $USECONDS/$POWERAPP_US)
echo "POWERAPP_US: $POWERAPP_US"
echo "NUM_SAPLES: $NUM_SAPLES"

# Datasets
DATASET_DIR=/home/root/TACO/datasets
# DATASET_LIST=$(find $DATASET_DIR -maxdepth 1 -mindepth 1 -type d -exec basename {} \;)
XMODELS_DIR=/home/root/TACO/xmodels/
# XMODELS_PATHS=$(find $XMODELS_DIR -name *.xmodel)
# echo "Running following xmodels:"
# echo "$XMODELS_PATHS"
# echo ""

ARCH_LIST=(
    # 512
    # 800
    # 1024
    # 1600
    2304
    # 3163
    4096
)

# Loop over files
for arch in ${ARCH_LIST[*]}
do
    # Compose xmodel and DT overlay name
    xmodel=${XMODELS_DIR}/arch${arch}_unet_cityscapes64.xmodel
    BIT=DPUcores1_ARCH${arch}

    # Sleep and reconfigure FPGA to decorrelate measures
    # echo "[INFO] Configuring FPGA for ARCH${arch}"
    # fpgautil -R
    # fpgautil -b /lib/firmware/xilinx/$BIT/*.bit.bin \
    #         -o /lib/firmware/xilinx/$BIT/*.dtbo

    # echo "[INFO] Sleeping a $SLEEP_SEC seconds..."
    # sleep $SLEEP_SEC

    # Set variables for experiment_0.sh script
    echo "[INFO] Running $xmodel"
    export XMODEL_BASENAME=$(basename $xmodel .xmodel)
    export DATASET=cifar100
    export LABELS="null"
    export IMAGE_PATH=$DATASET_DIR/$DATASET/

    # Launch sub-script
    time bash $SCRIPT_PATH/experiment_0.sh $xmodel
done