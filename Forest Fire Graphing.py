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
from numpy.random import choice
import pandas as pd

filename = "dynamic_images.html"
# change the fps to speed up or slow down the animation
writer = animation.HTMLWriter(fps=12)
# ensure matrix is not truncated
np.set_printoptions(threshold=np.inf)
fig = plt.figure()
# array of images
ims = []


def simulation(p, ny, nx, nrep, animate, separate):
    if separate == True:
        # empties animation array after each change in density of mud in the forest.
        global ims
        ims = []

    ## The total distance across the simulation replications.
    TD = 0

    ## The number of times that the edge is reached.
    NB = 0

    print("\nRunning simulation:")
    # Initialize the forest grid.
    X = np.random.choice([0, 1], size=ny * nx, p=[1-p, p]).reshape(ny, nx)
    # Starting position of fire at centre of grid
    X[(ny//2), (nx//2)] = 2
    # Displacements from a cell to its eight nearest neighbours
    neighbourhood = ((-1, 1), (0, 1), (1, 1), (1, 0), (1, -1), (0, -1), (-1, -1), (-1, 0))

    """Iterate the forest according to the forest-fire rules."""
    if animate == True:
        draw(X)
    iy, ix = ny // 2, nx // 2
    positions = []
    positions.append([iy, ix])
    boolean = True
    while True:
        for i in positions:
            for dx, dy in neighbourhood:
                try:
                    ## Keep track of how often we reach the edges.
                    if boolean:
                        if ((i[0] + dy == ny - 1) or (i[1] + dx == nx - 1)) and X[i[0] + dy, i[1] + dx] == 0:
                            X[i[0] + dy, i[1] + dx] = 2
                            ## Draws the final frame of each simulation multiple times
                            ## to allow enough time for the user to pause the animation
                            if animate == True:
                                for i in range(5):
                                    draw(X)
                                create_animation()
                            boolean = False
                            break
                        else:
                            if X[i[0] + dy, i[1] + dx] == 0:
                                X[i[0] + dy, i[1] + dx] = 2
                                positions.append([i[0] + dy, i[1] + dx])
                                if animate == True:
                                    draw(X)
                    continue
                except IndexError:
                    pass
        if boolean != False:
            ## Draws the final frame of each simulation multiple times
            ## to allow enough time for the user to pause the animation
            if animate == True:
                for i in range(5):
                    draw(X)
                create_animation()
            break
        break
    return NB, TD


def main():
    # Would you like to animate the simulations, please note this could take a while
    animate = True
    # Determines whether to create new animation at each level of density or to
    # append the new frames to the existing animation.
    separate = True
    # Forest size (number of cells in x and y directions).
    ny, nx = 10, 10
    ## The number of simulation replications.
    nrep = [1e1,1e2]
    # By how much is p decremented for each realisation
    step = 0.1
    print("\nThe grid size is: " + str(ny) + " x " + str(nx))
    print("The number of simulation replications is: " + str(nrep))
    for i in nrep:
        # The density of mud in the forest not occupied by trees
        p = 1
        df = pd.DataFrame(columns=["Density", "Number_Edge"])
        j = 0
        while p > 0:
            p -= step
            print(p)
            print(nrep)
            p = round(p, 2)
            sim = simulation(p, ny, nx, i, animate, separate)
            NB = sim[0]
            TD = sim[1]
            ## The estimated probability that we reach the edge.
            NBprob = NB / i

            ## The average distance that is reached.
            TDavg = TD / i
            x = 1 - p
            df.loc[j] = [x, NB]
            j += 1
            print("\nThe density of trees in the mud is: " + str(p))
            print("The total depth across the simulation replications is: " + str(TD))
            print("The number of times that the edge is reached: " + str(NB))
            print("The estimated probability that we reach the edge is: " + str(NBprob))
            print("The average depth that is reached is: "
                  + str(TDavg) + " of " + str(ny) + " layers")
        print(df)
        df.plot(x='Density', y='Number_Edge', kind='scatter')
        plt.xlim(0, 1)
        plt.ylim(0, i)
        plt.xticks(np.arange(0, 1+step, step=0.1))
        plt.yticks(np.arange(0, i+1, step=i/10))
        plt.show()


def draw(data):
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
    im = plt.imshow(data, cmap=cmap, norm=norm, animated=True)
    ims.append([im])


def create_animation():
    print(ims)
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
