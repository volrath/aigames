import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

from game_objects.stage import Stage
from game_objects.characters import Slash, Enemy
from physics.vector3 import Vector3
from physics.behavior import *
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
        self.characters = [self.main_character]
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

    def prepare_behave(self):
        """
        For the main character, catch keyboards interruptions and execute the
        appropiate behavior according to the key stroke catched.
        For AI characters (enemies), gets the current behavior they are doing
        and updates its kinematic and steering data.
        """
        # Slash behavior
        keymap_handler(self) # Maybe i can just pass self.main_character

        # AI characters behavior
        for enemy in self.enemies:
            enemy.behavior.execute()

    def render(self):
        # Renders all game's objects
        self.stage.render()   # TODO: improve stage rendering, use display lists

        self.main_character.update(self).render()
        for enemy in self.enemies:
            enemy.update(self).render()

    def add_character(self, character):
        """
        Add a character to the game, for now only enemies..
        To-do: allies?
        """
        self.enemies.append(character)
        self.characters.append(character)

    def random_enemies(self, number):
        """
        Add <number> random enemies...
        Improve this when different type of enemies are complete.
        """
        for i in range(0,number):
            enemy = Enemy(20.,20., position=Vector3(12., 0., 8.), orientation=0.)
            enemy.add_behavior(PURSUE)
            enemy.behavior.character = enemy
            enemy.behavior.target = self.main_character
            self.add_character(enemy)
