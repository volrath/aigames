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
    global camera

    # Game initialization
    pygame.init()
    screen = pygame.display.set_mode(map(int, SCREEN.size), HWSURFACE|OPENGL|DOUBLEBUF)
    OGLManager.resize(*(map(int, SCREEN.size)))
    OGLManager.init(*(map(int, SCREEN.size)))

    pygame.display.set_caption("Reggaetonator")

    # Game's objects initialization
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

        # Set FPS
        game.clock.tick(FPS)

        # Updates cammera position, if asked.
        camera.handle_keys()
        # Draw the camera
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        glClearColor(0.0,0.0,0.0,0.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        gluLookAt(*camera.to_args())
#        print camera

        # Draw the game
        game.prepare_behave() # Follows behaviors in game.characters
        game.render()         # Render all game's elements

        # Draw game's axes <optional, remove after debugging...
        game.draw_axes()

        # Flip and display view.
        pygame.display.flip()

if __name__ == '__main__': main()
