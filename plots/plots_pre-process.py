#!/usr/bin/python3
import os
import numpy as np
import re
import matplotlib.pyplot as plt
import glob
import pandas
import sys

plt.rcParams.update({'font.size': 20})

# Input data directory
data_dir = "../data/raw/"
dataset = "cifar10"
calibration_dir = "../data/calibration/"
# Output directory
figures_dir = "./figures/pre-process/"
out_dir = "../data/pre-processed/"

# teacher="ResNet-50"
teacher="DenseNet-201"

if len(sys.argv) >= 2:
	teacher = sys.argv[1]
if len(sys.argv) >= 3:
	dataset = sys.argv[2]

print("teacher: ", teacher)
print("dataset: ", dataset)

base_nets = re.sub("-.+", "", teacher)

##############
# Power data #
##############
wildcard_path = data_dir + dataset + "_*" + base_nets + "*.csv"
print("Reading from", wildcard_path)
net_paths = glob.glob(wildcard_path)
assert(len(net_paths) != 0)
# Sort net paths from shallower to deeper student, then teacher
# For DenseNet and ResNet, the teacher comes alphabetically before students (e.g., subResNet)
net_paths.sort()
net_paths = net_paths[1:] + net_paths[: 1]
net_names = ["" for net in range(len(net_paths))]
# print("net_paths: ", net_paths)

for net in range(0,len(net_paths)):
	# basename
	net_names[net] = net_paths[net][len(data_dir + dataset)+1:-4]
	net_names[net] = re.sub("KD_|_T.+|_sc.+", "", net_names[net])
print("net_names ", net_names)

num_layers = [0 for net in range(len(net_paths))]
for net in range(0,len(net_names)):
	num_layers[net] = re.sub("sub", "", net_names[net])
	num_layers[net] = re.sub(base_nets, "", num_layers[net])
	num_layers[net] = int(re.sub("-|_.+", "", num_layers[net]))
num_layers.sort()
print("num_layers: ", num_layers)

# Read data
power_nets = list(range(len(net_paths)))
for net in range(0,len(net_paths)):
	power_nets[net] = pandas.read_csv(net_paths[net], sep=";", index_col=0 )

############
# Raw data #
############

suffix_currents = ".raw_currents"
suffix_voltages = ".raw_voltages"

print(wildcard_path + "*" + suffix_voltages)
print(wildcard_path + "*" + suffix_currents)
net_paths_raw_voltages = glob.glob(wildcard_path + "*" + suffix_voltages)
net_paths_raw_currents = glob.glob(wildcard_path + "*" + suffix_currents)
net_paths_raw_voltages.sort()
net_paths_raw_currents.sort()
# Sort net paths from shallower to deeper student, then teacher
# For DenseNet and ResNet, the teacher comes alphabetically before students (e.g., subResNet)
net_paths_raw_voltages = net_paths_raw_voltages[1:] + net_paths_raw_voltages[: 1]
net_paths_raw_currents = net_paths_raw_currents[1:] + net_paths_raw_currents[: 1]
print(net_paths_raw_currents)

assert(len(net_paths_raw_voltages) != 0)
assert(len(net_paths_raw_voltages) != 0)

net_names_raw = ["" for net in range(len(net_paths_raw_voltages))]
for net in range(0,len(net_paths_raw_voltages)):
	# basename
	net_names_raw[net] = net_paths_raw_voltages[net][len(data_dir + dataset)+1:(-1*len(suffix_voltages))]


# Read data
raw_nets_voltages = list(range(len(net_names_raw)))
raw_nets_currents = list(range(len(net_names_raw)))
for net in range(0,len(net_names_raw)):
	raw_nets_currents[net] = pandas.read_csv( net_paths_raw_currents[net], sep=";", index_col=0 )
	raw_nets_voltages[net] = pandas.read_csv( net_paths_raw_voltages[net], sep=";", index_col=0 )

assert(len(raw_nets_currents) != 0)
assert(len(raw_nets_voltages) != 0)

###################
# Correction data #
###################

# Read calibration data
print(calibration_dir + "calibration.csv")
calibration_path = glob.glob(calibration_dir + "calibration.csv")
calibration_mean = pandas.read_csv(calibration_path[0], sep=";", header=None).to_numpy().mean()
print("Calibration mean:", calibration_mean, " mW")

# Adjust measures for powerapp
for net in range(0,len(net_paths)):
	power_nets[net]["Total mW"] -= calibration_mean
	power_nets[net]["PS mW"]	-= calibration_mean

# TODO: add calibration also for raw measures?

###################
# Timestamps data #
###################

time_nets = [0. for _ in range(len(net_paths))]
for net in range(0,len(net_paths)):
	# print(net_paths[net] + ".time")
	time_nets[net] = pandas.read_csv(net_paths[net] + ".time", sep=";" )

