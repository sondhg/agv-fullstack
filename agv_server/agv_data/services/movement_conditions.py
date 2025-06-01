"""
Movement condition evaluation for AGV control policy.

This module implements the evaluation of movement conditions as described in Algorithm 2
of the DSPA algorithm from algorithms-pseudocode.tex.
"""
from dataclasses import dataclass
from typing import List, Tuple, Optional
from ..models import Agv
from .utils import is_node_reserved_by_others


@dataclass
class MovementConditionResult:
    can_move: bool
    should_apply_spare_points: bool
    clear_spare_points: bool = False


class MovementConditionEvaluator:
    """Evaluates AGV movement conditions based on DSPA Algorithm 2."""

    def __init__(self, agv: Agv):
        self.agv = agv
        self.next_node = agv.next_node
        self.adjacent_common_nodes = agv.adjacent_common_nodes
        self.reserved_by_others = is_node_reserved_by_others(
            agv.next_node, agv.agv_id) if agv.next_node else True

    def evaluate(self) -> MovementConditionResult:
        """Evaluate all movement conditions and return the result."""
        if not self.next_node:
            return MovementConditionResult(False, False)

        if self.reserved_by_others:
            return MovementConditionResult(False, False)

        if self._check_condition_1():
            return MovementConditionResult(True, False, True)

        if self._check_condition_2():
            return MovementConditionResult(True, False, True)

        return self._evaluate_condition_3()

    def _check_condition_1(self) -> bool:
        """Check if next node is not in SCP and not reserved by others."""
        return self.next_node not in self.adjacent_common_nodes

    def _check_condition_2(self) -> bool:
        """Check if next node is in SCP but no SCP points are reserved by AGVs without spare points."""
        return (self.next_node in self.adjacent_common_nodes and
                not self._has_adjacent_common_nodes_with_no_spare_reservations())

    def _evaluate_condition_3(self) -> MovementConditionResult:
        """Evaluate condition 3 and determine if spare points should be applied."""
        if self.agv.spare_flag:
            return MovementConditionResult(True, True)
        return MovementConditionResult(False, True)

    def _has_adjacent_common_nodes_with_no_spare_reservations(self) -> bool:
        """Check if any SCP point is reserved by an AGV without spare points."""
        return any(
            Agv.objects.filter(
                reserved_node=point,
                spare_flag=False
            ).exclude(
                agv_id=self.agv.agv_id
            ).exists()
            for point in self.adjacent_common_nodes
        )


def evaluate_movement_conditions(agv: Agv) -> Tuple[bool, bool]:
    """
    Evaluate if an AGV can move based on Algorithm 2's conditions.

    Conditions evaluated:
    1. v_n^i ∉ SCP^i and v_n^i ∉ {v_r^j, j ≠ i}
    2. v_n^i ∈ SCP^i but ∀v_x ∈ SCP^i, v_x ∉ {v_r^j, j ≠ i, F^j = 0} and v_n^i ∉ {v_r^j, j ≠ i}
    3. v_n^i ∈ SCP^i and ∃v_x ∈ SCP^i, v_x ∈ {v_r^j, j ≠ i, F^j = 0} but SP^i ≠ ∅ 

    Args:
        agv (Agv): The AGV to evaluate

    Returns:
        Tuple[bool, bool]: (can_move, should_apply_spare_points)
            - can_move: True if any condition is satisfied and AGV can move
            - should_apply_spare_points: True if AGV needs to apply for spare points
    """
    evaluator = MovementConditionEvaluator(agv)
    result = evaluator.evaluate()

    if result.clear_spare_points:
        agv.spare_flag = False
        agv.spare_points = {}

    return result.can_move, result.should_apply_spare_points
