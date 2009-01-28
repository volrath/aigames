"""
 Steering Behaviors.
"""

from functools import wraps
from math import pi, atan2

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
def arrive(character, target, target_radius, slow_radius, time_to_target):
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

def align(character, target, target_radius, slow_radius, time_to_target):
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

def velocity_match(character, target, time_to_target):
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
    def decorator(character, target, max_prediction, *args, **kwargs):
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

def face(character, target, *args, **kwargs):
    direction = target.position - character.position
    if direction.length == 0:
        return
    orientation_to_look = atan2(direction.x, direction.z)
    print direction, orientation_to_look
    align(character, orientation_to_look, *args, **kwargs)
