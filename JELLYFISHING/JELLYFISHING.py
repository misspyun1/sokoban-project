import ConfigParser
import pygame
from pygame.locals import *
import pygame.locals as pg
import random, sys, copy, os, pygame


width, height = (32, 32)
screenwidth=800
screenheight=600
TILEWIDTH=48
TILEHEIGHT=48
TILEFLOORHEIGHT = 48
imagex=48
imagey=48

UP = 'up'
DOWN = 'down'
LEFT = 'left'
RIGHT = 'right'



def main():
    global IMAGESDICT, TILEMAPPING,OUTSIDEDECOMAPPING,PLAYERIMAGES,ourScreen,levelObj,mapObj,gameStateObj,goals
    pygame.init()
    ourScreen=pygame.display.set_mode((screenwidth,screenheight))
    pygame.display.set_caption("JELLYFISHING")


    IMAGESDICT = {'uncovered goal': pygame.image.load('RedSelector.png'),
                  'covered goal': pygame.image.load('Selector.png'),
                  'star': pygame.image.load('star.png'),
                  'corner': pygame.image.load('Grass_Block.png'),
                  'wall': pygame.image.load('Wood_Block_Tall.png'),
                  'inside floor': pygame.image.load('Plain_Block.png'),
                  'outside floor': pygame.image.load('Grass_Block.png'),
                  'title': pygame.image.load('star_title.png'),
                  'solved': pygame.image.load('star_solved.png'),
                  'princess': pygame.image.load('princess.png'),
                  }

    TILEMAPPING = {
                   '#': IMAGESDICT['wall'],
                   'o': IMAGESDICT['inside floor'],
                   ' ': IMAGESDICT['outside floor'],
               '\n':IMAGESDICT['outside floor'],
               '.':IMAGESDICT['covered goal'],
               '$':IMAGESDICT['star'],
               '@':IMAGESDICT['princess']}

    PLAYERIMAGES = [IMAGESDICT['princess']]

    startScreen()

    levels=readLevelsFile('tilemap_test.txt')
    levelNum=0
    
    while True:
        levelObj = levels[levelNum]
        mapObj=levelObj['mapObj']
        gameStateObj = copy.deepcopy(levelObj['startState'])
        goals=levelObj['goals']
        result = runLevel(levels, levelNum)

        if result in ('solved', 'next'):
            levelNum += 1
            if levelNum >= len(levels):
                levelNum = 0
        elif result == 'back':
            levelNum -= 1
            if levelNum < 0:
                levelNum = len(levels)-1
        elif result == 'reset':
            pass

def startScreen():
    clock = pygame.time.Clock()
    titleRect = IMAGESDICT['title'].get_rect()
    topCoord = 50 # topCoord tracks where to position the top of the text
    titleRect.top = topCoord+20
    titleRect.centerx = int(screenwidth/2)
    topCoord += titleRect.height

    ourScreen.fill((0,170,255))
    ourScreen.blit(IMAGESDICT['title'], titleRect)

    while True: # Main loop for the start screen.
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                return # user has pressed a key, so return.

        pygame.display.update()
        clock.tick()

