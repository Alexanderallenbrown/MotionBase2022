import socket
import sys, select
import time
from numpy import *
from scipy.signal import *
from matplotlib.pyplot import *
import sys,traceback
import serial
from threading import Thread
import copy

import Tkinter as tk

#create a global variable to hold the platform command
cmd = [0,0,0,0,0,0]
# command = [xdes_final,ydes_final,zdes_final,rdes_final,pdes_final,ades_final]
endSerialThread = False


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

############## CALLBACK FOR RUN BUTTON ##################

def startPlatformThread():
    global platthread,endSerialThread
    endSerialThread = False
    statemsg["text"] = "Connected"
    platthread = Thread(target=doPlatform)
    platthread.start()
    
def cleanupPlatformThread():
    global endSerialThread
    endSerialThread=True
    



############## Function to communicate with Arduino ###########
def doPlatform():
    global cmd,ser,endSerialThread
    #initialize old time
    arduino_delay = 0.1

    #connect to the serial port.
    #the portentry.get() call gets the port name
    #from the textbox.
    ser = serial.Serial(
    port=portentry.get(), #ACM100',   #USB0', 
    baudrate=115200,
    timeout = .1) 
    print("initializing")
    ser.close()
    time.sleep(2.0)
    ser.open()
    time.sleep(2.0)
    print("done") 
    
    starttime = time.time()
    lastsendtime = time.time()-starttime
    #this is an infinite loop  .
    while not endSerialThread:
        cmdlocal = copy.deepcopy(cmd)
        #get current time
        tnow = time.time()-starttime
        # print(tnow-lastsendtime)
        if tnow-lastsendtime>arduino_delay:     ### also happens super fast
            #print 'sent'
            print("at t = "+format(tnow,'0.2f')+", sent: "+format(cmdlocal[0],'0.2f')+","+format(cmdlocal[1],'0.2f')+","+format(cmdlocal[2],'0.2f')+","+format(cmdlocal[3],'0.4f')+","+format(cmdlocal[4],'0.4f')+","+format(cmdlocal[5],'0.4f'))
            lastsendtime = tnow
            ser.write('!')
            for ind in range(0,len(cmdlocal)-1):
              ser.write(format(cmdlocal[ind],'0.3f'))
              ser.write(',')
            ser.write(str(cmdlocal[-1]))
            ser.write('\n')
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




################## GUI SETUP #########################

#create GUI window
window = tk.Tk()
#title the window
window.title('Lafayette Motion Platform Control')
#set window size
window.geometry("750x750+100+50")


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
yawslider = tk.Scale(yawframe,orient=tk.HORIZONTAL,from_=-0.1,to=0.1,resolution=.001,command=yawcallback,length=400)
yawslider.pack(side=tk.RIGHT)

#create a slider for x
xframe = tk.Frame(window,relief=tk.GROOVE,borderwidth=3)
xframe.pack()
xlabel = tk.Label(xframe,text="x (rad)")
xlabel.pack(side=tk.LEFT)
xslider = tk.Scale(xframe,orient=tk.HORIZONTAL,from_=-2,to=2,resolution=.1,command=xcallback,length=400)
xslider.pack(side=tk.RIGHT)

#create a slider for y
yframe = tk.Frame(window,relief=tk.GROOVE,borderwidth=3)
yframe.pack()
ylabel = tk.Label(yframe,text="y (rad)")
ylabel.pack(side=tk.LEFT)
yslider = tk.Scale(yframe,orient=tk.HORIZONTAL,from_=-2,to=2,resolution=.1,command=ycallback,length=400)
yslider.pack(side=tk.RIGHT)

#create a slider for z
zframe = tk.Frame(window,relief=tk.GROOVE,borderwidth=3)
zframe.pack()
zlabel = tk.Label(zframe,text="z (rad)")
zlabel.pack(side=tk.LEFT)
zslider = tk.Scale(zframe,orient=tk.HORIZONTAL,from_=-2,to=2,resolution=.1,command=zcallback,length=400)
zslider.pack(side=tk.RIGHT)

#create a status message in this frame to show serial port status
echomsg = tk.Label(window,text="No Data Received")
echomsg.pack()




#run the TK mainloop to keep the window up and open.
window.mainloop()
