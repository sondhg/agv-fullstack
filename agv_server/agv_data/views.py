from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from .models import Agv
from .serializers import AGVSerializer
from .services.algorithm_1.algorithm1 import TaskDispatcher
from .services.algorithm_2.controller import ControlPolicyController
from .services.algorithm_3.algorithm3 import DeadlockResolver
from .constants import ErrorMessages, SuccessMessages


class ListAGVsView(ListAPIView):
    queryset = Agv.objects.all()
    serializer_class = AGVSerializer


class CreateAGVView(APIView):
    def post(self, request):
        if isinstance(request.data, list):
            # Handle multiple objects
            serializer = AGVSerializer(data=request.data, many=True)
        else:
            # Handle single object
            serializer = AGVSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DeleteAGVView(APIView):
    def delete(self, request, agv_id):
        try:
            agv = Agv.objects.get(agv_id=agv_id)
            agv.delete()
            return Response(
                {"message": f"AGV {agv_id} deleted successfully."},
                status=status.HTTP_200_OK,
            )
        except Agv.DoesNotExist:
            return Response(
                {"error": f"AGV {agv_id} does not exist."},
                status=status.HTTP_404_NOT_FOUND,
            )


class BulkDeleteAGVsView(APIView):
    def delete(self, request):
        try:
            agv_ids = request.data.get("agv_ids", [])
            if not agv_ids:
                return Response(
                    {"error": "No AGV IDs provided for deletion."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            deleted_count, _ = Agv.objects.filter(
                agv_id__in=agv_ids).delete()
            return Response(
                {"message": f"{deleted_count} AGVs deleted successfully."},
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {"error": f"An error occurred during bulk deletion: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class UpdateAGVPositionView(APIView):
    """
    API endpoint for AGVs to report their positions and receive control decisions.
    Implements the Central Controller's decision-making process from Algorithm 2.

    According to Algorithm 2 in algorithms-pseudocode.tex, when an AGV reaches an
    identification node, it should report its position to the central controller.
    The controller then:
    1. Updates the traveling information (I^i)
    2. Updates residual path (Π_i), shared points (CP^i), and sequential shared points (SCP^i)
    3. Evaluates movement conditions to determine if the AGV can move
    4. Handles spare point application or removal if needed
    5. Returns the updated state to the AGV

    If the AGV enters a waiting state (SA^i = 2), the controller should also:
    6. Check for deadlocks using Algorithm 3
    7. Resolve any detected deadlocks by moving AGVs with spare points to their spare points
    """

    def post(self, request):
        """
        Handles position update requests from AGVs.

        The AGV sends its current position and ID, and the controller calculates
        the next action based on Algorithm 2: Control Policy of the Central Controller.

        Request format:
        {
            "agv_id": int,           # ID of the AGV (r_i)
            "current_node": int,     # Current position of the AGV (v_c^i)
        }

        Response format:
        {
            "success": bool,         # Whether the request was processed successfully
            "message": str,          # Description message
            "state": str,            # "idle", "moving", or "waiting" (SA^i)
            "next_node": int|null,   # Next node to move to (v_n^i) if state is "moving"
            "reserved_node": int|null, # Reserved node (v_r^i)
            "spare_flag": bool,      # Whether AGV has spare points (F^i)
            "spare_points": object,  # Spare points mapping (SP^i)
        }
        """
        try:
            # Extract data from the request
            agv_id = request.data.get('agv_id')
            current_node = request.data.get('current_node')

            # Validate the input data
            if agv_id is None or current_node is None:
                return Response(
                    {
                        "success": False,
                        "message": "agv_id and current_node are required fields"
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Get the AGV from the database
            try:
                agv = Agv.objects.get(agv_id=agv_id)
            except Agv.DoesNotExist:
                return Response(
                    {
                        "success": False,
                        "message": f"AGV with ID {agv_id} not found"
                    },
                    status=status.HTTP_404_NOT_FOUND,
                )

            # Store previous position for logging
            previous_node = agv.current_node

            # Update the AGV's current position
            agv.current_node = current_node
            agv.save()

            # Initialize the control policy controller
            controller = ControlPolicyController()

            # Call update_agv_state to determine the AGV's next action
            # This method implements Algorithm 2 from the research paper
            result = controller.update_agv_state(agv_id)

            # Get the updated AGV data for the response
            updated_agv = Agv.objects.get(agv_id=agv_id)

            # If the AGV entered a waiting state, check for and resolve deadlocks
            # This implements the automatic deadlock detection and resolution from Algorithm 3
            deadlock_info = {}
            if result.get("state") == "waiting":
                # Initialize the deadlock resolver
                resolver = DeadlockResolver()

                # Detect and resolve deadlocks
                deadlock_result = resolver.detect_and_resolve_deadlocks()

                # If deadlocks were resolved, refresh the AGV data
                if deadlock_result.get("deadlocks_resolved", 0) > 0:
                    # Re-fetch the AGV to get updated state after deadlock resolution
                    updated_agv = Agv.objects.get(agv_id=agv_id)

                    # Update the result with the new state if this AGV was moved
                    if agv_id in deadlock_result.get("agvs_moved", []):
                        result["state"] = "moving"
                        result["message"] = "AGV moved to spare point to resolve deadlock"
                        result["next_node"] = updated_agv.next_node

                    deadlock_info = {
                        "deadlock_resolved": True,
                        "deadlock_details": deadlock_result
                    }

            # Add detailed state information to the response
            if result["success"]:
                result.update({
                    "reserved_node": updated_agv.reserved_node,
                    "spare_flag": updated_agv.spare_flag,
                    "spare_points": updated_agv.spare_points,
                    "moved_from": previous_node,
                    # Updated to use agv.residual_path directly
                    "residual_path": updated_agv.residual_path,
                    **deadlock_info  # Add deadlock information if applicable
                })

            # Log the position update for debugging
            print(f"AGV {agv_id} updated position from {previous_node} to {current_node}, " +
                  f"state: {result.get('state', 'unknown')}, next_node: {result.get('next_node', None)}")

            # Return the result to the AGV
            return Response(result, status=status.HTTP_200_OK)

        except Exception as e:
            import traceback
            traceback_str = traceback.format_exc()
            return Response(
                {
                    "success": False,
                    "message": f"Error processing position update: {str(e)}",
                    "details": traceback_str
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class ProcessOrdersView(APIView):
    """
    API endpoint to process orders and assign them to available AGVs.
    This replaces the functionality previously in the schedule_generate app.
    """

    def post(self, request):
        """
        Process available orders and assign them to idle AGVs.

        Returns:
            Response: Information about processed orders and assigned AGVs.
        """
        try:
            # Initialize the task dispatcher (Algorithm 1)
            dispatcher = TaskDispatcher()

            # Dispatch tasks (orders) to available AGVs
            processed_orders = dispatcher.dispatch_tasks()

            if processed_orders:
                return Response(
                    {
                        "success": True,
                        "message": SuccessMessages.ORDERS_PROCESSED.format(len(processed_orders)),
                        "processed_orders": processed_orders
                    },
                    status=status.HTTP_200_OK,
                )
            else:
                return Response(
                    {
                        "success": False,
                        "message": "No orders were processed. Check that you have available orders and idle AGVs."
                    },
                    status=status.HTTP_200_OK,
                )
        except ValueError as e:
            return Response(
                {"success": False, "message": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            import traceback
            traceback_str = traceback.format_exc()
            return Response(
                {
                    "success": False,
                    "message": f"Error processing orders: {str(e)}",
                    "details": traceback_str
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
