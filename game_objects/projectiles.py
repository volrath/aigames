from math import sqrt

from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

from physics.vector3 import Vector3
from utils.locals import GRAVITY, FPS

class Bullet(object):
    def __init__(self, position, velocity):
        self.position  = position
        self.velocity  = velocity

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
        glColor3f(*self.color)
        glutSolidSphere(self.radius, 10, 10)
        glPopMatrix()

    def explode(self, game):
        """
        Renders the ball's explotion
        """
        game.projectiles.remove(self)


class SlashNormalBullet(Bullet):
    radius = .9
    color = 6., 6., 6.
    hit_force = 130.
    damage = 4.

class EnemyBullet(Bullet):
    radius = .6
    color = 9., 9., 9.
    hit_force = 150.
    damage = 5
