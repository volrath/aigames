"""
 Steering Behaviors.
"""
import sys

from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

from functools import wraps
from math import pi, atan2, sqrt

from physics.vector3 import Vector3
from physics.geometric import *
from utils.levels import LEVEL
from utils.locals import FPS
from utils.functions import random_binomial, graph_quantization

# Basic.

def target_transform(func):
    @wraps(func)
    def decorator(character, target, *args, **kwargs):
        if hasattr(target, 'position'):
            target = target.position
        return func(character, target, *args, **kwargs)
    return decorator

@target_transform
def seek(character, target, target_radius=None):
    """
    Character will seek a given target.
    The argument 'target' can be either a Character's instance or a simple
    position in the space.
    """
    steering = {}
    new_acc = target - character.position
    if new_acc.length < 5.: return None
    steering['linear'] = new_acc.set_length(character.std_acc_step)
    steering['angular'] = 0.
    return steering

@target_transform
def flee(character, target, target_radius=None):
    """
    Character will flee from a given target.
    The argument 'target' can be either a Character's instance or a simple
    position in the space.
    """
    steering = {}
    new_acc = character.position - target
#    if target_radius is not None and new_acc.length > target_radius:
#        return None
    steering['linear'] = new_acc.set_length(character.std_acc_step)
    steering['angular'] = 0.
    return steering

@target_transform
def arrive(character, target, target_radius=.5, slow_radius=1.5,
           time_to_target=.1):
    steering = {}
    direction = target - character.position
    distance = direction.length
    # Are we there?
    if distance < target_radius:
        character.velocity.set_length(0)
        return { 'linear': Vector3(), 'angular': 0. }
    # Are we <slow_radius>near?
    if distance < slow_radius:
        speed = character.max_speed * distance / slow_radius
    else:
        speed = character.max_speed
    character.velocity.set_length(speed)
    #steering['linear'] = (velocity - character.velocity) / time_to_target
    steering['linear'] = direction / time_to_target
    # Check if the acceleration is too fast
    if steering['linear'].length > character.max_acc:
        steering['linear'].set_length(character.max_acc)
    return steering

def align(character, target, target_radius=.3, slow_radius=3.5,
          time_to_target=.1):
    """
    
    """
    def map_to_range(o):
        if o > pi:
            if o >= 0:
                return o - 2*pi
            else:
                return o + 2*pi
        else:
            return o
    steering = {}
    if hasattr(target, 'orientation'):
        target = target.orientation
    rotation_direction = target - character.orientation
    rotation_direction = map_to_range(rotation_direction) # map the result to a (-pi, pi) interval
    rotation_size = abs(rotation_direction)
    if rotation_size < target_radius:  # Are we there?
        character.rotation = 0.
        return { 'linear': Vector3(), 'angular': 0. }
    if rotation_size < slow_radius:  # Are we near?
        rotation = character.max_rotation * rotation_size / slow_radius
    else:
        rotation = character.max_rotation
    rotation *= rotation_direction / rotation_size
    steering['angular'] = (rotation - character.rotation) / time_to_target
    angular_acc = abs(steering['angular'])
    if angular_acc > character.max_ang:
        steering['angular'] /= angular_acc
        steering['angular'] *= character.max_ang
    return steering

def look_where_you_are_going(character):
    """
    Makes the character look where he's going.. duh
    """
    if character.velocity.length > 0:
        character.orientation = atan2(character.velocity.x,
                                      character.velocity.z)

def velocity_match(character, target, time_to_target=.1, radius=14.):
    """
    The character tries to match the velocity of a list of targets
    Note: parameter 'target' represents a list of targets
    """
    steering = {'linear': Vector3(), 'angular': 0.}
    vel_center_mass = Vector3()
    weight = 0
    
    for boid in target:
        if boid == character: continue
        relative_pos = boid.position - character.position
        relative_vel = boid.velocity - character.velocity
        if relative_pos.length > radius: continue
        vel_center_mass += boid.velocity
        weight += 1
    if weight == 0:
        return None
    vel_center_mass /= weight
    
    steering['linear'] = vel_center_mass - character.velocity
    steering['linear'] /= time_to_target
    # Check if we are going too fast
    if steering['linear'].length > character.max_acc:
        steering['linear'].set_length(character.max_acc)
    steering['angular'] = 0.
    return steering


# Advanced.

