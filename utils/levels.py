from game_objects.stage import Obstacle, SideAmplificator, MainAmplificator
from physics.vector3 import Vector3
from ai.graph import Node
from physics.vector3 import Vector3

SECTORS = [
    ((-30, -30), (-24, -30), (-30, -13.3)),        # 0
    ((-30, -13.3), (-24, -30), (-24, -13.3)),
    ((-24, -13.3), (-19, -13.3), (-24, -30)),
    ((-24, -30), (-19, -13.3), (-9, -17.5)),
    ((-9, -17.5), (-24, -30), (-6.3, -23.5)),      # 4
    ((-6.3, -23.5), (-6.3, -30), (-24, -30)),
    ((-24, -13.3), (-30, -13.3), (-24, 7.9)),
    ((-30, -13.3), (-24, 7.9), (-30, 7.9)),
    ((-30, 7.9), (-30, 21.6), (-20.8, 17.7)),
    ((-20.8, 17.7), (-30, 7.9), (-24, 7.9)),       # 9
    ((-24, 7.9), (-20.8, 17.7), (-19, 7.9)),
    ((-19, 7.9), (-20.8, 17.7), (-14.8, 17.7)),
    ((-14.8, 17.7), (-19, 7.9), (-9, 9.7)),
    ((-19, 7.9), (-9, 9.7), (-9, -8.3)),
    ((-9, -8.3), (-19, 7.9), (-19, -13.3)),       # 14
    ((-19, -13.3), (-9, -8.3), (-9, -17.5)),
    ((-9, -17.5), (-9, -8.3), (0, -12.4)),
    ((-9,  9.7), (-14.8, 17.7), (0, 30)),
    ((-14.8, 17.7), (0, 30), (-14.8, 23.7)),
    ((-14.8, 23.7), (0, 30), (-18.3, 30)),        # 19
    ((-14.8, 23.7), (-18.3, 30), (-25.7, 26.8)),
    ((-25.7, 26.8), (-18.3, 30), (-30, 30)),
    ((-30, 30), (-25.7, 26.8), (-30, 21.6)),
    ((-9, -8.3), (-9, 9.7), (0, .7)),
    ]
symmetric_sectors = []
for sector in SECTORS:
    symetric = ()
    for side in sector:
        side = tuple(map(float, side))
        symetric += ((side[0] * -1, side[1]),)
    symmetric_sectors.append(symetric)
SECTORS.extend(symmetric_sectors)

# Add the unsymmetrical sectors
SECTORS.extend([
    ((-6.3, -30.), (6.3, -30.), (-6.3, -23.5)),      # 48
    ((-6.3, -23.5), (6.3, -30.), (6.3, -23.5)),
    ((-9., -8.3), (9., -8.3), (0, -12.4)),
    ((-9., -8.3), (9., -8.3), (0, .7)),
    ((-9., 9.7), (9., 9.7), (0, .7)),
    ((-9., 9.7), (9., 9.7), (0, 30.)),
    ])

NODES = []
NUMBER_OF_NODES = 0
for sector in SECTORS:
    s1, s2, s3 = sector
    NODES.append(Node(location=Vector3(((s1[0] + s2[0] + s3[0])/3),
                                       0.,
                                       ((s1[1] + s2[1] + s3[1])/3)),
                      node_id=NUMBER_OF_NODES))
    NUMBER_OF_NODES +=1

NEIGHBORS = [
    (1,),           # 0
    (0, 2, 6),
    (1, 3),
    (2, 4, 15),
    (3, 5),         # 4
    (4, 48),
    (1, 7),
    (6, 9),
    (9,),
    (8, 7, 10),     # 9
    (9, 11),
    (10, 12),
    (11, 13, 17),
    (12, 14, 23),
    (13, 15),       # 14
    (14, 16, 3),
    (15, 50),
    (12, 53, 18),
    (17, 19),
    (18, 20),       # 19
    (19, 21),
    (20, 22),
    (21,),
    (13, 47, 51, 52),
    (25,),          # 24
    (24, 30, 26),
    (25, 27),
    (26, 28, 39),
    (27, 29),
    (28, 49),       # 29
    (25, 31),
    (30, 33),
    (33,),
    (32, 31, 34),
    (33, 35),       # 34
    (34, 36),
    (35, 37, 41),
    (36, 38, 47),
    (37, 39),
    (38, 40, 27),   # 39
    (39, 50),
    (36, 42, 53),
    (41, 43),
    (42, 44),
    (43, 45),       # 44
    (44, 46),
    (45,),
    (23, 37, 51, 52),
    (5, 49),
    (48, 29),       # 49
    (16, 40, 51),
    (23, 47, 50, 52),
    (23, 47, 51, 53),
    (17, 41, 52),
    ]

OBSTACLES = [
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
    ]

LEVEL = {
    'sectors': SECTORS,
    'nodes': NODES,
    'number_of_nodes': NUMBER_OF_NODES,
    'neighbors': NEIGHBORS,
    'obstacles':  OBSTACLES,
    'enemies': [Vector3(-9., 0., 15.), Vector3(9., 0., 15.)],
    }
