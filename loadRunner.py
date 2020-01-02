import pygame,time,sys,random
SCREEN_WIDTH,SCREEN_HEIGHT,MAX_RADIUS = 900,600,540
PIC_WIDTH,PIC_HEIGHT = 30,33
GRID_COLS,GRID_ROWS = 28,16

HOLE_ID,SPACE_ID,VGROUND_ID,GROUND_ID,FLOOR_ID,BAR_ID,LADDER_ID,HLADDER_ID,\
    BOX_ID,POLICE_ID = -1,0,1,2,3,4,5,6,7,8
# runner status: on ground, on ladder, falling,in hole facing left/right, initial
ONGROUND_STAT,ONLADDER_STAT,FALL_STAT,RHOLE_STAT,LHOLE_STAT,WAIT_STAT\
    = 9,10,11,12,13,99

ROLE_LIST = '.#=-HTBPR'
SPEED_X   = [1,0,-1,0,0]
SPEED_Y   = [0,1,0,-1,0]
ACT_RATE  = 3

# initialize pictures
def initPic(pf):
    pic = pygame.image.load(pf)
    pic.set_colorkey((0,0,0))
    return pic
def initPicList(fList):
    picList = []
    for pf in fList:
        pic = initPic(pf)
        picList.append(pic)
    return picList
def drawCircle(screen,r):
    W,H = SCREEN_WIDTH//2,SCREEN_HEIGHT//2
    hMax = H-r
    if hMax>0:
        screen.fill((0,0,0),(0,0,SCREEN_WIDTH,hMax))
        screen.fill((0,0,0),(0,SCREEN_HEIGHT-hMax,SCREEN_WIDTH,SCREEN_HEIGHT))
    for y in range(r,-1,-1):
        x = (r*r-y*y)**0.5
        screen.fill((0,0,0),(0,int(round(H-y)),int(round(W-x)),1))
        screen.fill((0,0,0),(int(round(W+x)),int(round(H-y)),int(round(W-x)),1))
        screen.fill((0,0,0),(0,int(round(H+y)),int(round(W-x)),1))
        screen.fill((0,0,0),(int(round(W+x)),int(round(H+y)),int(round(W-x)),1))
    return

