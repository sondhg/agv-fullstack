from typing import List, Dict, Set, Optional, Tuple
from ..models import Schedule
from ..constants import AGVState

class DeadlockService:
    @staticmethod
    def detect_heading_on_deadlock() -> List[Dict]:
        """
        Detect heading-on deadlocks between AGVs.
        Returns a list of deadlock information if found.
        """
        deadlocks = []
        schedules = Schedule.objects.filter(state=AGVState.WAITING)
        
        for schedule_i in schedules:
            for schedule_j in schedules:
                if schedule_i.schedule_id != schedule_j.schedule_id:
                    if (schedule_i.traveling_info["v_n"] == schedule_j.traveling_info["v_c"] and
                        schedule_j.traveling_info["v_n"] == schedule_i.traveling_info["v_c"]):
                        deadlocks.append({
                            "type": "heading_on",
                            "agv_1": schedule_i.schedule_id,
                            "agv_2": schedule_j.schedule_id,
                            "location": {
                                "agv_1": schedule_i.traveling_info["v_c"],
                                "agv_2": schedule_j.traveling_info["v_c"]
                            }
                        })
        
        return deadlocks

    @staticmethod
    def detect_loop_deadlock() -> List[Dict]:
        """
        Detect loop deadlocks between AGVs.
        Returns a list of deadlock information if found.
        """
        deadlocks = []
        schedules = list(Schedule.objects.filter(state=AGVState.WAITING))
        visited = set()

        def find_cycle(schedule: Schedule, path: List[int]) -> Optional[List[int]]:
            if schedule.schedule_id in path:
                cycle_start = path.index(schedule.schedule_id)
                return path[cycle_start:]
            
            if schedule.schedule_id in visited:
                return None

            visited.add(schedule.schedule_id)
            path.append(schedule.schedule_id)

            next_point = schedule.traveling_info["v_n"]
            for next_schedule in schedules:
                if next_schedule.traveling_info["v_c"] == next_point:
                    cycle = find_cycle(next_schedule, path)
                    if cycle:
                        return cycle

            path.pop()
            return None

        for schedule in schedules:
            if schedule.schedule_id not in visited:
                cycle = find_cycle(schedule, [])
                if cycle:
                    deadlocks.append({
                        "type": "loop",
                        "agvs": cycle,
                        "locations": [
                            Schedule.objects.get(schedule_id=agv_id).traveling_info["v_c"]
                            for agv_id in cycle
                        ]
                    })

        return deadlocks

    @staticmethod
    def resolve_heading_on_deadlock(deadlock: Dict) -> bool:
        """
        Resolve a heading-on deadlock by moving one AGV to its spare point.
        Returns True if resolved successfully.
        """
        agv_1 = Schedule.objects.get(schedule_id=deadlock["agv_1"])
        agv_2 = Schedule.objects.get(schedule_id=deadlock["agv_2"])

        # Try to move AGV with spare points first
        if agv_1.spare_flag and agv_1.sp:
            current_point = agv_1.traveling_info["v_c"]
            if current_point in agv_1.sp:
                spare_point = agv_1.sp[current_point]
                agv_1.traveling_info["v_n"] = spare_point
                agv_1.traveling_info["v_r"] = spare_point
                agv_1.save()
                return True
        
        if agv_2.spare_flag and agv_2.sp:
            current_point = agv_2.traveling_info["v_c"]
            if current_point in agv_2.sp:
                spare_point = agv_2.sp[current_point]
                agv_2.traveling_info["v_n"] = spare_point
                agv_2.traveling_info["v_r"] = spare_point
                agv_2.save()
                return True

        return False

    @staticmethod
    def resolve_loop_deadlock(deadlock: Dict) -> bool:
        """
        Resolve a loop deadlock by moving one AGV with spare points.
        Returns True if resolved successfully.
        """
        for agv_id in deadlock["agvs"]:
            schedule = Schedule.objects.get(schedule_id=agv_id)
            if schedule.spare_flag and schedule.sp:
                current_point = schedule.traveling_info["v_c"]
                if current_point in schedule.sp:
                    spare_point = schedule.sp[current_point]
                    schedule.traveling_info["v_n"] = spare_point
                    schedule.traveling_info["v_r"] = spare_point
                    schedule.save()
                    return True
        
        return False

    @classmethod
    def check_and_resolve_deadlocks(cls) -> Tuple[bool, List[Dict]]:
        """
        Check for deadlocks and attempt to resolve them.
        Returns (resolved, deadlock_info) tuple.
        """
        # Check for heading-on deadlocks
        heading_on = cls.detect_heading_on_deadlock()
        if heading_on:
            for deadlock in heading_on:
                if cls.resolve_heading_on_deadlock(deadlock):
                    return True, heading_on
            return False, heading_on

        # Check for loop deadlocks
        loop = cls.detect_loop_deadlock()
        if loop:
            for deadlock in loop:
                if cls.resolve_loop_deadlock(deadlock):
                    return True, loop
            return False, loop

        return True, [] 