def runLevel(levels, levelNum):
    mapObj = emptyMap(levelObj['mapObj'], levelObj['startState']['player'])
    mapNeedsRedraw = True 
    mapWidth = len(mapObj) * TILEWIDTH
    mapHeight = (len(mapObj[0]) - 1) * TILEFLOORHEIGHT + TILEHEIGHT
    levelIsComplete = False
    clock = pygame.time.Clock()

    while True: 
        playerMoveTo = None
        keyPressed = False

        for event in pygame.event.get(): 
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == KEYDOWN:
                keyPressed = True
                if event.key == K_LEFT:
                    playerMoveTo = LEFT
                elif event.key == K_RIGHT:
                    playerMoveTo = RIGHT
                elif event.key == K_UP:
                    playerMoveTo = UP
                elif event.key == K_DOWN:
                    playerMoveTo = DOWN

                elif event.key == K_n:
                    return 'next'
                elif event.key == K_b:
                    return 'back'
                elif event.key == K_ESCAPE:
                       pygame.quit()
                       sys.exit()
                elif event.key == K_BACKSPACE:
                    return 'reset' 

        if playerMoveTo != None and not levelIsComplete:
            moved = playermoving(mapObj, gameStateObj, playerMoveTo)

            if moved:
                mapNeedsRedraw = True

            if LevelFinish(levelObj, gameStateObj):
                levelIsComplete = True
                keyPressed = False

        background=pygame.image.load("background.png")

        ourScreen.blit(background,(0,0))

        if mapNeedsRedraw:
            mapSurf = drawMap(mapObj, gameStateObj, levelObj['goals'])
            mapNeedsRedraw = False

        mapSurfRect = mapSurf.get_rect()
        mapSurfRect.center = (int(screenwidth/2) , int(screenheight/2) )
        ourScreen.blit(mapSurf, mapSurfRect)
        #here levelNum 
        if levelIsComplete:
            solvedRect = IMAGESDICT['solved'].get_rect()
            solvedRect.center = (int(screenwidth/2)+10, int(screenheight/2)-30)
            ourScreen.blit(IMAGESDICT['solved'], solvedRect)

            if keyPressed:
                return 'solved'

        pygame.display.update()
        clock.tick()

def detectCollisions(mapObj, x, y):
    if x < 0 or x >= len(mapObj) or y < 0 or y >= len(mapObj[x]):
        return False 
    elif mapObj[x][y] in ('#'):
        return True 
    return False

def emptyMap(mapObj,startxy):
    startx,starty=startxy
    mapObjcopy=copy.deepcopy(mapObj)
    for x in range(len(mapObjcopy)):
        for y in range(len(mapObjcopy[0])):
            if mapObjcopy[x][y] in ('$', '.', '@', '+', '*'):
                mapObjcopy[x][y] = ' '
    floodFill(mapObjcopy, startx, starty, ' ', 'o')
    return mapObjcopy

def detectBlock(mapObj,gameStateobj,x,y):
    if detectCollisions(mapObj,x,y):
        return True
    elif x<0 or x>=len(mapObj) or y<0 or y>=len(mapObj[x]):
        return True
    elif (x,y) in gameStateObj['stars']:
        return True
    else :
        return False
 

def playermoving(mapObj,gameStateObj,playerMoveTo):
    playerx, playery = gameStateObj['player']
    stars = gameStateObj['stars']
    if playerMoveTo == UP:
        deltax = 0
        deltay = -1
    elif playerMoveTo == RIGHT:
        deltax = 1
        deltay = 0
    elif playerMoveTo == DOWN:
        deltax = 0
        deltay = 1
    elif playerMoveTo == LEFT:
        deltax = -1
        deltay = 0
   
    if detectCollisions(mapObj, playerx + deltax, playery + deltay):
        return False
    else:
        if (playerx + deltax, playery + deltay) in stars:
            if not detectBlock(mapObj, gameStateObj, playerx + (deltax*2), playery + (deltay*2)):
                ind = stars.index((playerx + deltax, playery + deltay))
                gameStateObj['stars'][ind] = (stars[ind][0] + deltax, stars[ind][1] + deltay)
            else:
                return False
        gameStateObj['player'] = (playerx + deltax, playery + deltay)
        return True



