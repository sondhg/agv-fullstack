from typing import List, Dict, Tuple, Optional, Set
from django.db.models import Q
from ..models import Schedule
from ..pathfinding.movement_conditions import MovementConditions
from ..constants import AGVState
from map_data.models import Connection
import json

class DeadlockService:
    """
    Service for detecting and resolving deadlocks between AGVs.
    Implementation based on Algorithm 3 from the algorithms-pseudocode.tex.
    """
    
    @staticmethod
    def calculate_shared_points(schedule: Schedule) -> Tuple[List[int], List[int]]:
        """
        Calculate shared points (CP) and sequential shared points (SCP) for an AGV.
        Implements Definition 3 and 4 from the paper.
        
        Args:
            schedule: The Schedule object to calculate shared points for
            
        Returns:
            Tuple[List[int], List[int]]: A tuple containing (CP, SCP)
        """
        # Get all active schedules except the current one
        other_schedules = Schedule.objects.exclude(
            schedule_id=schedule.schedule_id
        ).exclude(state=AGVState.IDLE)
        
        # Get current schedule's residual path
        try:
            residual_path = json.loads(schedule.residual_path)
        except json.JSONDecodeError:
            return [], []
            
        # Calculate shared points (CP)
        shared_points = []
        for point in residual_path:
            for other_schedule in other_schedules:
                try:
                    other_path = json.loads(other_schedule.residual_path)
                    if point in other_path:
                        shared_points.append(point)
                        break
                except json.JSONDecodeError:
                    continue
        
        # Calculate sequential shared points (SCP)
        sequential_shared = []
        for i, point in enumerate(shared_points):
            # Skip if this is the last point
            if i == len(shared_points) - 1:
                continue
                
            # Check if current point and next point are connected
            next_point = shared_points[i + 1]
            try:
                Connection.objects.get(
                    Q(node1=point, node2=next_point) |
                    Q(node1=next_point, node2=point)
                )
                # Points are connected, add both to sequential shared points
                if point not in sequential_shared:
                    sequential_shared.append(point)
                if next_point not in sequential_shared:
                    sequential_shared.append(next_point)
            except Connection.DoesNotExist:
                continue
        
        return shared_points, sequential_shared
    
    @staticmethod
    def find_free_points(point: int, all_residual_paths: Set[int]) -> List[int]:
        """
        Find free points connected to a given point.
        A free point is a point that is connected to the given point but not in any AGV's residual path.
        
        Args:
            point: The point to find free points for
            all_residual_paths: Set of all points in any AGV's residual path
            
        Returns:
            List[int]: List of free points, sorted by distance
        """
        # Get all connected points
        connections = Connection.objects.filter(
            Q(node1=point) | Q(node2=point)
        ).order_by('distance')
        
        free_points = []
        for conn in connections:
            connected_point = conn.node2 if conn.node1 == point else conn.node1
            if connected_point not in all_residual_paths:
                free_points.append(connected_point)
        
        return free_points
    
    @classmethod
    def allocate_spare_points(cls, schedule: Schedule) -> Dict[str, int]:
        """
        Allocate spare points for sequential shared points.
        Implements Algorithm 4 from the paper.
        
        Args:
            schedule: The Schedule object to allocate spare points for
            
        Returns:
            Dict[str, int]: Dictionary mapping points to their spare points
        """
        # Get all residual paths from all active AGVs
        all_paths = set()
        active_schedules = Schedule.objects.exclude(state=AGVState.IDLE)
        for s in active_schedules:
            try:
                path = json.loads(s.residual_path)
                all_paths.update(path)
            except json.JSONDecodeError:
                continue
        
        # Get sequential shared points
        try:
            scp = schedule.scp
        except AttributeError:
            _, scp = cls.calculate_shared_points(schedule)
            schedule.scp = scp
            schedule.save()
        
        spare_points = {}
        # For each point in SCP, find a spare point
        for point in scp:
            free_points = cls.find_free_points(point, all_paths)
            if not free_points:
                # If we can't find a spare point for any point, return empty dict
                return {}
            # Assign the nearest free point as spare point
            spare_points[str(point)] = free_points[0]
        
        return spare_points

    @staticmethod
    def check_movement_conditions(schedule: Schedule) -> Tuple[bool, int]:
        """
        Check the three movement conditions defined in the paper.
        
        Args:
            schedule: The Schedule object to check conditions for
            
        Returns:
            Tuple[bool, int]: (can_move, condition_met)
            where condition_met is 0 for no condition met, or 1-3 for which condition was met
        """
        traveling_info = schedule.traveling_info or {}
        v_n = traveling_info.get("v_n")
        if not v_n:
            return False, 0
            
        # Get all other active schedules
        other_schedules = Schedule.objects.exclude(
            schedule_id=schedule.schedule_id
        ).exclude(state=AGVState.IDLE)
        
        # Check if v_n is reserved by another AGV
        for other in other_schedules:
            other_info = other.traveling_info or {}
            if other_info.get("v_r") == v_n:
                return False, 0
        
        # Condition 1: v_n not in SCP and not reserved
        if v_n not in schedule.scp:
            return True, 1
            
        # Condition 2: v_n in SCP but no points in SCP reserved by AGVs without spare points
        for point in schedule.scp:
            for other in other_schedules:
                other_info = other.traveling_info or {}
                if (other_info.get("v_r") == point and 
                    not other.spare_flag):
                    break
            else:
                continue
            break
        else:
            return True, 2
            
        # Condition 3: v_n in SCP, some points reserved by AGVs without spare points,
        # but this AGV has spare points
        if schedule.sp:
            return True, 3
            
        return False, 0
    
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
                info_i = schedule_i.traveling_info or {}
                info_j = schedule_j.traveling_info or {}
                
                v_n_i = info_i.get("v_n")
                v_c_i = info_i.get("v_c")
                v_n_j = info_j.get("v_n")
                v_c_j = info_j.get("v_c")
                
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
            info = current.traveling_info or {}
            v_n = info.get("v_n")
            if not v_n:
                path.pop()
                return None
            
            # Find the AGV at position v_n (if any)
            for next_schedule in schedules:
                next_info = next_schedule.traveling_info or {}
                v_c = next_info.get("v_c")
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
                            info = s.traveling_info or {}
                            locations.append(info.get("v_c"))
                        except StopIteration:
                            locations.append(None)
                    
                    deadlocks.append({
                        "type": "loop",
                        "agvs": cycle,
                        "locations": locations
                    })
        
        return deadlocks
    
    @classmethod
    def update_agv_state(cls, schedule: Schedule, condition: int) -> None:
        """
        Update AGV state based on movement conditions and spare point status.
        Implements the state transitions from Algorithm 2.
        
        Args:
            schedule: The Schedule object to update
            condition: Which movement condition was met (0-3)
        """
        traveling_info = schedule.traveling_info or {}
        
        if condition == 0:
            schedule.state = AGVState.WAITING
            traveling_info["v_r"] = traveling_info.get("v_c")
        else:
            schedule.state = AGVState.MOVING
            traveling_info["v_r"] = traveling_info.get("v_n")
            
            if condition in [1, 2]:
                # Reset spare points and flag if moving under conditions 1 or 2
                schedule.spare_flag = False
                schedule.sp = {}
            elif condition == 3 and not schedule.spare_flag:
                # Set spare flag if moving under condition 3 and don't have spare points
                schedule.spare_flag = True
                
        schedule.traveling_info = traveling_info
        schedule.save()

    @classmethod
    def resolve_deadlock(cls) -> bool:
        """
        Main deadlock resolution method implementing Algorithm 3.
        Integrates heading-on and loop deadlock detection and resolution.
        
        Returns:
            bool: True if any deadlock was resolved, False otherwise
        """
        # First check for heading-on deadlocks
        heading_deadlocks = cls.detect_heading_on_deadlock()
        for deadlock in heading_deadlocks:
            if cls.resolve_heading_on_deadlock(deadlock):
                return True
                
        # Then check for loop deadlocks
        loop_deadlocks = cls.detect_loop_deadlock()
        for deadlock in loop_deadlocks:
            if cls.resolve_loop_deadlock(deadlock):
                return True
                
        return False

    @classmethod
    def resolve_heading_on_deadlock(cls, deadlock: Dict) -> bool:
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
            
            # Try to resolve using AGV with spare points first
            for agv in [agv_1, agv_2]:
                other_agv = agv_2 if agv == agv_1 else agv_1
                
                if agv.spare_flag and cls.move_to_spare_point(agv):
                    # Update other AGV's state to MOVING
                    other_agv.state = AGVState.MOVING
                    other_info = other_agv.traveling_info or {}
                    other_info["v_r"] = other_info.get("v_n")
                    other_agv.traveling_info = other_info
                    other_agv.save()
                    return True
            
            # If neither AGV has spare points, try to allocate them
            for agv in [agv_1, agv_2]:
                other_agv = agv_2 if agv == agv_1 else agv_1
                
                # Calculate shared points and try to allocate spare points
                shared_points, sequential_shared = cls.calculate_shared_points(agv)
                agv.cp = shared_points
                agv.scp = sequential_shared
                spare_points = cls.allocate_spare_points(agv)
                
                if spare_points:
                    agv.sp = spare_points
                    agv.spare_flag = True
                    agv.save()
                    
                    if cls.move_to_spare_point(agv):
                        # Update other AGV's state to MOVING
                        other_agv.state = AGVState.MOVING
                        other_info = other_agv.traveling_info or {}
                        other_info["v_r"] = other_info.get("v_n")
                        other_agv.traveling_info = other_info
                        other_agv.save()
                        return True
            
            return False
            
        except Schedule.DoesNotExist:
            return False

    @classmethod
    def resolve_loop_deadlock(cls, deadlock: Dict) -> bool:
        """
        Resolve a loop deadlock by moving one AGV with spare points.
        This implements lines 13-17 of Algorithm 3 from the paper.
        
        Args:
            deadlock (Dict): The detected deadlock information.
            
        Returns:
            bool: True if the deadlock was resolved, False otherwise.
        """
        try:
            # First try to find an AGV that already has spare points
            for agv_id in deadlock["agvs"]:
                schedule = Schedule.objects.get(schedule_id=agv_id)
                if schedule.spare_flag and cls.move_to_spare_point(schedule):
                    # Set all other AGVs in the loop to MOVING state
                    for other_agv_id in deadlock["agvs"]:
                        if other_agv_id != agv_id:
                            other_schedule = Schedule.objects.get(schedule_id=other_agv_id)
                            other_schedule.state = AGVState.MOVING
                            other_info = other_schedule.traveling_info or {}
                            other_info["v_r"] = other_info.get("v_n")
                            other_schedule.traveling_info = other_info
                            other_schedule.save()
                    return True
            
            # If no AGV has spare points, try to allocate them
            for agv_id in deadlock["agvs"]:
                schedule = Schedule.objects.get(schedule_id=agv_id)
                
                # Calculate shared points and try to allocate spare points
                shared_points, sequential_shared = cls.calculate_shared_points(schedule)
                schedule.cp = shared_points
                schedule.scp = sequential_shared
                spare_points = cls.allocate_spare_points(schedule)
                
                if spare_points:
                    schedule.sp = spare_points
                    schedule.spare_flag = True
                    schedule.save()
                    
                    if cls.move_to_spare_point(schedule):
                        # Set all other AGVs in the loop to MOVING state
                        for other_agv_id in deadlock["agvs"]:
                            if other_agv_id != agv_id:
                                other_schedule = Schedule.objects.get(schedule_id=other_agv_id)
                                other_schedule.state = AGVState.MOVING
                                other_info = other_schedule.traveling_info or {}
                                other_info["v_r"] = other_info.get("v_n")
                                other_schedule.traveling_info = other_info
                                other_schedule.save()
                        return True
            
            return False
            
        except Schedule.DoesNotExist:
            return False

    @classmethod
    def move_to_spare_point(cls, schedule: Schedule) -> bool:
        """
        Move an AGV to its spare point and update all necessary information.
        This is a helper method used by both heading-on and loop deadlock resolution.
        
        Args:
            schedule: The Schedule object to move to its spare point
            
        Returns:
            bool: True if the AGV was successfully moved to a spare point, False otherwise
        """
        if not schedule.spare_flag or not schedule.sp:
            return False
            
        traveling_info = schedule.traveling_info or {}
        current_point = traveling_info.get("v_c")
        if not current_point:
            return False
            
        current_point_str = str(current_point)
        
        if current_point_str not in schedule.sp:
            return False
            
        # Get the spare point for this position
        spare_point = schedule.sp[current_point_str]
        
        # Update traveling info (I^i)
        traveling_info["v_n"] = spare_point
        traveling_info["v_r"] = spare_point
        schedule.traveling_info = traveling_info
        
        # Update residual path (Π_i) to include detour through spare point
        try:
            residual_path = json.loads(schedule.residual_path)
            current_idx = residual_path.index(current_point)
            # Insert spare point after current position
            residual_path.insert(current_idx + 1, spare_point)
            # Insert current point after spare point to ensure AGV returns
            residual_path.insert(current_idx + 2, current_point)
            schedule.residual_path = json.dumps(residual_path)
        except (json.JSONDecodeError, ValueError, IndexError):
            return False
            
        # Set state to MOVING
        schedule.state = AGVState.MOVING
        schedule.save()
        
        return True

    @classmethod
    def check_and_resolve_deadlocks(cls) -> Tuple[bool, List[Dict]]:
        """
        Check for and resolve any deadlocks in the system.
        
        Returns:
            Tuple[bool, List[Dict]]: A tuple containing:
                - bool: True if any deadlock was resolved, False otherwise
                - List[Dict]: List of detected deadlocks (both heading-on and loop)
        """
        # First check for heading-on deadlocks
        heading_deadlocks = cls.detect_heading_on_deadlock()
        
        # Then check for loop deadlocks
        loop_deadlocks = cls.detect_loop_deadlock()
        
        # Combine all detected deadlocks
        all_deadlocks = heading_deadlocks + loop_deadlocks
        
        # If there are deadlocks, try to resolve them
        if all_deadlocks:
            resolved = cls.resolve_deadlock()
            return resolved, all_deadlocks
        
        return False, []