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

filename = "dynamic_images.html"
# change the fps to speed up or slow down the animation
writer = animation.HTMLWriter(fps=4)
# ensure matrix is not truncated
np.set_printoptions(threshold=np.inf)

fig = plt.figure()

# array of images
ims = []

def simulation(nrep):
    # The density of mud in the forest not occupied by trees
    p = 0.4
    # Forest size (number of cells in x and y directions).
    ny, nx = 10, 10

    ## The total distance across the simulation replications.
    TD = 0

    ## The number of times that the edge is reached.
    NB = 0

    for i in range(int(nrep)):
        # Initialize the forest grid.
        X = np.random.choice([0, 1], size=ny * nx, p=[1-p, p]).reshape(ny, nx)
        # Starting position of fire at centre of grid
        X[(ny//2), (nx//2)] = 2
        # Displacements from a cell to its eight nearest neighbours
        neighbourhood = ((-1, 1), (0, 1), (1, 1), (1, 0), (1, -1), (0, -1), (-1, -1), (-1, 0))

        """Iterate the forest according to the forest-fire rules."""

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
                        if X[i[0] + dy, i[1] + dx] == 0:
                            X[i[0] + dy, i[1] + dx] = 2
                            draw(X)
                            if i[0] + dy == ny - 1  or i[1] + dx == nx - 1:
                                print(str(i[0] + dy) + " = " + str(ny - 1) + " or " + str(
                                    i[0] + dy) + " = " + str(nx - 1))
                                create_animation()
                                print("Reached Edge")
                                boolean = False
                                break
                            else:
                                positions.append([i[0] + dy, i[1] + dx])
                        continue
                    except IndexError:
                        pass
            if boolean != False:
                print("Fire stopped spreading")
                create_animation()
            break

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


def main():
    # The number of simulation replications.
    nrep = 1
    simulation(nrep)
    print("exit")


if __name__ == '__main__':
    main()
