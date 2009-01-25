# Steering Behaviors.

def seek(character, target):
    new_acc = target.position - character.position
    character.acceleration = new_acc.set_length(character.std_acc)
    character.angular = 0.

def flee(character, target):
    new_acc = character.position - target.position
    character.acceleration = new_acc.set_length(character.std_acc)
    character.angular = 0.

def arrive(character, target, target_radius, slow_radius, time_to_target):
    direction = target.position - character.position
    distance = direction.length
    # Are we there?
    if distance < target_radius:
        return # Maybe put velocity = acceleration = 0?
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
