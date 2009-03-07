from heapq import heappop, heappush
from ai.graph import *

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
        open_nodes = []
        heappush(open_nodes, (0, (start, start)))
        while open_nodes:
            aux_cost, (aux_node, aux_parent) = heappop(open_nodes)
            if aux_node == end:
                break
            if self.visited[aux_node] != -1:
                continue
            self.visited[aux_node] = aux_parent
            for neighbor in self.graph.paths[aux_node]:
                if neighbor != aux_parent:
                    heappush(open_nodes,
                             (aux_cost + self.graph.cost[aux_node, neighbor], \
                              (neighbor, aux_node)))
        self.visited[aux_node] = aux_parent
        return {
            'path': self.retrieve_from_parents(start, [aux_node]),
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
