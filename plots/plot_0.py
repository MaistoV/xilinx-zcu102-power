import matplotlib.pyplot as plt
import numpy
import glob
import pandas
import re

# Data directory
data_dir = "../data/"

##############
# Power data #
##############

net_paths = glob.glob(data_dir + "*.csv") 
net_paths.sort()
net_names = ["" for i in range(len(net_paths))]
for i in range(0,len(net_paths)):
	net_names[i] = net_paths[i][len(data_dir):-4]

num_layers = [0 for i in range(len(net_paths))]
for i in range(0,len(net_names)):
	num_layers[i] = int(net_names[i][13:-3])

# Read data
power_nets = list(range(len(net_paths)))
for i in range(0,len(net_paths)):
	power_nets[i] = pandas.read_csv(net_paths[i], sep=";", index_col=0 )

##############
# Power plot #
##############

plt.figure("Power", figsize=[15,15])
ax = plt.subplot(2,4,1) # Assuming 8 nets
for i in range(0,len(net_paths)):
	ax = plt.subplot(2, 4, i+1, sharey=ax, sharex=ax) # Assuming 8 nets

	# # Plot all
	# for column in power_nets[i]:
	# 	plt.plot( power_nets[i][column], label=column	)

	# Plot just PL and PS
	plt.plot(power_nets[i]["PS mW"	], label="PS"	)
	plt.plot(power_nets[i]["PL mW"	], label="PL"	)

	# Decorate
	plt.legend()
	plt.title(net_names[i])
	plt.xlabel("Samples")
	plt.ylabel("mW")

plt.savefig("power.png", bbox_inches="tight")

###############
# Energy plot #
###############

TIME_BIN_s = 0.02
NUM_SAMPLES = 400
RUNTIME = TIME_BIN_s * NUM_SAMPLES
plt.figure("Energy from power", figsize=[15,15])
pl_energy_mJ = [0. for i in range(len(power_nets))]
ps_energy_mJ = [0. for i in range(len(power_nets))]
for i in range(0,len(power_nets)):
	pl_energy_mJ[i] = power_nets[i]["PL mW"].sum() * RUNTIME
	ps_energy_mJ[i] = power_nets[i]["PS mW"].sum() * RUNTIME

NUM_FRAMES=1000
# J / frame
# print((pl_energy_mJ[-1] + ps_energy_mJ[-1]) / 1000 / NUM_FRAMES)
# exit()

# plt.plot(num_layers, pl_energy_mJ, label="PL", marker="o" )
# plt.plot(num_layers, ps_energy_mJ, label="PS", marker="o" )
# plt.plot(num_layers[-1], pl_energy_mJ[-1], marker="*", markerSize=15, color="r", label="Teacher")
# plt.plot(num_layers[-1], ps_energy_mJ[-1], marker="*", markerSize=15, color="r" )
# plt.legend()
# plt.xlabel("Number of layers")
# plt.ylabel("mJ")
# plt.savefig("Energy from power.png", bbox_inches="tight")

plt.figure("Relative energy efficiency")
tot_energy_mJ = [0. for i in range(len(power_nets))]
relative_energy = [0. for i in range(len(power_nets))]
for i in reversed(range(0,len(tot_energy_mJ))):
	tot_energy_mJ[i] = pl_energy_mJ[i] + pl_energy_mJ[i]
	relative_energy[i] = tot_energy_mJ[i] / tot_energy_mJ[-1]
plt.plot(num_layers, relative_energy, marker="o" )
plt.xlabel("Number of layers")
plt.title("Student / Teacher energy gain")
plt.xticks(ticks=num_layers)
plt.savefig("Relative energy.png", bbox_inches="tight")

plt.show()
	
#####################
# Raw measures data #
#####################

suffix_currents = ".csv.raw_currents"
suffix_voltages = ".csv.raw_voltages"
net_paths_raw_voltages = glob.glob(data_dir + "*" + suffix_voltages) 
net_paths_raw_currents = glob.glob(data_dir + "*" + suffix_currents) 
net_paths_raw_voltages.sort()
net_paths_raw_currents.sort()
net_names_raw = ["" for i in range(len(net_paths_raw_voltages))]
for i in range(0,len(net_paths_raw_voltages)):
	net_names_raw[i] = net_paths_raw_voltages[i][len(data_dir):(-1*len(suffix_voltages))]

power_rails = [
		# # Cortex-As (PS)
		"VCCPSINTFP",	# Dominant
		# "VCCPSINTLP",
		# "VCCPSAUX",	
		# "VCCPSPLL",	
		"VCCPSDDR",		# Dominant
		# "VCCOPS",		# Don't use
		# "VCCOPS3",	# Don't use
		# "VCCPSDDRPLL",
		# FPGA (PL)
		"VCCINT",		# Dominant
		# "VCCBRAM",
		# "VCCAUX",
		# "VCC1V2",
		# "VCC3V3",
		# # MGT
		# "MGTRAVCC",
		# "MGTRAVTT",
		# "MGTAVCC",
		# "MGTAVTT",
		# "VCC3V3",
		]

# Read data
raw_nets_voltages = list(range(len(net_names_raw)))
raw_nets_currents = list(range(len(net_names_raw)))
plt.figure("Power from raw data", figsize=[15,15])
ax = plt.subplot(2,4,1) # Assuming 8 nets
for i in range(0,len(net_names_raw)):
# for i in range(0,1):
	ax = plt.subplot(2, 4, i+1, sharey=ax, sharex=ax) # Assuming 8 nets

	raw_nets_currents[i] = pandas.read_csv( net_paths_raw_currents[i], sep=";", index_col=0 )
	raw_nets_voltages[i] = pandas.read_csv( net_paths_raw_voltages[i], sep=";", index_col=0 )

#####################
# Raw measures plot #
#####################

for i in range(0,len(net_names_raw)):	
	for pr in power_rails:
		plt.plot( (raw_nets_currents[i][pr + " mA"] * raw_nets_voltages[i][pr + " mV"]) / 1000., label=pr	)

	# Decorate
	if ( i == 0 ):
		plt.legend()
	plt.title(net_names_raw[i])
	plt.xlabel("Samples")
	plt.ylabel("mW (mA*mV/1000)")


plt.savefig("raw.png", bbox_inches="tight")




plt.show()