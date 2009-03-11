from heapq import heappop, heappush
from ai.graph import *

class NodeHolder(object):
    """
    """
    def __init__(self, node, parent, cost, heuristic):
        self.node      = node
        self.parent    = parent
        self.cost      = cost
        self.heuristic = heuristic

    def __lt__(self, other):
        return (self.cost + self.heuristic) < (other.cost + other.heuristic)

    def __le__(self, other):
        return (self.cost + self.heuristic) <= (other.cost + other.heuristic)

    def __gt__(self, other):
        return (self.cost + self.heuristic) > (other.cost + other.heuristic)

    def __lt__(self, other):
        return (self.cost + self.heuristic) >= (other.cost + other.heuristic)

    def __iter__(self):
        return iter((self.node, self.parent, self.cost, self.heuristic))


class AStar(object):
    """
    Class that implement A* algorithm
    """
    def __init__(self, graph):
        self.graph = graph
        self.visited = [-1 for x in range(0, self.graph.size)]

    def get_route(self, start, end):
        """
        (node_id, parent_id, cost)
        """
        self.visited = [-1 for x in range(0, self.graph.size)]
        open_nodes = []
        im_here = False
        heappush(open_nodes, NodeHolder(start, start, 0, self.graph.cost[start, end]))
        while open_nodes:
            aux_node, aux_parent, aux_cost, _ = heappop(open_nodes)
            if aux_node == end:
                im_here = True
                break
            if self.visited[aux_node] != -1:
                continue
            self.visited[aux_node] = aux_parent
            for neighbor in self.graph.paths[aux_node]:
                if neighbor != aux_parent:
                    heappush(open_nodes,
                             NodeHolder(neighbor, aux_node,
                                        aux_cost + self.graph.cost[aux_node, neighbor],
                                        self.graph.cost[neighbor, end]))
        self.visited[aux_node] = aux_parent
        return {
            'path': self.retrieve_from_parents(start, [aux_node]),
            'im_here': im_here,
            'cost': aux_cost
            }

    def retrieve_from_parents(self, start, acc):
        """
        """
        if acc[0] == start:
            self.visited[acc[0]] = -1
            return acc
        else:
            new_p = self.visited[acc[0]]
            self.visited[acc[0]] = -1
            acc.insert(0, new_p)
            return self.retrieve_from_parents(start, acc)
