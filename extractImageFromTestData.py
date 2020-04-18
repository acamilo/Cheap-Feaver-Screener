import pickle
import struct


# offsets
#    8:11:  FrameSize
#   12:15:  ThermalSize
#   16:19:  JpgSize
#   20:23:  StatusSize
#   last 3 should add up to FrameSize

# load capture
frames = pickle.load(open("packets/packet-0.p","rb"))

# reassemble
buffer=frames

sizeData = buffer[8:24]
FrameSize,ThermalSize,JpgSize,StatusSize = struct.unpack("<LLLL",sizeData)

print("%s"%(buffer[0:4]))
print("Buffer Length:\t%s"%(len(buffer)))

print("Frame Size:\t%s (%s)"%(FrameSize,str(ThermalSize+JpgSize+StatusSize)))
print("Thermal Size:\t%s"%(ThermalSize))
print("Jpg Size:\t%s"%(JpgSize))
print("Status Size:\t%s"%(StatusSize))

thermal_data    = buffer[28:28+ThermalSize]
jpeg_data       = buffer[28+ThermalSize:28+ThermalSize+JpgSize]
status_data     = buffer[28+ThermalSize+JpgSize:28+ThermalSize+JpgSize+StatusSize]
