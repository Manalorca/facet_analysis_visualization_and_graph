import numpy as np
import matplotlib.pyplot as plt
import json
import random
from math import ceil
import os

"""
Enter the path of the folder containing one subfolder for each scan named S{scan number}. 
Each folder S{scan number} must contain the following files : 
facet_label.npy
facet_label_index.json
"""
folder_path = ''


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

"""
The list of the index you want to display.
Each sublist corresponds to one graph. 
If there are more than on index on the same sublist, 
all this index will be displayed on the same graph
"""
different_families = [[[1,1,1], [-1,-1,-1]], 
                      [[-1,-1,-1]],
                      [[1,0,0], [0,1,0], [0,0,1]],
                      ]

#If you want, you can choose the path where you want to save the graphic
#If you let it equal to None, it will be the same folder of the folder_path
save_path = None

#Choose the size of the points on the graphic
size = 1000


dict_scans = {}

for scan in scans:

    path = f'{folder_path}\\S{scan}\\'

    facet_label = np.load(f'{path}facet_label.npy')

    with open(f'{path}facet_label_index.json', 'r') as f:
        facet_label_index = json.load(f)

    dict_scans[scan] = {'facet_label' : facet_label, 'facet_label_index' : facet_label_index}
    
dict_facet_strain = {}

nb_voxel_min = np.inf
nb_voxel_max = 0

for scan in scans:
    facet_label = dict_scans[scan]['facet_label']
    facet_label_index = dict_scans[scan]['facet_label_index']
    for i in range(len(facet_label_index)):
        label = facet_label_index[i][0]
        nb_voxels = np.sum(facet_label == label)
        if nb_voxels < nb_voxel_min:
            nb_voxel_min = nb_voxels
        if nb_voxels > nb_voxel_max:
            nb_voxel_max = nb_voxels

for scan in scans:
    facet_label = dict_scans[scan]['facet_label']
    facet_label_index = dict_scans[scan]['facet_label_index']
    for i in range(len(facet_label_index)):
        label = facet_label_index[i][0]
        index = tuple(facet_label_index[i][1])
        mean_strain = facet_label_index[i][2][1]
        sd_strain = facet_label_index[i][2][2]
        minmax_strain = facet_label_index[i][2][3]
        nb_voxels = np.sum(facet_label == label)
        if index in dict_facet_strain:
            dict_facet_strain[index][0].append(scans.index(scan))
            dict_facet_strain[index][1].append(mean_strain)
            dict_facet_strain[index][2].append(sd_strain/2)
            dict_facet_strain[index][3].append(nb_voxels/nb_voxel_max * size)
        else:
            dict_facet_strain[index] = [[scans.index(scan)] , [mean_strain], [sd_strain], [nb_voxels/nb_voxel_max * size]]

            
new = []

for sublist in different_families:
    new.extend(sublist)

# Set up a list of colors for each index
N = ceil((len(new))**(1/3))+1
list_colors = []
for i in range(N-1):
    for j in range(N-1):
        for k in range(N-1):
            list_colors.append((i*1/N, j*1/N, k*1/N, 1))
random.shuffle(list_colors)

if save_path is None:
    save_path = f'{folder_path}facets\\'
    os.makedirs(save_path, exist_ok=True)

nb_color = 0
for i in range(len(different_families)):
    # Plotting
    fig, ax = plt.subplots()
    handles = []
    # Set x-axis ticks and labels
    plt.xticks([i for i in range(len(scans))], [scan_description[scan] for scan in scans], rotation=30, ha="right")

    ax.set_xlabel('Scan')
    ax.set_ylabel('Strain')
    ax.set_title('Strain Values for Different Indices')
    ax.grid(True, zorder=2)

    for index, scans_strain_values in dict_facet_strain.items():
            if list(index) in different_families[i]:
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
                            zorder=4  
                            )

                # Plot points with size proportional to the number of voxels
                scatter = ax.scatter(list_scans, strain_values, c=list_colors[nb_color], s=nb_voxels_values, marker='.', label=str(index), edgecolors='black', zorder=5)
                ax.plot(list_scans, strain_values, ':', color=list_colors[nb_color], zorder=3)

                # Store handles for the main plot (excluding error bars)
                handles.append(scatter)
      
                nb_color += 1
    
    # Initialize empty lists to store legend elements
    legend_elements = []

    # Add legend elements for nb_voxel_min and nb_voxel_max
    legend_elements.append(ax.scatter([0], [0], c='black', s=nb_voxel_min/nb_voxel_max * size, marker='.', label=str(nb_voxel_min), edgecolors='black', zorder=0))
    legend_elements.append(ax.scatter([0], [0], c='black', s=nb_voxel_max/nb_voxel_max * size, marker='.', label=str(nb_voxel_min), edgecolors='black', zorder=0))
    ax.scatter([0], [0], c='white', s=nb_voxel_max/nb_voxel_max * size * 2, marker='.', label=str(nb_voxel_min), edgecolors='white', zorder=1)

    ax.legend(handles=handles+ legend_elements, labels=[str(index) for index in dict_facet_strain.keys() if list(index) in different_families[i]] + [f'{nb_voxel_min} voxels', f'{nb_voxel_max} voxels'], bbox_to_anchor=(1.05, 1), loc='upper left', title='Index')
    

    ax.set_aspect('auto')
    
    # Save the figure
    plt.tight_layout()
    plt.savefig(f'{save_path}facet_{i}.png')
    plt.close(fig)

# Show the plot
# plt.show()