def readLevelsFile(filename):
    assert os.path.exists(filename), 'Cannot find the level file: %s' % (filename)
    mapFile = open(filename, 'r')
    content = mapFile.readlines() + ['\r\n']
    mapFile.close()
    mapObj=[]
    goals = []
    levels = [] 
    levelNum = 0
    mapTextLines = [] 
    for lineNum in range(len(content)):
        line = content[lineNum].rstrip('\r\n')

        if ';' in line:
            line = line[:line.find(';')]

        if line != '':
            mapTextLines.append(line)
        elif line == '' and len(mapTextLines) > 0:
            maxWidth = -1
            for i in range(len(mapTextLines)):
                if len(mapTextLines[i]) > maxWidth:
                    maxWidth = len(mapTextLines[i])
            for i in range(len(mapTextLines)):
                mapTextLines[i] += ' ' * (maxWidth - len(mapTextLines[i]))
            for x in range(len(mapTextLines[0])):
                mapObj.append([])
            for y in range(len(mapTextLines)):
                for x in range(maxWidth):
                    mapObj[x].append(mapTextLines[y][x])
            startx = None 
            starty = None
            goals = []
            stars = [] 
            for x in range(maxWidth):
                for y in range(len(mapObj[x])):
                    if mapObj[x][y] in ('@', '+'):
                        startx = x
                        starty = y
                    if mapObj[x][y] in ('.', '+', '*'):
                        goals.append((x, y))
                    if mapObj[x][y] in ('$', '*'):
                        stars.append((x, y))
            assert startx != None and starty != None, 'Level %s (around line %s) in %s is missing a "@" or "+" to mark the start point.' % (levelNum+1, lineNum, filename)
            assert len(goals) > 0, 'Level %s (around line %s) in %s must have at least one goal.' % (levelNum+1, lineNum, filename)
            assert len(stars) >= len(goals), 'Level %s (around line %s) in %s is impossible to solve. It has %s goals but only %s stars.' % (levelNum+1, lineNum, filename, len(goals), len(stars))

            gameStateObj = {'player': (startx, starty),
                            'stepCounter': 0,
                            'stars': stars}
            levelObj = {'width': maxWidth,
                        'height': len(mapObj),
                        'mapObj': mapObj,
                        'goals': goals,
                        'startState': gameStateObj}

            levels.append(levelObj)
            mapTextLines = []
            mapObj = []
            gameStateObj = {}
            levelNum += 1
    return levels

def drawMap(mapObj, gameStateObj, goals):
    smallScreenWidth = len(mapObj) * TILEWIDTH
    smallScreenHeight = (len(mapObj[0]) - 1) * TILEFLOORHEIGHT + TILEHEIGHT
    smallScreen = pygame.Surface((smallScreenWidth, smallScreenHeight))
    smallScreen.fill((0,0,0)) 

    for x in range(len(mapObj)):
        for y in range(len(mapObj[x])):
            spaceRect = pygame.Rect((x * TILEWIDTH, y * TILEFLOORHEIGHT, TILEWIDTH, TILEHEIGHT))
            if mapObj[x][y] in TILEMAPPING:
                baseTile = TILEMAPPING[mapObj[x][y]]    
            smallScreen.blit(baseTile, spaceRect)    
            if (x, y) in gameStateObj['stars']:
                if (x, y) in goals:
                    smallScreen.blit(IMAGESDICT['covered goal'], spaceRect)
                else : smallScreen.blit(IMAGESDICT['star'], spaceRect)
            elif (x, y) in goals:
                smallScreen.blit(IMAGESDICT['uncovered goal'], spaceRect)
            if (x, y) == gameStateObj['player']:
                smallScreen.blit(PLAYERIMAGES[0], spaceRect)

    return smallScreen

def LevelFinish(levelObj, gameStateObj):
    for goal in levelObj['goals']:
        if goal not in gameStateObj['stars']:
            return False
    return True

def floodFill(mapObj, x, y, oldCharacter, newCharacter):
    if mapObj[x][y] == oldCharacter:
        mapObj[x][y] = newCharacter

    if x < len(mapObj) - 1 and mapObj[x+1][y] == oldCharacter:
        floodFill(mapObj, x+1, y, oldCharacter, newCharacter) #right
    if x > 0 and mapObj[x-1][y] == oldCharacter:
        floodFill(mapObj, x-1, y, oldCharacter, newCharacter) # left
    if y < len(mapObj[x]) - 1 and mapObj[x][y+1] == oldCharacter:
        floodFill(mapObj, x, y+1, oldCharacter, newCharacter) #down
    if y > 0 and mapObj[x][y-1] == oldCharacter:
        floodFill(mapObj, x, y-1, oldCharacter, newCharacter) # up

main()
    
