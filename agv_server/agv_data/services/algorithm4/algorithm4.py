from ...models import Agv
from map_data.models import Connection
from django.db.models import Q


class BackupNodesAllocator:
    """
    Algorithm 4: Dynamic Backup Nodes Allocation Service

    This class implements the backup nodes allocation strategy from DSPA algorithm.
    It allocates backup nodes for AGVs based on their adjacent common nodes (sequential shared points).
    """

    def __init__(self, agv: Agv):
        self.agv = agv

    def allocate_backup_nodes(self):
        """
        Main method to allocate backup nodes for the AGV.

        For each node in adjacent_common_nodes:
        1. Find connected free nodes (not in any other AGV's remaining_path)
        2. Select the closest free node as backup node

        Returns:
            dict: Mapping of {node: backup_node} for successful allocations
        """
        backup_nodes = {}

        # Get the AGV's adjacent common nodes (sequential shared points)
        adjacent_common_nodes = self.agv.adjacent_common_nodes

        if not adjacent_common_nodes:
            return backup_nodes

        # Get remaining paths of all other AGVs to identify occupied nodes
        occupied_nodes = self._get_occupied_nodes_by_other_agvs()        # For each node in adjacent_common_nodes, find backup node
        for node in adjacent_common_nodes:
            backup_node = self._find_backup_node_for(node, occupied_nodes)
            if backup_node is not None:
                # Convert node to string since JSON dictionary keys must be strings
                backup_nodes[str(node)] = backup_node

        return backup_nodes

    def _get_occupied_nodes_by_other_agvs(self):
        """
        Get all nodes that are in remaining_path of other AGVs.

        Returns:
            set: Set of nodes that are occupied by other AGVs
        """
        occupied_nodes = set()

        # Get all other AGVs (excluding current AGV)
        other_agvs = Agv.objects.exclude(agv_id=self.agv.agv_id)

        for other_agv in other_agvs:
            if other_agv.remaining_path:
                occupied_nodes.update(other_agv.remaining_path)

        return occupied_nodes

    def _find_backup_node_for(self, node, occupied_nodes):
        """
        Find the closest free backup node for a given node.

        Args:
            node (int): The node for which to find a backup
            occupied_nodes (set): Set of nodes occupied by other AGVs

        Returns:
            int or None: The backup node if found, None otherwise
        """
        # Get all nodes connected to the given node
        connected_nodes = self._get_connected_nodes(node)

        # Filter out occupied nodes to get free nodes
        free_nodes = [n for n in connected_nodes if n not in occupied_nodes]

        if not free_nodes:
            return None

        # Find the closest free node (by shortest distance)
        closest_node = self._get_closest_node(node, free_nodes)

        return closest_node

    def _get_connected_nodes(self, node):
        """
        Get all nodes that are directly connected to the given node.

        Args:
            node (int): The node to find connections for

        Returns:
            list: List of connected node IDs
        """
        # Query connections where node is either node1 or node2
        connections = Connection.objects.filter(
            Q(node1=node) | Q(node2=node)
        )

        connected_nodes = []
        for connection in connections:
            # Add the other node in the connection
            if connection.node1 == node:
                connected_nodes.append(connection.node2)
            else:
                connected_nodes.append(connection.node1)

        return connected_nodes

    def _get_closest_node(self, reference_node, candidate_nodes):
        """
        Find the closest node to the reference node from a list of candidates.

        Args:
            reference_node (int): The reference node
            candidate_nodes (list): List of candidate nodes

        Returns:
            int: The closest node ID
        """
        if not candidate_nodes:
            return None

        if len(candidate_nodes) == 1:
            return candidate_nodes[0]

        # Find the connection with minimum distance
        min_distance = float('inf')
        closest_node = None

        for candidate in candidate_nodes:
            # Try to find connection in both directions
            connection = Connection.objects.filter(
                Q(node1=reference_node, node2=candidate) |
                Q(node1=candidate, node2=reference_node)
            ).first()

            if connection and connection.distance < min_distance:
                min_distance = connection.distance
                closest_node = candidate

        return closest_node

    def apply_for_backup_nodes(self):
        """
        Apply for backup nodes and update the AGV's backup_nodes field.
        This is the main interface method to be called from the control policy.

        Returns:
            bool: True if backup nodes were successfully allocated, False otherwise
        """
        # Allocate backup nodes
        backup_nodes = self.allocate_backup_nodes()

        # Update AGV's backup_nodes field
        self.agv.backup_nodes = backup_nodes
        self.agv.spare_flag = True
        self.agv.save(update_fields=['backup_nodes', 'spare_flag'])

        # # Return True if any backup nodes were allocated
        # return len(backup_nodes) > 0
