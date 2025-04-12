from typing import List, Dict, Tuple, Optional
from ..models import Schedule
from ..constants import AGVState
import json

class DeadlockService:
    """
    Service for detecting and resolving deadlocks between AGVs.
    Implementation based on Algorithm 3 from the algorithms-pseudocode.tex.
    """
    
    @staticmethod
    def detect_heading_on_deadlock() -> List[Dict]:
        """
        Detect heading-on deadlocks between AGVs.
        This implements the first part of Definition 9 from the paper:
        
        "If v_n^i = v_c^j and v_n^j = v_c^i, then a heading-on deadlock occurs between r_i and r_j."
        
        Returns:
            List[Dict]: A list of detected heading-on deadlocks, each with the involved AGVs and their locations.
        """
        deadlocks = []
        
        # Only consider AGVs in WAITING state (SA^i = 2)
        schedules = Schedule.objects.filter(state=AGVState.WAITING)
        
        for schedule_i in schedules:
            for schedule_j in schedules:
                # Skip self-comparison
                if schedule_i.schedule_id == schedule_j.schedule_id:
                    continue
                
                # Get traveling info
                v_n_i = schedule_i.traveling_info.get("v_n")
                v_c_i = schedule_i.traveling_info.get("v_c")
                v_n_j = schedule_j.traveling_info.get("v_n")
                v_c_j = schedule_j.traveling_info.get("v_c")
                
                # Check heading-on deadlock condition: v_n^i = v_c^j and v_n^j = v_c^i
                if v_n_i == v_c_j and v_n_j == v_c_i:
                    deadlocks.append({
                        "type": "heading_on",
                        "agv_1": schedule_i.schedule_id,
                        "agv_2": schedule_j.schedule_id,
                        "location": {
                            "agv_1": v_c_i,
                            "agv_2": v_c_j
                        }
                    })
        
        return deadlocks
    
    @staticmethod
    def detect_loop_deadlock() -> List[Dict]:
        """
        Detect loop deadlocks between AGVs.
        This implements the second part of Definition 9 from the paper:
        
        "A loop deadlock occurs if there exists a set of vehicles R = {r_i, r_j, r_p, ..., r_q} 
        such that v_n^i = v_c^j, v_n^j = v_c^p, ..., v_n^q = v_c^i."
        
        Returns:
            List[Dict]: A list of detected loop deadlocks, each with the involved AGVs and their locations.
        """
        deadlocks = []
        
        # Only consider AGVs in WAITING state (SA^i = 2)
        schedules = list(Schedule.objects.filter(state=AGVState.WAITING))
        visited = set()
        
        def find_cycle(schedule_id: int, path: List[int]) -> Optional[List[int]]:
            """Find a cycle in the graph of waiting AGVs"""
            if schedule_id in path:
                # Found a cycle, return the subpath from the first occurrence
                cycle_start = path.index(schedule_id)
                return path[cycle_start:]
            
            if schedule_id in visited:
                return None  # Already visited, but not part of a cycle
            
            visited.add(schedule_id)
            path.append(schedule_id)
            
            # Get the current schedule
            try:
                current = next(s for s in schedules if s.schedule_id == schedule_id)
            except StopIteration:
                path.pop()
                return None
            
            # Get next node in potential path
            v_n = current.traveling_info.get("v_n")
            if not v_n:
                path.pop()
                return None
            
            # Find the AGV at position v_n (if any)
            for next_schedule in schedules:
                v_c = next_schedule.traveling_info.get("v_c")
                if v_c == v_n:
                    # Continue the search from this AGV
                    cycle = find_cycle(next_schedule.schedule_id, path)
                    if cycle:
                        return cycle
            
            # Remove current node from path as we backtrack
            path.pop()
            return None
        
        # Start DFS from each unvisited AGV
        for schedule in schedules:
            if schedule.schedule_id not in visited:
                cycle = find_cycle(schedule.schedule_id, [])
                if cycle:
                    # Found a cycle (loop deadlock)
                    locations = []
                    for agv_id in cycle:
                        try:
                            s = next(s for s in schedules if s.schedule_id == agv_id)
                            locations.append(s.traveling_info.get("v_c"))
                        except StopIteration:
                            locations.append(None)
                    
                    deadlocks.append({
                        "type": "loop",
                        "agvs": cycle,
                        "locations": locations
                    })
        
        return deadlocks
    
    @staticmethod
    def resolve_heading_on_deadlock(deadlock: Dict) -> bool:
        """
        Resolve a heading-on deadlock by moving one AGV to its spare point.
        This implements lines 5-12 of Algorithm 3 from the paper.
        
        Args:
            deadlock (Dict): The detected deadlock information.
            
        Returns:
            bool: True if the deadlock was resolved, False otherwise.
        """
        try:
            # Get the two AGVs involved in the deadlock
            agv_1 = Schedule.objects.get(schedule_id=deadlock["agv_1"])
            agv_2 = Schedule.objects.get(schedule_id=deadlock["agv_2"])
            
            # Try to resolve using AGV 1's spare point first
            if agv_1.spare_flag and agv_1.sp:
                current_point = agv_1.traveling_info["v_c"]
                current_point_str = str(current_point)
                
                if current_point_str in agv_1.sp:
                    # Get the spare point for this position
                    spare_point = agv_1.sp[current_point_str]
                    
                    # Update AGV 1 to move to its spare point
                    agv_1.traveling_info["v_n"] = spare_point
                    agv_1.traveling_info["v_r"] = spare_point
                    
                    # Update initial path to include the detour to spare point
                    initial_path = agv_1.initial_path
                    if isinstance(initial_path, str):
                        try:
                            initial_path = json.loads(initial_path)
                        except json.JSONDecodeError:
                            initial_path = []
                    
                    if isinstance(initial_path, list) and current_point in initial_path:
                        # Insert spare point right after current position
                        index = initial_path.index(current_point)
                        initial_path.insert(index + 1, spare_point)
                        agv_1.initial_path = json.dumps(initial_path)
                    
                    # Set both AGVs to MOVING state
                    agv_1.state = AGVState.MOVING
                    agv_2.state = AGVState.MOVING
                    
                    # Save changes
                    agv_1.save()
                    agv_2.save()
                    
                    return True
            
            # If AGV 1 couldn't resolve, try AGV 2
            if agv_2.spare_flag and agv_2.sp:
                current_point = agv_2.traveling_info["v_c"]
                current_point_str = str(current_point)
                
                if current_point_str in agv_2.sp:
                    # Get the spare point for this position
                    spare_point = agv_2.sp[current_point_str]
                    
                    # Update AGV 2 to move to its spare point
                    agv_2.traveling_info["v_n"] = spare_point
                    agv_2.traveling_info["v_r"] = spare_point
                    
                    # Update initial path to include the detour to spare point
                    initial_path = agv_2.initial_path
                    if isinstance(initial_path, str):
                        try:
                            initial_path = json.loads(initial_path)
                        except json.JSONDecodeError:
                            initial_path = []
                    
                    if isinstance(initial_path, list) and current_point in initial_path:
                        # Insert spare point right after current position
                        index = initial_path.index(current_point)
                        initial_path.insert(index + 1, spare_point)
                        agv_2.initial_path = json.dumps(initial_path)
                    
                    # Set both AGVs to MOVING state
                    agv_1.state = AGVState.MOVING
                    agv_2.state = AGVState.MOVING
                    
                    # Save changes
                    agv_1.save()
                    agv_2.save()
                    
                    return True
            
            # Couldn't resolve the deadlock
            return False
            
        except Schedule.DoesNotExist:
            return False
    
    @staticmethod
    def resolve_loop_deadlock(deadlock: Dict) -> bool:
        """
        Resolve a loop deadlock by moving one AGV with spare points.
        This implements lines 13-17 of Algorithm 3 from the paper.
        
        Args:
            deadlock (Dict): The detected deadlock information.
            
        Returns:
            bool: True if the deadlock was resolved, False otherwise.
        """
        try:
            # Get all AGVs in the loop and find one with spare points
            for agv_id in deadlock["agvs"]:
                schedule = Schedule.objects.get(schedule_id=agv_id)
                
                # Check if this AGV has spare points
                if schedule.spare_flag and schedule.sp:
                    current_point = schedule.traveling_info["v_c"]
                    current_point_str = str(current_point)
                    
                    if current_point_str in schedule.sp:
                        # Get the spare point for this position
                        spare_point = schedule.sp[current_point_str]
                        
                        # Update to move to spare point
                        schedule.traveling_info["v_n"] = spare_point
                        schedule.traveling_info["v_r"] = spare_point
                        
                        # Update initial path to include the detour
                        initial_path = schedule.initial_path
                        if isinstance(initial_path, str):
                            try:
                                initial_path = json.loads(initial_path)
                            except json.JSONDecodeError:
                                initial_path = []
                        
                        if isinstance(initial_path, list) and current_point in initial_path:
                            # Insert spare point right after current position
                            index = initial_path.index(current_point)
                            initial_path.insert(index + 1, spare_point)
                            schedule.initial_path = json.dumps(initial_path)
                        
                        # Set this AGV to MOVING state
                        schedule.state = AGVState.MOVING
                        schedule.save()
                        
                        # Set all other AGVs in the loop to MOVING state
                        for other_agv_id in deadlock["agvs"]:
                            if other_agv_id != agv_id:
                                other_schedule = Schedule.objects.get(schedule_id=other_agv_id)
                                other_schedule.state = AGVState.MOVING
                                other_schedule.save()
                        
                        return True
            
            # No AGV with spare points found
            return False
            
        except Schedule.DoesNotExist:
            return False
    
    @classmethod
    def check_and_resolve_deadlocks(cls) -> Tuple[bool, List[Dict]]:
        """
        Check for deadlocks and attempt to resolve them.
        This is the main entry point for deadlock detection and resolution.
        Implements the main logic of Algorithm 3 from the paper.
        
        Returns:
            Tuple[bool, List[Dict]]: 
                - bool: True if no deadlocks or all deadlocks were resolved
                - List[Dict]: Information about any detected deadlocks
        """
        # Check for heading-on deadlocks first
        heading_on_deadlocks = cls.detect_heading_on_deadlock()
        
        if heading_on_deadlocks:
            # Try to resolve each heading-on deadlock
            for deadlock in heading_on_deadlocks:
                if cls.resolve_heading_on_deadlock(deadlock):
                    return True, heading_on_deadlocks
            
            # Couldn't resolve the deadlocks
            return False, heading_on_deadlocks
        
        # Check for loop deadlocks
        loop_deadlocks = cls.detect_loop_deadlock()
        
        if loop_deadlocks:
            # Try to resolve each loop deadlock
            for deadlock in loop_deadlocks:
                if cls.resolve_loop_deadlock(deadlock):
                    return True, loop_deadlocks
            
            # Couldn't resolve the deadlocks
            return False, loop_deadlocks
        
        # No deadlocks detected
        return True, [] 