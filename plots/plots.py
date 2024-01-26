# import numpy as np
from cProfile import run
import sys
import pandas as pd
import matplotlib.pyplot as plt
import re
# import numpy as np
# from scipy import stats, integrate
# from scipy.interpolate import interp1d
# import seaborn as sns
# from scipy.spatial import distance
# from sklearn.preprocessing import MinMaxScaler

# reading data
data_dir = "../data/pre-processed/"
dataset  = 'cifar10'
teacher  = 'ResNet-50'

# Output
figures_dir  = 'figures/'

if len(sys.argv) >= 2 :
	teacher = sys.argv[1]
if len(sys.argv) >= 3 :
	dataset = sys.argv[2]

base_nets = re.sub("-.+", "", teacher)
base_nets_lower = base_nets.lower() + "s"
print("Running " + dataset + " " + base_nets_lower + " " + teacher)

#############
# Read data #
#############
# Paths
path_accuracy	= data_dir + dataset + '_' + base_nets_lower + '_accuracy.csv'
path_energy	  	= data_dir + dataset + '_' + base_nets_lower + '_energy.csv'
path_size 		= data_dir + dataset + '_' + base_nets_lower + '_size.csv'
path_runtime 	= data_dir + dataset + '_' + base_nets_lower + '_runtime.csv'
# Read
df_accuracy = pd.read_csv(path_accuracy		)
df_energy 	= pd.read_csv(path_energy		)
df_size 	= pd.read_csv(path_size	)
df_runtime	= pd.read_csv(path_runtime		)

################
# Extract data #
################
# Teacher
teacher_energy 		= df_energy		.loc[ df_energy		.Network == teacher, 'Energy (mJ)'	  ].values[0]
teacher_accuracy  	= df_accuracy	.loc[ df_accuracy	.Network == teacher, 'Scratch'   	  ].values[0]
teacher_float_MB 	= df_size		.loc[ df_size		.Network == teacher, 'Float Size (MB)'].values[0]
teacher_int_MB	 	= df_size		.loc[ df_size		.Network == teacher, 'Int Size (MB)'  ].values[0]
teacher_runtime 	= df_runtime	.loc[ df_runtime	.Network == teacher, 'Runtime(s)'	  ].values[0]

# Students
# Filter useless net_list, does this make sense?
net_list = df_accuracy.Network.unique()
print("net_list: ", net_list)
# df_energy = df_energy[df_energy['Network'].isin(net_list)]
# students_energy = df_energy[df_energy['Network'].isin(net_list)]
# students_accuracy = df_accuracy[df_accuracy['Network'].isin(net_list)]

# Relative compression
compression_KD = df_size['Float Size (MB)'] / teacher_float_MB * 100
compression_KD_PTQ = df_size['Int Size (MB)'] / teacher_float_MB * 100
# compression_KD_PTQ = df_size['Int Size (MB)'] / teacher_int_MB * 100
# Print to file
print(compression_KD_PTQ)
print(compression_KD)


# Relative reduction in runtime
runtime = [0. for _ in range(0, len(net_list))]
# df_runtime = df_runtime[df_runtime['Network'].isin(net_list)]
runtime = df_runtime['Runtime(s)'] / teacher_runtime * 100

base_net = re.sub("-|\d", "", teacher)
num_layers = [0 for net in range(len(net_list))]
for net in range(0,len(net_list)):
	num_layers[net] = re.sub("sub|Sub", "", net_list[net])
	num_layers[net] = re.sub(base_net, "", num_layers[net])
	num_layers[net] = int(re.sub("-|_.+", "", num_layers[net]))
print("num_layers: ", num_layers)

# removing last entry (teacher)
# students = net_list[:-1]

# calculating accuracy-energy Relative Sturent/Teacheres
decrementi_energy = df_energy.copy()
#decrementi_energy["Energy (mJ)"] = 1 - (teacher_energy - df_energy["Energy (mJ)"])/teacher_energy
decrementi_energy["Energy (mJ)"] = df_energy["Energy (mJ)"] / teacher_energy * 100
# # Normalize min-max
print("decrementi_energy:\n", decrementi_energy["Energy (mJ)"])
# min_energy = min(decrementi_energy["Energy (mJ)"])
# max_energy = max(decrementi_energy["Energy (mJ)"])
# decrementi_energy["Energy (mJ)"] = ( decrementi_energy["Energy (mJ)"] - min_energy ) / ( max_energy - min_energy )

# Print relative compression data to file
# Concatenate serires
df_compression = pd.concat([compression_KD, compression_KD_PTQ, runtime, decrementi_energy], axis="columns")
df_compression = pd.concat([compression_KD, compression_KD_PTQ, runtime, decrementi_energy], axis="columns")
# Swap columns
df_compression = df_compression.reindex(columns=["Network", "Float Size (MB)", "Int Size (MB)", "Runtime(s)", "Energy (mJ)"])
# Rename columns
df_compression = df_compression.rename(columns={"Float Size (MB)"	: "Float Size (%)",
												"Int Size (MB)"		: "Int Size (%)",
												"Energy (mJ)"		: "Energy (%)",
												"Runtime(s)"		: "Runtime (%)"
												}
										)

# Float MB (\%) & PTQ MB (\%) & Runtime\% & Energy\% 

