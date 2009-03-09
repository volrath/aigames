import sys

from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from math import atan2, pi, atan, degrees, cos, sin, radians
from sympy.matrices import Matrix

from ai.behavior import *
from game_objects.projectiles import Bullet
from game_objects.weapons import SlashWeapon, EnemyNormalWeapon
from graphics.utils import draw_circle
from utils.functions import load_image, random_binomial
from utils.exceptions import BehaviorNotAssociated
from physics.vector3 import Vector3
from physics.rect import Rect
from utils.functions import graph_quantization
from utils.locals import FPS, GRAVITY, KINETIC_FRICTION_COEFICIENT, \
     STANDARD_INITIAL_FORCE, IMPACT_ORIENTATION_UMBRAL

def hit_detection(hitter, hitted):
    """
    Returns if the hitter character hits the hitted or not.
    To find out if the hitter hits the hitted, we use the collision axis
    and the hitter velocity (where he was aiming) and calculates the
    angle between them to see if the hitter was aiming the hitted at the
    time of collision.
    """
    collision_axis = hitted.position - hitter.position
    if collision_axis.length > 0:
        collision_orientation = atan2(collision_axis.x, collision_axis.z)
    else:
        collision_orientation = hitter.orientation
    if abs(collision_orientation - hitter.orientation) < IMPACT_ORIENTATION_UMBRAL: # We hit!
        return True
    return False


class Character(object):
    """
    Character properties, movement, size, etc..
    """
    def __init__(self, linear_max_speed, angular_max_speed, position,
                 orientation, colors, size, mass, weapon, hit_force, hit_damage,
                 max_acc, std_initial_force=None):
        self.max_speed = linear_max_speed
        self.max_rotation = angular_max_speed
        self.area = Rect((position.x, position.z), size*2, size*2)
        self.radius = sqrt(2 * (size**2))
        self.height = size*2

        # Optional, color and stuff
        self.colors = colors
        self.size = size
        self.mass = mass
        self.hit_force = hit_force
        self.hit_damage = hit_damage
        # Kinematic data
        self.position = position
        self.sector_position = None
        self.orientation = orientation
        self.velocity = Vector3()
        self.rotation = 0.
        # Steering output
        self.acceleration = Vector3()
        self.behave_acceleration = Vector3()
        self.hitting_acceleration = Vector3()
        self.bullet_acceleration = Vector3()
        self.angular = 0.
        self.behave_angular = 0.
        if std_initial_force is None:
            self.std_acc_step = STANDARD_INITIAL_FORCE / self.mass
        else:
            self.std_acc_step = std_initial_force / self.mass
        self.max_acc = max_acc
        self.std_ang_step = .1
        self.max_ang = 15.

        # Control options
        self.energy = 100
        self.dying = False
        self.hitting = False
        self.shooting = False
        self.jumping = False
        self.jumping_initial_speed = 13.
        self.weapon = weapon

    def calculate_external_forces(self):
        """
        Finds forces applied to the character and adds the accelerations.
        This function really calculates accelerations, not forces. When the
        function ends, returns the resulting acceleration.
        In this function we look for the following forces:
        1. steering
        2. hit by another character (hitting or normal colliding)
        3. hit by a bullet
        4. floor friction
        """
        friction = self.velocity.unit() * -(((GRAVITY * self.mass) * KINETIC_FRICTION_COEFICIENT).length) / self.mass
        self.acceleration = (self.behave_acceleration + \
                             self.hitting_acceleration + \
                             self.bullet_acceleration + \
                             friction)

    def accelerate(self, acceleration=None, deacc=False):
        """
        Accelerates the character, given a acceleration VECTOR. This
        method ensures that the character isn't going at its maximum speed
        """
        if self.velocity.length > self.max_speed:
            self.behave_acceleration.length = 0
        else:
            self.behave_acceleration += acceleration

    def update(self, game):
        """
        Updates the character steering data. This method only covers the
        following:
          1. checks if the character is dying and returns the character
             without updating its position.
          2. checks the actual energy of the character.
          3. calculates external forces acting on the charcter to find out the
             acceleration to be used.
          4. updates the object's static data (position, and orientation) using
             its linear and angular velocities.
          5. updates the object's dinamic data (velocity) using its previous
             linear and angular acceleration.

        Everything else will be removed.
        """
        time = (1./FPS)
