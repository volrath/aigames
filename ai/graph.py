class CostMatrix(object):
    """
    Class that stores the precalculated distance between all the nodes.
    Its main goal is to establish an O(1) access to the cost<distance>
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

    def load(self):
        """
        Loads the manhattan cost between all the nodes
        """
        self.cost = CostMatrix(self.nodes)
