import numpy as np
import matplotlib.pyplot as plt
import glob
import pandas
# import re
# import sys

# Data directory
data_dir = "../data/calibration"

##############
# Power data #
##############
calibration_meas_path = glob.glob(data_dir + "/" + "calibration_measure.csv")
calibration_test_path = glob.glob(data_dir + "/" + "calibration_test.csv")

# Read data
calibration_meas = pandas.read_csv(calibration_meas_path[0], sep=";", index_col=0)
calibration_test = pandas.read_csv(calibration_test_path[0], sep=";", index_col=0)

# Realign timestamps to zero
offset = calibration_meas["Timestamp"].loc[0]
calibration_meas["Timestamp"] -= offset
calibration_test["Timestamp"] -= offset

#########
# Power #
#########
plt.figure("Raw calibration", figsize=[15,10])

# Plot all
plt.plot( calibration_meas["Timestamp"], calibration_meas["Total mW"], label="meas", marker="o")
plt.plot( calibration_test["Timestamp"], calibration_test["Total mW"], label="test"	)

# Start and end test timestamp
meas_start_time	= calibration_meas["Timestamp"].iloc[ 0]
meas_end_time	= calibration_meas["Timestamp"].iloc[-1]

test_start_time	= calibration_test["Timestamp"].iloc[ 0]
test_end_time	= calibration_test["Timestamp"].iloc[-1]
plt.axvline(x=test_start_time, color="r", linestyle="--", label="test")
plt.axvline(x=test_end_time	 , color="r", linestyle="--", label="test")
plt.axvline(x=meas_start_time, color="b", linestyle="--", label="meas")
plt.axvline(x=meas_end_time  , color="b", linestyle="--", label="meas")

# Decorate
plt.legend()
plt.title("Raw calibration measures")
plt.xlabel("Seconds")
plt.ylabel("mW")

# Averages
PRE_TEST=0 	# Pre-test
TEST=1		# During test
POST_TEST=2 # Post-test
means = [0. for _ in [PRE_TEST, TEST, POST_TEST]]
means[PRE_TEST ] = calibration_meas["Total mW"].loc[calibration_meas["Timestamp"] < test_start_time].mean()
means[POST_TEST] = calibration_meas["Total mW"].loc[calibration_meas["Timestamp"] > test_end_time].mean()
# Split selection in two steps
tmp_df 		= calibration_meas	.loc[(calibration_meas["Timestamp"] > test_start_time)]
means[TEST] = tmp_df["Total mW"].loc[(tmp_df		  ["Timestamp"] < test_end_time	 )].mean()

plt.hlines(y=means[PRE_TEST ], xmin=meas_start_time	, xmax=test_start_time	, linestyle="dashdot", color="b", label="Local means")
plt.hlines(y=means[TEST     ], xmin=test_start_time	, xmax=test_end_time	, linestyle="dashdot", color="b")
plt.hlines(y=means[POST_TEST], xmin=test_end_time	, xmax=meas_end_time 	, linestyle="dashdot", color="b")


plt.savefig("Raw calibration.png")

print(means[PRE_TEST] - means[POST_TEST])
print(means[PRE_TEST] - means[TEST	   ])
print(means[TEST	] - means[POST_TEST])
print(means[PRE_TEST] )
print(means[POST_TEST])
print(means[TEST	] )

# plt.show()
exit()

##########
# Energy #
##########

# Compute integral in the target time frame
TIME_BIN_s = 0.02 # 20000 us
plt.figure("Energy from power", figsize=[15,10])
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
			# Accumulate power
			pl_energy_mJ[net] += power_nets[net]["PL mW"][sample]
			ps_energy_mJ[net] += power_nets[net]["PS mW"][sample]
	# Multiply with time bin (constant across samples)
	pl_energy_mJ[net] *= TIME_BIN_s
	ps_energy_mJ[net] *= TIME_BIN_s

# Dataframe per franca
header = ["CNN", "Energy"]
df = [["" for _ in header] for _ in range(len(power_nets))]
for i in range(0,len(net_names)):
	df[i][0] = net_names[i] 
	df[i][1] = str(ps_energy_mJ[i] + pl_energy_mJ[i])

df = pandas.DataFrame(df)
df.to_csv(base_net + "_energy.csv")

NUM_FRAMES=1000
# J / frame
print("J/frame(32x32)", (pl_energy_mJ[-1] + ps_energy_mJ[-1]) / 1000 / NUM_FRAMES)

plt.plot(num_layers, pl_energy_mJ, label="PL", marker="o" )
plt.plot(num_layers, ps_energy_mJ, label="PS", marker="o" )
plt.plot(num_layers[-1], pl_energy_mJ[-1], marker="*", markersize=15, color="r", label="Teacher")
plt.plot(num_layers[-1], ps_energy_mJ[-1], marker="*", markersize=15, color="r" )
plt.xticks(ticks=num_layers)
plt.legend()
plt.xlabel("Number of layers")
plt.ylabel("mJ")
plt.savefig(base_net + "_Energy from power.png", bbox_inches="tight")

