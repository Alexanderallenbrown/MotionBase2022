# Import the library
import serial

# Try to connect to the port
try:
    myPySerial = serial.Serial('COM5', 9600) #Using COM4 as serial port connection, replace with yours.
except:
    print('Failed to connect. Try running this command in the command line to see your available serial port conections:')
    print('python -m serial.tools.list_ports')
    print('(Note that this is not your command line, this is a the Python Interpreter)')
    exit()

# Read data and print it to terminal... until you stop the program
while 1:
#reads a line of serial data, it expets a line ending
    line = myPySerial.readline()
    print(line)

#Optional code, makes the serial data easier to work with

#Decode takes the string byte values and turns them into letters and numbers we can work with
#    line = line.decode()
#Find looks for a letter in a string and returns its position in the string. Returns -1 if none is found. 
#    letterPosition = line.find('R')          
#    if letterPosition > -1:
#        print('I found an R in your serial data')
#    else:
#        print('I did not find an R in your serial data')
