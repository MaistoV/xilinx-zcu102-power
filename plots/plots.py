# import numpy as np
import sys
import pandas as pd
import matplotlib.pyplot as plt
# from scipy import stats, integrate
# from scipy.interpolate import interp1d
# import seaborn as sns
# from scipy.spatial import distance
# from sklearn.preprocessing import MinMaxScaler

# reading data
data_dir = "../data/pre-processed/"
dataset = 'cifar100'
networks = 'resnets'
teacher = 'ResNet-50'

if len(sys.argv) >= 2 :
    dataset = sys.argv[1]
if len(sys.argv) >= 3 :
    networks = sys.argv[2]
if len(sys.argv) >= 4 :
    teacher = sys.argv[3]

path_accuracy    = data_dir + dataset + '_' + networks + '_accuracy.xlsx'
path_energy      = data_dir + dataset + '_' + networks + '_energy.xlsx'
path_compression = data_dir + dataset + '_' + networks + '_compressions.xlsx'


df_accuracy = pd.read_excel(path_accuracy)
df_energy = pd.read_excel(path_energy)
df_compression = pd.read_excel(path_compression)

my_students = df_accuracy.Network.unique()
df_energy = df_energy[df_energy['Network'].isin(my_students)]

my_students = my_students[:-1] # removing last entry (teacher)

teacher_energy = df_energy.loc[df_energy.Network==teacher, 'Energy'].values[0]
teacher_accuracy = df_accuracy.loc[df_accuracy.Network==teacher, 'Scratch'].values[0]
# teacher_compression = df_compression.loc[df_compression.Network==teacher, 'Compression'].values[0]

students_energy = df_energy[df_energy['Network'].isin(my_students)]
students_accuracy = df_accuracy[df_accuracy['Network'].isin(my_students)]
# students_compression = df_compression[df_compression['Network'].isin(my_students)]

# calculating accuracy-energy Relative Sturent/Teacheres
decrementi_energy = df_energy.copy()
#decrementi_energy.Energy = 1 - (teacher_energy - df_energy.Energy)/teacher_energy
decrementi_energy.Energy = df_energy.Energy/teacher_energy
# # Normalize min-max
# min_energy = min(decrementi_energy.Energy)
# max_energy = max(decrementi_energy.Energy)
# decrementi_energy.Energy = ( decrementi_energy.Energy - min_energy ) / ( max_energy - min_energy )

decrementi_accuracy = df_accuracy.copy()
for c in df_accuracy.columns[1:]:
    #decrementi_accuracy[c] = (teacher_accuracy - df_accuracy[c])/teacher_accuracy
    # decrementi_accuracy[c] = ( 1 - df_accuracy[c]/teacher_accuracy )
    decrementi_accuracy[c] = df_accuracy[c]/teacher_accuracy
    #plt.yscale('log')
    # Normalize min-max
    # min_accuracy = min(decrementi_accuracy[c])
    # max_accuracy = max(decrementi_accuracy[c])
    # decrementi_accuracy[c] = ( decrementi_accuracy[c] - min_accuracy ) / ( max_accuracy - min_accuracy )


# generating plot for kd-ptq models
plt.figure(figsize=(15,10))
plt.plot(decrementi_accuracy['Network'],decrementi_energy['Energy'][:],linewidth=3,label='Energy', color="blue")
for c in df_accuracy.columns[2:]:
    plt.plot(decrementi_accuracy['Network'],decrementi_accuracy[c],linewidth=1,label='Accuracy KD+PTQ ' + c)
    plt.legend(fontsize=15)
    plt.xlabel('Networks',fontsize=15)
    plt.ylabel('Relative Sturent/Teacher',fontsize=15)
    plt.xticks(fontsize=15)
    plt.yticks(fontsize=15)
    # plt.title('Energy-Accuracy Trade-Off for KT+PTQ with ' + c,fontsize=20)
    temperature =c.rsplit('=', 1)
figname = 'figures/' + dataset + '_' + networks + '_tradeoff_kdptq_T' + temperature[1] + '.png'
# plt.savefig(figname,dpi=400, bbox_inches="tight")

# calculating best accuracy values for KD
best_accuracy = pd.DataFrame()
best_accuracy['Network'] = df_accuracy['Network']
best_accs = []

for n in df_accuracy.Network.unique():
    temp = df_accuracy[df_accuracy['Network'] == n]
    best = temp.iloc[:,2:].values.flatten()
    best = max(best)
    best_accs.append(best)
best_accuracy['Accuracy']=best_accs


decrementi_best = best_accuracy.copy()

# decrementi_best['Accuracy']= 1 - (best_accs/teacher_accuracy)
decrementi_best['Accuracy']= best_accs / teacher_accuracy


# generating plot for kd+ptq models (best accuracies)
# plt.figure(figsize=(15,10))
# plt.plot(decrementi_accuracy['Network'],decrementi_energy['Energy'][:],linewidth=3,label='Energy')
plt.plot(decrementi_accuracy['Network'],decrementi_best['Accuracy'],linewidth=3,label='Best Accuracy (KD+PTQ)', color="red")
plt.legend(fontsize=15)
plt.xlabel('Networks',fontsize=15)
plt.ylabel('Relative Sturent/Teacher',fontsize=15)
plt.xticks(fontsize=15)
plt.yticks(fontsize=15)
# plt.title('Energy-Accuracy Trade-Off for Best KD+PTQ Models',fontsize=20)
figname = 'figures/' + dataset + '_' + networks + '_tradeoff_kdptq_best.png'
# plt.savefig(figname,dpi=400, bbox_inches="tight")


# generating plot for ptq-only models
# plt.figure(figsize=(15,10))
# plt.plot(decrementi_accuracy['Network'],decrementi_energy['Energy'][:],linewidth=3,label='Energy')
plt.plot(decrementi_accuracy['Network'],decrementi_accuracy['Scratch'],linewidth=3,label='Accuracy (PTQ-Only)', color="green")
plt.legend(fontsize=15)
plt.xlabel('Networks',fontsize=15)
plt.ylabel('Relative Sturent/Teacher',fontsize=15)
plt.xticks(fontsize=15)
plt.yticks(fontsize=15)
# plt.title('Energy-Accuracy Trade-Off for PTQ-Only Models',fontsize=20)
# figname = 'figures/' + dataset + '_' + networks + '_tradeoff_ptqonly.png'
plt.title('Relative Energy-Accuracy Performace',fontsize=20)
figname = 'figures/' + dataset + '_' + networks + '_alltogether.png'
plt.savefig(figname,dpi=400, bbox_inches="tight")




