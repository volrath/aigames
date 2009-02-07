"""
 Steering Behaviors.
"""
import sys

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

class CollisionAvoidance:
    def __init__(self, character, target, radius=None):
        self.character = character
        self.targets = target
        self.radius = radius or 3.
        self.first_target = None

    def execute(self, *args, **kwargs):
        steering = {}
        shortest_time = sys.maxint
        first_target = None

        for target in self.targets:
            relative_pos = target.position - self.character.position
            relative_vel = target.velocity - self.character.velocity
            try:
                time_to_collision = -1* relative_pos.dot(relative_vel) \
                            / (relative_vel.length * relative_vel.length)
            except ZeroDivisionError:
                time_to_collision = 0
            if time_to_collision > 0 and time_to_collision < shortest_time:
                shortest_time = time_to_collision
            # Check if it is going to be collision at all
            min_separation = relative_pos.length - \
                             relative_vel.length * shortest_time
#            print target, ':', shortest_time, time_to_collision, min_separation
            if min_separation > 2 * self.radius:
                continue
            if time_to_collision > 0:
                first_target = target
                first_min_separation = min_separation
                first_distance = relative_pos.length
                first_relative_pos = relative_pos
                first_relative_vel = relative_vel

        # Get the steering
        if first_target is None:
            return None
        # If we are going to hit exactly, or if we are alredy colliding,
        # then do the separation based on the current position
        if first_min_separation <= 0 or first_distance < 2 * self.radius:
            relative_pos = first_target.position - self.character.position
        else:
            relative_pos = first_relative_pos + \
                           first_relative_vel * shortest_time
        relative_pos.normalize()
        # Avoid the target
        return { 'linear': relative_pos * self.character.max_acc, 'angular': 0. }
