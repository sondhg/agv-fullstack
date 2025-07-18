from typing import Optional, List
from ...models import Agv
import logging

logger = logging.getLogger(__name__)


class PositionManager:
    """Handles AGV position and path updates."""

    def __init__(self, agv: Agv):
        self.agv = agv

    def update_positions(self, current_node: int) -> None:
        """Update current and previous node positions."""
        if self.agv.current_node is not None:
            self.agv.previous_node = self.agv.current_node

        self.agv.current_node = current_node
        self.agv.save(update_fields=["current_node", "previous_node"])

    def update_path(self, current_node: int) -> None:
        """Update remaining path and next node based on current position."""
        if self._should_remove_current_node_from_path(current_node):
            self._remove_current_node_from_path(current_node)

        self._update_next_node()

    def _should_remove_current_node_from_path(self, current_node: int) -> bool:
        """Check if current node should be removed from remaining path."""
        return (
            self.agv.remaining_path
            and len(self.agv.remaining_path) > 0
            and current_node == self.agv.remaining_path[0]
        )

    def _remove_current_node_from_path(self, current_node: int) -> None:
        """Remove current node from remaining path."""
        logger.debug(
            f"AGV {self.agv.agv_id} reached node {current_node}, removing from remaining path"
        )
        self.agv.remaining_path = self.agv.remaining_path[1:]
        self.agv.save(update_fields=["remaining_path"])

    def _update_next_node(self) -> None:
        """Update next node based on remaining path."""
        if self.agv.remaining_path and len(self.agv.remaining_path) > 0:
            self.agv.next_node = self.agv.remaining_path[0]
        else:
            logger.debug(
                f"AGV {self.agv.agv_id} has no remaining path, clearing next_node"
            )
            self.agv.next_node = None

        self.agv.save(update_fields=["next_node"])


class SharedNodesManager:
    """Handles shared nodes management between AGVs."""

    def __init__(self, agv: Agv):
        self.agv = agv

    def update_shared_nodes(self, current_node: int) -> None:
        """Update common nodes and adjacent common nodes when reaching a node."""
        self._remove_from_shared_nodes(current_node, "common_nodes")
        self._remove_from_shared_nodes(current_node, "adjacent_common_nodes")
        self._cleanup_insufficient_adjacent_nodes()

    def _remove_from_shared_nodes(self, node: int, field_name: str) -> None:
        """Remove node from shared node lists of this and other AGVs if appropriate."""
        self._remove_from_current_agv(node, field_name)
        self._remove_from_other_agvs_if_needed(node, field_name)

    def _remove_from_current_agv(self, node: int, field_name: str) -> None:
        """Remove node from this AGV's shared node list."""
        shared_nodes = getattr(self.agv, field_name)
        if node in shared_nodes:
            shared_nodes.remove(node)
            setattr(self.agv, field_name, shared_nodes)
            self.agv.save(update_fields=[field_name])

    def _remove_from_other_agvs_if_needed(self, node: int, field_name: str) -> None:
        """Remove node from other AGVs if only one or no other AGV has this node."""
        filter_kwargs = {f"{field_name}__contains": [node]}
        other_agvs_with_node = Agv.objects.filter(**filter_kwargs).exclude(
            agv_id=self.agv.agv_id
        )

        if other_agvs_with_node.count() <= 1:
            for other_agv in other_agvs_with_node:
                other_shared_nodes = getattr(other_agv, field_name)
                if node in other_shared_nodes:
                    other_shared_nodes.remove(node)
                    setattr(other_agv, field_name, other_shared_nodes)
                    other_agv.save(update_fields=[field_name])

    def _cleanup_insufficient_adjacent_nodes(self) -> None:
        """Clear adjacent_common_nodes for all AGVs if they have less than 2 nodes."""
        for agv in Agv.objects.all():
            if len(agv.adjacent_common_nodes) < 2:
                agv.adjacent_common_nodes = []
                agv.save(update_fields=["adjacent_common_nodes"])


