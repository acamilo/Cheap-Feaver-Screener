import usb.core
import usb.util as util
import struct
import pickle
from PIL import Image, ImageDraw
import time

class FlirOneR2:

    def __init__(self):
        self.dev = usb.core.find(idVendor=0x09cb, idProduct=0x1996)
        self.buffer=None
        self.packetCount = 0
        self.byteCount = 0
        self.FrameSize,self.ThermalSize,self.JpgSize,self.StatusSize = [0,0,0,0]
        self.thermal_data    = None
        self.jpeg_data       =None
        self.status_data     =None
        # was it found?
        if self.dev is None:
            raise ValueError('Device not found')
#        else:
#            print(self.dev)

        self.dev.set_configuration()
        #self.conf = self.dev.get_active_configuration()
        #self.intf = self.conf[(0,0)]

        #self.control_intf = self.conf[(0,0)]
        #self.control_endp_out = self.intf[1]

        #self.file_intf = self.conf[(1,0)]
        #self.control_endp_out = self.intf[3]

        #self.image_intf = self.conf[(2,0)]
        #self.control_endp_out = self.intf[5]

        # 01 0b 01 00 01 00 00 00 c4 d5
        # bmRequestType = 01
        #   0:4     1:  Interface
        #   5:6     0:  Standard
        #   7       0:  Host->Device
        # bRequest = 0b
        #   0b: SET_INTERFACE
        # wValue = 0001
        #   Interface: 1  (0:disable/1:enable)
        # wIndex = 01 (interface #)
        #
        data=bytes([0,0])
        time.sleep(0.1)
        print("STOP interface 2 FRAME..",end='')
        r = self.dev.ctrl_transfer(
                bmRequestType=1,
                bRequest=0x0B,
                wValue=0,
                wIndex=2,
                data_or_wLength=data,
                timeout=100)
        print(r)
        time.sleep(0.1)
        print("STOP interface 1 FILEIO",end='')
        r = self.dev.ctrl_transfer(
                bmRequestType=1,
                bRequest=0x0B,
                wValue=0,
                wIndex=1,
                data_or_wLength=data,
                timeout=100)
        print(r)
        time.sleep(0.1)
        print("START interface 1 FILEIO",end='')
        r = self.dev.ctrl_transfer(
                bmRequestType=1,
                bRequest=0x0B,
                wValue=1,
                wIndex=1,
                data_or_wLength=data,
                timeout=100)
        print(r)
        time.sleep(0.1)
        print("Ask for video stream START EP0x85",end='')
        r = self.dev.ctrl_transfer(
                bmRequestType=1,
                bRequest=0x0B,
                wValue=1,
                wIndex=2,
                data_or_wLength=data,
                timeout=200)

        print(r)
        time.sleep(0.5)

    def doUSB(self):
        # service the other two endpoints
        try:
            a=self.dev.read(0x81,1048576,100)
            a=self.dev.read(0x83,1048576,100)
        except usb.core.USBError:
            pass

        try:
            buf85 = self.dev.read(0x85,1048576,100)
            #print(len(buf85))
        except usb.core.USBError:
            print("Bulk Transfer Failed")
            return

        if len(buf85)==0:
            print("Zero length packet")
            return
        # If we see magic, it's a new frame.
        if buf85[0:4]==bytearray([239,190,0,0]):
            self.buffer=buf85
            self.byteCount=len(buf85)
            self.FrameSize,self.ThermalSize,self.JpgSize,self.StatusSize = struct.unpack("<LLLL",self.buffer[8:24])
            print("I saw the magic! (%s)"%(len(buf85)))
        else:
            #sometimes we get a first packet without start magic.
            if self.buffer==None:
                return
            self.buffer += buf85
            self.byteCount += len(buf85)
        # Are we done with a frame?
        print("%s\t%s"%(self.byteCount,self.FrameSize))
        if self.byteCount>=(28+self.FrameSize):
            print("Have Frame!")
            self.packetCount += 1
            self.thermal_data    = self.buffer[28:28+self.ThermalSize]
            self.jpeg_data       = self.buffer[28+self.ThermalSize:28+self.ThermalSize+self.JpgSize]
            self.status_data     = self.buffer[28+self.ThermalSize+self.JpgSize:28+self.ThermalSize+self.JpgSize+self.StatusSize]
            return True
        else:
            return False


    def getFrame(self):
        #run USB untill we have a frame.
        while(self.doUSB()==False):
            pass

        return

    def getThermal(self):
        # Create a python image from raw data
        thermal_data = self.thermal_data
        new = Image.new('I',(160, 120))
        if thermal_data:
            pixels = new.load()

            for y in range(0,120):
                for x in range(0,160):
                    if x<80:
                        v = thermal_data[2*(y*164+x)+4] + thermal_data[2*(y*164+x)+5]
                    else:
                        v = thermal_data[2*(y*164+x)+8] + thermal_data[2*(y*164+x)+9]
                    #print("%s,%s:\t%s"%(x,y,v))
                    pixels[x,y] = v
        else:
            print("Error, no data")
        return new

    def getImage():
        return self.jpeg_data

    def disconnect(self):
        data=bytes([0,0])
        print("STOP interface 2 FRAME..",end='')
        r = self.dev.ctrl_transfer(
                bmRequestType=1,
                bRequest=0x0B,
                wValue=0,
                wIndex=2,
                data_or_wLength=data,
                timeout=100)
        print(r)

        print("STOP interface 1 FILEIO",end='')
        r = self.dev.ctrl_transfer(
                bmRequestType=1,
                bRequest=0x0B,
                wValue=0,
                wIndex=1,
                data_or_wLength=data,
                timeout=100)
        print(r)
