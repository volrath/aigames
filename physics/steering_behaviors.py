"""
 Steering Behaviors.
"""
import sys

from sympy.geometry import *
from functools import wraps
from math import pi, atan2, sqrt

from utils.locals import FPS
from utils.functions import random_binomial
from physics.vector3 import Vector3

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
    if target_radius is not None and new_acc.length > target_radius:
        return None
    steering['linear'] = new_acc.set_length(character.std_acc_step)
    steering['angular'] = 0.
    return steering

@target_transform
def arrive(character, target, target_radius=.3, slow_radius=3.5,
           time_to_target=.1):
    steering = {}
    direction = target - character.position
    distance = direction.length
    # Are we there?
    if distance < target_radius:
        character.velocity.set_length(0.)
        return { 'linear': Vector3(), 'angular': 0. }
    # Are we <slow_radius>near?
    if distance < slow_radius:
        speed = character.max_speed * distance / slow_radius
    else:
        speed = character.max_speed
    velocity = direction.set_length(speed)
    steering['linear'] = (velocity - character.velocity) / time_to_target
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
    Makes the character looks where he's going.. duh
    """
    if character.velocity.length > 0:
        character.orientation = atan2(character.velocity.x,
                                      character.velocity.z)

def velocity_match(character, target, time_to_target=.1):
    """
    
    """
    steering = {}
    steering['linear'] = target.velocity - character.velocity
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
    def decorator(character, target, max_prediction=.5, *args, **kwargs):
        # First calculate the target to delegate the seek
        distance = (target.position - character.position).length
        if character.velocity.length <= distance / max_prediction:
            prediction = max_prediction
        else:
            prediction = distance / character.velocity.length
        # Now we tell seek to look after a target that have a
        # position = real_target.velocity * prediction
        ## ALERT: small modification, if the target.velocity == 0 we are
        ## pursuing/evading the target itself, not some delegate target which
        ## doesn't exists.
        
        # Target radius depends on target's size
        kwargs['target_radius'] = sqrt(2 * (2*target.size) * (2*target.size))
        if target.velocity.length != 0:
            return basic_behavior(character,
                                  target.position + (target.velocity * prediction),
                                  **kwargs)
        else:
            return basic_behavior(character, target, **kwargs)
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
        self.radius = radius or 3.

    def execute(self):
        steering = {'linear': Vector3(), 'angular': 0.}
        for target in self.targets:
            if self.character == target:
                continue
            relative_pos = self.character.position - target.position
            try:
                steering['linear'] += (relative_pos * self.radius) \
                                      / relative_pos.length**2
            except ZeroDivisionError:
                steering['linear'] += (self.radius * relative_pos) / 0.01**2
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
        self.avoid_distance = avoid_distance or self.character.size + .5

    def execute(self, *args, **kwargs):
        steering = {}

        collision = self.predict_collision(self.game)
        if collision is None:
            return None

        target = collision['position'] + collision['normal'] * self.avoid_distance
        print 'returning', flee(self.character, target, 3)
        return flee(self.character, target, 3)

    def predict_collision(self, game):
        """
        """
        ray_vector = self.character.velocity.copy()
        ray_vector.set_length(self.look_ahead)
        ray_vector += self.character.position

        # Creates a sympy segment to check for intersection
        begin = Point(self.character.position.x, self.character.position.z)
        end   = Point(ray_vector.x, ray_vector.z)
        if begin == end:
            return None
        ray_seg = Segment(begin, end)
        # AND THE FANS

        # Creates a sympy polygon to check for intersections
        st = Polygon(*(map(Point, game.stage.floor.area.corners())))
        
        intersection_points = set()
        # Check for intersections with all the game's obstacles
        for obstacle in game.stage.obstacles:
            obs_area = Polygon(*(map(Point, obstacle.area.corners())))
            intersection_points.add(self.intersection_and_normal(obs_area,
                                                                 ray_seg,
                                                                 begin))
            # AND BETWEEN THE FANS
#            intersection_points.extend(intersection(obstacle, left_fan))
#            intersection_points.extend(intersection(obstacle, right_fan))

        # And dont forget the entire stage
        intersection_points.add(self.intersection_and_normal(st, ray_seg,
                                                             begin))
#        intersection_points.extend(intersection(st, left_fan))
#        intersection_points.extend(intersection(st, right_fan))

        # Removes any None in the intersection_points set
        intersection_points.remove(None)

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

    def intersection_and_normal(self, obs_area, seg, begin):
        def order_points(x, y):
            x = Point.distance(begin, x)
            y = Point.distance(begin, y)
            return cmp(x, y)
        print 'intersection between', obs_area, seg, intersection(obs_area, seg)
        points = intersection(obs_area, seg)
        points.sort(order_points)
        try:
            point = points[0]
        except IndexError: # We didn't hit this obstacle
            return None
        # search witch side of the obstacle we hit
        for i in range(0, len(obs_area.sides)):
            if intersection(obs_area.sides[i], point):
                normal = obstacle_side_normal[i]
                break
        return (point, normal)