class Framework(object):
    def __init__(self,fList,rpList,gpList,ppList,bPic,tPic,nPic,\
                 x0,y0,cols,rows):
        self.map = pygame.Surface((PIC_WIDTH*GRID_COLS,PIC_HEIGHT*GRID_ROWS))
        self.picList = initPicList(fList)
        self.x0,self.y0 = x0,y0
        self.cols,self.rows = cols,rows
        self.grid = []
        self.boxList = []
        self.policeList = []
        self.runner = Runner(rpList[0:3],rpList[3:6],rpList[6:9],rpList[9:12],\
                             rpList[12:14],rpList[16],rpList[14],rpList[15],\
                             x0,y0,14*PIC_WIDTH,14*PIC_HEIGHT)
        self.gpList = []
        for fn in gpList:
            pic = pygame.image.load(fn)
            self.gpList.append(pic)
        self.ppList = ppList
        self.boxPic = initPic(bPic)
        self.titlePic  = initPic(tPic)
        self.numPic = pygame.image.load(nPic)
        self.level,self.boxNum,self.holeNum,self.begin = 1,0,0,time.time()
        self.grdList = []
        self.readLevel(self.ppList,self.boxPic) #init 1st level
        self.openR,self.openStp = 0,5
        return
    def processPicNo(self,x,y,picNo):
        if picNo<5:
            self.grid[y][x] = picNo+1
            self.map.blit(self.picList[picNo],(x*PIC_WIDTH,y*PIC_HEIGHT))
        elif picNo == 5:    #box
            self.grid[y][x] = picNo+1
        elif picNo == 6:    #box
            box = Box(self.boxPic,self.x0,self.y0,x,y)
            self.boxList.append(box)
        elif picNo == 7:    #new police
            pl = self.ppList
            police = Police(pl[0:3],pl[3:6],pl[6:9],pl[9:12],pl[12:14],pl[14],pl[14],pl[14],\
                            self.x0,self.y0,x*PIC_WIDTH,y*PIC_HEIGHT)
            police.x,police.y = x*PIC_WIDTH,y*PIC_HEIGHT
            police.gx,police.gy,police.stat = x,y,WAIT_STAT
            police.plcList = self.policeList #!danger!#
            self.policeList.append(police)
        elif picNo == 8:    #runner
            self.runner.x,self.runner.y = x*PIC_WIDTH,y*PIC_HEIGHT
            self.runner.gx,self.runner.gy,self.runner.stat = x,y,WAIT_STAT
        return
    def readLevel(self,ppList,bPic):
        fn = open('level'+str(self.level)+'.lrn')
        strList = fn.readlines()
        fn.close()
        self.boxList,self.policeList,self.grdList,self.grid = [],[],[],[]
        self.boxNum,self.holeNum = 0,0
        for y in range(self.rows):
            line = [0]*self.cols
            self.grid.append(line)
        self.map.fill((0,0,0))
        for y in range(len(strList)):
            line = strList[y]
            for x in range(len(line)):
                if x>=self.cols:
                    break
                if not (line[x]in ROLE_LIST):
                    continue
                picNo = ROLE_LIST.index(line[x])
                self.processPicNo(x,y,picNo)
        return
    def ifAbleDig(self,grid,gx,gy,flag):
        dx = 1
        if flag == pygame.K_z:
            dx = -1
            if gx == 0:
                return False
        elif gx == GRID_COLS-1:
            return False
        if gy == GRID_ROWS-1:
            return False
        if (not grid[gy][gx+dx] in (HOLE_ID,SPACE_ID,BAR_ID,HLADDER_ID))\
           or grid[gy+1][gx+dx] != GROUND_ID:
            return False
        self.runner.x,self.runner.y = gx*PIC_WIDTH,gy*PIC_HEIGHT
        grd = Ground(self.gpList,self.x0,self.y0,gx+dx,gy)
        self.grdList.append(grd)
        grid[gy+1][gx+dx] = HOLE_ID
        return True
    def draw(self,screen,flag):
        screen.blit(self.map,(self.x0,self.y0))
        titleY = self.y0+GRID_ROWS*PIC_HEIGHT
        screen.blit(self.titlePic,(self.x0,titleY))
        if flag>4:
            if not self.ifAbleDig(self.grid,self.runner.gx,self.runner.gy,flag):
                flag = 4
        if self.openR<=MAX_RADIUS:
            flag,self.runner.stat = 4,WAIT_STAT
        for grd in self.grdList:
            p = grd.draw(screen,self.grid)
            if grd.tick>330:
                self.grid[grd.gy+1][grd.gx]=GROUND_ID
        for grd in self.grdList:
            if grd.tick>336:
                self.grdList.pop(self.grdList.index(grd))
        self.runner.drive(screen,self.grid,flag)
        if self.grid[self.runner.gy][self.runner.gx]==GROUND_ID\
           and self.openR>MAX_RADIUS:
            self.openR,self.openStp = MAX_RADIUS,-5
            print("game over")
        if self.runner.status == WAIT_STAT:
            self.begin = time.time()
        else:
            end = time.time()
            self.writeNum(screen,int(end-self.begin),460,titleY+7)
        for box in self.boxList:
            box.draw(screen)
            if self.runner.gx == box.gx and self.runner.gy == box.gy:
                self.boxList.pop(self.boxList.index(box))
                self.boxNum+=1
        self.writeNum(screen,self.boxNum,30,titleY+7)
        for police in self.policeList:
            if police.drive(screen,self.grid,self.runner)\
               and self.openR>MAX_RADIUS:
                self.openR,self.openStp = MAX_RADIUS,-5
                print('You have been caught!')
            holeFlag = 0
            while self.grid[police.gy][police.gx] == GROUND_ID:
                police.y,police.gy,police.gx = -3,0,random.randint(0,27)
                police.x,police.stat = police.gx*PIC_WIDTH,FALL_STAT
                police.systick,holeFlag = 20,1
            self.holeNum += holeFlag
        self.writeNum(screen,self.holeNum,198,titleY+7)
        self.writeNum(screen,self.level,746,titleY+7)
        #天梯
        if len(self.boxList) == 0:
            self.showHladder()
            #过关
            if self.runner.gy == 0 and self.openStp>0:
                self.level+=1
                self.openR,self.openStp = MAX_RADIUS,-5
        if self.openR<=MAX_RADIUS:
            drawCircle(screen,self.openR)
            self.openR+=self.openStp
            if self.openR<0:
                self.openStp = -self.openStp
                self.readLevel(self.ppList,self.boxPic)
        return
    def showHladder(self):
        for gy in range(len(self.grid)):
            for gx in range(len(self.grid[gy])):
                if self.grid[gy][gx] == HLADDER_ID:
                    self.grid[gy][gx] = LADDER_ID
                    self.map.blit(self.picList[LADDER_ID-1],\
                                  (gx*PIC_WIDTH,gy*PIC_HEIGHT))
        return
    def writeNum(self,screen,num,x,y):
        x,y = self.x0+x,self.y0+y
        h = num//100
        screen.blit(self.numPic,(x,y),(h*PIC_WIDTH,0,PIC_WIDTH,PIC_HEIGHT))
        t,x = num//10%10,x+PIC_WIDTH
        screen.blit(self.numPic,(x,y),(t*PIC_WIDTH,0,PIC_WIDTH,PIC_HEIGHT))
        s,x = num%10,x+PIC_WIDTH
        screen.blit(self.numPic,(x,y),(s*PIC_WIDTH,0,PIC_WIDTH,PIC_HEIGHT))
        return

