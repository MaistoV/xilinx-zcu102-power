
# Fixed parameters 
SLEEP_SEC=2
MODELS_PATH=/home/root/TSUSC/KD_compiled_xmodels
SCRIPT_PATH=/home/root/TSUSC/scripts

# Sub-script fixed parameters
export NUM_THREADS=1
export RUN_SOFTMAX=0
export LABELS=/home/root/datasets/CIFAR10/labels.txt
export IMAGE_PATH=/home/root/datasets/CIFAR10/test_set/img/

# Sub-script Tunable parameters
export MAX_IMAGES=1000
export POWERAPP_US=20000 # 20 ms
export NUM_SAPLES=400 # this has to be hand-tuned

# Loop over files
for xmodel in $MODELS_PATH/*.xmodel
do
    export XMODEL_BASENAME=$(basename $xmodel .h5.xmodel)
    echo "Running $XMODEL_BASENAME"
    time bash -x $SCRIPT_PATH/experiment_0.sh $xmodel

    # Sleep and reconfigure FPGA to decorrelate measures
    sleep $SLEEP_SEC
    bash /home/root/init.sh

done