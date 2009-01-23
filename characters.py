from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

from utils import load_image

class Character:
    """
    Character properties, movement, size, etc..
    """
    def __init__(self, linear_max_speed, angular_max_speed):
        self.lms = linear_max_speed
        self.ams = angular_max_speed

class Slash(Character):
    """
    Super Slash object =)
    """
    def __init__(self, lms, ams, initial={'pos': (0.,0.), 'ori': 0}):
        Character.__init__(self, lms, ams)
        self.position = { 'x': initial['pos'][0], 'z': initial['pos'][1] }
        self.orientation = initial['ori']
        #self.image, self.rect = load_image('main_character.png')