class Box(object):
    def __init__(self,pic,x0,y0,gx,gy):
        self.pic = pic
        self.x0,self.y0 = x0,y0
        self.gx,self.gy = gx,gy
        return
    def put(self,gx,gy):
        self.gx,self.gy = gx,gy
        return
    def draw(self,screen):
        if self.gx>=0:
            screen.blit(self.pic,\
                    (self.x0+self.gx*PIC_WIDTH,self.y0+self.gy*PIC_HEIGHT))
        return
class Ground(object):
    def __init__(self,gpList,x0,y0,gx,gy):
        self.picList = gpList
        self.x0,self.y0 = x0,y0
        self.gx,self.gy = gx,gy
        self.tick = 0
        return
    def draw(self,screen,grid):
        p = 6
        if self.tick<18:
            p = self.tick//3
        elif self.tick>317:
            p = self.tick//3-100
        self.tick+=1
        screen.blit(self.picList[p],\
                    (self.x0+self.gx*PIC_WIDTH,self.y0+self.gy*PIC_HEIGHT))
        return p
class Runner(object):
    def __init__(self,runRPL,runLPL,barRPL,barLPL,upPL,fallPic,holePL,holePR,x0,y0,x,y):
        self.runRPL  = initPicList(runRPL)
        self.runLPL  = initPicList(runLPL)
        self.barRPL  = initPicList(barRPL)
        self.barLPL  = initPicList(barLPL)
        self.upPL    = initPicList(upPL)
        self.fallPic = initPic(fallPic)
        self.holePL  = initPic(holePL)
        self.holePR  = initPic(holePR)
        self.x0,self.y0,self.x,self.y = x0,y0,x,y
        self.gx,self.gy = 0,0
        self.flag = 4
        self.status = WAIT_STAT
        self.systick = 0
        self.currentPic = self.fallPic
        return
    def test(self,grid,flag,gx,gy):
        gx += SPEED_X[flag]
        gy += SPEED_Y[flag]
        if gx == GRID_COLS or gx<0:
            return False
        if gy == GRID_ROWS:
            return False
        return not grid[gy][gx]in(FLOOR_ID,GROUND_ID,VGROUND_ID)
    def getStat(self,grid,gx,gy):
        stat = grid[gy][gx]
        if stat<=SPACE_ID or stat == HLADDER_ID or stat == VGROUND_ID:
            if gy==GRID_ROWS-1:
                stat = ONGROUND_STAT
            elif grid[gy+1][gx] in (GROUND_ID,FLOOR_ID,POLICE_ID):
                stat = ONGROUND_STAT
            elif grid[gy+1][gx] == LADDER_ID:
                stat = ONLADDER_STAT
            elif (grid[gy+1][gx]<=VGROUND_ID\
                  or grid[gy+1][gx] == BAR_ID\
                  or grid[gy+1][gx] == HLADDER_ID):
                stat = FALL_STAT
        return stat
    def hMove(self,picList,flag):
        self.x += SPEED_X[flag]*3
        self.y  = self.gy*PIC_HEIGHT
        self.currentPic = picList[self.systick//ACT_RATE%len(picList)]
        return
    def vMove(self,picList,flag):
        self.x  = self.gx*PIC_WIDTH
        self.y += SPEED_Y[flag]*3
        self.currentPic = picList[self.systick//ACT_RATE%len(picList)]
        return
    def fallMove(self,screen,grid):
        self.vMove([self.fallPic],1)
        return
    def barMove(self,screen,grid,flag):
        if flag == 0 and self.test(grid,flag,self.gx,self.gy):
            self.hMove(self.barRPL,flag)
        elif flag == 2 and self.test(grid,flag,self.gx,self.gy):
            self.hMove(self.barLPL,flag)
        elif flag == 1 and self.test(grid,flag,self.gx,self.gy):
            self.gx = int(self.x/PIC_WIDTH+0.5)
            self.status = FALL_STAT
            self.fallMove(screen,grid)
        return
    def onLadderMove(self,screen,grid,flag):
        if flag == 0 or flag == 2:
            self.onGroundMove(screen,grid,flag)
        elif flag == 1:
            self.ladderMove(screen,grid,flag)
        return
    def ladderMove(self,screen,grid,flag):
        if flag == 0 or flag == 2:
            self.gy = int(self.y/PIC_HEIGHT+0.5)
            self.onGroundMove(screen,grid,flag)
            return
        if (self.x+6)%PIC_WIDTH<=12:
            if flag!=4 and self.test(grid,flag,self.gx,self.gy):
                self.vMove(self.upPL,flag)
        else:
            flag = 2
            if self.gx*PIC_WIDTH<self.x:
                flag = 0
            self.onGroundMove(screen,grid,flag)
        return
    def onGroundMove(self,screen,grid,flag):
        pic = self.currentPic
        if flag == 0 and self.test(grid,flag,self.gx,self.gy):
            self.hMove(self.runRPL,flag)
        elif flag == 2 and self.test(grid,flag,self.gx,self.gy):
            self.hMove(self.runLPL,flag)
        return
    def drive(self,screen,grid,flag):
        self.systick+=1
        if flag == pygame.K_z:
            self.currentPic = self.holePL
            self.draw(screen)
            return
        elif flag == pygame.K_x:
            self.currentPic = self.holePR
            self.draw(screen)
            return
        elif flag != 4 and self.status == WAIT_STAT: #when game begins
            self.status = self.getStat(grid,self.gx,self.gy)
        if self.stat == FALL_STAT:
            self.fallMove(screen,grid)
        elif self.stat == BAR_ID:
            self.barMove(screen,grid,flag)
        elif self.stat == LADDER_ID:
            self.ladderMove(screen,grid,flag)
        elif self.stat == ONLADDER_STAT:
            self.onLadderMove(screen,grid,flag)
        elif self.stat == ONGROUND_STAT:
            self.onGroundMove(screen,grid,flag)
        elif self.stat == WAIT_STAT:
            self.hMove(self.runRPL,4)
        self.draw(screen)
        if self.status == WAIT_STAT:
            return
        gx,gy = self.gx,self.gy
        if (self.x+6)%PIC_WIDTH<=12:
            gx = (self.x+6)//PIC_WIDTH
        if (self.y+4)%PIC_HEIGHT<=6:
            gy = (self.y+4)//PIC_HEIGHT
            self.gx,self.gy = gx,gy
            self.stat = self.getStat(grid,self.gx,self.gy)
        return
    def draw(self,screen):
        screen.blit(self.currentPic,(int(round(self.x0+self.x)),int(round(self.y0+self.y))))
        return
    def hole(self,key):
        self.currentPic = self.holePL
        if key == pygame.K_x:
            self.currentPic = self.holePR
        return

class Police(Runner):
    def hMove(self,picList,flag):
        self.x+= SPEED_X[flag]*1.5
        self.y = self.gy*PIC_HEIGHT
        self.currentPic = picList[self.systick//ACT_RATE%len(picList)]
        return
    def vMove(self,picList,flag):
        self.x = self.gx*PIC_WIDTH
        self.y+= SPEED_Y[flag]*1.5
        self.currentPic = picList[self.systick//ACT_RATE%len(picList)]
        return
    def test(self,grid,flag,gx,gy):
        gx+=SPEED_X[flag]
        gy+=SPEED_Y[flag]
        if gx == GRID_COLS or gx<0:
            return False
        if gy == GRID_ROWS:
            return False
        for police in self.plcList:
            if gx == police.gx and gy==police.gy:
                return False
        return not grid[gy][gx] in (FLOOR_ID,GROUND_ID,VGROUND_ID)
    def findUpdown(self,grid):
        upLD,downLD,downJP = GRID_COLS,GRID_COLS,GRID_COLS
        for dx in range(0,GRID_COLS-self.gx):
            if grid[self.gy][self.gx+dx] == LADDER_ID and upLD>dx:
                upLD = dx
            if self.gy<GRID_ROWS-1:
                if grid[self.gy+1][self.gx+dx] == LADDER_ID and downLD>dx:
                    downLD = dx
                if grid[self.gy+1][self.gx+dx] in [SPACE_ID,VGROUND_ID]:
                    if downJP>dx:
                        downJP = dx
                    if grid[self.gy][self.gx+dx]!=BAR_ID:
                        break
            if not self.test(grid,0,self.gx+dx,self.gy):
                break
        for dx in range(0,-self.gx-1,-1):
            if (grid[self.gy][self.gx+dx] == LADDER_ID) and (abs(upLD)>abs(dx)):
                upLD = dx
            if self.gy<GRID_ROWS-1:
                if (grid[self.gy+1][self.gx+dx] == LADDER_ID) and (abs(downLD)>abs(dx)):
                    downLD = dx
                if grid[self.gy+1][self.gx+dx] in [SPACE_ID,VGROUND_ID]:
                    if abs(downJP)>abs(dx):
                        downJP = dx
                    if grid[self.gy][self.gx+dx]!=BAR_ID:
                        break
            if not self.test(grid,2,self.gx+dx,self.gy):
                break
        return upLD,downLD,downJP
    def drive(self,screen,grid,runner):
        if runner.stat == WAIT_STAT:
            self.draw(screen)
            return False
        flag = self.flag
        upLD,downLD,downJP = self.findUpdown(grid)
        if runner.gy>self.gy:
            flag = 1
            down = downLD
            if abs(downLD)>abs(downJP):
                down = downJP
            if down>0 and down!=GRID_COLS:
                flag = 0
            elif down<0:
                flag = 2
            #if not able to turn keep direction
            if flag == 1 and (not self.stat in (FALL_STAT,ONLADDER_STAT,LADDER_ID,BAR_ID)):
                flag = self.flag
        elif runner.gy<self.gy:
            flag = 3
            if upLD>0 and upLD!=GRID_COLS:
                flag = 0
            elif upLD<0:
                flag = 2
            elif self.stat != LADDER_ID:
                flag = self.flag
        elif runner.gx>self.gx:
            flag = 0
            if downJP==1 and grid[self.gy][self.gx+1]!=BAR_ID:
                flag = 1
        elif runner.gx<self.gx:
            flag = 2
            if downJP==-1 and grid[self.gy][self.gx-1]!=BAR_ID:
                flag = 1
        else: # if caught runner
            return True
        self.flag = flag
        if self.stat == HOLE_ID: #if in hole
            if self.systick>0:
                grid[self.gy][self.gx] = POLICE_ID
                self.hX,self.hY = self.gx,self.gy #remember coordinate of hole
                self.systick = -180 #time needed to get out
            elif self.systick == 0:
                self.systick = 1
                self.stat = ONGROUND_STAT
                if grid[self.hY][self.hX] == POLICE_ID:
                    grid[self.hY][self.hX] = HOLE_ID #restore hole to ground
                return False
            elif self.systick>-70 and self.systick%3==0:
                self.gx,self.gy = self.hX,self.hY-1
                self.x = self.gx*PIC_WIDTH
                self.vMove(self.upPL,3)
        self.systick+=1
        if self.stat == WAIT_STAT: #start of game
            self.stat = self.getStat(grid,self.gx,self.gy)
        if self.stat == FALL_STAT:
            self.fallMove(screen,grid)
        elif self.stat == BAR_ID:
            self.barMove(screen,grid,flag)
        elif self.stat == LADDER_ID:
            self.ladderMove(screen,grid,flag)
        elif self.stat == ONLADDER_STAT:
            self.onLadderMove(screen,grid,flag)
        elif self.stat == ONGROUND_STAT:
            self.onGroundMove(screen,grid,flag)
        self.draw(screen)
        if self.stat == WAIT_STAT:
            return False
        
        gx,gy = self.gx,self.gy
        if (self.x+3)%PIC_WIDTH<=6:
            gx = (self.x+6)//PIC_WIDTH
        if (self.y+3)%PIC_HEIGHT<=6:
            gy = (self.y+3)//PIC_HEIGHT
        if gx == self.gx and gy == self.gy and self.stat != FALL_STAT:
            return False
        self.gx,self.gy = round(gx),round(gy)
        if grid[self.gy][self.gx] == HOLE_ID:
            self.stat = HOLE_ID
            return False
        if self.systick>10:
            self.stat = self.getStat(grid,self.gx,self.gy)
        return False
#------------------MAIN------------------#
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH,SCREEN_HEIGHT))
pygame.display.set_caption('LodeRunner')
clock = pygame.time.Clock()

picList = ['assets/vground.bmp','assets/ground.bmp','assets/floor.bmp','assets/bar.bmp','assets/ladder.bmp']
runList = ['assets/rr01.bmp', 'assets/rr02.bmp', 'assets/rr03.bmp', 'assets/lr01.bmp', 'assets/lr02.bmp', \
 'assets/lr03.bmp', 'assets/rbar01.bmp', 'assets/rbar02.bmp', 'assets/rbar03.bmp', 'assets/lbar01.bmp', 'assets/lbar02.bmp',\
 'assets/lbar03.bmp', 'assets/up01.bmp', 'assets/up02.bmp', 'assets/lhole.bmp', 'assets/rhole.bmp', 'assets/fall.bmp' ]
ppList = ['assets/pr01.bmp', 'assets/pr02.bmp', 'assets/pr03.bmp', 'assets/pl01.bmp', 'assets/pl02.bmp', \
 'assets/pl03.bmp', 'assets/prbar01.bmp', 'assets/prbar02.bmp', 'assets/prbar03.bmp', 'assets/plbar01.bmp', 'assets/plbar02.bmp',\
 'assets/plbar03.bmp', 'assets/pup01.bmp', 'assets/pup02.bmp', 'assets/pfall.bmp']
gpList = ['assets/grd00.bmp', 'assets/grd01.bmp', 'assets/grd02.bmp', 'assets/grd03.bmp', 'assets/grd04.bmp', \
          'assets/grd05.bmp', 'assets/grd06.bmp', 'assets/grd07.bmp', 'assets/grd08.bmp', 'assets/grd09.bmp', \
          'assets/grd10.bmp', 'assets/grd11.bmp', 'assets/grd12.bmp' ]
framework = Framework(picList,runList,gpList,ppList,\
            "assets/box.bmp",'assets/title.bmp','assets/number.bmp',30,10,28,16)
while True:
    currentFlag = 4
    keyPressed = pygame.key.get_pressed()
    if keyPressed[pygame.K_RIGHT]:
        currentFlag = 0
    elif keyPressed[pygame.K_LEFT]:
        currentFlag = 2
    elif keyPressed[pygame.K_UP]:
        currentFlag = 3
    elif keyPressed[pygame.K_DOWN]:
        currentFlag = 1
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_z or event.key == pygame.K_x:
                currentFlag = event.key
#            if event.key == pygame.K_p:
#                print('POLICE',framework.policeList[0].x,framework.policeList[0].y,\
#                      framework.policeList[0].status)
    framework.draw(screen,currentFlag)
    pygame.display.update()
    clock.tick(50)
