#!/usr/bin/env python
import time
from numpy import *
from scipy.signal import *
from matplotlib.pyplot import *

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
    self.updateFilterCoefficients(dt)

    #prepare vectors of "past" values for filters to use
    # we have a max of a 4th order TF, so we will include 4 "lagged" values
    self.xvec = [0,0,0,0,0] #x position (m) comes from HIGH PASS scoot filter
    self.yvec = [0,0,0,0,0] #y position (m) comes from HIGH PASS scoot filter
    self.zvec = [0,0,0,0,0] #z position (m) comes from HIGH PASS scoot filter
    self.axvec = [0,0,0,0,0] #x acceleration (m/s/s)
    self.ayvec = [0,0,0,0,0] #y acceleration (m/s/s)
    self.azvec = [0,0,0,0,0] #z acceleration (m/s/s)
    self.avec = [0,0,0,0,0] #yaw ANGLE (rad) comes from high pass "scoot" filter
    self.axrawvec = [0,0,0,0,0] #raw (input) x acceleration (m/s/s)
    self.ayrawvec = [0,0,0,0,0] #raw (input) y acceleration (m/s/s)
    self.azrawvec = [0,0,0,0,0] #raw (input) z acceleration (m/s/s)
    self.wzrawvec = [0,0,0,0,0] #raw (input) yaw rate (rad/s)
    self.g = 9.81

  def updateFilterCoefficients(self,dt):
    #Washout filter definitions (could read from a file or make adjustable...)
    
    #filter 1: high pass that produces a y command from y acceleration ("scoot" filter)
    # G(s) =                      s
  #           ----------------------------------
  #           s^3 + 2.333 s^2 + 1.667 s + 0.3333

    (self.numyhp,self.denyhp,self.dtyhp) = cont2discrete(([1.,0],[1.,5.,8.,4.]),self.dt,method='zoh') #numerator and denominator coefficients

    print(self.numyhp,self.denyhp,self.dtyhp)
    #filter 2: low pass that produces a roll angle to simulate sustained acceleration in y
    #ay to roll
    (self.numylp,self.denylp,self.dtylp) = cont2discrete(([100.],[1.,20.,100.]),self.dt,method='zoh')

    #filter 3: high pass that produces a x command from x acceleration ("scoot" filter)
    # G(s) = 10s^2/(s^2+10s+20)
    (self.numxhp,self.denxhp,self.dtxhp) = cont2discrete(([1.,0],[1.,5.,8.,4.]),self.dt,method='zoh') #numerator and denominator coefficients

    #filter 4: low pass that produces a pitch angle to simulate sustained acceleration in x
    #ax to pitch
    (self.numxlp,self.denxlp,self.dtxlp) = cont2discrete(([100.],[1.,20.,100.]),self.dt,method='zoh')


    #filter 5: high pass filter producing a z command from z acceleration (scoot)
    #az to z_desired
    (self.numzhp,self.denzhp,self.dtzhp) = cont2discrete(([1.,0],[1.,5.,8.,4.]),self.dt,method='zoh')

    #filter 6: high pass filter producing a anglez to anglez_filtered
    # instead of "y" for yaw we will use "a" for "azimuth"
    (self.numahp,self.denahp,self.dtahp) = cont2discrete(([1.,0],[1.,5.,8.,4.]),self.dt,method='zoh')

    #filter 7: High pass filter producing an x acceleration, without the leak, created random zeta and omega_n for testing
    (self.numAccYhp,self.denAccYhp,self.dtAccYhp) = cont2discrete (([1.,0,0],[1,(2*.7*1**2),(1**2)]),self.dt,method='zoh')



    ## need to add in another TF here that is s^2/s^2 * 2 zeta omega s * omega^2

  #this function gets called over and over in the loop. It takes in accelerations and yaw rate
  #it produces and updated guess for the simulated accelerations and yaw rates.
  def doWashout(self,ax_raw,ay_raw,az_raw,wz_raw):
    # MAKE SURE THESE INPUT ANGLES ARE IN G for accelerations and rad/s for yaw rate!!

    #first we need to scale the signals down.
    ax_raw = ax_raw*self.axscale
    ay_raw = ay_raw*self.ayscale
    az_raw = az_raw*self.azscale
    wz_raw = wz_raw*self.wzscale


    #now we actually apply the filters. the "raw" accel is the input to each TF
    #the vectors ax,ay, etc. are the "output."
    #y_desired[3]=-den1[1]*y_desired[2]-den1[2]*y_desired[1]+num1[1]*ay_raw_small[2]+num1[2]*ay_raw_small[1]
    
    # all high pass filters below
    # print(self.numyhp)
    xfilt = 1./self.denxhp[0]*(-self.denxhp[1]*self.xvec[-1] - self.denxhp[2]*self.xvec[-2] - self.denxhp[3]*self.xvec[-3] + (ax_raw*self.numxhp[0][0] + self.axrawvec[-1]*self.numxhp[0][1] + self.axrawvec[-2]*self.numxhp[0][2]+ self.axrawvec[-3]*self.numxhp[0][3]))
    yfilt = 1./self.denyhp[0]*(-self.denyhp[1]*self.yvec[-1] - self.denyhp[2]*self.yvec[-2] - self.denyhp[3]*self.yvec[-3] + (ax_raw*self.numyhp[0][0] + self.ayrawvec[-1]*self.numyhp[0][1] + self.ayrawvec[-2]*self.numyhp[0][2]+ self.ayrawvec[-3]*self.numyhp[0][3]))
    zfilt = 1./self.denzhp[0]*(-self.denzhp[1]*self.zvec[-1] - self.denzhp[2]*self.zvec[-2] - self.denzhp[3]*self.zvec[-3] + (ay_raw*self.numzhp[0][0] + self.azrawvec[-1]*self.numzhp[0][1] + self.azrawvec[-2]*self.numzhp[0][2]+ self.azrawvec[-3]*self.numzhp[0][3]))
    afilt = 1./self.denahp[0]*(-self.denahp[1]*self.avec[-1] - self.denahp[2]*self.avec[-2] - self.denahp[3]*self.avec[-3] + (wz_raw*self.numahp[0][0] + self.wzrawvec[-1]*self.numahp[0][1] + self.wzrawvec[-2]*self.numahp[0][2]+ self.wzrawvec[-3]*self.numahp[0][3]))

    #all low pass filters below: Need to finish adding in the rest of these
    axfilt = 1./self.denxlp[0]*(-self.denxlp[1]*self.axvec[-1] - self.denxlp[2]*self.axvec[-2] + (ax_raw*self.numxlp[0][0] + self.axrawvec[-1]*self.numxlp[0][-1]))
    ayfilt = 1./self.denylp[0]*(-self.denylp[1]*self.ayvec[-1] - self.denylp[2]*self.ayvec[-2] + (ay_raw*self.numylp[0][0] + self.ayrawvec[-1]*self.numylp[0][-1]))

    #High pass filters that produce the accelerations 
    #accelX
    accelYfilt = 1./self.denAccYhp[0]*(-self.denAccYhp[1]*self.yvec[-1] - self.denAccYhp[2]*self.yvec[-2]  + (ay_raw*self.numAccYhp[0][0] + self.ayrawvec[-1]*self.numAccYhp[0][1] + self.ayrawvec[-2]*self.numAccYhp[0][2]))
    #now we can compute the tilt angles in RADIANS.
    #positive roll is to driver's right side, so to feel like accelerating in positive y (drive left), need to take neg
    roll = arcsin(ayfilt)
    #positive pitch is down towards driver feet, so to feel like accelerating in positive x, need to take neg
    pitch = arcsin(axfilt)

    #now we have to update our "buffers" of past acceleration and position values
    #pop(0) removes the first element in the array. append() adds a new value to the end.
    #the next lines remove the "oldest" value in each vector and replace the last element with the newest.
    self.xvec.pop(0);self.xvec.append(xfilt)
    self.yvec.pop(0);self.yvec.append(yfilt)
    self.zvec.pop(0);self.zvec.append(zfilt)
    self.axvec.pop(0);self.axvec.append(axfilt)
    self.ayvec.pop(0);self.ayvec.append(ayfilt)
    self.avec.pop(0);self.avec.append(afilt)

    #now we put raw input values in their "lagged" arrays so we can use "old" values in the filter as required.
    #pop(0) removes the first element in the array. append() adds a new value to the end.
    #the next 3 lines remove the "oldest" value of acceleration and replace the last element with the newest.
    self.axrawvec.pop(0);self.axrawvec.append(ax_raw)
    self.ayrawvec.pop(0);self.ayrawvec.append(ay_raw)
    self.azrawvec.pop(0);self.azrawvec.append(az_raw)
    self.wzrawvec.pop(0);self.wzrawvec.append(wz_raw)

    print(accelYfilt)

    #now return the commands to the platform. each call to this function returns the scalar value that's relevant NOW
    return xfilt,yfilt,zfilt,roll,pitch,afilt,accelYfilt