# frame = {
# 			"Quantized": compression_KD,
# 			"Energy": decrementi_energy,
# 			"Runtime": runtime,
# 			}
			
# print("frame", frame)
# df = pd.DataFrame(frame)

print(df_compression)
filename = data_dir + dataset + "_" + base_nets_lower + "_compression.csv"
print(filename)
df_compression.to_csv(filename, index=False)

decrementi_accuracy = df_accuracy.copy()
for c in df_accuracy.columns[1:]:
	# decrementi_accuracy[c] = ( 1 - df_accuracy[c]/teacher_accuracy )
	decrementi_accuracy[c] = df_accuracy[c] / teacher_accuracy
	# Normalize min-max
	# min_accuracy = min(decrementi_accuracy[c])
	# max_accuracy = max(decrementi_accuracy[c])
	# decrementi_accuracy[c] = ( decrementi_accuracy[c] - min_accuracy ) / ( max_accuracy - min_accuracy )

#########
# Plots #
#########

# Plot compression data
plt.figure(figsize=(15,10))

# Energy
plt.plot(num_layers,decrementi_energy["Energy (mJ)"][:],linewidth=3,label='Energy')
# Runtime
plt.plot(num_layers,runtime,linewidth=3,label='Runtime')
# Compression
plt.plot(num_layers,compression_KD,linewidth=3,label='Compression KD')
plt.plot(num_layers,compression_KD_PTQ,linewidth=3,label='Compression KD+PTQ')
# Decorate
plt.legend(fontsize=15)
plt.xlabel('Number of layers',fontsize=15)
plt.ylabel('Relative Sturent/Teacher',fontsize=15)
plt.xticks(num_layers, fontsize=15)
plt.yticks(fontsize=15)
figname = figures_dir + dataset + '_' + base_nets + '_compression.png'
print(figname)
plt.savefig(figname, dpi=400, bbox_inches="tight")


# Accuracy vs Energy
plt.figure(figsize=(15,10))

# Energy
plt.plot(num_layers,decrementi_energy["Energy (mJ)"][:],linewidth=3,label='Energy')

# Accuracy
for c in df_accuracy.columns[2:]:
	plt.plot(num_layers,decrementi_accuracy[c],linewidth=1,label='KD+PTQ ' + c)
	plt.legend(fontsize=15)
	plt.xlabel('Number of layers',fontsize=15)
	plt.ylabel('Relative Sturent/Teacher',fontsize=15)
	plt.xticks(num_layers, fontsize=15)
	plt.yticks(fontsize=15)
	# plt.title('Energy-Accuracy Trade-Off for KT+PTQ with ' + c,fontsize=20)
	temperature =c.rsplit('=', 1)
figname = figures_dir + dataset + '_' + base_nets + '_tradeoff_kdptq_T' + temperature[1] + '.png'
# plt.savefig(figname, dpi=400, bbox_inches="tight")

# Best students
# calculating best accuracy values for KD
best_accuracy = pd.DataFrame()
best_accuracy['Network'] = df_accuracy['Network']
best_accuracies = []
for n in df_accuracy.Network.unique():
	temp = df_accuracy[df_accuracy['Network'] == n]
	best = temp.iloc[:,2:].values.flatten()
	best = max(best)
	best_accuracies.append(best)
best_accuracy['Accuracy'] = best_accuracies

decrementi_best = best_accuracy.copy()
# decrementi_best['Accuracy']= 1 - (best_accuracies/teacher_accuracy)
decrementi_best['Accuracy']= best_accuracies / teacher_accuracy

# generating plot for kd+ptq models (best accuracies)
# plt.figure(figsize=(15,10))
# plt.plot(num_layers,decrementi_energy["Energy (mJ)"][:],linewidth=3,label='Energy')
plt.plot(num_layers,decrementi_best['Accuracy'],linewidth=3,label='KD+PTQ (Best)', color="red")
plt.legend(fontsize=15)
plt.xlabel('Number of layers',fontsize=15)
plt.ylabel('Relative Sturent/Teacher',fontsize=15)
plt.xticks(num_layers, fontsize=15)
plt.yticks(fontsize=15)
# plt.title('Energy-Accuracy Trade-Off for Best KD+PTQ Models',fontsize=20)
# figname = figures_dir + dataset + '_' + base_nets + '_tradeoff_kdptq_best.png'
# plt.savefig(figname, dpi=400, bbox_inches="tight")


# PTQ-only
# plt.figure(figsize=(15,10))
# plt.plot(num_layers,decrementi_energy["Energy (mJ)"][:],linewidth=3,label='Energy')
plt.plot(num_layers,decrementi_accuracy['Scratch'],linewidth=3,label='PTQ-Only', color="green")
plt.legend(fontsize=15)
plt.xlabel('Number of layers',fontsize=15)
plt.ylabel('Relative Sturent/Teacher',fontsize=15)
plt.xticks(num_layers, fontsize=15)
plt.yticks(fontsize=15)
# plt.title('Energy-Accuracy Trade-Off for PTQ-Only Models',fontsize=20)
# figname = figures_dir + dataset + '_' + base_nets + '_tradeoff_ptqonly.png'
plt.title('Relative Accuracy vs Energy Performace',fontsize=20)
figname = figures_dir + dataset + '_' + base_nets + '_accuracy.png'
plt.savefig(figname, dpi=400, bbox_inches="tight")
print(figname)



