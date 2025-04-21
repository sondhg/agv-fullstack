from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from .models import Agv
from .serializers import AGVSerializer
from schedule_generate.services.algorithm_2 import ControlPolicyController


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

            # Add detailed state information to the response
            if result["success"]:
                result.update({
                    "reserved_node": updated_agv.reserved_node,
                    "spare_flag": updated_agv.spare_flag,
                    "spare_points": updated_agv.spare_points,
                    "moved_from": previous_node,
                    "residual_path": updated_agv.active_schedule.residual_path if updated_agv.active_schedule else None,
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
