import numpy as np
import matplotlib.pyplot as plt
import json
import random
from math import ceil
import os

"""
Enter the path of the folder containing one subfolder for each scan named S{scan number}. 
Each folder S{scan number} must contain the following files : 
corner_label.npy
corner_label_index.json
"""
folder_path = 'C:\\Users\\matth\\Desktop\\graph_test\\'

#The list of the scan number
scans = [706, 764, 814, 833, 847, 872, 910, 949, 959]

#The description of each scan
scan_description = {
    706: "H2, 450C",
    764: "He, 450C",
    814: "CO2, 450C, 10%",
    833: "CO2, 450C, 20%",
    847: "CO2, 450C, 30%",
    872: "CO2, 450C, 40%",
    910: "CO2, 450C, 50%",
    949: "He, 450C",
    959: "H2, 450C"
}

#Enter the number of facets
nb_facets = 26

#If you want, you can choose the path where you want to save the graphic
#If you let it equal to None, it will be the same folder of the folder_path
save_path = None

#Choose the size of the points on the graphic
size = 1000


dict_scans = {}

for scan in scans:

    path = f'{folder_path}\\S{scan}\\'

    corner_label = np.load(f'{path}corner_label.npy')

    with open(f'{path}corner_label_index.json', 'r') as f:
        corner_label_index = json.load(f)

    dict_scans[scan] = {'corner_label' : corner_label, 'corner_label_index' : corner_label_index}
    
dict_corner_strain = {}

nb_voxel_min = np.inf
nb_voxel_max = 0

for scan in scans:
    corner_label = dict_scans[scan]['corner_label']
    corner_label_index = dict_scans[scan]['corner_label_index']
    for i in range(len(corner_label_index)):
        if len(corner_label_index[i]) == 3 and corner_label_index[i][0]>nb_facets:
            label = corner_label_index[i][0]
            nb_voxels = np.sum(corner_label == label)
            if nb_voxels < nb_voxel_min:
                nb_voxel_min = nb_voxels
            if nb_voxels > nb_voxel_max:
                nb_voxel_max = nb_voxels

for scan in scans:
    corner_label = dict_scans[scan]['corner_label']
    corner_label_index = dict_scans[scan]['corner_label_index']
    for i in range(len(corner_label_index)):
        if len(corner_label_index[i]) == 3 and corner_label_index[i][0]>nb_facets:
            label = corner_label_index[i][0]
            direction = tuple(np.round(corner_label_index[i][1],1))
            mean_strain = corner_label_index[i][2][1]
            sd_strain = corner_label_index[i][2][2]
            minmax_strain = corner_label_index[i][2][3]
            nb_voxels = np.sum(corner_label == label)
            if direction in dict_corner_strain:
                dict_corner_strain[direction][0].append(scans.index(scan))
                dict_corner_strain[direction][1].append(mean_strain)
                dict_corner_strain[direction][2].append(sd_strain)
                dict_corner_strain[direction][3].append(nb_voxels/nb_voxel_max * size)
            else:
                dict_corner_strain[direction] = [[scans.index(scan)] , [mean_strain], [sd_strain], [nb_voxels/nb_voxel_max * size]]

# Set up a list of colors for each index
N = ceil((len(dict_corner_strain))**(1/3))+1
list_colors = []
for i in range(N-1):
    for j in range(N-1):
        for k in range(N-1):
            list_colors.append((i*1/N, j*1/N, k*1/N, 1))
random.shuffle(list_colors)

if save_path is None:
    save_path = f'{folder_path}corners\\'
    os.makedirs(save_path, exist_ok=True)

nb_color = 0
i = 0
for nghbs_index, scans_strain_values in dict_corner_strain.items():
    # Plotting
    fig, ax = plt.subplots()

    # Set x-axis ticks and labels
    plt.xticks([i for i in range(len(scans))], [scan_description[scan] for scan in scans], rotation=30, ha="right")
    
    # Customize the plot
    ax.set_xlabel('Scan')
    ax.set_ylabel('Strain')
    ax.set_title(f'Strain Values for {nghbs_index[0:0+3]}')
    ax.grid(True, zorder=0)

    list_scans = scans_strain_values[0]
    strain_values = scans_strain_values[1]
    sd_values = scans_strain_values[2]
    nb_voxels_values = scans_strain_values[3]

     # Plot error bars
    ax.errorbar(list_scans, 
                strain_values, 
                yerr=sd_values, 
                fmt='none', 
                color=list_colors[nb_color],
                capsize=4,
                capthick=1.5,
                zorder=2  
                )
    
     # Plot points with size proportional to the number of voxels
    scatter = ax.scatter(list_scans, strain_values, c=list_colors[nb_color], s=nb_voxels_values, marker='.', label=str(nghbs_index), edgecolors='black', zorder=3)
    ax.plot(list_scans, strain_values, ':', color=list_colors[nb_color], zorder=1)

    nb_color += 1

   # Initialize empty lists to store legend elements
    legend_elements = []

    # Add legend elements for nb_voxel_min and nb_voxel_max
    legend_elements.append(ax.scatter([0], [0], c='black', s=nb_voxel_min/nb_voxel_max * size, marker='.', label=str(nb_voxel_min), edgecolors='black', zorder=0))
    legend_elements.append(ax.scatter([0], [0], c='black', s=nb_voxel_max/nb_voxel_max * size, marker='.', label=str(nb_voxel_min), edgecolors='black', zorder=0))
    ax.scatter([0], [0], c='white', s=nb_voxel_max/nb_voxel_max * size * 2, marker='.', label=str(nb_voxel_min), edgecolors='white', zorder=1)
    
    ax.legend(handles=legend_elements, labels=[f'{nb_voxel_min} voxels', f'{nb_voxel_max} voxels'], bbox_to_anchor=(1.05, 1), loc='upper left', title='Index')

    ax.set_aspect('auto')

    # Save the figure
    plt.tight_layout()
    plt.savefig(f'{save_path}corner_{i}.png')
    i += 1
    plt.close(fig)

# Show the plot
# plt.show()




    
