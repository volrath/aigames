from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from math import atan2, pi

from utils import load_image, FPS
from vector3 import Vector3

class Character:
    """
    Character properties, movement, size, etc..
    """
    def __init__(self, linear_max_speed, angular_max_speed):
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

class Slash(Character):
    """
    Super Slash object =)
    """
    def __init__(self, lms, ams):
        Character.__init__(self, lms, ams)
        #self.image, self.rect = load_image('main_character.png')
        self.size = 2. # static, for now...
        self.std_acc = 1

    def accelerate(self, acceleration=None, deacc=False):
        """
        Acceleration to slash, given a acceleration VECTOR. This
        method ensures that slash isn't going at its maximum speed
        """
        if deacc:
            # Negative acceleration.
            if self.velocity.length = 0:
                self.acceleration.length = 0
            else:
                self.acceleration = self.velocity.unit() * -12.
            return
        if self.velocity.length < self.lms:
            self.acceleration += acceleration

    def update(self, deacc=False):
        time = (1./FPS)
        self.position += self.velocity * time
        #self.orientation += self.rotation * time
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
        if self.velocity.length > 0:
            self.orientation = atan2(-self.velocity.x, self.velocity.y)
        print self.orientation
        return self

    def render(self):
        # 255 153 0 #FF9900
        # 255  85 0 #FF5500
        glPushMatrix()
        glTranslatef(self.position.x, self.size, self.position.z)
        glRotatef((self.orientation * 180. / pi), 0., 1., 0.)
        #solidCube(self.size)    -> to implement...
        glBegin(GL_QUADS)
        
	glColor3f(1., 153./255, 0.)		# Set The Color To Light Orange
	glVertex3f( self.size, self.size, self.size)		# Top Right Of The Quad (Front)
	glVertex3f(-self.size, self.size, self.size)		# Top Left Of The Quad (Front)
	glVertex3f(-self.size,-self.size, self.size)		# Bottom Left Of The Quad (Front)
	glVertex3f( self.size,-self.size, self.size)		# Bottom Right Of The Quad (Front)

	glColor3f(1., 85./255, 0.)			# Set The Color To Dark Orange
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