#######################
# Offset to zero time #
#######################

# Realign timestamps to zero
for net in range(0,len(net_paths)):
	offset = power_nets[net]["Timestamp"].loc[0]
	power_nets[net]["Timestamp"] -= offset
	time_nets [net]				 -= offset

############################
# Compute and save runtime #
############################

# Filename
base_nets_lower = base_nets.lower() + "s"
filename = out_dir + dataset + "_" + base_nets_lower + "_" + "runtime.csv"
print("Writing to", filename)

# Open file
file1 = open(filename, "w")

# Header
file1.write("Network,Runtime(s)\n")

# Compute and write to file
runtime_net = [0. for net in range(len(net_paths))]
for net in range(0,len(net_paths)):
	runtime_net[net] = time_nets[net]["End(sec)"].to_numpy() - time_nets[net]["Start(sec)"].to_numpy()
	print(runtime_net[net])
	# print out students first
	if "sub" in os.path.basename(net_paths[net]):
		file1.write(net_names[net] + "," + str(runtime_net[net][0]) + "\n")
	else:
		# Save teacher index
		teacher_index = net
# Print out teacher
file1.write(net_names[teacher_index] + "," + str(runtime_net[teacher_index][0]) + "\n")

# Close file
file1.close()

# Realign timestamps to zero
for net in range(0,len(net_names_raw)):
	offset = raw_nets_currents[net]["Timestamp"].loc[0]
	raw_nets_currents[net]["Timestamp"] -= offset
	raw_nets_voltages[net]["Timestamp"] -= offset

##############
# Power plot #
##############

# plt.figure("Power", figsize=[15,7])
# ax = plt.subplot(2,4,1) # Assuming 8
# for net in range(0,len(net_paths)):
# 	ax = plt.subplot(2, 4, net+1, sharey=ax) # Assuming 8

# 	# # Plot all
# 	# for column in power_nets[net]:
# 	# 	plt.plot( power_nets[net][column], label=column	)

# 	# Plot just PL and PS
# 	plt.plot(power_nets[net]["Timestamp"], power_nets[net]["PS mW"	], label="PS"	)
# 	plt.plot(power_nets[net]["Timestamp"], power_nets[net]["PL mW"	], label="PL"	)
# 	# plt.plot(power_nets[net]["Timestamp"], power_nets[net]["MGT mW"	], label="MGT"	)
# 	# plt.plot(power_nets[net]["Timestamp"], power_nets[net]["Total mW"	], label="Total"	)

# 	# Plot timeframe boundary
# 	plt.axvline(x=time_nets[net]["Start(sec)"].to_numpy(), linestyle="--", label="Timeframe")
# 	plt.axvline(x=time_nets[net]["End(sec)"  ].to_numpy(), linestyle="--")

# 	# Decorate
# 	if ( net == 0 ):
# 		plt.legend(fontsize=15)
# 	plt.title(net_names[net])
# 	plt.xlabel("Seconds")
# 	plt.ylabel("mW")

# plt.savefig(figures_dir + dataset + "_" + base_nets + "_power.png", bbox_inches="tight")

###############
# Energy plot #
###############

# Compute integral in the target time frame
TIME_BIN_s = 0.024 # 24000 us
pl_energy_mJ = [0. for net in range(len(power_nets))]
ps_energy_mJ = [0. for net in range(len(power_nets))]
pl_avg_power_mW = [0. for net in range(len(power_nets))]
ps_avg_power_mW = [0. for net in range(len(power_nets))]
# Loop over nets
for net in range(0,len(power_nets)):
	cnt = 0
	# Loop over samples
	for sample in range(0,len(power_nets[net])):
		# If this sample is in the timeframe
		if (
			power_nets[net]["Timestamp"][sample] > time_nets[net]["Start(sec)"].to_numpy()
			and power_nets[net]["Timestamp"][sample] < time_nets[net]["End(sec)"].to_numpy()
			):
			# Count up
			cnt += 1
			# Accumulate power
			pl_avg_power_mW[net] += power_nets[net]["PL mW"][sample]
			ps_avg_power_mW[net] += power_nets[net]["PS mW"][sample]
	# Multiply with time bin (constant across samples)
	pl_energy_mJ[net] = pl_avg_power_mW[net] * TIME_BIN_s
	ps_energy_mJ[net] = ps_avg_power_mW[net] * TIME_BIN_s
	# Compute average by dividing by number of samples
	pl_avg_power_mW[net] /= cnt
	ps_avg_power_mW[net] /= cnt
	print(net_names[net], "Number of samples:", cnt)

# Plot powers
total_power = [ (pl_avg_power_mW[i] + ps_avg_power_mW[i]) for i in range(0,len(power_nets))]
# total_power = [ ((pl_avg_power_mW[i] + ps_avg_power_mW[i]) / num_layers[i]) for i in range(0,len(power_nets))]


