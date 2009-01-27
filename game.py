import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

from game_objects.stage import Stage
from game_objects.characters import Slash, Enemy
from physics.vector3 import Vector3
from physics import steering_behaviors as behaviors
from utils.camera import Camera
from utils.functions import keymap_handler
from utils.locals import MAIN_VIEW, FPS, STAGE_SIZE

class OGLManager:
    @classmethod
    def init(self, width, height):
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glShadeModel(GL_SMOOTH)
        glClearColor(0., 1., 0., 1.)
        glClearDepth(1.)
        glEnable(GL_ALPHA_TEST)
        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_LESS)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45.0, float(width)/float(height), 0.1, 100.0)
        glMatrixMode(GL_MODELVIEW)
        # GLUT
        glutInit()

    @classmethod
    def resize(self, width, height):
        if height == 0:
            height = 1
        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45.0, float(width)/height, .1, 100.)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

class Game:
    def __init__(self):
        # Set the games objects
        self.clock = pygame.time.Clock()
        self.main_character = Slash(20.,20.,position=Vector3(-12.,0.,-17.), orientation=1.5)
        self.enemies = []
        self.stage = Stage(STAGE_SIZE)

    def draw_axes(self):
        # Space axes
        # Axis X
        glBegin(GL_LINES)
        glColor3f(1.0,0.0,0.0)
        glVertex3f(-20000.0,0.0,0.0)
        glVertex3f(20000.0,0.0,0.0)
        glEnd()
        # Axis Y
        glBegin(GL_LINES)
        glColor3f(0.,1.,0.)
        glVertex3f(0.0,-200.0,0.0)
        glVertex3f(0.0,200.0,0.0)
        glEnd()
        # Axis Z
        glBegin(GL_LINES)
        glColor3f(0.,0.,1.)
        glVertex3f(0.0,0.0,-200.0)
        glVertex3f(0.0,0.0,200.0)
        glEnd()

    def render(self):
        # Renders all game's objects
        self.stage.render()   # TODO: improve stage rendering, use display lists
        # Before update and render i have to check for the behaviors this
        # character should be doing. TODO
        self.main_character.update().render()
        for enemy in self.enemies:
            enemy.update().render()

##        behaviors.arrive(self.enemies[0], self.main_character, .5, 3.5, .1)
##        behaviors.pursue(self.enemies[0], self.main_character, .5)

        behaviors.pursue_and_stop(self.enemies[0], self.main_character,
                                  max_prediction=.5, target_radius=.5,
                                  slow_radius=3.5, time_to_target=.1)

    def add_character(self, character):
        """
        Add a character to the game, for now only enemies..
        To-do: allies?
        """
        self.enemies.append(character)

    def random_enemies(self, number):
        """
        Add <number> random enemies...
        Improve this when different type of enemies are complete.
        """
        for i in range(0,number):
            self.add_character(Enemy(5.,5., position=Vector3(12., 0., 8.), orientation=0.))
