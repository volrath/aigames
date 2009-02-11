import sys

from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from math import atan2, pi, atan, degrees, cos, sin, radians
from sympy.matrices import Matrix

from game_objects.projectiles import Bullet
from utils.functions import load_image, random_binomial
from utils.locals import FPS, GRAVITY, FLOOR_FRICTION, STANDARD_INITIAL_FORCE
from utils import BehaviorNotAssociated
from physics.vector3 import Vector3
from physics.rect import Rect
from physics.behavior import *

class Character(object):
    """
    Character properties, movement, size, etc..
    """
    def __init__(self, linear_max_speed, angular_max_speed, position,
                 orientation, colors, size, max_acc, std_initial_force=None):
        self.max_speed = linear_max_speed
        self.max_rotation = angular_max_speed
        self.area = Rect((position.x, position.z), size*2, size*2)
        self.radius = sqrt(2 * (size**2))
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
        self.max_ang = 15.

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
            if self.velocity.length <= 0:
                self.velocity = Vector3()
                self.acceleration = Vector3()
            else:
                self.acceleration = self.velocity.unit() * -FLOOR_FRICTION
            return
        self.acceleration += acceleration
        if self.velocity.length > self.max_speed:
            self.velocity.set_length(self.max_speed)

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
            self.position += self.velocity * time + (GRAVITY * time * time) / 2
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
        old_velocity *= self.velocity
        if old_velocity.x < 0: self.velocity.x = 0.
        if old_velocity.y < 0: self.velocity.y = 0.
        if old_velocity.z < 0: self.velocity.z = 0.
        self.update_position(game)
        return self

    def update_position(self, game):
        """
        Updates the position/area of a character. ensures it doesn't
        collide with some specific elements of the game.
        """
        self.area.center = (self.position.x, self.position.z)
        if not game.stage.floor.area.contains(self.area):
            self.reset_velocity(game=game, wall=True)
        # For every stage obstacle
        for obstacle in game.stage.obstacles:
            distance = (self.position - obstacle.position).length
            if distance < self.radius + obstacle.radius and \
               self.position.y < obstacle.height:
                self.reset_velocity(game=game, obj=obstacle)
        # For every other character check if they are colliding
        for ch in game.characters:
            if ch == self:
                continue
            distance = (self.position - ch.position).length
            if distance < self.radius + ch.radius and \
               self.position.y < ch.position.y + ch.height and \
               ch.position.y < self.position.y + self.height:
                self.reset_velocity(game=game, obj=ch)
        # Check for negative position.y and corrects it
        if self.position.y < 0:
            self.position.y = 0.
            self.velocity.y = 0.
            self.acceleration.y = 0.
        return self

    def reset_velocity(self, game, obj=None, wall=False):
        """
        Solve tridimensional calculation of velocities after a collision.
        """
        if wall:
            # Has to guess with which side are we hitting
            if game.stage.floor.area.collide_point(*self.area.center):
                # If my center is still on the stage
                if game.stage.floor.size - abs(self.area.center[0]) <= \
                   game.stage.floor.size - abs(self.area.center[1]):
                    # We are closer to an horizontal edge
                    self.velocity.x *= -1
                    self.acceleration.x *= -1
                else:
                    # We are closer to an vertical edge
                    self.velocity.z *= -1
                    self.acceleration.z *= -1
            else:
                # My center is out of the stage
                self.velocity *= -1
                self.acceleration *= -1
            return

        relative_pos = self.position - obj.position # x_diff & y_diff
        if relative_pos.x > 0:
            angle = degrees(atan(relative_pos.z/relative_pos.x))
            if relative_pos.z < 0:
                angle *= 1
            vel_x = -self.velocity.length * cos(radians(angle))
            vel_z = -self.velocity.length * sin(radians(angle))
        elif relative_pos.x < 0:
            angle = degrees(atan(relative_pos.z/relative_pos.x))
            if relative_pos.z < 0:
                angle += -180
            else:
                angle += 180
            vel_x = -self.velocity.length * cos(radians(angle))
            vel_z = -self.velocity.length * sin(radians(angle))
        elif relative_pos.x == 0:
            if relative_pos.z > 0:
                angle = -90
            else:
                angle = 90
            vel_x = self.velocity.length * cos(radians(angle))
            vel_z = self.velocity.length * sin(radians(angle))
        elif relative_pos.z == 0:
            if relative_pos.x < 0:
                angle = 0
            else:
                angle = 180
            vel_x = self.velocity.length * cos(radians(angle))
            vel_z = self.velocity.length * sin(radians(angle))
        self.velocity.set(vel_x, self.velocity.y, -vel_z)
        acc_length = self.acceleration.length / 2.
        self.acceleration = self.velocity.copy()
        self.acceleration.set_length(acc_length)

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

        # Character area
        glPushMatrix()
        glTranslatef(0.,0.,0.)
        glColor3f(0.0,1.0,0.0)
        glBegin(GL_LINES)
        glVertex3f(self.area.top_left[0], 2.0, self.area.top_left[1])
        glVertex3f(self.area.top_right[0], 2.0, self.area.top_right[1])
        glEnd()
        glBegin(GL_LINES)
        glVertex3f(self.area.top_left[0], 2.0, self.area.top_left[1])
        glVertex3f(self.area.bottom_left[0], 2.0, self.area.bottom_left[1])
        glEnd()
        glBegin(GL_LINES)
        glVertex3f(self.area.top_right[0], 2.0, self.area.top_right[1])
        glVertex3f(self.area.bottom_right[0], 2.0, self.area.bottom_right[1])
        glEnd()
        glBegin(GL_LINES)
        glVertex3f(self.area.bottom_left[0], 2.0, self.area.bottom_left[1])
        glVertex3f(self.area.bottom_right[0], 2.0, self.area.bottom_right[1])
        glEnd()
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
        self.behavior = Behavior(character=self, active=True,
                                 **LOOK_WHERE_YOU_ARE_GOING)
        self.canon = 45
        self.shooting_force = 20.
        self.shoot = False

    def __str__(self):
        return 'Slash'

    __repr__ = __str__

    def behave(self, game):
        # Handle shooting
        if self.shoot:
            bullet_position = Vector3(4. * sin(self.orientation) * cos(radians(self.canon)),
                                      4. * sin(radians(self.canon)) + self.size,
                                      4. * cos(self.orientation) * cos(radians(self.canon)))
            bullet_velocity = bullet_position.copy()
            bullet_velocity.y -= self.size
            bullet_position += self.position
            bullet_velocity.set_length(self.shooting_force)
            bullet = Bullet(position=bullet_position, velocity=bullet_velocity,
                            radius=1.)
            game.projectiles.append(bullet)
            self.shoot = False
        # Behave
        self.behavior.execute()

    def render(self, *args, **kwargs):
        # Slash weapon
        glPushMatrix()
        glTranslatef(self.position.x, self.size, self.position.z)
        glRotatef((self.orientation * 180. / pi), 0., 1., 0.)
        glRotatef(self.canon, -1., 0., 0.)
        glRotatef(-90, 0., 0., 1.)
        glColor3f(1., 234/255., 0.)
        glutSolidCylinder(1., 4., 360, 50)
        glPopMatrix()
        super(Slash, self).render(**kwargs)

