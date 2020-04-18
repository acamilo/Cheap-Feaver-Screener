import usb.core
import usb.util as util
import struct
import pickle

class FlirOne:

    def __init__(self):
        self.dev = usb.core.find(idVendor=0x09cb, idProduct=0x1996)
        self.buffer=None
        self.packetCount = 0
        self.byteCount = 0
        self.FrameSize,self.ThermalSize,self.JpgSize,self.StatusSize = [0,0,0,0]
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
        #print("STOP interface 2 FRAME")
        r = self.dev.ctrl_transfer(
                bmRequestType=1,
                bRequest=0x0B,
                wValue=0,
                wIndex=2,
                data_or_wLength=data,
                timeout=100)
        #print(r)

        #print("STOP interface 1 FILEIO")
        r = self.dev.ctrl_transfer(
                bmRequestType=1,
                bRequest=0x0B,
                wValue=0,
                wIndex=1,
                data_or_wLength=data,
                timeout=100)
        #print(r)

        #print("START interface 1 FILEIO")
        r = self.dev.ctrl_transfer(
                bmRequestType=1,
                bRequest=0x0B,
                wValue=1,
                wIndex=1,
                data_or_wLength=data,
                timeout=100)
        #print(r)

        #print("Ask for video stream START EP0x85")
        r = self.dev.ctrl_transfer(
                bmRequestType=1,
                bRequest=0x0B,
                wValue=1,
                wIndex=2,
                data_or_wLength=data,
                timeout=200)

        #print(r)

    def doUSB(self):
        # service the other two endpoints
        try:
            a=self.dev.read(0x81,1048576,100)
            a=self.dev.read(0x83,1048576,100)
        except usb.core.USBError:
            pass

        try:
            buf85 = self.dev.read(0x85,1048576,100)
        except usb.core.USBError:
            print("Bulk Transfer Failed")
            pass
        # If we see magic, it's a new frame.
        if buf85[0:4]==bytearray([239,190,0,0]):
            self.buffer=buf85
            self.byteCount=len(buf85)
            self.FrameSize,self.ThermalSize,self.JpgSize,self.StatusSize = struct.unpack("<LLLL",self.buffer[8:24])
            #print("I saw the magic! (%s)"%(len(buf85)))
        else:
            #sometimes we get a first packet without start magic.
            if self.buffer==None:
                return
            self.buffer += buf85
            self.byteCount += len(buf85)
        # Are we done with a frame?
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

    def getThermal():
        return self.thermal_data

    def getImage():
        return self.jpeg_data

    def disconnect(Self):
        pass

flir = FlirOne();
for i in range(0,30):
    flir.getFrame()

flir.disconnect()
exit()
#i = flir.getImage()
