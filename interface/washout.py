#!/usr/bin/env python
import time
from numpy import *
from scipy.signal import *
from matplotlib.pyplot import *
import sys,traceback

class Washout:
  def __init__(self,dt):
    #scale factors for simulating accelerations.
    #these prevent the platform from trying to simulate 1G (90 degrees of roll or pitch)
    self.ayscale = 0.25
    self.axscale = 0.25
    self.azscale = 0.25
    #scale factors for simulating angular velocities
    self.wzscale = 1.0
    self.dt = dt #this should be your guess for how fast the algorithm will run.
    #the speed of the loop will have a huge effect on how accurate this is,
    #so make sure you tune the thread that operates this filter to have this dt.
    
    #call the function to do the filter definitions.
    #may want to update this function to make filters not hard-coded...
    #possibly pass them in as options
    self.updateFilters(dt)

    #prepare vectors of "past" values for filters to use
    # we have a max of a 4th order TF, so we will include 4 "lagged" values
    self.axvec = [0,0,0,0,0] #x acceleration (m/s/s)
    self.ayvec = [0,0,0,0,0] #y acceleration (m/s/s)
    self.azvec = [0,0,0,0,0] #z acceleration (m/s/s)
    self.wzvec = [0,0,0,0,0] #yaw rate (rad/s)
    self.g = 9.81

  def updateFilters(self,dt):
    #Washout filter definitions (could read from a file or make adjustable...)
    
    #filter 1: high pass that produces a y command from y acceleration ("scoot" filter)
    # G(s) = 10s^2/(s^2+10s+20)
    (self.numyhp,self.denyhp,self.dtyhp) = cont2discrete(([10,0],[1,10,20]),self.dt) #numerator and denominator coefficients

    #filter 2: low pass that produces a roll angle to simulate sustained acceleration in y
    #ay to roll
    (self.numylp,self.denylp,self.dtylp) = cont2discrete(([-32500.],[1.,100.,1300.]),self.dt)

    #filter 3: high pass that produces a x command from x acceleration ("scoot" filter)
    # G(s) = 10s^2/(s^2+10s+20)
    (self.numxhp,self.denxhp,self.dtxhp) = cont2discrete(([10,0],[1,10,20]),self.dt) #numerator and denominator coefficients

    #filter 4: low pass that produces a pitch angle to simulate sustained acceleration in x
    #ax to pitch
    (self.numxlp,self.denxlp,self.dtxlp) = cont2discrete(([-32500.],[1.,100.,1300.]),self.dt)


    #filter 5: high pass filter producing a z command from z acceleration (scoot)
    #az to z_desired
    (self.numzhp,self.denzhp,self.dtzhp) = cont2discrete(([10.,0],[1.,11.,110.,100.]),dt[-1])

    #filter 6: high pass filter producing a anglez to anglez_filtered
    # instead of "y" for yaw we will use "a" for "azimuth"
    (self.numahp,self.denahp,self.dtahp) = cont2discrete(([1,0,0],[1.,2.,4.]),dt[-1])


  #this function gets called over and over in the loop. It takes in accelerations and yaw rate
  #it produces and updated guess for the simulated accelerations and yaw rates.
  def doWashout(self,ax_raw,ay_raw,az_raw,wz_raw):
    #first we need to scale the signals down.
    ax_raw = ax_raw*self.axscale
    ay_raw = ay_raw*self.ayscale
    az_raw = az_raw*self.azscale
    wz_raw = wz*self.wzscale

    #now we actually apply the filters. the "raw" accel is the input to each TF
    #the vectors ax,ay, etc. are the "output."

    #now we have to update our "buffers" of past acceleration values
    #pop(0) removes the first element in the array. append() adds a new value to the end.
    #the next 3 lines remove the "oldest" value of acceleration and replace the last element with the newest.
    self.ax.pop(0);self.ax.append(axfilt)
    self.ay.pop(0);self.ay.append(ayfilt)
    self.az.pop(0);self.az.append(azfilt)
    self.wz.pop(0);self.wz.append(wzfilt)

    