plt.figure("Power", figsize=[15,7])
# print(num_layers)
# plt.plot(num_layers, pl_avg_power_mW, label="PL", marker="o", linewidth=3, markersize=12 )
# plt.plot(num_layers, ps_avg_power_mW, label="PS", marker="d", linewidth=3, markersize=12 )
plt.plot(num_layers, total_power, label="Sum", marker="d", linewidth=3, markersize=12 )
plt.xticks(ticks=num_layers)
plt.legend()
plt.xlabel("Number of layers")
plt.ylabel("mW")
plt.grid()
plt.savefig(figures_dir + dataset + "_" + base_nets + "_Power.png", bbox_inches="tight", dpi=400)

# Dataframe per franca
header = ["Network", "Energy (mJ)"]
df_list = [["" for _ in header] for _ in range(len(power_nets))]
for i in range(0,len(net_names)):
	df_list[i][0] = base_nets + "-" + str(num_layers[i] )
	df_list[i][1] = str(ps_energy_mJ[i] + pl_energy_mJ[i])

df = pandas.DataFrame(df_list, index=None, columns=header)
filename = out_dir + dataset + "_" + base_nets_lower + "_energy.csv"
print("Writing to", filename)
df.to_csv(filename, index=False)

# # NUM_FRAMES=1000
# # J / frame
# # print("J/frame(32x32)", (pl_energy_mJ[-1] + ps_energy_mJ[-1]) / 1000 / NUM_FRAMES)
plt.figure("Energy from power", figsize=[15,7])

# Select P_Watts
if teacher == "ResNet-50":
	if dataset == "cifar10":
		P_Watts = 24.77 # ResNet / cifar10
	if dataset == "cifar100":
		P_Watts = 34.76 # ResNet / cifar100
if teacher == "DenseNet-201":
	if dataset == "cifar10":
		P_Watts = 25.90 # ResNet / cifar10
	if dataset == "cifar100":
		P_Watts = 32.35 # ResNet / cifar10

P_heuristic = [(P_Watts * 1e3 / runtime_net[l]) for l in range(0,len(num_layers))]
E_heuristic = [((pl_energy_mJ[l] + ps_energy_mJ[l]) / num_layers[l]) for l in range(0,len(num_layers))]
print("E_heuristic: ", E_heuristic)

print(runtime_net)

# print(num_layers)
plt.plot(num_layers, pl_energy_mJ, label="PL", marker="o", linewidth=3, markersize=12 )
plt.plot(num_layers, ps_energy_mJ, label="PS", marker="d", linewidth=3, markersize=12 )
plt.plot(num_layers, E_heuristic, "--", label="Heuristic",  linewidth=3, markersize=12 )
# plt.plot(num_layers[-1], pl_energy_mJ[-1], marker="*", markersize=15, color="r", label="Teacher")
# plt.plot(num_layers[-1], ps_energy_mJ[-1], marker="*", markersize=15, color="r" )
plt.xticks(ticks=num_layers)
plt.legend()
plt.xlabel("Number of layers")
plt.ylabel("mJ")
plt.grid()
plt.savefig(figures_dir + dataset + "_" + base_nets + "_Energy from power.png", bbox_inches="tight", dpi=400)

# plt.figure("Relative energy efficiency", figsize=[15,7])
# tot_energy_mJ = [0. for net in range(len(power_nets))]
# relative_energy = [0. for net in range(len(power_nets))]
# for net in reversed(range(0,len(tot_energy_mJ))):
# 	tot_energy_mJ[net] = pl_energy_mJ[net] + pl_energy_mJ[net]
# 	relative_energy[net] = tot_energy_mJ[net] / tot_energy_mJ[-1]
# plt.plot(num_layers, relative_energy, marker="o" )
# plt.xlabel("Number of layers")
# plt.ylabel("%")
# plt.yticks(np.arange(0,1.1,0.1), labels=np.arange(0,110,10))
# plt.title("Student / Teacher energy gain")
# plt.savefig(figures_dir + dataset + "_" + base_nets + "_Relative energy.png", bbox_inches="tight")

#####################
# Raw measures data #
#####################
TIME_BIN_s = 0.02 # 20000 us

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
		# # FPGA (PL)
		"VCCINT",		# Dominant
		# "VCCBRAM",
		# "VCCAUX",
		# "VCC1V2",
		# "VCC3V3",
		# # # MGT
		# "MGTRAVCC",
		# "MGTRAVTT",
		# "MGTAVCC",
		# "MGTAVTT",
		# "VCC3V3",
		]

power_rails_names = [ "PS", "DDR", "PL"]

