from utils.enum import Enum

STATE = Enum('shooting', 'hitting', 'hold')

class StateMachine(object):
    """
    State machine. Handles a character state and behavior
    """

    def __init__(self, character):
        self.character = character
        self.state = STATE.hold


    def fuzzy_life(self, game):
        """
        Calculates the sight of pursuing or evading that the character
        has to have depending on his current energy. The more alive he
        is, the more he will pursue.
        """
        try:
            pursue_evade = self.character.behaviors['pursue_evade']
        except KeyError:
            return
        pursue = pursue_evade.behavior_set['Pursue']
        evade  = pursue_evade.behavior_set['Evade']
        if not hasattr(pursue, 'args'):
            setattr(pursue, 'args', {})
        if not hasattr(evade, 'args'):
            setattr(evade, 'args', {})
        pursue.args['characters_sight'] = 40. * (self.character.energy / 100.)
        evade.args['characters_sight']  = 40. - pursue.args['characters_sight']

    def update(self, game):
        """
        Updates the character's state and behavior.
        """
        # 1. Updates character's behavior
        self.fuzzy_life(game)

        # 2. Updates character's action state
        distance = (self.character.position - game.main_character.position).length
        
        # Check for hitting
        if distance < game.main_character.radius + 5 and \
               hit_detection(self.character, game.main_character): # FIX THIS WIRED CODE =S!
            self.state = STATE.hitting
            
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
            if min_distance.length < character.radius and \
               target_direction.length < bullet_trajectory.length*9.3 and \
               abs(abs(atan2(target_direction.x, target_direction.z)) - \
               self.character.orientation) < pi/3:
                # We shoot!!
                self.state == STATE.shooting
                game.projectiles.append(bullet)
        except ValueError:
            pass
        if not self.state == STATE.hitting and not self.state == STATE.shooting:
            self.state = STATE.hold
        return self

    def execute(self):
        """
        Tells the character to execute the corresponding action according to its
        state.
        """
        if self.state == STATE.hitting:
            self.character.hit()
        if self.state == STATE.shooting:
            self.character.shoot()
