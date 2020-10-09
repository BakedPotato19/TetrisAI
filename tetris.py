import time
import typing
import random
from abc import ABC, abstractmethod
import pygame
import numpy as np
from enum import Enum

from PyEngine.States.GameState import *
from PyEngine.States.Statestack import *

from DesignPatterns.ObserverPattern.Observer import *

##########################################################
# This section contains the Tetris game
# and logic itself. 
# Including:
# Tiles
# Pieces
# Tetris Logic
##########################################################

class Pieces(Enum):
    IPiece = 0
    JPiece = 1
    SPiece = 2
    ZPiece = 3
    LPiece = 4
    TPiece = 5
    OPiece = 6

class Tile():
    def __init__(self, color: pygame.Color):
        self.color = color

class Piece(ABC):
    @abstractmethod
    def __init__(self):
        # Abstract property
        pass

    @property
    def color(self):
        raise NotImplementedError
    
    @property
    def matrix(self):
        raise NotImplementedError

    def rotateLeft(self):
        return np.rot90(self.matrix)

    def rotateRight(self):
        return np.rot90(self.matrix,3)



class IPiece(Piece):
    color = pygame.Color(0,240,240)
    matrix = np.array(
            [
            None,None,None,None,
            Tile(color),Tile(color),Tile(color),Tile(color),
            None,None,None,None,
            None,None,None,None]).reshape((4,4))

    def __init__(self):
        pass

class JPiece(Piece):
    color = pygame.Color(0,0,240)
    matrix = np.array(
            [
            None,None,Tile(color),None,
            None,None,Tile(color),None,
            None,Tile(color),Tile(color),None,
            None,None,None,None]).reshape((4,4))

    def __init__(self):
        pass

class LPiece(Piece):
    color = pygame.Color(240,160,0)
    matrix = np.array(
            [
            None,Tile(color),None,None,
            None,Tile(color),None,None,
            None,Tile(color),Tile(color),None,
            None,None,None,None]).reshape((4,4))

    def __init__(self):
        pass

class OPiece(Piece):
    color = pygame.Color(240,240,0)
    matrix = np.array(
            [
            None,None,None,None,
            None,Tile(color),Tile(color),None,
            None,Tile(color),Tile(color),None,
            None,None,None,None]).reshape((4,4))

    def __init__(self):
        pass

class SPiece(Piece):
    color = pygame.Color(0,240,0)
    matrix = np.array(
            [
            None,None,None,None,
            None,None,Tile(color),Tile(color),
            None,Tile(color),Tile(color),None,
            None,None,None,None]).reshape((4,4))

    def __init__(self):
        pass

class TPiece(Piece):
    color = pygame.Color(160,0,240)
    matrix = np.array(
            [
            None,None,None,None,
            None,None,Tile(color),None,
            None,Tile(color),Tile(color),Tile(color),
            None,None,None,None]).reshape((4,4))

    def __init__(self):
        pass

class ZPiece(Piece):
    color = pygame.Color(240,0,0)
    matrix = np.array(
            [
            None,None,None,None,
            Tile(color),Tile(color),None,None,
            None,Tile(color),Tile(color),None,
            None,None,None,None]).reshape((4,4))

    def __init__(self):
        pass

class PieceGenerator():
    @staticmethod
    def generate():
        i = random.choice(list(Pieces)).value
        if i is 0:
            return IPiece()
        elif i is 1:
            return ZPiece()
        elif i is 2:
            return TPiece()
        elif i is 3:
            return LPiece()
        elif i is 4:
            return JPiece()
        elif i is 5:
            return OPiece()
        elif i is 6:
            return SPiece()

