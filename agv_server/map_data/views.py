"""Views for handling map data operations."""
import logging
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from .services.map_service import MapService
from .constants import ErrorMessages, SuccessMessages, LogMessages

logger = logging.getLogger(__name__)


@csrf_exempt
@require_POST
def import_connections(request):
    """Import connection data from CSV file."""
    try:
        data = request.body.decode("utf-8")
        result = MapService.import_connections(data)

        if result["success"]:
            logger.info(LogMessages.IMPORT_CONNECTIONS.format(
                result["connection_count"]))
            return JsonResponse({"message": result["message"]}, status=200)
        else:
            logger.error(result["message"])
            return JsonResponse({"error": result["message"]}, status=400)
    except Exception as e:
        logger.error(ErrorMessages.IMPORT_ERROR.format(str(e)))
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
@require_POST
def import_directions(request):
    """Import direction data from CSV file."""
    try:
        data = request.body.decode("utf-8")
        result = MapService.import_directions(data)

        if result["success"]:
            logger.info(LogMessages.IMPORT_DIRECTIONS.format(
                result["direction_count"]))
            return JsonResponse({"message": result["message"]}, status=200)
        else:
            logger.error(result["message"])
            return JsonResponse({"error": result["message"]}, status=400)
    except Exception as e:
        logger.error(ErrorMessages.IMPORT_ERROR.format(str(e)))
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
def get_map_data(request):
    """Get all map data including nodes, connections, and directions."""
    try:
        result = MapService.get_map_data()

        if result["success"]:
            return JsonResponse(result["data"], status=200)
        else:
            # Return a 206 Partial Content status if we have partial data
            status_code = 206 if "available" in result else 404
            return JsonResponse(result, status=status_code)

    except Exception as e:
        logger.error(str(e))
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
@require_POST
def delete_all_map_data(request):
    """Delete all map data."""
    try:
        result = MapService.delete_all_data()

        if result["success"]:
            logger.info(LogMessages.DELETE_SUCCESS)
            return JsonResponse(result, status=200)
        else:
            logger.error(result["message"])
            return JsonResponse({"error": result["message"]}, status=500)
    except Exception as e:
        logger.error(LogMessages.DELETE_ERROR.format(str(e)))
        return JsonResponse({"error": str(e)}, status=500)
