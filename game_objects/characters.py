from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from math import atan2, pi

from utils.functions import load_image, random_binomial,\
     vector3_from_orientation
from utils.locals import FPS
from physics.vector3 import Vector3

class Character:
    """
    Character properties, movement, size, etc..
    """
    def __init__(self, linear_max_speed, angular_max_speed, colors, size, std_acc):
        self.lms = linear_max_speed
        self.ams = angular_max_speed
        # Kinematic data
        self.position = Vector3()
        self.orientation = 0.
        self.velocity = Vector3()
        self.rotation = 0.
        # Steering output
        self.acceleration = Vector3()
        self.angular = 0.
        self.std_acc = std_acc

        # Optional, color and stuff
        self.colors = colors
        self.size = size

    def accelerate(self, acceleration=None, deacc=False):
        """
        Acceleration to slash, given a acceleration VECTOR. This
        method ensures that slash isn't going at its maximum speed
        """
        if deacc:
            # Negative acceleration.
            if self.velocity.length == 0:
                self.acceleration.length = 0
            else:
                self.acceleration = self.velocity.unit() * -15.
            return
        if self.velocity.length < self.lms:
            self.acceleration += acceleration

    def update(self, deacc=False):
        time = (1./FPS)
        # Check for the kinematic movements i'm doing and execute them
        if hasattr(self, 'wandering') and self.wandering:
            self.do_wander()

        self.position += self.velocity * time
        self.orientation += self.rotation * time
        new_velocity = self.velocity + self.acceleration * time
        old_velocity = self.velocity
        if new_velocity.length > self.lms:
            self.velocity.set_length(self.lms)
        else:
            self.velocity = new_velocity
            if new_velocity.x * old_velocity.x < 0: self.velocity.x = 0.
            if new_velocity.y * old_velocity.y < 0: self.velocity.y = 0.
            if new_velocity.z * old_velocity.z < 0: self.velocity.z = 0.
        #self.rotation += self.angular * time

        # get new orientation
##         if self.velocity.length > 0:
##             self.orientation = atan2(self.velocity.x, self.velocity.z)
        print self.velocity
        return self

    def render(self):
        glPushMatrix()
        glTranslatef(self.position.x, self.size, self.position.z)
        glRotatef((self.orientation * 180. / pi), 0., 1., 0.)
        #solidCube(self.size)    -> to implement...
        glBegin(GL_QUADS)
        
	glColor3f(*self.colors[0])		# Set The Color To Primary Character Color
	glVertex3f( self.size, self.size, self.size)		# Top Right Of The Quad (Front)
	glVertex3f(-self.size, self.size, self.size)		# Top Left Of The Quad (Front)
	glVertex3f(-self.size,-self.size, self.size)		# Bottom Left Of The Quad (Front)
	glVertex3f( self.size,-self.size, self.size)		# Bottom Right Of The Quad (Front)

	glColor3f(*self.colors[1])			# Set The Color To Secondary Character Color
	glVertex3f( self.size, self.size,-self.size)		# Top Right Of The Quad (Top)
	glVertex3f(-self.size, self.size,-self.size)		# Top Left Of The Quad (Top)
	glVertex3f(-self.size, self.size, self.size)		# Bottom Left Of The Quad (Top)
	glVertex3f( self.size, self.size, self.size)		# Bottom Right Of The Quad (Top)

	glVertex3f( self.size, self.size,-self.size)		# Top Right Of The Quad (Back)
	glVertex3f(-self.size, self.size,-self.size)		# Top Left Of The Quad (Back)
	glVertex3f(-self.size,-self.size,-self.size)		# Bottom Left Of The Quad (Back)
	glVertex3f( self.size,-self.size,-self.size)		# Bottom Right Of The Quad (Back)

	glVertex3f(-self.size, self.size, self.size)		# Top Right Of The Quad (Left)
	glVertex3f(-self.size, self.size,-self.size)		# Top Left Of The Quad (Left)
	glVertex3f(-self.size,-self.size,-self.size)		# Bottom Left Of The Quad (Left)
	glVertex3f(-self.size,-self.size, self.size)		# Bottom Right Of The Quad (Left)

	glVertex3f( self.size, self.size, self.size)		# Top Right Of The Quad (Right)
	glVertex3f( self.size, self.size,-self.size)		# Top Left Of The Quad (Right)
	glVertex3f( self.size,-self.size,-self.size)		# Bottom Left Of The Quad (Right)
	glVertex3f( self.size,-self.size, self.size)		# Bottom Right Of The Quad (Right)

	glEnd()				# Done Drawing The Quad
        glPopMatrix()

class Slash(Character):
    """
    Super Slash object =)
    """
    def __init__(self, lms, ams):
        Character.__init__(self, lms, ams, colors=[(1., 155./255, 0.), (1., 85./255, 0.)], size=2., std_acc=1.)
        #self.image, self.rect = load_image('main_character.png')

class Enemy(Character):
    """
    An enemy
    """
    def __init__(self, lms, ams):
        Character.__init__(self, lms, ams, colors=[(126./255, 190./255, 228./255), (39./255, 107./255, 148./255)], size=1.5, std_acc=.2)
        # Kinematic and Steering Behaviors flag.
        self.wandering = False
        self.seeking = None
        self.evading = []
        #self.image, self.rect = load_image('main_character.png')

    def do_wander(self):
        self.velocity = vector3_from_orientation((self.orientation * 180.)/pi,
                                                 self.lms)
        self.rotation = random_binomial() * self.ams
