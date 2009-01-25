"""
 Steering Behaviors.
"""

# Basic.

def seek(character, target):
    new_acc = target.position - character.position
    character.acceleration = new_acc.set_length(character.std_acc_step)
    character.angular = 0.

def flee(character, target):
    new_acc = character.position - target.position
    character.acceleration = new_acc.set_length(character.std_acc_step)
    character.angular = 0.

def arrive(character, target, target_radius, slow_radius, time_to_target):
    direction = target.position - character.position
    distance = direction.length
    # Are we there?
    if distance < target_radius:
        character.velocity.set_length(0.)
        character.acceleration.set_length(0.)
        return
    # Are we <slow_radius>near?
    if distance < slow_radius:
        speed = character.lms * distance / slow_radius
    else:
        speed = character.lms
    velocity = direction.set_length(speed)
    character.acceleration = (velocity - character.velocity) / time_to_target
    # Check if the acceleration is too fast
    if character.acceleration.length > character.max_acc:
        character.acceleration.set_length(character.max_acc)

def align(character, target, target_radius, slow_radius, time_to_target):
    rotation_direction = target.orientation - character.orientation
    #rotation_direction = map_to_range(rotation_direction) # map the result to a (-pi, pi) interval
    rotation_size = abs(rotation_direction)
    if rotation_size < target_radius:  # Are we there?
        character.rotation = 0.
        character.angular = 0.
        return
    if rotation_size < slow_radius:  # Are we near?
        rotation = character.ams * rotation_size / slow_radius
    else:
        rotation = character.ams
    rotation *= rotation_direction / rotation_size
    angular_acc = abs(character.angular)
##     if angular_acc > character.max_angular:
##         character.angular /= angular_acc
##         character.angular *= character.max_angular

def velocity_match(character, target, time_to_target):
    character.acceleration = target.velocity - character.velocity
    character.acceleration /= time_to_target
    # Check if we are going too fast
    if character.acceleration.length > character.max_acc:
        character.acceleration.set_length(character.max_acc)
    character.angular = 0.

# Advanced.
