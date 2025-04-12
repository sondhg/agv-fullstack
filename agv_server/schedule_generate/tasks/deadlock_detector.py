from schedule_generate.models import Schedule
from schedule_generate.constants import AGVState


class DeadlockDetector:
    """
    Detects and resolves deadlocks among AGVs.
    Implementation based on Algorithm 3 from the algorithms-pseudocode.tex.
    """
    
    @staticmethod
    def detect_heading_on_deadlock():
        """
        Detect heading-on deadlocks among AGVs based on Definition 9:
        "If v_n^i = v_c^j and v_n^j = v_c^i, then a heading-on deadlock occurs between r_i and r_j."
        
        Returns:
            list: A list of tuples representing AGVs involved in heading-on deadlocks.
                  Each tuple contains two schedule IDs.
        """
        # Only consider AGVs in WAITING state (SA^i = 2)
        schedules = Schedule.objects.filter(state=AGVState.WAITING)
        deadlocks = []

        for schedule_i in schedules:
            for schedule_j in schedules:
                # Skip self comparison
                if schedule_i.schedule_id == schedule_j.schedule_id:
                    continue
                    
                # Get traveling info
                v_n_i = schedule_i.traveling_info.get("v_n")
                v_c_i = schedule_i.traveling_info.get("v_c")
                v_n_j = schedule_j.traveling_info.get("v_n")
                v_c_j = schedule_j.traveling_info.get("v_c")
                
                # Check heading-on deadlock condition
                if (v_n_i == v_c_j and v_n_j == v_c_i):
                    deadlocks.append((schedule_i.schedule_id, schedule_j.schedule_id))

        return deadlocks

    @staticmethod
    def detect_loop_deadlock():
        """
        Detect loop deadlocks among AGVs based on Definition 9:
        "A loop deadlock occurs if there exists a set of vehicles R = {r_i, r_j, r_p, ...} 
        such that v_n^i = v_c^j, v_n^j = v_c^p, ..., v_n^q = v_c^i."
        
        Returns:
            list: A list of lists representing AGVs involved in loop deadlocks.
                  Each inner list contains schedule IDs forming a loop.
        """
        # Only consider AGVs in WAITING state (SA^i = 2)
        schedules = list(Schedule.objects.filter(state=AGVState.WAITING))
        visited = set()
        loops = []

        def dfs(schedule_id, path):
            """Depth-first search to find loops in the deadlock graph"""
            if schedule_id in path:
                # Found a loop, return the path from the first occurrence of this node
                loop_start = path.index(schedule_id)
                return path[loop_start:]
                
            if schedule_id in visited:
                # Already visited, no loop found through this node
                return None
                
            # Mark as visited and add to path
            visited.add(schedule_id)
            path.append(schedule_id)
            
            # Get the current schedule
            try:
                current_schedule = next(s for s in schedules if s.schedule_id == schedule_id)
            except StopIteration:
                # Schedule not found
                path.pop()
                return None
                
            # Get the next node in the potential path
            v_n = current_schedule.traveling_info.get("v_n")
            if not v_n:
                # No next node defined
                path.pop()
                return None
                
            # Find AGVs at the next position (v_n)
            for next_schedule in schedules:
                v_c = next_schedule.traveling_info.get("v_c")
                if v_c == v_n:
                    # Continue DFS from this AGV
                    loop = dfs(next_schedule.schedule_id, path)
                    if loop:
                        return loop
            
            # Backtrack
            path.pop()
            return None

        # Start DFS from each unvisited AGV
        for schedule in schedules:
            if schedule.schedule_id not in visited:
                loop = dfs(schedule.schedule_id, [])
                if loop:
                    loops.append(loop)

        return loops