class JourneyPhaseManager:
    """Handles AGV journey phase transitions and validations."""

    def __init__(self, agv: Agv):
        self.agv = agv

    def check_journey_phase_transition(self, current_node: int) -> None:
        """Check if the AGV should transition between journey phases or complete order."""
        if not self.agv.active_order:
            return

        if self.agv.journey_phase == Agv.OUTBOUND:
            self._handle_outbound_phase(current_node)
        elif self.agv.journey_phase == Agv.INBOUND:
            self._handle_inbound_phase(current_node)

    def _handle_outbound_phase(self, current_node: int) -> None:
        """Handle outbound to inbound transition."""
        workstation_node = self.agv.active_order.workstation_node

        if current_node == workstation_node and self._is_outbound_journey_complete():
            self._transition_to_inbound_journey()

    def _handle_inbound_phase(self, current_node: int) -> None:
        """Handle inbound phase validation and order completion."""
        self._validate_inbound_remaining_path(current_node)

        parking_node = self.agv.active_order.parking_node
        if current_node == parking_node and self._is_inbound_journey_complete():
            self._complete_order_journey()

    def _is_inbound_journey_complete(self) -> bool:
        """
        Check if the inbound journey is complete.

        Returns:
            True if remaining path is empty or AGV is at parking node
        """
        if not self.agv.remaining_path or len(self.agv.remaining_path) == 0:
            return True

        if (
            self.agv.active_order
            and self.agv.current_node == self.agv.active_order.parking_node
        ):
            return True

        return False

    def _is_outbound_journey_complete(self) -> bool:
        """
        Check if the outbound journey is complete.

        Returns:
            True if remaining path matches inbound path or is empty at workstation
        """
        if not self.agv.remaining_path or len(self.agv.remaining_path) == 0:
            logger.debug(
                f"AGV {self.agv.agv_id} outbound journey complete: no remaining path"
            )
            return True

        if not self.agv.inbound_path:
            logger.warning(
                f"AGV {self.agv.agv_id} has no inbound path set, treating outbound as complete"
            )
            return True

        if self.agv.remaining_path == self.agv.inbound_path:
            logger.debug(
                f"AGV {self.agv.agv_id} outbound journey complete: remaining path matches inbound path"
            )
            return True

        if (
            len(self.agv.remaining_path) <= len(self.agv.inbound_path)
            and self.agv.remaining_path
            == self.agv.inbound_path[: len(self.agv.remaining_path)]
        ):
            logger.debug(
                f"AGV {self.agv.agv_id} outbound journey complete: remaining path is subset of inbound path"
            )
            return True

        logger.debug(
            f"AGV {self.agv.agv_id} outbound journey not complete. Remaining: {self.agv.remaining_path}, Inbound: {self.agv.inbound_path}"
        )
        return False

    def _validate_inbound_remaining_path(self, current_node: int) -> None:
        """Validate and fix the remaining path for AGVs already in inbound phase."""
        if not self.agv.inbound_path:
            return

        if self._is_at_parking_node(current_node):
            self._clear_remaining_path_at_parking()
            return

        if self._should_fix_remaining_path():
            self._fix_inbound_remaining_path(current_node)

    def _is_at_parking_node(self, current_node: int) -> bool:
        """Check if AGV is at the parking node."""
        return (
            self.agv.active_order and current_node == self.agv.active_order.parking_node
        )

    def _clear_remaining_path_at_parking(self) -> None:
        """Clear remaining path when AGV reaches parking node."""
        if self.agv.remaining_path:
            logger.info(
                f"AGV {self.agv.agv_id} has reached parking node, clearing remaining path for order completion"
            )
            self.agv.remaining_path = []
            self.agv.next_node = None
            self.agv.reserved_node = None
            self.agv.save(
                update_fields=["remaining_path", "next_node", "reserved_node"]
            )

    def _should_fix_remaining_path(self) -> bool:
        """Check if remaining path needs correction."""
        if not self.agv.remaining_path:
            logger.warning(
                f"AGV {self.agv.agv_id} in inbound phase but has no remaining path"
            )
            return True

        if (
            len(self.agv.remaining_path) > len(self.agv.inbound_path)
            or not self._is_valid_inbound_remaining_path()
        ):
            logger.warning(
                f"AGV {self.agv.agv_id} in inbound phase but remaining path doesn't match inbound structure"
            )
            return True

        return False

    def _fix_inbound_remaining_path(self, current_node: int) -> None:
        """Fix the remaining path for inbound journey."""
        logger.info(f"Fixing remaining path for AGV {self.agv.agv_id} in inbound phase")

        self.agv.remaining_path = self.agv.inbound_path.copy()

        if self._should_remove_current_node_from_remaining_path(current_node):
            logger.info(
                f"AGV {self.agv.agv_id} is at node {current_node}, removing from remaining path"
            )
            self.agv.remaining_path = self.agv.remaining_path[1:]

        self._update_next_and_reserved_nodes()

        logger.info(
            f"Fixed AGV {self.agv.agv_id} remaining path: {self.agv.remaining_path}"
        )

    def _should_remove_current_node_from_remaining_path(
        self, current_node: int
    ) -> bool:
        """Check if current node should be removed from remaining path."""
        return (
            self.agv.remaining_path
            and len(self.agv.remaining_path) > 0
            and current_node == self.agv.remaining_path[0]
        )

    def _update_next_and_reserved_nodes(self) -> None:
        """Update next_node and reserved_node based on remaining path."""
        if self.agv.remaining_path and len(self.agv.remaining_path) > 0:
            self.agv.next_node = self.agv.remaining_path[0]
        else:
            self.agv.next_node = None

        self.agv.reserved_node = None
        self.agv.save(update_fields=["remaining_path", "next_node", "reserved_node"])

    def _is_valid_inbound_remaining_path(self) -> bool:
        """Check if the current remaining path is a valid subset of the inbound path."""
        if not self.agv.inbound_path or not self.agv.remaining_path:
            return False

        for i in range(len(self.agv.inbound_path)):
            if (
                len(self.agv.remaining_path) <= len(self.agv.inbound_path) - i
                and self.agv.remaining_path
                == self.agv.inbound_path[i : i + len(self.agv.remaining_path)]
            ):
                return True
        return False

    def _transition_to_inbound_journey(self) -> None:
        """Transition AGV from outbound to inbound journey phase."""
        logger.info(
            f"AGV {self.agv.agv_id} transitioning from outbound to inbound journey"
        )

        if not self.agv.inbound_path:
            logger.error(
                f"AGV {self.agv.agv_id} cannot transition to inbound: no inbound path set"
            )
            return

        self._set_inbound_journey_state()
        self._recalculate_common_nodes()

    def _set_inbound_journey_state(self) -> None:
        """Set the AGV state for inbound journey."""
        self.agv.journey_phase = Agv.INBOUND
        self.agv.remaining_path = self.agv.inbound_path.copy()

        if self._should_remove_current_node_from_remaining_path(self.agv.current_node):
            logger.info(
                f"AGV {self.agv.agv_id} is already at workstation node {self.agv.current_node}, removing from remaining path"
            )
            self.agv.remaining_path = self.agv.remaining_path[1:]

        self._update_next_and_reserved_nodes()

        self.agv.save(
            update_fields=[
                "journey_phase",
                "remaining_path",
                "next_node",
                "reserved_node",
            ]
        )
        logger.info(
            f"AGV {self.agv.agv_id} now on inbound journey with remaining path: {self.agv.remaining_path}"
        )

    def _complete_order_journey(self) -> None:
        """Complete the AGV's order journey when it reaches the parking node."""
        if not self.agv.active_order:
            logger.warning(
                f"AGV {self.agv.agv_id} cannot complete journey: no active order"
            )
            return

        order_id = self.agv.active_order.order_id
        logger.info(f"AGV {self.agv.agv_id} completing order {order_id}")

        self._reset_agv_to_idle()
        self._recalculate_common_nodes()

        logger.info(
            f"AGV {self.agv.agv_id} order {order_id} completion finished - now idle"
        )

    def _reset_agv_to_idle(self) -> None:
        """Reset AGV to idle state after completing order."""
        # Clear order-related data
        self.agv.active_order = None
        self.agv.initial_path = []
        self.agv.remaining_path = []
        self.agv.outbound_path = []
        self.agv.inbound_path = []
        self.agv.common_nodes = []
        self.agv.adjacent_common_nodes = []

        # Reset journey phase and motion state
        self.agv.journey_phase = Agv.OUTBOUND
        self.agv.motion_state = Agv.IDLE
        self.agv.next_node = None
        self.agv.reserved_node = None
        self.agv.direction_change = Agv.TURN_AROUND

        # Clear deadlock-related flags
        self.agv.spare_flag = False
        self.agv.backup_nodes = {}
        self.agv.waiting_for_deadlock_resolution = False
        self.agv.deadlock_partner_agv_id = None

        self.agv.save(
            update_fields=[
                "active_order",
                "initial_path",
                "remaining_path",
                "outbound_path",
                "inbound_path",
                "common_nodes",
                "adjacent_common_nodes",
                "journey_phase",
                "motion_state",
                "next_node",
                "reserved_node",
                "direction_change",
                "spare_flag",
                "backup_nodes",
                "waiting_for_deadlock_resolution",
                "deadlock_partner_agv_id",
            ]
        )

    def _recalculate_common_nodes(self) -> None:
        """Recalculate common nodes for all AGVs."""
        try:
            from ..algorithm1.common_nodes import recalculate_all_common_nodes

            recalculate_all_common_nodes(log_summary=True)
            logger.info(
                f"Recalculated common nodes after AGV {self.agv.agv_id} journey phase change"
            )
        except Exception as e:
            logger.error(f"Failed to recalculate common nodes: {str(e)}")


