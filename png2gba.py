import os
import argparse
import cv2
import numpy as np
"""image colors are in BGR order"""

class Tile(object):
    def __init__(self):
        self.values = [[0,0,0,0,0,0,0,0],
                       [0,0,0,0,0,0,0,0],
                       [0,0,0,0,0,0,0,0],
                       [0,0,0,0,0,0,0,0],
                       [0,0,0,0,0,0,0,0],
                       [0,0,0,0,0,0,0,0],
                       [0,0,0,0,0,0,0,0],
                       [0,0,0,0,0,0,0,0]]
        self.hexvalues = []
        
    def __str__(self):
        s = ""
        for i in range(8):
            s += str(self.values[i]) + "\n"
        return s

    def hex32bit(self):
        '''Turn the values into a list of hex code strings'''
        self.hexvalues = []
        for i in range(len(self.values)):
            s = ''
            for val in range(len(self.values[i])):
                s += str(self.values[i][val])
            self.hexvalues.append("0x"+s[::-1])
            

parser = argparse.ArgumentParser(description='Process image files into C code for GBA')
parser.add_argument('--image', '-i', help="path and name of image")
args = parser.parse_args()
print(args.image)

if args.image is not None:
    filename = args.image
    fname = filename.split('/')
    outfilename = fname[-1]
    fname.remove(outfilename)    
    print(fname)
    path = ""
    for i in range(len(fname)):
        path += fname[i]+"/"
    print(path)
    print(outfilename)
    basename = outfilename.split('.')[0]
    outfilename = basename+"_image.c"
    print(outfilename)
    
else:
    filename = 'samus.png'
    basename = filename.split('.')[0]
    path = None
    outfilename = basename+"_image.c"


#Read in the image file  shouldn't have to resize in actual program
orig = cv2.imread(filename)
img = cv2.resize(orig, (24,34), interpolation=cv2.INTER_NEAREST)
print(img.shape)
img = img[1:img.shape[0]-1, 4:img.shape[1]-4]
print(img.shape)

#Get a list of all of the colors in RGB order
colors = []
for i in range(img.shape[0]):
    for j in range(img.shape[1]):
        colors.append([img[i][j][2], img[i][j][1], img[i][j][0]])

#Get a unique list of colors used in the image
palette = []
for color in colors:
    if color not in palette:
        palette.append(color)

#Convert to GBA color range (0-255) -> (0-31)
palette_gba = []
for color in palette:
    r = int((color[0]/255.0)*31)
    g = int((color[1]/255.0)*31)
    b = int((color[2]/255.0)*31)
    palette_gba.append((r,g,b))

print(palette)
print(palette_gba)
if len(palette_gba) < 16:
    for i in range(16-len(palette_gba)):
        palette_gba.append((0,0,0))



img_zero = np.zeros(img.shape[0]*img.shape[1])
#print(img_zero.shape)
#print(img_zero)
img_map = img_zero.reshape((img.shape[0], img.shape[1]))
#print(img_map)
print(img_map.shape)

#Create an 'image' using the palette indices where the colors are
for i in range(img.shape[0]):
    for j in range(img.shape[1]):
        temp = [img[i][j][2], img[i][j][1], img[i][j][0]]
        img_map[i][j] = int(palette.index(temp))

print(img_map)


print(img_map[0])
print("Tiles")
print(int(img_map.shape[0]/8))
print(int(img_map.shape[1]/8))

#Divide the image up into 8x8 tiles
numtiles = int(img_map.shape[0] * img_map.shape[1] / 64)
print("NUM TILES=%s" % numtiles)
tiles = []
for i in range(numtiles):
    tiles.append(Tile())

tilerow = 0
tilecol = 0
numcols = int(img_map.shape[1]/8)
print("Number of columns=%s" % numcols)

for row in range(img_map.shape[0]):
    #print(int(row % 8))
    #print("Tile row = %s" % int(row/8))
    tilerow = int(row/8)
    for col in range(img_map.shape[1]):
        tilecol = int(col/8)
        #print(int(col%8))
        #print("Tile col = %s" % int(col/8))
        tiles[tilerow*numcols+tilecol].values[int(row%8)][int(col%8)] = int(img_map[row][col])
        



        
print(tiles[1])
#tiles[1].hex32bit()
#print(tiles[1].hexvalues)

#Get the hexvalues for all of the tiles
for tile in tiles:
    tile.hex32bit()


if path is not None:
    f = open(path + outfilename, "a")
else:
    f = open(outfilename, "a")


#write out the palette first (palette_gba)
s = "u16 " + basename+"_palette[16][3] = {"
for i, rgb in enumerate(palette_gba):
    #if i == 0:
    s += "{"
    #else:
    #    s += " {"
    for j, val in enumerate(rgb):
        if j < (len(rgb)-1):
            s += str(val)+","
        else:
            if i < (len(palette_gba)-1):
                s += str(val)+"}, "
            else:
                s += str(val)+"}};\n\n"

            
f.write(s)
f.write("u32 " + basename+"_image["+str(numtiles)+"][8] = {\n")
for t, tile in enumerate(tiles):
    s = "\t{"
    for i, value in enumerate(tile.hexvalues):
        s += value
        if i < (len(tile.hexvalues)-1):
            s += ", "
        else:
            if t < (len(tiles)-1):
                s += "},\n"
            else:
                s += "}\n"
    f.write(s)
f.write("};\n\n")

f.close()
