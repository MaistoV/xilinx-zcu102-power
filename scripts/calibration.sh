# Sampling periods
TEST_T=20000 # same as tests
MEAS_T=80000
MIN_T=10000

# Keep -n * -t constant to 800*20000
CONST_meas=8000000
SAMPLES_meas=$(($CONST_meas/$MEAS_T))
# Keep -n * -t constant to 100*20000
CONST_test=2000000
SAMPLES_test=$(($CONST_test/$MEAS_T))

# Derive bandwidth
TEST_B=$(bc -l <<< 1./$TEST_T)
MEAS_B=$(bc -l <<< 1./$MEAS_T)
MAX_B=$(bc -l <<< 1./$MIN_T)
echo TEST_B $TEST_B
echo MEAS_B $MEAS_B
echo "MIN_B " $MAX_B
EXPR="$MAX_B - $TEST_B - $MEAS_B"
echo REAS_B $(bc -l <<< $EXPR)
# NOTE: this assumes the system to be linear, which it is not
echo $(bc -l <<< $EXPR) | \
    grep "-" && echo "Not enough bandwidth available" && exit

# Output
OUT_DIR=data/calibration
mkdir -p $OUT_DIR

sleep 1

# Launch measurement
./powerapp -p 1 -n $SAMPLES_meas -t $MEAS_T -o $OUT_DIR/calibration_measure.csv > /dev/null  &

sleep 2

# Launch test
./powerapp -n $SAMPLES_test -t $TEST_T -o $OUT_DIR/calibration_test.csv 

# Wait for measurement to complete
wait