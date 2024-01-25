import numpy as np
import matplotlib.pyplot as plt
import glob
import pandas
# import re
# import sys

# TODO: add calibration also for raw measures?

# Data directory
data_dir = "../data/calibration"

# Output directory
out_dir = "../data/calibration/"
plot_dir = "./calibration/"

##############
# Power data #
##############
calibration_meas_path = glob.glob(data_dir + "/calibration_measure.csv")
calibration_test_path = glob.glob(data_dir + "/calibration_test.csv")



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
plt.figure("Power calibration", figsize=[15,10])

# Plot all
plt.plot( calibration_meas["Timestamp"], calibration_meas["Total mW"], label="Samples", linestyle="", marker="o")
# plt.plot( calibration_test["Timestamp"], calibration_test["Total mW"], label="test"	)

# Start and end test timestamp
meas_start_time	= calibration_meas["Timestamp"].iloc[ 0]
meas_end_time	= calibration_meas["Timestamp"].iloc[-1]

test_start_time	= calibration_test["Timestamp"].iloc[ 0]
test_end_time	= calibration_test["Timestamp"].iloc[-1]
plt.axvline(x=test_start_time, color="r", linestyle="dashed", label="Timeframe")
plt.axvline(x=test_end_time	 , color="r", linestyle="dashed")
# plt.axvline(x=meas_start_time, color="b", linestyle="dashed", label="meas")
# plt.axvline(x=meas_end_time  , color="b", linestyle="dashed", label="meas")

# Averages
PRE_TEST=0 	# Pre-test
TEST=1		# During test
POST_TEST=2 # Post-test
NON_TEST=3
means = [0. for _ in [PRE_TEST, TEST, POST_TEST, NON_TEST]]
means[PRE_TEST ] = calibration_meas["Total mW"].loc[calibration_meas["Timestamp"] < test_start_time].mean()
means[POST_TEST] = calibration_meas["Total mW"].loc[calibration_meas["Timestamp"] > test_end_time].mean()
means[NON_TEST] = (means[PRE_TEST] + means[POST_TEST]) / 2
# Split selection in two steps
tmp_df 		= calibration_meas	.loc[(calibration_meas["Timestamp"] > test_start_time)]
means[TEST] = tmp_df["Total mW"].loc[(tmp_df		  ["Timestamp"] < test_end_time	 )].mean()

# plt.hlines(y=means[PRE_TEST ], xmin=meas_start_time	, xmax=test_start_time	, linestyle="dashdot", color="b", label="pre test" )
# plt.hlines(y=means[POST_TEST], xmin=test_end_time	, xmax=meas_end_time 	, linestyle="dashdot", color="b", label="post test")
# plt.hlines(y=means[TEST     ], xmin=test_start_time	, xmax=test_end_time	, linewidth=5, linestyle="dashdot", color="r", label="test"	   )
plt.hlines(y=means[TEST		], xmin=meas_start_time	, xmax=meas_end_time 	, linewidth=2, linestyle="dashdot", color="r", label="avg test" )
plt.hlines(y=means[NON_TEST ], xmin=meas_start_time	, xmax=meas_end_time 	, linewidth=2, linestyle="dashdot", color="b", label="avg non-test" )

# Decorate
plt.legend(fontsize=15)
plt.title("Raw calibration measures")
plt.xlabel("Seconds")
plt.ylabel("mW")
plt.savefig(plot_dir + "Calibration power.png", dpi=400, bbox_inches="tight")

################
# Save to file #
################
diff = means[TEST] - means[NON_TEST] 
diff_filename = "../data/calibration/calibration.csv"
file1 = open(diff_filename, "a")  # append mode
file1.write(str(diff) + "\n")
file1.close()

# diff_df = pandas.read_csv(diff_filename)
# plt.figure("Computed differences", figsize=[15,10])
# # plt.subplot(1,2,1)
# # plt.title("Samples")
# # # plt.plot(diff_df, marker="o", linestyle="")
# # plt.boxplot(diff_df)
# # plt.subplot(1,2,2)
# plt.title("Histogram")
# plt.hist(diff_df, orientation="horizontal", label="Histogram", bins=20)
# plt.axhline(y=diff_df.to_numpy().mean(), label="Mean", color="r", linestyle="dashed" )
# plt.legend(fontsize=15)
# plt.savefig(plot_dir + "Calibration histogram.png", dpi=400, bbox_inches="tight")
 
#################
# Raw meas data #
#################
TIME_BIN_s = 0.02 # 20000 us

suffix_currents = ".csv.raw_currents"
suffix_voltages = ".csv.raw_voltages"

calibration_meas_voltages_path = glob.glob(data_dir + "/calibration_measure" + suffix_voltages)
calibration_meas_currents_path = glob.glob(data_dir + "/calibration_measure" + suffix_currents)
calibration_test_voltages_path = glob.glob(data_dir + "/calibration_test"    + suffix_voltages)
calibration_test_currents_path = glob.glob(data_dir + "/calibration_test"    + suffix_currents)

# Read data
calibration_meas_voltages = pandas.read_csv(calibration_meas_voltages_path[0], sep=";", index_col=0)
calibration_meas_currents = pandas.read_csv(calibration_meas_currents_path[0], sep=";", index_col=0)
calibration_test_voltages = pandas.read_csv(calibration_test_voltages_path[0], sep=";", index_col=0)
calibration_test_currents = pandas.read_csv(calibration_test_currents_path[0], sep=";", index_col=0)

# Realign timestamps to zero
offset = calibration_meas_voltages["Timestamp"].loc[0]
calibration_meas_voltages["Timestamp"] -= offset
calibration_test_voltages["Timestamp"] -= offset

offset = calibration_meas_currents["Timestamp"].loc[0]
calibration_meas_currents["Timestamp"] -= offset
calibration_test_currents["Timestamp"] -= offset

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

#################
# Raw meas plot #
#################
plt.figure("Raw calibration", figsize=[15,10])
plt.title("Raw calibration measures")

# ax = plt.subplot(3,1,pr + 1)
for pr in range(0,len(power_rails)):
	# plt.subplot(3,2,2*pr + 1)
	# plt.title(power_rails[pr])
	# plt.plot( calibration_meas_voltages["Timestamp"], calibration_meas_voltages[power_rails[pr] + " mV"], label="Samples", linestyle="", marker="o")
	# plt.ylabel("mV")

	# plt.subplot(3,2,2*pr + 2)
	# plt.subplot(3,1,pr + 1, shareay=ax)
	plt.title(power_rails[pr])
	plt.plot( calibration_meas_currents["Timestamp"], calibration_meas_currents[power_rails[pr] + " mA"], label=power_rails[pr], linestyle="", marker="o")
	plt.ylabel("mA")

	
plt.axvline(x=test_start_time, color="r", linestyle="dashed", label="Timeframe")
plt.axvline(x=test_end_time	 , color="r", linestyle="dashed")

# Decorate
plt.legend(fontsize=15)
plt.xlabel("Seconds")
plt.savefig(plot_dir + "Calibration raw.png", dpi=400, bbox_inches="tight")