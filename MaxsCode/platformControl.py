import socket
import sys, select
import time
from numpy import *
from scipy.signal import *
from matplotlib.pyplot import *
from tkinter import *
import sys,traceback
import serial
from threading import Thread
import copy

import tkinter as tk
from washout import Washout

from matplotlib import pyplot as plt    
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.animation as animation




#create a global variable to hold the platform command
cmd = [0,0,0,0,0,0]
# command = [xdes_final,ydes_final,zdes_final,rdes_final,pdes_final,ades_final]
endSerialThread = False

washcmd = [0,0,0,0,0,0]
washoutraw = [0,0,0,0]

washdt = .01
washalg = Washout(washdt)#attempt a .01sec dt

#Plotting Options List
PlottingOptions = {"xAccel":"1","yAccel":"2","zAccel":"3",
                    "xGyro":"4","yGyro":"5","zGyro":"6"}
                 





############### CALLBACKS FOR SLIDERS ###################
def rollcallback(v):
    cmd[3]=rollslider.get()
def pitchcallback(v):
    cmd[4]=pitchslider.get()
def yawcallback(v):
    cmd[5]=yawslider.get()
def xcallback(v):
    cmd[0]=xslider.get()
def ycallback(v):
    cmd[1]=yslider.get()
def zcallback(v):
    cmd[2]=zslider.get()+0

def axcallback(v):
    washoutraw[0]=axslider.get()
def aycallback(v):
    washoutraw[1]=ayslider.get()
def azcallback(v):
    washoutraw[2]=azslider.get()
def yawratecallback(v):
    washoutraw[3]=yawrateslider.get()

############## CALLBACK FOR RUN BUTTON ##################

def startPlatformThread():
    global platthread,endSerialThread
    endSerialThread = False
    statemsg["text"] = "Connected"
    platthread = Thread(target=doPlatform)
    washoutthread = Thread(target=doWashout)
    readSerial = Thread(target = doSerial)
    platthread.start()
    washoutthread.start()
    readSerial.start()


def cleanupPlatformThread():
    global endSerialThread
    endSerialThread=True




def doWashout():
    global washoutcmd,washoutraw,endSerialThread

    while not endSerialThread:
        ax,ay,az,wz = copy.deepcopy(washoutraw[0]), copy.deepcopy(washoutraw[1]), copy.deepcopy(washoutraw[2]), copy.deepcopy(washoutraw[3])
        x,y,z,roll,pitch,yaw = washalg.doWashout(ax,ay,az,wz)
        if(abs(yaw)>.1):
            yaw = sign(yaw)*.1
        yaw = float(yaw)

        x,y,z,roll,pitch,yaw = x/.0254,y/.0254,z/.0254,roll*1.0,pitch*1.0,yaw*1.0

        washoutcmd = [x,y,z,roll,pitch,yaw]
        time.sleep(washdt)



############## Function to communicate with Arduino ###########
def doPlatform():
    global cmd,ser,endSerialThread,washoutcmd
    #initialize old time
    arduino_delay = 0.1

    #connect to the serial port.
    #the portentry.get() call gets the port name
    #from the textbox.
    ser = serial.Serial(
    port=portentry.get(), #ACM100',   #USB0',
    baudrate=115200,
    timeout = .1)
    #print("initializing")
    ser.close()
    time.sleep(2.0)
    ser.open()
    time.sleep(2.0)
    #print("done")

    starttime = time.time()
    lastsendtime = time.time()-starttime
    #this is an infinite loop  .
    while not endSerialThread:
        if not washoutBool.get():
            #print("pose commands")
            cmdlocal = copy.deepcopy(cmd)
        else:
            #print("washout")
            cmdlocal = copy.deepcopy(washoutcmd)
        #get current time
        tnow = time.time()-starttime
        # print(tnow-lastsendtime)
        if tnow-lastsendtime>arduino_delay:     ### also happens super fast
            #print 'sent'
           # print("at t = "+format(tnow,'0.2f')+", sent: "+format(cmdlocal[0],'0.2f')+","+format(cmdlocal[1],'0.2f')+","+format(cmdlocal[2],'0.2f')+","+format(cmdlocal[3],'0.4f')+","+format(cmdlocal[4],'0.4f')+","+format(cmdlocal[5],'0.4f'))
            lastsendtime = tnow
            ser.write('!'.encode())
            for ind in range(0,len(cmdlocal)-1):
              ser.write(format(cmdlocal[ind],'0.4f').encode())
              ser.write(','.encode())
            ser.write(format(cmdlocal[-1],'0.4f').encode())
            ser.write('\n'.encode())
            # time.sleep(0.01)
            #line = ser.readline()
            #print ("at time = "+format(tnow,'0.2f')+ " received: "+line)
            #print(line)
            #echomsg["text"] = "at t = "+format(tnow,'0.2f')+" received: "+line
        else:
          time.sleep(.1)
        # print(cmd)
        # time.sleep(0.1)
    ser.close()
    statemsg["text"] = "Not Connected"




