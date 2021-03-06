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

import rF2data as RF2Data


#create a global variable to hold the platform command
cmd = [0,0,0,0,0,0]
# command = [xdes_final,ydes_final,zdes_final,rdes_final,pdes_final,ades_final]
endSerialThread = False

washcmd = [0,0,0,0,0,0]
washoutraw = [0,0,0,0]

washdt = .01
washalg = Washout(washdt)#attempt a .01sec dt
washYaccel = []

#Plotting Options List
PlottingOptions = {"xAccel":"1","yAccel":"2","zAccel":"3",
                    "xGyro":"4","yGyro":"5","zGyro":"6"}

#washout plotting options
WashPlottingOptions = {"Washout X Accel":"1","Washout Y Accel":"2","Washout Z Accel":"3"}


rf2accelInfo = RF2Data.SimInfo()

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
    platthread.start()
    washoutthread.start()
    

def startIMUThread():
    readSerial = Thread(target = doSerial)
    readSerial.start()

def cleanupPlatformThread():
    global endSerialThread
    endSerialThread=True




def doWashout():
    global washoutcmd,washoutraw,endSerialThread

    while not endSerialThread:
        accelVecX = rf2accelInfo.Rf2Tele.mVehicles[0].mLocalAccel.x #should spit out the acceleration in X direction from RF2
        accelVecY = rf2accelInfo.Rf2Tele.mVehicles[0].mLocalAccel.y #should spit out the acceleration in Y direction from RF2
        accelVecZ = rf2accelInfo.Rf2Tele.mVehicles[0].mLocalAccel.z #should spit out the acceleration in Z direction from RF2
        yawRF2 = rf2accelInfo.Rf2Tele.mVehicles[0].mLocalRotAccel.x #yaw rate
        if (f.get() == 0):
            ax,ay,az,wz = copy.deepcopy(washoutraw[0]), copy.deepcopy(washoutraw[1]), copy.deepcopy(washoutraw[2]), copy.deepcopy(washoutraw[3])
        if (f.get() ==1):
            ax,ay,az,wz = (accelVecZ/9.80665,accelVecX/9.80665,accelVecY/9.80665,yawRF2/9.80665)
            #print(ax,ay,az,wz)
            
        x,y,z,roll,pitch,yaw,washYaccel,washXaccel,washZaccel,xTotal,yTotal,zTotal = washalg.doWashout(ax,ay,az,wz)
       
        if(abs(yaw)>.1):
            yaw = sign(yaw)*.1
        yaw = float(yaw)

        x,y,z,roll,pitch,yaw = x/.0254,y/.0254,z/.0254,roll*1.0,pitch*1.0,yaw*1.0
        #x,y,z,roll,pitch,yaw = x,y,z,roll*1.0,pitch*1.0,yaw*1.0
        washoutcmd = [x,y,z,roll,pitch,yaw,washYaccel,washXaccel,washZaccel,xTotal,yTotal,zTotal] #added in the washout accels here

        time.sleep(washdt)



############## Function to communicate with Arduino ###########
def doPlatform():
    global cmd,ser,endSerialThread,washoutcmd
    #initialize old time
    arduino_delay = 0.1

    #connect to the serial port.
    #the portentry.get() call gets the port name
    #from the textbox.
    ser = serial.Serial('COM13', 115200)
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
        #HACK to add z offset to platform
        #cmdlocal[2]+=2.0

        if tnow-lastsendtime>arduino_delay:     ### also happens super fast
            #print 'sent'
           # print("at t = "+format(tnow,'0.2f')+", sent: "+format(cmdlocal[0],'0.2f')+","+format(cmdlocal[1],'0.2f')+","+format(cmdlocal[2],'0.2f')+","+format(cmdlocal[3],'0.4f')+","+format(cmdlocal[4],'0.4f')+","+format(cmdlocal[5],'0.4f'))
            lastsendtime = tnow
            ser.write('!'.encode())
       
            for ind in range(0,5): #this is minus 7 to ignore the washout accels that are in this array
                ser.write(format(cmdlocal[ind],'0.4f').encode())
                ser.write(','.encode())
            ser.write(format(cmdlocal[-1],'0.4f').encode())
            ser.write('\n'.encode())
            print(cmdlocal[0] , ' + ', cmdlocal[1], ' + ', cmdlocal[2])

        else:
          time.sleep(.01)
        # print(cmd)
        # time.sleep(0.1)
    ser.close()
    statemsg["text"] = "Not Connected"




