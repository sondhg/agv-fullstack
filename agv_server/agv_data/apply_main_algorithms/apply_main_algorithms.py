import logging
from typing import List
from ..models import Agv
from ..main_algorithms.algorithm2.algorithm2 import ControlPolicy
from ..main_algorithms.algorithm3.algorithm3 import DeadlockResolver
from ..main_algorithms.algorithm4.algorithm4 import BackupNodesAllocator

from ..direction_change.direction_to_turn import determine_direction_change

logger = logging.getLogger(__name__)


def _get_agv_by_id(agv_id):
    """Get AGV instance by ID."""
    try:
        return Agv.objects.get(agv_id=agv_id)
    except Agv.DoesNotExist:
        logger.error(f"AGV with ID {agv_id} not found in database")
        return None


def _update_agv_position(agv: Agv, current_node: int):
    """Update AGV's position and path information."""
    control_policy = ControlPolicy(agv)
    control_policy.update_position_info(current_node)


def _apply_control_policy(agv: Agv) -> List[Agv]:
    """
    Apply DSPA control policy to determine AGV's next action.

    Returns:
        List[Agv]: List of other AGVs that were affected by deadlock resolution
    """
    control_policy = ControlPolicy(agv)

    # If AGV is idle (no active order and no next node), no control policy needed
    if not agv.active_order and not agv.next_node:
        logger.debug(f"AGV {agv.agv_id} is idle, no control policy needed")
        return []

    # Check if AGV can move based on basic conditions
    if control_policy.can_move_freely():
        control_policy.set_moving_state()
        # Clear deadlock resolution state if it was set
        if agv.waiting_for_deadlock_resolution:
            deadlock_resolver = DeadlockResolver(agv)
            deadlock_resolver.clear_deadlock_resolution_state()
            logger.info(
                f"AGV {agv.agv_id} cleared from deadlock resolution and moving normally"
            )

        determine_direction_change(agv)
        return []

    # Handle backup node scenarios
    if control_policy.should_use_backup_nodes():
        _handle_backup_node_scenario(agv)
        determine_direction_change(agv)
        return []

    # Handle waiting and deadlock scenarios
    affected_agvs = _handle_waiting_scenario(agv)
    determine_direction_change(agv)
    return affected_agvs


def _trigger_deadlock_partner_control_policy(moved_agv_id: int) -> List[Agv]:
    """
    When an AGV moves, check if any other AGVs were waiting for this AGV
    due to deadlock resolution, and trigger their control policy.

    Returns:
        List[Agv]: List of AGVs whose control policy was triggered due to deadlock resolution
    """
    partner_agvs = []
    try:
        # Find AGVs that were waiting for this AGV due to deadlock resolution
        waiting_agvs = Agv.objects.filter(
            waiting_for_deadlock_resolution=True,
            deadlock_partner_agv_id=moved_agv_id,
            motion_state=Agv.WAITING,
        )

        for waiting_agv in waiting_agvs:
            logger.info(
                f"Triggering control policy for AGV {waiting_agv.agv_id} "
                f"after partner AGV {moved_agv_id} moved"
            )
            additional_affected_agvs = _apply_control_policy(waiting_agv)
            partner_agvs.append(waiting_agv)
            partner_agvs.extend(additional_affected_agvs)

    except Exception as e:
        logger.error(f"Error triggering deadlock partner control policy: {str(e)}")

    return partner_agvs


def _handle_backup_node_scenario(agv: Agv) -> None:
    """Handle scenarios involving backup nodes."""
    control_policy = ControlPolicy(agv)
    if agv.spare_flag:
        control_policy.cleanup_current_backup_node()
    else:
        backup_allocator = BackupNodesAllocator(agv)
        backup_allocator.allocate_backup_nodes()

    if control_policy.can_move_with_backup():
        control_policy.set_moving_with_backup_state()


def _handle_waiting_scenario(agv: Agv) -> List[Agv]:
    """
    Handle waiting scenarios and potential deadlocks.

    Returns:
        List[Agv]: List of other AGVs that were affected by deadlock resolution
    """
    control_policy = ControlPolicy(agv)
    control_policy.set_waiting_state()

    deadlock_resolver = DeadlockResolver(agv)
    if deadlock_resolver.has_heading_on_deadlock():
        return deadlock_resolver.resolve_heading_on_deadlock()
    elif deadlock_resolver.has_loop_deadlock():
        return deadlock_resolver.resolve_loop_deadlock()
    else:
        deadlock_resolver.reserve_current_position()
        return []
