# xilinx-zcu102-power
Simplified collection of tools used to calibrate and measure power draw on the ZCU102 power rails.


## Getting Started
Setup cross-compilation environment from either:
- Vitis-AI host setup
- Petalinux SDK installation, e.g.:
```bash
soruce <petalinux installation>/environment-setup-cortexa72-cortexa53-xilinx-linux
```

Or just use the provided setup script:
```bash
source settings.sh
```

## Tree Structure
```bash
├── app # A Vitis-AI example application is provided as measuring subject.
├── data          # Directory for collected data
├── Makefile      # Top Makefile
├── plots         # Scripts for plots
├── powerapp      # Power-measuring app
├── README.md     # this file
├── scripts       # Measurement and claibration scripts
└── settings.sh   # setup script
```

## Tools and versions
Tools and versions used:
  * Vitis-AI 3.0
  * DPUCZDX8G IP v4.1
  * XCZU9EG MPSoC
  * Petalinux 2022.2
    * zcu102 bsp 2022.2
    * DPU Vivado flow TRD
  * Vivado 2022.2
  * Tensorflow 2, Keras 2

> NOTE: Some figures, raw and pre-processed data have been imported in this repo under the data/ folder.
