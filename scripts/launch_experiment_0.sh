# Fixed parameters 
BIT=DPUcores_1 # Bitstream
SLEEP_SEC=2 # Between runs
SCRIPT_PATH=/home/root/TSUSC/scripts

# Sub-script fixed parameters
export NUM_THREADS=1
export RUN_SOFTMAX=0

# Sub-script tunable parameters
export MAX_IMAGES=1000
export POWERAPP_US=20000 # 20 ms (TIME_BIN_US)
USECONDS=8000000.0 # 8 seconds (floating point)
export NUM_SAPLES=$(bc -l <<< $USECONDS/$POWERAPP_US) # 400

# Datasets
DATASET_ROOT=/home/root/datasets
DATASET_LIST=$(find $DATASET_ROOT -maxdepth 1 -mindepth 1 -type d -exec basename {} \;)

# Loop over datasets
for DATASET in $DATASET_LIST
do
    export DATASET=$DATASET
    export LABELS=/home/root/datasets/$DATASET/labels.txt
    export IMAGE_PATH=/home/root/datasets/$DATASET/test_set/img/
    MODELS_PATHS=$(find /home/root/TSUSC/KD_compiled_xmodels/$DATASET -name *.xmodel)

    # Loop over files
    for xmodel in $MODELS_PATHS
    do
        # Sleep and reconfigure FPGA to decorrelate measures
        echo "Configuring FPGA"
        fpgautil -R
        fpgautil -b /lib/firmware/xilinx/$BIT/$BIT.bit.bin \
                -o /lib/firmware/xilinx/$BIT/$BIT.dtbo
        
        sleep $SLEEP_SEC
        
        export XMODEL_BASENAME=$(basename $xmodel .h5.xmodel)
        echo "Running $DATASET/$XMODEL_BASENAME"
        time bash -x $SCRIPT_PATH/experiment_0.sh $xmodel
    done
done