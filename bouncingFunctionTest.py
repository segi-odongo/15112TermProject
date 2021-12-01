#This file is meant to test the algorithm for bouncing a ball on an angled surface
from cmu_112_graphics import *
import random,math
import numpy as np

class Ball(object):
  def __init__(self,cx,cy):
    self.cx=cx
    self.cy=cy
    randomIndex=random.randint(-12,12)
    self.dx=randomIndex
    self.dy=0
    self.hitGround=False  
  
  def bounceOffGround(self):
    self.dy=-1
    self.hitGround=True
  
  def bounceOffLine(self):
    pass
  
def appStarted(app):
    randomIndex=random.randint(1,600)
    app.ball=Ball(cx=randomIndex,cy=50)
    app.wall=((60,350),(600,200))
    app.platformerBackground = app.loadImage('oldTraffordImage.jpg')
    app.ballImage=app.loadImage('soccerBall.jpg')
    app.timeSinceCollision=0
    app.collisions=0


def timerFired(app):
    randomIndex=random.randint(1,600)
    app.timeSinceCollision+=1
    if(app.ball.cy>app.height):
        app.ball=Ball(cx=randomIndex,cy=30)
    moveBall(app)
    # printAngleOfBall(app)

def printAngleOfBall(app):
    angle=math.degrees(findAngle((0,0),(app.ball.dx,app.ball.dy)))
    print(angle)

def moveBall(app):
  app.ball.cy-=app.ball.dy
  app.ball.cx+=app.ball.dx
  if(collisionWithWall(app) and app.timeSinceCollision>3):
      app.ball.cy+=app.ball.dy
      app.ball.cx+=app.ball.dx
      app.timeSinceCollision=0
      app.ball.dx*=-0.9
  if(collision(app) and app.timeSinceCollision>3):
      app.collisions+=1
      app.timeSinceCollision=0
      colideWithWall(app)
  doGravity(app)

def collision(app):
    if(isWithinBounds(app) and isOnLine(app)):
        return True

def isWithinBounds(app):
    rightBound=max(app.wall[0][0],app.wall[1][0])
    leftBound=min(app.wall[0][0],app.wall[1][0])
    upperBound=min(app.wall[0][1],app.wall[1][1])
    lowerBound=max(app.wall[0][1],app.wall[1][1])
    if(app.ball.cx<leftBound or app.ball.cx>rightBound):
        return False
    if(app.ball.cy>lowerBound or app.ball.cy<upperBound): 
        return False
    return True

def isOnLine(app):
    epsilon=10
    point1=np.array([app.wall[0][0],app.wall[0][1]])
    point2=np.array([app.wall[1][0],app.wall[1][1]])
    point3=np.array([app.ball.cx,app.ball.cy])
    node1ToBall=point3-point1
    node1ToNode2=point2-point1
    cosineAngle=np.dot(node1ToBall,node1ToNode2)/(np.linalg.norm(node1ToBall)*np.linalg.norm(node1ToNode2))
    angleOfLine=np.arccos(cosineAngle)
    distanceToLine=math.sin(angleOfLine)*distance(app.wall[0][0],app.wall[0][1],app.ball.cx,app.ball.cy)
    if(distanceToLine<epsilon):
        return True
    return False

def distance(x0,y0,x1,y1):
    return math.sqrt((x0-x1)**2+(y0-y1)**2)

def colideWithWall(app):
    point1=app.wall[0]
    point2=app.wall[1]
    angleOfLine=findAngle(point1,point2)
    ballVec=np.array([[app.ball.dx],[app.ball.dy]])
    normalizedVec=rotateVector(ballVec,angleOfLine)
    normalizedOutputVec=rotateVector(normalizedVec,2*math.pi-2*angleOfLine)
    outputVec=rotateVector(normalizedOutputVec,-1*angleOfLine)
    app.ball.dx=int(-0.9*outputVec[0])
    app.ball.dy=int(-0.9*outputVec[1])

def rotateVector(vector,angle):
    rotationArray=np.array([[math.cos(angle),-1*math.sin(angle)],[math.sin(angle),math.cos(angle)]])
    newVec=np.matmul(rotationArray,vector)
    # print(f"originalVec={vector} \n newVec={newVec} \n angle={angle}")
    return newVec

def findAngle(point1,point2):
    slope=(point2[1]-point1[1])/(point2[0]-point1[0])
    return math.atan(slope)

def collisionWithWall(app):
    if(app.ball.cx>app.width or app.ball.cy<0
        or app.ball.cx<0):
        return True

def doGravity(app):
  app.ball.dy-=1.2

def redrawAll(app,canvas):
  drawBackground(app,canvas)
  drawBall(app,canvas)
  drawWall(app,canvas)
  drawScore(app,canvas)


def drawScore(app,canvas):
    canvas.create_text(80,40,text=f"Collisions: {app.collisions}",font="Arial 15 bold",fill="white")
def drawWall(app,canvas):
    canvas.create_line(app.wall[0][0],app.wall[0][1],app.wall[1][0],app.wall[1][1],width=5,fill="blue")
def drawBall(app,canvas):
    canvas.create_oval(app.ball.cx-20,app.ball.cy-20,app.ball.cx+20,app.ball.cy+20,fill="blue")


def drawBackground(app,canvas):
  canvas.create_image(app.width/2, app.height/2, image=ImageTk.PhotoImage(app.platformerBackground))
    
runApp(width=615, height=409)