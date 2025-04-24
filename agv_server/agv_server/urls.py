"""
URL configuration for agv_backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.urls import include, path
from django.conf import settings
from django.views.generic import RedirectView

# Import the new order processing view for compatibility
from agv_data.views import ProcessOrdersView

urlpatterns = [
    path("api/", include([
        path("auth/", include("users.urls")),
        path("orders/", include("order_data.urls")),
        path("map/", include("map_data.urls")),
        # For backwards compatibility, keep the schedules URLs but redirect key endpoints
        path("schedules/", include([
            # Redirect the schedule generation endpoint to the new process-orders endpoint
            path("generate/", ProcessOrdersView.as_view(), name="schedule_generate_compat"),
            # Include other schedule endpoints for now
            path("", include("schedule_generate.urls")),
        ])),
        path("agvs/", include("agv_data.urls")),
    ])),
]
