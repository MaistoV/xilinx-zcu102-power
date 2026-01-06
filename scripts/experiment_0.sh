#!/bin/bash
# Description:
#   Run powerapp and application with specified xmodel and parameters
# Args:
#   $1: Path to xmodel
# Environment variables:
#   DATASET
#   NUM_SAPLES
#   POWERAPP_US
#   XMODEL_BASENAME
#   IMAGE_PATH
#   LABELS
#   RUN_SOFTMAX
#   MAX_IMAGES
#   NUM_THREADS

# Parse args
XMODEL=$1

# Launch power measurement in background in continuous mode
echo "[DEBUG] Running powerapp "
export OUT_DIR=data/$DATASET
mkdir -p $OUT_DIR
./powerapp                                      \
        -n $NUM_SAPLES                          \
        -t $POWERAPP_US                         \
        -p 1                                    \
        -o $OUT_DIR/${XMODEL_BASENAME}.csv      \
        &
# Save PID for later
POWERAPP_PID=$!

# Wait for powerapp to init
echo "[DEBUG] Wait a sec"
sleep 1

# Launch
echo "[DEBUG] Running app_O0"
./app_O0 $XMODEL        \
    $IMAGE_PATH         \
    $LABELS             \
    $RUN_SOFTMAX        \
    $MAX_IMAGES         \
    $NUM_THREADS        \
    $OUT_DIR            \
    # > /dev/null

# Stop power measurement
# Give time to powerapp to flush to files
# sleep 2; kill $POWERAPP_PID

# Wait for all the samples to be collected
# echo "[DEBUG] Wait for powerapp to finish"
wait $POWERAPP_PID
echo "[DEBUG] Powerapp is done"
