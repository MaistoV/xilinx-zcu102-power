DATA_DIR  = ${PWD}/data
BOARD_ROOT_DIR = /home/root/TSUSC
BOARD_XMODELS_DIR = ${BOARD_ROOT_DIR}/xmodels
ARTIFACTS = powerapp/powerapp app/app_O0 scripts/

# Parameters
# TODO: extend for automation
# DATASETS = cifar10 cifar100
# NETS	 = "resnet ResNet-50" "densenets DenseNet-201"

all: ${ARTIFACTS}

############
# Binaries #
############
powerapp: powerapp/powerapp
powerapp/powerapp: powerapp/src/powerapp.c powerapp/src/powerapp.h
	${MAKE} -C powerapp powerapp

app: app/app_O0
app/app_O0: app/src/main.cc
	cd app/; bash build.sh

#########
# Utils #
#########

ssh:
	ssh root@${BOARD_IP} "${SSH_CMD}"

scp: ${ARTIFACTS}
	scp -r $^ root@${BOARD_IP}:${BOARD_ROOT_DIR}/

scp_models: ${XMODELS_DIR}
ifndef XMODELS_DIR
	$(error "[ERROR] XMODELS_DIR is unset, set it to the root directory of your compilex xmodels")
endif
	scp -r $^ root@${BOARD_IP}:${BOARD_XMODELS_DIR}

recover_data:
	mkdir -p ${DATA_DIR}
	scp -r root@${BOARD_IP}:${BOARD_ROOT_DIR}/data/cifar10*/* ${DATA_DIR}/raw/

###############
# Experiments #
###############
experiments: scp
	${MAKE} ssh SSH_CMD="time bash scripts/launch_experiment_0.sh"
	${MAKE} recover_data
	${MAKE} plots_pre-process
	${MAKE} plots

mock_run: app
	${MAKE} ssh SSH_CMD="bash scripts/mock_run.sh"

calibration: scp
	${MAKE} ssh SSH_CMD="time bash -x scripts/calibration.sh"
	scp -r root@${BOARD_IP}:${BOARD_ROOT_DIR}/calibration ${DATA_DIR}/
	${MAKE} plots_calibration

calibration_loop:
	${MAKE} calibration # 1
	${MAKE} calibration # 2
	${MAKE} calibration # 3
	${MAKE} calibration # 4
	${MAKE} calibration # 5
	${MAKE} calibration # 6
	${MAKE} calibration # 7
	${MAKE} calibration # 8
	${MAKE} calibration # 9
	${MAKE} calibration # 10

#########
# Plots #
#########
PLOT_ROOT := ./plots
plots:
	cd ${PLOT_ROOT}; \
	${PYTHON} plots.py  ResNet-50		cifar10 	; \
	${PYTHON} plots.py  ResNet-50		cifar100	; \
	${PYTHON} plots.py  DenseNet-201	cifar10 	; \
	${PYTHON} plots.py  DenseNet-201	cifar100

plots_pre-process:
	cd ${PLOT_ROOT}; \
	${PYTHON} plots_pre-process.py ResNet-50  	 cifar10	; \
	${PYTHON} plots_pre-process.py ResNet-50  	 cifar100	; \
	${PYTHON} plots_pre-process.py DenseNet-201  cifar10	; \
	${PYTHON} plots_pre-process.py DenseNet-201  cifar100

plots_calibration:
	cd ${PLOT_ROOT}; ${PYTHON} plots_calibration.py

#########
# Clean #
#########
clean:
	${MAKE} -C powerapp clean
	rm -vrf app/app_O0

###########
# PHONYes #
###########
.PHONY: powerapp app plots
