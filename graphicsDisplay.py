#This is the main file which runs the soccer game
import mediapipe as mp
import math,random,copy,time

from numpy.lib.function_base import angle
from cmu_112_graphics import *
import cv2
import numpy as np

mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_pose = mp.solutions.pose

class Ball(object):
  def __init__(self,cx,cy):
    self.cx=cx
    self.cy=cy
    self.dx=0
    self.dy=0
    self.r=5
    self.hitGround=False  
  
  def bounceOffGround(self):
    self.dy=-1
    self.hitGround=True
  
  def bounceOffLine(self):
    pass
  
lowerBodyGraph=dict()
lowerBodyGraph[0]={1,2}
lowerBodyGraph[1]={0,3}
lowerBodyGraph[2]={0,4}
lowerBodyGraph[3]={1,5}
lowerBodyGraph[4]={2,6,8}
lowerBodyGraph[5]={3,7,9}
lowerBodyGraph[6]={8,4}
lowerBodyGraph[7]={9,5}
lowerBodyGraph[8]={4,6}
lowerBodyGraph[9]={7,5}


def appStarted(app):
  #openCV Landmark Variables
  app.bodyLandmarks=None
  app.lowerBodyCoords=[]
  app.upperBodyCoords=[]

  #Backgrounds
  app.oldTraffordBackground = (app.loadImage('oldTraffordImage.jpg'),"Old Trafford")
  app.santiagoBernabeauBackground=(app.loadImage('santiagoBernabeuImage.jpg'),"Santiago Bernabeu")
  app.allianzArenaBackground=(app.loadImage('allianzArenaImage.jpg'),"Allianz Arena")
  app.neoQuimicaBackground=(app.loadImage('neoQuimicaImage.jpg'), "Neo Quimica Arena")
  app.anfieldBackground=(app.loadImage('anfieldImage.jpg'),"Anfield")
  app.background=app.oldTraffordBackground

  #Creates the head cx and cy
  app.headCenter=[]

  #Creates ball that is juggled
  randomIndex=random.randint(1,1150)
  app.ball=Ball(cx=randomIndex,cy=30)
  app.score=0

  #Dictionary that maps each node to every connecting node it has
  app.dictOfLines=lowerBodyGraph

  app.timeSinceCollision=0
  app.timerDelay=0

  #Game Mode Variables
  app.welcomeScreen=True
  app.inGame=False
  app.gameOver=False
  app.inSettings=False
  app.difficulty="Easy"
  app.gravity=1.2
  app.bounceSpeed=1

  #List for balls that fall during animation
  app.balls=[]



#Goes through all of the openCV functions each camerafired
def cameraFired(app):
  if(app.inGame):
    #If statement loop cited from: https://google.github.io/mediapipe/solutions/pose.html
    cap = app.camera
    with mp_pose.Pose(
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5) as pose:
      success, image = cap.read()
      if not success:
        print("Ignoring empty camera frame.")
        # If loading a video, use 'break' instead of 'continue'.
      else:
        # To improve performance, optionally mark the image as not writeable to
        # pass by reference.
        image.flags.writeable = False
        model_complexity=0
        enable_segmentation=True
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = pose.process(image)
        # Draw the pose annotation on the image.
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        mp_drawing.draw_landmarks(
            image,
            results.pose_landmarks,
            mp_pose.POSE_CONNECTIONS,
            landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style())

        #Extracting Landmark Values and storing them to app.bodyLandmarks
        try:
          app.bodyLandmarks=results.pose_landmarks.landmark
        except:
          pass
        app.frame=cv2.flip(image,1)


################################################
#Colision Detection Functions#
################################################
def collisionWithLeg(app):
  cx,cy=app.ball.cx,app.ball.cy
  epislon=distance(app.lowerBodyCoords[0][0],app.lowerBodyCoords[0][1],app.lowerBodyCoords[2][0],app.lowerBodyCoords[2][1])
  for r in app.lowerBodyCoords:
    if(distance(r[0],r[1],cx,cy)<epislon):
      break
  lineEndPoints=ballOnLine(app)
  return lineEndPoints

#Checks which limb the ball just hit
def ballOnLine(app):
  for node in app.dictOfLines:
    for connection in app.dictOfLines[node]:
      if(isBetweenPoints(app,node,connection) and isOnLine(app,node,connection)):
        return node,connection
  return

