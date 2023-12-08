import matplotlib.pyplot as plt
import numpy
import glob
import pandas
import re

# Data directory
data_dir = "../data/"

net_names = glob.glob(data_dir + "*") 
print(net_names)
exit

# Loop over image and thread
# data_net = [[0. for _ in range()) ] for _ in range(len(net_names))]
power_nets = list(range(len(net_names)))
for i in range(0,len(net_names)):
    power_nets[i] = pandas.read_csv(net_names[i], sep=";", index_col=0 )

    plt.figure("Power")
    for column in power_nets[i]:
        plt.plot( power_nets[i][column], label=column    )
    # plt.semilogy(power_nets[i]["Sample"], power_nets[i]["PS mW"    ], label="PS"    )
    # plt.semilogy(power_nets[i]["Sample"], power_nets[i]["PL mW"    ], label="PL"    )
    # plt.semilogy(power_nets[i]["Sample"], power_nets[i]["MGT mW"   ], label="MGT"   )
    # plt.semilogy(power_nets[i]["Sample"], power_nets[i]["Total mW" ], label="Total" )
    plt.legend()
    plt.xlabel("Samples")
    plt.ylabel("mW")
plt.show()

net_names = [ "raw_powerapp" ]
power_rails = [
		"VCCPSINTFP",
		"VCCPSINTLP",
		"VCCPSAUX",
		"VCCPSPLL",
		"MGTRAVCC",
		"MGTRAVTT",
		"VCCPSDDR",
		"VCCOPS",
		"VCCOPS3",
		"VCCPSDDRPLL",
		"VCCINT",
		"VCCBRAM",
		"VCCAUX",
		"VCC1V2",
		"VCC3V3",
		"VADJ_FMC",
		"MGTAVCC"#,
		# "MGTAVTT" # forgot to save it
        ]
raw_nets = list(range(len(net_names)))
for i in range(0,len(net_names)):
    raw_nets[i] = pandas.read_csv(data_dir + net_names[i] + ".csv", sep="; ", index_col=0 )

    plt.figure("Raw measures mA*mV/1000")
    for pr in power_rails:
        plt.plot( raw_nets[i][pr + " mA"] * raw_nets[i][pr + " mV"], label=pr    )
plt.legend()
plt.xlabel("Samples")
plt.ylabel("mW")

plt.show()