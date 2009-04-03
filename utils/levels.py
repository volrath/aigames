from ai.graph import Node, WayPoint
from game_objects.stage import Obstacle, SideAmplificator, MainAmplificator
from physics.vector3 import Vector3
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
    (1, 2, 3, 4, 5),               # 0
    (0, 2, 5, 6),                  # 1
    (0, 1, 3),                     # 2
    (0, 2, 4, 15),                 # 3
    (0, 3, 5, 15),                 # 4
    (0, 4, 48, 0),                 # 5
    (1, 7),                        # 6
    (6, 9),                        # 7
    (9, 11),                       # 8
    (8, 7, 10),                    # 9
    (9, 11, 12),                   # 10
    (8, 10, 12),                   # 11
    (10, 11, 13, 17, 52, 53),                  # 12
    (12, 14, 23, 51, 52),                  # 13
    (13, 15, 23, 50, 51),                      # 14
    (14, 16, 3, 4, 51, 23),                   # 15
    (15, 50),                      # 16
    (12, 53, 18, 41, 43),                  # 17
    (17, 19, 42, 43),                      # 18
    (18, 20, 43, 42, 41, 53),                      # 19
    (19, 21),                      # 20
    (20, 22),                      # 21
    (21,),                         # 22
    (13, 14, 47, 51, 52, 15),              # 23
    (25, 26, 27, 28, 29),                         # 24
    (24, 30, 26, 29),                  # 25
    (25, 27, 24),                      # 26
    (26, 28, 39, 24),                  # 27
    (27, 29, 24, 39),                      # 28
    (28, 49, 24, 25),                      # 29
    (25, 31),                      # 30
    (30, 33),                      # 31
    (33, 35),                         # 32
    (32, 31, 34),                  # 33
    (33, 35, 36),                      # 34
    (34, 36, 32),                      # 35
    (35, 37, 41, 34, 52, 53),                  # 36
    (36, 38, 47, 51, 52),                  # 37
    (37, 39, 50, 51, 52),                      # 38
    (38, 40, 27, 28, 51, 47),                  # 39
    (39, 50),                      # 40
    (36, 42, 53, 17),                  # 41
    (41, 43, 18, 19),                      # 42
    (42, 44, 17, 18, 19, 53),                      # 43
    (43, 45, ),                      # 44
    (44, 46),                      # 45
    (45,),                         # 46
    (23, 37, 38, 51, 52, 39),              # 47
    (5, 49),                       # 48
    (48, 29),                      # 49
    (16, 40, 51, 14, 38),                  # 50
    (23, 47, 50, 52, 14, 38, 13, 37, 15, 39),              # 51
    (23, 47, 51, 53, 12, 13, 36, 37),              # 52
    (17, 41, 52, 19, 43),                  # 53
    ]

WAYPOINTS = [WayPoint(NODES[20], uncover_from=(17, 18, 19, 20, 21, 22)),
             WayPoint(NODES[44], uncover_from=(41, 42, 43, 44, 45, 46)),
             WayPoint(NODES[48], uncover_from=(3, 4, 5, 48, 49, 29)),
             WayPoint(NODES[49], uncover_from=(5, 48, 49, 27, 28, 29))]

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
    'waypoints': WAYPOINTS,
    'obstacles':  OBSTACLES,
    'enemies': [(Vector3(-28., 0., -24.), '#1'), (Vector3(28., 0., -24.),'#2'),
                (Vector3(0., 0., 24.), '#3')]
##     'enemies': [(Vector3(-28., 0., -24.), '#1'), (Vector3(28., 0., -24.), '#2'),
##                 (Vector3(-18.2, 0., 14.43),'#3'), (Vector3(18.2, 0., 14.43),'#4')],
    }
