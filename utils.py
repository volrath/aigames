import os, pygame
from pygame.locals import *
from math import sin, cos, pi

from vector3 import Vector3

if not pygame.font: print 'Warning, fonts disabled'
if not pygame.mixer: print 'Warning, sound disabled'

# Some settings
MEDIA_PATH = 'media'
FPS = 60
# Presets camera positions
MAIN_VIEW = { 
    'position': { 'x': 0., 'y': 12., 'z': 54.5 },
    'view': { 'x': 0., 'y': 12.6, 'z': 0.1 }
    }
SIDE_VIEW = { 
    'position': { 'x': -26., 'y': 15.5, 'z': 37.5 },
    'view': { 'x': 2.3, 'y': 2.2, 'z': 0.1 }
    }

class Camera:
    """
    Models an opengl camera
    """
    def __init__(self, position=(0.,0.,0.), view=(0.,0.,0.), up=(0.,1.,0.)):
        self.position = {'x': position[0], 'y': position[1], 'z': position[2]}
        self.view     = {'x': view[0], 'y': view[1], 'z': view[2]}
        self.up       = {'x': up[0], 'y': up[1], 'z': up[2]}

    def __unicode__(self):
        args = self.to_args()
        return 'POSITION: %s  VIEW: %s' % (args[:3], args[3:6])
    __str__ = __unicode__

    def to_args(self):
        """
        return a tuple of its values to be passed as arguments to a function
        """
        return (self.position['x'], self.position['y'], self.position['z']) + \
               (self.view['x'], self.view['y'], self.view['z']) + \
               (self.up['x'], self.up['y'], self.up['z'])
# WTF?!
#        return tuple(self.position.values()) + \
#               tuple(self.view.values()) + \
#               tuple(self.up.values())

    def set(self, view_dict):
        """
        set the camera view, given a representive dict
        """
        if view_dict.has_key('position'):
            self.position = view_dict['position'].copy()
        if view_dict.has_key('view'):
            self.view = view_dict['view'].copy()
        if view_dict.has_key('up'):
            self.up = view_dict['up'].copy()
        return self

def keymap_handler(character, camera=None):
    pressed = pygame.key.get_pressed()

    # Debugging keys
    if pressed[K_SPACE]:
        print 'pressed space'
        character.wandering = True

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
        character.accelerate(Vector3((character.std_acc * sin(pi/4)), 0., -(character.std_acc * sin(pi/4))))
        return
    elif pressed[K_d] and pressed[K_s]:
        character.accelerate(Vector3((character.std_acc * sin(pi/4)), 0., (character.std_acc * sin(pi/4))))
        return
    elif pressed[K_a] and pressed[K_w]:
        character.accelerate(Vector3(-(character.std_acc * sin(pi/4)), 0., -(character.std_acc * sin(pi/4))))
        return
    elif pressed[K_a] and pressed[K_s]:
        character.accelerate(Vector3(-(character.std_acc * sin(pi/4)), 0., (character.std_acc * sin(pi/4))))
        return
    if pressed[K_d]:
        character.accelerate(Vector3(character.std_acc, 0., 0.))
        return
    elif pressed[K_a]:
        character.accelerate(Vector3(-character.std_acc, 0., 0.))
        return
    if pressed[K_s]:
        character.accelerate(Vector3(0., 0., character.std_acc))
        return
    if pressed[K_w]:
        character.accelerate(Vector3(0., 0., -character.std_acc))
        return
    elif not any([pressed[K_w], pressed[K_s], pressed[K_a], pressed[K_d]]):
        character.accelerate(deacc=True)
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
