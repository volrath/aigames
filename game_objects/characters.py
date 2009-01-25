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
    def __init__(self, linear_max_speed, angular_max_speed, position,
                 orientation, colors, size, std_acc_step, max_acc):
        self.max_speed = linear_max_speed
        self.max_rotation = angular_max_speed
        # Kinematic data
        self.position = position
        self.orientation = orientation
        self.velocity = Vector3()
        self.rotation = 0.
        # Steering output
        self.acceleration = Vector3()
        self.angular = 0.
        self.std_acc_step = std_acc_step
        self.max_acc = max_acc
        self.std_ang_step = .1
        self.max_ang = 5

        # Optional, color and stuff
        self.colors = colors
        self.size = size

    def accelerate(self, acceleration=None, deacc=False):
        """
        Acceleratios the character, given a acceleration VECTOR. This
        method ensures that the character isn't going at its maximum speed
        """
        if deacc:
            # Negative acceleration.
            if self.velocity.length == 0:
                self.acceleration.length = 0
            else:
                self.acceleration = self.velocity.unit() * -15.
            return
        if self.velocity.length < self.max_speed:
            self.acceleration += acceleration

    def update(self):
        """
        Updates the character steering data. This method only covers the
        following:
          1. updates the object's static data (position, and orientation) using
             its linear and angular velocities.
          2. updates the object's dinamic data (velocity) using its previous
             linear and angular acceleration.
          3. ensures that the maximum speed is being respected
          4. Tries to handle deceleration properly, this needs some
             improvement though =S.

        Everything else will be removed.
        """
        time = (1./FPS)
        # Check for the kinematic movements i'm doing and execute them
        if hasattr(self, 'wandering') and self.wandering:
            self.do_wander()

        self.position += self.velocity * time
#        self.orientation += self.rotation * time

        old_velocity = self.velocity.copy()
        self.velocity += self.acceleration * time
#        self.rotation += self.angular * time

        if self.velocity.length > self.max_speed:
            self.velocity.set_length(self.max_speed)
        else:
            old_velocity *= self.velocity
            if old_velocity.x < 0: self.velocity.x = 0.
            if old_velocity.y < 0: self.velocity.y = 0.
            if old_velocity.z < 0: self.velocity.z = 0.

        # get new orientation
        if self.velocity.length > 0:
            self.orientation = atan2(self.velocity.x, self.velocity.z)
        print self.velocity
        return self

    def render(self):
        """
        Draw the 3D character.
        TODO: handle blending and textures...
        """
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
    def __init__(self, max_speed, max_rotation, position=Vector3(), orientation=0.):
        Character.__init__(self, max_speed, max_rotation, position, orientation,
                           colors=[(1., 155./255, 0.), (1., 85./255, 0.)],
                           size=2., std_acc_step=1., max_acc=20.)
        #self.image, self.rect = load_image('main_character.png')

class Enemy(Character):
    """
    An enemy
    """
    def __init__(self, max_speed, max_rotation, position=Vector3(), orientation=0.):
        Character.__init__(self, max_speed, max_rotation, position, orientation,
                           colors=[(126./255, 190./255, 228./255),
                                   (39./255, 107./255, 148./255)],
                           size=1.8, std_acc_step=.5, max_acc=10.)
        # Kinematic and Steering Behaviors flag.
        self.wandering = False
        self.seeking = None
        self.evading = []
        #self.image, self.rect = load_image('main_character.png')

    def do_wander(self):
        self.velocity = vector3_from_orientation((self.orientation * 180.)/pi,
                                                 self.max_speed)
        self.rotation = random_binomial() * self.max_rotation
