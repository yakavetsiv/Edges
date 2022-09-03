# -*- coding: utf-8 -*-
"""
Created on Sun Jul 24 18:19:28 2022

@author: vipro
"""

import tifffile
import numpy as np
from skimage import io
from scipy import ndimage
import pandas as pd

def load_angles(name):
    df = pd.read_csv(name)
    df['Angle'] = df['Angle']*(-1)
    df['Slice'] = df['Slice'] -1
    
    an = df['Angle'].tolist()
    fr = df['Slice'].tolist()
    return fr, an
    
def rotate(img, origin, degrees):
    padX = [img.shape[1] - pivot[0], pivot[0]]
    padY = [img.shape[0] - pivot[1], pivot[1]]
    imgP = np.pad(img, [padY, padX, [0,0]], 'constant')

    imgR = ndimage.rotate(imgP, degrees, reshape=False)
    imgC = imgR[padY[0] : -padY[1], padX[0] : -padX[1]]
    
    return imgC


def lin_time(frames, angles):
    an = np.linspace(angles[0],angles[1], num=frames[1]-frames[0])
    fr = np.arange(frames[0]-1,frames[1], 1)
    return fr, an
    

def rotate_seq(img, frames, angles, pivot):
    img_rot = []

    for frame, angle in zip(frames, angles):
        imgC = rotate(img_raw[frame], pivot,  angle)
        img_rot.append(imgC)
        
    return img_rot

def save_seq(img, name):
    tifffile.imwrite('d:/temp/6hrs_rot.tif', img)

pivot = (300, 317)


table_name = 'd:/temp/Results.csv'
fr, an = load_angles(table_name)

#fr, an = lin_time([1,19],[0,25])

img_name = 'd:/temp/6hrs_r.tif'
img_raw = io.imread(img_name)

imgC = rotate_seq(img_raw, fr, an, pivot)

res_name = 'd:/temp/6hrs_rot.tif'
save_seq(imgC, res_name)



  

    
