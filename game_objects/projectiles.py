from math import sqrt

from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

from physics.vector3 import Vector3
from utils.locals import GRAVITY, FPS

class Bullet(object):
    def __init__(self, position, velocity, radius):
        self.position = position
        self.velocity = velocity
        self.radius   = float(radius)
        self.damage   = 8

    def update(self, game):
        """
        Updates balls position
        """
        time = (1./FPS)
        self.position += self.velocity * time + (GRAVITY * time**2) / 2
        self.velocity += GRAVITY * time
        return self

    def render(self):
        """
        Renders the spherical bullet
        """
        glPushMatrix()
        glTranslatef(*self.position)
        glColor3f(.6, .6, .6)
        glutSolidSphere(self.radius, 10, 10)
        glPopMatrix()

    def explode(self):
        """
        Renders the ball's explotion
        """
        pass
