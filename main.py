import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

from game import Game, OGLManager
from utils.camera import Camera
from utils.functions import keymap_handler
from utils.locals import SCREEN, FPS

def main():
    pygame.init()
    screen = pygame.display.set_mode(SCREEN.size, HWSURFACE|OPENGL|DOUBLEBUF)

    OGLManager.resize(*SCREEN.size)
    OGLManager.init(*SCREEN.size)

    pygame.display.set_caption("No title yet...")

    camera = Camera()
    game = Game()             # Game object. This will handle all the game world
                              # and its components
    game.random_enemies(1)    # Creates one random enemy

    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                return
            if event.type == KEYUP and event.key == K_ESCAPE:
                return

        keymap_handler(game, camera)

        # Set FPS
        game.clock.tick(FPS)

        # Draw the camera
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        glClearColor(0.0,0.0,0.0,0.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        gluLookAt(*camera.to_args())
#        print camera

        # Draw the game
        game.render()

        # Draw game's axes <optional, remove after debugging...>
        game.draw_axes()

        # Flip and display view.
        pygame.display.flip()

if __name__ == '__main__': main()
