import os, pygame
from pygame.locals import *
from math import sin, cos, pi

from physics.vector3 import Vector3
from utils.locals import MAIN_VIEW, SIDE_VIEW, TOP_VIEW

# Check for dependencies.
if not pygame.font: print 'Warning, fonts disabled'
if not pygame.mixer: print 'Warning, sound disabled'

# Some settings

def keymap_handler(game):
    pressed = pygame.key.get_pressed()

    # Main Character
    # ==============

    # Canon and hitting
    if pressed[K_h]:
        if game.main_character.hitting:
            return
        game.main_character.hitting = True

    # Canon and shooting
    if pressed[K_y]:
        if game.main_character.weapon.orientation < 90:
            game.main_character.weapon.orientation += 3
    if pressed[K_u]:
        if game.main_character.weapon.orientation > 0:
            game.main_character.weapon.orientation -= 3
    if pressed[K_n]:
        if game.main_character.weapon.shooting_force > 0:
            game.main_character.weapon.shooting_force += 2
    if pressed[K_m]:
        if game.main_character.weapon.shooting_force < 40:
            game.main_character.weapon.shooting_force -= 2
    if pressed[K_j]:
        if game.main_character.hitting: # If I'm hitting, i can't shoot
            return
        game.main_character.shooting = True

    # Movement
    # First handle two keys pressed at the same time.
    if game.main_character.jumping:
        return
    if pressed[K_SPACE]:
        game.main_character.jump()
        return
    if pressed[K_d] and pressed[K_w]:
        game.main_character.accelerate(Vector3((game.main_character.std_acc_step * sin(pi/4)), 0., -(game.main_character.std_acc_step * sin(pi/4))))
        return
    elif pressed[K_d] and pressed[K_s]:
        game.main_character.accelerate(Vector3((game.main_character.std_acc_step * sin(pi/4)), 0., (game.main_character.std_acc_step * sin(pi/4))))
        return
    elif pressed[K_a] and pressed[K_w]:
        game.main_character.accelerate(Vector3(-(game.main_character.std_acc_step * sin(pi/4)), 0., -(game.main_character.std_acc_step * sin(pi/4))))
        return
    elif pressed[K_a] and pressed[K_s]:
        game.main_character.accelerate(Vector3(-(game.main_character.std_acc_step * sin(pi/4)), 0., (game.main_character.std_acc_step * sin(pi/4))))
        return
    if pressed[K_d]:
        game.main_character.accelerate(Vector3(game.main_character.std_acc_step, 0., 0.))
        return
    elif pressed[K_a]:
        game.main_character.accelerate(Vector3(-game.main_character.std_acc_step, 0., 0.))
        return
    if pressed[K_s]:
        print 'pressed s'
        game.main_character.accelerate(Vector3(0., 0., game.main_character.std_acc_step))
        return
    if pressed[K_w]:
        game.main_character.accelerate(Vector3(0., 0., -game.main_character.std_acc_step))
        return
    elif not any([pressed[K_w], pressed[K_s], pressed[K_a], pressed[K_d]]):
        game.main_character.behave_acceleration.length = 0
        return

# functions to load resources

def load_image(name, colorkey=None):
    fullname = os.path.join(MEDIA_PATH, name)
    try:
        image = pygame.image.load(fullname)
    except pygame.error, message:
        print 'Cannot load image:', fullname
        raise SystemExit, message
    image = image.convert()
    if colorkey is not None:
        if colorkey is -1:
            colorkey = image.get_at((0,0))
        image.set_colorkey(colorkey, RLEACCEL)
    return image, image.get_rect()

def load_sound(name):
    class NoneSound:
        def play(self): pass
    if not pygame.mixer or not pygame.mixer.get_init():
        return NoneSound()
    fullname = os.path.join(MEDIA_PATH, name)
    try:
        sound = pygame.mixer.Sound(fullname)
    except pygame.error, message:
        print 'Cannot load sound:', fullname
        raise SystemExit, message
    return sound

##
# Misc functions...

def random_binomial():
    from random import random
    return random() - random()

def vector3_from_orientation(orientation, length):
    """
    Calculates velocity from a character's orientation in a 2D(1/2) space
    """
    return Vector3(length * cos(orientation), 0., length * sin(orientation))
