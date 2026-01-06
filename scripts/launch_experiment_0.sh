# Fixed parameters
# BIT=DPUcores_1 # Bitstream
SLEEP_SEC=2 # Between runs
SCRIPT_PATH=/home/root/JSA/scripts

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
DATASET_DIR=/home/root/JSA/datasets
# DATASET_LIST=$(find $DATASET_DIR -maxdepth 1 -mindepth 1 -type d -exec basename {} \;)
XMODELS_DIR=/home/root/JSA/xmodels/
XMODELS_PATHS=$(find $XMODELS_DIR -name *.xmodel)
echo "Running following xmodels:"
echo "$XMODELS_PATHS"
echo ""

# Loop over files
for xmodel in $XMODELS_PATHS
do
    # Sleep and reconfigure FPGA to decorrelate measures
    # echo "Configuring FPGA"
    # fpgautil -R
    # fpgautil -b /lib/firmware/xilinx/$BIT/$BIT.bit.bin \
    #         -o /lib/firmware/xilinx/$BIT/$BIT.dtbo

    # sleep $SLEEP_SEC

    # Set variables for experiment_0.sh script
    echo "[INFO] Running $xmodel"
    export XMODEL_BASENAME=$(basename $xmodel .xmodel)
    export DATASET=cifar100
    export LABELS=$DATASET_DIR/$DATASET/labels.txt
    # export IMAGE_PATH=$DATASET_DIR/$DATASET/test/apple/
    export IMAGE_PATH=$DATASET_DIR/$DATASET/

    # Launch run
    time bash $SCRIPT_PATH/experiment_0.sh $xmodel
done