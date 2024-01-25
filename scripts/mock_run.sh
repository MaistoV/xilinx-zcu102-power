# DATASET=cifar10
DATASET=cifar100

# MODEL=ResNet
MODEL=DenseNet

XMODEL=$( ls /home/root/TSUSC/xmodels/new_3.0/${DATASET}/${MODEL}s/${DATASET}_${MODEL}-*.h5.xmodel ) 

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