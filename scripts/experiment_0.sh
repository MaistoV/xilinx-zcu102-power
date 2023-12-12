#!/bin/bash
# Run application with specified xmodel

# Launch power measurement in background in continuous mode
mkdir -p data
./powerapp \
        -n $NUM_SAPLES                          \
        -t $POWERAPP_US                         \
        -p 1                                    \
        -o data/$(basename $1 .h5.xmodel).csv   \
        &
# Save PID for later
POWERAPP_PID=$!

# Wait for powerapp to init
sleep 1

# Launch 
./app_O0 $1             \
    $IMAGE_PATH         \
    $LABELS             \
    $RUN_SOFTMAX        \
    $MAX_IMAGES         \
    $NUM_THREADS        \
    > /dev/null           # Suppress output to save CPU bandwidth

# Stop power measurement
# Give time to powerapp to flush to files
# sleep 2; kill $POWERAPP_PID

# Wait for all the samples to be collected
wait $POWERAPP_PID