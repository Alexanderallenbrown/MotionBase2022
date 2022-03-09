clc; close all; clear all; 

%bring in data from Python created txt files
IMUdata = readtable('IMUFile.txt');
washData = readtable('washFile.txt');

%organize IMU data from python
xAccel = table2array(IMUdata(:,1));
yAccel = table2array(IMUdata(:,2));
zAccel = table2array(IMUdata(:,3));

xGyro = table2array(IMUdata(:,4));
yGyro = table2array(IMUdata(:,5));
zGyro = table2array(IMUdata(:,6));

timeArduino = table2array(IMUdata(:,7));

%organize washoutData from Python
washX = table2array(washData(:,1));
washY = table2array(washData(:,2));
washZ = table2array(washData(:,3));


%need to trim data
trimAmount = size(timeArduino) - size(washX);

xAccel = xAccel(trimAmount(1)+1:end);
yAccel = yAccel(trimAmount(1)+1:end);
zAccel = zAccel(trimAmount(1)+1:end);
xGyro = xGyro(trimAmount(1)+1:end);
yGyro = yGyro(trimAmount(1)+1:end);
zGyro = zGyro(trimAmount(1)+1:end);
timeArduino = timeArduino(trimAmount(1)+1:end);

%now just need to plot everything

%x accel validation
figure(1)
plot(timeArduino,xAccel)
hold on
plot(timeArduino,washX)
xlabel('Time, s')
ylabel('X acceleration')
title ('X Acceleration Validation Plot')

figure(2)
plot(timeArduino,yAccel)
hold on
plot(timeArduino,washY)
xlabel('Time, s')
ylabel('X acceleration')
title ('X Acceleration Validation Plot')

figure(3)
plot(timeArduino,zAccel)
hold on
plot(timeArduino,washZ)
xlabel('Time, s')
ylabel('X acceleration')
title ('X Acceleration Validation Plot')

