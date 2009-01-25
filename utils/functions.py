import os, pygame
from pygame.locals import *
from math import sin, cos, pi

from physics.vector3 import Vector3
from utils.locals import MAIN_VIEW, SIDE_VIEW

# Check for dependencies.
if not pygame.font: print 'Warning, fonts disabled'
if not pygame.mixer: print 'Warning, sound disabled'

# Some settings

def keymap_handler(game, camera=None):
    pressed = pygame.key.get_pressed()

    # Debugging keys
    if pressed[K_SPACE]:
        print 'pressed space'
        game.main_character.wandering = True

    # Camera
    if pressed[K_1]:
        camera.set(MAIN_VIEW)
    elif pressed[K_2]:
        camera.set(SIDE_VIEW)
    if pressed[K_LEFT]:
        camera.position['x'] += .5
    elif pressed[K_RIGHT]:
        camera.position['x'] += -.5
    if pressed[K_UP]:
        camera.position['y'] += -.5
    elif pressed[K_DOWN]:
        camera.position['y'] += +.5
    if pressed[K_z]:
        camera.position['z'] += -.5
    elif pressed[K_x]:
        camera.position['z'] += +.5

    # Character
    # First handle two keys pressed at the same time.
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
        game.main_character.accelerate(Vector3(0., 0., game.main_character.std_acc_step))
        return
    if pressed[K_w]:
        game.main_character.accelerate(Vector3(0., 0., -game.main_character.std_acc_step))
        return
    elif not any([pressed[K_w], pressed[K_s], pressed[K_a], pressed[K_d]]):
        game.main_character.accelerate(deacc=True)
        return
##
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
