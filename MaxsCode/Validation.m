clc; close all; clear all; 

%bring in data from Python created txt files
IMUdata = readtable('IMUFileValidationFullSize.txt');
washData = readtable('washFileValidationFullSize.txt');

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

%need to match units of accel, IMU reads in m/s^s and the washout is in G's
xAccel = xAccel * 0.101971621;
yAccel = yAccel * 0.101971621;
zAccel = zAccel * 0.101971621;

%now just need to plot everything

%x accel validation
figure(1)
plot(timeArduino(1:1000),(-xAccel(1:1000)+mean(xAccel(1:20))))
hold on
plot(timeArduino(1:1000),washX(1:1000))
xlabel('Time, s')
ylabel('X acceleration')
title ('X Acceleration Validation Plot')
legend('IMU Plot','Washout Plot')

figure(2)
plot(timeArduino(1:500),(-yAccel(1:500)+mean(yAccel(1:20))))
hold on
plot(timeArduino(1:1000),washY(1:1000))
xlabel('Time, s')
ylabel('Y acceleration')
title ('Y Acceleration Validation Plot')
legend('IMU Plot','Washout Plot')

figure(3)
plot(timeArduino(1:500),zAccel(1:500))
hold on
plot(timeArduino(1:500),washZ(1:500)+.981)
xlabel('Time, s')
ylabel('Z acceleration')
title ('Z Acceleration Validation Plot')
legend('IMU Plot','Washout Plot')

