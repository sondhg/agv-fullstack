"""
Quick test to verify the journey phase transition fix.
This script tests the fix for the workstation node transition issue.
"""

from agv_data.main_algorithms.algorithm2.algorithm2 import ControlPolicy
from agv_data.models import Agv
import os
import sys
import django

# Add the project root to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agv_server.settings')
django.setup()


def test_workstation_transition_fix():
    """Test the fix for workstation transition remaining path issue."""

    print("=== Testing Workstation Transition Fix ===\n")

    # Get AGV 1 which should be at workstation
    agv = Agv.objects.get(agv_id=1)

    print(f"AGV {agv.agv_id} Current State:")
    print(f"Current node: {agv.current_node}")
    print(f"Journey phase: {agv.get_journey_phase_display()}")
    print(f"Remaining path: {agv.remaining_path}")
    print(f"Next node: {agv.next_node}")
    print(f"Reserved node: {agv.reserved_node}")
    print(f"Inbound path: {agv.inbound_path}")
    print()

    # Create control policy instance
    control_policy = ControlPolicy(agv)

    # Test the validation fix for inbound remaining path
    if agv.journey_phase == Agv.INBOUND:
        print("AGV is already in inbound phase - testing validation fix...")

        print("Before validation fix:")
        print(f"  Remaining path: {agv.remaining_path}")
        print(f"  Next node: {agv.next_node}")
        print(f"  Reserved node: {agv.reserved_node}")

        # Call the validation method directly
        control_policy._validate_inbound_remaining_path(agv.current_node)

        # Reload to see changes
        agv.refresh_from_db()

        print("After validation fix:")
        print(f"  Remaining path: {agv.remaining_path}")
        print(f"  Next node: {agv.next_node}")
        print(f"  Reserved node: {agv.reserved_node}")

        # Verify the fix
        if agv.remaining_path and len(agv.remaining_path) > 0:
            expected_next = agv.remaining_path[0]
            if agv.next_node == expected_next:
                print(f"✅ SUCCESS: Next node correctly set to {agv.next_node}")
                if agv.current_node != agv.next_node:
                    print(
                        f"✅ SUCCESS: AGV is ready to move from {agv.current_node} to {agv.next_node}")
                else:
                    print(
                        f"❌ FAIL: Next node {agv.next_node} is same as current node {agv.current_node}")
            else:
                print(
                    f"❌ FAIL: Next node is {agv.next_node}, expected {expected_next}")
        else:
            print("ℹ️  No remaining path after validation")

    elif agv.journey_phase == Agv.OUTBOUND and agv.active_order:
        # Test outbound to inbound transition
        workstation_node = agv.active_order.workstation_node
        if agv.current_node == workstation_node:
            print("AGV is at workstation - testing outbound to inbound transition...")

            print("Before transition:")
            print(f"  Journey phase: {agv.get_journey_phase_display()}")
            print(f"  Remaining path: {agv.remaining_path}")
            print(f"  Next node: {agv.next_node}")

            # Call the transition method
            if control_policy._is_outbound_journey_complete():
                control_policy._transition_to_inbound_journey()

                # Reload to see changes
                agv.refresh_from_db()

                print("After transition:")
                print(f"  Journey phase: {agv.get_journey_phase_display()}")
                print(f"  Remaining path: {agv.remaining_path}")
                print(f"  Next node: {agv.next_node}")
                print(f"  Reserved node: {agv.reserved_node}")
            else:
                print("Outbound journey not complete yet")

    print(f"\n✅ Test completed for AGV {agv.agv_id}!")


def test_simulation_of_position_update():
    """Simulate the full position update process that happens via MQTT."""

    print("\n=== Simulating Position Update Process ===\n")

    agv = Agv.objects.get(agv_id=1)
    current_node = agv.current_node

    print(
        f"Simulating position update for AGV {agv.agv_id} at node {current_node}")

    # This simulates what happens in _update_agv_position
    control_policy = ControlPolicy(agv)
    control_policy.update_position_info(current_node)

    # Reload to see final state
    agv.refresh_from_db()

    print("Final state after position update:")
    print(f"  Journey phase: {agv.get_journey_phase_display()}")
    print(f"  Current node: {agv.current_node}")
    print(f"  Next node: {agv.next_node}")
    print(f"  Reserved node: {agv.reserved_node}")
    print(f"  Remaining path: {agv.remaining_path}")


if __name__ == "__main__":
    print("AGV Journey Phase Fix Test\n")

    try:
        test_workstation_transition_fix()
        test_simulation_of_position_update()

    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