class Tetris(Subject):
    _observers = []
    def __init__(self, rows, cols):
        self.rows, self.cols = (rows,cols)
        self.board = np.array([None]*self.rows*self.cols).reshape(self.rows,self.cols)  
        self.cpiece = PieceGenerator.generate()
        self.npiece = PieceGenerator.generate()

        self.offset = (0,3)
        self.score = 0
        self.tickcap = 20
        self.ticks = 0

        self.running = True
        self.busy = False

        self.moveLeft = False
        self.moveRight = False
        self.moveDown = False
        self.rotateRight = False
        self.rotateLeft = False

    def update(self):
        self.ticks +=1
        if(self.ticks % 3 == 0): self.domoves()
        if(self.ticks % 1 == 0): self.dorotations()

        if self.ticks < self.tickcap: return
        self.ticks = 0
        
        if self.collisionx(1,self.cpiece.matrix) or self.collisionpiece((1,0),self.cpiece.matrix): 
            self.recover()
            self.clearlines()
        else:
            self.move((1,0))

    def domoves(self):
        if self.busy:
            return
        if self.moveLeft and not self.collisiony(-1,self.cpiece.matrix) and not self.collisionpiece((0,-1),self.cpiece.matrix):
            self.move((0,-1))
        if self.moveRight and not self.collisiony(1,self.cpiece.matrix) and not self.collisionpiece((0,1),self.cpiece.matrix):
            self.move((0,1))
    
    def dorotations(self):
        if self.busy:
            return
        if self.rotateLeft:
            new = self.cpiece.rotateLeft()
            if( not self.collisionx(0,new) 
                and not self.collisiony(0,new)
                and not self.collisionpiece((0,0),new)):
                self.cpiece.matrix = new
                self.rotateLeft = False
        if self.rotateRight:
            new = self.cpiece.rotateRight()
            if( not self.collisionx(0,new) 
                and not self.collisiony(0,new)
                and not self.collisionpiece((0,0),new)):
                self.cpiece.matrix = new
                self.rotateRight = False


    def recover(self):
        self.blitpiecetoboard()
        self.cpiece = self.npiece
        self.npiece = PieceGenerator.generate()
        self.offset = (0,3)
        if self.collisionpiece((0,0),self.cpiece.matrix):
            self.running = False

    def move(self,pos):
        self.offset = (self.offset[0]+pos[0],self.offset[1]+pos[1])

    def blitpiecetoboard(self):
        for i, arr in enumerate(self.cpiece.matrix):
            for j, tile in enumerate(arr):
                if tile: self.board[i+self.offset[0],j+self.offset[1]] = tile

    def collisionx(self,x,matrix):
        for i,arr in enumerate(matrix):
            for j, tile in enumerate(arr):
                if tile and (i+self.offset[0]+x > 19):
                    return True
        return False
    
    def collisiony(self, y,matrix):
        for i, arr in enumerate(matrix):
            for j, tile in enumerate(arr):
                if tile and (0>j+self.offset[1]+y or j+self.offset[1]+y>9):
                    return True
        return False

    def collisionpiece(self,pos,matrix):
        for i, arr in enumerate(matrix):
            for j, tile in enumerate(arr):
                if tile and (self.board[i+self.offset[0]+pos[0],j+self.offset[1]+pos[1]]):
                        return True
        return False
    
    def clearlines(self):
        for i, arr in enumerate(self.board):
            if self.linefull(arr):
                self.board = np.delete(self.board,[i],0)
                self.board = np.insert(self.board,0,np.array([None]*self.cols),0)

    def linefull(self, line):
        for i in line:
            if not i:
                return False
        return True

    def prettyprint(self):
        for i in self.board:
            for j in i:
                if j:
                    print("T ",end="")
                else: print("N ",end="")
            print()

####################################################
# Static Renderer
####################################################

class Renderer():
    @staticmethod
    def drawtiles(screen, matrix, size, offset=(0,0)):
        for i,arr in enumerate(matrix):
            for j,tile in enumerate(arr):
                if tile:
                    pygame.draw.rect(screen, tile.color, ((j+offset[1])*size[1],(i+offset[0])*size[0],size[1]-1,size[0]-1))

    def drawnext(screen, matrix, size, offset):
        for i, arr in enumerate(matrix):
            for j, tile in enumerate(arr):
                pygame.draw.rect(
                        screen,
                        (pygame.Color(60,60,60) if not tile else tile.color), 
                            ((j+offset[1])*size[1],(i+offset[0])*size[0],size[1]-1,size[0]-1)
                                )

#####################################################
# This sections contains
# the GameType type. GameType
# contains information about different GameTypes
# (SP, MP, Online.). WindowSize etc. is contained 
# in GameType.
#####################################################
class GameType(Enum):
    sp = 1
    mp = 2
    server = 3


class IGameType:
    @property
    def controller(self):
        raise NotImplementedError

    @property
    def renderer(self):
        raise NotImplementedError

    @abstractmethod
    def calcWindowSize(self):
        raise NotImplementedError
    
    @abstractmethod
    def update(self, dt):
        raise NotImplementedError

    @abstractmethod
    def render(self, screen):
        raise NotImplementedError

    @abstractmethod
    def events(self, events):
        raise NotImplementedError


class SinglePlayerGameType(IGameType):
    controller = None
    renderer = None
    
    def __init__(self):
        self.rows, self.cols = (20,10)
        self.t = Tetris(self.rows, self.cols)

        self.controller = SinglePlayerController()
        self.renderer = SinglePlayerRenderer(self.rows, self.cols)
    
    def calcWindowSize(self):
        return self.renderer.windowsize
    
    def update(self, dt):
        self.t.update()

    def render(self, screen):
        self.renderer.render(screen, self.t)

    def events(self, events):
        self.controller.GameInput(events,self.t)

