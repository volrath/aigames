import sys

import pygame
from pygame.locals import *

from utils.enum import Enum
from utils.functions import load_image

MENU_OPTIONS = Enum('play', 'get_out')

class Menu(object):
    """
    """
    def __init__(self, screen, game):
        self.screen        = screen
        self.background, _ = load_image('menu_game.png', -1)
        selector_image, _  = load_image('rose_selector.png', -1)
        self.selector      = {
            'image':  selector_image,
            'position': (290, 250)
            }
        self.loading       = None
        self.option        = MENU_OPTIONS.play
        self.game          = game

    def update(self):
        """
        Also handle key events
        """
        pressed = pygame.key.get_pressed()

        if pressed[K_LEFT]:
            self.option = MENU_OPTIONS.play
            self.selector['position'] = (290, 250)
        if pressed[K_RIGHT]:
            self.option = MENU_OPTIONS.get_out
            self.selector['position'] = (550, 250)
        if pressed[K_RETURN]:
            # Set Loading!
            if self.option == MENU_OPTIONS.play:
                print 'LOADING!'
                self.game.set_level(0)
                print 'ALL SET...'
                return False
            else:
                sys.exit()
        return True

    def render(self):
        self.screen.blit(self.background, (0,0))
        self.screen.blit(self.selector['image'], self.selector['position'])
