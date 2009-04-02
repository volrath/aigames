from math import sqrt, atan2, pi

import pygame
from pygame.locals import *

from physics.vector3 import Vector3
from utils.enum import Enum
from utils.locals import GRAVITY
from utils.functions import hit_detection, graph_quantization

M_STATE = Enum('wandering', 'pursuing', 'evading')
F_STATE = Enum('shooting', 'hitting', 'hold')
S_STATE = Enum('none', 'uncovered', 'shaking', 'attacking')

class StateMachine(object):
    """
    State machine. Handles a character state and behavior
    """

    def __init__(self, character):
        self.character = character
        self.moving_state = M_STATE.wandering
        self.last_moving_state = M_STATE.wandering
        self.fighting_state = F_STATE.hold
        self.scared_state = S_STATE.none
        self.dizzy = False
        # Collision behavior
        try:
            self.collision_group = self.character.behaviors['collision_avoidance']
            self.avoidance_manager = \
                    self.collision_group.behavior_set['Obstacle Avoidance']
            if not hasattr(self.avoidance_manager, 'args'): # This shouldn't happen!
                setattr(self.avoidance_manager, 'args', {})

        except KeyError:
            self.collision_group   = None
            self.avoidance_manager = None

    def _fuzzy_life(self, game):
        """
        Calculates the sight of pursuing or evading that the character
        has to have depending on his current energy. The more alive he
        is, the more he will pursue.
        """
        try:
            pursue = self.character.behaviors['pursue']
            evade  = self.character.behaviors['evade']
        except KeyError:
            return
        pursue = pursue.behavior_set['Pursue']
        evade  = evade.behavior_set['Evade']
        if not hasattr(pursue, 'args'):
            setattr(pursue, 'args', {})
        if not hasattr(evade, 'args'):
            setattr(evade, 'args', {})
        pursue.args['characters_sight'] = 40. * (self.character.energy / 100.)
        evade.args['characters_sight']  = 40. - pursue.args['characters_sight']

    def _still_dizzy(self):
        """
        Check if the character is still dizzy, calculating the dizzy begin time
        and dizzy duration, and comparing with the current time
        """
        current_time = pygame.time.get_ticks()
        begin_time, duration = self.character.dizzy
        return current_time - begin_time < duration

    def _check_sound_wave_collision(self, sound_wave):
        """
        Checks if the character has been hitted by a sound wave =S
        """
        if sound_wave is None:
            return False
        distance = ((sound_wave.position - Vector3(0., 5., 0.)) - \
                    self.character.position).length
        return self.character.radius + sound_wave.radius > distance

    def _fighting_tree(self, game):
                # 2. Updates character's fighting action state
        distance = (self.character.position - game.main_character.position).length
        
        # Check for hitting
        if distance < game.main_character.radius + 5 and \
               hit_detection(self.character, game.main_character): # FIX THIS WIRED CODE =S!
            self.fighting_state = F_STATE.hitting
        else:
            self.fighting_state = F_STATE.hold
            
        # Check for shooting (a.k.a. predicting physics)
        # Step 0. Simulate a bullet
        bullet = self.character.shoot()
        # Step 1. Get landing time of the bullet
        try:
            lt = (-bullet.velocity.y + \
                  sqrt(bullet.velocity.y - 2 * GRAVITY.y * bullet.position.y)) / \
                  GRAVITY.y
            # Step 2. Get position of impact
            pix = Vector3(bullet.position.x + bullet.velocity.x * lt,
                         0.,
                         bullet.position.z + bullet.velocity.z * lt)
            # Step 3. Intersects position of impact with target's radius
            bullet_trajectory = pix - self.character.position
            target_direction  = (game.main_character.position + \
                                 self.character.velocity * lt) - \
                                 self.character.position
            min_distance = target_direction - target_direction.projection(bullet_trajectory)
            if min_distance.length < self.character.radius and \
               target_direction.length < bullet_trajectory.length*13. and \
               abs(atan2(target_direction.x, target_direction.z) - \
               self.character.orientation) < pi/3:
                # We shoot!!
                self.fighting_state = F_STATE.shooting
                game.projectiles.append(bullet)
        except ValueError:
            pass
        if not self.fighting_state == F_STATE.hitting and not \
               self.fighting_state == F_STATE.shooting:
            self.fighting_state = F_STATE.hold

    def _moving_support(self):
        """
        Updates character's moving state
        """
        self.last_moving_state = self.moving_state
        if self.character.last_behavior == 'pursue':
            self.moving_state = M_STATE.pursuing
        if self.character.last_behavior == 'evade':
            self.moving_state = M_STATE.evading
        if self.character.last_behavior == 'wander':
            self.moving_state = M_STATE.wandering
        

    def update(self, game):
        """
        Updates the character's state and behavior.
        """
        # Check if the character is dizzy
        if self.character.is_dizzy:
            if self._still_dizzy():
                self.dizzy = True
                return self
            else:
                self.dizzy = False
                self.character.dizzy = None

        # Check if the character is hitted by some sound wave
        if self._check_sound_wave_collision(game.sound_wave):
            # Set dizzynes
            # First we need to calculate the level of dizzynes
            if game.sound_wave.intensity > self.character.hearing_umbral:
                dizzyness_level = 16000 * game.sound_wave.intensity / 100
                self.character.dizzy = (pygame.time.get_ticks(), dizzyness_level)
                return self

        # 1. Updates character's behavior
        self._fuzzy_life(game)

        # Check if the enemy is super powerfull
        if game.main_character.is_kicking_asses:
            # Was I attacking before?
            if self.scared_state == S_STATE.attacking:
                self._fighting_tree(game)
                if self.fighting_state != F_STATE.hold:
                    return self
                
            # Am I covered?
            my_waypoint = None
            for waypoint in game.level['waypoints']:
                localization_node = graph_quantization(self.character.position)
                if waypoint.main_node.id == localization_node.id and \
                   waypoint.taken == self.character:
                    # Yes i'm covered
                    self.scared_state = S_STATE.shaking
                    my_waypoint = waypoint
                else:
                    # No, i'm not!
                    # Is m enemy near to me?
                    if (self.character.position - game.main_character.position).length < 4:
                        self.scared_state = S_STATE.attacking
                    else:
                        self.scared_state = S_STATE.uncovered
                    return self

            if my_waypoint is not None:
                # Do I hear steps that came from an uncover location?
                for step in game.main_character.steps:
                    if self._check_sound_wave_collision(step) and \
                       step.intensity > self.character.hearing_umbral:
                        
                        node = graph_quantization(step.location)
                        if node.id in my_waypoint.uncover_form:
                            # Yes I hear them
                            self.scared_state = S_STATE.attacking
                    return self

        # NORMAL BEHAVIOR
        # 2. Fighting check
        self._fighting_tree(game)

        # 3. Moving support
        self._moving_support()

        return self

    def execute(self, game):
        """
        Tells the character to execute the corresponding action according to its
        state.
        """
        # Dizzyness
        if self.dizzy:
            return

        # When scared
        if self.scared_state == S_STATE.uncover:
            self.cover()
            return
        if self.scared_state == S_STATE.shaking:
            self.shake()
            return

        # When fighting
        if self.fighting_state == F_STATE.hitting:
            self.character.hit()
        if self.fighting_state == F_STATE.shooting:
            self.character.shoot()

        # When moving
        if self.moving_state == self.last_moving_state or \
           self.avoidance_manager is None:
            return # optimizing what's below

        if self.moving_state == M_STATE.wandering:
            self.avoidance_manager.args['look_ahead'] = 10.
            self.collision_group.priority = 5
        elif self.moving_state == M_STATE.pursuing:
            self.avoidance_manager.args['look_ahead'] = 4.
            self.collision_group.priority = 2
        else:
            self.avoidance_manager.args['look_ahead'] = 14.
            self.collision_group.priority = 5