xAccel = []
yAccel = []
zAccel = []  #arrays for IMU data to dump into
xGyro = []
yGyro = []
zGyro = []
timeArduino = []

xar = []
yar = [] #x and y data for IMU Plotting

xDes = []
yDes = [] #x and y data for washout plotting

plotWashY = []
plotWashX = []
plotWashZ = [] #just creating arrays for the washout to dump data to

washoutData = [0,0,0]

buffSize = 500

yPlot = []


class IMUData:

    def __init__(self,master):
        #print("Hello from plotting function")
        frame = tk.Frame(window) #prepping for the plotter

        self.fig = plt.figure(figsize=(6 , 4), dpi=100) #define size of plot

        self.ax = self.fig.add_subplot(1,1,1) 
        self.ax.set_ylim(0, 100) #set initial y limits
        self.line, = self.ax.plot(xar, yar) #tell it what to plot
        self.line2, = self.ax.plot(xDes,yDes) #Trying to add a second line to the plot

        self.canvas = FigureCanvasTkAgg(self.fig, master=master)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side='top', fill='x', expand=1) #actually putting the canvas on the page
        frame.pack()


    def animate(self,i):
        #print("hello from plotting func")
        self.line.set_data(xar,yar)
        self.line2.set_data(xDes,yDes) #Trying to add in a line for the second plot, unsuccessful as of now
        
        if len(timeArduino)>0 & len(timeArduino)<buffSize:
            #print(len(timeArduino))
            self.ax.set_xlim(timeArduino[0],timeArduino[-1]) #set the x limit of plot to update with values
            self.ax.set_ylim(-max(yar)-3, max(yar)+3) #set y limit of the live plot to update with max values
        elif len(timeArduino)>0 & len(timeArduino)>buffSize:
            self.ax.set_xlim(timeArduino[(len(timeArduino)-buffSize)],timeArduino[-1])
            self.ax.set_ylim(-max(yar),max(yar))


file = open('IMUFileNoMotionTest.txt','w', buffering =1) #opening the text file for the data: name this x,y,z validation to be clear about the movement
fileWash = open('washFileNoMotionTest.txt','w',buffering=1)
### Function to communicate with the arduni for the IMU###

def doSerial():
    #print("helo from serial")
    global file,xAccel,yAccel,zAccel,yGyro,zGyro,xGyro,timeArduino, arduino, xar, yar, yPlot, v,x, xDes, yDes, plotWashY, plotWashX, plotWashZ,w, washoutData
    y =1
    arduino = serial.Serial('COM10',115200)
    while not endSerialThread:
        data = arduino.readline()   
        #print(data)
        data = data.decode() 
        data = str(data)
        file.write(data) #getting the data and writing it to a text file            
        data = data.split()

        #print("hello from serial thread")
        if(len(data)>6):
            if len(xAccel)<buffSize:    
                y=y+1
                xAccel.append(float(data[0]))
                yAccel.append(float(data[1]))
                zAccel.append(float(data[2]))

                xGyro.append(float(data[3]))
                yGyro.append(float(data[4]))
                zGyro.append(float(data[5]))
                timeArduino.append(float(data[6])) #adding data to the array

                plotWashY.append(float(washoutcmd[9]))
                plotWashX.append(float(washoutcmd[10]))
                plotWashZ.append(float(washoutcmd[11]))

                #washoutData = (plotWashY + plotWashX + plotWashZ)             
                #washoutData = str(washoutData)
                fileWash.write(str(plotWashY[-1]) + ", " + str(plotWashX[-1]) + ", " +  str(plotWashZ[-1]) + " \n") #writing washout data to a file 
                #print(v.get())
                xar = timeArduino
                if v.get() == "1":
                    yar = xAccel
                elif v.get() == "2":
                    yar = yAccel
                elif v.get() == "3":
                    yar = zAccel
                elif v.get() == "4":   #These are for the radio button choices
                    yar = xGyro
                elif v.get() == "5":
                    yar = yGyro
                else:
                    yar = zGyro

                xDes = timeArduino 
                if w.get() == "1":
                    yDes = plotWashY
                elif w.get() == "2":
                    yDes = plotWashX            #Washout plotting options
                else:
                    yDes = plotWashZ
                

            else:
                y = y+1
                xAccel = xAccel[1:]
                yAccel = yAccel[1:]
                zAccel = zAccel[1:]
                xGyro = xGyro[1:]
                yGyro = yGyro[1:]
                zGyro = zGyro[1:]
                timeArduino = timeArduino[1:] #this removes the first index of the array to make space for a new one

                plotWashY = plotWashY[1:]
                plotWashX = plotWashX[1:]
                plotWashZ = plotWashZ[1:]

                xAccel.append(float(data[0]))
                yAccel.append(float(data[1]))
                zAccel.append(float(data[2]))

                xGyro.append(float(data[3]))
                yGyro.append(float(data[4]))
                zGyro.append(float(data[5]))
                timeArduino.append(float(data[6])) #adding data to the array

                plotWashY.append(float(washoutcmd[6])) #washout data collecting
                plotWashX.append(float(washoutcmd[7]))
                plotWashZ.append(float(washoutcmd[8]))

                #washoutData = (plotWashY,plotWashX,plotWashZ)             
                #ashoutData = str(washoutData)
                #fileWash.write(washoutData)
                fileWash.write(str(plotWashY[-1]) + ", " + str(plotWashX[-1]) + ", " +  str(plotWashZ[-1]) + " \n") #writing washout data to a file 

                #print(v.get())
                xar = timeArduino
                if v.get() == "1":
                    yar = xAccel
                elif v.get() == "2":
                    yar = yAccel
                elif v.get() == "3":
                    yar = zAccel                #IMU radio button choices
                elif v.get() == "4":
                    yar = xGyro
                elif v.get() == "5":
                    yar = yGyro
                else:
                    yar = zGyro

                xDes = timeArduino 
                if w.get() == "1":
                    yDes = plotWashX
                elif w.get() == "2":
                    yDes = plotWashY            #Washout plotting options
                else:
                    yDes = plotWashZ
        time.sleep(.01)
    arduino.close() #closes arduino if disconnect button is pressed
     

