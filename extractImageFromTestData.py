import pickle
import struct
from PIL import Image, ImageDraw
import ST7789 as ST7789
import sys

disp = ST7789.ST7789(
    port=0,
    cs=ST7789.BG_SPI_CS_FRONT,  # BG_SPI_CSB_BACK or BG_SPI_CS_FRONT
    dc=9,
    backlight=19,               # 18 for back BG slot, 19 for front BG slot.
    spi_speed_hz=80 * 1000 * 1000
)


WIDTH = disp.width
HEIGHT = disp.height
# offsets
#    8:11:  FrameSize
#   12:15:  ThermalSize
#   16:19:  JpgSize
#   20:23:  StatusSize
#   last 3 should add up to FrameSize

# load capture
frames = pickle.load(open(sys.argv[1],"rb"))

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

# Create a python image from raw data
new = Image.new('I',(160, 120))
pixels = new.load()

for y in range(0,120):
    for x in range(0,160):
        if x<80:
            v = thermal_data[2*(y*164+x)+4] + thermal_data[2*(y*164+x)+5]
        else:
            v = thermal_data[2*(y*164+x)+8] + thermal_data[2*(y*164+x)+9]
        #print("%s,%s:\t%s"%(x,y,v))
        pixels[x,y] = v

#convert the image into a displayable form
rgbimg = Image.new("RGBA", new.size)
rgbimg.paste(new)
scr = rgbimg.resize((240,240))
disp.display(scr)
