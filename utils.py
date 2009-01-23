import os, pygame
from pygame.locals import *

if not pygame.font: print 'Warning, fonts disabled'
if not pygame.mixer: print 'Warning, sound disabled'

# Some settings
MEDIA_PATH = 'media'
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
            self.position = view_dict['position']
        if view_dict.has_key('view'):
            self.view = view_dict['view']
        if view_dict.has_key('up'):
            self.up = view_dict['up']
        return self

def keymap_handler(character, camera=None):
    pressed = pygame.key.get_pressed()
    # Camera
    if pressed[K_1]:
        camera.set(MAIN_VIEW.copy())
    elif pressed[K_2]:
        camera.set(SIDE_VIEW.copy())
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
    if pressed[K_d]:
        character.position['x'] += .1
    elif pressed[K_a]:
        character.position['x'] += -.1
    if pressed[K_s]:
        character.position['z'] += -.1
    elif pressed[K_w]:
        character.position['z'] += +.1
##     if pressed[K_q]:
##         view['z'] += -.1
##     elif pressed[K_e]:
##         view['z'] += +.1
##     if pressed[K_1]:
##         print '1 pressed'
##         camera = MAIN_VIEW['camera'].copy()
##         view = MAIN_VIEW['view'].copy()
##     elif pressed[K_2]:
##         camera = SIDE_VIEW['camera'].copy()
##         view = SIDE_VIEW['view'].copy()

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