plt.figure("Relative energy efficiency", figsize=[15,10])
tot_energy_mJ = [0. for net in range(len(power_nets))]
relative_energy = [0. for net in range(len(power_nets))]
for net in reversed(range(0,len(tot_energy_mJ))):
	tot_energy_mJ[net] = pl_energy_mJ[net] + pl_energy_mJ[net]
	relative_energy[net] = tot_energy_mJ[net] / tot_energy_mJ[-1]
plt.plot(num_layers, relative_energy, marker="o" )
plt.xlabel("Number of layers")
plt.ylabel("%")
plt.yticks(np.arange(0,1.1,0.1), labels=np.arange(0,110,10))
plt.title("Student / Teacher energy gain")
plt.savefig(base_net + "_Relative energy.png", bbox_inches="tight")

#####################
# Raw meass data #
#####################
TIME_BIN_s = 0.02 # 20000 us

suffix_currents = ".csv.raw_currents"
suffix_voltages = ".csv.raw_voltages"

net_paths_raw_voltages = glob.glob(data_dir + "/*" + base_net + "*" + suffix_voltages) 
net_paths_raw_currents = glob.glob(data_dir + "/*" + base_net + "*" + suffix_currents) 
net_paths_raw_voltages.sort()
net_paths_raw_currents.sort()
net_names_raw = ["" for net in range(len(net_paths_raw_voltages))]
for net in range(0,len(net_paths_raw_voltages)):
	# basename
	net_names_raw[net] = net_paths_raw_voltages[net][len(data_dir)+1:(-1*len(suffix_voltages))]

# Read data
raw_nets_voltages = list(range(len(net_names_raw)))
raw_nets_currents = list(range(len(net_names_raw)))
for net in range(0,len(net_names_raw)):
	raw_nets_currents[net] = pandas.read_csv( net_paths_raw_currents[net], sep=";", index_col=0 )
	raw_nets_voltages[net] = pandas.read_csv( net_paths_raw_voltages[net], sep=";", index_col=0 )

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

#####################
# Raw meass plot #
#####################
plt.figure("Power from raw data", figsize=[15,10])
RANGE = np.arange(0, len(raw_nets_currents[0]["Timestamp"])*TIME_BIN_s, TIME_BIN_s)
# ax = plt.subplot(2,4,1) # Assuming 8 nets
# for net in range(0,len(net_names_raw)):	
for net in range(1,2):	
	# ax = plt.subplot(2, 4, net+1, sharey=ax) # Assuming 8 nets
	
	# loop over power rails
	for pr in power_rails:
		power_mW = (raw_nets_currents[net][pr + " mA"] * raw_nets_voltages[net][pr + " mV"]) / 1000.
		plt.plot(raw_nets_currents[net]["Timestamp"], power_mW, label=pr	)
		# plt.plot(RANGE, power_mW, label=pr	)

	# Plot timeframe boundary
	plt.axvline(x=time_nets[net]["Start(sec)"].to_numpy(), linestyle="--", label="Timeframe")
	plt.axvline(x=time_nets[net]["End(sec)"  ].to_numpy(), linestyle="--")

	# Decorate
	if ( net == 0 ):
		plt.legend()
	plt.legend()
	plt.title(net_names_raw[net])
	plt.xlabel("Time(s)")
	# plt.xticks(ticks=raw_nets_currents[net]["Timestamp"], labels=RANGE)
	plt.xticks([])
	plt.ylabel("mW")

plt.savefig(base_net + "_raw.png", bbox_inches="tight")

# Compute integral in the target time frame
plt.figure("Energy from raw", figsize=[15,10])
energy_mJ = [[0. for _ in range(len(power_rails))] for _ in range(len(power_nets))]
# Loop over nets
for net in range(0,len(net_names_raw)):	
	# Loop over samples
	for sample in range(0,len(raw_nets_currents[net])):
		# If this sample is within the timeframe
		if (
			raw_nets_currents[net]["Timestamp"][sample] > time_nets[net]["Start(sec)"].to_numpy()
			and raw_nets_currents[net]["Timestamp"][sample] < time_nets[net]["End(sec)"].to_numpy()
			):
			# Accumulate power
			for pr in range(0, len(power_rails)):
				power_mW = (raw_nets_currents[net][power_rails[pr] + " mA"][sample] * raw_nets_voltages[net][power_rails[pr] + " mV"][sample]) / 1000.
				energy_mJ[net][pr] += power_mW * TIME_BIN_s
	# # Multiply with time bin (constant across samples)
	# energy_mJ[net] *= TIME_BIN_s

# ax=plt.subplot(2,4,1)
WIDTH=0.2
colors=["orange","green","blue"]
for net in range(0,len(net_names_raw)):	
	for pr in range(0, len(power_rails)):
		# ax=plt.subplot(2,4,net+1, sharey=ax)
		plt.bar(net-WIDTH+(pr*WIDTH), # Assuming 3 prs
			energy_mJ[net][pr],
			width=WIDTH, 
			color=colors[pr]
			)
for col in range(0,len(colors)):
	plt.bar(0,0,color=colors[col], label=power_rails[col])

plt.legend()
plt.xlabel("Number of layers")
plt.xticks( ticks=range(0, len(net_names_raw)),
			labels=num_layers
			)
			
plt.ylabel("mJ")
plt.savefig(base_net + "_Energy from raw.png", bbox_inches="tight")

# plt.show()