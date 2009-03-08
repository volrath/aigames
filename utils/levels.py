from game_objects.stage import Obstacle, SideAmplificator, MainAmplificator
from physics.vector3 import Vector3

LEVELS = (
    [
    # Side Amps
    SideAmplificator(position=Vector3(-21.5, 0., -10.8)),
    SideAmplificator(position=Vector3(-21.5, 0., -5.4)),
    SideAmplificator(position=Vector3(-21.5, 0., 0.)),
    SideAmplificator(position=Vector3(-21.5, 0., 5.4)),
    SideAmplificator(position=Vector3(21.5, 0., -10.8)),
    SideAmplificator(position=Vector3(21.5, 0., -5.4)),
    SideAmplificator(position=Vector3(21.5, 0., 0.)),
    SideAmplificator(position=Vector3(21.5, 0., 5.4)),
    # Main Amps
    MainAmplificator(position=Vector3(-17.8, 0., 20.7), rotation=0.),
    MainAmplificator(position=Vector3(-24.8, 0., 22.7), rotation=30.),
    MainAmplificator(position=Vector3(17.8, 0., 20.7), rotation=0.),
    MainAmplificator(position=Vector3(24.8, 0., 22.7), rotation=-30.),
    # Drums
    Obstacle(size=7, position=Vector3(-2.7, 0., -18.4), color=(164/255., 95/255., 21/255.), rotation=-30.),
    Obstacle(size=7, position=Vector3(2.7, 0., -18.4), color=(164/255., 95/255., 21/255.), rotation=30.),
    ],
    )
