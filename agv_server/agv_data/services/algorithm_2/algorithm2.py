"""
Implementation of Algorithm 2: Control Policy of the Central Controller

This module is now a proxy to the refactored implementation spread across multiple files
for better maintainability. The public API remains the same for backward compatibility.

According to Definition 8 in the paper, an AGV's traveling information is denoted as:
I^i = {v_c^i, v_n^i, v_r^i}, where:
- v_c^i: Current position or the point the AGV last left
- v_n^i: Next point to be visited
- v_r^i: Point that the AGV has reserved

Key points from algorithms-pseudocode.tex:
1. AGVs can only move if next point is not reserved by another AGV
2. For sequential shared points (SCP), AGVs must have spare points to proceed
3. When AGV is in sequential shared points with spare points (F^i = 1), it should 
   remove the spare point for its current position when it reaches a new point
"""

# Import the controller from the refactored implementation
from .controller import ControlPolicyController

# Export the class with the same name to maintain backwards compatibility
# The actual implementation is now in controller.py
__all__ = ['ControlPolicyController']