def pursue_evade(basic_behavior):
    """
    
    """
    @wraps(basic_behavior)
    def decorator(character, target, characters_sight=None, max_prediction=1.,
                  *args, **kwargs):
        global LEVEL
        # First calculate the target to delegate the seek
        if hasattr(target, 'position'):
            distance = (target.position - character.position).length
        else:
            distance = (target - character.position).length
        if characters_sight is not None and distance > characters_sight:
            return None
        if character.velocity.length <= distance / max_prediction:
            prediction = max_prediction
        else:
            prediction = distance / character.velocity.length

        # Now we tell seek to look after a target that have a
        # position = real_target.velocity * prediction
        ## ALERT: small modification, if the target.velocity == 0 we are
        ## pursuing/evading the target itself, not some delegate target which
        ## doesn't exists.
        if hasattr(target, 'velocity') and target.velocity.length != 0:
            target_node = graph_quantization(target.position + \
                                             (target.velocity * prediction))
        else:
            if hasattr(target, 'position'):
                target_node = graph_quantization(target.position)
            else:
                target_node = graph_quantization(target)
        a_result = LEVEL['a_star'].get_route(character.node_position.id, target_node.id)
#        print 'pursuing', a_result['path'], target_node.id
        try:
            node = LEVEL['nodes'][a_result['path'][1]]
        except IndexError:
            return None
        return basic_behavior(character, node.location, **kwargs)
    return decorator

pursue          = pursue_evade(seek)
pursue_and_stop = pursue_evade(arrive)
evade           = pursue_evade(flee)

@target_transform
def face(character, target, *args, **kwargs):
    direction = target - character.position
    if direction.length == 0:
        return
    orientation_to_look = atan2(direction.x, direction.z)
    return align(character, orientation_to_look, *args, **kwargs)

class Wander:
    def __init__(self, character, wander_offset=5.5, wander_radius=5.3,
                 wander_rate=20.1, target=None):
        self.character = character
        self.wander_offset = wander_offset
        self.wander_radius = wander_radius
        self.wander_rate = wander_rate
        self.wander_orientation = 0

    def execute(self, *args, **kwargs):
        steering = {}
        # Updates the wander orientation
        self.wander_orientation += random_binomial() * self.wander_rate
        orientation = self.wander_orientation + self.character.orientation
        target_circle = self.character.position + \
            Vector3.from_orientation(self.character.orientation, self.wander_offset)
        target_circle += \
                Vector3.from_orientation(orientation, self.wander_radius)
        # Delegates to seek
        look_where_you_are_going(self.character)
        return seek(self.character, target_circle, *args, **kwargs)
        
        # Set the character linear acceleration to be at full
##         steering['linear'] = \
##             Vector3.from_orientation(character.orientation, character.max_acc)

class Separation:
    def __init__(self, character, target, radius=None):
        self.character = character
        self.targets = target
        self.radius = radius or character.size + 3.

    def execute(self):
        steering = {'linear': Vector3(), 'angular': 0.}
        for target in self.targets:
            if self.character == target:
                continue
            relative_pos = self.character.position - target.position
            if relative_pos.length > self.radius: continue
            try:
                steering['linear'] += (relative_pos * self.radius) \
                                      / relative_pos.length**2
            except ZeroDivisionError:
                steering['linear'] += (self.radius * relative_pos) / 0.01**2
        return steering

class Cohesion:
    def __init__(self, character, target, radius=None):
        self.character = character
        self.targets = target
        self.radius = radius or self.character.size + 16.

    def execute(self):
        steering = {'linear': Vector3(), 'angular': 0.}
        center_mass = Vector3()
        weight = 0
        for target in self.targets:
            if target == self.character: continue
            relative_pos = target.position - self.character.position
            if relative_pos.length > self.radius: continue
            center_mass += target.position
            weight += 1
        if weight == 0:
            return None
        center_mass /= weight
        steering['linear'] = center_mass - self.character.position
        steering['linear'].set_length(self.character.max_speed)
#        steering['linear'] -= self.character.velocity
        return steering

obstacle_side_normal = {
    0: Vector3(0., 0., -1.),
    1: Vector3(-1., 0., 0.),
    2: Vector3(0., 0., 1.),
    3: Vector3(1., 0., 0.),
}

class ObstacleAvoidance:
    def __init__(self, character, game, look_ahead, fan_angle=None,
                 fan_size=None, avoid_distance=None, target=None):
        self.character = character
        self.game = game
        self.look_ahead = look_ahead
        self.fan_angle = fan_angle or pi/4.
        self.fan_size  = fan_size or sqrt(2 * self.character.size**2) + .5
        self.avoid_distance = avoid_distance or self.character.size + 2.5

    def execute(self, *args, **kwargs):
        steering = {}

        collision = self.predict_collision(self.game)
        if collision is None:
            return None
        
        target = collision['position'] + collision['normal'] * self.avoid_distance
        return flee(self.character, target)

    def predict_collision(self, game):
        """
        """
        ray_vector = self.character.velocity.copy()
        ray_vector.set_length(self.look_ahead)
        ray_vector += self.character.position

        # Creates a sympy segment to check for intersection
        begin = self.character.position.x, self.character.position.z
        end   = ray_vector.x, ray_vector.z
        if begin == end:
            return None
        ray_seg = begin, end
        # AND THE FANS

        # printing ray_segments
        glPushMatrix()
        glTranslatef(0., 0., 0.)
        glColor3f(0., 1., 0.)
        glBegin(GL_LINES)
        glVertex3f(begin[0], self.character.size, begin[1])
        glVertex3f(end[0], self.character.size, end[1])
        glEnd()
        glPopMatrix()

        # Creates a sympy polygon to check for intersections
        stage_sides = game.stage.floor.area.sides()
        
        intersection_points = set()
        # Check for intersections with all the game's obstacles
        for obstacle in game.stage.obstacles:
            obs_area_sides = obstacle.area.sides()
            intersection_points.add(self.intersection_and_normal(obs_area_sides,
                                                                 ray_seg,
                                                                 begin))
            # AND BETWEEN THE FANS
