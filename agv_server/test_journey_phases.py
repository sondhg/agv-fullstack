"""
Test script to verify AGV journey phase implementation.
This script tests the transition from outbound to inbound journey phases.
"""

from order_data.models import Order
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


def test_journey_phases():
    """Test AGV journey phase transitions."""

    print("=== AGV Journey Phase Test ===\n")

    # Find an AGV with an active order for testing
    test_agv = Agv.objects.filter(active_order__isnull=False).first()

    if not test_agv:
        print("❌ No AGV with active order found for testing")
        print("Please assign an order to an AGV first using the admin interface")
        return False

    print(f"Testing with AGV {test_agv.agv_id}")
    print(f"Active order: {test_agv.active_order.order_id}")
    print(f"Current journey phase: {test_agv.get_journey_phase_display()}")
    print(f"Current node: {test_agv.current_node}")
    print(f"Outbound path: {test_agv.outbound_path}")
    print(f"Inbound path: {test_agv.inbound_path}")
    print(f"Remaining path: {test_agv.remaining_path}")
    print()

    # Create control policy instance
    control_policy = ControlPolicy(test_agv)

    # Test outbound journey completion check
    print("--- Testing Outbound Journey Completion ---")

    if test_agv.journey_phase == Agv.OUTBOUND:
        # Simulate reaching workstation
        workstation_node = test_agv.active_order.workstation_node
        print(f"Simulating AGV reaching workstation node: {workstation_node}")

        # Update AGV to be at workstation with inbound path as remaining
        test_agv.current_node = workstation_node
        test_agv.remaining_path = test_agv.inbound_path.copy() if test_agv.inbound_path else []
        test_agv.save()

        # Test the transition logic
        control_policy._check_journey_phase_transition(workstation_node)

        # Reload AGV to see changes
        test_agv.refresh_from_db()

        print(f"After transition:")
        print(f"Journey phase: {test_agv.get_journey_phase_display()}")
        print(f"Remaining path: {test_agv.remaining_path}")
        print()

    elif test_agv.journey_phase == Agv.INBOUND:
        print("AGV is already on inbound journey")

        # Test order completion
        print("--- Testing Order Completion ---")
        parking_node = test_agv.active_order.parking_node
        print(f"Simulating AGV reaching parking node: {parking_node}")

        # Update AGV to be at parking with empty remaining path
        test_agv.current_node = parking_node
        test_agv.remaining_path = []
        test_agv.save()

        # Test the completion logic
        control_policy._check_journey_phase_transition(parking_node)

        # Reload AGV to see changes
        test_agv.refresh_from_db()

        print(f"After completion:")
        print(f"Journey phase: {test_agv.get_journey_phase_display()}")
        print(f"Motion state: {test_agv.get_motion_state_display()}")
        print(f"Active order: {test_agv.active_order}")
        print(f"Remaining path: {test_agv.remaining_path}")

    print("\n✅ Journey phase test completed successfully!")
    return True


def test_journey_helper_methods():
    """Test the helper methods for journey phase detection."""

    print("=== Testing Journey Helper Methods ===\n")

    # Find an AGV with paths for testing
    test_agv = Agv.objects.filter(
        outbound_path__isnull=False,
        inbound_path__isnull=False
    ).exclude(
        outbound_path=[],
        inbound_path=[]
    ).first()

    if not test_agv:
        print("❌ No AGV with valid paths found for testing")
        return False

    control_policy = ControlPolicy(test_agv)

    # Test outbound completion detection
    print("--- Testing Outbound Completion Detection ---")

    # Case 1: Empty remaining path
    test_agv.remaining_path = []
    result = control_policy._is_outbound_journey_complete()
    print(f"Empty remaining path: {result} (should be True)")

    # Case 2: Remaining path matches inbound path
    test_agv.remaining_path = test_agv.inbound_path.copy()
    result = control_policy._is_outbound_journey_complete()
    print(f"Remaining equals inbound: {result} (should be True)")

    # Case 3: Remaining path is different
    test_agv.remaining_path = test_agv.outbound_path.copy()
    result = control_policy._is_outbound_journey_complete()
    print(f"Remaining equals outbound: {result} (should be False)")

    # Test inbound completion detection
    print("\n--- Testing Inbound Completion Detection ---")

    # Case 1: Empty remaining path
    test_agv.remaining_path = []
    result = control_policy._is_inbound_journey_complete()
    print(f"Empty remaining path: {result} (should be True)")

    # Case 2: Non-empty remaining path
    test_agv.remaining_path = [1, 2, 3]
    result = control_policy._is_inbound_journey_complete()
    print(f"Non-empty remaining path: {result} (should be False)")

    print("\n✅ Helper methods test completed!")
    return True


if __name__ == "__main__":
    print("AGV Journey Phase Implementation Test\n")

    try:
        # Test helper methods first
        test_journey_helper_methods()
        print()

        # Test actual journey phases
        test_journey_phases()

    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
