# -*- coding: utf-8 -*-
"""
Created on Tue Mar 0 00:05:58 2020

@author: wjph
"""
## Simulate a forest fire percolating outwards from the
# centre of a mass of trees and mud.
##
## Generate a random NxM matrix of 0's and 1's where 1 corresponds
## to mud and 0 corresponds to trees.  Generate the values in the
## matrix independently, based on a given probability p that each
## space is occupied by mud.
##
## A drop of liquid starts at the centre of the matrix grid (row N//2,
## column M//2).  It then moves according to the following system.
##
##
## 1. Consider an individual cell and the 8 neighbouring cell that surround it
## 2. Starting from the top left neighbouring cell travel clockwise
## 3. For any cells not already on fire that contain trees set these alight
## 4. Store the location of an cells containing fire and repeat
## the above process for the outermost cells that are alight.
##
## If none of these moves can be made, the spread of the fire is stopped.
##
## Use simulation to calculate the average distance over which the fire
## spreads before getting stuck, and the proportion of the time that the
## fire reaches the edge of the forest.
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib import colors
import os
from sys import platform
import shlex
import pandas as pd
from openpyxl import load_workbook
import seaborn as sns

filename = "dynamic_images.html"
# change the fps to speed up or slow down the animation
writer = animation.HTMLWriter(fps=12)
# ensure matrix and data frame are not truncated
np.set_printoptions(threshold=np.inf)
#pd.set_option('display.max_columns', None)
#pd.set_option('display.max_rows', None)
fig = plt.figure()
# array of images
ims = []


