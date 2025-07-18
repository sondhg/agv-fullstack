from ...models import Agv
from map_data.models import Connection
from django.db.models import Q


class BackupNodesAllocator:
    """
    Algorithm 4: Dynamic Backup Nodes Allocation Service

    This class implements the backup nodes allocation strategy from DSPA algorithm.
    It allocates backup nodes for AGVs based on their adjacent common nodes
    (sequential shared points) to provide alternative paths during conflicts.
    """

    def __init__(self, agv: Agv):
        self.agv = agv

    # === Public Interface ===

    def allocate_backup_nodes(self):
        """
        Allocate backup nodes for the AGV and update its state.

        This is the main interface method that should be called to allocate
        backup nodes for an AGV.

        Returns:
            bool: True if backup nodes were successfully allocated
        """
        backup_nodes = self._find_backup_nodes()

        # Update AGV with allocated backup nodes
        self.agv.backup_nodes = backup_nodes
        self.agv.spare_flag = True
        self.agv.save(update_fields=["backup_nodes", "spare_flag"])

        return len(backup_nodes) > 0

    # === Private Implementation ===

    def _find_backup_nodes(self):
        """
        Find backup nodes for all adjacent common nodes of this AGV.

        For each node in adjacent_common_nodes:
        1. Find connected free nodes (not occupied by other AGVs)
        2. Select the closest free node as backup node

        Returns:
            dict: Mapping of {node: backup_node} for successful allocations
        """
        backup_nodes = {}

        if not self.agv.adjacent_common_nodes:
            return backup_nodes

        occupied_nodes = self._get_nodes_occupied_by_others()

        for node in self.agv.adjacent_common_nodes:
            backup_node = self._find_best_backup_for_node(node, occupied_nodes)
            if backup_node is not None:
                backup_nodes[str(node)] = backup_node

        return backup_nodes

    def _get_nodes_occupied_by_others(self):
        """
        Get all nodes that are currently occupied by other AGVs.

        A node is considered occupied if it's in another AGV's remaining_path.

        Returns:
            set: Set of nodes occupied by other AGVs
        """
        occupied_nodes = set()

        other_agvs = Agv.objects.exclude(agv_id=self.agv.agv_id)

        for agv in other_agvs:
            if agv.remaining_path:
                occupied_nodes.update(agv.remaining_path)

        return occupied_nodes

    def _find_best_backup_for_node(self, node, occupied_nodes):
        """
        Find the best backup node for a given node.

        The best backup node is the closest free node that is directly
        connected to the given node.

        Args:
            node (int): The node to find a backup for
            occupied_nodes (set): Set of nodes occupied by other AGVs

        Returns:
            int or None: The best backup node, or None if none available
        """
        connected_nodes = self._get_directly_connected_nodes(node)
        free_nodes = [n for n in connected_nodes if n not in occupied_nodes]

        if not free_nodes:
            return None

        return self._find_closest_node(node, free_nodes)

    def _get_directly_connected_nodes(self, node):
        """
        Get all nodes that are directly connected to the given node.

        Args:
            node (int): The node to find connections for

        Returns:
            list: List of directly connected node IDs
        """
        connections = Connection.objects.filter(Q(node1=node) | Q(node2=node))

        connected_nodes = []
        for connection in connections:
            # Add the other node in each connection
            other_node = (
                connection.node2 if connection.node1 == node else connection.node1
            )
            connected_nodes.append(other_node)

        return connected_nodes

    def _find_closest_node(self, reference_node, candidate_nodes):
        """
        Find the closest node to the reference node from candidates.

        Closeness is determined by the distance field in the Connection model.

        Args:
            reference_node (int): The reference node
            candidate_nodes (list): List of candidate nodes

        Returns:
            int or None: The closest node ID, or None if no valid connection
        """
        if not candidate_nodes:
            return None

        if len(candidate_nodes) == 1:
            return candidate_nodes[0]

        closest_node = None
        min_distance = float("inf")

        for candidate in candidate_nodes:
            connection = Connection.objects.filter(
                Q(node1=reference_node, node2=candidate)
                | Q(node1=candidate, node2=reference_node)
            ).first()

            if connection and connection.distance < min_distance:
                min_distance = connection.distance
                closest_node = candidate

        return closest_node
