from functools import wraps
from math import sin, cos, pi

from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

def draw_circle(position, radius, color):
    """
    Draw a circle in a 3d space
    """
    glPushMatrix()
    glTranslatef(0.,0.,0.)
    glColor3f(*color)
    glBegin(GL_LINES)
    x = radius * cos(359 * pi/180.) + position.x
    z = radius * sin(359 * pi/180.) + position.z
    for i in range(0,360):
        glVertex3f(x, position.y, z)
        x = radius * cos(i * pi/180.) + position.x
        z = radius * sin(i * pi/180.) + position.z
        glVertex3f(x, position.y, z)
    glEnd()
    glPopMatrix()

def rock_bar(character, z_pos):
    """
    Draw a rock bar for the main character
    """
    if character.rock_bar > 20:
        character.rock_bar = 20
    glPushMatrix()
    glTranslatef(-16.6, 50., z_pos)
    glColor3f(90/255., 90/255., 90/255.)
    glBegin(GL_LINES)
    glVertex3f(0., 0., 0.)
    glVertex3f(4.5, 0., 0.)
    glEnd()
    glBegin(GL_LINES)
    glVertex3f(4.5, 0., 0.)
    glVertex3f(4.5, 0., .8)
    glEnd()
    glBegin(GL_LINES)
    glVertex3f(4.5, 0., .8)
    glVertex3f(0., 0., .8)
    glEnd()
    glBegin(GL_LINES)
    glVertex3f(0., 0., .8)
    glVertex3f(0., 0., 0.)
    glEnd()

    glTranslatef(.07, 0., .07)
    glColor3f(1., character.rock_bar/30., 0.)
    glBegin(GL_QUADS)
    glVertex3f(0., 0., 0.)
    glVertex3f(4.38 * character.rock_bar / 20., 0., 0.)
    glVertex3f(4.38 * character.rock_bar / 20., 0., .68)
    glVertex3f(0., 0., .68)
    glEnd()
    glPopMatrix()

def life_bar(character, z_pos):
    """
    Draw a life bar for the especified character
    """
    if character.energy < 0:
        character.energy = 0
    glPushMatrix()
    glTranslatef(-16.6, 50., z_pos)
    glColor3f(120/255., 120/255., 120/255.)
    glBegin(GL_LINES)
    glVertex3f(0., 0., 0.)
    glVertex3f(4.5, 0., 0.)
    glEnd()
    glBegin(GL_LINES)
    glVertex3f(4.5, 0., 0.)
    glVertex3f(4.5, 0., .8)
    glEnd()
    glBegin(GL_LINES)
    glVertex3f(4.5, 0., .8)
    glVertex3f(0., 0., .8)
    glEnd()
    glBegin(GL_LINES)
    glVertex3f(0., 0., .8)
    glVertex3f(0., 0., 0.)
    glEnd()

    glTranslatef(.07, 0., .07)
    glColor3f(1-character.energy/50., character.energy/50., 0.)
    glBegin(GL_QUADS)
    glVertex3f(0., 0., 0.)
    glVertex3f(4.38 * character.energy / 100., 0., 0.)
    glVertex3f(4.38 * character.energy / 100., 0., .68)
    glVertex3f(0., 0., .68)
    glEnd()
    glPopMatrix()
