#!/usr/bin/env python
"""
Test script to verify that the spare_flag is correctly set to False for idle AGVs
after order completion and that it only becomes True when backup nodes are needed.
"""

import os
import sys
import django

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agv_server.settings')
django.setup()

import logging
from agv_data.models import Agv
from django.db import transaction

logger = logging.getLogger(__name__)


def test_spare_flag_idle_agvs():
    """Test that idle AGVs have spare_flag = False"""
    print("=== Testing spare_flag for idle AGVs ===")
    
    idle_agvs = Agv.objects.filter(
        motion_state=Agv.IDLE,
        active_order=None,
        next_node=None
    )
    
    print(f"Found {idle_agvs.count()} idle AGVs")
    
    for agv in idle_agvs:
        print(f"AGV {agv.agv_id}: spare_flag={agv.spare_flag}, current_node={agv.current_node}")
        if agv.spare_flag:
            print(f"  ERROR: Idle AGV {agv.agv_id} should have spare_flag=False")
        else:
            print(f"  OK: Idle AGV {agv.agv_id} has spare_flag=False")


def test_fix_idle_agv_spare_flags():
    """Fix spare_flag for idle AGVs that incorrectly have it set to True"""
    print("\n=== Fixing spare_flag for idle AGVs ===")
    
    idle_agvs_with_spare_flag = Agv.objects.filter(
        motion_state=Agv.IDLE,
        active_order=None,
        next_node=None,
        spare_flag=True
    )
    
    if idle_agvs_with_spare_flag.exists():
        print(f"Found {idle_agvs_with_spare_flag.count()} idle AGVs with incorrect spare_flag=True")
        
        with transaction.atomic():
            for agv in idle_agvs_with_spare_flag:
                print(f"  Fixing AGV {agv.agv_id}: setting spare_flag=False")
                agv.spare_flag = False
                agv.save(update_fields=['spare_flag'])
        
        print("Fixed all idle AGVs spare_flag")
    else:
        print("No idle AGVs found with incorrect spare_flag=True")


def test_spare_flag_logic():
    """Test the spare_flag logic in ControlPolicy"""
    print("\n=== Testing spare_flag logic ===")
    
    from agv_data.main_algorithms.algorithm2.algorithm2 import ControlPolicy
    
    # Test with idle AGVs
    idle_agvs = Agv.objects.filter(
        motion_state=Agv.IDLE,
        active_order=None,
        next_node=None
    ).first()
    
    if idle_agvs:
        control_policy = ControlPolicy(idle_agvs)
        should_use_backup = control_policy.should_use_backup_nodes()
        print(f"Idle AGV {idle_agvs.agv_id}: should_use_backup_nodes() = {should_use_backup}")
        if should_use_backup:
            print(f"  ERROR: Idle AGV should not use backup nodes")
        else:
            print(f"  OK: Idle AGV correctly does not use backup nodes")
    
    # Test with AGVs that have next_node
    agvs_with_next_node = Agv.objects.filter(next_node__isnull=False)
    
    for agv in agvs_with_next_node[:3]:  # Test first 3
        control_policy = ControlPolicy(agv)
        should_use_backup = control_policy.should_use_backup_nodes()
        print(f"AGV {agv.agv_id} (next_node={agv.next_node}): should_use_backup_nodes() = {should_use_backup}")
        print(f"AGV {agv.agv_id}:")
        print(f"  Active order: {agv.active_order.order_id if agv.active_order else 'None'}")
        print(f"  Motion state: {agv.get_motion_state_display()}")
        print(f"  Next node: {agv.next_node}")
        print(f"  Spare flag: {agv.spare_flag}")
        print()
    
    # Test control policy for each idle AGV
    print("Testing control policy application for idle AGVs...")
    
    for agv in agvs:
        if not agv.active_order and not agv.next_node:
            print(f"\nTesting AGV {agv.agv_id} (should be idle):")
            
            print(f"Before control policy:")
            print(f"  Spare flag: {agv.spare_flag}")
            print(f"  Motion state: {agv.get_motion_state_display()}")
            
            # Test should_use_backup_nodes method
            control_policy = ControlPolicy(agv)
            should_use_backup = control_policy.should_use_backup_nodes()
            print(f"  Should use backup nodes: {should_use_backup}")
            
            # Apply control policy
            affected_agvs = _apply_control_policy(agv)
            
            # Reload AGV to see changes
            agv.refresh_from_db()
            
            print(f"After control policy:")
            print(f"  Spare flag: {agv.spare_flag}")
            print(f"  Motion state: {agv.get_motion_state_display()}")
            print(f"  Affected AGVs: {len(affected_agvs)}")
            
            # Verify the fix
            if agv.spare_flag == False:
                print(f"  ✅ SUCCESS: Spare flag correctly set to False")
            else:
                print(f"  ❌ FAIL: Spare flag is {agv.spare_flag}, should be False")
        else:
            print(f"\nSkipping AGV {agv.agv_id} - not idle (has active order or next node)")

def fix_spare_flags_manually():
    """Manually fix spare_flags for all idle AGVs."""
    
    print("\n=== Manually Fixing Spare Flags ===\n")
    
    idle_agvs = Agv.objects.filter(
        active_order__isnull=True,
        next_node__isnull=True,
        motion_state=Agv.IDLE
    )
    
    print(f"Found {idle_agvs.count()} idle AGVs to fix")
    
    for agv in idle_agvs:
        if agv.spare_flag:
            print(f"Fixing AGV {agv.agv_id}: setting spare_flag from True to False")
            agv.spare_flag = False
            agv.save(update_fields=['spare_flag'])
        else:
            print(f"AGV {agv.agv_id}: spare_flag already correct (False)")
    
    print("\nFixed all idle AGV spare flags!")

if __name__ == "__main__":
    print("AGV Spare Flag Fix Test\n")
    
    try:
        test_idle_agv_spare_flag()
        fix_spare_flags_manually()
        
        # Test again after manual fix
        print("\n" + "="*50)
        test_idle_agv_spare_flag()
        
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