class MovementDecisionManager:
    """Handles movement decision logic for AGVs."""

    def __init__(self, agv: Agv):
        self.agv = agv

    def can_move_freely(self) -> bool:
        """Check if AGV can move without any restrictions."""
        if not self.agv.next_node:
            return False

        reserved_nodes = self._get_reserved_nodes_by_others()

        # Condition 1: Next node not reserved and not in adjacent common nodes
        if (
            self.agv.next_node not in reserved_nodes
            and self.agv.next_node not in self.agv.adjacent_common_nodes
        ):
            return True

        # Condition 2: Next node in adjacent common nodes but safe to move
        if (
            self.agv.next_node not in reserved_nodes
            and self.agv.next_node in self.agv.adjacent_common_nodes
        ):
            reserved_by_non_spare = self._get_reserved_nodes_by_others(spare_flag=False)
            adjacent_nodes_blocked = any(
                node in reserved_by_non_spare for node in self.agv.adjacent_common_nodes
            )
            return not adjacent_nodes_blocked

        return False

    def should_use_backup_nodes(self) -> bool:
        """Check if backup node handling is needed."""
        if not self.agv.next_node:
            return False

        reserved_nodes = self._get_reserved_nodes_by_others()
        return self.agv.next_node not in reserved_nodes

    def can_move_with_backup(self) -> bool:
        """Check if AGV can move after backup node allocation."""
        if not self.agv.next_node or not self.agv.backup_nodes:
            return False

        reserved_nodes = self._get_reserved_nodes_by_others()
        reserved_by_non_spare = self._get_reserved_nodes_by_others(spare_flag=False)

        adjacent_nodes_blocked = any(
            node in reserved_by_non_spare for node in self.agv.adjacent_common_nodes
        )

        return (
            self.agv.next_node not in reserved_nodes
            and self.agv.next_node in self.agv.adjacent_common_nodes
            and adjacent_nodes_blocked
        )

    def _get_reserved_nodes_by_others(
        self, spare_flag: Optional[bool] = None
    ) -> List[int]:
        """Get reserved nodes from other AGVs, optionally filtered by spare_flag."""
        other_agvs = Agv.objects.exclude(agv_id=self.agv.agv_id)

        if spare_flag is not None:
            other_agvs = other_agvs.filter(spare_flag=spare_flag)

        return [
            agv.reserved_node for agv in other_agvs if agv.reserved_node is not None
        ]


