from ai.graph import Node
from physics.vector3 import Vector3

NODES = map(Node, [
    Vector3(0., 0., -15.),
    Vector3(0., 0., 15.),
    Vector3(-15., 0., 0.),
    Vector3(15., 0., 0.),
    ])

NUMBER_OF_NODES = 0
for node in NODES:
    node.id = NUMBER_OF_NODES
    NUMBER_OF_NODES += 1

NEIGHBORS = [
    (3,),
    (2, 3,),
    (1, 3,),
    (0, 1, 2,),
    ]
