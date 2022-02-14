import tkinter as Tk
from matplotlib import pyplot as plt
import matplotlib.animation as animation
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import serial 
from threading import Thread
import time

arduino = serial.Serial(port='/dev/cu.usbmodem14701', baudrate=115200, timeout=.01)

placeHolder = False;

xData = []
dataList = []

xAccel = []
yAccel = []
zAccel = []

xGyro = []
yGyro = []
zGyro = []

timeArduino = []

buffSize = 500

file = open('myfile.txt','w', buffering =1)


class Window:

    def __init__(self,master):
        frame = Tk.Frame(master)

        self.fig = plt.figure(figsize=(14, 4.5), dpi=100)

        self.ax = self.fig.add_subplot(1,1,1)
        self.ax.set_ylim(0, 100)
        self.line, = self.ax.plot(xar, yar)

        self.canvas = FigureCanvasTkAgg(self.fig, master=master)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side='top', fill='x', expand=1)
        frame.pack()

    #def animate(self,i):
        #yar.append(99-i)
        #xar.append(i)
        #self.line.set_data(xar, yar)

    def animate(self,i):
        print("hello from plotting func")
        self.line.set_data(timeArduino,zGyro)
        self.ax.set_ylim(-10, 10)
        if len(timeArduino)>0:
            self.ax.set_xlim(timeArduino[0],timeArduino[-1])


"""
def startThread():
    print("start thread is working")
    global endSerialThread
    endSerialThread = False
    #printDataThread = Thread(target = DataPrinting)
    #printDataThread.start()
    readData = Thread(target = readArduino)
    readData.start()
"""


def serialThread():
    global file,xAccel,yAccel,zAccel,yGyro,zGyro,xGyro,timeArduino
    while 1:
        data = arduino.readline()
        data = data.decode() 
        data = str(data)
        file.write(data)
        # file.close()
        # time.sleep(.01)
        
        data = data.split()
        print("hello from serial thread")
        if(len(data)>6):
            if len(xAccel)<buffSize:
                xAccel.append(float(data[0]))
                yAccel.append(float(data[1]))
                zAccel.append(float(data[2]))

                xGyro.append(float(data[3]))
                yGyro.append(float(data[4]))
                zGyro.append(float(data[5]))
                timeArduino.append(float(data[6]))
            else:
                xAccel = xAccel[1:]
                yAccel = yAccel[1:]
                xAccel = zAccel[1:]
                xGyro = xGyro[1:]
                yGyro = yGyro[1:]
                zGyro = zGyro[1:]
                timeArduino = timeArduino[1:]

                xAccel.append(float(data[0]))
                yAccel.append(float(data[1]))
                zAccel.append(float(data[2]))

                xGyro.append(float(data[3]))
                yGyro.append(float(data[4]))
                zGyro.append(float(data[5]))
                timeArduino.append(float(data[6]))
        time.sleep(0.01)



xar = timeArduino
yar = zGyro


root = Tk.Tk()

printDataBool = Tk.IntVar()
printDataCheck = Tk.Checkbutton(root, text = "Start Data", variable = printDataBool) #lots of options here
printDataCheck.pack()

arduinoThread = Thread(target=serialThread)
arduinoThread.start()

app = Window(root)
ani = animation.FuncAnimation(app.fig, app.animate , interval=500, blit=False)



root.mainloop()