###### Implements Washout Filters (design these using MATLAB)
def doWashout(ax_raw,ay_raw,az_raw,wx_raw,wy_raw,wz_raw,dt):

  global platform_port, t, ax_raw, ay_raw, az_raw, anglex_raw, angley_raw, anglez_raw, buffsize, anglezraw#, dt

  # initialize position variables
  N = 4
  x_desired = zeros(N)
  y_desired = zeros(N)
  z_desired = zeros(N)
  ax_tilt = zeros(N)
  ay_tilt = zeros(N)
  ax_raw_small = zeros(N)
  ay_raw_small = zeros(N)
  az_raw_small = zeros(N)
  anglex_raw_small = zeros(N)
  angley_raw_small = zeros(N)
  anglez_raw_small = zeros(N)
  anglex = 0
  angley = 0
  anglex_filtered=zeros(N)
  angley_filtered=zeros(N)
  anglez_filtered=zeros(N)
  anglez=zeros(N)
  ax_tiltLP=0
  ay_tiltLP=0
  index=0 
  command = [0,0,0,0,0,0]

  # initialize time variables
  starttime = time.time()
  oldtime = time.time()
  time.sleep(.01)
  # dt = 0.005
  lastsendtime = time.time()
  arduino_delay = 0.01
  lastfilttime = time.time()
  filter_delay = 0.05

  platform_port = startSerial()
   
  print len(t)
  while 1:        ## >>> 500 Hz
    
    tnow = time.time()  # what time is it mr. fox??
    #print tnow
    #print len(t)
    if len(t)>=buffsize:
      # timetime = time.time()
      # take most recent value read from buffer
      # trecent = time.time()
      ax_raw_small = append(ax_raw_small[1:],ax_raw[-1])
      ay_raw_small = append(ay_raw_small[1:],ax_raw[-1])
      az_raw_small = append(az_raw_small[1:],ax_raw[-1])
      anglex_raw_small = append(anglex_raw_small[1:],anglex_raw[-1])
      angley_raw_small = append(angley_raw_small[1:],angley_raw[-1])
      anglez_raw_small = append(anglez_raw_small[1:],anglez_raw[-1])
      
      # tapp = tnow-trecent
      # print tapp
      #print tnow-lastfilttime
      if (tnow-lastfilttime)>filter_delay:              ## filters run at ~500 Hz
        
        # tstartfilt = time.time()
        #determine time step
        # print dt[-1]
        dt = array([tnow-lastfilttime])
        #print dt
        lastfilttime = tnow #have to reset this!! otherwise we don't keep track of this properly.
        
        # oldtime = tnow

        scaledown_roll = 0.0 #or .6
        scaledown_pitch = 2.0

        #ay to y_desired, and ax to x_desired
        (num1,den1,dt1) = cont2discrete(([10,0],[1,10,20]),dt[-1])

        #ay to ax_tilt
        (num2,den2,dt2) = cont2discrete(([-32500.*scaledown_roll],[1.,100.,1300.]),dt[-1])

        #copy of that for x only
        (num2a,den2a,dt2) = cont2discrete(([-32500.*scaledown_pitch],[1.,100.,1300.]),dt[-1])
  
        #anglex to anglex_filtered
        (num3,den3,dt3) = cont2discrete(([1,0],[1.,2.,4.]),dt[-1])

        #az to z_desired
        (num4,den4,dt4) = cont2discrete(([10.,0],[1.,11.,110.,100.]),dt[-1])

        #anglez to anglez_filtered
        (num5,den5,dt5) = cont2discrete(([1,0,0],[1.,2.,4.]),dt[-1])

        num1,num2,num2a,num3,num4,num5 = num1[0],num2[0],num2a[0],num3[0],num4[0],num5[0]

        x_desired = append(x_desired[1:],0)
        y_desired = append(y_desired[1:],0)
        z_desired = append(z_desired[1:],0)+2.0#####TODO!!!! THIS IS A TEMP

        anglez_filtered = append(anglez_filtered[1:],0)

        # timeendfilt = time.time()
        # filtTime=timeendfilt-tstartfilt
        # print filtTime
        # timetime = time.time()
        #final values: x_desired, y_desired, z_desired, anglex, angley, anglez
        if index>1:             ## happens way fast
          y_desired[3]=-den1[1]*y_desired[2]-den1[2]*y_desired[1]+num1[1]*ay_raw_small[2]+num1[2]*ay_raw_small[1]
          x_desired[3]=-den1[1]*x_desired[2]-den1[2]*x_desired[1]+num1[1]*ax_raw_small[2]+num1[2]*ax_raw_small[1]
          ax_tilt[3]=-den2a[1]*ax_tilt[2]-den2a[2]*ax_tilt[1]+num2a[1]*ay_raw_small[2]+num2a[2]*ay_raw_small[1]
          if abs(ax_tilt[3])>1.0:
            ax_tilt[3] = sign(ax_tilt[3])
          ax_tiltLP=math.asin(ax_tilt[3])
          ay_tilt[3]=-den2[1]*ay_tilt[2]-den2[2]*ay_tilt[1]+num2[1]*ax_raw_small[2]+num2[2]*ax_raw_small[1]
          if abs(ay_tilt[3])>1.0:
            ay_tilt[3] = sign(ax_tilt[3])
          ay_tiltLP=math.asin(-ay_tilt[3])

          anglex_filtered[3]=-den3[1]*anglex_filtered[2]-den3[2]*anglex_filtered[1]+num3[1]*anglex_raw_small[2]+num3[2]*anglex_raw_small[1]
          angley_filtered[3]=-den3[1]*angley_filtered[2]-den3[2]*angley_filtered[1]+num3[1]*angley_raw_small[2]+num3[2]*angley_raw_small[1]
          anglex=ax_tiltLP+anglex_filtered[3]
          angley=ay_tiltLP+angley_filtered[3]

          z_desired[3]=-den4[1]*z_desired[2]-den4[2]*z_desired[1]-den4[3]*z_desired[0]+num4[1]*az_raw_small[2]+num4[2]*az_raw_small[1]+num4[3]*az_raw_small[0]
          anglez_filtered[3]=-den5[1]*anglez_filtered[2]-den5[2]*anglez_filtered[1]+num5[0]*anglezraw+num5[1]*anglez_raw_small[2]+num5[2]*anglez_raw_small[1]
        else:
          y_desired[3]=0
          x_desired[3]=0
          z_desired[3]=0
          ay_tilt[3]=0 
          ax_tilt[3]=0 
          anglex=0
          angley=0
          anglex_filtered[3]=0
          angley_filtered[3]=0
          anglez_filtered[3]=anglezraw
        #how many times have we tried to filteR?
        index=index+1
        #what is our command?

        ##original
        #command = [x_desired[-1],y_desired[-1],z_desired[-1],ax_tiltLP,ay_tiltLP,anglez_filtered[-1]]

        ##attempt
        
        #set a soft limit for the angle commands...
        angle_softlim = 0.1

        xdes_final = 0#x_desired[-1]/100.0
        ydes_final = 0#y_desired[-1]/100.0
        zdes_final = 0#z_desired[-1]/100.0
        rdes_final = ax_tiltLP
        if abs(rdes_final)>angle_softlim:
          rdes_final = sign(rdes_final)*angle_softlim
        pdes_final = ay_tiltLP
        if abs(pdes_final)>angle_softlim:
          pdes_final = sign(pdes_final)*angle_softlim
        ades_final = anglez_filtered[-1]
        if abs(ades_final)>angle_softlim:
          ades_final = sign(ades_final)*angle_softlim
        #rdes_final = 0
        ades_final = 0 #TODO RELEASE THIS CONSTRAINT WHEN COMFORTABLE.
        command = [xdes_final,ydes_final,zdes_final,rdes_final,pdes_final,ades_final]

        #this worked before, but we just did some stuff above.
        #command = [x_desired[-1]/100.0,y_desired[-1]/100.0,(z_desired[-1]/100.0)+.5,ax_tiltLP,ay_tiltLP,anglez_filtered[-1]]

        # commandtime = time.time()
        # tcomm = commandtime - timetime
        # print tcomm
      #print "not frozen"
      if tnow-lastsendtime>arduino_delay:     ### also happens super fast
        #print 'sent'
        #print "sent: "+format(command[0],'0.2f')+","+format(command[1],'0.2f')+","+format(command[2],'0.2f')+","+format(command[3],'0.4f')+","+format(command[4],'0.4f')+","+format(command[5],'0.4f')
        lastsendtime = tnow
        ser.write('!')
        for ind in range(0,len(command)-1):
          ser.write(format(command[ind],'0.2f'))
          ser.write(',')
        ser.write(str(command[-1]))
        ser.write('\n')
        #line = ser.readline()
        #print "recieved: "+line
    else:
      time.sleep(.1)
        
        # lasttime=time.time()
        # endend=lasttime-timetime
        # print endend





####### execute the thread
if __name__ == "__main__" :

    