#        print self, self.energy

        if self.dying:
            self.position += self.velocity * time
            if abs(self.position.y) > self.size * 2:
                game.characters.remove(self)
                try:
                    game.enemies.remove(self)
                except ValueError:
                    pass
                return None
            else:
                return self

        # Check my energy
        if self.energy <= 0:
            self.die(on_stage=True) # =(
            return self

        # Updates character acceleration, based on all the force found
        # acting over itself
        self.calculate_external_forces()

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

        old_velocity *= self.velocity
        for c in range(0,3):
            if old_velocity[c] < 0:
                self.acceleration[c] = 0.
                self.velocity[c] = 0.
        return self.update_position(game)

    def update_position(self, game):
        """
        Updates the position/area of a character. checks for:
        0. resets all the forces applied to the character
        1. collisions with some specific elements of the game.
        2. hit with bullets
        3. negative Y position
        4. we're finally dead
        """
        # Reset forces
        self.hitting_acceleration.length = 0
        self.bullet_acceleration.length  = 0
        
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

        # Check for bullets hitting me
        self.check_for_bullets(game)

        # Check for negative position.y and corrects it
        if self.position.y < 0 and not self.dying:
            self.position.y = 0.
            self.velocity.y = 0.
            self.acceleration.y = 0.
        # Updates node_position using quantization
        self.node_position = graph_quantization(self.position)
        return self

    def reset_velocity(self, game, obj=None, wall=False):
        """
        Solves tridimensional calculation of velocities after a collision.
        """
        if wall:
            if (self.acceleration * self.mass).length > 3500.:
                self.die()
                self.acceleration += GRAVITY * 2
            # Has to guess with which side are we hitting
            if game.stage.floor.area.collide_point(*self.area.center):
                # If my center is still on the stage
                if game.stage.floor.size - abs(self.area.center[0]) <= \
                   game.stage.floor.size - abs(self.area.center[1]):
                    # We are closer to an horizontal edge
                    self.velocity.x *= -1
                    self.hitting_acceleration.x *= -1
                else:
                    # We are closer to an vertical edge
                    self.velocity.z *= -1
                    self.hitting_acceleration.z *= -1
            else:
                # My center is out of the stage
                self.velocity *= -1
                self.hitting_acceleration *= -1
            return

        collision_axis = (self.position - obj.position).normalize()
        self_speed_x = self.velocity.dot(collision_axis)
        obj_speed_x  = obj.velocity.dot(collision_axis)
        linear_momentum = self_speed_x*self.mass + obj_speed_x*obj.mass
        vel_reflection  = self_speed_x - obj_speed_x

        # Find the elastic collision result
        # Find velocity components vectors according to the collision axis
        self_collision_vx = self.velocity.projection(collision_axis)
        self_collision_vy = self.velocity - self_collision_vx
        obj_collision_vx  = obj.velocity.projection(collision_axis)
        obj_collision_vy  = obj.velocity - obj_collision_vx
        # Resolve equation system.
        self_new_vx = (linear_momentum - obj.mass*vel_reflection) / \
                      (self.mass + obj.mass)
        obj_new_vx  = self_speed_x - obj_speed_x + self_new_vx
        # Gets the vectors
        try:
            self_new_vx = collision_axis.copy().set_length(abs(self_new_vx)) * \
                          (self_new_vx/abs(self_new_vx))
        except ZeroDivisionError:
            self_new_vx = Vector3()
        try:
            obj_new_vx = collision_axis.copy().set_length(abs(obj_new_vx)) * \
                         (obj_new_vx/abs(obj_new_vx)) 
        except ZeroDivisionError:
            obj_new_vx = Vector3()
        # Set new velocities
        self.velocity = self_collision_vy + self_new_vx
        obj.velocity  = obj_collision_vy + obj_new_vx

        # Check for hitting
        if self.hitting and hit_detection(self, obj):
            # If i'm really hitting the 'obj' character, we'll change its mass
            # to a fuzzy mass depending on its damage
            obj.energy -= self.hit_damage
            obj_hit_acc_length = obj.hitting_acceleration.length
            obj.hitting_acceleration = obj.velocity.copy()
            try:
                obj.hitting_acceleration.set_length(obj_hit_acc_length + \
                        self.hit_force / (obj.mass * (obj.energy / 100.)))
            except ZeroDivisionError:
                obj.hitting_acceleration.set_length(obj_hit_acc_length + \
                        self.hit_force / (obj.mass * 0.0001))

        if hasattr(obj, 'hitting') and obj.hitting and hit_detection(obj, self):
            # Same as the upper if.
            self.energy -= obj.hit_damage
            try:
                hit_acc_result = obj.hit_force / (self.mass * (self.energy / 100.))
            except ZeroDivisionError:
                hit_acc_result = obj.hit_force / (self.mass * 0.0001)
            self_hitted = True
        else:
            self_hitted = False

        hit_acc_length = self.hitting_acceleration.length
        self.hitting_acceleration += self.velocity
        if self_hitted:
            self.hitting_acceleration.set_length(hit_acc_length + hit_acc_result)
        else:
            self.hitting_acceleration.set_length(hit_acc_length)

    def check_for_bullets(self, game):
        for projectile in game.projectiles:
            distance = (self.position - projectile.position).length
            if distance < self.radius + projectile.radius:
                # Oh-oh, it hit me!
                self.energy -= projectile.damage
                self.bullet_acceleration = Vector3(projectile.velocity.x, 0.,
                                                   projectile.velocity.z)
                try:
                    self.bullet_acceleration.set_length(projectile.hit_force / \
                                             (self.mass * (self.energy / 100.)))
                except ZeroDivisionError:
                    self.bullet_acceleration.set_length(projectile.hit_force / \
                                                        0.000001)
                projectile.explode(game)

    def die(self, on_stage=False):
        if self.dying:
            return # leave me alone, dying
        if on_stage:
            self.velocity += Vector3(0., -5., 0.)
        if hasattr(self, 'behaviors'):
            self.behaviors = {}
        self.dying = True

    def shoot(self):
        """
        Defines shooting.
        """
        bullet_position = \
            Vector3(self.weapon.size * sin(self.orientation) * cos(radians(self.weapon.orientation)),
                    self.weapon.size * sin(radians(self.weapon.orientation)) + self.size,
                    self.weapon.size * cos(self.orientation) * cos(radians(self.weapon.orientation)))
        bullet_velocity = bullet_position.copy()
        bullet_velocity.y -= self.size
        bullet_position += self.position
        bullet_velocity.set_length(self.weapon.shooting_force)
        bullet = self.weapon.bullet_class(position=bullet_position,
                                          velocity=bullet_velocity)
        self.shooting = False
        return bullet

    def hit(self):
        """
        Defines hitting.
        """
        self.hitting = self.weapon.hit(increase_size=1.3)

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
        self.check_energy()
        glPopMatrix()

        # Character's Radius
        draw_circle(self.position + Vector3(0., self.size, 0.), self.radius, (1., 0., 228/255.))

        # Character's weapon, if any
        if hasattr(self, 'weapon'):
            glPushMatrix()
            glTranslatef(self.position.x, self.position.y + self.size, self.position.z)
            glRotatef((self.orientation * 180. / pi), 0., 1., 0.)
            glRotatef(self.weapon.orientation, -1., 0., 0.)
            glRotatef(-90, 0., 0., 1.)
            glColor3f(*self.weapon.color)
            glutSolidCylinder(.7, self.weapon.size, 360, 50)
            glPopMatrix()

    def check_energy(self):
        """
        Renders some graphics indicating that my energy is low
        """
        if self.energy <= 20:
            std_height = self.position.y + self.size + 1.
            glColor3f(1., 0., 0.)
            glBegin(GL_LINES)
            glVertex3f(0., std_height, 0.)
            glVertex3f(0., std_height + 2., 0.)
            glEnd()
            glBegin(GL_LINES)
            glVertex3f(0., std_height, 0.)
            glVertex3f(1., std_height + 2., sin(30) * -2.)
            glEnd()
            glBegin(GL_LINES)
            glVertex3f(0., std_height, 0.)
            glVertex3f(-1., std_height + 2., sin(30) * 2.)
            glEnd()