xAccel = []
yAccel = []
zAccel = []

xGyro = []
yGyro = []
zGyro = []

timeArduino = []

xar = []
yar = []

xDes = []
yDes = []

buffSize = 500

yPlot = []




class IMUData:

    def __init__(self,master):
        #print("Hello from plotting function")
        frame = tk.Frame(window) #prepping for the plotter

        self.fig = plt.figure(figsize=(10 , 1), dpi=100) #define size of plot

        self.ax = self.fig.add_subplot(1,1,1) 
        self.ax.set_ylim(0, 100) #set initial y limits
        self.line, = self.ax.plot(xar, yar) #tell it what to plot
        self.line, = self.ax.plot(xDes,yDes)

        self.canvas = FigureCanvasTkAgg(self.fig, master=master)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side='top', fill='x', expand=1)
        frame.pack()


    def animate(self,i):
        #print("hello from plotting func")
        self.line.set_data(xar,yar)
        self.line.set_data(xDes,yDes) #starting to add in the line for desired plot
        
        if len(timeArduino)>0 & len(timeArduino)<buffSize:
            #print(len(timeArduino))
            self.ax.set_xlim(timeArduino[0],timeArduino[-1]) #set the x limit of plot to update with values
            self.ax.set_ylim(-max(yar)-3, max(yar)+3) #set y limit of the live plot to update with max values
        elif len(timeArduino)>0 & len(timeArduino)>buffSize:
            self.ax.set_xlim(timeArduino[(len(timeArduino)-buffSize)],timeArduino[-1])
            set.ax.set_ylim(-max(yar),max(yar))


file = open('myfile.txt','w', buffering =1)
### Function to communicate with the arduni for the IMU###

def doSerial():
    #print("helo from serial")
    global file,xAccel,yAccel,zAccel,yGyro,zGyro,xGyro,timeArduino, arduino, xar, yar, yPlot, v,x
    x =1
    arduino = serial.Serial(port=IMUportentry.get(), baudrate=115200, timeout= 50)
    while 1:
        data = arduino.readline()   
        #print(data)
        data = data.decode() 
        data = str(data)
        file.write(data)
            # file.close()
            # time.sleep(.01)
            
        data = data.split()
        #print("hello from serial thread")
        if(len(data)>6):
            if len(xAccel)<buffSize:    
                xAccel.append(float(data[0]))
                yAccel.append(float(data[1]))
                zAccel.append(float(data[2]))

                xGyro.append(float(data[3]))
                yGyro.append(float(data[4]))
                zGyro.append(float(data[5]))
                timeArduino.append(float(data[6]))
                print(v.get())
                xar = timeArduino
                if v.get() == "1":
                    yar = xAccel
                elif v.get() == "2":
                    yar = yAccel
                elif v.get() == "3":
                    yar = zAccel
                elif v.get() == "4":
                    yar = xGyro
                elif v.get() == "5":
                    yar = yGyro
                else:
                    yar = zGyro

                xDes = timeArduino #just creating some fake test data
                ydes = x+1
                

            else:
                xAccel = xAccel[1:]
                yAccel = yAccel[1:]
                zAccel = zAccel[1:]
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

                print(v.get())
                xar = timeArduino
                if v.get() == "1":
                    yar = xAccel
                elif v.get() == "2":
                    yar = yAccel
                elif v.get() == "3":
                    yar = zAccel
                elif v.get() == "4":
                    yar = xGyro
                elif v.get() == "5":
                    yar = yGyro
                else:
                    yar = zGyro
                

                #print((zGyro))
    else:
        quit()





               




