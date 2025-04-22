"""
Algorithm 2 implementation package for AGV control policy

This package implements the central controller's logic for managing AGV movement
based on the DSPA algorithm described in algorithms-pseudocode.tex.
"""
from .controller import ControlPolicyController

__all__ = ['ControlPolicyController']