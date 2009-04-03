from math import sqrt

from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

from physics.vector3 import Vector3
from utils.locals import GRAVITY, FPS
from graphics.utils import draw_circle

class Bullet(object):
    def __init__(self, position, velocity, owner):
        self.position  = position
        self.velocity  = velocity
        self.owner     = owner
        self.explotion = None

    def update(self, game):
        """
        Updates balls position
        """
        if self.explotion is not None:
            self.radius -= .1
            self.explotion.update()
        else:
            time = (1./FPS)
            self.position += self.velocity * time + (GRAVITY * time**2) / 2
            self.velocity += GRAVITY * time

        return self

    def render(self):
        """
        Renders the spherical bullet
        """
        if self.explotion is not None:
            if self.radius < 0:
                try:
                    self.game.projectiles.remove(self)
                except ValueError:
                    pass
            self.explotion.render()
        glPushMatrix()
        glTranslatef(*self.position)
        glColor3f(*self.color)
        glutSolidSphere(self.radius, 10, 10)
        glPopMatrix()

    def explode(self, game):
        """
        Renders the ball's explotion
        """
        # Define a new render method
        self.game = game
        self.explotion = BallExplotionWave(self.position, self.radius)


class SlashNormalBullet(Bullet):
    radius = .9
    color = 6., 6., 6.
    hit_force = 130.
    damage = 4.

class SlashSuperBullet(Bullet):
    radius = 1.3
    color = 238/255., 254/255., 1.
    hit_force = 220.
    damage = 8.

class EnemyBullet(Bullet):
    radius = .6
    color = 9., 9., 9.
    hit_force = 150.
    damage = 5

class SoundWave(object):
    def __init__(self, position, radius):
        self.position  = position
        self.intensity = 100
        self.radius    = radius

    def update(self, game=None):
        """
        Updates sound wave's radius and intensity
        """
        self.intensity -= self.intensity_decrease
        if self.intensity >= 0:
            self.radius *= self.radius_expansion
            self.color = tuple([x - .02 for x in self.color])
        return self

    def render(self):
        """
        Renders the wave...
        """
        draw_circle(self.position, self.radius, self.color)

class NormalSoundWave(SoundWave):
    intensity_decrease = 3
    radius_expansion   = 1.07
    color              = (1., 0., 0.)

class SuperSoundWave(SoundWave):
    intensity_decrease = 5
    radius_expansion   = 1.15
    color              = (1., 240/255., 0.)

class StepSoundWave(SoundWave):
    intensity_decrease = 4
    radius_expansion   = 1.09
    color              = (46/255., 1., 76/255.)

class BallExplotionWave(SoundWave):
    intensity_decrease = 6
    radius_expansion   = 1.09
    color              = (1., 1., 1.)
