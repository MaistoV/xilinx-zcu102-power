DATASET=cifar100
# DATASET=CIFAR-100-dataset-main

# MODEL=ResNet
# MODEL=cifar100*subDenseNet-185
# MODEL=cifar100*DenseNet-201
MODEL=arch4096_TinyImagenet_vitis_ResNet-50

XMODEL=$( find /home/root/JSA/xmodels/ -name ${MODEL}.xmodel )
# XMODEL=/home/root/app/model/resnet50.xmodel
echo "Running xmodel: $XMODEL"

mkdir -p data/${DATASET}
mkdir -p tmp

time \
XMODEL_BASENAME=$(basename $XMODEL .h5.xmodel) \
DEBUG_RUN=1 \
./app_O0 \
    $XMODEL \
    /home/root/JSA/datasets/${DATASET}/ \
    "/home/root/JSA/datasets/${DATASET}/labels.txt" \
    0 \
    1000 \
    1 \
    tmp/