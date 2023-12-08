BOARD_IP  = 192.168.1.240
DATA_DIR  = ${PWD}/data
BOARD_DIR = /home/root/TSUSC
ARTIFACTS = powerapp/powerapp app/app_O0 scripts/

all: ${ARTIFACTS}

powerapp/powerapp: powerapp/src/powerapp.c
	${MAKE} -C powerapp powerapp

app/app_O0: app/src/main.cc
	cd app/; bash build.sh

ssh:
	ssh root@${BOARD_IP}

scp: ${ARTIFACTS}
	scp -r $^ root@${BOARD_IP}:${BOARD_DIR}/

recover_data:
	mkdir -p ${DATA_DIR}
	scp root@${BOARD_IP}:${BOARD_DIR}/data/*.csv* ${DATA_DIR}/

plots:
	cd plots; python plot_0.py

.PHONY: powerapp app plots

clean:
	${MAKE} -C powerapp clean
	rm -rf app/app_O0
