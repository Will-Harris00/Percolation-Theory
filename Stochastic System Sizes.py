# -*- coding: utf-8 -*-
"""
Created on Thu Feb 13 20:23:33 2020

@author: jbru
"""
## Simulate a drop of liquid percolating down through a mixture of
## sand and rock.
##
## Generate a random 100x100 matrix of 0's and 1's where 1 corresponds
## to rock and 0 corresponds to sand.  Generate the values in the
## matrix independently, based on a given probability p that each
## space is occupied by rock.
##
## A drop of liquid starts in the middle of the top layer (row 1,
## column 50).  It then moves according to the following four options,
## where options with lower numbers have higher precedence.
##
## 1. If the space directly below is sand, move there.
## 2. If the space below and to the left is sand, move there.
## 3. If the space below and to the right is sand, move there.
## 4. If the space directly to the right is sand, move there.
##
## If none of these moves can be made, the drop of liquid is stuck.
##
## Use simulation to calculate the average depth to which the liquid
## drops before getting stuck, and the proportion of the time that the
## drop reaches the bottom layer.
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
writer = animation.HTMLWriter(fps=4)

# ensure matrix and data frame are not truncated
np.set_printoptions(threshold=np.inf)
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
fig = plt.figure()

# array of images
ims = []


def simulation(p, N, nrep, animate, separate):
    if separate == True:
        # empties animation array after each change in density of rocks in the sand.
        global ims
        ims = []

    ## The total depth across the simulation replications.
    TD = 0

    ## The number of times that the bottom is reached.
    NB = 0

    ## Simulation replications.
    for j in range(int(nrep)):
        ## Randomly lay out the rocks.
        M = (1 * (np.random.uniform(0, 1, size=N * N) < p)).reshape(N, N)

        ## The initial position of the droplet.
        r = 0
        c = int(N / 2) - 1

        ## Checks whether the user wishes to animate the simulations
        if animate == True:
            M[r, c] = 2

        ## Let the droplet percolate through the rocks.
        while r < N - 1:
            try:
                ## Always go straight down if possible.
                if (M[r + 1, c] == 0):
                    r = r + 1
                    if animate == True:
                        M[r, c] = 2

                ## Next try down/left.
                elif ((c > 1) & (M[r + 1, c - 1] == 0)):
                    r = r + 1
                    c = c - 1
                    if animate == True:
                        M[r, c] = 2

                ## Next try down/right.
                elif ((c < N) & (M[r + 1, c + 1] == 0)):
                    r = r + 1
                    c = c + 1
                    if animate == True:
                        M[r, c] = 2

                ## Next try right.
                elif ((c < N) & (M[r, c + 1] == 0)):
                    c = c + 1
                    if animate == True:
                        M[r, c] = 2

                ## We're stuck
                else:
                    break

            ## We've reached the edge of the screen
            except IndexError:
                break

        ## Keep track of how often we reach the bottom.
        if (r == N - 1):
            NB = NB + 1

        ## Keep track of the total of the final depths.
        TD = TD + r

        # Draws the final frame of each simulation for a number of realisations
        if animate == True:
            draw(M, j + 1, p, N)

    ## Draws the final frame of the last simulation for number of realisations
    ## to allow enough time for the user to pause the animation
    if animate == True:
        for i in range(5):
            draw(M, j + 1, p, N)
        create_animation()
    return NB, TD


def main():
    # Would you like to animate the simulations, please note this could take a while
    animate = False
    # Determines whether to create new animation at each level of density or to
    # append the new frames to the existing animation.
    separate = True
    # Grid size
    sizes = [10, 50, 100, 200, 400]
    ## The number of simulation replications.
    nrep = [100]
    # By how much is p decremented for each realisation
    step = 0.01
    pc = pd.DataFrame(columns=["Grid Size", "Density", "Frequency_Reach_Bottom"])
    k = 0
    for N in sizes:
        n = round(n)
        print("\nThe grid size is: " + str(N) + "x" + str(N))
        for i in nrep:
            i = round(i)
            print("\nRunning simulation with " + str(i) + " realisations")
            ## The density of rocks in the sand.
            p = 1
            while p > 0:
                p = round(p, 2)
                sim = simulation(p, N, i, animate, separate)
                NB = sim[0]
                ## The estimated probability that we reach the bottom.
                ## Frequency with which the bottom is reached at each probability
                NBprob = NB / i

                pc.loc[k] = [N, p, NBprob]
                k += 1
                p -= step
    # method removes trailing zeros from data frame
    size = pd.Series(pc['Grid Size'])
    mask = pd.to_numeric(size).notnull()
    size.loc[mask] = size.loc[mask].astype(np.int64)
    pc['Grid Size'] = size
    print(pc)
    # Use the 'hue' argument to provide a factor variable
    sns.scatterplot(data=pc, x="Density", y="Frequency_Reach_Bottom", hue='Grid Size',
                    legend='full', markers=["o", "x", "1", "s", "d"],
                    palette=['green', 'orange', 'purple', 'dodgerblue', 'red'])
    plt.title("Water percolation for different size grids\n" + str(i) + " realisations")
    plt.xlim(0, 1)
    plt.ylim(0, 1)
    plt.xlabel('Density of rock in the sand')
    plt.ylabel('Expectation that the bottom is reached')
    plt.legend(loc='upper right')
    plt.xticks(np.arange(0, 1+0.1, step=0.1))
    plt.yticks(np.arange(0, 1+0.1, step=0.1))
    plt.show()
    with pd.ExcelWriter("percolationpcmulti.xlsx") as writer:
        writer.save()
        print("Created the excel file 'percolationpcmulti.xlsx'")
    try:
        with pd.ExcelWriter("percolationpcmulti.xlsx", engine='openpyxl', mode='a') as writer:
            writer.book = load_workbook("percolationpcmulti.xlsx")
            sheetName = "Critical Percolations Multi"
            pc.to_excel(writer, sheetName, index=False, header=True)
            try:
                writer.book.remove(writer.book['Sheet1'])
            except KeyError:
                pass
            writer.save()
    except PermissionError:
        print("Please ensure the file 'percolationpcmulti.xlsx' is not open in another program")


def draw(data, j, p, N):
    # Colours for visualization: gold for sand, grey for rock and blue for water.
    # module is poorly coded so colours and boundary array each need one more
    # element than there are colours in the animation and numbers in the matrix.
    colors_list = ['burlywood', 'grey', 'black', 'aqua']
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
              + str(j) + "\nSize of matrix: " + str(N) + "x" + str(N))
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
