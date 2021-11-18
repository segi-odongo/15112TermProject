import threading
import mediapipe as mp
import math,random,copy
from cmu_112_graphics import *
from dataclasses import make_dataclass
import cv2
from threading import Thread

mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_pose = mp.solutions.pose

class Ball(object):
  def __init__(self,cx,cy):
    self.cx=cx
    self.cy=cy
    self.dx=0
    self.dy=0
    self.hitGround=False
  
  def bounceOffGround(self):
    self.dy=-1
    self.hitGround=True
  


def appStarted(app):
  #Threading
  app.bodyLandmarks=None
  app.lowerBodyCoords=[]
  app.upperBodyCoords=[]
  app.platformerBackground = app.loadImage('oldTraffordImage.jpg')
  app.headCenter=[]
  app.ball=Ball(cx=int(app.width*(5/6)),cy=30)
  app.ballImage=app.loadImage('soccerBall.jpg')
  app.score=0

def cameraFired(app):
  cap = cv2.VideoCapture(0)
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


def collision(app):
  cx,cy=app.ball.cx,app.ball.cy
  epislon=distance(app.lowerBodyCoords[0][0],app.lowerBodyCoords[0][1],app.lowerBodyCoords[2][0],app.lowerBodyCoords[2][1])
  for r in app.lowerBodyCoords:
    if(distance(r[0],r[1],cx,cy)<epislon):
      break
  lineEndPoints=ballOnLine(app)
  if(lineEndPoints):
    app.ball.bounceOffLine(app,lineEndPoints)

def ballOnLine(app):
  pass
  

def distance(x0,y0,x1,y1):
  return math.sqrt((x0-x1)**2+(y0-y1)**2)
  
def extractLowerBodyCoords(app):
  lowerBodyCoords=[23,24,25,26,27,28,29,30,31,32]
  result=[]
  for s in lowerBodyCoords:
    result.append(s)
  return result


def extractUpperBodyCoords(app):
  result=[0]
  for i in range(11,23):
    result.append(i)
  return result

def doGravity(app):
  app.ball.dy-=1.2

def moveBall(app):
  app.ball.cy-=app.ball.dy
  app.ball.cx+=app.ball.dx

def timerFired(app):
  
  if(app.ball.cy>app.height):
    app.ball=Ball(cx=int(app.width*(5/6)),cy=30)
  
  if(app.bodyLandmarks):
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
    doGravity(app)
    if(collision(app)):
      app.score+=1
    

def redrawAll(app,canvas):
  canvas.create_rectangle(100,100,200,200)
  # app.drawCamera(canvas)
  #Test Code for line betweeen Knees
  # if(len(app.lowerBodyCoords)>0):
  #   canvas.create_line(app.lowerBodyCoords[2][0],app.lowerBodyCoords[2][1],app.lowerBodyCoords[3][0],app.lowerBodyCoords[3][1],fill="red",width=10)
  drawBackground(app,canvas)
  if(len(app.lowerBodyCoords)>0):
    drawLowerBody(app,canvas)
    drawUpperBody(app,canvas)
    drawHead(app,canvas)
    drawBall(app,canvas)
  

def drawBall(app,canvas):
  canvas.create_image(app.ball.cx,app.ball.cy,image=ImageTk.PhotoImage(app.ballImage))


  
def drawHead(app,canvas):
  lineWidth=10
  cx,cy=app.upperBodyCoords[0]
  radius=abs(app.upperBodyCoords[1][1]-cy)
  canvas.create_oval(cx-radius,cy-radius,cx+radius,cy+radius,width=lineWidth,outline='black')
  drawSmileyFace(app,canvas,cx,cy,radius)
  
#Drawing the face
def drawSmileyFace(app,canvas,cx,cy,radius):
  pass


def drawBackground(app,canvas):
  canvas.create_image(app.width/2, app.height/2, image=ImageTk.PhotoImage(app.platformerBackground))


def drawLowerBody(app,canvas):
  lineWidth=10
  #Draw Waist Line
  canvas.create_line(app.lowerBodyCoords[0][0],app.lowerBodyCoords[0][1],app.lowerBodyCoords[1][0],app.lowerBodyCoords[1][1],fill="black",width=lineWidth)


############################################################################
  # #Draw Left Leg
###########################################################################

#Upper Leg
  canvas.create_line(app.lowerBodyCoords[0][0],app.lowerBodyCoords[0][1],app.lowerBodyCoords[2][0],app.lowerBodyCoords[2][1],fill="black",width=lineWidth)

#Lower Leg
  canvas.create_line(app.lowerBodyCoords[2][0],app.lowerBodyCoords[2][1],app.lowerBodyCoords[4][0],app.lowerBodyCoords[4][1],fill="black",width=lineWidth)

