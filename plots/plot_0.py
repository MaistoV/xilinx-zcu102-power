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
net_names = ["" for net in range(len(net_paths))]
for net in range(0,len(net_paths)):
	net_names[net] = net_paths[net][len(data_dir):-4]

num_layers = [0 for net in range(len(net_paths))]
for net in range(0,len(net_names)):
	num_layers[net] = int(net_names[net][13:-3])

# Read data
power_nets = list(range(len(net_paths)))
for net in range(0,len(net_paths)):
	power_nets[net] = pandas.read_csv(net_paths[net], sep=";", index_col=0 )


###################
# Timestamps data #
###################
 
time_nets = [0. for net in range(len(net_paths))]
for net in range(0,len(net_paths)):
	time_nets[net] = pandas.read_csv(net_paths[net] + ".time", sep=";" )

##############
# Power plot #
##############

plt.figure("Power", figsize=[15,15])
ax = plt.subplot(2,4,1) # Assuming 8 nets
for net in range(0,len(net_paths)):
	ax = plt.subplot(2, 4, net+1, sharey=ax) # Assuming 8 nets

	# # Plot all
	# for column in power_nets[net]:
	# 	plt.plot( power_nets[net][column], label=column	)

	# Plot just PL and PS
	plt.plot(power_nets[net]["Timestamp"], power_nets[net]["PS mW"	], label="PS"	)
	plt.plot(power_nets[net]["Timestamp"], power_nets[net]["PL mW"	], label="PL"	)
	
	# Plot timeframe boundary
	plt.axvline(x=time_nets[net]["Start(sec)"].to_numpy(), linestyle="--", label="Timeframe")
	plt.axvline(x=time_nets[net]["End(sec)"  ].to_numpy(), linestyle="--")

	# Decorate
	if ( net == 0 ):
		plt.legend()
	plt.title(net_names[net])
	plt.xlabel("Time")
	plt.ylabel("mW")

plt.savefig("power.png", bbox_inches="tight")

###############
# Energy plot #
###############

# Compute integral in the target time frame
TIME_BIN_s = 0.02 # 20000 us
plt.figure("Energy from power", figsize=[15,15])
pl_energy_mJ = [0. for net in range(len(power_nets))]
ps_energy_mJ = [0. for net in range(len(power_nets))]
# Loop over nets
for net in range(0,len(power_nets)):
	# Loop over samples
	for sample in range(0,len(power_nets[net])):
		# If this sample is in the timeframe
		if (
			power_nets[net]["Timestamp"][sample] > time_nets[net]["Start(sec)"].to_numpy()
			and power_nets[net]["Timestamp"][sample] < time_nets[net]["End(sec)"].to_numpy()
			):
			# Accumulate
			pl_energy_mJ[net] += power_nets[net]["PL mW"][sample]
			ps_energy_mJ[net] += power_nets[net]["PS mW"][sample]
	# Multiply with time bin (constant across samples)
	pl_energy_mJ[net] *= TIME_BIN_s
	ps_energy_mJ[net] *= TIME_BIN_s

NUM_FRAMES=1000
# J / frame
print("J/frame(32x32)", (pl_energy_mJ[-1] + ps_energy_mJ[-1]) / 1000 / NUM_FRAMES)

plt.plot(num_layers, pl_energy_mJ, label="PL", marker="o" )
plt.plot(num_layers, ps_energy_mJ, label="PS", marker="o" )
plt.plot(num_layers[-1], pl_energy_mJ[-1], marker="*", markersize=15, color="r", label="Teacher")
plt.plot(num_layers[-1], ps_energy_mJ[-1], marker="*", markersize=15, color="r" )
plt.legend()
plt.xlabel("Number of layers")
plt.ylabel("mJ")
plt.savefig("Energy from power.png", bbox_inches="tight")

plt.figure("Relative energy efficiency", figsize=[15,15])
tot_energy_mJ = [0. for net in range(len(power_nets))]
relative_energy = [0. for net in range(len(power_nets))]
for net in reversed(range(0,len(tot_energy_mJ))):
	tot_energy_mJ[net] = pl_energy_mJ[net] + pl_energy_mJ[net]
	relative_energy[net] = tot_energy_mJ[net] / tot_energy_mJ[-1]
plt.plot(num_layers, relative_energy, marker="o" )
plt.xlabel("Number of layers")
plt.title("Student / Teacher energy gain")
plt.xticks(ticks=num_layers)
plt.savefig("Relative energy.png", bbox_inches="tight")
	
#####################
# Raw measures data #
#####################

suffix_currents = ".csv.raw_currents"
suffix_voltages = ".csv.raw_voltages"
net_paths_raw_voltages = glob.glob(data_dir + "*" + suffix_voltages) 
net_paths_raw_currents = glob.glob(data_dir + "*" + suffix_currents) 
net_paths_raw_voltages.sort()
net_paths_raw_currents.sort()
net_names_raw = ["" for net in range(len(net_paths_raw_voltages))]
for net in range(0,len(net_paths_raw_voltages)):
	net_names_raw[net] = net_paths_raw_voltages[net][len(data_dir):(-1*len(suffix_voltages))]

power_rails = [
		# # Cortex-As (PS)
		"VCCPSINTFP",	# Dominant
		"VCCPSINTLP",
		"VCCPSAUX",	
		"VCCPSPLL",	
		"VCCPSDDR",		# Dominant
		# "VCCOPS",		# Don't use
		# "VCCOPS3",	# Don't use
		"VCCPSDDRPLL",
		# FPGA (PL)
		"VCCINT",		# Dominant
		"VCCBRAM",
		"VCCAUX",
		"VCC1V2",
		"VCC3V3",
		# MGT
		"MGTRAVCC",
		"MGTRAVTT",
		"MGTAVCC",
		"MGTAVTT",
		"VCC3V3",
		]

# Read data
raw_nets_voltages = list(range(len(net_names_raw)))
raw_nets_currents = list(range(len(net_names_raw)))
for net in range(0,len(net_names_raw)):
	raw_nets_currents[net] = pandas.read_csv( net_paths_raw_currents[net], sep=";", index_col=0 )
	raw_nets_voltages[net] = pandas.read_csv( net_paths_raw_voltages[net], sep=";", index_col=0 )

#####################
# Raw measures plot #
#####################
plt.figure("Power from raw data", figsize=[15,15])
# ax = plt.subplot(2,4,1) # Assuming 8 nets
# for net in range(0,len(net_names_raw)):	
for net in range(5,6):	
	# ax = plt.subplot(2, 4, net+1, sharey=ax) # Assuming 8 nets
	
	# loop over power rails
	for pr in power_rails:
		plt.plot(raw_nets_currents[net]["Timestamp"], (raw_nets_currents[net][pr + " mA"] * raw_nets_voltages[net][pr + " mV"]) / 1000., label=pr	)

	# Plot timeframe boundary
	plt.axvline(x=time_nets[net]["Start(sec)"].to_numpy(), linestyle="--", label="Timeframe")
	plt.axvline(x=time_nets[net]["End(sec)"  ].to_numpy(), linestyle="--")

	# Decorate
	if ( net == 0 ):
		plt.legend()
	plt.legend()
	plt.title(net_names_raw[net])
	plt.xlabel("Time")
	plt.xticks([])
	plt.ylabel("mW")


plt.savefig("raw.png", bbox_inches="tight")

plt.show()