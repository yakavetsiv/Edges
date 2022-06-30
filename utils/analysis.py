#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun 20 22:13:48 2022

@author: viprorok
"""

import pandas as pd 
import matplotlib.pyplot as plt
import numpy as np
from scipy.signal import savgol_filter


def load_data(name):
    data = pd.read_csv(name)
    data.columns = ['time', 'h']

    return data

def calc_flow_rate(data, scale, time_int):
    data['time'] = data['time']*time_int
    
    window = (data.shape[0] // 2)*2 -1
    
    ###ul
    data['vol'] = data['h']/scale    
    data['vol_smooth'] = savgol_filter(data['vol'], window, 1)
    
    ###Flow rate (ul/h)

    data['q'] = -np.gradient(data['vol_smooth'].to_numpy(), data['time'].to_numpy()/60)
    data['q_smooth'] = savgol_filter(data['q'], window, 1)
    

    return data



def plot_results(data):
    
    t = data['time']   
    q = data['q'] 
    vol = data['vol']
    q_smooth = data['q_smooth']
    vol_smooth = data['vol_smooth']
    
    q_mean = (vol.max()-vol.min())/t[len(t)-1]*60
    print(round(q_mean,2))

    fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(10, 5))
    
    ax[0].scatter(t,vol, marker = '+')
    ax[0].plot(t,vol_smooth, linewidth = 1, color = 'black')
    
    
    ax[1].scatter(t,q, marker = '+')
    ax[1].plot(t,q_smooth, linewidth = 2, color = 'black')

    ax[1].plot([0,t[len(t)-1]],[q_mean,q_mean], linewidth = 2, color = 'tab:red')
    ax[1].text(t[len(t)-1]-30, q_mean+3, f'{round(q_mean,2)} ul/h', color = 'tab:red')
    
    
    ax[0].set_xlim(0,t[len(t)-1])
    ax[0].set_xlabel('Time (min)')
    ax[0].set_ylabel('Volume (ul)')
    
    ax[1].set_xlim(0,t[len(t)-1])
    ax[1].set_xlabel('Time (min)')
    ax[1].set_ylabel('Flow rate (ul/h)')
    plt.show()
    

def main():
    ###scale ml/mm
    scale = 0.095
    ##time resolution in min
    time_int = 2
    
    name = '5_results-1.csv'
    data = load_data(name)
    
    data_f = calc_flow_rate(data, scale, time_int)
    plot_results(data_f)
    
    pd.DataFrame(data_f).to_csv(f'{name[:-4]}_flow.csv')


if __name__ == "__main__":
    main()