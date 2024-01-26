# DATASET=cifar10
DATASET=cifar100

# MODEL=ResNet
# MODEL=cifar100*subDenseNet-185
MODEL=cifar100*DenseNet-201

XMODEL=$( find /home/root/TSUSC/xmodels/ -name ${MODEL}.h5.xmodel ) 
echo "Running $XMODEL"

time \
XMODEL_BASENAME=$(basename $XMODEL .h5.xmodel) \
DEBUG_RUN=1 \
./app_O0 \
    $XMODEL \
    /home/root/datasets/${DATASET}/test_set/img/ \
    /home/root/datasets/${DATASET}/labels.txt \
    0 \
    1000 \
    1 \
    data/${DATASET} 