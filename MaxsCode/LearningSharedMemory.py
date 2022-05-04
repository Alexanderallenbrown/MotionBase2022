from multiprocessing import shared_memory

testing_memory = shared_memory.SharedMemory(name = 'rideHeight')
myWeather = testing_memory.buf

print(myWeather)

  
