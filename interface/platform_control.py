import socket
import sys, select
import time
from numpy import *
from scipy.signal import *
from matplotlib.pyplot import *
import sys,traceback
import serial
from threading import Thread

import tkinter as tk

#create a global variable to hold the platform command
cmd = [0,0,0,0,0,0]
# command = [xdes_final,ydes_final,zdes_final,rdes_final,pdes_final,ades_final]

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
    cmd[2]=zslider.get()

############## CALLBACK FOR RUN BUTTON ##################

def startPlatformThread():
    platthread = Thread(target=doPlatform)
    platthread.start()



############## Function to communicate with Arduino ###########
def doPlatform():
    global cmd
    while 1:
        print(cmd)
        time.sleep(0.1)



################## GUI SETUP #########################

#create GUI window
window = tk.Tk()
#title the window
window.title('Lafayette Motion Platform Control')
#set window size
window.geometry("450x450+100+50")


#create a frame to hold the serial port configuration
portframe = tk.Frame(window,relief=tk.GROOVE,borderwidth=3)
portframe.pack()
#create a label for port config:
portmsg = tk.Label(portframe,text="port: ")
portmsg.pack(side=tk.LEFT)
#create a textbox for the port name
portentry = tk.Entry(portframe)
#insert a default port
portentry.insert(0,"/dev/ttyUSB100")
portentry.pack(side=tk.RIGHT)
# create a button to connect to platform
platbut = tk.Button(
    portframe,
    text="Connect",
    command=startPlatformThread)
platbut.pack(side=tk.RIGHT)
#create a status message in this frame to show serial port status
statemsg = tk.Label(window,text="Not Connected")
statemsg.pack()


#create a slider for roll
rollframe = tk.Frame(window,relief=tk.GROOVE,borderwidth=3)
rollframe.pack()
rolllabel = tk.Label(rollframe,text="Roll (rad)")
rolllabel.pack(side=tk.LEFT)
rollslider = tk.Scale(rollframe,orient=tk.HORIZONTAL,from_=-0.1,to=0.1,resolution=.001,command=rollcallback)
rollslider.pack(side=tk.RIGHT)

#create a slider for pitch
pitchframe = tk.Frame(window,relief=tk.GROOVE,borderwidth=3)
pitchframe.pack()
pitchlabel = tk.Label(pitchframe,text="pitch (rad)")
pitchlabel.pack(side=tk.LEFT)
pitchslider = tk.Scale(pitchframe,orient=tk.HORIZONTAL,from_=-0.1,to=0.1,resolution=.001,command=pitchcallback)
pitchslider.pack(side=tk.RIGHT)

#create a slider for yaw
yawframe = tk.Frame(window,relief=tk.GROOVE,borderwidth=3)
yawframe.pack()
yawlabel = tk.Label(yawframe,text="yaw (rad)")
yawlabel.pack(side=tk.LEFT)
yawslider = tk.Scale(yawframe,orient=tk.HORIZONTAL,from_=-0.1,to=0.1,resolution=.001,command=yawcallback)
yawslider.pack(side=tk.RIGHT)

#create a slider for x
xframe = tk.Frame(window,relief=tk.GROOVE,borderwidth=3)
xframe.pack()
xlabel = tk.Label(xframe,text="x (rad)")
xlabel.pack(side=tk.LEFT)
xslider = tk.Scale(xframe,orient=tk.HORIZONTAL,from_=-0.1,to=0.1,resolution=.001,command=xcallback)
xslider.pack(side=tk.RIGHT)

#create a slider for y
yframe = tk.Frame(window,relief=tk.GROOVE,borderwidth=3)
yframe.pack()
ylabel = tk.Label(yframe,text="y (rad)")
ylabel.pack(side=tk.LEFT)
yslider = tk.Scale(yframe,orient=tk.HORIZONTAL,from_=-0.1,to=0.1,resolution=.001,command=ycallback)
yslider.pack(side=tk.RIGHT)

#create a slider for z
zframe = tk.Frame(window,relief=tk.GROOVE,borderwidth=3)
zframe.pack()
zlabel = tk.Label(zframe,text="z (rad)")
zlabel.pack(side=tk.LEFT)
zslider = tk.Scale(zframe,orient=tk.HORIZONTAL,from_=-0.1,to=0.1,resolution=.001,command=zcallback)
zslider.pack(side=tk.RIGHT)






#run the TK mainloop to keep the window up and open.
window.mainloop()
