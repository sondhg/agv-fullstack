# Testing Example 2 from Research Paper

## Test Process

1. Create 3 test orders with the same initial paths as Example 1:

   ```json
   [
     {
       "order_id": 1,
       "order_date": "2025-04-13",
       "start_time": "01:07:52",
       "parking_node": 7,
       "storage_node": 15,
       "workstation_node": 23
     },
     {
       "order_id": 2,
       "order_date": "2025-04-13",
       "start_time": "01:08:52",
       "parking_node": 19,
       "storage_node": 11,
       "workstation_node": 16
     },
     {
       "order_id": 3,
       "order_date": "2025-04-13",
       "start_time": "01:09:52",
       "parking_node": 13,
       "storage_node": 11,
       "workstation_node": 9
     }
   ]
   ```

2. Generate schedules for these orders using the web app
   These schedules will have the following initial_path fields:

   - Schedule 1: {7, 15, 23}
   - Schedule 2: {19, 11, 12, 13, 14, 15, 16}
   - Schedule 3: {13, 12, 11, 10, 9}

3. Focus on AGV r2 to test spare point allocation:

   - SCP_2 = {11, 12, 13}
   - For point 11: free point is 3, so SP(11) = 3
   - For point 12: free points are {4, 20}, but 4 is closer, so SP(12) = 4
   - For point 13: free point is 5, so SP(13) = 5
   - Expected SP_2 = {"11":3, "12":4, "13":5}

4. Expected Results:

   - The spare points should be allocated exactly as shown in Example 2:
     ```
     SP(11) = 3  (only free point for node 11)
     SP(12) = 4  (closest of free points {4, 20})
     SP(13) = 5  (only free point for node 13)
     ```

5. Success Criteria:
   - The web app correctly identifies free points for each sequential shared point
   - For points with multiple free points, the nearest one is chosen
   - The spare point allocation matches the example values exactly
   - Free points are correctly identified as points that are:
     a) Connected to the shared point
     b) Not in any AGV's residual path

```json
[
  {
    "schedule_id": 1,
    "order_id": 1,
    "order_date": "2025-04-13",
    "start_time": "01:07:52",
    "est_end_time": "00:00:00",
    "parking_node": 7,
    "storage_node": 15,
    "workstation_node": 23,
    "initial_path": "[7, 15, 23]",
    "residual_path": "[7, 15, 23]",
    "cp": [15],
    "scp": [],
    "sp": {},
    "traveling_info": {
      "v_c": 7,
      "v_n": 15,
      "v_r": 15
    },
    "state": 1,
    "spare_flag": false
  },
  {
    "schedule_id": 2,
    "order_id": 2,
    "order_date": "2025-04-13",
    "start_time": "01:08:52",
    "est_end_time": "00:00:00",
    "parking_node": 19,
    "storage_node": 11,
    "workstation_node": 16,
    "initial_path": "[19, 11, 12, 13, 14, 15, 16]",
    "residual_path": "[19, 11, 12, 13, 14, 15, 16]",
    "cp": [11, 12, 13, 15],
    "scp": [11, 12, 13],
    "sp": {
      "11": 3,
      "12": 4,
      "13": 5
    },
    "traveling_info": {
      "v_c": 19,
      "v_n": 11,
      "v_r": 11
    },
    "state": 1,
    "spare_flag": false
  },
  {
    "schedule_id": 3,
    "order_id": 3,
    "order_date": "2025-04-13",
    "start_time": "01:09:52",
    "est_end_time": "00:00:00",
    "parking_node": 13,
    "storage_node": 11,
    "workstation_node": 9,
    "initial_path": "[13, 12, 11, 10, 9]",
    "residual_path": "[13, 12, 11, 10, 9]",
    "cp": [13, 12, 11],
    "scp": [13, 12, 11],
    "sp": {
      "11": 3,
      "12": 4,
      "13": 5
    },
    "traveling_info": {
      "v_c": 13,
      "v_n": 12,
      "v_r": 12
    },
    "state": 1,
    "spare_flag": false
  }
]
```

## Notes

- This test verifies only the spare point allocation aspect of the DSPA algorithm
- The test uses the same initial setup as Example 1 for consistency
- Free points must not be in any AGV's residual path
- For points with multiple free points available, the nearest one should be chosen
- This example does not involve AGV movement or spare point application - it only tests the initial allocation calculation
