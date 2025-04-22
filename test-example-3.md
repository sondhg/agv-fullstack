# Testing Example 3 from Research Paper

## Test Process

1. Create 3 test orders with the same initial paths as Example 3:

   ```json
   [
     {
       "order_id": 1,
       "order_date": "2025-04-13",
       "start_time": "01:07:52",
       "parking_node": 7,
       "storage_node": 5,
       "workstation_node": 21
     },
     {
       "order_id": 2,
       "order_date": "2025-04-13",
       "start_time": "01:08:52",
       "parking_node": 17,
       "storage_node": 10,
       "workstation_node": 22
     },
     {
       "order_id": 3,
       "order_date": "2025-04-13",
       "start_time": "01:09:52",
       "parking_node": 32,
       "storage_node": 15,
       "workstation_node": 19
     }
   ]
   ```

2. Generate schedules for these orders using the web app
   These schedules will have the following initial_path fields:

   - Schedule 1: {7, 6, 5, 13, 21}
   - Schedule 2: {17, 18, 10, 11, 12, 13, 14, 22}
   - Schedule 3: {32, 31, 23, 15, 14, 13, 12, 11, 19}

3. Focus on AGV r3 to test spare point allocation at t=5s:

   - SCP_3 = {14, 13, 12, 11}
   - For point 14: free point is 6, so SP(14) = 6
   - For point 13: free point is 5, so SP(13) = 5
   - For point 12: free point is 4, so SP(12) = 4
   - For point 11: free point is 3, so SP(11) = 3
   - Expected SP_3 = {"11":3, "12":4, "13":5, "14":6}

4. Expected Results:

   - The spare points should be allocated exactly as shown in Example 3:
     ```
     SP(14) = 6  (only free point for node 14)
     SP(13) = 5  (only free point for node 13)
     SP(12) = 4  (only free point for node 12)
     SP(11) = 3  (only free point for node 11)
     ```

5. Success Criteria:
   - The web app correctly identifies free points for each sequential shared point
   - The spare point allocation matches the example values exactly
   - Free points are correctly identified as points that are:
     a) Connected to the shared point
     b) Not in any AGV's residual path
   - At t=5s:
     - r1 should be at point 5 with next point 13
     - r2 should be at point 10 with next point 11
     - r3 should be at point 15 requesting spare points