class Enemy(Character):
    """
    An enemy
    """
    def __init__(self, max_speed, max_rotation, position=Vector3(),
                 orientation=0., behavior_groups=[]):
        Character.__init__(self, max_speed, max_rotation, position, orientation,
                           colors=[(126./255, 190./255, 228./255),
                                   (39./255, 107./255, 148./255)],
                           size=1.8, max_acc=80.)
        # Behaviors
        self.behaviors = set(behavior_groups)

        #self.image, self.rect = load_image('main_character.png')

    def __str__(self):
        return 'Enemy'

    #
    # Behaviors
    #
    def add_behavior_group(self, bg):
        self.behaviors.add(bg)

    def add_behavior_in_group(self, b, bg):
        group = None
        for g in self.behaviors:
            if g.name == bg:
                group = g
                break
        if group is not None:
            group.behavior_set.add(b)

    def behave(self):
        def group_priority_cmp(g1, g2):
            if g1 is None: return -1
            if g2 is None: return 1
            if g1['priority'] > g2['priority']:
                return 1
            elif g1['priority'] == g2['priority']:
                return 0
            else: # <
                return -1
        group_outputs = [group.execute() for group in self.behaviors]
        # Sort by priorities
        group_outputs.sort(group_priority_cmp)
        while not group_outputs == []:
            try:
                steering = group_outputs.pop()
                if steering is not None:
                    print steering['name']
                    steering = steering['steering']
                else:
                    continue
            except IndexError:
                continue
            # Apply to the character.
            linear  = steering.get('linear', None)
            angular = steering.get('angular', None)
            if linear is not None:
                if linear.length > self.max_acc:
                    linear.set_length(self.max_acc)
                self.acceleration += linear
            if angular is not None:
                self.angular += angular
            break

