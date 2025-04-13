# Testing Example 1 from Research Paper

## Test Process

1. Create 3 test orders by sending the following JSON data via the UI:

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

3. Compare the schedule data with Example 1 from the research paper to verify:

   - The shared points between AGVs match:

     ```
     CP_1 = {15}
     CP_2 = {11, 12, 13, 14, 15}
     CP_3 = {13, 12, 11}
     ```

   - The sequential shared points match:
     ```
     SCP_1 = ∅
     SCP_2 = {11, 12, 13, 14}
     SCP_3 = {13, 12, 11}
     ```

4. Expected Results:

   - The web app should generate schedules that show the same shared points and sequential shared points as in Example 1
   - This verifies that the DSPA algorithm is correctly implemented for handling shared points and sequential shared points

5. Success Criteria:
   - Generated schedule data matches the example values from the research paper
   - AGVs coordinate properly around shared points
   - No deadlocks occur during execution

## Notes

- The test focuses specifically on verifying the shared points calculation aspect of the algorithm
- Additional tests would be needed to verify other aspects like spare point allocation
- Any discrepancies between generated results and the paper example should be investigated
