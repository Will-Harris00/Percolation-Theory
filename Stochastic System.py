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
from matplotlib import colors

np.set_printoptions(threshold=np.inf)
## The density of rocks in the sand.
p = 1 - 0.599

## The number of simulation replications.
nrep = 1e2

## The total depth across the simulation replications.
TD = 0

## The number of times that the bottom is reached.
NB = 0

# Grid size
N = 20


def simulation():
    ## Simulation replications.
    for i in range(int(nrep)):
        ## Randomly lay out the rocks.
        M = (1 * (np.random.uniform(0, 1, size=N * N) < p)).reshape(N, N)

        ## The initial position of the droplet.
        r = 0
        c = int(N / 2) - 1
        M[r, c] = 2

        ## Let the droplet percolate through the rocks.
        while r < N - 1:
                ## Always go straight down if possible.
            if (M[r + 1, c] == 0):
                r = r + 1
                M[r, c] = 2
                ## Next try down/left.
            elif ((c > 1) & (M[r + 1, c - 1] == 0)):
                r = r + 1
                c = c - 1
                M[r, c] = 2
                ## Next try down/right.
            elif ((c < N) & (M[r + 1, c + 1] == 0)):
                r = r + 1
                c = c + 1
                M[r, c] = 2
                ## Next try right.
            elif ((c < N) & (M[r, c + 1] == 0)):
                c = c + 1
                M[r, c] = 2
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
        draw(M)


def draw(data):
    # Colours for visualization: gold for sand, grey for rock and blue for water.
    colors_list = ['gold', 'grey', 'black', 'blue']
    # create discrete colormap
    cmap = colors.ListedColormap(colors_list)
    bounds = [0, 1, 2, 3]
    norm = colors.BoundaryNorm(bounds, cmap.N)

    fig, ax = plt.subplots()
    ax.imshow(data, cmap=cmap, norm=norm)

    plt.show()


def main():
    simulation()


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
