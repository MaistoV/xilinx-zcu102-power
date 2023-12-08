# Run application with specified xmodel

# Tunable parameters
MAX_IMAGES=100
POWERAPP_US=10000

# Fixed parameters
NUM_THREADS=1
RUN_SOFTMAX=0
LABELS=/home/root/datasets/CIFAR10/labels.txt
IMAGE_PATH=/home/root/datasets/CIFAR10/test_set/img/

# Launch power measurement in background in continuous mode
mkdir -p data
./powerapp -c 1                                 \
        -t 1000                                 \
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

# Wait for powerapp to flush
sleep 1

# Stop power measurement
kill $POWERAPP_PID
