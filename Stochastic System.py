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

filename = "dynamic_images.html"
# change the fps to speed up or slow down the animation
writer = animation.HTMLWriter(fps=11)
# ensure matrix is not truncated
np.set_printoptions(threshold=np.inf)
## The density of rocks in the sand.
p = 1 - 0.599

## The number of simulation replications.
nrep = 10

## The total depth across the simulation replications.
TD = 0

## The number of times that the bottom is reached.
NB = 0

# Grid size
N = 20

# array of images
ims = []
fig = plt.figure()

# Would you like to animate the simulations, please note this could take a while
animate = True


def simulation(animate):
    ## Simulation replications.
    for i in range(int(nrep)):
        ## Randomly lay out the rocks.
        M = (1 * (np.random.uniform(0, 1, size=N * N) < p)).reshape(N, N)

        ## The initial position of the droplet.
        r = 0
        c = int(N / 2) - 1

        ## Checks whether the user wishes to animate the simulations
        if animate == True:
            M[r, c] = 2
            draw(M)

        ## Let the droplet percolate through the rocks.
        while r < N - 1:
                ## Always go straight down if possible.
            if (M[r + 1, c] == 0):
                r = r + 1
                if animate == True:
                    M[r, c] = 2
                    draw(M)
                ## Next try down/left.
            elif ((c > 1) & (M[r + 1, c - 1] == 0)):
                r = r + 1
                c = c - 1
                if animate == True:
                    M[r, c] = 2
                    draw(M)
                ## Next try down/right.
            elif ((c < N) & (M[r + 1, c + 1] == 0)):
                r = r + 1
                c = c + 1
                if animate == True:
                    M[r, c] = 2
                    draw(M)
                ## Next try right.
            elif ((c < N) & (M[r, c + 1] == 0)):
                c = c + 1
                if animate == True:
                    M[r, c] = 2
                    draw(M)
                ## We're stuck
            else:
                break

        ## Keep track of how often we reach the bottom.
        if (r == N - 1):
            global NB
            NB = NB + 1

        ## Keep track of the total of the final depths.
        global TD
        TD = TD + r

        # Draws the final frame of each simulation multiple times
        # to allow enough time for the user to pause the animation
        if animate == True:
            for i in range(5):
                draw(M)


def draw(data):
    # Colours for visualization: gold for sand, grey for rock and blue for water.
    # module is poorly coded so colours and boundary array each need one more
    # element than there are colours in the animation and numbers in the matrix.
    colors_list = ['gold', 'grey', 'black', 'blue']
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
    simulation(animate)
    if animate == True:
        create_animation()


if __name__ == '__main__':
    main()
    ## The estimated probability that we reach the bottom.
    NBprob = NB / nrep

    ## The average depth that is reached.
    TDavg = TD / nrep

    print("The grid size is: " + str(N) + " X " + str(N) + " squared")
    print("The number of simulation replications is: " + str(nrep))
    print("\nThe total depth across the simulation replications is: " + str(TD))
    print("The number of times that the bottom is reached: " + str(NB))
    print("The estimated probability that we reach the bottom is: " + str(NBprob))
    print("The average depth that is reached is: " + str(TDavg) + " of " + str(N) + " layers")
