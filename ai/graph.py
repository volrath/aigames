class CostMatrix(object):
    """
    Class that stores the precalculated distance between all the nodes.
    Its main goal is to stablish an O(1) access to the cost<distance>
    between two given node's locations
    """
    def __init__(self, node_list):
        self.costs = []
        for node1 in node_list:
            mcost = []
            for node2 in node_list:
                mcost.append((node1.location - node2.location).length)
            self.costs.append(mcost)

    def __getitem__(self, key):
        """
        Key most be a tuple
        """
        i, j = key
        return self.costs[i][j]


class PathMatrix(object):
    """
    Class that stores the precalculated A* path between all the nodes for
    stablishing an O(1) access to the best path between two locations
    """
    def __init__(self, a_star):
        """
        """
        self.paths = []
        for node1 in a_star.graph.nodes:
            mpath = []
            for node2 in a_star.graph.nodes:
                mpath.append(a_star.get_route(node1.id, node2.id))
            self.paths.append(mpath)

    def __getitem__(self, key):
        """
        Key most be a tuple
        """
        i, j = key
        return self.paths[i][j]


class Node(object):
    """
    A node.
    """
    def __init__(self, location, node_id=None):
        """
        """
        self.location = location
        self.id = node_id

    def __str__(self):
        return "Node<%s> at (%s, %s)" % (self.id, self.location.x, self.location.z)
    __repr__ = __str__


class Graph(object):
    """
    Graph made of an adjacency list
    """
    def __init__(self, size, node_list, path_list):
        self.size  = size
        self.nodes = node_list
        self.paths = path_list

    def load(self, a_star):
        """
        Loads the euclidean cost and the A* path between all the nodes.
        """
        self.cost = CostMatrix(self.nodes)
        self.path = PathMatrix(a_star)


class WayPoint(object):
    """
    A special tactical node
    """
    def __init__(self, main_node, uncover_from=[]):
        self.main_node    = main_node
        self.uncover_from = uncover_from
        self.taken = None

    @property
    def is_taken(self):
        return self.taken is not None

    @classmethod
    def find_closest_for(cls, character, game):
        """
        Find the closest waypoint to cover for a character in the game, but it
        dismiss all the waypoints that are closer to other AI allies.
        """
        def euclidean_sort(wp1, wp2):
            dwp1 = (character.position - wp1.main_node.location).length
            dwp2 = (character.position - wp2.main_node.location).length
            return cmp(dwp1, dwp2)
        waypoints = game.level['waypoints']
        waypoints.sort(euclidean_sort)
        for wp in waypoints:
            if not wp.is_taken:
                return wp
