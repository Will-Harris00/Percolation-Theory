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

filename = "dynamic_images.html"
# change the fps to speed up or slow down the animation in milliseconds
writer = animation.HTMLWriter(fps=4)
# ensure matrix is not truncated
np.set_printoptions(threshold=np.inf)

fig = plt.figure()

# array of images
ims = []

def simulation(nrep):
    # The initial fraction of the forest occupied by trees.
    forest_fraction = 0.8
    # Probability of new tree growth per empty cell, and of lightning strike.
    p, f = 0, 0.1
    # Forest size (number of cells in x and y directions).
    nx, ny = 10, 10
    try:
        for i in range(int(nrep)):
            print(i)
            # Initialize the forest grid.
            X = np.zeros((ny, nx))
            X[1:ny - 1, 1:nx - 1] = np.random.randint(0, 2, size=(ny - 2, nx - 2))
            X[1:ny - 1, 1:nx - 1] = np.random.random(size=(ny - 2, nx - 2)) < forest_fraction
            draw(X)
            iterate(X, ny, nx, p, f)
    except MemoryError:
        pass


def iterate(X, ny, nx, p, f):
    # Displacements from a cell to its eight nearest neighbours
    neighbourhood = ((-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1))

    """Iterate the forest according to the forest-fire rules."""

    # The boundary of the forest is always empty, so only consider cells
    # indexed from 1 to nx-2, 1 to ny-2
    X1 = np.zeros((ny, nx))
    for ix in range(1,nx-1):
        for iy in range(1,ny-1):
            if X[iy,ix] == 0 and np.random.random() <= p:
                X1[iy,ix] = 1
                draw(X1)
            if X[iy,ix] == 1:
                X1[iy,ix] = 1
                draw(X1)
                for dx,dy in neighbourhood:
                    if X[iy+dy,ix+dx] == 2:
                        X1[iy,ix] = 2
                        draw(X1)
                        break
                else:
                    if np.random.random() <= f:
                        X1[iy,ix] = 2
                        draw(X1)
    return X1


def draw(data):
    # Colours for visualization: gold for sand, grey for rock and blue for water.
    # module is poorly coded so colours and boundary array each need one more
    # element than there are colours in the animation and numbers in the matrix.
    colors_list = ['brown', 'green', 'grey', 'orange']
    # note that the colour green appears nowhere in the animation and neither
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
    nrep = 15
    simulation(nrep)
    create_animation()
    print("exit")


if __name__ == '__main__':
    main()
