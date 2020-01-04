import pygame,sys,math

# [recognizer]
# date: 2019.08.24
# version: 1.0
# author: Candice Zhang

def calValue(pic,x,y,w,h):
    rVal,gVal,bVal = 0,0,0
    for b in range(h):
        for a in range(w):
            colors =  pic.get_at((x+a,y+b))
            rVal+=colors[0]
            gVal+=colors[1]
            bVal+=colors[2]
    return (rVal/(w*h),gVal/(w*h),bVal/(w*h))

def recognize(iValue,stdList):
    closest = ''
    minVal = -1
    for i in range(len(stdList)):
        curBlock = stdList[i][0]
        curVal = ((iValue[0]-curBlock[0])**2+(iValue[1]-curBlock[1])**2+(iValue[2]-curBlock[2])**2)**0.5
        if curVal<minVal or minVal == -1:
            minVal = curVal
            closest = stdList[i][1]
    return closest

picName = input("name of the image: ")
pic = pygame.image.load(picName)

picW,picH = pic.get_size()
w,h = int(picW/28),int(picH/16)
calValue(pic,0,0,picW,picH)
vground = pygame.image.load("assets/vground.bmp")
ground  = pygame.image.load("assets/ground.bmp")
floor   = pygame.image.load("assets/floor.bmp")
bar     = pygame.image.load("assets/bar.bmp")
box     = pygame.image.load("assets/box.bmp")
ladder  = pygame.image.load("assets/ladder.bmp")
lr02    = pygame.image.load("assets/lr02.bmp")
pr02    = pygame.image.load("assets/pr02.bmp")
stdList = []
stdList.append([calValue(vground,0,0,30,33),"."])
stdList.append([calValue(ground,0,0,30,33),'#'])
stdList.append([calValue(floor,0,0,30,33),'='])
stdList.append([calValue(bar,0,0,30,33),'-'])
stdList.append([calValue(box,0,0,30,33),'B'])
stdList.append([calValue(ladder,0,0,30,33),'H'])
stdList.append([calValue(lr02,0,0,30,33),'P'])
stdList.append([calValue(pr02,0,0,30,33),'R'])
stdList.append([(0.0,0.0,0.1),' '])

fName = input("name of output file: ")
with open(fName,'w') as file_obj:
    for y in range(16):
        for x in range(28):
            imageValue = calValue(pic,x*w,y*h,w,h)
            file_obj.write(recognize(imageValue,stdList))
        file_obj.write('\n')
        
print("level succesfully generated")

