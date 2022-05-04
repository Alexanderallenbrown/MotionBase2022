import rF2data as RF2Data


info = RF2Data.SimInfo()

while True:
      accelVecX = info.Rf2Tele.mVehicles[0].mLocalAccel.x #should spit out the acceleration in X direction
      accelVecY = info.Rf2Tele.mVehicles[0].mLocalAccel.y #should spit out the acceleration in X direction
      accelVecZ = info.Rf2Tele.mVehicles[0].mLocalAccel.z #should spit out the acceleration in X direction
      #AccelFile.write(accelVecX)
      #print('Acce;: %d' % (accelVec))
      version = info.Rf2Ext.mVersion
      v = bytes(version).partition(b'\0')[0].decode().rstrip()
      clutch = info.Rf2Tele.mVehicles[0].mUnfilteredClutch # 1.0 clutch down, 0 clutch up
      gear   = info.Rf2Tele.mVehicles[0].mGear  # -1 to 6
      test = info.Rf2Tele.mVehicles[0].mEngineWaterTemp
      print(accelVecY)
