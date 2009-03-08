import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

from ai.behavior import *
from ai.state_machine import StateMachine
from game_objects.stage import Stage
from game_objects.characters import Slash, Enemy
from physics.vector3 import Vector3
from utils.camera import Camera
from utils.functions import keymap_handler
from utils.locals import MAIN_VIEW, FPS, STAGE_SIZE
from utils.exceptions import GameOverException

class OGLManager:
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

class Game:
    def __init__(self, level=None):
        # Set the games objects
        self.clock = pygame.time.Clock()
        self.main_character = Slash(20.,20.,position=Vector3(0.,0.,-1.), orientation=1.5)

        self.enemies = []
        self.characters = [self.main_character]
        self.projectiles = [] # projectiles pool
        self.stage = Stage(STAGE_SIZE)

    def set_level(self, level):
        """
        Set the game's level, following this operations:
        1. Get level structure
        2. Set level's obstacles
        3. Load the level's graph
        4. Set level's characters (enemies)
        """
        # 1. Little bit of wired code =p
        from utils.levels import LEVEL
        # 2.
        self.stage.set_level(LEVEL['obstacles'])
        # 3.
        self.graph = Graph(LEVEL['number_of_nodes'], LEVEL['nodes'], LEVEL['neighbors'])
        self.graph.load()
        self.a_star = AStar(self.graph)
        # 4.
        self.random_enemies(LEVEL['enemies'])

    def draw_axes(self):
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

    def behave(self):
        """
        For the main character, catch keyboards interruptions and execute the
        appropiate behavior according to the key stroke catched.
        For AI characters (enemies), gets the current behavior they are doing
        and updates its kinematic and steering data.
        """
        # Slash behavior
        keymap_handler(self) # Maybe i can just pass self.main_character
        self.main_character.behave(game=self)

        # AI characters behavior
        for enemy in self.enemies:
            StateMachine.fuzzy_life(enemy, self)
            enemy.behave()
            enemy.attack(self)

    def render(self):
        # Renders all game's objects
        self.stage.render()

        try:
            self.main_character.update(self).render()
        except AttributeError, e:
            self.game_over(False)

        if not self.enemies:
            self.game_over(True)
        for enemy in self.enemies:
            try:
                enemy.update(self).render()
            except AttributeError, e:
                pass

        # Renders projectiles
        for projectile in self.projectiles:
            projectile.update(self).render()
            if projectile.position.y < 0:
                self.projectiles.remove(projectile)

    def game_over(self, i_won):
        if i_won:
            # I won!
            print "You Rock So Hard!! =)"
        else:
            # I failed =(
            print "You suck..."
        raise GameOverException

    def add_character(self, character):
        """
        Add a character to the game, for now only enemies..
        To-do: allies?
        """
        self.enemies.append(character)
        self.characters.append(character)

    def random_enemies(self, positions):
        """
        Add <number> random enemies...
        Improve this when different type of enemies are complete.
        """
        for position in positions:
            enemy = Enemy(3.5,3., position=position, orientation=0.)

            pursue_evade_behaviors = [
                Behavior(character=enemy,
                         target=self.main_character,
                         args={'characters_sight': 20.},
                         **PURSUE),
                Behavior(character=enemy,
                         target=self.main_character,
                         args={'characters_sight': 5.},
                         **EVADE)
                ]

            wander_behaviors = [Behavior(character=enemy, **WANDER)]

            flocking = [
                Behavior(character=enemy, target=self.enemies, **SEPARATION),
                Behavior(character=enemy, target=self.enemies, **COHESION),
                Behavior(character=enemy, target=self.enemies,
                         **VELOCITY_MATCHING),
                ]

            collision_behaviors = [
                Behavior(character=enemy,
                         args={'game': self, 'look_ahead': 15.},
                         **OBSTACLE_AVOIDANCE)
                ]
            
##             enemy.add_behavior_group(BehaviorGroup(b_set=pursue_evade_behaviors,
##                                                    **PURSUE_EVADE_GROUP))
##             enemy.add_behavior_group(BehaviorGroup(b_set=collision_behaviors,
##                                                    **COLLISION_AVOIDANCE_GROUP))
##             enemy.add_behavior_group(BehaviorGroup(b_set=flocking,
##                                                    **FLOCKING_GROUP))
##             enemy.add_behavior_group(BehaviorGroup(b_set=wander_behaviors,
##                                                    **WANDER_GROUP))
            self.add_character(enemy)