#Checks if the ball is within the bounds of the slope of a line
def isOnLine(app,node1,node2):
  #strictness of collision(angle in degrees)
  epsilon=60
  point1=np.array([app.lowerBodyCoords[node1][0],app.lowerBodyCoords[node1][1]])
  point2=np.array([app.lowerBodyCoords[node2][0],app.lowerBodyCoords[node2][1]])
  point3=np.array([app.ball.cx,app.ball.cy])
  node1ToBall=point3-point1
  node1ToNode2=point2-point1
  cosineAngle=np.dot(node1ToBall,node1ToNode2)/(np.linalg.norm(node1ToBall)*np.linalg.norm(node1ToNode2))
  angleOfLine=np.arccos(cosineAngle)
  distanceToLine=math.sin(angleOfLine)*distance(app.lowerBodyCoords[node1][0],app.lowerBodyCoords[node1][1],app.ball.cx,app.ball.cy)
  if(distanceToLine<epsilon):
    return True
  return False
  
  
#Checks if a ball is within the bounding box two points
def isBetweenPoints(app,node1,node2):
  rightBound=max(app.lowerBodyCoords[node1][0],app.lowerBodyCoords[node2][0])
  leftBound=min(app.lowerBodyCoords[node1][0],app.lowerBodyCoords[node2][0])
  upperBound=min(app.lowerBodyCoords[node1][1],app.lowerBodyCoords[node2][1])
  lowerBound=max(app.lowerBodyCoords[node1][1],app.lowerBodyCoords[node2][1])
  if(app.ball.cx<leftBound or app.ball.cx>rightBound):
    return False
  if(app.ball.cy>lowerBound or app.ball.cy<upperBound): 
    return False
  return True

#Checks if there is a collision with the wall
def collisionWithWall(app):
  if(app.ball.cx+40>app.width or app.ball.cx-40<0):
    return True
  return False


########################################################################
########################################################################

#Distance between two points helper function
def distance(x0,y0,x1,y1):
  return math.sqrt((x0-x1)**2+(y0-y1)**2)
  
#Places the lower body coordinates into a list of indexes
def extractLowerBodyCoords(app):
  lowerBodyCoords=[23,24,25,26,27,28,29,30,31,32]
  result=[]
  for s in lowerBodyCoords:
    result.append(s)
  return result

#Places the upper body coordinates into a list of indexes
def extractUpperBodyCoords(app):
  result=[0]
  for i in range(11,23):
    result.append(i)
  return result

#Changes the y velocity of the ball being kicked
def doGravity(app):
  app.ball.dy-=app.gravity
  for b in app.balls:
    b.dy-=1.2

#Moves the ball which is being kicked by the player
def moveBall(app):
  app.ball.cy-=app.ball.dy
  app.ball.cx+=app.ball.dx
  if(collisionWithWall(app) and app.timeSinceCollision>30):
      app.ball.cy+=app.ball.dy
      app.ball.cx+=app.ball.dx
      app.timeSinceCollision=0
      app.ball.dx*=-0.9
  doGravity(app)


def timerFired(app):
  if(app.welcomeScreen):
    randomIndex=random.randint(1,1150)
    newBall=Ball(cx=randomIndex,cy=0)
    app.balls.append(newBall)
    moveBalls(app)
    removeBalls(app)
  else:
    app.balls=[]
  app.timeSinceCollision+=1
  if(app.ball.cy>app.height):
    app.gameOver=True
    app.inGame=False
    randomIndex=random.randint(1,1150)
    app.ball=Ball(cx=randomIndex,cy=30)
  if(app.bodyLandmarks and app.inGame):
    #Setting LowerBody Coordinates
    lowerBodyCoords=extractLowerBodyCoords(app)
    app.lowerBodyCoords=[]
    for i in lowerBodyCoords:
      tempCord=(app.width-app.bodyLandmarks[i].x*app.width,app.bodyLandmarks[i].y*app.height)
      app.lowerBodyCoords.append(tempCord)
    #Setting UpperBody Coordinates
    upperBodyCoords=extractUpperBodyCoords(app)
    app.upperBodyCoords=[]
    for i in upperBodyCoords:
      tempCord=(app.width-app.bodyLandmarks[i].x*app.width,app.bodyLandmarks[i].y*app.height)
      app.upperBodyCoords.append(tempCord)
    moveBall(app)
    linePoints=collisionWithLeg(app)
    if(linePoints and app.timeSinceCollision):
      app.score+=1
      colideWithWall(app,linePoints[0],linePoints[1])

#Moves the balls in the welcome screen
def moveBalls(app):
  for b in app.balls:
    b.cy-=b.dy
    b.cx-=b.dx
  doBallsGravity(app)

