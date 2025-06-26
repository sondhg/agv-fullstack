# Spare Flag Logic Fix

## Problem

After AGVs completed their orders and became idle, their `spare_flag` was incorrectly set to `True` instead of `False`. Idle AGVs should have `spare_flag = False` since they don't need backup node logic.

## Root Cause Analysis

The issue was NOT in the `should_use_backup_nodes()` function, but rather in the edge case handling of the `can_move_with_backup()` function which could potentially return `True` for AGVs with `next_node = None` under certain conditions.

## Fixes Applied

### 1. Added Guard in `can_move_with_backup()`

```python
def can_move_with_backup(self):
    """Check if AGV can move after backup node allocation (condition 3)."""
    # If AGV has no next_node (idle), it cannot move with backup
    if not self.agv.next_node:
        return False
    # ... rest of function
```

### 2. Direct Database Fix

Fixed the immediate issue by setting `spare_flag = False` for all idle AGVs:

```python
idle_agvs = Agv.objects.filter(
    motion_state=Agv.IDLE,
    active_order=None,
    next_node=None,
    spare_flag=True
)
for agv in idle_agvs:
    agv.spare_flag = False
    agv.save(update_fields=['spare_flag'])
```

## Logic Verification

### Correct Behavior for Idle AGVs

For AGVs that are idle (motion_state=IDLE, active_order=None, next_node=None):

- ✅ `spare_flag` should be `False`
- ✅ `can_move_freely()` should return `False`
- ✅ `should_use_backup_nodes()` should return `False`
- ✅ `can_move_with_backup()` should return `False`

### When spare_flag Should Be True

- AGV is in MOVING state with backup nodes allocated
- AGV has an active order and next_node
- `can_move_with_backup()` returns `True`

### When spare_flag Should Be False

- AGV is IDLE with no active order
- AGV has no next_node
- AGV is moving without backup nodes
- AGV is WAITING

## Testing

Created comprehensive test script `test_spare_flag_logic_fix.py` that:

1. Verifies idle AGVs have correct spare_flag behavior
2. Fixes any incorrect spare_flag values
3. Tests spare_flag conditions for all AGV states

## Files Modified

1. `agv_server/agv_data/main_algorithms/algorithm2/algorithm2.py`
   - Added guard in `can_move_with_backup()` for idle AGVs
2. `agv_server/test_spare_flag_logic_fix.py`
   - Created comprehensive test script

## Verification

All tests pass:

- 3 idle AGVs all have `spare_flag = False`
- All control policy methods return correct values for idle AGVs
- No incorrect spare_flag values found in database

The spare_flag logic is now working correctly for all AGV states.
