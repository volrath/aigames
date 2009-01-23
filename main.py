import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

from stage import Stage

# Presets camera positions
MAIN_VIEW = { 
    'camera': { 'x': 0., 'y': 12., 'z': 54.5 },
    'view': { 'x': 0., 'y': 12.6, 'z': 0.1 }
    }
SIDE_VIEW = { 
    'camera': { 'x': -26., 'y': 15.5, 'z': 37.5 },
    'view': { 'x': 2.3, 'y': 2.2, 'z': 0.1 }
    }
# First position
camera = MAIN_VIEW['camera'].copy()
view = MAIN_VIEW['view'].copy()
up = { 'x': 0., 'y': 1., 'z': 0. }

SCREEN = Rect(0, 0, 1000, 700)

def drawAxes():
    # Space axes
    #Eje X
    glBegin(GL_LINES)
    glColor3f(1.0,0.0,0.0)
    glVertex3f(-20000.0,0.0,0.0)
    glVertex3f(20000.0,0.0,0.0)
    glEnd()
    
    #Eje Y
    glBegin(GL_LINES)
    glColor3f(0.,1.,0.)
    glVertex3f(0.0,-200.0,0.0)
    glVertex3f(0.0,200.0,0.0)
    glEnd()
    
    #Eje Z
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
    stage = Stage(floor_size=20).default_amplificators()

    global camera, view, up

    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                return
            if event.type == KEYUP and event.key == K_ESCAPE:
                return

        # Clear the screen, and z-buffer
#        glClearColor(0.0,0.0,0.0,0.0)
#        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);

        pressed = pygame.key.get_pressed()
        if pressed[K_LEFT]:
            camera['x'] += .5
        elif pressed[K_RIGHT]:
            camera['x'] += -.5
        if pressed[K_UP]:
            camera['y'] += -.5
        elif pressed[K_DOWN]:
            camera['y'] += +.5
        if pressed[K_z]:
            camera['z'] += -.5
        elif pressed[K_x]:
            camera['z'] += +.5
        if pressed[K_d]:
            view['x'] += .1
        elif pressed[K_a]:
            view['x'] += -.1
        if pressed[K_s]:
            view['y'] += -.1
        elif pressed[K_w]:
            view['y'] += +.1
        if pressed[K_q]:
            view['z'] += -.1
        elif pressed[K_e]:
            view['z'] += +.1
        if pressed[K_1]:
            print '1 pressed'
            camera = MAIN_VIEW['camera'].copy()
            view = MAIN_VIEW['view'].copy()
        elif pressed[K_2]:
            camera = SIDE_VIEW['camera'].copy()
            view = SIDE_VIEW['view'].copy()

        clock.tick(60)

        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        glClearColor(0.0,0.0,0.0,0.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        gluLookAt(camera['x'], camera['y'], camera['z'],
                  view['x'], view['y'], view['z'],
                  up['x'], up['y'], up['z'])
        print 'CAMERA: ', camera['x'], camera['y'], camera['z'], 'VIEW:', view['x'], view['y'], view['z']

        stage.render()

        drawAxes()
        pygame.display.flip()

if __name__ == '__main__': main()
