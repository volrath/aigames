# -*- coding: utf-8 -*-
import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

from game import Game, OGLManager
from physics.vector3 import Vector3
from utils.camera import Camera
from utils.functions import keymap_handler
from utils.locals import SCREEN, FPS
from utils.exceptions import GameOverException

def main():
    global camera

    # Game initialization
    pygame.init()
    screen = pygame.display.set_mode(map(int, SCREEN.size), HWSURFACE|OPENGL|DOUBLEBUF)
    OGLManager.resize(*(map(int, SCREEN.size)))
    OGLManager.init(*(map(int, SCREEN.size)))

    pygame.display.set_caption("¡A ti te va a caer el Axl!")

    # Game's objects initialization
    camera = Camera()
    game = Game()             # Game object. This will handle all the game world
                              # and its components
    game.random_enemies([Vector3(4., 0., -5.)])    # Creates 'random' enemies

##     try:
##         import psyco
##         psyco.full()
##     except ImportError:
##         pass
    
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
        try:
            game.render()         # Render all game's elements
            game.behave()         # Follows behaviors in game.characters
        except GameOverException:
            import sys, time
            # wait a few seconds to show the result of the game.
            time.sleep(4)
            # Continue? maybe later
            sys.exit()

        # Flip and display view.
        pygame.display.flip()

if __name__ == '__main__': main()
