import sys

from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from math import atan2, pi
from sympy.matrices import Matrix

from utils.functions import load_image, random_binomial
from utils.locals import FPS, GRAVITY, FLOOR_FRICTION, STANDARD_INITIAL_FORCE
from utils import BehaviorNotAssociated
from physics.vector3 import Vector3
from physics.rect import Rect
from physics.behavior import *

class Character:
    """
    Character properties, movement, size, etc..
    """
    def __init__(self, linear_max_speed, angular_max_speed, position,
                 orientation, colors, size, max_acc, std_initial_force=None):
        self.max_speed = linear_max_speed
        self.max_rotation = angular_max_speed
        self.area = Rect((position.x, position.z), size*2, size*2)
        self.height = size*2

        # Optional, color and stuff
        self.colors = colors
        self.size = self.mass = size # For now, all characters will be
                                     # equally dense
        # Kinematic data
        self.position = position
        self.orientation = orientation
        self.velocity = Vector3()
        self.rotation = 0.
        # Steering output
        self.acceleration = Vector3()
        self.angular = 0.
        if std_initial_force is None:
            self.std_acc_step = STANDARD_INITIAL_FORCE / self.mass
        else:
            self.std_acc_step = std_initial_force / self.mass
        self.max_acc = max_acc
        self.std_ang_step = .1
        self.max_ang = 5

        # Control options
        self.jumping = False
        self.jumping_initial_speed = 13.

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
                self.acceleration = self.velocity.unit() * -FLOOR_FRICTION
            return
        if self.velocity.length < self.max_speed:
            self.acceleration += acceleration

    def update(self, game):
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

        old_velocity = self.velocity.copy()
        if self.jumping:
            self.position += self.velocity * time + \
                             (GRAVITY * time * time) / 2
            self.orientation += self.rotation * time
            self.velocity += GRAVITY * time
            if self.position.y <= 0:
                self.position.y = self.velocity.y = self.acceleration.y = 0.
                self.jumping = False
        else:
            self.position += self.velocity * time
            self.orientation += self.rotation * time
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

        self.update_position(game)
        return self

    def update_position(self, game):
        """
        Updates the position/area of a character. ensures it doesn't
        collide with some specific elements of the game.
        """
        self.area.center = (self.position.x, self.position.z)
        if not game.stage.floor.area.contains(self.area):
            print 'fuera'
            self.reset_velocity()
        # For every other character check if they are colliding
        for ch in game.characters:
            if self.area.collide_rect(ch.area) and \
                   ((self.position.y < ch.position.y + ch.height and \
                    self.position.y > ch.position.y) \
                    or \
                    (self.position.y + self.height > ch.position.y and \
                     self.position.y + self.height < ch.position.y + ch.height)):
                ch.velocity = self.reset_velocity(ch)

    def reset_velocity(self, obj=None):
        """
        Solve tridimensional calculation of velocities after a collision.
        Returns the velocity of the colliding object
        """
        class Wall(object):
            def __init__(self, position):
                self.velocity = Vector3()
                self.mass = sys.maxint
                self.position = position
        if obj is None:
            obj = Wall(position=self.position)
            
        collision_axis = (self.position - obj.position).normalize()
        self_velocity_x = self.velocity.projection(collision_axis)
        self_velocity_z = self.velocity - self_velocity_x
        obj_velocity_x  = obj.velocity.projection(collision_axis)
        obj_velocity_z  = obj.velocity - obj_velocity_x
        
        self_velocity_x = (self_velocity_x * (self.mass - obj.mass) + \
                           obj_velocity_x * 2 * obj.mass) / (self.mass + obj.mass)
        obj_velocity_x  = (self_velocity_x * 2 * self.mass + \
                           obj_velocity_x * (self.mass - obj.mass)) / \
                           (self.mass + obj.mass)
        self.velocity = self_velocity_x + self_velocity_z
        print collision_axis, self_velocity_x, self_velocity_z
        # Return obj_velocity
        return obj_velocity_x + obj_velocity_z

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
                           size=2., max_acc=20.)
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
                           size=5.8, max_acc=10.)
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
