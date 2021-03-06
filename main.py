# -*- coding: utf-8 -*-
import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

from game import Game, OGLManager
from physics.vector3 import Vector3
from utils.camera import Camera
from utils.exceptions import GameOverException
from utils.functions import keymap_handler
from utils.locals import SCREEN, FPS
from utils.menu import Menu

def main():
    global camera

    # Game initialization
    pygame.init()
    screen = pygame.display.set_mode(map(int, SCREEN.size))

    # Game's objects initialization
    camera = Camera()
    game   = Game()             # Game object. This will handle all the game world
                                # and its components
    menu   = Menu(screen, game)

    # Game's menu
    while menu.update():
        menu.render()
        for event in pygame.event.get():
            if event.type == QUIT:
                return
            if event.type == KEYUP and event.key == K_ESCAPE:
                return
        pygame.display.flip()

    screen = pygame.display.set_mode(map(int, SCREEN.size), HWSURFACE|OPENGL|DOUBLEBUF)
    OGLManager.resize(*(map(int, SCREEN.size)))
    OGLManager.init(*(map(int, SCREEN.size)))

    pygame.display.set_caption("¡A ti te va a caer el Axl!")
    # Game!
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                return
            if event.type == KEYUP and event.key == K_ESCAPE:
                return

        # Set FPS
        game.clock.tick(FPS)

        # Updates camera position, if asked.
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
            game.render()         # Renders all game's elements
            game.behave()         # Follows behaviors in game.characters
            game.extra()          # Loads extra content in the game, if needed
        except GameOverException:
            import sys, time
            # wait a few seconds to show the result of the game.
            time.sleep(4)
            # Continue? maybe later
            sys.exit()
        # Flip and display view.
        pygame.display.flip()

if __name__ == '__main__': main()
