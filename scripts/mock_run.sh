DATASET=cifar100
# DATASET=CIFAR-100-dataset-main

# MODEL=ResNet
# MODEL=cifar100*subDenseNet-185
# MODEL=cifar100*DenseNet-201

XMODEL="xmodels/arch4096_unet_cityscapes64.xmodel"
echo "Running $XMODEL"
export XMODEL_BASENAME=$(basename $XMODEL)

time \
DEBUG_RUN=1 \
./app_O0 \
    ${XMODEL} \
    datasets/cifar100/ \
    NULL \
    0 \
    1000 \
    1 \
    data/${DATASET}
