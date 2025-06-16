from ...models import Agv


class ControlPolicy:
    """
    Algorithm 2: DSPA Control Policy

    This class implements the control policy that determines how AGVs should move
    based on their current state and the state of other AGVs in the system.
    """

    def __init__(self, agv: Agv):
        self.agv = agv

    # === Position and Path Updates ===

    def update_position_info(self, current_node):
        """
        Update all position-related information when AGV reaches a new node.

        Args:
            current_node (int): The new current position of the AGV
        """
        self._update_node_positions(current_node)
        self._update_path_info(current_node)
        self._update_shared_nodes(current_node)

    def _update_node_positions(self, current_node):
        """Update current and previous node positions."""
        if self.agv.current_node is not None:
            self.agv.previous_node = self.agv.current_node

        self.agv.current_node = current_node
        self.agv.save(update_fields=['current_node', 'previous_node'])

    def _update_path_info(self, current_node):
        """Update remaining path and next node based on current position."""
        # Remove current node from remaining path if it matches
        if (self.agv.remaining_path and
            len(self.agv.remaining_path) > 0 and
                current_node == self.agv.remaining_path[0]):

            self.agv.remaining_path = self.agv.remaining_path[1:]
            self.agv.save(update_fields=['remaining_path'])

        # Update next node based on remaining path
        if self.agv.remaining_path and len(self.agv.remaining_path) > 0:
            self.agv.next_node = self.agv.remaining_path[0]
            self.agv.save(update_fields=['next_node'])

    def _update_shared_nodes(self, current_node):
        """Update common nodes and adjacent common nodes when reaching a node."""
        self._remove_from_shared_nodes(current_node, 'common_nodes')
        self._remove_from_shared_nodes(current_node, 'adjacent_common_nodes')
        self._cleanup_insufficient_adjacent_nodes()

    def _remove_from_shared_nodes(self, node, field_name):
        """Remove node from shared node lists of this and other AGVs if appropriate."""
        # Remove from this AGV's list
        shared_nodes = getattr(self.agv, field_name)
        if node in shared_nodes:
            shared_nodes.remove(node)
            setattr(self.agv, field_name, shared_nodes)
            self.agv.save(update_fields=[field_name])

        # Check other AGVs with this node in their shared nodes
        filter_kwargs = {f"{field_name}__contains": [node]}
        other_agvs_with_node = Agv.objects.filter(
            **filter_kwargs).exclude(agv_id=self.agv.agv_id)

        # If only one or no other AGV has this node, remove it from them too
        if other_agvs_with_node.count() <= 1:
            for other_agv in other_agvs_with_node:
                other_shared_nodes = getattr(other_agv, field_name)
                if node in other_shared_nodes:
                    other_shared_nodes.remove(node)
                    setattr(other_agv, field_name, other_shared_nodes)
                    other_agv.save(update_fields=[field_name])

    def _cleanup_insufficient_adjacent_nodes(self):
        """Clear adjacent_common_nodes for all AGVs if they have less than 2 nodes."""
        for agv in Agv.objects.all():
            if len(agv.adjacent_common_nodes) < 2:
                agv.adjacent_common_nodes = []
                agv.save(update_fields=['adjacent_common_nodes'])

    # === Movement Decision Logic ===

    def can_move_freely(self):
        """
        Check if AGV can move without any restrictions.
        This covers movement conditions 1 and 2 from the original algorithm.
        """
        if not self.agv.next_node:
            return False

        reserved_nodes = self._get_reserved_nodes_by_others()

        # Condition 1: Next node not reserved and not in adjacent common nodes
        if (self.agv.next_node not in reserved_nodes and
                self.agv.next_node not in self.agv.adjacent_common_nodes):
            return True

        # Condition 2: Next node in adjacent common nodes but safe to move
        if (self.agv.next_node not in reserved_nodes and
                self.agv.next_node in self.agv.adjacent_common_nodes):

            reserved_by_non_spare = self._get_reserved_nodes_by_others(
                spare_flag=False)
            adjacent_nodes_blocked = any(
                node in reserved_by_non_spare
                for node in self.agv.adjacent_common_nodes
            )
            return not adjacent_nodes_blocked

        return False

    def should_use_backup_nodes(self):
        """Check if backup node handling is needed."""
        reserved_nodes = self._get_reserved_nodes_by_others()
        return self.agv.next_node not in reserved_nodes

    def can_move_with_backup(self):
        """Check if AGV can move after backup node allocation (condition 3)."""
        if not self.agv.backup_nodes:
            return False

        reserved_nodes = self._get_reserved_nodes_by_others()
        reserved_by_non_spare = self._get_reserved_nodes_by_others(
            spare_flag=False)

        adjacent_nodes_blocked = any(
            node in reserved_by_non_spare
            for node in self.agv.adjacent_common_nodes
        )

        return (self.agv.next_node not in reserved_nodes and
                self.agv.next_node in self.agv.adjacent_common_nodes and
                adjacent_nodes_blocked)

    # === State Management ===

    def set_moving_state(self):
        """Set AGV to moving state without backup nodes."""
        self.agv.motion_state = Agv.MOVING
        self.agv.spare_flag = False
        self.agv.backup_nodes = {}
        self.agv.reserved_node = self.agv.next_node
        self.agv.save(
            update_fields=['motion_state', 'spare_flag', 'backup_nodes', 'reserved_node'])

    def set_moving_with_backup_state(self):
        """Set AGV to moving state with backup nodes."""
        self.agv.motion_state = Agv.MOVING
        self.agv.spare_flag = True
        self.agv.reserved_node = self.agv.next_node
        self.agv.save(update_fields=['motion_state',
                      'spare_flag', 'reserved_node'])

    def set_waiting_state(self):
        """Set AGV to waiting state."""
        self.agv.motion_state = Agv.WAITING
        self.agv.save(update_fields=['motion_state'])

    # === Backup Node Management ===

    def cleanup_current_backup_node(self):
        """Remove backup node associated with current position."""
        if (self.agv.current_node is not None and
                str(self.agv.current_node) in self.agv.backup_nodes):

            backup_nodes_copy = dict(self.agv.backup_nodes)
            backup_nodes_copy.pop(str(self.agv.current_node))
            self.agv.backup_nodes = backup_nodes_copy
            self.agv.save(update_fields=['backup_nodes'])

    # === Helper Methods ===

    def _get_reserved_nodes_by_others(self, spare_flag=None):
        """
        Get reserved nodes from other AGVs, optionally filtered by spare_flag.

        Args:
            spare_flag (bool, optional): Filter by spare_flag value

        Returns:
            list: List of reserved nodes
        """
        other_agvs = Agv.objects.exclude(agv_id=self.agv.agv_id)

        if spare_flag is not None:
            other_agvs = other_agvs.filter(spare_flag=spare_flag)

        return [
            agv.reserved_node for agv in other_agvs
            if agv.reserved_node is not None
        ]
