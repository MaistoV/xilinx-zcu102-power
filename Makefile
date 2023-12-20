BOARD_IP  = 192.168.1.240
DATA_DIR  = ${PWD}/data
BOARD_DIR = /home/root/TSUSC
ARTIFACTS = powerapp/powerapp app/app_O0 scripts/

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
	${MAKE} plot_calibration

#########
# Plots #
#########

plots:
	cd plots; python plot_0.py

plots_calibration:
	cd plots; python plot_calibration.py
	
.PHONY: powerapp app plots

clean:
	${MAKE} -C powerapp clean
	rm -vrf app/app_O0

.PHONY: tmp
tmp:
	-scp root@192.168.1.240:/home/root/TSUSC/powerapp400.csv.raw_currents powerapp400.csv.raw_currents.csv 
	-scp root@192.168.1.240:/home/root/TSUSC/powerapp400.csv			  powerapp400.csv
	# browse powerapp400.csv.raw_currents.csv 
	browse powerapp400.csv