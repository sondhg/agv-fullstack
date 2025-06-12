import schedule
import time
import datetime
import threading
from typing import List, Dict
from django.db.models import QuerySet
from django.conf import settings

from ..models import Agv
from .. import mqtt


class HelloSchedulerService:
    """
    Service class to handle MQTT hello message scheduling logic.
    """

    def __init__(self):
        self.scheduler_running = False
        self.scheduler_thread = None

    def get_agvs_with_active_orders(self) -> QuerySet[Agv]:
        """
        Get all AGVs that have active orders.

        Returns:
            QuerySet[Agv]: All AGVs with active orders
        """
        return Agv.objects.filter(active_order__isnull=False)

    def calculate_schedule_datetime_for_agv(self, agv: Agv) -> datetime.datetime:
        """
        Calculate the scheduled datetime for an AGV's hello message.

        Args:
            agv: The AGV to calculate schedule time for

        Returns:
            datetime.datetime: The scheduled datetime
        """
        active_order = agv.active_order
        return datetime.datetime.combine(active_order.order_date, active_order.start_time)

    def is_hello_scheduled_for_future(self, schedule_datetime: datetime.datetime) -> bool:
        """
        Check if the hello message is scheduled for future execution.

        Args:
            schedule_datetime: The scheduled datetime

        Returns:
            bool: True if scheduled for future, False otherwise
        """
        return schedule_datetime > datetime.datetime.now()

    def create_scheduled_message_info(self, agv_id: str, schedule_datetime: datetime.datetime) -> Dict:
        """
        Create information dictionary for a scheduled hello message.

        Args:
            agv_id: The ID of the AGV
            schedule_datetime: When the message is scheduled

        Returns:
            Dict: Message scheduling information
        """
        now = datetime.datetime.now()
        return {
            "agv_id": agv_id,
            "scheduled_time": schedule_datetime.strftime("%Y-%m-%d %H:%M:%S"),
            "seconds_from_now": (schedule_datetime - now).total_seconds()
        }

    def send_agv_hello_message(self, agv_id: str) -> None:
        """
        Send a "Hey" message to the MQTT broker topic agvhello/{agv_id}.

        Args:
            agv_id: The ID of the AGV to send the hello message to
        """
        try:
            topic = f"{settings.MQTT_TOPIC_AGVHELLO}/{agv_id}"

            frame = bytearray()
            HELLO_FRAME = 0x01
            frame.append(HELLO_FRAME)

            message = bytes(frame)

            # Use the global MQTT client from the mqtt module
            mqtt.client.publish(topic, message)
            print(
                f"Successfully sent MQTT message {message} to topic '{topic}' for AGV {agv_id}")

        except Exception as e:
            print(
                f"Error sending MQTT hello message to AGV {agv_id}: {str(e)}")

    def create_hello_job(self, agv_id: str) -> callable:
        """
        Create a scheduled hello message job function.

        Args:
            agv_id: The ID of the AGV

        Returns:
            callable: The hello function to be scheduled
        """
        def create_hello_function(agv_id_val):
            def send_hello():
                self.send_agv_hello_message(agv_id_val)
                return schedule.CancelJob  # Remove job after execution
            return send_hello

        return create_hello_function(agv_id)

    def schedule_hello_message(self, agv: Agv) -> None:
        """
        Schedule a hello message for future sending.

        Args:
            agv: The AGV to schedule hello message for
        """
        hello_function = self.create_hello_job(agv.agv_id)
        start_time = agv.active_order.start_time

        job = schedule.every().day.at(start_time.strftime("%H:%M:%S")).do(hello_function)
        job.tag(f"agv_{agv.agv_id}")

        print(
            f"Scheduled MQTT message for AGV {agv.agv_id} at {start_time.strftime('%H:%M:%S')}")

    def process_agvs_for_hello_scheduling(self, agvs_with_orders: QuerySet[Agv]) -> List[Dict]:
        """
        Process all AGVs with orders for hello message scheduling or immediate sending.

        Args:
            agvs_with_orders: QuerySet of AGVs with active orders

        Returns:
            List[Dict]: List of scheduled message information
        """
        scheduled_messages = []

        for agv in agvs_with_orders:
            schedule_datetime = self.calculate_schedule_datetime_for_agv(agv)

            if self.is_hello_scheduled_for_future(schedule_datetime):
                # Schedule for future sending
                self.schedule_hello_message(agv)
                scheduled_message_info = self.create_scheduled_message_info(
                    agv.agv_id, schedule_datetime)
                scheduled_messages.append(scheduled_message_info)
            else:
                # Send immediately if scheduled time has passed
                self.send_agv_hello_message(agv.agv_id)
                print(
                    f"Sent immediate MQTT hello message to AGV {agv.agv_id} (scheduled time already passed)")

        return scheduled_messages

    def start_scheduler_if_needed(self, scheduled_messages: List[Dict]) -> None:
        """
        Start the scheduler thread if there are scheduled messages and it's not already running.

        Args:
            scheduled_messages: List of scheduled messages
        """
        if not self.scheduler_running and scheduled_messages:
            if self.scheduler_thread and self.scheduler_thread.is_alive():
                # Reuse existing thread
                pass
            else:
                # Create a new thread
                self.scheduler_thread = threading.Thread(
                    target=self._run_scheduler,
                    daemon=True,
                    name="hello_scheduler_thread"
                )
                self.scheduler_thread.start()

    def _run_scheduler(self) -> None:
        """Run the scheduler in a background thread"""
        self.scheduler_running = True
        while self.scheduler_running:
            schedule.run_pending()
            time.sleep(1)
        print("Hello scheduler thread stopped")
