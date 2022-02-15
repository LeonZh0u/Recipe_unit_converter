from collections import defaultdict

class NodeData(object):
    def __init__(self, key: int, unit: str):
        self.key = key
        self.unit = unit
            
class DiGraph:

    def __init__(self):
        self.Vertices = dict()
        self.Ni_in = dict()
        self.Ni_out = dict()
        self.__EdgeSize = 0
        self.unit_to_id = defaultdict(lambda:-1)

    def v_size(self) -> int:
        """
        Returns the number of vertices in this graph
        @return: The number of vertices in this graph
        """
        # or use self.Vertices.keys
        return len(self.Vertices)

    def e_size(self) -> int:
        return self.__EdgeSize

    def add_edge(self, id1: int, id2: int, weight: float) -> bool:
        
        if id1 not in self.Vertices or id2 not in self.Vertices or id2 in self.Ni_out[id1] or id1 in self.Ni_in[id2]:
            return False
        else:
            self.Ni_out[id1][id2] = weight
            self.Ni_in[id2][id1] = weight
            self.__EdgeSize += 1
            return True

    def add_node(self, node_id: int, unit :str) -> bool:
        if unit not in self.unit_to_id:
            self.unit_to_id[unit] = node_id
            self.Vertices[node_id] = NodeData(key=node_id, unit = unit)
            self.Ni_in[node_id] = {}
            self.Ni_out[node_id] = {}
            return True

        return False

    def remove_node(self, node_id: int) -> bool:
        if node_id not in self.Vertices:
            return False
        else:
            for nib_out in self.all_out_edges_of_node(node_id).copy():
                # Sends all the edges going out a given node_id to remove func
                self.remove_edge(node_id, nib_out)
                self.remove_edge(nib_out, node_id)
            for nib_in in self.all_in_edges_of_node(node_id).copy():
                # Sends all the edges going in a given node_id to remove func
                self.remove_edge(node_id, nib_out)
                self.remove_edge(nib_out, node_id)
            # Deletes the node_id itself from records
            del self.Ni_in[node_id]
            del self.Ni_out[node_id]
            del self.Vertices[node_id]
            self.__McCount += 1
            return True

    def remove_edge(self, node_id1: int, node_id2: int) -> bool:
        if node_id1 not in self.Ni_in[node_id2] or node_id2 not in self.Ni_out[node_id1]:
            return False
        else:
            del self.Ni_out[node_id1][node_id2]
            del self.Ni_in[node_id2][node_id1]
            self.__McCount += 1
            self.__EdgeSize -= 1
            return True
        
    def all_out_edges_of_node(self, id1: int) -> dict:
        return self.Ni_out[id1]
    
    def get_all_v(self) -> dict:
        return self.Vertices