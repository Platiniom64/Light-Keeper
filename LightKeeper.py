"""
Hello and welcome to the Light Keeper! This is a two player game where one of the two players plays on a microbit.
In order to play please connet the microbit to the computer and adapt the 'ser.port' accordingly.
The player using the mocrobit is the 'light keeper'. He can use the microbit to place light source on the screen
in order to reveal the other player on the screen. He first has to choose which colum to choose, then press the
two buttons simultaneously to select it. Afterwards if he selects the row then he will see a light source
appear on the screen where he wanted it to be placed. The other player uses awsd to move around. His goal
is to get the four keys on the board without getting reveiled by the light! He can be reveiled for few seconds
otherwise it is too hard for him. When the game start the player that plays the 'hider' has a small asvantage as everything is
dark. However, the walls are still preventing him from directly going to the light, also the light keeper will soon
place a light.
Have fun!
This project was created and finished during the Hello World Hackathon on the 08-09/02/2020
made by Vladimir Hanin and Lu Peiheng.
"""

import tkinter
import serial
import time


# * get the value form the microbit game
ser = serial.Serial(timeout=0.03)
ser.baudrate = 115200
ser.port = "COM6"
ser.open()


# * creation of the window
root = tkinter.Tk()
root.title("Light keeper")
canvasSize = 800
c = tkinter.Canvas(root, width=canvasSize, heigh=canvasSize)
c.configure(bg="white")
c.pack()

def new_winF(text): # new window definition

    newwin = tkinter.Toplevel(root)
    newwin.geometry("500x300")

    if text == "lightWon":
        text = tkinter.Text(newwin, width=50, height=40)
        text.insert(tkinter.INSERT,"Congratulations to the light keeper! You won!")
        text.pack()

    if text == "hiderWon":
        text = tkinter.Text(newwin, width=50, height=40)
        text.insert(tkinter.INSERT,"Congratulations to the hiders! You managed to get the four keys!")
        text.pack()


# ! this list collects all the rectangles that are created
listOfRect = []
class Rectangle(object):
    
    # * this function initiates the variables of the rectangle, it gives each vertex a value
    def __init__(self, x1, y1, x2, y2, colour="grey"):
        #these variables are stored for the next funciton, to update the recangle
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.colour = colour

        # top and bottom lines
        Line(x1, y1, x2, y1)
        Line(x1, y2, x2, y2)

        #left and right lines
        Line(x1, y1, x1, y2)
        Line(x2,y1, x2, y2)

        #creates the rectangle to be visible, otherwise there are only four lines
        self.shape = c.create_rectangle(x1, y1, x2, y2, fill=colour)

        #adds it to the list
        listOfRect.append(self)
    
    # * this function updates the rectangles so that they stay on top of the shadows of the lines
    def updateRec(self):
        #first we remove the previous rectangle
        c.delete(self.shape)
        #then we replace it on top of the shadows
        self.shape = c.create_rectangle(self.x1, self.y1, self.x2, self.y2, fill=self.colour)

