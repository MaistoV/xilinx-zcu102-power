# import numpy as np
import sys
import pandas as pd
import matplotlib.pyplot as plt
import re
# from scipy import stats, integrate
# from scipy.interpolate import interp1d
# import seaborn as sns
# from scipy.spatial import distance
# from sklearn.preprocessing import MinMaxScaler

# reading data
data_dir = "../data/pre-processed/"
dataset  = 'cifar10'
networks = 'resnets'
teacher  = 'ResNet-50'

if len(sys.argv) >= 2 :
	dataset = sys.argv[1]
if len(sys.argv) >= 3 :
	networks = sys.argv[2]
if len(sys.argv) >= 4 :
	teacher = sys.argv[3]

print("Running " + dataset + " " + networks + " " + teacher)

#############
# Read data #
#############
# Paths
path_accuracy	= data_dir + dataset + '_' + networks + '_accuracy.xlsx'
path_energy	  = data_dir + dataset + '_' + networks + '_energy.xlsx'
path_compression = data_dir + dataset + '_' + networks + '_compressions.xlsx'
path_runtime = data_dir + dataset + '_' + networks + '_runtime.csv'
# Read
df_accuracy = pd.read_excel(path_accuracy)
df_energy = pd.read_excel(path_energy)
df_compression = pd.read_excel(path_compression)
df_runtime = pd.read_csv(path_runtime)

################
# Extract data #
################
# Teacher
teacher_energy 		= df_energy		.loc[ df_energy		.Network == teacher, 'Energy'     ].values[0]
teacher_accuracy  	= df_accuracy	.loc[ df_accuracy	.Network == teacher, 'Scratch'    ].values[0]
teacher_parameters 	= df_compression.loc[ df_compression.Network == teacher, 'Parameters' ].values[0]
teacher_runtime 	= df_runtime	.loc[ df_runtime	.Network == teacher, 'Runtime(s)' ].values[0]


# Students
# Filter useless students, does this make sense?
students = df_accuracy.Network.unique()
df_energy = df_energy[df_energy['Network'].isin(students)]
students = students[:-1] # removing last entry (teacher)
# students_energy = df_energy[df_energy['Network'].isin(students)]
# students_accuracy = df_accuracy[df_accuracy['Network'].isin(students)]

# Relative compression
compression = df_compression['Parameters'] / teacher_parameters

# Relative reduction in runtime
print(students)
runtime = [0. for _ in range(0, len(students) +1)]
df_runtime = df_runtime[df_runtime['Network'].isin(students)]
runtime = df_runtime['Runtime(s)'] / teacher_runtime
runtime[-1] = 1

base_net = re.sub("-|\d", "", teacher)
num_layers = ["" for net in range(len(students) +1)]
for net in range(0,len(students)):
	num_layers[net] = re.sub("sub|Sub", "", students[net])
	num_layers[net] = re.sub(base_net, "", num_layers[net])
	num_layers[net] = int(re.sub("-|_.+", "", num_layers[net]))
# Append teacher layers
num_layers[-1] = int(re.sub("-|[^\d]", "", teacher))
print("num_layers: ", num_layers)

# calculating accuracy-energy Relative Sturent/Teacheres
decrementi_energy = df_energy.copy()
#decrementi_energy.Energy = 1 - (teacher_energy - df_energy.Energy)/teacher_energy
decrementi_energy.Energy = df_energy.Energy / teacher_energy
# # Normalize min-max
# min_energy = min(decrementi_energy.Energy)
# max_energy = max(decrementi_energy.Energy)
# decrementi_energy.Energy = ( decrementi_energy.Energy - min_energy ) / ( max_energy - min_energy )

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
plt.figure(figsize=(15,10))

# Energy
plt.plot(num_layers,decrementi_energy['Energy'][:],linewidth=3,label='Energy', color="blue")

# Runtime
plt.plot(num_layers,runtime,linewidth=3,label='Runtime', color="grey")

# Compression
plt.plot(num_layers,compression,linewidth=3,label='Compression', color="black")

# Accuracy students
for c in df_accuracy.columns[2:]:
	plt.plot(num_layers,decrementi_accuracy[c],linewidth=1,label='Accuracy KD+PTQ ' + c)
	plt.legend(fontsize=15)
	plt.xlabel('Number of layers',fontsize=15)
	plt.ylabel('Relative Sturent/Teacher',fontsize=15)
	plt.xticks(num_layers, fontsize=15)
	plt.yticks(fontsize=15)
	# plt.title('Energy-Accuracy Trade-Off for KT+PTQ with ' + c,fontsize=20)
	temperature =c.rsplit('=', 1)
figname = 'figures/' + dataset + '_' + networks + '_tradeoff_kdptq_T' + temperature[1] + '.png'
# plt.savefig(figname,dpi=400, bbox_inches="tight")

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
# plt.plot(num_layers,decrementi_energy['Energy'][:],linewidth=3,label='Energy')
plt.plot(num_layers,decrementi_best['Accuracy'],linewidth=3,label='Best Accuracy KD+PTQ', color="red")
plt.legend(fontsize=15)
plt.xlabel('Number of layers',fontsize=15)
plt.ylabel('Relative Sturent/Teacher',fontsize=15)
plt.xticks(num_layers, fontsize=15)
plt.yticks(fontsize=15)
# plt.title('Energy-Accuracy Trade-Off for Best KD+PTQ Models',fontsize=20)
figname = 'figures/' + dataset + '_' + networks + '_tradeoff_kdptq_best.png'
# plt.savefig(figname,dpi=400, bbox_inches="tight")


# PTQ-only
# plt.figure(figsize=(15,10))
# plt.plot(num_layers,decrementi_energy['Energy'][:],linewidth=3,label='Energy')
plt.plot(num_layers,decrementi_accuracy['Scratch'],linewidth=3,label='Accuracy PTQ-Only', color="green")
plt.legend(fontsize=15)
plt.xlabel('Number of layers',fontsize=15)
plt.ylabel('Relative Sturent/Teacher',fontsize=15)
plt.xticks(num_layers, fontsize=15)
plt.yticks(fontsize=15)
# plt.title('Energy-Accuracy Trade-Off for PTQ-Only Models',fontsize=20)
# figname = 'figures/' + dataset + '_' + networks + '_tradeoff_ptqonly.png'
plt.title('Relative Energy-Accuracy Performace',fontsize=20)
figname = 'figures/' + dataset + '_' + networks + '_alltogether.png'
plt.savefig(figname,dpi=400, bbox_inches="tight")




