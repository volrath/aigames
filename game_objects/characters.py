from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from math import atan2, pi

from utils.functions import load_image, random_binomial
from utils.locals import FPS, GRAVITY
from utils import BehaviorNotAssociated
from physics.vector3 import Vector3
from physics.rect import Rect
from physics.behavior import *

class Character:
    """
    Character properties, movement, size, etc..
    """
    def __init__(self, linear_max_speed, angular_max_speed, position,
                 orientation, colors, size, std_acc_step, max_acc):
        self.max_speed = linear_max_speed
        self.max_rotation = angular_max_speed
        self.area = Rect(position.x-size*2, position.z-size*2, size*2, size*2)
        self.height = size*2
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

        # Control options
        self.jumping = False
        self.jumping_initial_speed = 30.

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

        if self.jumping:
            self.acceleration += GRAVITY
            self.position += self.velocity * time + ((self.acceleration + GRAVITY) * time * time) / 2
            print self.velocity, self.position
            if self.position.y <= 0:
                self.position.y = self.velocity.y = 0.
                self.acceleration -= GRAVITY
                self.jumping = False
        else:
            self.position += self.velocity * time
        self.orientation += self.rotation * time

        old_velocity = self.velocity.copy()
        self.velocity += self.acceleration * time
        self.rotation += self.angular * time

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

#        print self.velocity
        return self

    def update_position(self, stage):
        self.area.left = self.position.x
        self.area.top  = self.position.z
        if not stage.move_dup(self.size, self.size).inflate_dup(-self.size, -self.size).contains(self.area):
            self.area.left = self.position.x = \
                self.position.x - Vector3.from_orientation(self.orientation, 25*(1./FPS)).x
            self.area.top = self.position.z = \
                self.position.z - Vector3.from_orientation(self.orientation, 25*(1./FPS)).z
            self.velocity.length = 0

    def jump(self):
        self.jumping = True
        self.velocity.y = self.jumping_initial_speed

    def render(self):
        """
        Draw the 3D character.
        TODO: handle blending and textures...
        """
        glPushMatrix()
        glTranslatef(self.position.x, self.size + self.position.y, self.position.z)
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
    def __init__(self, max_speed, max_rotation, position=Vector3(),
                 orientation=0., behaviors=[]):
        Character.__init__(self, max_speed, max_rotation, position, orientation,
                           colors=[(126./255, 190./255, 228./255),
                                   (39./255, 107./255, 148./255)],
                           size=1.8, std_acc_step=.5, max_acc=10.)
        # Kinematic and Steering Behaviors flag.
        self.wandering = False
        self.seeking = None
        self.evading = []
        # Behaviors
        try:
            self.current_behavior = behaviors[0]
        except IndexError:
            self.current_behavior = None
        self.behaviors = set(behaviors)

        #self.image, self.rect = load_image('main_character.png')

    #
    # Behaviors
    #
    def _set_current_behavior(self, b):
        """ Sets the current behavior of this character """
        if b in self.behaviors:
            self.current_behavior = b
        else:
            raise BehaviorNotAssociated()
    def _get_current_behavior(self):
        """ Gets the current behavior of this character """
        return self.current_behavior
    behavior = property(_get_current_behavior, _set_current_behavior, None,
                        "Current behavior of this character")

    def add_behavior(self, b):
        self.behaviors.add(b)
        if len(self.behaviors) == 1:
            self.current_behavior = b