################## GUI SETUP #########################

#create GUI window
window = tk.Tk()
#title the window
window.title('Lafayette Motion Platform Control')
#set window size
window.geometry("750x750+100+50")

#create a frame to hold the serial port configuration
IMUportframe = tk.Frame(window,relief=tk.GROOVE,borderwidth=3)
IMUportframe.pack()

#create a label for the IMU config:

IMUportmsg = tk.Label(IMUportframe,text="IMU port: ")
IMUportmsg.pack(side=tk.LEFT)
#create a textbox for the port name
IMUportentry = tk.Entry(IMUportframe)
#insert a default port
IMUportentry.insert(0,"/dev/cu.usbmodem2201")
IMUportentry.pack(side=tk.LEFT) 


#create a frame to hold the serial port configuration
portframe = tk.Frame(window,relief=tk.GROOVE,borderwidth=3)
portframe.pack()
#create a label for port config:
portmsg = tk.Label(portframe,text="port: ")
portmsg.pack(side=tk.LEFT)
#create a textbox for the port name
portentry = tk.Entry(portframe)
#insert a default port
portentry.insert(0,"/dev/cu.usbmodem2101")
portentry.pack(side=tk.LEFT)
# create a button to connect to platform
platbut = tk.Button(
    portframe,
    text="Connect",
    command=startPlatformThread)
platbut.pack(side=tk.RIGHT)
killbut = tk.Button(
    portframe,
    text="Disconnect",
    command=cleanupPlatformThread)
killbut.pack(side=tk.RIGHT)
#create a status message in this frame to show serial port status
statemsg = tk.Label(window,text="Not Connected")
statemsg.pack()


#create a slider for roll
rollframe = tk.Frame(window,relief=tk.GROOVE,borderwidth=3)
rollframe.pack()
rolllabel = tk.Label(rollframe,text="Roll (rad)")
rolllabel.pack(side=tk.LEFT)
rollslider = tk.Scale(rollframe,orient=tk.HORIZONTAL,from_=-0.1,to=0.1,resolution=.001,command=rollcallback,length=400)
rollslider.pack(side=tk.RIGHT)

#create a slider for pitch
pitchframe = tk.Frame(window,relief=tk.GROOVE,borderwidth=3)
pitchframe.pack()
pitchlabel = tk.Label(pitchframe,text="pitch (rad)")
pitchlabel.pack(side=tk.LEFT)
pitchslider = tk.Scale(pitchframe,orient=tk.HORIZONTAL,from_=-0.1,to=0.1,resolution=.001,command=pitchcallback,length=400)
pitchslider.pack(side=tk.RIGHT)

#create a slider for yaw
yawframe = tk.Frame(window,relief=tk.GROOVE,borderwidth=3)
yawframe.pack()
yawlabel = tk.Label(yawframe,text="yaw (rad)")
yawlabel.pack(side=tk.LEFT)
yawslider = tk.Scale(yawframe,orient=tk.HORIZONTAL,from_=-0.15,to=0.15,resolution=.001,command=yawcallback,length=400)
yawslider.pack(side=tk.RIGHT)

