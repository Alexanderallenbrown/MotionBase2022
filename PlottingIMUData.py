import tkinter as Tk
from matplotlib import pyplot as plt
import matplotlib.animation as animation
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import serial 
from threading import Thread
import time

arduino = serial.Serial(port='/dev/tty.usbmodem2101', baudrate=115200, timeout=.1)

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
        print("hello everyone")
        x = -1
        s = 0 
        while not placeHolder:
        
            if x <1:

                file = open('myfile.txt','a', buffering =1)
            else:
                file = open('myfile.txt','a', buffering =1)

            data = arduino.readline()
            data = data.decode() 
            data = str(data)
            file.write(data)
            file.close()
            x = x+1
            time.sleep(.1)
            
            data = data.split()

            print(data)
            if x>2:
                xAccel.append(data[0])
                yAccel.append(data[1])
                zAccel.append(data[2])

                xGyro.append(data[3])
                yGyro.append(data[4])
                zGyro.append(data[5])

                timeArduino.append(data[6])
        self.line.set_data(timeArduino[x],zGyro[x])
            


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



xar = timeArduino
yar = zGyro


root = Tk.Tk()

printDataBool = Tk.IntVar()
printDataCheck = Tk.Checkbutton(root, text = "Start Data", variable = printDataBool) #lots of options here
printDataCheck.pack()

app = Window(root)
ani = animation.FuncAnimation(app.fig, app.animate , interval=1000, blit=False)



root.mainloop()