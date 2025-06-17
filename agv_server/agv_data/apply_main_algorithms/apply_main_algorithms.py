import logging
from ..models import Agv
from ..main_algorithms.algorithm2.algorithm2 import ControlPolicy
from ..main_algorithms.algorithm3.algorithm3 import DeadlockResolver
from ..main_algorithms.algorithm4.algorithm4 import BackupNodesAllocator

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


def _apply_control_policy(agv: Agv) -> None:
    """Apply DSPA control policy to determine AGV's next action."""
    control_policy = ControlPolicy(agv)

    # Check if AGV can move based on basic conditions
    if control_policy.can_move_freely():
        control_policy.set_moving_state()
        # Clear deadlock resolution state if it was set
        if agv.waiting_for_deadlock_resolution:
            deadlock_resolver = DeadlockResolver(agv)
            deadlock_resolver.clear_deadlock_resolution_state()
        return

    # Handle backup node scenarios
    if control_policy.should_use_backup_nodes():
        _handle_backup_node_scenario(agv)
        return

    # Handle waiting and deadlock scenarios
    _handle_waiting_scenario(agv)


def _trigger_deadlock_partner_control_policy(moved_agv_id: int) -> None:
    """
    When an AGV moves, check if any other AGVs were waiting for this AGV
    due to deadlock resolution, and trigger their control policy.
    """
    try:
        # Find AGVs that were waiting for this AGV due to deadlock resolution
        waiting_agvs = Agv.objects.filter(
            waiting_for_deadlock_resolution=True,
            deadlock_partner_agv_id=moved_agv_id,
            motion_state=Agv.WAITING
        )

        for waiting_agv in waiting_agvs:
            logger.info(f"Triggering control policy for AGV {waiting_agv.agv_id} "
                        f"after partner AGV {moved_agv_id} moved")
            _apply_control_policy(waiting_agv)

    except Exception as e:
        logger.error(
            f"Error triggering deadlock partner control policy: {str(e)}")


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


def _handle_waiting_scenario(agv: Agv) -> None:
    """Handle waiting scenarios and potential deadlocks."""
    control_policy = ControlPolicy(agv)
    control_policy.set_waiting_state()

    deadlock_resolver = DeadlockResolver(agv)
    if deadlock_resolver.has_heading_on_deadlock():
        deadlock_resolver.resolve_heading_on_deadlock()
    elif deadlock_resolver.has_loop_deadlock():
        deadlock_resolver.resolve_loop_deadlock()
    else:
        deadlock_resolver.reserve_current_position()
