from physics.rect import Rect
from physics.vector3 import Vector3

# Game's local constants

SCREEN = Rect((0, 0), 1000, 700)
STAGE_SIZE = 30
MEDIA_PATH = 'media'
FPS = 60
GRAVITY = Vector3(0., -39.24, 0.)
NEW_ENEMY_TIME = 90000

# Character's constants
STANDARD_INITIAL_FORCE = 8.
KINETIC_FRICTION_COEFICIENT = 1.2
SUPER_POWERFULL_TIME = 40000
STEP_FRAME = 2500

# Steering constants
LOW_STEERING_UMBRAL = .2
IMPACT_ORIENTATION_UMBRAL = .4

# Presets camera positions
MAIN_VIEW = { 
    'position': { 'x': 0., 'y': 20., 'z': 67. },
    'view': { 'x': 0., 'y': 12.6, 'z': 2.5 }
    }
SIDE_VIEW = { 
    'position': { 'x': -32.5, 'y': 8.5, 'z': 52.5 },
    'view': { 'x': 0., 'y': 12.6, 'z': 2.5 }
    }
TOP_VIEW = {
    'position': { 'x': 0., 'y': 79.5, 'z': 0.7 },
    'view': { 'x': 0., 'y': 1.5, 'z': 0.1 }
    }