class Slash(Character):
    """
    Super Slash object =)
    """
    def __init__(self, max_speed, max_rotation, position=Vector3(), orientation=0.):
        Character.__init__(self, max_speed, max_rotation, position, orientation,
                           colors=[(1., 155./255, 0.), (1., 85./255, 0.)],
                           size=1.2, mass=1.2, weapon=SlashWeapon(), hit_force=100.,
                           hit_damage=20., max_acc=20.)
        #self.image, self.rect = load_image('main_character.png')
        self.behavior = Behavior(character=self, active=True,
                                 **LOOK_WHERE_YOU_ARE_GOING)

    def __str__(self):
        return 'Slash'

    __repr__ = __str__

    def behave(self, game):
        # Handle hitting
        if self.hitting:
            self.hit()
            self.shooting = False
        # Handle shooting
        elif self.shooting:
            game.projectiles.append(self.shoot())
        # Behave
        self.behavior.execute()


class Enemy(Character):
    """
    An enemy
    """
    def __init__(self, max_speed, max_rotation, position=Vector3(),
                 orientation=0., behavior_groups=[]):
        Character.__init__(self, max_speed, max_rotation, position, orientation,
                           colors=[(126./255, 190./255, 228./255),
                                   (39./255, 107./255, 148./255)],
                           size=1., mass=1., weapon=EnemyNormalWeapon(),
                           hit_force=35., hit_damage=5., max_acc=48.)
        # Behaviors
        self.behaviors = dict([(bg.name, bg) for bg in behavior_groups])
        #self.image, self.rect = load_image('main_character.png')

    def __str__(self):
        return 'Enemy'

    #
    # Behaviors
    #
    def add_behavior_group(self, bg):
        self.behaviors[bg.name] = bg

    def add_behavior_in_group(self, b, bg):
        self.behaviors[bg].behavior_set[b.name] = b

    def behave(self):
        def group_priority_cmp(g1, g2):
            if g1 is None: return -1
            if g2 is None: return 1
            return cmp(g1['priority'], g2['priority'])

        self.behave_angular = 0.
        group_outputs = [group.execute() for g_name, group in self.behaviors.iteritems()]
        # Sort by priorities
        group_outputs.sort(group_priority_cmp)
        while group_outputs:
            try:
                steering = group_outputs.pop()
                if steering is not None:
#                    print steering['name']
                    steering = steering['steering']
                else:
                    continue
            except IndexError:
                continue
            # Apply to the character.
            linear  = steering.get('linear', None)
            angular = steering.get('angular', None)
            if linear is not None:
                self.behave_acceleration += linear
                if self.behave_acceleration.length > self.max_acc:
                    self.behave_acceleration.set_length(self.max_acc)
            if angular is not None:
                self.behave_angular += angular
            break
        if self.behave_acceleration.length > self.max_acc:
            self.behave_acceleration.set_length(self.max_acc)

    def attack(self, game):
        """
        Checks if i can attack a given character, giving priority to
        person-to-person attack (hitting) over long distance attack (shooting)
        """
        character = game.main_character
        distance = (character.position - self.position).length
        # Check for hitting
        if distance < character.radius + 5 and hit_detection(self, character): # FIX THIS WIRED CODE =S!
            # We hit!!!
            self.hit()
        # Check for shooting (a.k.a. predicting physics)
        # Step 0. Simulate a bullet
        bullet = self.shoot()
        # Step 1. Get landing time of the bullet
        try:
            lt = (-bullet.velocity.y + \
                  sqrt(bullet.velocity.y - 2 * GRAVITY.y * bullet.position.y)) / \
                  GRAVITY.y
            # Step 2. Get position of impact
            pix = Vector3(bullet.position.x + bullet.velocity.x * lt,
                         0.,
                         bullet.position.z + bullet.velocity.z * lt)
            # Step 3. Intersects position of impact with target's radius
            bullet_trajectory = pix - self.position
            target_direction  = (character.position + self.velocity * lt) - self.position
            min_distance = target_direction - target_direction.projection(bullet_trajectory)
            if min_distance.length < character.radius and \
               target_direction.length < bullet_trajectory.length*9.3 and \
               abs(abs(atan2(target_direction.x, target_direction.z)) - self.orientation) < pi/3:
                # We shoot!!
                game.projectiles.append(bullet)
        except ValueError:
            pass
