"""
Test script to verify the order completion fix.
This script tests AGV 1 which should complete its order since it's at the parking node.
"""

import os
import sys
import django

# Add the project root to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agv_server.settings')
django.setup()

from agv_data.models import Agv
from agv_data.main_algorithms.algorithm2.algorithm2 import ControlPolicy

def test_order_completion_fix():
    """Test the fix for order completion when AGV reaches parking node."""
    
    print("=== Testing Order Completion Fix ===\n")
    
    # Get AGV 1 which should complete its order
    agv = Agv.objects.get(agv_id=1)
    
    print(f"AGV {agv.agv_id} Current State:")
    print(f"Current node: {agv.current_node}")
    print(f"Parking node (from order): {agv.active_order.parking_node if agv.active_order else 'No active order'}")
    print(f"Journey phase: {agv.get_journey_phase_display()}")
    print(f"Motion state: {agv.get_motion_state_display()}")
    print(f"Remaining path: {agv.remaining_path}")
    print(f"Next node: {agv.next_node}")
    print(f"Reserved node: {agv.reserved_node}")
    print(f"Active order: {agv.active_order.order_id if agv.active_order else 'None'}")
    print()
    
    # Check if AGV should complete its order
    if (agv.active_order and 
        agv.current_node == agv.active_order.parking_node and
        agv.journey_phase == Agv.INBOUND):
        
        print(f"✅ AGV {agv.agv_id} is at parking node and should complete order!")
        
        # Simulate the position update process
        control_policy = ControlPolicy(agv)
        
        print("Simulating position update...")
        control_policy.update_position_info(agv.current_node)
        
        # Reload to see changes
        agv.refresh_from_db()
        
        print("\nAfter position update:")
        print(f"Journey phase: {agv.get_journey_phase_display()}")
        print(f"Motion state: {agv.get_motion_state_display()}")
        print(f"Remaining path: {agv.remaining_path}")
        print(f"Next node: {agv.next_node}")
        print(f"Reserved node: {agv.reserved_node}")
        print(f"Active order: {agv.active_order.order_id if agv.active_order else 'None'}")
        
        # Verify the fix
        if not agv.active_order:
            print(f"✅ SUCCESS: AGV {agv.agv_id} order completed successfully!")
            print(f"✅ SUCCESS: AGV is now idle (motion_state = {agv.get_motion_state_display()})")
        else:
            print(f"❌ FAIL: AGV {agv.agv_id} still has active order {agv.active_order.order_id}")
            
            # Let's manually check what's happening
            print("\nDebugging - manually checking completion logic:")
            
            # Test inbound journey completion
            is_complete = control_policy._is_inbound_journey_complete()
            print(f"Is inbound journey complete: {is_complete}")
            
            # Test if AGV is at parking node
            at_parking = agv.current_node == agv.active_order.parking_node
            print(f"Is AGV at parking node: {at_parking}")
            
    else:
        print(f"AGV {agv.agv_id} is not ready for order completion")
        if not agv.active_order:
            print("- No active order")
        elif agv.current_node != agv.active_order.parking_node:
            print(f"- Not at parking node (current: {agv.current_node}, parking: {agv.active_order.parking_node})")
        elif agv.journey_phase != Agv.INBOUND:
            print(f"- Not in inbound phase (current: {agv.get_journey_phase_display()})")

def test_all_agvs():
    """Test all AGVs to see their order completion status."""
    
    print("\n=== Testing All AGVs ===\n")
    
    for agv in Agv.objects.filter(active_order__isnull=False):
        print(f"AGV {agv.agv_id}:")
        print(f"  Current: {agv.current_node}, Parking: {agv.active_order.parking_node}")
        print(f"  Journey: {agv.get_journey_phase_display()}, Motion: {agv.get_motion_state_display()}")
        print(f"  Remaining path: {agv.remaining_path}")
        
        at_parking = agv.current_node == agv.active_order.parking_node
        in_inbound = agv.journey_phase == Agv.INBOUND
        
        if at_parking and in_inbound:
            print(f"  🔄 Should complete order!")
        elif in_inbound:
            print(f"  🚚 In progress (inbound journey)")
        else:
            print(f"  🚚 In progress (outbound journey)")
        print()

if __name__ == "__main__":
    print("AGV Order Completion Fix Test\n")
    
    try:
        test_all_agvs()
        test_order_completion_fix()
        
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
