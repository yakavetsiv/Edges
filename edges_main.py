#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 22 21:59:36 2022

@author: viprorok
"""
from PyQt5 import QtWidgets, uic, QtGui
from PyQt5.QtGui import QPixmap, QIcon, QImage, QPainter, QBrush, QPen
from PyQt5.QtWidgets import QMenu, QMenuBar, QFileDialog, QMainWindow, QAction, qApp, QApplication, QListWidgetItem
from PyQt5.QtCore import Qt 

import qimage2ndarray

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import sys
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from skimage import io
from skimage.draw import (line_aa, circle_perimeter_aa)

from PIL import Image
from utils.edges_flow import *
from utils.analysis import *

import math



class SecondWindow(QtWidgets.QMainWindow):
    def __init__(self):
      
         super(SecondWindow, self).__init__()

             
         
         self.main_widget = QtWidgets.QWidget()
         self.setCentralWidget(self.main_widget)
         
         save_data_B = QtWidgets.QPushButton("Save data")
         save_plot_B = QtWidgets.QPushButton("Save plot")
         
         radio_1 = QtWidgets.QRadioButton("Volume")
         radio_1.setChecked(True)
         radio_1.toggled.connect(self.onClicked)
         radio_1.state = 0
         self.plot_type = 0
         
         
         radio_2 = QtWidgets.QRadioButton("Flow rate")
         radio_2.toggled.connect(self.onClicked)
         radio_1.state = 1

         layout_main = QtWidgets.QVBoxLayout(self.main_widget)
         
         self.canvas = MyMplCanvas(self.main_widget, width = 300, height = 200)
         layout_main.addWidget(self.canvas)
         
         layout_btn = QtWidgets.QHBoxLayout()
         
         
         layout_btn.addWidget(radio_1)
         layout_btn.addWidget(radio_2)
         layout_btn.addWidget(save_data_B)
         layout_btn.addWidget(save_plot_B)
         
         layout_main.addLayout(layout_btn)
         
         save_plot_B.clicked.connect(self.save_plot)
         save_data_B.clicked.connect(self.save_data)
    
    def onClicked(self):
        radioButton = self.sender()
        if radioButton.isChecked():
            if radioButton.text() == "Volume":
                self.plot_type = 0
            else:
                self.plot_type = 1
        
        self.canvas.update_figure(self.plot_type)
        self.canvas.draw()
        
        
    
    def save_plot(self):
        dialog = QtWidgets.QFileDialog()
        fileName, ext = dialog.getSaveFileName(None, "Save plot", "", "PNG (*.png);;JPEG (*.jpeg)", options=QtWidgets.QFileDialog.DontUseNativeDialog)
        
        if  (fileName  == '') :
            return
        if ext == 'PNG (*.png)':
            fileName = fileName + '.png'
        if ext == 'JPEG (*.jpeg)':
            fileName = fileName + '.jpeg'
        
        self.canvas.fig.savefig(fileName)

        
    def save_data(self):
        dialog = QtWidgets.QFileDialog()
        fileName, ext = dialog.getSaveFileName(None, "Save data", "", "CSV (*.csv)", options=QtWidgets.QFileDialog.DontUseNativeDialog)
        
        fileName = fileName + '.csv'
        
        self.canvas.data.to_csv(fileName, index = False)

         
         

class MyMplCanvas(FigureCanvas):

    def __init__(self, parent=None, width= 300, height= 200):
        self.fig = Figure(figsize=(width, height))
        self.axes = self.fig.add_subplot(111)

        
        parameters = {'xtick.labelsize': 10,
                  'ytick.labelsize': 10,
                  'font.family':'sans-serif',
                  'font.sans-serif':['Arial']}
        plt.rcParams.update(parameters)
        

        FigureCanvas.__init__(self, self.fig)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(self, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

    def compute_figure(self, state, data):
        
        colors = ['Red', 'Green', 'Blue',  'Yellow', 'Purple', 'Cyan']
        
        self.data = data
        
        self.axes.cla() 
       
        
        x = data['time']
        n = (len(data.columns)-1) // 4
        
        self.axes.set_xlabel('Time (min)', fontsize=10)
        self.axes.set_xlim(0,x[len(x)-1])  
        
        if state == 0:
            self.axes.set_ylabel('Volume  (ul)', fontsize=10)
            
            for i in range(n):
                color = colors[i % 6]
                y = data[f'vol_{i}']
                y_raw = data[f'vol_raw_{i}']
                
                self.axes.scatter(x,y_raw, marker = '+', color = color)
                self.axes.plot(x,y, linewidth = 1, color = color)
                
                
        else:
            self.axes.set_ylabel('Flow rate (ul/h)', fontsize=10)
            
            for i in range(n):
                color = colors[i % 6]
                
                y = data[f'q_{i}']
                y_raw = data[f'q_raw_{i}']
                
                
                vol = data[f'vol_raw_{i}']
                
                q_mean = (vol.max()-vol.min())/x[len(x)-1]*60
                print(q_mean)
                
                self.axes.scatter(x,y_raw, marker = '+', color = color)
                self.axes.plot(x,y, linewidth = 1, color = color)                
                #self.axes.plot([0,x[len(x)-1]],[q_mean,q_mean], linewidth = 2, color = 'tab:red')
                #self.axes.text(x[len(x)-1]-30, q_mean+3, f'{round(q_mean,2)} ul/h', color = 'tab:red')
        
  
        self.fig.set_tight_layout(True)
        
        
        
        
    def update_figure(self, state):
        self.compute_figure(state, self.data)


class MainWindow(QtWidgets.QMainWindow):
    
    
    def __init__(self, *args, **kwargs):
        
        super().__init__(*args, **kwargs)
        uic.loadUi("gui/edges_ui.ui", self)
        self._createMenuBar()
        self.frameBox = [(140, 22), 620, 450]
        self.connectSignalsSlots()
        
        self.colors = ['Red', 'Green', 'Blue',  'Purple']
        self.stack = None
        self.line_flag = False
        self.add_line_flag = False
        self.scale_flag = False
        self.points = []
        self.temp_point = []
        
        self.last_x, self.last_y = None, None
        
        self.add_line_B.setShortcut("Ctrl+A")
        
    def _createMenuBar(self):
        
        openAct = QAction(QIcon('exit.png'), ' &Open file', self)   

        openAct.setShortcut('Ctrl+O')
        openAct.setStatusTip('Open sequence')
        openAct.triggered.connect(self.open_file)
        
        
        exitAct = QAction(QIcon('exit.png'), ' &Quit', self)   
        exitAct.setShortcut('Ctrl+Q')
        exitAct.setStatusTip('Exit application')
        exitAct.triggered.connect(qApp.quit)
        
        
        menuBar = QMenuBar()
        self.setMenuBar(menuBar)
        menuBar.setNativeMenuBar(False)
        # Creating menus using a QMenu object
        fileMenu = QMenu(" &File", self)
        fileMenu.addAction(openAct)
        fileMenu.addSeparator()
        fileMenu.addAction(exitAct)
        
        menuBar.addMenu(fileMenu)
        # Creating menus using a title
        
    def open_file(self):
        fname = QFileDialog.getOpenFileName(self, 'Open file', '/Users/viprorok/Downloads/Sina - kin/',"Image files (*.tif)")
    
        self.stack = load_stack(fname[0])
        self.frames_total = self.stack.shape[0]
        self.frame = 0
        
        self.update_frame()
        
        self.add_line_B.setEnabled(True)
        self.scale_B.setEnabled(True)
        
        self.list_lines.clear()
        self.remove_line_B.setEnabled(False)
        self.clear_B.setEnabled(False)
        
        if self.frames_total > 1:
            self.slider.setEnabled(True)
            self.slider.setMaximum(self.frames_total)

        

    def draw_lines(self, coords, im):
        
        im = im/im.max()*255
        overlay = np.zeros((*im.shape,4), dtype=np.uint8)
        overlay[:,:,3] = 255 - im     
        
        if len(coords)>0:
            for i, line_coords in enumerate(coords):                          
                rr, cc, val = line_aa(line_coords[0][1], line_coords[0][0], line_coords[1][1], line_coords[1][0])
                rr_1, cc_1, val_1 = circle_perimeter_aa(line_coords[0][1], line_coords[0][0], 10)
                rr_2, cc_2, val_2 = circle_perimeter_aa(line_coords[1][1], line_coords[1][0], 5)
                self.add_to_overlay(overlay, rr, cc, val, i)
                self.add_to_overlay(overlay, rr_1, cc_1, val_1, i)  
                self.add_to_overlay(overlay, rr_2, cc_2, val_2, i)
                

        return overlay
        
    def add_to_overlay(self, overlay, rr, cc, val, i):
        i = i % 6
        
        if i < 3:
            overlay[rr, cc,i] = val * 255
            overlay[rr, cc,3] = 255
            
        if i == 3:
            overlay[rr, cc,0] = val * 255
            overlay[rr, cc,1] = val * 255
            overlay[rr, cc,3] = 255
        if i == 4:
            overlay[rr, cc,1] = val * 255
            overlay[rr, cc,2] = val * 255
            overlay[rr, cc,3] = 255
        if i == 5:
            overlay[rr, cc,0] = val * 255
            overlay[rr, cc,2] = val * 255
            overlay[rr, cc,3] = 255   
            
        return overlay
        
        
        
        
        
        
    def update_image(self, im):
        
        
        
        
        canvas = self.draw_lines(self.points, im)
        
        
        qimage=qimage2ndarray.array2qimage(canvas, normalize = True)
        #qimage = QImage(im_np.data, im.shape[1], im.shape[0], 3* im.shape[0], QImage.Format_Indexed8)                                                                                                                                                                 
        self.pixmap = QPixmap(qimage)                                                                                                                                                                      
        self.pixmap = self.pixmap.scaled(620, 450, Qt.KeepAspectRatio)   
        
                        
        if im.shape[1] > im.shape[0]:
            self.scale = 620/im.shape[1]      
            
        else:
            self.scale = 450/im.shape[0]
                                                                                                                                                
        self.label_im.setPixmap(self.pixmap)

    
    def update_frame(self):
        self.frame = self.slider.value()
        self.frame_L.setText(f'{self.frame}/{self.frames_total}')
        self.update_image(self.stack[self.frame-1])
        
        
    
    def connectSignalsSlots(self):
        self.slider.valueChanged.connect(self.update_frame)
        self.add_line_B.clicked.connect(self.add_line)
        self.clear_B.clicked.connect(self.clear_list)
        self.remove_line_B.clicked.connect(self.remove_line)
        self.scale_B.clicked.connect(self.set_scale)
        self.analysis_B.clicked.connect(self.analysis)
        
    
    def set_scale(self):
        self.scale_flag = True
    
    def add_line(self):
        self.add_line_flag = True
    
    def clear_list(self):
        self.list_lines.clear()
        self.update_frame()
        
    def remove_line(self):
        before = self.list_lines.count()
        row = self.list_lines.currentRow()
        self.list_lines.takeItem(row)
        after = self.list_lines.count()
        if before > after :
            self.points.pop(row)
        
        if self.list_lines.count() == 0:
            self.remove_line_B.setEnabled(False)
            self.clear_B.setEnabled(False)
            self.analysis_B.setEnabled(False)
        self.update_frame()
            
        
        
    def mousePressEvent(self, e):
        

            if not(self.stack is None):
                
                if e.button() == Qt.LeftButton: 
                    x = round((e.pos().x() - self.frameBox[0][0])/self.scale)
                    y = round((e.pos().y() - self.frameBox[0][1])/self.scale)
                    
                    if (0 <= x <= self.stack.shape[2]) & (0 <= y <= self.stack.shape[1]):
                        if self.line_flag:
                            self.temp_point.append((x,y))
                            
                            if self.add_line_flag:
                                self.points.append(self.temp_point)
                                self.line_flag = False
                                
                                self.list_lines.addItem(f'{self.temp_point}')
                                
                            
                                
                                self.temp_point = []
                                self.remove_line_B.setEnabled(True)
                                self.clear_B.setEnabled(True)
                                self.analysis_B.setEnabled(True)
                                self.update_frame()
                                
                            if self.scale_flag:
                                dist = math.dist(self.temp_point[0], self.temp_point[1])/10
                                self.scale_T.setText(f'{round(dist,3)}')
                                self.line_flag = False
                                self.temp_point = []
                                self.scale_flag = False
                                self.update_frame()
                                
                            
                        else:
                            self.temp_point.append((x,y))
                            self.line_flag = True
    

    def analysis(self):
        scale = float(self.scale_T.text())
        scale_vol = float(self.scale_vol_T.text())
        time_int = int(self.time_int_T.text())
    
        
        time = np.arange(0, self.stack.shape[0], 1)
        results = pd.DataFrame(time* time_int)
        results.columns = ['time']
        
        for i, vector in enumerate(self.points):
            vector = self.points[i]
            kin = max_kin(vector, self.stack, scale = scale)
            data = pd.DataFrame(time)
            data.columns = ['time']
            data['h'] = kin
            data_f = calc_flow_rate(data, scale_vol, time_int)
            
            results[f'vol_raw_{i}'] = data_f['vol']
            results[f'q_raw_{i}'] = data_f['q']
            
            results[f'vol_{i}'] = data_f['vol_smooth']
            results[f'q_{i}'] = data_f['q_smooth']
  
        self.plot(results)
            


    def plot(self, results):
        try:
            self.SW.canvas.axes.clear()
            self.SW.canvas.compute_figure(self.SW.plot_type, results)
            self.SW.canvas.draw()

        except:
            self.SW = SecondWindow()
            self.SW.resize(450,350)
            self.SW.move(1000, 300)
            self.SW.canvas.compute_figure(self.SW.plot_type,results)
            self.SW.show()
 



def main():

    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
        
                 
if __name__ == "__main__":
    main()