# ! this list collects all the lines that are created
listOfLines = []
class Line(object):
    def __init__(self, x1, y1, x2, y2):
        # we first store the variables from the innit function
        self.coords = [(x1, y1), (x2, y2)]

        # we then create the line at those coordinates
        self.shape = c.create_line(x1, y1, x2, y2, fill="black")
        # we also create its shadow sothat when we update the shadow the entity exists
        self.shadow = c.create_line(-10,-10,-10,-10)

        listOfLines.append(self)

    def createShadow(self, mouseX, mouseY):
        #we first delete the shadow we created (that wasn't displayed on the screen if it is the first time)
        c.delete(self.shadow)
        
        # we begin by adding the two woordinates to the list of coordinates for the polynomial
        coordsPoly = [self.coords[1], self.coords[0]]

        # * for each coordinate of the line, we create a coordinate that extends to the end of the window to then create the polygon
        # the for loop takes the two end point of the line and get the coordinate of the window comparing that vertex.
        for vertex in self.coords:
            # this if statement checks if the mouse is on the left of the point
            if mouseX < vertex[0]:
                #this is the calculation for getting the coordinate at the side of the window
                gradient = (vertex[1] - mouseY)/(vertex[0] - mouseX)
                cornerY = gradient * canvasSize- gradient*vertex[0] + vertex[1]
                cornerX = canvasSize
                coordsPoly.append((cornerX, cornerY))

            elif mouseX > vertex[0]:
                gradient = (vertex[1] - mouseY)/(vertex[0] - mouseX)
                cornerY = gradient * 0- gradient*vertex[0] + vertex[1]
                cornerX = 0
                coordsPoly.append((cornerX, cornerY))

            # if the mouse is nor left nor right from the end point of the line, then it must be above or under
            else:
                # this checks that the mouse is rigth or left compared to the other point of the line
                if mouseX < self.coords[0][0] or mouseX < self.coords[1][0]:
                    # then we check if the mouse is under or above
                    if mouseY > self.coords[0][1]:
                        coordsPoly.append((mouseX, 0))
                        coordsPoly.append((canvasSize, 0))
                    else:
                        coordsPoly.append((mouseX, canvasSize))
                        coordsPoly.append((canvasSize, canvasSize))
                        

                elif mouseX > self.coords[0][0] or mouseX > self.coords[1][0]:
                    if mouseY > self.coords[0][1]:
                        coordsPoly.append((0, 0))
                        coordsPoly.append((mouseX, 0))
                    else:
                        coordsPoly.append((0, canvasSize))
                        coordsPoly.append((mouseX, canvasSize))

                # this means that the line is vertical
                else:
                    if mouseY > self.coords[0][1]:
                        coordsPoly.append((mouseX, 0))
                    else:
                        coordsPoly.append((mouseX, canvasSize))

                        

        # * this expands the polygon as when the line is horizontal, the shape ends on each side so these funtions extend those sothat the cover the hole window
        if coordsPoly[2][0] == 0 and coordsPoly[3][0] == canvasSize and mouseY <= self.coords[1][1]:
            coordsPoly.insert(3, (0,canvasSize))
            coordsPoly.insert(4, (canvasSize,canvasSize))
            
        if coordsPoly[2][0] == 0 and coordsPoly[3][0] == canvasSize and mouseY >= self.coords[1][1]:
            coordsPoly.insert(3, (0,0))
            coordsPoly.insert(4, (canvasSize,0))
        
        # with all these coordinates we can now create the polygon
        self.shadow = c.create_polygon(coordsPoly)

class Hidder(object):
    # initial position of the hider 
    def __init__(self):
        self.x = 400
        self.y = 400
        self.speed = 5
        self.life = 80

        self.shape = c.create_rectangle(self.x-5, self.y-5, self.x+5, self.y+5, fill="red")

    def moveUp(self):
        if (self.y - self.speed > 0) and not isWall(self.x, self.y - self.speed, self.x, self.y - self.speed):
            self.y = self.y - self.speed
            c.delete(self.shape)

            self.shape = c.create_rectangle(self.x-5, self.y-5, self.x+5, self.y+5, fill="red")

    def moveDown(self):
        if (self.y + self.speed < canvasSize) and not isWall(self.x, self.y + self.speed, self.x, self.y + self.speed):
            self.y = self.y + self.speed
            c.delete(self.shape)
            
            self.shape = c.create_rectangle(self.x-5, self.y-5, self.x+5, self.y+5, fill="red")
            

    def moveLeft(self):
        if (self.x - self.speed > 0) and not isWall(self.x - self.speed, self.y, self.x - self.speed, self.y):
            self.x = self.x - self.speed
            c.delete(self.shape)
            
            self.shape = c.create_rectangle(self.x-5, self.y-5, self.x+5, self.y+5, fill="red")

    
    def moveRight(self):
        if (self.x + self.speed < canvasSize) and not isWall(self.x + self.speed, self.y, self.x + self.speed, self.y):
            self.x = self.x + self.speed
            c.delete(self.shape)

            self.shape = c.create_rectangle(self.x-5, self.y-5, self.x+5, self.y+5, fill="red")

    def decideMove(self, i):
        if (i == 'w'):
            self.moveUp()
        elif (i == 'a' ):
            self.moveLeft()
        elif (i == 's'):
            self.moveDown()
        elif (i == 'd'):
            self.moveRight()

