BOARD_IP  = 192.168.1.240
DATA_DIR  = ${PWD}/data
BOARD_DIR = /home/root/TSUSC
ARTIFACTS = powerapp/powerapp app/app_O0 scripts/

all: ${ARTIFACTS}

powerapp: powerapp/powerapp
powerapp/powerapp: powerapp/src/powerapp.c powerapp/src/powerapp.h
	${MAKE} -C powerapp powerapp

app: app/app_O0
app/app_O0: app/src/main.cc
	cd app/; bash build.sh

ssh:
	ssh root@${BOARD_IP}

scp: ${ARTIFACTS}
	scp -r $^ root@${BOARD_IP}:${BOARD_DIR}/

scp_models: ${MODELS_DIR}
	scp -r $^ root@${BOARD_IP}:${BOARD_DIR}/

recover_data:
	mkdir -p ${DATA_DIR}
	scp -r root@${BOARD_IP}:${BOARD_DIR}/data/* ${DATA_DIR}/
#	Post process


plots:
	cd plots; python plot_0.py

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