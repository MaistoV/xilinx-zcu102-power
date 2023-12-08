
SLEEP_SEC=2
MODELS_PATH=/home/root/TSUSC/KD_compiled_xmodels
SCRIPT_PATH=/home/root/TSUSC/scripts

# Loop over files
for xmodel in $MODELS_PATH/*.xmodel
do
    bash -x $SCRIPT_PATH/experiment_0.sh $xmodel

    # Sleep a little to decorrelate measures
    sleep $SLEEP_SEC

done