from flironerev2 import FlirOneR2
import sys
import ST7789 as ST7789
from PIL import Image, ImageDraw, ImageFont
# Create ST7789 LCD display class.
disp = ST7789.ST7789(
    port=0,
    cs=ST7789.BG_SPI_CS_FRONT,  # BG_SPI_CSB_BACK or BG_SPI_CS_FRONT
    dc=9,
    backlight=19,               # 18 for back BG slot, 19 for front BG slot.
    spi_speed_hz=80 * 1000 * 1000
)

WIDTH = disp.width
HEIGHT = disp.height
image = Image.open("cat.jpg")
image = image.resize((WIDTH, HEIGHT))

disp.display(image)

flir = FlirOneR2();
if flir.active==False:
    exit()
while(True):
    flir.getFrame()
    img = flir.getThermal()

    #convert the image into a displayable form
    rgbimg = Image.new("RGBA", img.size)
    scr = rgbimg.resize((240,240))
    scr.paste(img.resize((240,180)))
    print(flir.maxvloc)
    x,y=flir.maxvloc
    x=int(x*1.5)
    y=int(y*1.5)
    draw = ImageDraw.Draw(scr)
    draw.point(flir.maxvloc,'red')
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 30)
    text="Temp {:0.2f}ºC".format(flir.maxvc)
    draw.text((5, 185), text,font=font)
    draw.ellipse([(x-2,y-2),(x+2,y+2)], fill=(255,0,0,255))
    disp.display(scr)

flir.disconnect()
exit()
#i = flir.getImage()
