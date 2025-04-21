# AGV Position Update Testing

This document outlines the process of testing the AGV position update functionality using Example 3 from the research paper referenced in the `algorithms-pseudocode.tex` file.

## Testing Overview

The testing involves sending POST requests to the server endpoint `http://127.0.0.1:8000/api/agvs/update-position/` using Postman. The goal is to verify that the AGVs' positions are updated correctly and that the server performs the necessary calculations as expected.

### Request and Response Format

- **Request Body**: The request body is in JSON format and contains the AGV ID and the new position of the AGV. Example:

  ```json
  {
    "agv_id": 2,
    "current_node": 13
  }
  ```

- **Response Format**: The server responds with a JSON object.

## Test Case: Example 3

The following sequence of requests is based on Example 3 from the research paper:

### Request Sequence

1. **AGV 2** at node **17**
2. **AGV 2** at node **18**
3. **AGV 2** at node **10**
4. **AGV 1** at node **7**
5. **AGV 1** at node **6**
6. **AGV 1** at node **5**
7. **AGV 3** at node **32**
8. **AGV 3** at node **31**
9. **AGV 3** at node **23**
10. **AGV 3** at node **15**
11. **AGV 1** at node **13**
12. **AGV 2** at node **11**
13. **AGV 1** at node **21**
14. **AGV 2** at node **12**
15. **AGV 3** at node **14**
16. **AGV 2** at node **13**
17. **AGV 3** at node **6**
18. **AGV 2** at node **14** <!-- With current code, this is where unexpected error happens, need to fix.>

## Notes

- Ensure that the server's response matches the expected output for each request.
- Verify that the AGVs' positions are updated correctly in the system after each request.