####### this bottom "if" only runs if you run this file as a script, like $python washout.py
#it acts as a "demo" for the library.
if __name__ == "__main__" :

  #this demo simulates platform motion for a step in acceleration and yaw rate
  g = 9.81#m/s/s, gravitational constant
  vehicle_speed = 20.0 #m/s, forward speed
  vehicle_accel = 9.81 #m/s/s, lateral acceleration
  #use max acceleration and fwd speed to get a turn radius
  #U^2/R = ay soo.... U^2/ay = R
  turn_radius = vehicle_speed**2/vehicle_accel
  #yaw rate can then be computed as U/R (just geometry...)
  yawrate = vehicle_speed/turn_radius

  #now create fake raw inputs for each of the vehicle's IMU readings that are read by washout:
  #decide what timestep we'll run at (when running in "real time" this will depend on your threads and time.sleep())
  dt = 0.01
  #set up an array of time values to loop through
  tsim = arange(0,4,dt)

  #set up vectors for each variable
  ax = zeros(size(tsim))
  ay = ones(size(tsim))*vehicle_accel #at t=0, vehicle enters turn "perfectly" (no dynamics)
  az = zeros(size(tsim))
  wz = ones(size(tsim))*yawrate #at t=0, vehicle enters turn "perfectly" (no dynamics)

  #now create the washout object
  wash = Washout(dt)#be sure to specify the CORRECT dt to the best of your ability!

  #create a matrix to hold our platform commands x,y,z,roll,pitch,yaw
  cmdvec = zeros((len(tsim),7))#each row will represent commands at a particular timestep

  #now set up a for-loop to simulate this happening.
  #in "live" setting, this is a "while 1" infinite loop, and you're just calling the washout each time.
  for k in range(0,len(tsim)):
    #IRL you'd measure ax,ay,az,wz from a simulation, then to this to get commands.
    #we are pulling commands out of a vector because we've pre-stored them... but you would just use like ax/g...
    x,y,z,roll,pitch,yaw,yAccel = wash.doWashout(ax[k]/g,ay[k]/g,az[k]/g,wz[k])
    #now for plotting, store everything in our array of commands
    cmdvec[k,:] = array([x,y,z,roll,pitch,yaw,yAccel])

  #now we've gotten our results, so let's plot
  figure(figsize=(18, 6), dpi=80)
  subplot(141)
  plot(tsim,cmdvec[:,1],'k')
  xlabel('Time (s)')
  ylabel('y position (m)')
  grid('on')
  subplot(142)
  plot(tsim,cmdvec[:,3]*180/pi*2,'k')
  xlabel('Time (s)')
  ylabel('roll angle (deg)')
  grid('on')
  subplot(143)
  plot(tsim,cmdvec[:,5],'k')
  grid('on')
  xlabel('Time (s)')
  ylabel('yaw angle (rad)')
  subplot(144)
  plot(tsim,cmdvec[:,6])
  grid ('on')
  xlabel('Time (s)')
  ylabel('Y Acceleration')

  axis('tight')

  show()

    