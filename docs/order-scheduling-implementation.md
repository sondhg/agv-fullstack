# Order Scheduling Implementation

## Overview

This document describes the implementation of the scheduling service for AGV order dispatch, which replaces the immediate assignment functionality with a time-based scheduling system.

## Implementation Summary

### Backend Changes (`agv_server/agv_data/views.py`)

#### Modified `DispatchOrdersToAGVsView`

The `DispatchOrdersToAGVsView` has been completely restructured to implement scheduling functionality:

**Key Features:**

1. **Time-Based Scheduling**: Orders are now scheduled to be assigned to AGVs at their specified `order_date` and `start_time`
2. **Background Scheduler**: Uses Python's `schedule` library with a background thread to execute scheduled assignments
3. **Immediate Assignment**: Orders with past scheduled times are assigned immediately
4. **AGV Selection**: Orders are matched to AGVs based on `parking_node` matching `preferred_parking_node`

**New Methods:**

- `_run_scheduler()`: Background thread that continuously runs the scheduler
- `_assign_single_order()`: Assigns a single order to an available AGV when scheduled time arrives

**Response Structure:**
```json
{
  "success": true,
  "message": "Successfully scheduled X orders and immediately assigned Y orders",
  "scheduled_orders": [
    {
      "order_id": 1,
      "agv_id": 2,
      "parking_node": 7,
      "scheduled_time": "2025-06-12 14:30:00",
      "seconds_from_now": 3600
    }
  ],
  "immediate_orders": [
    {
      "order_id": 3,
      "agv_id": 4,
      "parking_node": 19,
      "status": "assigned_immediately"
    }
  ],
  "total_processed": 2
}
```

### Frontend Changes

#### Updated `PageAGVs.tsx`

**Modified `handleDispatchOrders` function:**
- Enhanced to handle the new scheduling response structure
- Provides detailed feedback about scheduled vs immediately assigned orders
- Updated button text from "Dispatch orders to AGVs" to "Schedule orders to AGVs"

**Updated `dispatchOrdersToAGVs` API function:**
- Changed return type to match new response structure
- Better error handling for scheduling responses

## How It Works

### 1. Order Scheduling Process

When users click "Schedule orders to AGVs":

1. **Order Collection**: System fetches all unassigned orders (`active_agv__isnull=True`)
2. **AGV Availability Check**: For each order, finds available AGV with matching `preferred_parking_node`
3. **Time Calculation**: Combines `order_date` and `start_time` to determine execution time
4. **Scheduling Decision**:
   - If scheduled time is in the future: Creates a scheduled job
   - If scheduled time is in the past: Assigns immediately

### 2. Scheduled Assignment Execution

When a scheduled time arrives:

1. **Order Validation**: Verifies order is still unassigned
2. **AGV Availability Re-check**: Ensures AGV is still available
3. **Path Calculation**: Uses TaskDispatcher and OrderProcessor to generate paths
4. **Assignment**: Updates AGV with order data and sets motion state to WAITING

### 3. Scheduler Management

- **Thread Safety**: Uses daemon threads that automatically terminate when main application stops
- **Job Management**: Clears existing jobs before creating new ones to avoid duplicates
- **Single Instance**: Ensures only one scheduler thread runs at a time

## Configuration Requirements

### Database Models

The implementation relies on existing models:

**Order Model** (`order_data/models.py`):
- `order_date`: DateField for the target execution date
- `start_time`: TimeField for the target execution time
- `parking_node`: IntegerField matching AGV's preferred parking node

**AGV Model** (`agv_data/models.py`):
- `preferred_parking_node`: IntegerField for AGV's preferred parking location
- `active_order`: OneToOneField linking to assigned order
- `motion_state`: IntegerField tracking AGV status

### Dependencies

- `schedule`: Python library for job scheduling
- `threading`: For background scheduler execution
- `datetime`: For time calculations and comparisons

## Benefits

1. **Time-Based Execution**: Orders are assigned exactly when needed
2. **Resource Optimization**: AGVs remain available until their assigned time
3. **Flexible Scheduling**: Supports both immediate and future assignments
4. **Better User Feedback**: Clear indication of scheduled vs immediate assignments
5. **Robust Error Handling**: Graceful degradation when AGVs become unavailable

## Usage Example

1. Create orders with specific `order_date` and `start_time`
2. Ensure AGVs have matching `preferred_parking_node` values
3. Click "Schedule orders to AGVs" button
4. System will:
   - Schedule future orders for automatic assignment
   - Immediately assign orders with past times
   - Provide detailed feedback about the scheduling results

## Error Handling

- **No Available AGVs**: Orders are skipped with logged warnings
- **Invalid Order Data**: Orders with invalid nodes are skipped
- **Scheduler Failures**: Individual order assignment failures don't affect others
- **Thread Management**: Scheduler thread is properly managed and cleaned up

## Future Enhancements

Potential improvements could include:

1. **Order Priority**: Support for high-priority orders that jump the queue
2. **Dynamic Rescheduling**: Ability to reschedule orders after initial scheduling
3. **Load Balancing**: More sophisticated AGV selection algorithms
4. **Notification System**: Alerts when orders are successfully assigned
5. **Monitoring Dashboard**: Real-time view of scheduled vs executed orders
