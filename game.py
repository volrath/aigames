import random
from math import pi

import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

from ai.a_star import AStar
from ai.behavior import *
from ai.graph import Graph
from ai.state_machine import StateMachine
from game_objects.stage import Stage
from game_objects.characters import Slash, Enemy
from graphics.utils import life_bar, rock_bar
from physics.vector3 import Vector3
from utils.camera import Camera
from utils.functions import keymap_handler
from utils.locals import MAIN_VIEW, FPS, STAGE_SIZE, NEW_ENEMY_TIME
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
        self.main_character = Slash(20.,20.,position=Vector3(0.,0.,-1.), orientation=0.)

        self.enemies = []
        self.characters = [self.main_character]
        self.projectiles = []  # projectiles pool
        self.sound_wave = None # sound wave 'pool'
        self.stage = Stage(STAGE_SIZE)
        # Control
        self.print_debug = False
        self.last_enemy_addition = 0

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
        global LEVEL
        self.level = LEVEL
        # 2.
        self.stage.set_level(LEVEL['obstacles'])
        # 3.
        self.graph = Graph(LEVEL['number_of_nodes'], LEVEL['nodes'], LEVEL['neighbors'])
        self.a_star = AStar(self.graph)
        self.graph.load(self.a_star)
        LEVEL['graph'] = self.graph
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
            enemy.behave()
            if not hasattr(enemy, 'state'):
                setattr(enemy, 'state', StateMachine(enemy))
            enemy.state.update(self).execute(self)

    def render(self):
        # Renders sectors and nodes
        if self.print_debug:
            self.render_debug()

        # Renders all the eye candy:
        life_bar(self.main_character, -10.)
        rock_bar(self.main_character, -9.)
        enemy_z_pos = 10.
        for enemy in self.enemies:
            life_bar(enemy, enemy_z_pos)
            enemy_z_pos -= 1
            

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
            # Checks if the projectile reach the floor
            if projectile.position.y < 0:
                self.projectiles.remove(projectile)
            # Checks if the projectile hit an obstacle
            for obstacle in self.stage.obstacles:
                distance = (obstacle.position - projectile.position).length
                if distance < obstacle.radius + projectile.radius:
                    # They hit!
                    projectile.explode(self)

        # Renders sound wave, if any
        if self.sound_wave is not None:
            if self.sound_wave.intensity <= 0:
                self.sound_wave = None
                self.main_character.playing = False
            else:
                self.sound_wave.update(self).render()

    def extra(self):
        """
        Loads extra content in the game, if needed
        """
        current_time = pygame.time.get_ticks()
        # Add a new enemy every 90s
        if len(self.characters) < 4 and \
           current_time - self.last_enemy_addition > NEW_ENEMY_TIME:
            random_node = random.choice(self.level['nodes'])
            while random_node.id in \
                  [node.id for node in \
                   [graph_quantization(character.position) for character in \
                    self.characters]]:
                random_node = random.choice(self.level['nodes'])
            self.random_enemies([(random_node.location, 'X')])
            self.last_enemy_addition = current_time

    def render_debug(self):
        """
        """
        glPushMatrix()
        # Sectors
        glTranslatef(0., 1., 0.)
        glColor3f(0., 1., 0.)
        for sector in self.level['sectors']:
            s1, s2, s3 = sector
            glBegin(GL_LINES)
            glVertex3f(s1[0], 0., s1[1])
            glVertex3f(s2[0], 0., s2[1])
            glEnd()
            glBegin(GL_LINES)
            glVertex3f(s1[0], 0., s1[1])
            glVertex3f(s3[0], 0., s3[1])
            glEnd()
            glBegin(GL_LINES)
            glVertex3f(s3[0], 0., s3[1])
            glVertex3f(s2[0], 0., s2[1])
            glEnd()
        glPopMatrix()

        glPushMatrix()
        glTranslatef(0., 1., 0.)
        for node in self.level['nodes']:
            glColor3f(1., 1., 1.)
            glBegin(GL_LINES)
            glVertex3f(node.location.x, 0., node.location.z)
            glVertex3f(node.location.x, 5., node.location.z)
            glEnd()
            for neighbor in self.level['neighbors'][node.id]:
                neighbor = self.level['nodes'][neighbor]
                glColor3f(1., 0., 0.)
                glBegin(GL_LINES)
                glVertex3f(node.location.x, 1., node.location.z)
                glVertex3f(neighbor.location.x, 1., neighbor.location.z)
                glEnd()
        glPopMatrix()

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

    def random_enemies(self, initials):
        """
        Add <number> random enemies...
        Improve this when different type of enemies are complete.
        """
        for initial in initials:
            position, name = initial
            enemy = Enemy(5.5,3., name=name, position=position, orientation=pi)

            pursue_behaviors = [
                Behavior(character=enemy,
                         target=self.main_character,
                         args={'characters_sight': 30.},
                         **PURSUE),
                ]
            evade_behaviors = [
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
            separation = [
                Behavior(character=enemy, target=self.enemies, **SEPARATION),
                ]

            collision_behaviors = [
                Behavior(character=enemy,
                         args={'game': self, 'look_ahead': 10.},
                         **OBSTACLE_AVOIDANCE)
                ]
            
            enemy.add_behavior_group(BehaviorGroup(b_set=separation,
                                                   **FLOCKING_GROUP))
            enemy.add_behavior_group(BehaviorGroup(b_set=pursue_behaviors,
                                                   **PURSUE_GROUP))
            enemy.add_behavior_group(BehaviorGroup(b_set=evade_behaviors,
                                                   **EVADE_GROUP))
            enemy.add_behavior_group(BehaviorGroup(b_set=collision_behaviors,
                                                   **COLLISION_AVOIDANCE_GROUP))
            enemy.add_behavior_group(BehaviorGroup(b_set=wander_behaviors,
                                                   **WANDER_GROUP))
            self.add_character(enemy)