##def doRF2():
##    global accelVecX, accelVecY,accelVecZ, f
##    if (f.get() == 1):
##        while True:
##            accelVecX = rf2accelInfo.Rf2Tele.mVehicles[0].mLocalAccel.x #should spit out the acceleration in X direction from RF2
##            accelVecY = rf2accelInfo.Rf2Tele.mVehicles[0].mLocalAccel.y #should spit out the acceleration in Y direction from RF2
##            accelVecZ = rf2accelInfo.Rf2Tele.mVehicles[0].mLocalAccel.z #should spit out the acceleration in Z direction from RF2
##            print(accelVecX,accelVecY,accelVecZ)
##            




################## GUI SETUP #########################

#create GUI window
window = tk.Tk()
#title the window
window.title('Lafayette Motion Platform Control')
#set window size
window.geometry("1250x1250+100+50")

#create a frame to hold the serial port configuration
IMUportframe = tk.Frame(window,relief=tk.GROOVE,borderwidth=3)
IMUportframe.pack()

#create a label for the IMU config:

IMUportmsg = tk.Label(IMUportframe,text="IMU port: ")
IMUportmsg.pack(side=tk.LEFT)
#create a textbox for the port name
IMUportentry = tk.Entry(IMUportframe)
#insert a default port
IMUportentry.insert(0,"COM5")
IMUportentry.pack(side=tk.LEFT) 

IMUbut = tk.Button(IMUportframe, text = "Connect",command = startIMUThread)
IMUbut.pack(side=tk.RIGHT)


#create a frame to hold the serial port configuration
portframe = tk.Frame(window,relief=tk.GROOVE,borderwidth=3)
portframe.pack()
#create a label for port config:
portmsg = tk.Label(portframe,text="port: ")
portmsg.pack(side=tk.LEFT)
#create a textbox for the port name
portentry = tk.Entry(portframe)
#insert a default port
portentry.insert(0,"COM7")
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

#Live IMU Plotting stuff
app = IMUData(window)
ani = animation.FuncAnimation(app.fig, app.animate , interval=150, blit=False)

#IMU Radio Button stuff
v = StringVar(window,"1") #variable that keeps track of radio button for IMU data 
for (text,value) in PlottingOptions.items():
    Radiobutton(window,text=text,variable=v,value=value).pack(side = "left") #creating the radio button
#washout radio button stuff
w = StringVar(window,"1") #variable that keeps track of radio buttong for washout plotting
for (text,value) in WashPlottingOptions.items():
    Radiobutton(window,text=text, variable=w,value=value).pack(side="right")

f = tk.IntVar()
RFBut = tk.Checkbutton(window,text = 'RF2', variable = f, onvalue = 1, offvalue = 0).pack()
#run the TK mainloop to keep the window up and open.
window.mainloop()