class TwoPlayerGameType(IGameType):
    controller = None
    renderer = None

    def __init__(self):
        self.rows, self.cols = (20,10)
        self.t1 = Tetris(self.rows, self.cols)
        self.t2 = Tetris(self.rows, self.cols)

        self.controller = TwoPlayerController()

        self.renderer = TwoPlayerRenderer(self.rows, self.cols)

    def calcWindowSize(self):
        return self.renderer.windowsize

    def update(self,dt):
        self.t1.update()
        self.t2.update()

    def render(self, screen):
        self.renderer.render(screen, [self.t1,self.t2])

    def events(self, events):
        self.controller.GameInput(events,[self.t1, self.t2])


class GameTypeFactory:
    @staticmethod
    def GenerateGameType(enu : GameType) -> IGameType:
        if enu is GameType.sp:
            return SinglePlayerGameType()
        elif enu is GameType.mp:
            return TwoPlayerGameType()
        elif enu is GameType.server:
            return SinglePlayerGameType()
        else:
            raise NotImplementedError

#####################################################
# This section contains
# different GameStates
#####################################################
class MainMenu(GameState):
    windowsize = None
    def __init__(self):
        self.w, self.h = (300,300)
        self.windowsize = (self.w, self.h)
        self.surf1 = pygame.Surface((self.w,self.h))

    def update(self, dt):
        pass

    def render(self, screen):
        self.surf1.fill((250,0,0))
        screen.blit(self.surf1,(0,0))
        

    def events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    StateStack.push(GameRunning(GameType.sp))
                elif event.key == pygame.K_m:
                    StateStack.push(GameRunning(GameType.mp))


class GameRunning(GameState):
    windowsize = None
    def __init__(self, gameType):

        self.gameType = GameTypeFactory.GenerateGameType(gameType)
        self.windowsize = self.gameType.calcWindowSize()
        

    def update(self,dt):
        self.gameType.update(dt)

    def render(self, screen):
        self.gameType.render(screen)

    def events(self,events):
        self.gameType.events(events)

    

#####################################################
# This section contains information about
# how to render different GameTypes
#
#####################################################

class IGameStateRenderer:
    @abstractmethod
    def __init__(self, rows, cols):
        pass

    @abstractmethod
    def render(self, screen, tetris):
        raise NotImplementedError

class SinglePlayerRenderer(IGameStateRenderer):
    ### BAD DESIGN: change (rows, cols) to render method
    def __init__(self, rows, cols):

        self.rows, self.cols = (rows,cols)
        self.w, self.h = (300,600)
        self.sw, self.sh = (200,self.h)
        self.surf1 = pygame.Surface((self.w,self.h))
        self.surf2 = pygame.Surface((self.sw, self.sh))
        self.windowsize = (self.w+self.sw,self.h)

    def render(self, screen, tetris):
        self.surf1.fill((180,180,180))
        self.surf2.fill((60,60,60))
        Renderer.drawtiles(self.surf1,tetris.cpiece.matrix,(self.w/self.cols, self.h/self.rows),tetris.offset)
        Renderer.drawtiles(self.surf1,tetris.board,(self.w/self.cols, self.h/self.rows), (0,0))
        Renderer.drawnext(self.surf2,tetris.npiece.matrix,(self.w/self.cols, self.h/self.rows),(1,1))

        screen.blit(self.surf1,(0,0))
        screen.blit(self.surf2,(self.w,0))

class TwoPlayerRenderer(IGameStateRenderer):
    def __init__(self, rows, cols):
        self.rows, self.cols = (rows,cols)
        self.w, self.h = (300,600)
        self.sw, self.sh = (200,self.h) 

        self.surf1p1 = pygame.Surface((self.w,self.h))
        self.surf2p1 = pygame.Surface((self.sw, self.sh))

        self.surf1p2 = pygame.Surface((self.w,self.h))
        self.surf2p2 = pygame.Surface((self.sw, self.sh))

        self.p1 = pygame.Surface((self.w+self.sw,self.h))
        self.p2 = pygame.Surface((self.w+self.sw,self.h))

        self.windowsize = (2*(self.w+self.sw),self.h)

    def render(self, screen, tetris):
        self.surf1p1.fill((180,180,180))
        self.surf2p1.fill((60,60,60))
        self.surf1p2.fill((180,180,180))
        self.surf2p2.fill((60,60,60))

        Renderer.drawtiles(self.surf1p1,tetris[1].cpiece.matrix,(self.w/self.cols, self.h/self.rows),tetris[1].offset)
        Renderer.drawtiles(self.surf1p1,tetris[1].board,(self.w/self.cols, self.h/self.rows), (0,0))
        Renderer.drawnext(self.surf2p1,tetris[1].npiece.matrix,(self.w/self.cols, self.h/self.rows),(1,1))

        Renderer.drawtiles(self.surf1p2,tetris[0].cpiece.matrix,(self.w/self.cols, self.h/self.rows),tetris[0].offset)
        Renderer.drawtiles(self.surf1p2,tetris[0].board,(self.w/self.cols, self.h/self.rows), (0,0))
        Renderer.drawnext(self.surf2p2,tetris[0].npiece.matrix,(self.w/self.cols, self.h/self.rows),(1,1))

        self.p1.blit(self.surf1p1,(0,0))
        self.p1.blit(self.surf2p1,(self.w,0))
        self.p2.blit(self.surf1p2,(0,0))
        self.p2.blit(self.surf2p2,(self.w,0))

        screen.blit(self.p1,(0,0))
        screen.blit(self.p2,(self.w+self.sw,0))




