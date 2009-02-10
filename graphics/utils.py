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