#            intersection_points.extend(intersection(obstacle, left_fan))
#            intersection_points.extend(intersection(obstacle, right_fan))

        # And dont forget the entire stage
        intersection_points.add(self.intersection_and_normal(stage_sides,
                                                             ray_seg, begin))
#        intersection_points.extend(intersection(st, left_fan))
#        intersection_points.extend(intersection(st, right_fan))

        # Removes any None in the intersection_points set
        try:
            intersection_points.remove(None)
        except KeyError:
            pass

        # Order the points according to its distance to character.position
        def order_collisions(x, y):
            x = Point.distance(begin, x[0])
            y = Point.distance(begin, y[0])
            return cmp(x, y)
        intersection_points = list(intersection_points)
        intersection_points.sort(order_collisions)
        try:
            intersection = intersection_points[0]
        except IndexError:
            return None
        return {
            'position': Vector3(intersection[0][0], 0., intersection[0][1]),
            'normal': intersection[1],
        }

    def intersection_and_normal(self, obs_sides, seg, begin):
        """
        Returns the closest point of collision and its normal
        """
        def order_points(x, y):
            x = Point.distance(begin, x)
            y = Point.distance(begin, y)
            return cmp(x, y)
        points = self.intersect_obstacle(obs_sides, seg)
        points.sort(order_points)
        try:
            point = points[0]
        except IndexError: # We didn't hit this obstacle
            return None

        # search which side of the obstacle we hit
        if abs(obs_sides[0][0][0]) != abs(point[0]) and \
           abs(obs_sides[0][0][0]) != abs(point[1]):
            if abs(obs_sides[0][0][0]) - abs(point[0]) < \
               abs(obs_sides[0][0][0]) - abs(point[1]):
                point = (abs(obs_sides[0][0][0]) * (point[0] / abs(point[0])), point[1])
            else:
                point = (point[0], abs(obs_sides[0][0][0]) * (point[1] / abs(point[1])))
        normal = self.character.velocity.copy()
        normal.normalize()
        normal *= -1
        for i in range(0, len(obs_sides)):
            if Point.is_between(point, obs_sides[i]):
                normal = obstacle_side_normal[i]
                break
        return (point, normal)

    def intersect_obstacle(self, obstacle_sides, seg):
        """
        Returns a list of all intersections with the sides of an obstacle
        """
        intersections = []
        for side in obstacle_sides:
            intersections.extend(self.intersect_segments(side, seg))
        return intersections

    def intersect_segments(self, seg1, seg2):
        """
        Returns the point of intersection between two segments, if any
        """
        d = (seg1[0][0] - seg1[1][0]) * (seg2[0][1] - seg2[1][1]) - \
            (seg1[0][1] - seg1[1][1]) * (seg2[0][0] - seg2[1][0])
        if d == 0:
            return []
        xi = ((seg2[0][0] - seg2[1][0]) * (seg1[0][0]*seg1[1][1] - seg1[0][1]*seg1[1][0]) - \
              (seg1[0][0] - seg1[1][0]) * (seg2[0][0]*seg2[1][1] - seg2[0][1]*seg2[1][0])) / d
        yi = ((seg2[0][1] - seg2[1][1]) * (seg1[0][0]*seg1[1][1] - seg1[0][1]*seg1[1][0]) - \
              (seg1[0][1] - seg1[1][1]) * (seg2[0][0]*seg2[1][1] - seg2[0][1]*seg2[1][0])) / d
        if xi < min(seg1[0][0], seg1[1][0]) or \
           xi > max(seg1[0][0], seg1[1][0]) or \
           xi < min(seg2[0][0], seg2[1][0]) or \
           xi > max(seg2[0][0], seg2[1][0]):
            return []
        if seg1[0][0] == seg1[1][0] and (yi > max(seg1[0][1], seg1[1][1]) or \
                                         yi < min(seg1[0][1], seg1[1][1])):
            return []
        if seg2[0][0] == seg2[1][0] and (yi > max(seg2[0][1], seg2[1][1]) or \
                                         yi < min(seg2[0][1], seg2[1][1])):
            return []
        return [(xi, yi)]
           