#Removes the balls which fall off the screen
def removeBalls(app):
  for b in app.balls:
    if(b.cy>app.height):
      app.balls.remove(b)

#Adds changing velocity to the balls at the start
def doBallsGravity(app):
  for b in app.balls:
    b.dy-=1.2
  
  
#Checks for key presses which change the game mode
def keyPressed(app,event):
  if(app.welcomeScreen):
    if(event.key=="Space"):
      app.welcomeScreen=False
      app.inGame=True
    if(event.key=="s"):
      app.inSettings=True
      app.welcomeScreen=False
  if(app.gameOver):
    if(event.key=="r"):
      app.inGame=True
      app.gameOver=False
      app.score=0
    if(event.key=="s"):
      app.gameOver=False
      app.inSettings=True
  if(app.inSettings):
    if(event.key=="q"):
      app.welcomeScreen=True
      app.inSettings=False
    if(event.key=="d"):
      toggleDifficulty(app)
    if(event.key=="b"):
      toggleBackground(app)
  
def toggleDifficulty(app):
  if(app.difficulty=="Easy"):
    app.difficulty="Medium"
    app.gravity=2.3
    app.bounceSpeed=1.2
  elif(app.difficulty=="Medium"):
    app.difficulty="Hard"
    app.gravity=5.2
    app.bounceSpeed=1.4
  elif(app.difficulty=="Hard"):
    app.difficulty="Easy"
    app.gravity=1.2
    app.bounceSpeed=1.5

def toggleBackground(app):
  if(app.background[1]=="Old Trafford"):
    app.background=app.santiagoBernabeauBackground
  elif(app.background[1]=="Santiago Bernabeu"):
    app.background=app.allianzArenaBackground
  elif(app.background[1]=="Allianz Arena"):
    app.background=app.neoQuimicaBackground
  elif(app.background[1]=="Neo Quimica Arena"):
    app.background=app.anfieldBackground
  elif(app.background[1]=="Anfield"):
    app.background=app.oldTraffordBackground


#Changes the vector of the ball after it colides with leg
def colideWithWall(app,node1,node2):
    point1=(app.lowerBodyCoords[node1][0],app.lowerBodyCoords[node1][1])
    point2=(app.lowerBodyCoords[node2][0],app.lowerBodyCoords[node2][1])
    angleOfLine=findAngle(point1,point2)
    ballVec=np.array([[app.ball.dx],[app.ball.dy]])
    normalizedVec=rotateVector(ballVec,angleOfLine)
    normalizedOutputVec=rotateVector(normalizedVec,2*math.pi-2*angleOfLine)
    outputVec=rotateVector(normalizedOutputVec,-1*angleOfLine)
    app.ball.dx=int(-1*outputVec[0])*app.bounceSpeed
    app.ball.dy=int(-1*outputVec[1])*app.bounceSpeed

#Used in calculating the return vector angle
def rotateVector(vector,angle):
    rotationArray=np.array([[math.cos(angle),-1*math.sin(angle)],[math.sin(angle),math.cos(angle)]])
    newVec=np.matmul(rotationArray,vector)
    return newVec

#Finds the angle between two points
def findAngle(point1,point2):
    slope=(point2[1]-point1[1])/(point2[0]-point1[0])
    return math.atan(slope)
    

    
#Contains all of the drawing funcitons
def redrawAll(app,canvas):
  print(app.difficulty)
  # app.drawCamera(canvas)
  #Test Code for line betweeen Knees
  # if(len(app.lowerBodyCoords)>0):
  #   canvas.create_line(app.lowerBodyCoords[2][0],app.lowerBodyCoords[2][1],app.lowerBodyCoords[3][0],app.lowerBodyCoords[3][1],fill="red",width=10)
  if(app.inGame):
    drawBackground(app,canvas)
    if(len(app.lowerBodyCoords)>0):
      drawLowerBody(app,canvas)
      drawUpperBody(app,canvas)
      drawHead(app,canvas)
      drawBall(app,canvas)
    drawScore(app,canvas)
  if(app.welcomeScreen):
    drawWelcomeScreen(app,canvas)
  if(app.gameOver):
    drawGameOver(app,canvas)
  if(app.inSettings):
    drawSettings(app,canvas)

