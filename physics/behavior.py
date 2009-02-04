from physics.steering_behaviors import *

class Behavior:
    """
    Character's behavior
    """
    def __init__(self, name, handler, character=None, target=None, args={}):
        self.name = name
        self.handler = handler
        self.character = character
        self.target = target
        self.args = args

    def execute(self):
        if self.target:
            return self.handler(character=self.character,
                                target=self.target, **self.args)
        else:
            return self.handler(character=self.character, **self.args)

    def __str__(self):
        return self.name

# Current behaviors
PURSUE = Behavior('Pursue', pursue_and_stop)
EVADE  = Behavior('Evade', evade)
WANDER = Behavior('Wander', Wander().execute)
FACE   = Behavior('Face', face)