#create a slider for x
xframe = tk.Frame(window,relief=tk.GROOVE,borderwidth=3)
xframe.pack()
xlabel = tk.Label(xframe,text="x (in)")
xlabel.pack(side=tk.LEFT)
xslider = tk.Scale(xframe,orient=tk.HORIZONTAL,from_=-2,to=2,resolution=.1,command=xcallback,length=400)
xslider.pack(side=tk.RIGHT)

#create a slider for y
yframe = tk.Frame(window,relief=tk.GROOVE,borderwidth=3)
yframe.pack()
ylabel = tk.Label(yframe,text="y (in)")
ylabel.pack(side=tk.LEFT)
yslider = tk.Scale(yframe,orient=tk.HORIZONTAL,from_=-2,to=2,resolution=.1,command=ycallback,length=400)
yslider.pack(side=tk.RIGHT)

#create a slider for z
zframe = tk.Frame(window,relief=tk.GROOVE,borderwidth=3)
zframe.pack()
zlabel = tk.Label(zframe,text="z (in)")
zlabel.pack(side=tk.LEFT)
zslider = tk.Scale(zframe,orient=tk.HORIZONTAL,from_=-2,to=2,resolution=.1,command=zcallback,length=400)
zslider.pack(side=tk.RIGHT)

#create a status message in this frame to show serial port status
echomsg = tk.Label(window,text="No Data Received")
echomsg.pack()

washoutBool = tk.IntVar()
washcheck = tk.Checkbutton(window, text='Washout (uses bottom sliders)',variable=washoutBool, onvalue=1, offvalue=0)
washcheck.pack()

#create a slider for ax
axframe = tk.Frame(window,relief=tk.GROOVE,borderwidth=3)
axframe.pack()
axlabel = tk.Label(axframe,text="ax (g)")
axlabel.pack(side=tk.LEFT)
axslider = tk.Scale(axframe,orient=tk.HORIZONTAL,from_=-1,to=1,resolution=.1,command=axcallback,length=400)
axslider.pack(side=tk.RIGHT)

#create a slider for ay
ayframe = tk.Frame(window,relief=tk.GROOVE,borderwidth=3)
ayframe.pack()
aylabel = tk.Label(ayframe,text="ay (g)")
aylabel.pack(side=tk.LEFT)
ayslider = tk.Scale(ayframe,orient=tk.HORIZONTAL,from_=-1,to=1,resolution=.1,command=aycallback,length=400)
ayslider.pack(side=tk.RIGHT)

#create a slider for az
azframe = tk.Frame(window,relief=tk.GROOVE,borderwidth=3)
azframe.pack()
azlabel = tk.Label(azframe,text="az (g)")
azlabel.pack(side=tk.LEFT)
azslider = tk.Scale(azframe,orient=tk.HORIZONTAL,from_=-1,to=1,resolution=.1,command=azcallback,length=400)
azslider.pack(side=tk.RIGHT)

#create a slider for yawrate
yawrateframe = tk.Frame(window,relief=tk.GROOVE,borderwidth=3)
yawrateframe.pack()
yawratelabel = tk.Label(yawrateframe,text="yawrate (rad/s)")
yawratelabel.pack(side=tk.LEFT)
yawrateslider = tk.Scale(yawrateframe,orient=tk.HORIZONTAL,from_=-1,to=1,resolution=.01,command=yawratecallback,length=400)
yawrateslider.pack(side=tk.RIGHT)

app = IMUData(window)
ani = animation.FuncAnimation(app.fig, app.animate , interval=5, blit=False)

v = StringVar(window,"1")


#creating the radio button
for (text,value) in PlottingOptions.items():
    Radiobutton(window,text=text,variable=v,value=value).pack(side = "left")




# Create button, it will change label text
#button = tk.Button( window , text = "click Me" , command = change_dropdown ).pack()







""" ADD THIS AS A CHECK BUTTON TO PLOT IMU CODE OR NOT
printDataBool = tk.IntVar()
printDataCheck = tk.Checkbutton(window, text = "Start Data", variable = printDataBool) #lots of options here
printDataCheck.pack()
"""



#run the TK mainloop to keep the window up and open.
window.mainloop()