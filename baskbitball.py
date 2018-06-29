# Baskbitball
# Made by Zenen Treadwell, June 29th 2018
# 
# A rudimentary physics simulator which employs bouncing off of round and flat
# surfaces, as well as hit detection with the net for scoring

import math
import pygame

WHITE = (0xFF,0xFF,0xFF) #These CONSTANTS are RGB representations of colours
BLACK = (0,0,0)
RED = (0xFF,0,0)
GREEN = (0,0xFF,0)
BLUE = (0,0,0xFF)

SCREEN_WIDTH = 800 # These are the CONSTANTS we use to indicate screen size
SCREEN_HEIGHT = 600

class Basketball: # This class defines all the things that the basketball can do,
                  # As well as all the information about it

    def __init__(self):
        self.sprite = pygame.image.load('ball.png') # the image we use
        self.sprite = pygame.transform.scale(self.sprite,(80,80))
        self.sprite.set_colorkey(WHITE) # the transparent background color
        self.x = 20 # X coordinate
        self.y = 20 # Y coordinate
        self.size = 80 # Diameter
        self.xvel = 0 # x component of the velocity
        self.yvel = 0 # y component of the velocity
        self.lastx = 0 # X coordinate of last frame (for throw speed)
        self.lasty = 0 # Y coordinate of last frame (for throw speed)
        self.dragging = False # is it being dragged?
        self.striking = False # is it bouncing off the mouse?

    def get_x(self): # returns the centre of the ball while changing its velocity/position

        self.lastx = self.x
        self.x += self.xvel

        if self.x > SCREEN_WIDTH-self.size:
            self.x = SCREEN_WIDTH-self.size
            self.xvel *= -0.9
        elif self.x < 0:
            self.x = 0
            self.xvel *= -0.9

        return self.x

    def get_y(self): # returns the centre of the ball while changing its velocity/position
        self.lasty = self.y
        self.yvel += 3.5
        self.y += self.yvel

        if self.y > SCREEN_HEIGHT-self.size:
            self.y = SCREEN_HEIGHT-self.size
            self.yvel *= -0.95
            if abs(self.yvel) < 4:
                self.yvel = 0

        if self.y >= SCREEN_HEIGHT-self.size and math.floor(self.yvel) <= 0:
            self.xvel *= 0.98

        return self.y

    def redirect(self, angle, force): # redirects the ball by vector
        self.xvel += force*math.cos(angle)
        self.yvel += force*math.sin(angle)

    def check_hit(self,(x_mouse,y_mouse),radius = 0): # a soft bounce (for mouse contact)
        x_centre = self.x + self.size/2
        y_centre = self.y + self.size/2
        distance = math.sqrt((x_centre-x_mouse)**2 + (y_centre-y_mouse)**2) + radius

        if distance < self.size/2:
            angle = math.atan2((y_centre-y_mouse),(x_centre-x_mouse))
            force = self.size/2 - distance
            self.redirect(angle,force)

    def is_touching(self,(x_coord,y_coord),radius = 0): # determines collision with a point
        x_centre = self.x + self.size/2
        y_centre = self.y + self.size/2
        distance = math.sqrt((x_centre-x_coord)**2 + (y_centre-y_coord)**2) + radius

        if distance < self.size/2:
            return True
        else:
            return False

    def point_bounce(self,(x_coord,y_coord),radius = 0): # bounces the ball off a point
        x_centre = self.x + self.size/2
        y_centre = self.y + self.size/2
        distance = math.sqrt((x_centre-x_coord)**2 + (y_centre-y_coord)**2) + radius

        if distance < self.size/2:
            angle = math.atan2((y_centre-y_coord),(x_centre-x_coord))
            force = math.sqrt(self.xvel**2 + self.yvel**2)
            self.xvel = 0
            self.yvel = 0
            self.redirect(angle,force)

    def rect_bounce(self,rect): # bounces the ball off of a rectangular object
        x_centre = self.x + self.size/2
        y_centre = self.y + self.size/2

        if y_centre < rect.bottom and y_centre > rect.top:
            if abs(rect.left - x_centre) < self.size/2:
                print("frontbounce")
                self.xvel = abs(self.xvel*0.9)*-1
            elif abs(rect.right - x_centre) < self.size/2:
                print("backbounce")
                self.xvel = abs(self.xvel*0.9)

    def slow(self): # slows down the ball (when it goes through the net)
        self.xvel *= 0.6
        self.yvel *= 0.7

    def drag(self,(x,y)): # snaps the ball to the mouse
        self.x = coords[0] - self.size/2
        self.y = coords[1] - self.size/2
        self.xvel = self.x - self.lastx
        self.yvel = self.y - self.lasty
        self.lastx = self.x
        self.lasty = self.y

    def collide_with_net(self,net): #manages collisions with the net
        ball.point_bounce(net.rim_front,10)
        ball.point_bounce(net.rim_back,10)
        ball.check_hit(net.rim_bridge,15)
        ball.rect_bounce(net.backboard)
        if net.netting.collidepoint(ball.x,ball.y):
            ball.slow()

    def collide_with_mouse(self,coords): # manages interactions with the mouse
        if pygame.mouse.get_pressed()[0] and pygame.mouse.get_focused():
            if self.is_touching(coords) and not self.striking:
                self.dragging = True # When this flag is true, we can drag the ball
            else:
                self.striking = True # With this, we can hit the ball with the mouse
        else:
            self.dragging = False
            self.striking = False

        if self.dragging:
            self.drag(coords)
        elif self.striking:
            self.check_hit(coords)

    def check_scoring(self, net): # Determines if the ball has gone in the net
        point1 = net.rim_front
        point2 = net.rim_back

        centre_x = self.x + self.size/2
        centre_y = self.y + self.size/2

        if centre_x > point1[0] and centre_x < point2[0]:
            if self.lasty <= point1[1] <= self.y and self.yvel > 0:
                net.updateScore()

