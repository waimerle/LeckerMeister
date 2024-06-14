from django.urls import path
from LeckerMeister import views as app_views

urlpatterns = [
        path("", app_views.Allgemein),
	
]