def simulation(p, ny, nx, nrep, animate, separate):
    if separate == True:
        # empties animation array after each change in density of mud in the forest.
        global ims
        ims = []

    ## The total distance across the simulation replications.
    #TD = 0

    ## The number of times that the edge is reached.
    NB = 0

    # Displacements from a cell to its eight nearest neighbours
    neighbourhood = ((-1, 1), (0, 1), (1, 1), (1, 0), (1, -1), (0, -1), (-1, -1), (-1, 0))

    ## Simulation replications.
    for j in range(int(nrep)):
        # Initialize the forest grid.
        X = np.random.choice([0, 1], size=ny * nx, p=[1-p, p]).reshape(ny, nx)
        # Starting position of fire at centre of grid
        X[(ny//2), (nx//2)] = 2

        """Iterate the forest according to the forest-fire rules."""

        iy, ix = ny // 2, nx // 2
        positions = []
        positions.append([iy, ix])
        boolean = True
        if animate == True:
            draw(X, j+1, p, ny, nx)
        while True:
            for i in positions:
                for dx, dy in neighbourhood:
                    try:
                        ## Keep track of how often we reach the edges.
                        if boolean:
                            if ((i[0] + dy == ny - 1) or (i[1] + dx == nx - 1)) \
                                    and X[i[0] + dy, i[1] + dx] == 0:
                                X[i[0] + dy, i[1] + dx] = 2
                                NB += 1
                                boolean = False
                                break
                            else:
                                if X[i[0] + dy, i[1] + dx] == 0:
                                    X[i[0] + dy, i[1] + dx] = 2
                                    #TD = TD + 1
                                    positions.append([i[0] + dy, i[1] + dx])
                                    if animate == True:
                                        draw(X, j+1, p, ny, nx)
                        continue
                    except IndexError:
                        pass
            if animate == True:
                for i in range(5):
                    draw(X, j+1, p, ny, nx)
            break
    return NB


def main():
    # Would you like to animate the simulations, please note this could take a while
    animate = False
    # Determines whether to create new animation at each level of density or to
    # append the new frames to the existing animation.
    separate = True
    # Forest size (number of cells in x and y directions).
    sizes = [10, 50, 100, 200, 400]
    ## The number of simulation replications.
    nrep = [100]
    # By how much is p decremented for each realisation
    step = 0.01
    pc = pd.DataFrame(columns=["Grid Size", "Density", "Frequency_Reach_Bottom"])
    k = 0
    for n in sizes:
        n = round(n)
        ny, nx  = n, n
        print("\nThe grid size is: " + str(ny) + "x" + str(nx))
        for i in nrep:
            i = round(i)
            print("\nRunning simulation with " + str(i) + " realisations")
            # The density of mud in the forest not occupied by trees
            p = 1
            while p > 0:
                p -= step
                p = round(p, 2)
                sim = simulation(p, ny, nx, i, animate, separate)
                NB = sim
                ## The estimated probability that we reach the edge.
                ## Frequency with which the edge is reached at each probability
                NBprob = NB / i

                pc.loc[k] = [n, p, NBprob]
                k += 1
    # method removes trailing zeros from data frame
    size = pd.Series(pc['Grid Size'])
    mask = pd.to_numeric(size).notnull()
    size.loc[mask] = size.loc[mask].astype(np.int64)
    pc['Grid Size'] = size
    print(pc)
    # Use the 'hue' argument to provide a factor variable
    sns.scatterplot(data=pc, x="Density", y="Frequency_Reach_Bottom", hue='Grid Size',
                    legend='full', markers=["o", "x", "1", "s", "d"],
                    palette=['Burlywood', 'DarkSlateGray', 'SaddleBrown', 'Teal', 'Olive'])
    plt.title("Forest fire percolation for different size grids\n" + str(i) + " realisations")
    plt.xlim(0, 1)
    plt.ylim(0, 1)
    plt.xlabel('Density of mud in the forest')
    plt.ylabel('Expectation that the edge is reached')
    plt.legend(loc='upper right')
    plt.xticks(np.arange(0, 1+0.1, step=0.1))
    plt.yticks(np.arange(0, 1+0.1, step=0.1))
    plt.show()
    with pd.ExcelWriter("forestpcmulti.xlsx") as writer:
        writer.save()
        print("Created the excel file 'forestpcmulti.xlsx'")
    try:
        with pd.ExcelWriter("forestpcmulti.xlsx", engine='openpyxl', mode='a') as writer:
            writer.book = load_workbook("forestpcmulti.xlsx")
            sheetName = "Critical Percolations Multi"
            pc.to_excel(writer, sheetName, index=False, header=True)
            try:
                writer.book.remove(writer.book['Sheet1'])
            except KeyError:
                pass
            writer.save()
    except PermissionError:
        print("Please ensure the file 'forestpcmulti.xlsx' is not open in another program")


def draw(data, j, p, ny, nx):
    # Colours for visualization: green for trees, brown for mud and orange for fire.
    # module is poorly coded so colours and boundary array each need one more
    # element than there are colours in the animation and numbers in the matrix.
    colors_list = ['green', 'brown', 'black', 'orange']
    # observe that the colour black appears nowhere in the animation and neither
    # does the number three appear anywhere within the matrix,
    # i do not know why the developer indexes the arrays incorrectly.
    # create discrete colormap
    cmap = colors.ListedColormap(colors_list)
    bounds = [0, 1, 2, 3]
    norm = colors.BoundaryNorm(bounds, cmap.N)
    global ims
    plt.xticks([])
    plt.yticks([])
    plt.title("Density of mud in the forest: " + str(p) + "\n Number of realisations: "
              + str(j) + "\nSize of matrix: " + str(ny) + "x" + str(nx))
    im = plt.imshow(data, cmap=cmap, norm=norm, animated=True)
    ims.append([im])


def create_animation():
    print("\nCreating animation, please wait...")
    ani = animation.ArtistAnimation(fig, ims, blit=True)
    ani.save(filename, writer=writer)
    # OS X
    if platform == "darwin":
        try:
            os.system("open " + shlex.quote(filename))
        except:
            print("You will need to manually open the html file")
    # Windows
    elif platform == "win32":
        try:
            os.system("start " + filename)
        except:
            print("You will need to manually open the html file")


if __name__ == '__main__':
    main()