#####################
# Raw measures plot #
#####################
plt.figure("Power from raw data", figsize=[15,7])
RANGE = np.arange(0, len(raw_nets_currents[0]["Timestamp"])*TIME_BIN_s, TIME_BIN_s)
ax = plt.subplot(2,2,1) # Assuming 8
# Remove tick marks
ax.tick_params(axis='x', which='both', bottom=False, top=False)
ax.set_xticks([])  # removes x-axis tick labels
# Skip teacher
for net in range(0,4):
	ax = plt.subplot(2, 2, net+1, sharey=ax) # Assuming 8

	# loop over power rails
	cnt = 0
	for pr in power_rails:
		power_mW = (raw_nets_currents[net][pr + " mA"] * raw_nets_voltages[net][pr + " mV"]) / 1000.
		plt.plot(raw_nets_currents[net]["Timestamp"], power_mW, label=power_rails_names[cnt])
		cnt += 1

	# Plot timeframe boundary
	plt.axvline(x=time_nets[net]["Start(sec)"].to_numpy(), linestyle="--", label="Timeframe")
	plt.axvline(x=time_nets[net]["End(sec)"  ].to_numpy(), linestyle="--")

	# Decorate
	if ( net == 1 ):
		plt.legend(fontsize=15)
	plt.title(net_names[net][3:], fontsize=15)
	plt.xlabel("Time", fontsize=15)
	# plt.xticks(ticks=raw_nets_currents[net]["Timestamp"], labels=RANGE)
	plt.xticks([])
	plt.grid(axis="both")
	plt.ylabel("Power(mW)", fontsize=15)

figname = figures_dir + dataset + "_" + base_nets + "_raw.png"
print(figname)
plt.savefig(figname, bbox_inches="tight")

##########################
# Print a single measure #
##########################
plt.figure("Single", figsize=[15,7])

# loop over power rails
cnt = 0
for pr in power_rails:
	# Plot the teacher
	power_mW = (raw_nets_currents[-1][pr + " mA"] * raw_nets_voltages[-1][pr + " mV"]) / 1000.
	plt.plot(raw_nets_currents[-1]["Timestamp"], power_mW, label=power_rails_names[cnt])
	cnt += 1

# Plot timeframe boundary
plt.axvline(x=time_nets[-1]["Start(sec)"].to_numpy(), linestyle="--", label="Timeframe")
plt.axvline(x=time_nets[-1]["End(sec)"  ].to_numpy(), linestyle="--")

# Decorate
plt.legend(fontsize=15)
plt.xlabel("Time", fontsize=15)
plt.grid(axis="both")
# plt.xticks(ticks=raw_nets_currents[net]["Timestamp"], labels=RANGE)
plt.xticks([])
plt.ylabel("Power(mW)", fontsize=15)

figname = figures_dir + "power_rails.png"
print(figname)
plt.savefig(figname, bbox_inches="tight")

# Compute integral in the target time frame
# plt.figure("Energy from raw", figsize=[15,7])
# energy_mJ = [[0. for _ in range(len(power_rails))] for _ in range(len(power_nets))]
# # Loop over nets
# for net in range(0,len(net_names_raw)):
# 	# Loop over samples
# 	for sample in range(0,len(raw_nets_currents[net])):
# 		# If this sample is within the timeframe
# 		if (
# 			raw_nets_currents[net]["Timestamp"][sample] > time_nets[net]["Start(sec)"].to_numpy()
# 			and raw_nets_currents[net]["Timestamp"][sample] < time_nets[net]["End(sec)"].to_numpy()
# 			):
# 			# Accumulate power
# 			for pr in range(0, len(power_rails)):
# 				power_mW = (raw_nets_currents[net][power_rails[pr] + " mA"][sample] * raw_nets_voltages[net][power_rails[pr] + " mV"][sample]) / 1000.
# 				energy_mJ[net][pr] += power_mW * TIME_BIN_s
# 	# # Multiply with time bin (constant across samples)
# 	# energy_mJ[net] *= TIME_BIN_s

# # ax=plt.subplot(2,4,1)
# WIDTH=0.2
# colors=["orange","green","blue"]
# for net in range(0,len(net_names_raw)):
# 	for pr in range(0, len(power_rails)):
# 		# ax=plt.subplot(2,4,net+1, sharey=ax)
# 		plt.bar(net-WIDTH+(pr*WIDTH), # Assuming 3 prs
# 			energy_mJ[net][pr],
# 			width=WIDTH,
# 			color=colors[pr]
# 			)
# for col in range(0,len(colors)):
# 	plt.bar(0,0,color=colors[col], label=power_rails[col])

# plt.legend(fontsize=15)
# plt.xlabel("Number of layers")
# plt.xticks( ticks=range(0, len(net_names_raw)),
# 			labels=num_layers
# 			)

# plt.ylabel("mJ")
# plt.savefig(figures_dir + dataset + "_" + base_nets + "_Energy from raw.png", bbox_inches="tight")

# # plt.show()