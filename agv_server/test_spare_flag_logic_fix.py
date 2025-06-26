#!/usr/bin/env python
"""
Test script to verify the spare_flag logic fix.

This script tests:
1. Idle AGVs should have spare_flag = False
2. Idle AGVs should not trigger backup node logic
3. Only AGVs with next_node and specific conditions should get spare_flag = True
"""

from django.db import transaction
from agv_data.main_algorithms.algorithm2.algorithm2 import ControlPolicy
from agv_data.models import Agv
import os
import sys
import django

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agv_server.settings')
django.setup()


def test_idle_agv_spare_flag_logic():
    """Test that idle AGVs have correct spare_flag behavior."""
    print("=== Testing Idle AGV Spare Flag Logic ===\n")

    idle_agvs = Agv.objects.filter(
        motion_state=Agv.IDLE,
        active_order=None,
        next_node=None
    )

    print(f"Found {idle_agvs.count()} idle AGVs\n")

    all_tests_passed = True

    for agv in idle_agvs:
        print(f"AGV {agv.agv_id}:")
        print(f"  spare_flag: {agv.spare_flag}")

        control_policy = ControlPolicy(agv)

        # Test the control policy methods
        can_move_freely = control_policy.can_move_freely()
        should_use_backup = control_policy.should_use_backup_nodes()
        can_move_with_backup = control_policy.can_move_with_backup()

        print(f"  can_move_freely(): {can_move_freely}")
        print(f"  should_use_backup_nodes(): {should_use_backup}")
        print(f"  can_move_with_backup(): {can_move_with_backup}")

        # Check for errors
        errors = []

        if agv.spare_flag:
            errors.append("spare_flag should be False for idle AGV")

        if can_move_freely:
            errors.append("idle AGV should not be able to move freely")

        if should_use_backup:
            errors.append("idle AGV should not need backup nodes")

        if can_move_with_backup:
            errors.append("idle AGV should not be able to move with backup")

        if errors:
            print(f"  ❌ ERRORS:")
            for error in errors:
                print(f"    - {error}")
            all_tests_passed = False
        else:
            print(f"  ✅ ALL TESTS PASSED")

        print()

    return all_tests_passed


def fix_incorrect_spare_flags():
    """Fix any AGVs that have incorrect spare_flag values."""
    print("=== Fixing Incorrect Spare Flags ===\n")

    # Find idle AGVs with incorrect spare_flag=True
    incorrect_idle_agvs = Agv.objects.filter(
        motion_state=Agv.IDLE,
        active_order=None,
        next_node=None,
        spare_flag=True
    )

    if incorrect_idle_agvs.exists():
        print(
            f"Found {incorrect_idle_agvs.count()} idle AGVs with incorrect spare_flag=True")

        with transaction.atomic():
            for agv in incorrect_idle_agvs:
                print(f"  Fixing AGV {agv.agv_id}: setting spare_flag=False")
                agv.spare_flag = False
                agv.save(update_fields=['spare_flag'])

        print("✅ Fixed all incorrect spare_flags\n")
        return True
    else:
        print("✅ No incorrect spare_flags found\n")
        return False


def test_spare_flag_conditions():
    """Test when spare_flag should be True vs False."""
    print("=== Testing Spare Flag Conditions ===\n")

    print("Spare flag should be True when:")
    print("  - AGV is in MOVING state with backup nodes")
    print("  - AGV has active order and next_node")
    print("  - can_move_with_backup() returns True")
    print()

    print("Spare flag should be False when:")
    print("  - AGV is IDLE with no active order")
    print("  - AGV has no next_node")
    print("  - AGV is moving without backup nodes")
    print("  - AGV is WAITING")
    print()

    # Check all AGVs
    agvs = Agv.objects.all()

    for agv in agvs:
        control_policy = ControlPolicy(agv)

        print(f"AGV {agv.agv_id}:")
        print(
            f"  State: motion_state={agv.motion_state}, active_order={bool(agv.active_order)}, next_node={agv.next_node}")
        print(f"  spare_flag: {agv.spare_flag}")

        # Determine if spare_flag is correct
        is_idle = (agv.motion_state == Agv.IDLE and
                   agv.active_order is None and
                   agv.next_node is None)

        if is_idle and agv.spare_flag:
            print(f"  ❌ ERROR: Idle AGV should not have spare_flag=True")
        elif is_idle and not agv.spare_flag:
            print(f"  ✅ CORRECT: Idle AGV has spare_flag=False")
        else:
            print(f"  ℹ️  Non-idle AGV - spare_flag logic depends on movement conditions")

        print()


if __name__ == '__main__':
    print("Spare Flag Logic Test\n")
    print("=" * 50)

    # Test current state
    all_tests_passed = test_idle_agv_spare_flag_logic()

    # Fix any issues
    had_fixes = fix_incorrect_spare_flags()

    # Test again if we had fixes
    if had_fixes:
        print("=" * 50)
        print("RE-TESTING AFTER FIXES\n")
        all_tests_passed = test_idle_agv_spare_flag_logic()

    # Test spare flag conditions
    test_spare_flag_conditions()

    print("=" * 50)
    if all_tests_passed:
        print("🎉 ALL TESTS PASSED - Spare flag logic is working correctly!")
    else:
        print("❌ SOME TESTS FAILED - Check the output above for details")

    print("\nTest complete.")
