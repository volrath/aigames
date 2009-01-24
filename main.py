import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

from stage import Stage
from characters import Slash
from utils import Camera, keymap_handler, MAIN_VIEW, FPS

# First position
camera = Camera().set(MAIN_VIEW)

SCREEN = Rect(0, 0, 1000, 700)

def drawAxes():
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

class GLUTManager:
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

def main():
    pygame.init()
    screen = pygame.display.set_mode(SCREEN.size, HWSURFACE|OPENGL|DOUBLEBUF)

    GLUTManager.resize(*SCREEN.size)
    GLUTManager.init(*SCREEN.size)

    pygame.display.set_caption("No title yet...")

    # Game's objects
    clock = pygame.time.Clock()
    slash = Slash(20,20)
    stage = Stage(floor_size=20)

    global camera, view, up

    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                return
            if event.type == KEYUP and event.key == K_ESCAPE:
                return

        keymap_handler(slash, camera)

        clock.tick(FPS)

        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        glClearColor(0.0,0.0,0.0,0.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        gluLookAt(*camera.to_args())
#        print camera

        stage.render()
        slash.update().render()

        drawAxes()
        pygame.display.flip()

if __name__ == '__main__': main()
