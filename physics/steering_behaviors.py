"""
 Steering Behaviors.
"""

from functools import wraps
from math import pi, atan2

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
def seek(character, target):
    """
    Character will seek a given target.
    The argument 'target' can be either a Character's instance or a simple
    position in the space.
    """
    new_acc = target - character.position
    character.acceleration = new_acc.set_length(character.std_acc_step)
    character.angular = 0.

@target_transform
def flee(character, target):
    """
    Character will flee from a given target.
    The argument 'target' can be either a Character's instance or a simple
    position in the space.
    """
    new_acc = character.position - target
    character.acceleration = new_acc.set_length(character.std_acc_step)
    character.angular = 0.

@target_transform
def arrive(character, target, target_radius=.3, slow_radius=3.5,
           time_to_target=.1):
    direction = target - character.position
    distance = direction.length
    # Are we there?
    if distance < target_radius:
        character.velocity.set_length(0.)
        character.acceleration.set_length(0.)
        return
    # Are we <slow_radius>near?
    if distance < slow_radius:
        speed = character.max_speed * distance / slow_radius
    else:
        speed = character.max_speed
    velocity = direction.set_length(speed)
    character.acceleration = (velocity - character.velocity) / time_to_target
    # Check if the acceleration is too fast
    if character.acceleration.length > character.max_acc:
        character.acceleration.set_length(character.max_acc)

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
    if hasattr(target, 'orientation'):
        target = target.orientation
    rotation_direction = target - character.orientation
    rotation_direction = map_to_range(rotation_direction) # map the result to a (-pi, pi) interval
    rotation_size = abs(rotation_direction)
    if rotation_size < target_radius:  # Are we there?
        character.rotation = 0.
        character.angular = 0.
        return
    if rotation_size < slow_radius:  # Are we near?
        rotation = character.max_rotation * rotation_size / slow_radius
    else:
        rotation = character.max_rotation
    rotation *= rotation_direction / rotation_size
    character.angular = (rotation - character.rotation) / time_to_target
    angular_acc = abs(character.angular)
    if angular_acc > character.max_ang:
        character.angular /= angular_acc
        character.angular *= character.max_ang

def look_where_you_are_going(character):
    """
    Makes the character looks where he's going.. duh
    """
    velocity = character.velocity + character.acceleration * (1./FPS)
    if velocity.length > 0:
        character.orientation = atan2(velocity.x, velocity.z)

def velocity_match(character, target, time_to_target=.1):
    """
    
    """
    character.acceleration = target.velocity - character.velocity
    character.acceleration /= time_to_target
    # Check if we are going too fast
    if character.acceleration.length > character.max_acc:
        character.acceleration.set_length(character.max_acc)
    character.angular = 0.


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
        if target.velocity.length != 0:
            basic_behavior(character,
                           target.position + (target.velocity * prediction),
                           **kwargs)
        else:
            basic_behavior(character, target, **kwargs)
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
    align(character, orientation_to_look, *args, **kwargs)

class Wander:
    def __init__(self):
        self.wander_orientation = 0;

    def execute(self, character, wander_offset=15.5, wander_radius=5.3,
                wander_rate=20.1, *args, **kwargs):
        # Updates the wander orientation
        self.wander_orientation += random_binomial() * wander_rate
        orientation = self.wander_orientation + character.orientation
        target_circle = character.position + \
                Vector3.from_orientation(character.orientation, wander_offset)
        target_circle += \
                Vector3.from_orientation(orientation, wander_radius)
        # Delegates to seek
        seek(character, target_circle, *args, **kwargs)
        look_where_you_are_going(character)
        # Set the character linear acceleration to be at full
##         character.acceleration = \
##             Vector3.from_orientation(character.orientation, character.max_acc)
