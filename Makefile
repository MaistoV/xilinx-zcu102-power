BOARD_IP  = 192.168.1.240
DATA_DIR  = ${PWD}/data
BOARD_DIR = /home/root/TSUSC
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
	scp -r $^ root@${BOARD_IP}:${BOARD_DIR}/

scp_models: ${MODELS_DIR}
	scp -r $^ root@${BOARD_IP}:${BOARD_DIR}/

recover_data:
	mkdir -p ${DATA_DIR}
	scp -r root@${BOARD_IP}:${BOARD_DIR}/data/* ${DATA_DIR}/

#########
# Tests #
#########
test: scp
	${MAKE} ssh SSH_CMD="cd TSUSC; time bash -x scripts/launch_experiment_0.sh"
	${MAKE} recover_data
	${MAKE} plot

calibration: scp
	${MAKE} ssh SSH_CMD="cd TSUSC; time bash -x scripts/calibration.sh"
	${MAKE} recover_data
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
PLOT_ROOTS := ./plots
plots:
	cd ${PLOT_ROOTS}; \
	python plots.py cifar10  resnets   ResNet-50   ; \
	python plots.py cifar100 resnets   ResNet-50	 ; \
	python plots.py cifar10  densenets DenseNet-201; \
	python plots.py cifar100 densenets DenseNet-201

plots_pre-process: 
	cd ${PLOT_ROOTS}; \
	python plot_pre-process.py cifar10  resnets   ResNet-50   ; \
	python plot_pre-process.py cifar100 resnets   ResNet-50	  ; \
	python plot_pre-process.py cifar10  densenets DenseNet-201; \
	python plot_pre-process.py cifar100 densenets DenseNet-201

plots_calibration:
	cd ${PLOT_ROOTS}; python plot_calibration.py

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