class BasketballNet:
    
    def __init__(self, height, width):
        self.height = height
        self.width = width
        self.rim_front = (540,282)
        self.rim_back = (662,282)
        self.rim_bridge = (670,295)
        self.backboard = pygame.Rect(675,123,20,190)
        self.netting = pygame.Rect(550,282,110,90)
        self.sprite = pygame.image.load("bballnet.png")
        self.sprite = pygame.transform.scale(self.sprite,(width,height))
        self.font = pygame.font.SysFont('Comic Sans MS',30)
        self.score = 0
        self.text = self.font.render('Score: {:<5}'.format(self.score), False, (0,0,0))

    def updateScore(self): # Increases the score by one and re-renders
        self.score += 1
        self.text = self.font.render('Score: {:<5}'.format(self.score), False, (0,0,0))

pygame.init() # Initializes the pygame module
pygame.font.init() # Initializes the font submodule
size = (SCREEN_WIDTH, SCREEN_HEIGHT) # Sets the size of the screen
screen = pygame.display.set_mode(size) # Creates the game window
pygame.display.set_caption("Baskbitball") # Captions the game window
clock = pygame.time.Clock()

ball = Basketball() # creates the basketball
net = BasketballNet(500,250) # creates the net
done = False

while not done: # An infinite loop that runs with the program
    for event in pygame.event.get(): # waits for events like buttons being pressed
        if event.type == pygame.QUIT: # if the X button is pressed...
            done = True # ...set done to True and exit the while loop

    coords = pygame.mouse.get_pos() # gets the mouse coordinates as a tuple

    ball.collide_with_mouse(coords) 
    ball.collide_with_net(net)
    ball.check_scoring(net)

    screen.fill(WHITE) # creates a white background
    screen.blit(ball.sprite,(ball.get_x(),ball.get_y())) # Draws the ball
    screen.blit(net.sprite,(SCREEN_WIDTH*2/3,SCREEN_HEIGHT-net.height)) # Draws the net
    screen.blit(net.text,(10,10))
    pygame.display.flip() # Updates the screen

    clock.tick(60) # sets the pace of the game

pygame.quit() # quits the game once the above while loop ends