def drawSettings(app,canvas):
  drawBackground(app,canvas)
  canvas.create_text(app.width//2,app.height//6,text=f"Difficulty is currently at {app.difficulty} press d to toggle",font="Arial 30 bold",fill="blue violet")
  canvas.create_text(app.width//2,app.height//3,text=f"Current stadium backgorund is {app.background[1]} press b to toggle", font="Arial 30 bold",fill="blue violet")
  canvas.create_text(app.width//6,app.height//10,text="press q to return to welcome screen",font="Arial 20 bold",fill="blue violet")

#Draws the game over screen
def drawGameOver(app,canvas):
  drawBackground(app,canvas)
  canvas.create_text(app.width//5,app.height//5,text="press s for settings",font="Arial 30 bold",fill="white")
  canvas.create_text(app.width//2,app.height//2,text="Game Over",font="Arial 90 bold",fill="white")
  canvas.create_text(app.width//2,app.height//2+50,text="press r to restart",font="Arial 30 bold",fill="white")
  canvas.create_text(app.width//2,app.height//2+80,text=f"Score: {app.score}",font="Arial 30 bold",fill="white")

#Draws the initial welcome screen
def drawWelcomeScreen(app,canvas):
  drawBackground(app,canvas)
  canvas.create_text(app.width//2,app.height//2,text="Welcome to Real Soccer!",font="Arial 90 bold",fill="white")
  canvas.create_text(app.width//2,app.height//2+50,text="press space to begin",font="Arial 30 bold",fill="white")
  canvas.create_text(app.width//5,app.height//5,text="press s for settings",font="Arial 30 bold",fill="white")
  drawFallingBalls(app,canvas)

#Draws the balls that fall during the welcome screen
def drawFallingBalls(app,canvas):
  for b in app.balls:
    canvas.create_oval(b.cx-b.r,b.cy-b.r,b.cx+b.r,b.cy+b.r,fill="white")

#Draws the score in the top left
def drawScore(app,canvas):
    canvas.create_text(80,40,text=f"Score: {app.score}",font="Arial 15 bold",fill="white")
  
#Draws the ball which is being juggled by the player
def drawBall(app,canvas):
  canvas.create_oval(app.ball.cx-40,app.ball.cy-40,app.ball.cx+40,app.ball.cy+40,fill="white")


#Draws the players head
def drawHead(app,canvas):
  lineWidth=20
  cx,cy=app.upperBodyCoords[0]
  radius=abs(app.upperBodyCoords[1][1]-cy)
  canvas.create_oval(cx-radius,cy-radius,cx+radius,cy+radius,width=lineWidth,outline='blue violet')

#Draws the head of the player
def drawBackground(app,canvas):
  canvas.create_image(app.width/2, app.height/2, image=ImageTk.PhotoImage(app.background[0]))

#Draws the entire lower body
def drawLowerBody(app,canvas):
  lineWidth=20

  #Draw Waist Line
  canvas.create_line(app.lowerBodyCoords[0][0],app.lowerBodyCoords[0][1],app.lowerBodyCoords[1][0],app.lowerBodyCoords[1][1],fill="blue violet",width=lineWidth)


############################################################################
  # #Draw Left Leg
###########################################################################

#Upper Leg
  canvas.create_line(app.lowerBodyCoords[0][0],app.lowerBodyCoords[0][1],app.lowerBodyCoords[2][0],app.lowerBodyCoords[2][1],fill="blue violet",width=lineWidth)

#Lower Leg
  canvas.create_line(app.lowerBodyCoords[2][0],app.lowerBodyCoords[2][1],app.lowerBodyCoords[4][0],app.lowerBodyCoords[4][1],fill="blue violet",width=lineWidth)

#Foot
  canvas.create_line(app.lowerBodyCoords[4][0],app.lowerBodyCoords[4][1],app.lowerBodyCoords[8][0],app.lowerBodyCoords[8][1],fill="blue violet",width=lineWidth)
  canvas.create_line(app.lowerBodyCoords[4][0],app.lowerBodyCoords[4][1],app.lowerBodyCoords[6][0],app.lowerBodyCoords[6][1],fill="blue violet",width=lineWidth)
  canvas.create_line(app.lowerBodyCoords[8][0],app.lowerBodyCoords[8][1],app.lowerBodyCoords[6][0],app.lowerBodyCoords[6][1],fill="blue violet",width=lineWidth)

###########################################################################
  # #Draw Right Leg
###########################################################################
#Upper Leg
  canvas.create_line(app.lowerBodyCoords[1][0],app.lowerBodyCoords[1][1],app.lowerBodyCoords[3][0],app.lowerBodyCoords[3][1],fill="blue violet",width=lineWidth)

#Lower Leg
  canvas.create_line(app.lowerBodyCoords[3][0],app.lowerBodyCoords[3][1],app.lowerBodyCoords[5][0],app.lowerBodyCoords[5][1],fill="blue violet",width=lineWidth)

#Foot
  canvas.create_line(app.lowerBodyCoords[5][0],app.lowerBodyCoords[5][1],app.lowerBodyCoords[9][0],app.lowerBodyCoords[9][1],fill="blue violet",width=lineWidth)
  canvas.create_line(app.lowerBodyCoords[5][0],app.lowerBodyCoords[5][1],app.lowerBodyCoords[7][0],app.lowerBodyCoords[7][1],fill="blue violet",width=lineWidth)
  canvas.create_line(app.lowerBodyCoords[9][0],app.lowerBodyCoords[9][1],app.lowerBodyCoords[7][0],app.lowerBodyCoords[7][1],fill="blue violet",width=lineWidth)


def drawUpperBody(app,canvas):
  lineWidth=20
  #Torso
  canvas.create_line(app.upperBodyCoords[1][0],app.upperBodyCoords[1][1],app.upperBodyCoords[2][0],app.upperBodyCoords[2][1],fill="blue violet",width=lineWidth)
  canvas.create_line(app.lowerBodyCoords[1][0],app.lowerBodyCoords[1][1],app.upperBodyCoords[2][0],app.upperBodyCoords[2][1],fill="blue violet",width=lineWidth)
  canvas.create_line(app.lowerBodyCoords[0][0],app.lowerBodyCoords[0][1],app.upperBodyCoords[1][0],app.upperBodyCoords[1][1],fill="blue violet",width=lineWidth)
  
  ###########################################################################
  # #Draw Left Arm
  ###########################################################################
  #Upper Arm
  canvas.create_line(app.upperBodyCoords[1][0],app.upperBodyCoords[1][1],app.upperBodyCoords[3][0],app.upperBodyCoords[3][1],fill="blue violet",width=lineWidth)

  #Lower Arm
  canvas.create_line(app.upperBodyCoords[5][0],app.upperBodyCoords[5][1],app.upperBodyCoords[3][0],app.upperBodyCoords[3][1],fill="blue violet",width=lineWidth)

  #Right Hand
  canvas.create_line(app.upperBodyCoords[5][0],app.upperBodyCoords[5][1],app.upperBodyCoords[7][0],app.upperBodyCoords[7][1],fill="blue violet",width=lineWidth)
  canvas.create_line(app.upperBodyCoords[7][0],app.upperBodyCoords[7][1],app.upperBodyCoords[9][0],app.upperBodyCoords[9][1],fill="blue violet",width=lineWidth)
  canvas.create_line(app.upperBodyCoords[5][0],app.upperBodyCoords[5][1],app.upperBodyCoords[9][0],app.upperBodyCoords[9][1],fill="blue violet",width=lineWidth)
  canvas.create_line(app.upperBodyCoords[5][0],app.upperBodyCoords[5][1],app.upperBodyCoords[11][0],app.upperBodyCoords[11][1],fill="blue violet",width=lineWidth)

###########################################################################
  # #Draw Right Arm
###########################################################################
#Upper Arm
  canvas.create_line(app.upperBodyCoords[2][0],app.upperBodyCoords[2][1],app.upperBodyCoords[4][0],app.upperBodyCoords[4][1],fill="blue violet",width=lineWidth)

  #Lower Arm
  canvas.create_line(app.upperBodyCoords[6][0],app.upperBodyCoords[6][1],app.upperBodyCoords[4][0],app.upperBodyCoords[4][1],fill="blue violet",width=lineWidth)

  #Right Hand
  canvas.create_line(app.upperBodyCoords[6][0],app.upperBodyCoords[6][1],app.upperBodyCoords[8][0],app.upperBodyCoords[8][1],fill="blue violet",width=lineWidth)
  canvas.create_line(app.upperBodyCoords[8][0],app.upperBodyCoords[8][1],app.upperBodyCoords[10][0],app.upperBodyCoords[10][1],fill="blue violet",width=lineWidth)
  canvas.create_line(app.upperBodyCoords[6][0],app.upperBodyCoords[6][1],app.upperBodyCoords[10][0],app.upperBodyCoords[10][1],fill="blue violet",width=lineWidth)
  canvas.create_line(app.upperBodyCoords[6][0],app.upperBodyCoords[6][1],app.upperBodyCoords[12][0],app.upperBodyCoords[12][1],fill="blue violet",width=lineWidth)


runApp(width=1200, height=900)