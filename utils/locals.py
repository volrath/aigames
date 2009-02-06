from physics.rect import Rect
from physics.vector3 import Vector3

# Game's local constants

SCREEN = Rect((0, 0), 1000, 700)
STAGE_SIZE = 20
MEDIA_PATH = 'media'
FPS = 60
GRAVITY = Vector3(0., -19.62, 0.)

# Character's constants
STANDARD_INITIAL_FORCE = 2.
FLOOR_FRICTION = 22.

# Steering constants
LOW_STEERING_UMBRAL = .2

# Presets camera positions
MAIN_VIEW = { 
    'position': { 'x': 0., 'y': 12., 'z': 54.5 },
    'view': { 'x': 0., 'y': 12.6, 'z': 0.1 }
    }
SIDE_VIEW = { 
    'position': { 'x': -26., 'y': 15.5, 'z': 37.5 },
    'view': { 'x': 2.3, 'y': 2.2, 'z': 0.1 }
    }
TOP_VIEW = {
    'position': { 'x': 0., 'y': 67.5, 'z': 0.7 },
    'view': { 'x': 0., 'y': 12.5, 'z': 0.1 }
    }
