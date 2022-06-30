#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun 20 12:05:28 2022

@author: viprorok
"""


###Preprocessing of the images in Fiji:
    ###- Open files 
    ###- Image - Stack - Images to stack
    ###- Process - Find edges
    ###- Check scale 
    ###- Chose the vector (x,y)




from skimage import io
from skimage.color import rgb2gray
import numpy as np
from skimage.draw import line
import math 
import matplotlib.pyplot as plt
import pandas as pd 


def load_stack(name):
    im = io.imread(name)
    return rgb2gray(im)

def line_profile(vector, image):
    # being start and end two points (x1,y1), (x2,y2)
    xx,yy = list(zip(line(vector[0][0],vector[0][1], vector[1][0], vector[1][1])))
    
    profile = []
    cords = []
    for x, y in zip(xx[0], yy[0]):
        pix = image[y,x]
        profile.append(pix)
        cords.append((x,y))
        
    
    return cords, profile

def max_kin(vector, stack, scale = 1):
    kin = []
    for image in stack:
        _, l_pr = line_profile(vector, image)
        #print(len(l_pr))
        max_v = np.argmax(l_pr)
        kin.append(max_v/scale)
        
    return kin
        
        
def plot_kin(kin, time_int = 1):
    fig, ax = plt.subplots()
    
    t = np.linspace(0, (len(kin)-1)*time_int, len(kin))
    ax.scatter(t,kin)
    ax.plot(t,kin)
    
    ax.set_xlabel("Time (mins)")
    ax.set_ylabel("Height (mm)")

    plt.show()
    
    
    
def main():

    ###Loading of the TIFF stack 
    
    name = 'Stack_edges.tif'
    stack = load_stack(name)
    
    
    ###Caclulating of the distance from the bottom to the max intensity (edges)
    vector = ((214,692), (222,58))
    scale = 14.62771
    time_int = 2
    
    kin = max_kin(vector, stack,scale = scale)
    
    ###Plotting the results

    plot_kin(kin, time_int = time_int)
    
    
    pd.DataFrame(kin).to_csv(f'{name[:-4]}_results.csv')
    
if __name__ == "__main__":
    main()