#Foot
  canvas.create_line(app.lowerBodyCoords[4][0],app.lowerBodyCoords[4][1],app.lowerBodyCoords[8][0],app.lowerBodyCoords[8][1],fill="black",width=lineWidth)
  canvas.create_line(app.lowerBodyCoords[4][0],app.lowerBodyCoords[4][1],app.lowerBodyCoords[6][0],app.lowerBodyCoords[6][1],fill="black",width=lineWidth)
  canvas.create_line(app.lowerBodyCoords[8][0],app.lowerBodyCoords[8][1],app.lowerBodyCoords[6][0],app.lowerBodyCoords[6][1],fill="black",width=lineWidth)

###########################################################################
  # #Draw Right Leg
###########################################################################
#Upper Leg
  canvas.create_line(app.lowerBodyCoords[1][0],app.lowerBodyCoords[1][1],app.lowerBodyCoords[3][0],app.lowerBodyCoords[3][1],fill="black",width=lineWidth)

#Lower Leg
  canvas.create_line(app.lowerBodyCoords[3][0],app.lowerBodyCoords[3][1],app.lowerBodyCoords[5][0],app.lowerBodyCoords[5][1],fill="black",width=lineWidth)

#Foot
  canvas.create_line(app.lowerBodyCoords[5][0],app.lowerBodyCoords[5][1],app.lowerBodyCoords[9][0],app.lowerBodyCoords[9][1],fill="black",width=lineWidth)
  canvas.create_line(app.lowerBodyCoords[5][0],app.lowerBodyCoords[5][1],app.lowerBodyCoords[7][0],app.lowerBodyCoords[7][1],fill="black",width=lineWidth)
  canvas.create_line(app.lowerBodyCoords[9][0],app.lowerBodyCoords[9][1],app.lowerBodyCoords[7][0],app.lowerBodyCoords[7][1],fill="black",width=lineWidth)


def drawUpperBody(app,canvas):
  lineWidth=10
  #Torso
  canvas.create_line(app.upperBodyCoords[1][0],app.upperBodyCoords[1][1],app.upperBodyCoords[2][0],app.upperBodyCoords[2][1],fill="black",width=lineWidth)
  canvas.create_line(app.lowerBodyCoords[1][0],app.lowerBodyCoords[1][1],app.upperBodyCoords[2][0],app.upperBodyCoords[2][1],fill="black",width=lineWidth)
  canvas.create_line(app.lowerBodyCoords[0][0],app.lowerBodyCoords[0][1],app.upperBodyCoords[1][0],app.upperBodyCoords[1][1],fill="black",width=lineWidth)
  
  ###########################################################################
  # #Draw Left Arm
  ###########################################################################
  #Upper Arm
  canvas.create_line(app.upperBodyCoords[1][0],app.upperBodyCoords[1][1],app.upperBodyCoords[3][0],app.upperBodyCoords[3][1],fill="black",width=lineWidth)

  #Lower Arm
  canvas.create_line(app.upperBodyCoords[5][0],app.upperBodyCoords[5][1],app.upperBodyCoords[3][0],app.upperBodyCoords[3][1],fill="black",width=lineWidth)

  #Right Hand
  canvas.create_line(app.upperBodyCoords[5][0],app.upperBodyCoords[5][1],app.upperBodyCoords[7][0],app.upperBodyCoords[7][1],fill="black",width=lineWidth)
  canvas.create_line(app.upperBodyCoords[7][0],app.upperBodyCoords[7][1],app.upperBodyCoords[9][0],app.upperBodyCoords[9][1],fill="black",width=lineWidth)
  canvas.create_line(app.upperBodyCoords[5][0],app.upperBodyCoords[5][1],app.upperBodyCoords[9][0],app.upperBodyCoords[9][1],fill="black",width=lineWidth)
  canvas.create_line(app.upperBodyCoords[5][0],app.upperBodyCoords[5][1],app.upperBodyCoords[11][0],app.upperBodyCoords[11][1],fill="black",width=lineWidth)

###########################################################################
  # #Draw Right Arm
###########################################################################
#Upper Arm
  canvas.create_line(app.upperBodyCoords[2][0],app.upperBodyCoords[2][1],app.upperBodyCoords[4][0],app.upperBodyCoords[4][1],fill="black",width=lineWidth)

  #Lower Arm
  canvas.create_line(app.upperBodyCoords[6][0],app.upperBodyCoords[6][1],app.upperBodyCoords[4][0],app.upperBodyCoords[4][1],fill="black",width=lineWidth)

  #Right Hand
  canvas.create_line(app.upperBodyCoords[6][0],app.upperBodyCoords[6][1],app.upperBodyCoords[8][0],app.upperBodyCoords[8][1],fill="black",width=lineWidth)
  canvas.create_line(app.upperBodyCoords[8][0],app.upperBodyCoords[8][1],app.upperBodyCoords[10][0],app.upperBodyCoords[10][1],fill="black",width=lineWidth)
  canvas.create_line(app.upperBodyCoords[6][0],app.upperBodyCoords[6][1],app.upperBodyCoords[10][0],app.upperBodyCoords[10][1],fill="black",width=lineWidth)
  canvas.create_line(app.upperBodyCoords[6][0],app.upperBodyCoords[6][1],app.upperBodyCoords[12][0],app.upperBodyCoords[12][1],fill="black",width=lineWidth)


runApp(width=615, height=409)