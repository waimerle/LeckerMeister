from django.urls import path
from LeckerMeister import views as app_views

urlpatterns = [
	path("Anmeldung.html", app_views.Anmeldung, name='Anmeldung'),
	path("Registrierung.html", app_views.Registrierung, name='Registrierung'),
	path("Homeseite.html", app_views.Homeseite, name='Homeseite'),
	path("Suchseite.html", app_views.Suchseite),
	path("Upload.html", app_views.Upload, name='Upload'),
	path("Kochbuch.html", app_views.Kochbuch),
	path("Profil.html", app_views.Profil, name='Profil'),
	path("Datenschutz.html", app_views.Datenschutz),
	path("Impressum.html", app_views.Impressum),
	path("AGB.html", app_views.AGB),
]