listOfKeys = []
class Key(object):
    def __init__(self, x1, y1, x2, y2):
        self.x1 = x1
        self.x2 = x2
        self.y1 = y1
        self.y2 = y2
        self.shape = c.create_oval(self.x1,self.y1, self.x2,self.y2,  fill="yellow")
        listOfKeys.append(self)

    def update(self):
        #first we remove the previous rectangle
        c.delete(self.shape)
        #then we replace it on top of the shadows
        self.shape = c.create_oval(self.x1, self.y1, self.x2, self.y2, fill="yellow")

playerCharacter = Hidder()

rectTOP = Rectangle(75, 0, 100, 150)
rectLEFT = Rectangle(575, 75, 725, 100)
rectBOTLEFT = Rectangle(200, 75, 400, 100)
rectRIGHT = Rectangle(475, 75, 500, 250)
rectMID = Rectangle(700, 700, 800, 725)

rectMID = Rectangle(325, 500, 350, 700)
rectMID = Rectangle(200, 200, 225, 450)
rectMID = Rectangle(0, 325, 100, 350)

rectMID = Rectangle(75, 600, 100, 800)
rectMID = Rectangle(300, 325, 500, 350)
rectMID = Rectangle(500, 475, 800, 500)

rectMID = Rectangle(700, 175, 725, 350)
rectMID = Rectangle(475, 600, 600, 625)

for line in listOfLines:
    line.createShadow(400, 330)

firstKey = Key(50,50, 60,60)
secondKey = Key(750,50, 760,60)
thirdKey = Key(750,750, 760,760)
fourthKey = Key(50,750, 60,760)


def key(event):
    playerCharacter.decideMove(event.char)
root.bind("<Key>", key)

keyGot = 0


def isWall(x1,y1,x2,y2):
    wallAHead = False
    for rect in listOfRect:
        if rect.shape in c.find_overlapping(x1,y1,x2,y2):
            wallAHead = True
    
    return wallAHead


lightCoord = []
def main(keyGot):

    lightx = str(ser.readline())

    if not lightx == "b''":
       
        lightx = lightx[2:]
        lightx = lightx.replace(" ","")
        lightx = lightx.replace("\\r\\n","")
        lightx = lightx.replace("'","")

        lightCoord.append(lightx)

    
    if len(lightCoord) == 2:

        try:
            resultx = int(lightCoord[0]) * 133
            resulty = int(lightCoord[1]) * 133
            #each time update is called, we first update the shadows of each line
            for line in listOfLines:
                line.createShadow(resultx, resulty)
            #then we update the rectangles by placing them on top of the shadows
            for rect in listOfRect:
                rect.updateRec()
            
            lightCoord.pop(1)
            lightCoord.pop(0)
        except:
            pass

    for key in listOfKeys:
        key.update()

    x1, y1, x2, y2 = c.coords(playerCharacter.shape)
    result = c.find_overlapping(x1, y1, x2, y2)

    if len(result) == 1:
        playerCharacter.life = playerCharacter.life - 1

    if playerCharacter.life == 0:
        new_winF("lightWon")
     

    for key in listOfKeys:
        if key.shape in result:
            print
            c.delete(key.shape)
            listOfKeys.remove(key)
            keyGot = keyGot + 1
    
    if keyGot == 4:
        keyGot = 2
        new_winF("hiderWon")

    root.after(1, main, keyGot)


main(keyGot)

# * start program
root.mainloop()
