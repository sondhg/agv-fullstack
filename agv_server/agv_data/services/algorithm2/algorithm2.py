from ...models import Agv


class ControlPolicy:
    def __init__(self, agv: Agv):
        self.agv = agv

    def update_current_node_and_previous_node(self, current_node):
        """
        Update AGV's travel information when receiving current_node update from MQTT.

        Args:
            current_node (int): The updated current node position of the AGV

        Returns:
            None
        """
        # Update previous_node with the current node before changing it
        if self.agv.current_node is not None:
            self.agv.previous_node = self.agv.current_node

        # Update current_node with new position received via MQTT
        self.agv.current_node = current_node
        # Update next_node based as the second element in remaining_path

        # Save the AGV state to the database
        self.agv.save(update_fields=['current_node',
                      'previous_node', ])

    def update_remaining_path(self, current_node):
        """
        Update AGV's remaining path when it reaches a new node.
        If the current node matches the first node in remaining_path, 
        remove it from the path.

        Args:
            current_node (int): The current node position of the AGV

        Returns:
            None
        """        # Check if the AGV has a remaining path
        if self.agv.remaining_path and len(self.agv.remaining_path) > 0:
            # If current node matches the first node in the path, remove it
            if current_node == self.agv.remaining_path[0]:
                # Remove the first element from the list
                self.agv.remaining_path = self.agv.remaining_path[1:]

                # Save only the remaining_path field to the database
                self.agv.save(update_fields=['remaining_path'])

    def update_next_node(self):
        """
        Update the next node for the AGV based on its remaining path.
        The next node is set to the first element of the remaining path.

        Returns:
            None
        """
        if self.agv.remaining_path and len(self.agv.remaining_path) > 0:
            self.agv.next_node = self.agv.remaining_path[0]
            self.agv.save(update_fields=['next_node'])

    def update_common_nodes(self, current_node=None):
        """
        Update common_nodes for this AGV and other AGVs when a node is reached.
        When an AGV reaches a node, that node should be removed from its common_nodes.
        If only one other AGV has this node in its common_nodes, then also remove
        it from that AGV's common_nodes.

        Args:
            current_node (int): The node that was just reached by the AGV.

        Returns:
            None
        """
        node_to_remove = current_node if current_node is not None else self.agv.current_node

        # Skip if no node to remove
        if node_to_remove is None:
            return

        # Remove the node from this AGV's common_nodes if it exists
        if node_to_remove in self.agv.common_nodes:
            self.agv.common_nodes.remove(node_to_remove)
            self.agv.save(update_fields=['common_nodes'])

        # Find all other AGVs that have this node in their common_nodes
        other_agvs_with_common_node = Agv.objects.filter(
            common_nodes__contains=[node_to_remove]
        ).exclude(agv_id=self.agv.agv_id)

        # If only one or zero other AGV has this node in its common_nodes
        if other_agvs_with_common_node.count() <= 1:
            # Remove the node from the other AGV's common_nodes if there is one
            for other_agv in other_agvs_with_common_node:
                if node_to_remove in other_agv.common_nodes:
                    other_agv.common_nodes.remove(node_to_remove)
                    other_agv.save(update_fields=['common_nodes'])

    def update_adjacent_common_nodes(self, current_node=None):
        node_to_remove = current_node if current_node is not None else self.agv.current_node

        # Skip if no node to remove
        if node_to_remove is None:
            return

        # Remove the node from this AGV's common_nodes if it exists
        if node_to_remove in self.agv.adjacent_common_nodes:
            self.agv.adjacent_common_nodes.remove(node_to_remove)
            self.agv.save(update_fields=['adjacent_common_nodes'])
            # number_of_nodes_left_in_adjacent_common_nodes = len(
            #     self.agv.adjacent_common_nodes)
            # if number_of_nodes_left_in_adjacent_common_nodes < 2:
            #     self.agv.adjacent_common_nodes = []
            #     self.agv.save(update_fields=['adjacent_common_nodes'])

        # Find all other AGVs that have this node in their common_nodes
        other_agvs_with_adjacent_common_nodes = Agv.objects.filter(
            adjacent_common_nodes__contains=[node_to_remove]
        ).exclude(agv_id=self.agv.agv_id)

        # If only one or zero other AGV has this node in its common_nodes
        if other_agvs_with_adjacent_common_nodes.count() <= 1:
            # Remove the node from the other AGV's common_nodes if there is one
            for other_agv in other_agvs_with_adjacent_common_nodes:
                if node_to_remove in other_agv.adjacent_common_nodes:
                    other_agv.adjacent_common_nodes.remove(node_to_remove)
                    other_agv.save(update_fields=['adjacent_common_nodes'])

        # Find all AGVs whose adjacent_common_nodes have less than 2 elements, then empty their adjacent_common_nodes because one or zero node cannot be considered as adjacent common nodes
        agvs = Agv.objects.all()
        for agv in agvs:
            if len(agv.adjacent_common_nodes) < 2:
                agv.adjacent_common_nodes = []
                agv.save(update_fields=['adjacent_common_nodes'])

    def update_backup_nodes(self):
        pass

    def _get_reserved_nodes_of_other_agvs(self, filter_spare_flag=None):
        """
        Get a list of reserved nodes from other AGVs, optionally filtered by spare_flag.

        Args:
            filter_spare_flag (bool, optional): If provided, only include reserved nodes
                                             from AGVs with this spare_flag value.

        Returns:
            list: List of unique reserved nodes from other AGVs
        """
        other_agvs = Agv.objects.exclude(agv_id=self.agv.agv_id)

        if filter_spare_flag is not None:
            # Filter by spare_flag if specified
            return list(set(
                agv.reserved_node for agv in other_agvs
                if agv.reserved_node is not None and agv.spare_flag == filter_spare_flag
            ))
        else:
            # Get all reserved nodes without filtering by spare_flag
            return list(set(
                agv.reserved_node for agv in other_agvs
                if agv.reserved_node is not None
            ))

    def _set_agv_moving_without_spare_flag_and_empty_backup_nodes(self):
        """
        Set the AGV to moving state and update related attributes.
        """
        self.agv.motion_state = Agv.MOVING
        self.agv.spare_flag = False
        self.agv.backup_nodes = {}
        self.agv.reserved_node = self.agv.next_node
        self.agv.save(update_fields=['motion_state', 'spare_flag',
                                     'backup_nodes', 'reserved_node'])

    def _set_agv_moving_with_spare_flag(self):
        """
        Set the AGV to moving state with spare_flag set to True.
        This is used when the AGV has backup nodes and is allowed to move.
        """
        self.agv.motion_state = Agv.MOVING
        self.agv.spare_flag = True
        self.agv.reserved_node = self.agv.next_node
        self.agv.save(update_fields=['motion_state',
                      'spare_flag', 'reserved_node'])

    def is_movement_condition_1_satisfied(self) -> bool:
        """
        Evaluate the first movement condition:
        AGV can move if its next node is not reserved by any other AGV
        and is not in its adjacent common nodes.
        """
        reserved_nodes = self._get_reserved_nodes_of_other_agvs()

        if (self.agv.next_node not in reserved_nodes and self.agv.next_node not in self.agv.adjacent_common_nodes):
            # self._set_agv_moving() # This is called in mqtt.py
            return True
        else:
            return False

    def is_movement_condition_2_satisfied(self) -> bool:
        """
        Evaluate the second movement condition:
        AGV can move if its next node is not reserved by any other AGV
        and none of its adjacent common nodes are reserved by other AGVs with spare_flag=False.
        """
        reserved_nodes = self._get_reserved_nodes_of_other_agvs()
        reserved_nodes_non_spare = self._get_reserved_nodes_of_other_agvs(
            filter_spare_flag=False)

        # Check if no adjacent common node is reserved by AGVs with spare_flag=False
        is_adjacent_node_reserved = any(
            node in reserved_nodes_non_spare for node in self.agv.adjacent_common_nodes
        )

        if (self.agv.next_node not in reserved_nodes and self.agv.next_node in self.agv.adjacent_common_nodes and not is_adjacent_node_reserved):
            # self._set_agv_moving() # This is called in mqtt.py
            return True
        else:
            return False

    def is_movement_condition_3_satisfied(self) -> bool:
        reserved_nodes = self._get_reserved_nodes_of_other_agvs()

        reserved_nodes_non_spare = self._get_reserved_nodes_of_other_agvs(
            filter_spare_flag=False)

        # Check if no adjacent common node is reserved by AGVs with spare_flag=False
        is_adjacent_node_reserved = any(
            node in reserved_nodes_non_spare for node in self.agv.adjacent_common_nodes
        )

        if (self.agv.next_node not in reserved_nodes and self.agv.next_node in self.agv.adjacent_common_nodes and is_adjacent_node_reserved and self.agv.backup_nodes):
            return True
        else:
            return False

    def remove_backup_node_associated_with_current_node(self):
        """
        Remove the backup node associated with the current node.
        This is used when the AGV reaches a node and needs to update its backup nodes.

        For example, if an AGV has backup_nodes={1:2, 3:5, 7:9} and its current_node is 1,
        then remove the 1:2 entry, resulting in backup_nodes = {3:5, 7:9}.
        """
        if self.agv.current_node is not None and str(self.agv.current_node) in self.agv.backup_nodes:
            # Convert current_node to string since JSON dictionary keys are strings
            # Create a copy of the dictionary, modify it, and reassign it to trigger Django's change detection
            backup_nodes_copy = dict(self.agv.backup_nodes)
            backup_nodes_copy.pop(str(self.agv.current_node))
            self.agv.backup_nodes = backup_nodes_copy
            self.agv.save(update_fields=['backup_nodes'])

    def _set_agv_waiting(self):
        """
        Set the AGV to waiting state
        """
        self.agv.motion_state = Agv.WAITING
        self.agv.save(update_fields=['motion_state'])
        
    def is_none_of_three_conditions_satisfied(self) -> bool:
        """
        Check if none of the three movement conditions are satisfied.
        This is used to determine if the AGV should wait.
        """
        reserved_nodes = self._get_reserved_nodes_of_other_agvs()
        if self.agv.next_node in reserved_nodes:
            return True
        else:
            return False