class StateManager:
    """Handles AGV state transitions and management."""

    def __init__(self, agv: Agv):
        self.agv = agv

    def set_moving_state(self) -> None:
        """Set AGV to moving state without backup nodes."""
        self.agv.motion_state = Agv.MOVING
        self.agv.spare_flag = False
        self.agv.backup_nodes = {}
        self.agv.reserved_node = self.agv.next_node
        self.agv.save(
            update_fields=[
                "motion_state",
                "spare_flag",
                "backup_nodes",
                "reserved_node",
            ]
        )

    def set_moving_with_backup_state(self) -> None:
        """Set AGV to moving state with backup nodes."""
        self.agv.motion_state = Agv.MOVING
        self.agv.spare_flag = True
        self.agv.reserved_node = self.agv.next_node
        self.agv.save(update_fields=["motion_state", "spare_flag", "reserved_node"])

    def set_waiting_state(self) -> None:
        """Set AGV to waiting state."""
        self.agv.motion_state = Agv.WAITING
        self.agv.save(update_fields=["motion_state"])


class BackupNodeManager:
    """Handles backup node management for AGVs."""

    def __init__(self, agv: Agv):
        self.agv = agv

    def cleanup_current_backup_node(self) -> None:
        """Remove backup node associated with current position."""
        if (
            self.agv.current_node is not None
            and str(self.agv.current_node) in self.agv.backup_nodes
        ):
            backup_nodes_copy = dict(self.agv.backup_nodes)
            backup_nodes_copy.pop(str(self.agv.current_node))
            self.agv.backup_nodes = backup_nodes_copy
            self.agv.save(update_fields=["backup_nodes"])


