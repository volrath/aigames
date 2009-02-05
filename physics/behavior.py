from physics.steering_behaviors import *

class Behavior:
    """
    Character's behavior
    """
    def __init__(self, name, handler, method=None, character=None, target=None, args={}):
        self.name = name
        if method is not None:
            self.handler = handler()
            self.handler = getattr(self.handler, method)
        else:
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
PURSUE = { 'name': 'Pursue', 'handler': pursue_and_stop }
EVADE  = { 'name': 'Evade', 'handler': evade }
WANDER = { 'name': 'Wander', 'handler': Wander, 'method':'execute' }
FACE   = { 'name': 'Face', 'handler': face }
