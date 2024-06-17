from django.urls import path
from LeckerMeister import views as app_views
from . import views

urlpatterns = [
	path("Anmeldung.html", app_views.Anmeldung, name='Anmeldung'),
	path("Abmeldung/", app_views.Abmeldung, name='Abmeldung'),
	path("Registrierung.html", app_views.Registrierung, name='registrierung'),
	path("Homeseite.html", app_views.Homeseite, name='Homeseite'),
	path("Suchseite.html", app_views.Suchseite, name='Suchseite'),
	path("Upload.html", app_views.Upload, name='Upload'),
	path("Kochbuch.html", app_views.Kochbuch, name='Kochbuch'),
	path("Profil.html", app_views.Profil, name='Profil'),
	path("AGB.html", app_views.AGB),
	path("Datenschutz.html", app_views.Datenschutz),
	path("Impressum.html", app_views.Impressum),
	path('add_comment/<str:rezept_name>/', views.add_comment, name='add_comment'),

]