class ControlPolicy:
    """
    Algorithm 2: DSPA Control Policy

    This class implements the control policy that determines how AGVs should move
    based on their current state and the state of other AGVs in the system.

    The class coordinates between multiple managers to handle different aspects
    of AGV control: position updates, shared nodes, journey phases, and movement decisions.
    """

    def __init__(self, agv: Agv):
        self.agv = agv
        self.position_manager = PositionManager(agv)
        self.shared_nodes_manager = SharedNodesManager(agv)
        self.journey_phase_manager = JourneyPhaseManager(agv)
        self.movement_manager = MovementDecisionManager(agv)
        self.state_manager = StateManager(agv)
        self.backup_manager = BackupNodeManager(agv)

    def update_position_info(self, current_node: int) -> None:
        """
        Update all position-related information when AGV reaches a new node.

        Args:
            current_node: The new current position of the AGV
        """
        self.position_manager.update_positions(current_node)
        self.position_manager.update_path(current_node)
        self.shared_nodes_manager.update_shared_nodes(current_node)
        self.journey_phase_manager.check_journey_phase_transition(current_node)

    # === Movement Decision Logic (Delegated to MovementDecisionManager) ===

    def can_move_freely(self) -> bool:
        """Check if AGV can move without any restrictions."""
        return self.movement_manager.can_move_freely()

    def should_use_backup_nodes(self) -> bool:
        """Check if backup node handling is needed."""
        return self.movement_manager.should_use_backup_nodes()

    def can_move_with_backup(self) -> bool:
        """Check if AGV can move after backup node allocation."""
        return self.movement_manager.can_move_with_backup()

    # === State Management (Delegated to StateManager) ===

    def set_moving_state(self) -> None:
        """Set AGV to moving state without backup nodes."""
        self.state_manager.set_moving_state()

    def set_moving_with_backup_state(self) -> None:
        """Set AGV to moving state with backup nodes."""
        self.state_manager.set_moving_with_backup_state()

    def set_waiting_state(self) -> None:
        """Set AGV to waiting state."""
        self.state_manager.set_waiting_state()

    # === Backup Node Management (Delegated to BackupNodeManager) ===

    def cleanup_current_backup_node(self) -> None:
        """Remove backup node associated with current position."""
        self.backup_manager.cleanup_current_backup_node()

    # === Helper Methods ===

    def _get_reserved_nodes_by_others(
        self, spare_flag: Optional[bool] = None
    ) -> List[int]:
        """Get reserved nodes from other AGVs, optionally filtered by spare_flag."""
        return self.movement_manager._get_reserved_nodes_by_others(spare_flag)
