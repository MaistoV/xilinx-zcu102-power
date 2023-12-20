# Sampling periods
TEST_T_us=20000 # 20ms (same as tests)
MEAS_T_us=20000 # 80ms
MIN_T_us=10000  # 10ms

# Keep latency constant (-n * -t)
LATENCY_test_us=8000000 # 8 seconds (same as tests)
LATENCY_meas_us=$(($LATENCY_test_us*4))
SAMPLES_meas=$(($LATENCY_meas_us/$MEAS_T_us))
SAMPLES_test=$((2*$LATENCY_test_us/$TEST_T_us))

# Before launching measures
SLEEP_TIME_BEFORE=3
# Before launching test
SLEEP_TIME_BETWEEN=$(($LATENCY_meas_us/1000000/4))

# # Derive bandwidth
# TEST_B=$(bc -l <<< 1./$TEST_T_us)
# MEAS_B=$(bc -l <<< 1./$MEAS_T_us)
# MAX_B=$(bc -l <<< 1./$MIN_T_us)
# echo TEST_B $TEST_B
# echo MEAS_B $MEAS_B
# echo "MIN_B " $MAX_B
# EXPR="$MAX_B - $TEST_B - $MEAS_B"
# echo REAS_B $(bc -l <<< $EXPR)
# # NOTE: this assumes the system to be linear, which it is not
# echo $(bc -l <<< $EXPR) | \
#     grep "-" && echo "Not enough bandwidth available" && exit

# Output
OUT_DIR=data/calibration
mkdir -p $OUT_DIR

echo "This run is going to last $(bc -l <<< $SLEEP_TIME_BEFORE+$LATENCY_meas_us/1000000.) seconds"

sleep $SLEEP_TIME_BEFORE

# Launch measurement
./powerapp                              \
    -p 1                                \
    -n $SAMPLES_meas                    \
    -t $MEAS_T_us                       \
    -o $OUT_DIR/calibration_measure.csv \
    > /dev/null  &

sleep $SLEEP_TIME_BETWEEN

# Launch test
./powerapp                           \
    -p 1                             \
    -n $SAMPLES_test                 \
    -t $TEST_T_us                    \
    -o $OUT_DIR/calibration_test.csv \
    > /dev/null

# Wait for measurement to complete
wait