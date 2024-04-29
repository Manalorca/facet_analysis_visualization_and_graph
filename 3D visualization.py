import numpy as np
import matplotlib.pyplot as plt
import json
import matplotlib as mpl
import random
from math import ceil
from matplotlib.colors import TwoSlopeNorm

"""
Enter the path of the folder containing the following files: 
facet_label.npy
facet_label_index.json
edge_label.npy
edge_label_index.json
corner_label.npy
corner_label_index.json
"""

path = ""


#indicate the number of facets
nb_facets = 26

#Choose whether to display clustering for facets, edges, corners or all three.
analysis = 'facet' # 'facet', 'edge', 'corner', 'all'

#Choose if you want to display the strain or not
display_strain = True

#Choose which index you want to display.
list_index_display = [[1,0,0]]

#Choose the size of the voxel in the 3D visualization
size = 20

#You can choose if you want the maximum of the color bar for the strain
vmax = None

#Chosse the color map for the strain
cmap_strain = 'bwr'

#Choose the color of the backgroud
background_color = 'black'

#Choose the angle of the first 3D view
elev=100
azim=90
roll=180


def display(clustering_label, vmax, clustering_label_index = None):

    if display_strain:

        clustering_strain = np.zeros(np.shape(clustering_label))

        for i in range(len(clustering_label_index)):
            label = clustering_label_index[i][0]
            strain = clustering_label_index[i][-1][1]
            x, y, z = np.where(clustering_label == label)
            clustering_strain[x, y, z] = strain
        
    # Display label

    # Get the unique labels
    unique_labels = np.unique(clustering_label)


    N = ceil((len(unique_labels))**(1/3))+1
    list_colors = []
    for i in range(N):
        for j in range(N):
            for k in range(N):
                list_colors.append((i*1/N, j*1/N, k*1/N, 1))
    random.shuffle(list_colors)

    len_list_colors = len(list_colors)
    color_labels = []
    for i in range(len(unique_labels)):
        color_labels.append(list_colors[round(i*len_list_colors/len(unique_labels))])
    
    # Create a color map with the same number of colors as unique labels
    colours=[]
    bins=[0.5]
    n=1.5
    for i in range(len(unique_labels)-1):
        colours.append(color_labels[i])
        bins.append(n)
        n += 1

    assert len(bins)== len(colours)+1
    cmap = mpl.colors.ListedColormap(colours)
    norm = mpl.colors.BoundaryNorm(boundaries=bins, ncolors=len(cmap.colors))

    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    x, y, z = np.where(clustering_label >=1)
    values = clustering_label[x, y, z]

    scatter = ax.scatter(x, y, z, c=values, cmap=cmap, s=size)

    plt.title(f'{nb_facets}')

    #Set the view angles (azim, elev)
    ax.view_init(elev=elev, azim=azim, roll = roll)  # Adjust the angles as needed

    # Set equal aspect ratio for all axes
    ax.set_box_aspect([np.ptp(coord) for coord in [x, y, z]])

    # Hide the axes (frame)
    ax.set_axis_off()

    # Create a separate axis for the colorbar
    cax = fig.add_axes([0.95, 0.1, 0.02, 0.8])  # Adjust the position and size as needed

    # Create the colorbar and associate it with the scatter plot
    cbar = mpl.colorbar.ColorbarBase(cax, cmap=cmap, norm=norm, ticks=unique_labels, boundaries=bins, spacing='uniform', format='%1i')

    # Displaying indices at the center of each facet
    if not clustering_label_index is None:
        for i in range(len(clustering_label_index)):
            label = clustering_label_index[i][0]
            if label <= nb_facets:
                index = clustering_label_index[i][1]
                if index in list_index_display:
                    index_x, index_y, index_z = index
                    center_x = np.mean(np.where(clustering_label == label)[0])
                    center_y = np.mean(np.where(clustering_label == label)[1])
                    center_z = np.mean(np.where(clustering_label == label)[2])

                    ax.text(center_x, center_y, center_z, f"({index_x}, {index_y}, {index_z})",
                        color='black', fontsize=8, ha='center', zorder=10)

    # plt.show()

    if display_strain:

        # Display strain

        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')

        x, y, z = np.where(clustering_label >= 1)
        values = clustering_strain[x, y, z]

        cmap = cmap_strain

        # Calculate the symmetric range around 0
        if vmax is None:
            vmax = max(np.max(values), -np.min(values))
        vmin = -vmax

        norm = TwoSlopeNorm(vmin=vmin, vcenter=0, vmax=vmax)

        scatter = ax.scatter(x, y, z, c=values, cmap=cmap, s=size, norm=norm)

        plt.title(f'{nb_facets}')

        #Set the view angles (azim, elev)
        ax.view_init(elev=elev, azim=azim, roll = roll)  # Adjust the angles as needed

        # Set equal aspect ratio for all axes
        ax.set_box_aspect([np.ptp(coord) for coord in [x, y, z]])

        # Hide the axes (frame)
        ax.set_axis_off()

        ax.set_facecolor(background_color)

        # Create a separate axis for the colorbar
        cax = fig.add_axes([0.75, 0.1, 0.02, 0.8])  # Adjust the position and size as needed

        # Create the colorbar and associate it with the scatter plot
        cbar = mpl.colorbar.ColorbarBase(cax, cmap=cmap, norm=norm)

        # Displaying indices at the center of each facet

        for i in range(len(clustering_label_index)):
            label = clustering_label_index[i][0]
            if label <= nb_facets:
                index = clustering_label_index[i][1]
                if index in list_index_display:
                    index_x, index_y, index_z = index
                    center_x = np.mean(np.where(clustering_label == label)[0])
                    center_y = np.mean(np.where(clustering_label == label)[1])
                    center_z = np.mean(np.where(clustering_label == label)[2])

                    ax.text(center_x, center_y, center_z, f"({index_x}, {index_y}, {index_z})",
                        color='black', fontsize=8, ha='center', zorder=10)
                    
if analysis == 'facet' or analysis == 'all':
    facet_label = np.load(f'{path}facet_label.npy')

    try:
        with open(f'{path}facet_label_index.json', 'r') as f:
            facet_label_index = json.load(f)

        print('strain_max = ', max(facet_label_index, key = lambda elem : elem[-1][1]))

        display(facet_label, vmax, facet_label_index)
    except: 
        display(facet_label, vmax)

if analysis == 'edge' or analysis == 'all':
    edge_label = np.load(f'{path}edge_label.npy')
    
    try: 
        with open(f'{path}edge_label_index.json', 'r') as f:
            edge_label_index = json.load(f)

        display(edge_label, vmax, edge_label_index)
    except: 
        display(edge_label, vmax)

if analysis == 'corner' or analysis == 'all':
    corner_label = np.load(f'{path}corner_label.npy')

    try:
        with open(f'{path}corner_label_index.json', 'r') as f:
            corner_label_index = json.load(f)

        display(corner_label, vmax, corner_label_index)
    except: 
        display(corner_label, vmax)

plt.show()
