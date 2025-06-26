# AGV Journey Phase Implementation

## Overview

The AGV system now properly handles the complete order journey cycle, which consists of two phases:

1. **Outbound Journey**: Parking Node → Storage Node → Workstation Node
2. **Inbound Journey**: Workstation Node → Parking Node

## Implementation Details

### Journey Phase Transitions

The journey phase transitions are automatically handled by the `ControlPolicy` class in Algorithm 2 when an AGV position is updated.

#### Outbound to Inbound Transition

- **Trigger**: AGV reaches the workstation node and outbound path is complete
- **Action**:
  - Set `journey_phase` to `INBOUND`
  - Update `remaining_path` to `inbound_path`
  - Recalculate common nodes for all AGVs

#### Order Completion

- **Trigger**: AGV reaches the parking node during inbound journey and remaining path is empty
- **Action**:
  - Clear all order-related data
  - Set AGV motion state to `IDLE`
  - Reset journey phase to `OUTBOUND` for next order
  - Recalculate common nodes for all AGVs

### Path Structure

When an order is assigned to an AGV:

1. **Initial Setup**:

   - `initial_path`: Complete path (outbound + inbound)
   - `outbound_path`: Parking → Storage → Workstation
   - `inbound_path`: Workstation → Parking
   - `remaining_path`: Initially set to `outbound_path`
   - `journey_phase`: Set to `OUTBOUND`

2. **During Outbound Journey**:

   - AGV follows `remaining_path` (which is the outbound path)
   - As AGV moves, nodes are removed from `remaining_path`

3. **At Workstation (Transition)**:

   - When AGV reaches workstation and outbound is complete
   - `journey_phase` changes to `INBOUND`
   - `remaining_path` is set to `inbound_path`

4. **During Inbound Journey**:

   - AGV follows `remaining_path` (which is now the inbound path)
   - As AGV moves, nodes are removed from `remaining_path`

5. **At Parking (Completion)**:
   - When AGV reaches parking node and remaining path is empty
   - Order is completed and AGV becomes idle

### Key Methods

#### In `ControlPolicy` class:

- `_check_journey_phase_transition()`: Main method that checks for transitions
- `_is_outbound_journey_complete()`: Validates if outbound journey is finished
- `_is_inbound_journey_complete()`: Validates if inbound journey is finished
- `_transition_to_inbound_journey()`: Handles outbound→inbound transition
- `_complete_order_journey()`: Handles order completion and AGV reset

### Error Handling

- Validates that inbound path exists before transition
- Logs warnings for missing inbound paths
- Handles edge cases where paths might be incomplete
- Gracefully handles errors in common nodes recalculation

### Integration Points

The journey phase logic is integrated into:

1. **Position Updates**: Called from `_update_path_info()` when AGV position changes
2. **MQTT Processing**: Automatically triggered when AGV position updates are received
3. **Common Nodes**: Recalculated after phase transitions to maintain system consistency

### Debugging and Monitoring

All journey phase transitions are logged with appropriate log levels:

- `INFO`: Major transitions (outbound→inbound, order completion)
- `DEBUG`: Detailed path analysis
- `WARNING`: Missing paths or unexpected states
- `ERROR`: Critical issues preventing transitions

## Usage Example

```python
# When AGV position is updated (e.g., from MQTT)
control_policy = ControlPolicy(agv)
control_policy.update_position_info(new_current_node)

# The journey phase transition logic runs automatically:
# 1. Updates remaining path
# 2. Checks for phase transitions
# 3. Handles outbound→inbound or order completion
# 4. Recalculates common nodes if needed
```

## Testing

To test the journey phase implementation:

1. Assign an order to an AGV
2. Simulate AGV movement through the outbound path
3. Verify transition to inbound phase at workstation
4. Simulate AGV movement through inbound path
5. Verify order completion and AGV idle state at parking

The implementation automatically handles all transitions based on AGV position updates.
