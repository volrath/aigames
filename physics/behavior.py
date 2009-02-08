from utils.locals import LOW_STEERING_UMBRAL
from physics.steering_behaviors import *
from physics.vector3 import Vector3

class Behavior(object):
    """
    Character's behavior
    """
    def __init__(self, name, weight, handler, active, method=None,
                 character=None, target=None, args={}):
        self.name = name
        self.weight = weight
        self.character = character
        self.target = target
        self.args = args
        self.method = method
        if method is not None:
            self.handler = handler(character=character, target=target, **args)
            self.handler = getattr(self.handler, method)
        else:
            self.handler = handler

    def execute(self):
        if self.method is not None:
            return self.handler()
        if self.target is not None:
            return self.handler(character=self.character,
                                target=self.target, **self.args)
        else:
            return self.handler(character=self.character, **self.args)

    def __str__(self):
        return self.name

class BehaviorGroup(object):
    def __init__(self, name, b_set, default_priority):
        self.name = name
        self.behavior_set = set(b_set)
        self.priority = default_priority

    def execute(self):
        """
        Executes all the behaviors in it and returns the total steering
        and, maybe, a dinamic priority
        """
        total_steering = { 'linear': Vector3(), 'angular': 0, }
        for behavior in self.behavior_set:
            b_steering = behavior.execute()
            if b_steering is None:
                continue
            if b_steering.has_key('linear'):
                total_steering['linear'] += b_steering['linear']
            if b_steering.has_key('angular'):
                total_steering['angular'] += b_steering['angular']

        if total_steering['linear'].length <= LOW_STEERING_UMBRAL and \
           total_steering['angular'] <= LOW_STEERING_UMBRAL:
            return None
        return { 'steering': total_steering, 'priority': self.priority, 'name': self.name }

# Current behaviors
PURSUE = { 'name': 'Pursue', 'weight': 3, 'handler': pursue_and_stop }
EVADE  = { 'name': 'Evade', 'weight': 3, 'handler': evade }
WANDER = { 'name': 'Wander', 'weight': 1, 'handler': Wander, 'method': 'execute' }
FACE   = { 'name': 'Face', 'weight': 2, 'handler': face }
LOOK_WHERE_YOU_ARE_GOING = { 'name': 'Look', 'weight': 2, 'handler': look_where_you_are_going }
SEPARATION = { 'name': 'Separation', 'weight': 5, 'handler': Separation, 'method': 'execute' }
OBSTACLE_AVOIDANCE = {'name': 'Obstacle Avoidance', 'weight': 5, 'handler': ObstacleAvoidance, 'method': 'execute'}
#COLLISION_AVOIDANCE = { 'name': 'Collision Avoidance', 'weight': 5, 'handler': CollisionAvoidance, 'method': 'execute' }

# DEFAULT GROUPS
COLLISION_AVOIDANCE_GROUP = {
    'name': 'collision_avoidance',
    'default_priority': 5,
}
PURSUE_EVADE_GROUP = {
    'name': 'pursue_evade',
    'default_priority': 3
}
WANDER_GROUP = {
    'name': 'wander',
    'default_priority': 1
}
