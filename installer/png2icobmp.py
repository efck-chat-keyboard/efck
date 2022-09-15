#!/usr/bin/env python3
import os.path
from PIL import Image

os.chdir(os.path.join(os.path.dirname(__file__), '..', 'efck', 'icons'))

img = Image.open('logo.png').convert('RGBA')

img.save('logo.ico')

bmp = Image.new("RGBA", img.size, "WHITE")
bmp.paste(img, (0, 0), img)
bmp.convert('RGB').save('logo.bmp')