#####################################################
# This section contains 
# code for input communication controller
# from Game to Tetris.
# This is needed as SP and MP needs
# to communicate to Tetris in a different way
#####################################################

class IController:
    @abstractmethod
    def GameInput(self, iput, tetris):
        raise NotImplementedError

    @abstractmethod
    def ServerInput(self, iput, tetris):
        raise NotImplementedError

class SinglePlayerController(IController):
    def GameInput(self,events,tetris):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    tetris.moveLeft = True
                if event.key == pygame.K_RIGHT:
                    tetris.moveRight = True
                if event.key == pygame.K_DOWN:
                    tetris.tickcap = 3
                if event.key == pygame.K_z:
                    tetris.rotateRight = True
                if event.key == pygame.K_x:
                    tetris.rotateLeft = True
                if event.key == pygame.K_SPACE:
                    tetris.tickcap = 1

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT:
                    tetris.moveLeft = False
                if event.key == pygame.K_RIGHT:
                    tetris.moveRight = False
                if event.key == pygame.K_DOWN:
                    tetris.tickcap = 20
                if event.key == pygame.K_SPACE:
                    tetris.tickcap = 20
        
    def ServerInput(self, events, tetris):
        pass

class TwoPlayerController(IController):
    def GameInput(self,events,tetris):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    tetris[0].moveLeft = True
                if event.key == pygame.K_RIGHT:
                    tetris[0].moveRight = True
                if event.key == pygame.K_DOWN:
                    tetris[0].tickcap = 3
                if event.key == pygame.K_PERIOD:
                    tetris[0].rotateRight = True
                if event.key == pygame.K_COMMA:
                    tetris[0].rotateLeft = True

                if event.key == pygame.K_a:
                    tetris[1].moveLeft = True
                if event.key == pygame.K_d:
                    tetris[1].moveRight = True
                if event.key == pygame.K_s:
                    tetris[1].tickcap = 3
                if event.key == pygame.K_1:
                    tetris[1].rotateRight = True
                if event.key == pygame.K_2:
                    tetris[1].rotateLeft = True

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT:
                    tetris[0].moveLeft = False
                if event.key == pygame.K_RIGHT:
                    tetris[0].moveRight = False
                if event.key == pygame.K_DOWN:
                    tetris[0].tickcap = 20

                if event.key == pygame.K_a:
                    tetris[1].moveLeft = False
                if event.key == pygame.K_d:
                    tetris[1].moveRight = False
                if event.key == pygame.K_s:
                    tetris[1].tickcap = 20

        
    def ServerInput(self, events, tetris):
        pass
...
...
...


#####################################################
# This section contains code for the communication
# channel between possibly two Tetris game.
# SP will initialize an empty communication channel.
# MP will be connected to either local or non-local
# Server
#####################################################
...
...
...

#####################################################
#
#
#
#
#####################################################



#####################################################
# Game
#####################################################

class Game():
    def __init__(self):
        ### pygame initializing
        pygame.init()
        self.w, self.h = (300,600)
        self.sw, self.sh = (200,self.h)
        self.screen = pygame.display.set_mode((self.w+self.sw,self.h))
        self.clock = pygame.time.Clock()
        self.running = True

        StateStack.push(MainMenu())
        self.CheckNewState()

    def events(self, events):
        for event in events:
            if event.type == pygame.QUIT:
                self.running = False
                pygame.quit()
 
    def run(self):
        while self.running:
            self.clock.tick(60)
            events = pygame.event.get()
            self.events(events)
            StateStack.events(events)
            StateStack.update(1)
            StateStack.render(self.screen)
            self.CheckNewState()
            pygame.display.update()
    
    def CheckNewState(self):
        if StateStack.readstate():
            pygame.display.set_mode(StateStack.windowsize())


g = Game()
g.run()
